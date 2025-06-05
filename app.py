from datetime import datetime
from flask_mongoengine import MongoEngine
from flask import Flask, request, jsonify
from functools import wraps
import jwt

app = Flask(__name__)

# JWT Configuration
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key in production

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            current_user = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return f(current_user, *args, **kwargs)
        except:
            return jsonify({'error': 'Token is invalid'}), 401
            
    return decorated

# MongoDB Configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'doceasy',
    'host': 'localhost',
    'port': 27017
}

# Initialize MongoDB
db = MongoEngine(app)

class Appointment(db.Document):
    patient_id = db.StringField(required=True)
    doctor_id = db.StringField(required=True)
    patient_name = db.StringField(required=True)
    doctor_name = db.StringField(required=True)
    appointment_date = db.DateTimeField(required=True)
    status = db.StringField(required=True, choices=['pending', 'confirmed', 'completed', 'cancelled'])
    reason = db.StringField()
    notes = db.StringField()
    rejection_reason = db.StringField()
    consultation_type = db.StringField(choices=['video', 'voice', 'chat', 'phone'])
    feedback = db.DictField()
    meta = {
        'collection': 'appointments'
    }

# Add to your imports and models section:
class Feedback(db.Document):
    patient_id = db.StringField(required=True)
    doctor_id = db.StringField(required=True)
    appointment_id = db.StringField(required=True)
    rating = db.IntField(required=True, min_value=1, max_value=5)
    feedback = db.StringField()
    timestamp = db.DateTimeField(default=datetime.utcnow)
    meta = {
        'collection': 'feedbacks',
        'indexes': [
            'patient_id',
            'doctor_id',
            'appointment_id'
        ]
    }

# Add these routes:
@app.route('/api/feedback/submit', methods=['POST'])
@token_required
def submit_feedback(current_user):
    if not current_user or current_user.get('role') != 'patient':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    appointment_id = data.get('appointmentId')
    doctor_id = data.get('doctorId')
    rating = data.get('rating')
    feedback_text = data.get('feedback')

    # Validate required fields
    if not all([appointment_id, doctor_id, rating]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate rating range
    if not 1 <= rating <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    try:
        # Check if appointment exists and belongs to the patient
        appointment = Appointment.objects(
            id=appointment_id,
            patient_id=current_user['id'],
            status='completed'
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found or not completed'}), 404

        # Check if feedback already exists
        existing_feedback = Feedback.objects(appointment_id=appointment_id).first()
        if existing_feedback:
            return jsonify({'error': 'Feedback already submitted for this appointment'}), 400

        # Create new feedback
        feedback = Feedback(
            patient_id=current_user['id'],
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            rating=rating,
            feedback=feedback_text,
            timestamp=datetime.utcnow()
        )
        feedback.save()

        # Update appointment with feedback reference
        appointment.update(
            feedback={
                'rating': rating,
                'feedback': feedback_text,
                'timestamp': feedback.timestamp
            }
        )

        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback': {
                'id': str(feedback.id),
                'rating': rating,
                'feedback': feedback_text,
                'timestamp': feedback.timestamp
            }
        }), 201

    except Exception as e:
        print('Error submitting feedback:', str(e))
        return jsonify({'error': 'Failed to submit feedback'}), 500

@app.route('/api/feedback/patient', methods=['GET'])
@token_required
def get_patient_feedback(current_user):
    if not current_user or current_user.get('role') != 'patient':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        feedbacks = Feedback.objects(patient_id=current_user['id']).order_by('-timestamp')
        return jsonify({
            'feedbacks': [{
                'id': str(f.id),
                'doctor_id': f.doctor_id,
                'appointment_id': f.appointment_id,
                'rating': f.rating,
                'feedback': f.feedback,
                'timestamp': f.timestamp
            } for f in feedbacks]
        }), 200

    except Exception as e:
        print('Error fetching feedback:', str(e))
        return jsonify({'error': 'Failed to fetch feedback'}), 500

@app.route('/api/feedback/doctor/<doctor_id>', methods=['GET'])
@token_required
def get_doctor_feedback(current_user, doctor_id):
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        feedbacks = Feedback.objects(doctor_id=doctor_id).order_by('-timestamp')
        return jsonify({
            'feedbacks': [{
                'id': str(f.id),
                'rating': f.rating,
                'feedback': f.feedback,
                'timestamp': f.timestamp
            } for f in feedbacks]
        }), 200

    except Exception as e:
        print('Error fetching doctor feedback:', str(e))
        return jsonify({'error': 'Failed to fetch feedback'}), 500 