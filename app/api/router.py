"""Root API router that mounts each module like a microservice."""

from fastapi import APIRouter

from app.smtp.routes.smtp import router as smtp_router

api_router = APIRouter()
api_router.include_router(smtp_router)
