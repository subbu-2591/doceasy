import os

# Print the current environment variables related to the port
print("Current PORT environment variable:", os.getenv('PORT'))
print("Current HOST environment variable:", os.getenv('HOST', '0.0.0.0'))

# Suggest the correct configuration for Render
print("\nFor Render deployment, use the following in your app.py:")
print("host = os.getenv('HOST', '0.0.0.0')")
print("port = int(os.getenv('PORT', 10000))  # Render detected port 10000")
print("app.run(host=host, port=port, debug=False, load_dotenv=False)")

print("\nMake sure your render.yaml or environment variables are properly set.") 