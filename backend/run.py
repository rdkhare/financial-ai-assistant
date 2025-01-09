from app import create_app
from app.routes import routes_bp  # Import the Blueprint for routes

# Create the Flask app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)