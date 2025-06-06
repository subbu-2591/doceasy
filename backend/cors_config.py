from flask import request, jsonify

def add_cors_headers(response):
    """Add CORS headers to the response"""
    origin = request.headers.get('Origin')
    allowed_origins = [
        'http://localhost:5173',
        'http://localhost:8080',
        'http://localhost:3000',
        'https://doc-easy.onrender.com'
    ]
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def handle_options_request():
    """Handle OPTIONS request for CORS preflight"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        origin = request.headers.get('Origin')
        allowed_origins = [
            'http://localhost:5173',
            'http://localhost:8080',
            'http://localhost:3000',
            'https://doc-easy.onrender.com'
        ]
        
        if origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    return None 