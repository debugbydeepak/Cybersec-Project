
from fastapi import APIRouter
from app.api.routes_simple import router as main_router

api_router = APIRouter()
api_router.include_router(main_router, prefix="", tags=["secureway"])
