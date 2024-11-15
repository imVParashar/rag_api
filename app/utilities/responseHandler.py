"""Response handler for success and failure"""
from typing import Dict, AnyStr, Union, Any
from app.utilities.logger import logger


def success_response(response: [Dict, AnyStr], status: int) -> Dict[str, Union[int, Any]]:
    """
    This method is used as a response
    handler for success responses.
    @param response: JSON/String
    @param status: Integer
    @return: JSON
    """
    logger.info('Request Processed Successfully by the Application!')
    return {"data": response, "status": status}


def failure_response(error: [Dict, AnyStr], status: int) -> Dict[str, Union[int, Any]]:
    """
    This method is used as a response
    handler for failure responses.
    @param error: JSON/String
    @param status: Integer
    @return: JSON
    """
    logger.error('Error while processing the request! - {}'.format(error))
    return {"error": error, "status": status}
