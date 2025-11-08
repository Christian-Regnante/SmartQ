import os
from app import create_app, init_db

# Get configuration from environment or use default
config_name = os.getenv('FLASK_CONFIG', 'development')

# Create Flask application
app = create_app(config_name)

# Initialize database with sample data
with app.app_context():
    init_db(app)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(config_name == 'development')
    )