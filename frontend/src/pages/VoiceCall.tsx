import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Users, 
  MessageSquare, 
  Settings,
  Upload,
  FileText,
  Clock,
  User,
  Shield,
  Heart,
  Activity,
  Stethoscope,
  ArrowLeft,
  Loader2
} from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import VoiceCallComponent from '@/components/VoiceCallComponent';
import axios from 'axios';

// Using relative API paths with Vite proxy
const API_URL = '';

interface ConsultationData {
  id: string;
  appointment_id: string;
  doctor_name: string;
  patient_name: string;
  consultation_type: string;
  appointment_date: string;
  status: string;
  notes?: string;
  doctor_specialty?: string;
  doctor_experience?: number;
}

const VoiceCallPage = () => {
  const { consultationId, appointmentId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // State for consultation data
  const [consultation, setConsultation] = useState<ConsultationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [showParticipants, setShowParticipants] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [participants, setParticipants] = useState<any[]>([]);
  const [consultationNotes, setConsultationNotes] = useState('');

  // Determine consultation ID from route params
  const currentConsultationId = consultationId || appointmentId;

  useEffect(() => {
    if (currentConsultationId) {
      fetchConsultationData();
    } else {
      setLoading(false);
      setError('No consultation ID provided');
      toast({
        title: "Invalid consultation",
        description: "No consultation ID provided",
        variant: "destructive"
      });
    }
  }, [currentConsultationId]);

  // Fetch consultation data
  const fetchConsultationData = async () => {
    const token = localStorage.getItem('token');
    
    try {
      const response = await axios.get(`${API_URL}/api/consultations/join/${currentConsultationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const consultationData = response.data.consultation;
      
      // Validate consultation type
      if (consultationData.consultation_type !== 'voice' && consultationData.consultation_type !== 'phone') {
        throw new Error('Invalid consultation type. Expected voice or phone consultation.');
      }
      
      setConsultation(consultationData);
      setConsultationNotes(consultationData.notes || '');
      
      // Set participants based on user role
      const userRole = localStorage.getItem('user_role');
      const isDoctor = userRole === 'doctor';
      
      setParticipants([
        { 
          id: 1, 
          name: consultationData.doctor_name, 
          role: 'Doctor', 
          isDoctor: true, 
          isHost: isDoctor, 
          isActive: true 
        },
        { 
          id: 2, 
          name: consultationData.patient_name, 
          role: 'Patient', 
          isDoctor: false, 
          isHost: !isDoctor, 
          isActive: true 
        }
      ]);
      
    } catch (err: any) {
      console.error('Error fetching consultation data:', err);
      const errorMessage = err.response?.data?.error || "Could not retrieve consultation data";
      setError(errorMessage);
      toast({
        title: "Failed to load consultation",
        description: errorMessage,
        variant: "destructive"
      });
      
      // Navigate back to dashboard after error
      setTimeout(() => {
        const userRole = localStorage.getItem('user_role');
        navigate(`/dashboard/${userRole || 'patient'}`);
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  // Save consultation notes
  const saveConsultationNotes = async () => {
    const token = localStorage.getItem('token');
    
    try {
      await axios.put(`${API_URL}/api/consultations/${currentConsultationId}/notes`, {
        notes: consultationNotes
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast({
        title: "Notes Saved",
        description: "Consultation notes have been saved successfully",
      });
    } catch (err) {
      console.error('Error saving consultation notes:', err);
      toast({
        title: "Failed to save notes",
        description: "Could not save consultation notes",
        variant: "destructive"
      });
    }
  };

  // Handle call end
  const handleCallEnd = async () => {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('user_role');
    
    try {
      // If doctor is ending the call, mark consultation as completed
      if (userRole === 'doctor') {
        await axios.put(`${API_URL}/api/consultations/${currentConsultationId}/complete`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      // Save notes before navigating away
      await saveConsultationNotes();
      
      // Navigate back to dashboard after a short delay
      setTimeout(() => {
        navigate(`/dashboard/${userRole || 'patient'}`);
      }, 2000);
      
    } catch (err) {
      console.error('Error ending consultation:', err);
      toast({
        title: "Error",
        description: "Failed to end consultation properly",
        variant: "destructive"
      });
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (consultation) {
      interval = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [consultation]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const sendMessage = () => {
    if (newMessage.trim()) {
      setChatMessages([...chatMessages, {
        id: chatMessages.length + 1,
        sender: 'You',
        message: newMessage,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isDoctor: localStorage.getItem('user_role') === 'doctor'
      }]);
      setNewMessage('');
    }
  };

  const handleBackToDashboard = () => {
    const userRole = localStorage.getItem('user_role');
    navigate(`/dashboard/${userRole || 'patient'}`);
  };

  if (loading) {
    return (
      <div className="h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600 mb-4" />
        <p className="text-gray-600">Loading consultation...</p>
      </div>
    );
  }

  if (!consultation) {
    return (
      <div className="h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-2">Consultation Not Found</h2>
          <p className="text-gray-600 mb-4">Unable to find the consultation details.</p>
          <button 
            onClick={handleBackToDashboard}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleBackToDashboard}
            className="flex items-center space-x-2 px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ArrowLeft size={16} />
            <span className="text-sm">Back to Dashboard</span>
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">D</span>
            </div>
            <span className="font-semibold text-gray-800">DocEasy</span>
          </div>
          <div className="h-6 w-px bg-gray-300"></div>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Shield size={16} className="text-green-500" />
            <span>Secure Voice Consultation</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock size={16} />
            <span>{formatTime(callDuration)}</span>
          </div>
          <div className="text-sm text-gray-600">
            Call ID: {consultation.id}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Voice Call Area */}
        <div className="flex-1 relative flex items-center justify-center">
          <div className="max-w-4xl w-full px-8">
            {/* Doctor Profile */}
            <div className="text-center mb-12">
              <div className="relative inline-block mb-6">
                <div className="w-48 h-48 bg-gradient-to-br from-blue-600 to-blue-800 rounded-full flex items-center justify-center shadow-2xl">
                  <User size={80} className="text-white" />
                </div>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2">{consultation.doctor_name}</h2>
              <p className="text-xl text-blue-600 mb-2">{consultation.doctor_specialty || 'Doctor'}</p>
              <p className="text-gray-600">
                {consultation.doctor_experience ? `${consultation.doctor_experience}+ Years Experience` : 'Medical Professional'}
              </p>
            </div>

            {/* Voice Call Component */}
            <div className="mb-8">
              <VoiceCallComponent
                appointmentId={consultation.appointment_id}
                userRole={localStorage.getItem('user_role') as 'doctor' | 'patient'}
                onCallEnd={handleCallEnd}
              />
            </div>

            {/* Medical Information Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                <div className="flex items-center space-x-3">
                  <Stethoscope size={24} className="text-blue-600" />
                  <div>
                    <p className="text-xs text-gray-600">Consultation Type</p>
                    <p className="font-semibold">Voice Call</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                <div className="flex items-center space-x-3">
                  <Heart size={24} className="text-red-500" />
                  <div>
                    <p className="text-xs text-gray-600">Specialty</p>
                    <p className="font-semibold">{consultation.doctor_specialty || 'General'}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                <div className="flex items-center space-x-3">
                  <Activity size={24} className="text-green-500" />
                  <div>
                    <p className="text-xs text-gray-600">Session</p>
                    <p className="font-semibold">Active</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Notes */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <FileText size={20} className="text-blue-600" />
                <h3 className="text-lg font-semibold">Consultation Notes</h3>
              </div>
              <textarea 
                className="w-full border border-gray-200 rounded-lg p-4 resize-none text-sm"
                rows={4}
                placeholder="Take notes during your consultation..."
                value={consultationNotes}
                onChange={(e) => setConsultationNotes(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Side Panels */}
        {(showChat || showParticipants) && (
          <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
            {/* Panel Header */}
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
              <div className="flex space-x-4">
                <button
                  onClick={() => { setShowChat(true); setShowParticipants(false); }}
                  className={`px-3 py-1 rounded text-sm font-medium ${showChat ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-gray-800'}`}
                >
                  Chat
                </button>
                <button
                  onClick={() => { setShowParticipants(true); setShowChat(false); }}
                  className={`px-3 py-1 rounded text-sm font-medium ${showParticipants ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-gray-800'}`}
                >
                  Participants ({participants.length})
                </button>
              </div>
            </div>

            {/* Chat Panel */}
            {showChat && (
              <div className="flex-1 flex flex-col">
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {chatMessages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.isDoctor ? 'justify-start' : 'justify-end'}`}>
                      <div className={`max-w-xs rounded-lg p-3 ${
                        msg.isDoctor 
                          ? 'bg-gray-100 text-gray-800' 
                          : 'bg-blue-600 text-white'
                      }`}>
                        <div className="text-xs font-medium mb-1">
                          {msg.sender} • {msg.time}
                        </div>
                        <div className="text-sm">{msg.message}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-4 border-t border-gray-200">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      placeholder="Type a message..."
                      className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={sendMessage}
                      className="bg-blue-600 text-white rounded-lg px-4 py-2 text-sm hover:bg-blue-700"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Participants Panel */}
            {showParticipants && (
              <div className="flex-1 p-4">
                <div className="space-y-3">
                  {participants.map((participant) => (
                    <div key={participant.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        participant.isDoctor ? 'bg-blue-600' : 'bg-green-600'
                      }`}>
                        <User size={20} className="text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-sm">{participant.name}</span>
                          {participant.isHost && (
                            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Host</span>
                          )}
                        </div>
                        <p className="text-xs text-gray-600">{participant.role}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Control Bar */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left Controls */}
          <div className="flex items-center space-x-3">
            <button className="w-14 h-14 rounded-full bg-gray-200 hover:bg-gray-300 text-gray-700 flex items-center justify-center">
              <Upload size={24} />
            </button>
          </div>

          {/* Center Controls */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowParticipants(!showParticipants)}
              className="flex items-center space-x-2 px-4 py-3 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700"
            >
              <Users size={18} />
              <span className="text-sm">{participants.length}</span>
            </button>

            <button
              onClick={() => setShowChat(!showChat)}
              className="flex items-center space-x-2 px-4 py-3 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700"
            >
              <MessageSquare size={18} />
              <span className="text-sm">Chat</span>
            </button>

            <button className="flex items-center space-x-2 px-4 py-3 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700">
              <Settings size={18} />
              <span className="text-sm">Settings</span>
            </button>
          </div>

          {/* Right Controls */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-800">Call Duration</div>
              <div className="text-lg font-bold text-blue-600">{formatTime(callDuration)}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceCallPage;