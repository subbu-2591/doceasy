import os
import sys

# Add the current directory to the path so Python can find the backend module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.app import app
except ImportError:
    # If that fails, try to import from the app.py file directly
    from backend.app import create_app
    app = create_app()

if __name__ == "__main__":
    app.run() 