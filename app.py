import os
import sys

# Add backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

try:
    # Try importing directly from backend.app
    from backend.app import app
except ImportError:
    # If that fails, try importing the create_app function
    try:
        from backend.app import create_app
        app = create_app()
    except ImportError:
        # Last resort - try to import from the relative path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app
        app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))) 