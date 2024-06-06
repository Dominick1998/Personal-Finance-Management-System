# run.py

# Import the application instance from the app package
from app import app

# Main entry point for the Flask application
if __name__ == "__main__":
    app.run(debug=True)  # Run the application in debug mode