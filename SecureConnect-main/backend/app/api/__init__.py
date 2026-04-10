
from fastapi import APIRouter
from app.api.routes_simple import router as main_router
from app.api.auth import router as auth_router
from app.api.pipeline import router as pipeline_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(main_router, prefix="", tags=["secureway"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["ci_cd_pipeline"])
