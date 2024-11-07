"""
This file contains the pydantic models for the general API
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    ENV_FOR_DYNACONF: str = Field(default="-----")
    DATABASE_NAME: str = Field(default="-----")
    DATABASE_HOST: str = Field(default="-----")
    DATABASE_PORT: str = Field(default="-----")
    DATABASE_PASSWORD: str
    DATABASE_USER: str = Field(default="-----")
    PORT: str = Field(default="-----")
    LOG_LEVEL: str = Field(default="-----")
    ANALYTICS_FOLDER: str = Field(default="-----")
    APP_VERSION: str = Field(default="-----")
    DB_TABLES: Optional[List[str]] = Field(default_factory=list)


class HealthCheckResponse(BaseModel):
    settings: Settings
    status: str = "ok"


class VersionResponse(BaseModel):
    version: str = Field(default="-----")
