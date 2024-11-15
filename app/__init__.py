"""This module is the core of the project."""

from flask import Flask
from app.utilities.logger import init_logger


def create_app():
    """
    Initialize the core application
    """

    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    init_logger()

    with app.app_context():

        # Import a module/component using its blueprint handler variable
        from app.auth.controllers import mod_auth as auth_module
        from app.rag.controllers import mod_rag as rag_module

        # Register blueprint(s)
        app.register_blueprint(auth_module)
        app.register_blueprint(rag_module)

        return app
