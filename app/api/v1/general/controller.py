"""
This module contains the general controller for the service.
It handles all http requests that are not entity specific.
"""

from fastapi import APIRouter
from app.common.config import settings
from app.common.database import inspector

router = APIRouter()


@router.get("/health", status_code=200)
async def health_check():

    tables = inspector.get_table_names()
    # get value of env variable ENV_FOR_DYNACONF
    # if it is not set, default to "development"

    password = settings.get("DATABASE_PASSWORD", None)
    masked_password = "*" * len(password) if password else "-----"

    resp = {
        "ENV_FOR_DYNACONF": settings.get("ENV_FOR_DYNACONF", "-----"),
        "DATABASE_NAME": settings.get("DATABASE_NAME", "-----"),
        "DATABASE_HOST": settings.get("DATABASE_HOST", "-----"),
        "DATABASE_PORT": settings.get("DATABASE_PORT", "-----"),
        "DATABASE_PASSWORD": masked_password,
        "DATABASE_USER": settings.get("DATABASE_USER", "-----"),
        "PORT": settings.get("PORT", "-----"),
        "LOG_LEVEL": settings.get("LOG_LEVEL", "-----"),
        "ANALYTICS_FOLDER": settings.get("ANALYTICS_FOLDER", "-----"),
        "APP_VERSION": settings.get("APP_VERSION", "-----"),
        "DB_TABLES": tables,
    }

    return {"settings": resp, "status": "ok"}


@router.get("/version", status_code=200)
async def version():
    return {"version": {settings.get("APP_VERSION", "-----")}}
