"""FastAPI composition root — wires modules into one monolith."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.smtp.services.smtp_service import smtp_service

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    smtp_service.load_from_settings(get_settings())
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "A modular monolith for SMTP testing. "
        "Save credentials, test the connection, and send a test email."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def home():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {
        "message": "SMTP Test Server is running",
        "docs": "/docs",
        "status": "/smtp/status",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
