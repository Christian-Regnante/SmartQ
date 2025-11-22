"""Simple entry point to run the SmartQ Flask application locally.

This module constructs the Flask app via the application factory and
runs the development server when executed directly.
"""

from app import create_app


# Create Flask application
app = create_app()


if __name__ == '__main__':
    # Run the development server. Debug=True is suitable for local
    # development only.
    app.run(debug=True, host='0.0.0.0', port=5000)
