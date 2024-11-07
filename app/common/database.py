"""Database module for the service"""

import logging

from tenacity import retry, wait_exponential, before_log

from app.common.config import settings
from app.common.constants import (
    RETRY_EXP_BACKOFF_MULTIPLIER,
    RETRY_EXP_BACKOFF_MIN,
    RETRY_EXP_BACKOFF_MAX,
)
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger

# Convert log level from string to integer
log_level = logging.getLevelName("DEBUG")


@retry(
    wait=wait_exponential(
        multiplier=RETRY_EXP_BACKOFF_MULTIPLIER,
        min=RETRY_EXP_BACKOFF_MIN,
        max=RETRY_EXP_BACKOFF_MAX,
    ),  # Exponential backoff
    before=before_log(logger, log_level),  # Log before each attempt
)
def create_db_engine():
    try:
        eng = create_engine(settings.DATABASE_URL, echo=True)
        eng.connect()
        logger.info("Database connection established")
        return eng
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise e


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# keeps all metadata about the DB schema, shared for all entities
Base = declarative_base()

# Create an inspector instance
inspector = inspect(engine)


def get_db():
    """
    generator function that provides a new database session for each request
    and  ensures that the session is properly closed after use
    """
    # create a new db session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
