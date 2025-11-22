"""Application factory and initialization for the SmartQ Flask app.

This module exposes `create_app` which constructs and configures the Flask
application using the provided configuration class. It also ensures the
database tables exist and creates an initial super-admin user when the
database is empty.
"""

from flask import Flask
from flask_migrate import Migrate
from config import Config
from app.models import db

migrate = Migrate()


def create_app(config_class=Config):
    """Create and configure the Flask application.

    Args:
        config_class: Configuration class to load into `app.config`.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import client, staff, admin, super_admin

    app.register_blueprint(client.bp)
    app.register_blueprint(staff.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(super_admin.bp)

    # Home route
    @app.route('/')
    def index():
        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="/static/css/homepage.css">
                <title>SmartQ - Home Page</title>
            </head>
            <body>
                <div class="header">
                    <h1>SmartQ</h1>
                </div>
                <main>
                    <section class="hero">
                        <div class="intro">
                            <h1>Welcome To SmartQ</h1>
                            <p>A comprehensive queue management system designed for Rwanda to reduce waiting time at service points like hospitals, banks and others.</p>
                        </div>
                    </section>

                    <section class="body">
                        <div class="features">
                            <h2>SmartQ - Models</h2>
                            <ul class="grid-container">
                                <a href="/client" class="grid-item item-1"><li>Client Queue Join</li></a>
                                <a href="/staff/login" class="grid-item item-2"><li>Staff Dashboard</li></a>
                                <a href="/admin/login" class="grid-item item-3"><li>Admin Panel</li></a>
                                <a href="/super-admin/login" class="grid-item item-4"><li>SuperAdmin Panel</li></a>
                            </ul>
                        </div>
                    </section>
                </main>
            </body>
            </html>
        '''

    # Create tables
    with app.app_context():
        db.create_all()
        create_initial_data()

    return app


def create_initial_data():
    """Create initial super-admin account if none exists.

    This helper is called at application startup (inside the app context)
    to ensure there is at least one super-admin user. It will create a user
    with username ``superadmin`` and password ``admin123`` only if no existing
    super-admin is found.
    """
    from app.models import User

    # Check if super admin exists
    super_admin = User.query.filter_by(role='super_admin').first()
    if not super_admin:
        admin = User(
            username='superadmin',
            role='super_admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Initial super admin created: username='superadmin'/ password='admin123'")
