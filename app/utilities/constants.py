"""All Modules related constants"""
from enum import Enum


class SuccessMessages(Enum):
    """
    Constants for Success Messages for All Modules
    """
    HEALTH_CHECK_DONE = "Health check-up successful"


class ErrorMessages(Enum):
    """
    Constants for Error Messages for All Modules
    """
    SOMETHING_WENT_WRONG = "Oops! Something went wrong."
