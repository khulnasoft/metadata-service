"""Service Entry Point"""

from readyapi import ReadyAPI
from readyapi.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from app.api.v1.tag_groups import controller as tag_group_controller
from app.api.v1.general import controller as general_controller
from app.api.v1.tags import controller as tags_controller
from app.api.v1.entity_tags import controller as entity_tags_controller
from app.common.config import settings
from app.common.constants import DEFAULT_APP_PORT
from app.common.exceptions import ExceptionResponse, ErrorDetail
from app.common.utils.logging_utils import setup_logger, LoggingFormat
from app.schema_migration import run_alembic_upgrade

logger = setup_logger(level="DEBUG", fmt=LoggingFormat.CONSOLE)

app = ReadyAPI()

app.include_router(tag_group_controller.router, prefix="/api/v1")
app.include_router(general_controller.router, prefix="/api/v1")
app.include_router(tags_controller.router, prefix="/api/v1")
app.include_router(entity_tags_controller.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    # Base.metadata.create_all(engine)
    run_alembic_upgrade()

    uvicorn.run(
        app, host="0.0.0.0", port=int(settings.get("PORT", default=DEFAULT_APP_PORT))
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    error_response = ExceptionResponse(
        error=ErrorDetail(
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal Server Error",
            details=str(exc),
            request=str(request),
        )
    )
    logger.error(error_response.model_dump())
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.model_dump()
    )


@app.exception_handler(HTTPException)
async def custom_validation_exception_handler(request, exc: HTTPException):
    error_response = ExceptionResponse(
        error=ErrorDetail(
            code=exc.status_code,
            message="Internal Server Error",
            details=str(exc),
            request=str(request),
        )
    )
    logger.error(error_response.model_dump())
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


app.add_exception_handler(Exception, global_exception_handler)
