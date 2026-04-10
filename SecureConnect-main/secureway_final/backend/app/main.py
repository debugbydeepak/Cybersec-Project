
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

from app.api import api_router

# Initialize Application
app = FastAPI(
    title="SECUREWAY Autonomous Logic Engine",
    description="Backend API for SECUREWAY security platform",
    version="2.0.0"
)

# CORS Middleware (Crucial for Frontend Communication)
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

# Include API Routes
app.include_router(api_router)
