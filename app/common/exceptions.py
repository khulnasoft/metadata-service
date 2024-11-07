"""Global exception handlers and custom exceptions and for the application"""

from pydantic import BaseModel
from typing import Optional


class ErrorDetail(BaseModel):
    code: int
    message: str
    details: Optional[str] = None  # Additional information, if any
    request: Optional[str] = None  # Request information, if any


class ExceptionResponse(BaseModel):
    error: ErrorDetail
