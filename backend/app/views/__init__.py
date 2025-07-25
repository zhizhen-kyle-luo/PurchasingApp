"""
Blueprint registration for the application
"""
from flask import Flask

from .auth import auth_bp
from .api import api_bp
from .main import main_bp


def register_blueprints(app: Flask):
    """Register all blueprints with the application"""
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
