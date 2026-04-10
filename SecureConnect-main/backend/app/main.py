
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import time
import os

from app.api import api_router

# Initialize Application
app = FastAPI(
    title="SECUREWAY Autonomous Logic Engine",
    description="Backend API for SECUREWAY security platform",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API Routes (no prefix - keeps /scan, /auth, /health, etc. working)
app.include_router(api_router)

# Serve Frontend Static Files at root
from fastapi.staticfiles import StaticFiles

static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend_static")

# Serve individual HTML pages explicitly so they take priority
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse(os.path.join(static_dir, "dashboard.html"))

@app.get("/login")
async def serve_login():
    return FileResponse(os.path.join(static_dir, "login.html"))

@app.get("/register")
async def serve_register():
    return FileResponse(os.path.join(static_dir, "register.html"))

# Mount static files for CSS, JS, images etc. (must be last)
if os.path.exists(static_dir):
    # Mount at root so style.css, landing.js etc. are served correctly
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static_assets")
