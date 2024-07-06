#!/usr/bin/env python3
"""app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class='config.Config'):
    """Main entry point."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from api.auth import auth_bp
    from api.home import home_bp
    from api.organisation import organisation_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(organisation_bp, url_prefix='/api')
    app.register_blueprint(home_bp, url_prefix='/')

    return app
