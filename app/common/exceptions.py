""" Global exception handlers and custom exceptions and for the application """

from app.common.utils.logging_utils import get_logger

logger = get_logger()


class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
