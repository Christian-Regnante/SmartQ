from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from config import config
from app.models import db, User

login_manager = LoginManager()


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # Configure login manager
    login_manager.login_view = 'staff.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.client import client_bp
    from app.routes.staff import staff_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Home route
    @app.route('/')
    def index():
        return '''
        <html>
        <head>
            <title>SmartQ - Queue Management System</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }
                .container {
                    background: white;
                    padding: 3rem;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 600px;
                }
                h1 {
                    color: #667eea;
                    margin-bottom: 0.5rem;
                    font-size: 2.5rem;
                }
                .subtitle {
                    color: #666;
                    margin-bottom: 2rem;
                    font-size: 1.1rem;
                }
                .links {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                a {
                    display: block;
                    padding: 1rem 2rem;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 10px;
                    font-size: 1.1rem;
                    transition: all 0.3s ease;
                }
                a:hover {
                    background: #764ba2;
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                .version {
                    margin-top: 2rem;
                    color: #999;
                    font-size: 0.9rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 SmartQ</h1>
                <p class="subtitle">Modern Queue Management for Rwanda</p>
                <div class="links">
                    <a href="/client">📱 Client Kiosk</a>
                    <a href="/staff/login">👨‍💼 Staff Dashboard</a>
                    <a href="/admin/login">⚙️ Admin Panel</a>
                </div>
                <p class="version">Version 1.0.0 MVP</p>
            </div>
        </body>
        </html>
        '''
    
    return app


def init_db(app):
    """Initialize database with sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if data already exists
        from app.models import Organization, Service, User, ServiceProvider
        
        if User.query.first() is None:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@smartq.rw',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample organization
            org = Organization(
                name='King Faisal Hospital',
                type='hospital',
                location='Kigali',
                contact_phone='+250788123456'
            )
            db.session.add(org)
            db.session.commit()
            
            # Create services
            services_data = [
                ('General Consultation', 'Room 101', 20),
                ('Pharmacy', 'Counter 1', 10),
                ('Laboratory', 'Lab 1', 15),
                ('Billing', 'Counter 2', 8)
            ]
            
            for name, counter, time in services_data:
                service = Service(
                    name=name,
                    organization_id=org.id,
                    counter_number=counter,
                    estimated_service_time=time
                )
                db.session.add(service)
            
            db.session.commit()
            
            # Create staff user
            staff_user = User(
                username='nurse1',
                email='nurse1@smartq.rw',
                role='staff',
                is_active=True
            )
            staff_user.set_password('nurse123')
            db.session.add(staff_user)
            db.session.commit()
            
            # Create service provider
            service = Service.query.filter_by(name='General Consultation').first()
            provider = ServiceProvider(
                user_id=staff_user.id,
                service_id=service.id,
                full_name='Dr. Jane Mugisha',
                phone='+250788999888'
            )
            db.session.add(provider)
            db.session.commit()
            
            print("✅ Database initialized with sample data")
            print("👤 Admin: admin / admin123")
            print("👨‍⚕️ Staff: nurse1 / nurse123")