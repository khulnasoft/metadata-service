""" Service Entry Point """

from fastapi import FastAPI
from fastapi.exception_handlers import (
    request_validation_exception_handler,
)
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from api.v1.tag_groups import controller as tag_group_controller
from api.v1.general import controller as general_controller
from api.v1.tags import controller as tags_controller
from api.v1.entity_tags import controller as entity_tags_controller
from common.config import settings
from common.constants import DEFAULT_APP_PORT
from common.utils.logging_utils import setup_logger, LoggingFormat
from alembic import command
from alembic.config import Config

logger = setup_logger(level="DEBUG", fmt=LoggingFormat.CONSOLE)

app = FastAPI()

app.include_router(tag_group_controller.router, prefix="/api/v1")
app.include_router(general_controller.router, prefix="/api/v1")
app.include_router(tags_controller.router, prefix="/api/v1")
app.include_router(entity_tags_controller.router, prefix="/api/v1")


def run_alembic_upgrade():
    # inject values from dynoconf
    # Alembic Config object
    # alembic_cfg = context.config
    # alembic_cfg.set_main_option("sqlalchemy.url", settings.get("DATABASE_URL"))

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "./migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    # alembic_cfg = Config("alembic.ini")
    try:
        logger.info("Running Alembic upgrade")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic upgrade completed successfully")
    except Exception as e:
        logger.error(f"Alembic upgrade failed: {e}")
        raise


if __name__ == "__main__":
    import uvicorn

    # Base.metadata.create_all(engine)
    run_alembic_upgrade()

    uvicorn.run(
        app, host="0.0.0.0", port=int(settings.get("PORT", default=DEFAULT_APP_PORT))
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}, request: {request}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


@app.exception_handler(HTTPException)
async def custom_validation_exception_handler(request, exc):
    logger(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


app.add_exception_handler(Exception, global_exception_handler)
