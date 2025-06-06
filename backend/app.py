import os
import sys
from flask import Flask, jsonify, request, current_app
from flask_cors import CORS
from cors_config import add_cors_headers, handle_options_request
from flask_mail import Mail
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import timedelta
import logging
from models import Admin
from routes import auth_bp, admin_bp, api_bp, doctor_bp, patient_bp, payment_bp
import time
from agora_token_builder import RtcTokenBuilder
from bson import ObjectId
from functools import wraps
import jwt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to load .env file, but continue if it fails
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Default Agora configuration
AGORA_APP_ID = os.getenv('AGORA_APP_ID', 'c579ccb211ff433a9f779af41141ca85')
AGORA_APP_CERTIFICATE = os.getenv('AGORA_APP_CERTIFICATE', '0b284fd4fca34a9cad8f069d464ebf29')

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration with extended JWT expiration for payment flow
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    # Extended token expiration to 7 days (168 hours) to prevent session expiry during payment
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 168)))
    
    # Frontend URL for email links
    app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'doceasy4@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'ryft lfyj qvko xobz')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'DocEasy <doceasy4@gmail.com>')
    
    # Initialize Flask-Mail
    mail = Mail(app)
    
    # MongoDB Atlas configuration
    uri = "mongodb+srv://subrahmanyag79:dhDShm338VxoPMUz@doceasy.kp4oh2g.mongodb.net/?retryWrites=true&w=majority&appName=doceasy"
    mongodb_db_name = os.getenv('MONGODB_DB_NAME', 'doceasy')
    
    # Connect to MongoDB Atlas
    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client[mongodb_db_name]
        app.config['DATABASE'] = db
        
        # Test connection
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB Atlas database: {mongodb_db_name}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    
    # CORS configuration - allow all common development ports for all routes
    cors_origins = os.getenv('CORS_ORIGIN', 'http://localhost:5173,http://localhost:8080,http://localhost:3000,https://doc-easy.onrender.com').split(',')
    CORS(app, 
         origins=cors_origins,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True
    )
    
    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        return add_cors_headers(response)
    
    # Handle OPTIONS requests
    @app.before_request
    def before_request():
        response = handle_options_request()
        if response:
            return response
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    
    # Create default admin user
    with app.app_context():
        create_default_admin(db)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({'message': 'Internal server error'}), 500
    
    # Health check endpoint with explicit CORS headers
    @app.route('/health', methods=['GET', 'OPTIONS'])
    def health_check():
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
            return response
            
        try:
            # Check database connection
            app.config['DATABASE'].list_collection_names()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'jwt_expiry_hours': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 168))
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 503
    
    # Add CORS headers to auth ping endpoint
    @app.route('/api/auth/ping', methods=['GET', 'OPTIONS'])
    def auth_ping():
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', 'https://doc-easy.onrender.com')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
            return response
            
        return jsonify({'status': 'ok', 'message': 'Auth service is running'}), 200
    
    @app.route('/get_agora_token', methods=['POST'])
    def get_agora_token():
        try:
            data = request.get_json()
            channel_name = data.get('channel')
            uid = data.get('uid', 0)
            role = data.get('role', 'publisher')  # publisher or subscriber
            
            if not channel_name:
                return jsonify({'error': 'Channel name is required'}), 400

            # Set token expiration time (24 hours)
            expiration_time_in_seconds = 24 * 3600
            current_timestamp = int(time.time())
            privilegeExpiredTs = current_timestamp + expiration_time_in_seconds

            # Generate token
            token = RtcTokenBuilder.buildTokenWithUid(
                AGORA_APP_ID,
                AGORA_APP_CERTIFICATE,
                channel_name,
                uid,
                1 if role == 'publisher' else 2,  # 1 for publisher, 2 for subscriber
                privilegeExpiredTs
            )

            return jsonify({
                'token': token,
                'appId': AGORA_APP_ID,
                'channel': channel_name,
                'uid': uid,
                'role': role,
                'expires_in': expiration_time_in_seconds
            })

        except Exception as e:
            logger.error(f"Error generating Agora token: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/consultations/<consultation_id>', methods=['GET'])
    @token_required
    def get_consultation(current_user, consultation_id):
        try:
            db = get_db()
            
            # Find consultation
            consultation = db.consultations.find_one({'_id': ObjectId(consultation_id)})
            
            if not consultation:
                return jsonify({'error': 'Consultation not found'}), 404

            # Check if user has access to this consultation
            if current_user['role'] == 'doctor' and str(consultation['doctor_id']) != current_user['id']:
                return jsonify({'error': 'Unauthorized access'}), 403
            elif current_user['role'] == 'patient' and str(consultation['patient_id']) != current_user['id']:
                return jsonify({'error': 'Unauthorized access'}), 403

            # Generate Agora channel name and token
            channel_name = f"consultation_{consultation_id}"
            uid = int(current_user['id'][-6:]) if len(current_user['id']) >= 6 else int(time.time()) % 1000000
            
            # Set token expiration time (24 hours)
            expiration_time_in_seconds = 24 * 3600
            current_timestamp = int(time.time())
            privilegeExpiredTs = current_timestamp + expiration_time_in_seconds

            # Generate token
            token = RtcTokenBuilder.buildTokenWithUid(
                AGORA_APP_ID,
                AGORA_APP_CERTIFICATE,
                channel_name,
                uid,
                1,  # Role: publisher
                privilegeExpiredTs
            )

            # Convert ObjectId to string for JSON serialization
            consultation['_id'] = str(consultation['_id'])
            consultation['doctor_id'] = str(consultation['doctor_id'])
            consultation['patient_id'] = str(consultation['patient_id'])
            if 'appointment_id' in consultation:
                consultation['appointment_id'] = str(consultation['appointment_id'])

            # Add Agora information
            consultation['agora'] = {
                'appId': AGORA_APP_ID,
                'channel': channel_name,
                'token': token,
                'uid': uid,
                'role': current_user['role'],
                'expires_in': expiration_time_in_seconds
            }

            return jsonify({
                'consultation': consultation
            })

        except Exception as e:
            logger.error(f"Error fetching consultation: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return app

def create_default_admin(db):
    """Create default admin user if it doesn't exist"""
    default_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'subrahmanyag79@gmail.com')
    default_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'Subbu@2004')
    
    # Check if admin already exists
    existing_admin = Admin.find_by_email(db, default_email)
    
    if not existing_admin:
        # Create default admin
        admin = Admin.create(db, default_email, default_password, "Admin User")
        logger.info(f"Created default admin user: {default_email}")
    else:
        logger.info(f"Default admin user already exists: {default_email}")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
            current_user = {'id': data['user_id'], 'role': data['role']}
        except:
            return jsonify({'error': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

def get_db():
    return current_app.config['DATABASE']

app = create_app()

# Optional: Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    logger.info(f"Starting Flask application on {host}:{port}")

    # Disable automatic .env loading to avoid encoding issues
    sys.argv.append('--without-threads')

    app.run(host=host, port=port, debug=debug, load_dotenv=False)
