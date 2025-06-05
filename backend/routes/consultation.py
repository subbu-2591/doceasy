from flask import Blueprint, request, jsonify
from agora_token_builder import RtcTokenBuilder
import time
from bson import ObjectId
from datetime import datetime, timedelta
from database import db
import os

consultation_bp = Blueprint('consultation', __name__)

# Agora app configuration
AGORA_APP_ID = os.getenv('AGORA_APP_ID')
AGORA_APP_CERTIFICATE = os.getenv('AGORA_APP_CERTIFICATE')

@consultation_bp.route('/api/consultations/join/<consultation_id>', methods=['GET'])
def join_consultation(consultation_id):
    try:
        # Get user info from token
        user_id = request.user_id  # Assuming you have middleware that sets this
        user_role = request.user_role
        
        # Find consultation in database
        consultation = db.consultations.find_one({
            '_id': ObjectId(consultation_id)
        })
        
        if not consultation:
            return jsonify({
                'error': 'Consultation not found'
            }), 404
            
        # Check if user is authorized to join
        if user_role == 'doctor' and str(consultation['doctor_id']) != str(user_id):
            return jsonify({
                'error': 'Unauthorized to join this consultation'
            }), 403
            
        if user_role == 'patient' and str(consultation['patient_id']) != str(user_id):
            return jsonify({
                'error': 'Unauthorized to join this consultation'
            }), 403
            
        # Format response data
        response_data = {
            'consultation': {
                'id': str(consultation['_id']),
                'appointment_id': str(consultation['appointment_id']),
                'doctor_name': consultation['doctor_name'],
                'patient_name': consultation['patient_name'],
                'consultation_type': consultation['consultation_type'],
                'appointment_date': consultation['appointment_date'].isoformat(),
                'status': consultation['status'],
                'notes': consultation.get('notes', ''),
                'doctor_specialty': consultation.get('doctor_specialty', ''),
                'doctor_experience': consultation.get('doctor_experience', None)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print('Error in join_consultation:', str(e))
        return jsonify({
            'error': 'Failed to join consultation'
        }), 500

@consultation_bp.route('/api/consultations/<consultation_id>/voice-channel', methods=['GET'])
def get_voice_channel(consultation_id):
    try:
        # Get user info from token
        user_id = request.user_id  # Assuming you have middleware that sets this
        user_role = request.user_role
        
        # Find consultation in database
        consultation = db.consultations.find_one({
            '_id': ObjectId(consultation_id)
        })
        
        if not consultation:
            return jsonify({
                'error': 'Consultation not found'
            }), 404
            
        # Check if user is authorized
        if user_role == 'doctor' and str(consultation['doctor_id']) != str(user_id):
            return jsonify({
                'error': 'Unauthorized to access this consultation'
            }), 403
            
        if user_role == 'patient' and str(consultation['patient_id']) != str(user_id):
            return jsonify({
                'error': 'Unauthorized to access this consultation'
            }), 403
            
        # Check if consultation has a channel already
        if 'voice_channel' not in consultation:
            # Generate new channel info
            channel_name = f"consultation_{consultation_id}"
            
            # Generate token with 24 hour expiry
            expiration_time = int(time.time()) + 24 * 3600
            
            # Generate unique UIDs for doctor and patient
            doctor_uid = int(str(consultation['doctor_id'])[-6:])  # Last 6 digits of doctor_id
            patient_uid = int(str(consultation['patient_id'])[-6:])  # Last 6 digits of patient_id
            
            # Generate tokens for both users
            doctor_token = RtcTokenBuilder.buildTokenWithUid(
                AGORA_APP_ID,
                AGORA_APP_CERTIFICATE,
                channel_name,
                doctor_uid,
                1,  # Role: publisher
                expiration_time
            )
            
            patient_token = RtcTokenBuilder.buildTokenWithUid(
                AGORA_APP_ID,
                AGORA_APP_CERTIFICATE,
                channel_name,
                patient_uid,
                1,  # Role: publisher
                expiration_time
            )
            
            # Store channel info in database
            voice_channel = {
                'channel': channel_name,
                'doctor_token': doctor_token,
                'patient_token': patient_token,
                'doctor_uid': doctor_uid,
                'patient_uid': patient_uid,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=24)
            }
            
            db.consultations.update_one(
                {'_id': ObjectId(consultation_id)},
                {'$set': {'voice_channel': voice_channel}}
            )
            
            consultation['voice_channel'] = voice_channel
            
        # Return appropriate token based on user role
        channel_info = {
            'channel': consultation['voice_channel']['channel'],
            'token': consultation['voice_channel']['doctor_token'] if user_role == 'doctor' else consultation['voice_channel']['patient_token'],
            'uid': consultation['voice_channel']['doctor_uid'] if user_role == 'doctor' else consultation['voice_channel']['patient_uid']
        }
        
        return jsonify(channel_info)
        
    except Exception as e:
        print('Error in get_voice_channel:', str(e))
        return jsonify({
            'error': 'Failed to get voice channel information'
        }), 500

@consultation_bp.route('/api/consultations/<consultation_id>/complete', methods=['PUT'])
def complete_consultation(consultation_id):
    try:
        # Get user info from token
        user_id = request.user_id
        user_role = request.user_role
        
        # Only doctors can mark consultations as complete
        if user_role != 'doctor':
            return jsonify({
                'error': 'Only doctors can mark consultations as complete'
            }), 403
            
        # Find and update consultation
        result = db.consultations.update_one(
            {
                '_id': ObjectId(consultation_id),
                'doctor_id': ObjectId(user_id)
            },
            {
                '$set': {
                    'status': 'completed',
                    'completed_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({
                'error': 'Consultation not found or unauthorized'
            }), 404
            
        return jsonify({
            'message': 'Consultation marked as completed'
        })
        
    except Exception as e:
        print('Error in complete_consultation:', str(e))
        return jsonify({
            'error': 'Failed to complete consultation'
        }), 500

@consultation_bp.route('/api/consultations/<consultation_id>/notes', methods=['PUT'])
def update_consultation_notes(consultation_id):
    try:
        # Get user info from token
        user_id = request.user_id
        user_role = request.user_role
        
        # Get notes from request
        notes = request.json.get('notes', '')
        
        # Find consultation
        consultation = db.consultations.find_one({
            '_id': ObjectId(consultation_id)
        })
        
        if not consultation:
            return jsonify({
                'error': 'Consultation not found'
            }), 404
            
        # Check authorization
        if user_role == 'doctor' and str(consultation['doctor_id']) != str(user_id):
            return jsonify({
                'error': 'Unauthorized to update notes'
            }), 403
            
        if user_role == 'patient' and str(consultation['patient_id']) != str(user_id):
            return jsonify({
                'error': 'Unauthorized to update notes'
            }), 403
            
        # Update notes
        db.consultations.update_one(
            {'_id': ObjectId(consultation_id)},
            {'$set': {'notes': notes}}
        )
        
        return jsonify({
            'message': 'Notes updated successfully'
        })
        
    except Exception as e:
        print('Error in update_consultation_notes:', str(e))
        return jsonify({
            'error': 'Failed to update consultation notes'
        }), 500 