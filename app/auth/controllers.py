from flask import Blueprint
from app.utilities.logger import logger
from app.utilities import responseHandler
from app.auth.constants import AuthSuccessMessages
from typing import Dict


# Defining the blueprint 'auth'
mod_auth = Blueprint("auth", __name__, url_prefix='/auth')


@mod_auth.route("/health", methods=['GET'])
def health() -> Dict:
    """
    This method is used for health
    check for auth blueprint.
    @return: JSON
    """
    logger.info(AuthSuccessMessages.HEALTH_CHECK_DONE)
    return responseHandler.success_response(
        AuthSuccessMessages.HEALTH_CHECK_DONE,
        200
    )
