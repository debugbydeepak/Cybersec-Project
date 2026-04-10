
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import json
import os
import secrets
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

# Simple file-based storage path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserCreate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None  # Accept 'username' from frontend too
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

def get_users_db():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users_db(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def fake_hash_password(pwd: str):
    return f"scrypt_mock_{pwd}"

def verify_password(plain_password, hashed_password):
    return fake_hash_password(plain_password) == hashed_password

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    users = get_users_db()
    
    # Accept email from either field
    email = user.email or user.username
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    if email in users:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    users[email] = {
        "email": email,
        "full_name": user.full_name,
        "hashed_password": fake_hash_password(user.password),
        "disabled": False
    }
    
    save_users_db(users)

    # Auto-login after registration
    token = secrets.token_hex(16)
    token_type = "bearer" # nosec
    return {"access_token": token, "token_type": token_type}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = get_users_db()
    user = users.get(form_data.username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = secrets.token_hex(16)
    token_type = "bearer" # nosec
    return {"access_token": token, "token_type": token_type}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real app, verify the JWT here.
    # For now, just return a dummy user if a token is present.
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(email="test@example.com", full_name="Test User")

# Simple API Key storage
API_KEYS_FILE = os.path.join(DATA_DIR, "api_keys.json")
if not os.path.exists(API_KEYS_FILE):
    with open(API_KEYS_FILE, "w") as f:
        json.dump({}, f)

def get_api_keys_db():
    with open(API_KEYS_FILE, "r") as f:
        return json.load(f)

def save_api_keys_db(keys):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

@router.post("/apikeys/generate")
async def generate_api_key(alias: str, current_user: User = Depends(get_current_user)):
    """
    CI/CD Integration: Generates a persistent API token mapped to a specific user and alias
    (e.g., 'GitHub Actions Token'). This allows automated runners to trigger pipelines
    without logging in to create short-lived web JWTs.
    """
    keys_db = get_api_keys_db()
    raw_key = secrets.token_urlsafe(32)
    api_key = f"sw_{raw_key}"
    
    keys_db[api_key] = {
        "email": current_user.email,
        "alias": alias,
        "active": True
    }
    
    save_api_keys_db(keys_db)
    return {
        "alias": alias,
        "api_key": api_key,
        "message": "Keep this secure! It cannot be fully retrieved again."
    }
