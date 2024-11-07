"""
Enable to run Alembic migration to update the DB to the latest schema version
"""

from alembic import command
from alembic.config import Config
from app.common.config import settings
from app.common.utils.logging_utils import setup_logger, LoggingFormat

logger = setup_logger(level="DEBUG", fmt=LoggingFormat.CONSOLE)


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
    # Base.metadata.create_all(engine)
    run_alembic_upgrade()
