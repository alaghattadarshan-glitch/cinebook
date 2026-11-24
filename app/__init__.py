"""
Application Factory for CINEBOOK.
Initializes Flask app, extensions, blueprints, and database tables.
"""

import os
from flask import Flask, session
from flask_login import LoginManager
from flask_migrate import Migrate

from app.config import config_by_name
from app.models.base import db
from app.models.user import BaseUser
from app.services.seed_service import SeedService

login_manager = LoginManager()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user retrieval callback."""
    return db.session.get(BaseUser, int(user_id))


def create_app(config_name: str = None) -> Flask:
    """
    Flask Application Factory pattern.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to complete your booking."
    login_manager.login_message_category = "info"

    # Context processors: Inject selected city and cities list everywhere
    @app.context_processor
    def inject_global_data():
        from app.repositories import TheatreRepository
        theatre_repo = TheatreRepository()
        selected_city = session.get("selected_city", "Mumbai")
        cities = theatre_repo.get_distinct_cities()
        if not cities:
            cities = ["Mumbai", "Bengaluru", "Delhi NCR"]
        return {
            "selected_city": selected_city,
            "all_cities": cities
        }

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    from app.routes.booking import booking_bp
    from app.routes.tickets import tickets_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(movies_bp, url_prefix="/movies")
    app.register_blueprint(booking_bp, url_prefix="/book")
    app.register_blueprint(tickets_bp, url_prefix="/tickets")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Auto-create tables and run seed service in development if database is empty
    with app.app_context():
        db.create_all()
        # If no users exist, auto-seed with sample data
        from app.models.user import BaseUser
        if BaseUser.query.count() == 0:
            SeedService.seed_all()

    return app
