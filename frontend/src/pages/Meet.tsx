import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Mic, 
  MicOff, 
  Video, 
  VideoOff, 
  Phone, 
  PhoneOff, 
  Users, 
  MessageSquare, 
  Settings,
  Monitor,
  Upload,
  FileText,
  Clock,
  User,
  Shield,
  ArrowLeft,
  Loader2,
  X
} from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import axios from 'axios';
import { JitsiMeeting } from '@jitsi/react-sdk';
import { Button } from '@/components/ui/button';

// Using relative API paths with Vite proxy
const API_URL = '';

interface ConsultationData {
  _id: string;
  doctor_id: string;
  patient_id: string;
  appointment_id: string;
  doctor_name: string;
  patient_name: string;
  consultation_type: string;
  scheduled_time: string;
  status: string;
  notes?: string;
  doctor_specialty?: string;
  doctor_experience?: number;
  duration?: number;
  chat_messages?: Array<{
    sender: string;
    message: string;
    timestamp: string;
    sender_type: 'doctor' | 'patient';
  }>;
  room_name?: string;
}

const VideoCallPage = () => {
  const { consultationId, appointmentId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const jitsiContainerRef = useRef<HTMLDivElement>(null);
  
  // State for consultation data
  const [consultation, setConsultation] = useState<ConsultationData | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [isCallActive, setIsCallActive] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const [showParticipants, setShowParticipants] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [participants, setParticipants] = useState<any[]>([]);
  const [jitsiApi, setJitsiApi] = useState<any>(null);
  // Add state for Quick Notes visibility
  const [showQuickNotes, setShowQuickNotes] = useState(false);
  const [notesContent, setNotesContent] = useState('');

  // Determine consultation ID from route params
  const currentConsultationId = consultationId || appointmentId;

  useEffect(() => {
    if (currentConsultationId) {
      fetchConsultationData();
    } else {
      setLoading(false);
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
      const response = await axios.get(`${API_URL}/api/consultations/${currentConsultationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const consultationData = response.data.consultation;
      setConsultation(consultationData);
      
      // Set initial chat messages if available
      if (consultationData.chat_messages) {
        setChatMessages(consultationData.chat_messages);
      } else {
        setChatMessages([
          { 
            id: 1, 
            sender: consultationData.doctor_name, 
            message: 'Hello! I can see you clearly. How are you feeling today?', 
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), 
            isDoctor: true 
          }
        ]);
      }
      
      // Set participants
      setParticipants([
        { 
          id: 1, 
          name: consultationData.doctor_name, 
          role: consultationData.doctor_specialty || 'Doctor', 
          isDoctor: true, 
          isHost: true 
        },
        { 
          id: 2, 
          name: 'You (Patient)', 
          role: 'Patient', 
          isDoctor: false, 
          isHost: false 
        }
      ]);
      
    } catch (err: any) {
      console.error('Error fetching consultation data:', err);
      toast({
        title: "Failed to load consultation",
        description: err.response?.data?.error || "Could not retrieve consultation data",
        variant: "destructive"
      });
      
      // Set default data for demo purposes
      setConsultation({
        _id: currentConsultationId || 'demo',
        doctor_id: 'demo_doctor',
        patient_id: 'demo_patient',
        appointment_id: currentConsultationId || 'demo',
        doctor_name: 'Dr. Sarah Wilson',
        patient_name: 'Patient',
        consultation_type: 'video',
        scheduled_time: new Date().toISOString(),
        status: 'active',
        doctor_specialty: 'Cardiologist'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isCallActive) {
      interval = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isCallActive]);

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
        isDoctor: false
      }]);
      setNewMessage('');
    }
  };

  const handleEndCall = () => {
    if (jitsiApi) {
      jitsiApi.executeCommand('hangup');
    }
    
    setIsCallActive(false);
    toast({
      title: "Call Ended",
      description: "The video consultation has ended successfully",
    });
    
    // Navigate back to dashboard after a short delay
    setTimeout(() => {
      const userRole = localStorage.getItem('user_role');
      if (userRole === 'doctor') {
        navigate('/dashboard/doctor');
      } else {
        navigate('/dashboard/patient');
      }
    }, 2000);
  };

  const handleBackToDashboard = () => {
    const userRole = localStorage.getItem('user_role');
    if (userRole === 'doctor') {
      navigate('/dashboard/doctor');
    } else {
      navigate('/dashboard/patient');
    }
  };

  // Handle Jitsi iframe reference
  const handleJitsiIFrameRef = (iframeRef: any) => {
    if (iframeRef) {
      iframeRef.style.height = '100%';
      iframeRef.style.width = '100%';
      iframeRef.style.border = 'none';
    }
  };

  // Handle Jitsi API ready event
  const handleJitsiApiReady = (api: any) => {
    setJitsiApi(api);
    
    // Listen for mute/unmute events
    api.addListener('audioMuteStatusChanged', (muted: boolean) => {
      setIsMuted(muted);
    });
    
    // Listen for video on/off events
    api.addListener('videoMuteStatusChanged', (muted: boolean) => {
      setIsVideoOff(muted);
    });
    
    // Listen for participant joined/left events
    api.addListener('participantJoined', (participant: any) => {
      const newParticipant = {
        id: participant.id,
        name: participant.displayName || 'Guest',
        role: 'Participant',
        isDoctor: false,
        isHost: false
      };
      setParticipants(prev => [...prev, newParticipant]);
    });
    
    api.addListener('participantLeft', (participant: any) => {
      setParticipants(prev => prev.filter(p => p.id !== participant.id));
    });
  };

  if (loading) {
    return (
      <div className="h-screen bg-gray-900 flex flex-col items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600 mb-4" />
        <p className="text-white">Loading consultation...</p>
      </div>
    );
  }

  if (!consultation) {
    return (
      <div className="h-screen bg-gray-900 flex flex-col items-center justify-center">
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

  // Generate a room name for the consultation
  const roomName = `doceasy_consultation_${consultation._id || appointmentId || Date.now().toString()}`;
  
  // Get user information
  const userName = localStorage.getItem('user_name') || 'User';
  const userEmail = localStorage.getItem('user_email') || '';
  const userRole = localStorage.getItem('user_role') || 'patient';

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
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
            <span>Secure Consultation</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock size={16} />
            <span>{formatTime(callDuration)}</span>
          </div>
          <div className="text-sm text-gray-600">
            Consultation ID: {consultation._id}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Video Area */}
        <div className="flex-1 relative">
          {/* Main Video */}
          <div className="h-full bg-gray-800 relative overflow-hidden" ref={jitsiContainerRef}>
            {isCallActive && (
              <JitsiMeeting
                domain="meet.jit.si"
                roomName={roomName}
                getIFrameRef={handleJitsiIFrameRef}
                onApiReady={handleJitsiApiReady}
                userInfo={{
                  displayName: userName,
                  email: userEmail
                }}
                configOverwrite={{
                  startWithAudioMuted: false,
                  startWithVideoMuted: false,
                  prejoinPageEnabled: false,
                  disableDeepLinking: true,
                  hideConferenceSubject: true,
                  hideConferenceTimer: true,
                  disableInviteFunctions: true,
                  requireDisplayName: false,
                  enableClosePage: false,
                  disableThirdPartyRequests: true,
                  disableLocalVideoFlip: true,
                  disableProfile: true,
                  hideLobbyButton: true,
                  disableInband: true,
                  enableWelcomePage: false,
                  enableInsecureRoomNameWarning: false,
                  enableNoisyMicDetection: true,
                  disableInitialGUM: false,
                  startSilent: false,
                  enableAuth: false,
                  authDomain: false,
                  p2p: {
                    enabled: true,
                    preferredCodec: 'VP9'
                  },
                  gumTimeoutMs: 15000,
                  resolution: 720,
                  constraints: {
                    video: {
                      height: {
                        ideal: 720,
                        max: 720,
                        min: 240
                      }
                    }
                  },
                  disableAudioLevels: true,
                  websocket: 'wss://meet-jit-si-turnrelay.jitsi.net:443/colibri-ws',
                  toolbarButtons: [
                    'microphone', 'camera', 'desktop', 'fullscreen',
                    'fodeviceselection', 'hangup', 'chat',
                    'settings', 'raisehand', 'videoquality', 'filmstrip',
                    'tileview'
                  ]
                }}
                interfaceConfigOverwrite={{
                  DISABLE_JOIN_LEAVE_NOTIFICATIONS: true,
                  SHOW_JITSI_WATERMARK: false,
                  HIDE_INVITE_MORE_HEADER: true,
                  DISABLE_FOCUS_INDICATOR: true,
                  TOOLBAR_ALWAYS_VISIBLE: true,
                  DISABLE_DOMINANT_SPEAKER_INDICATOR: true,
                  AUTHENTICATION_REQUIRED: false,
                  SHOW_CHROME_EXTENSION_BANNER: false,
                  CONNECTION_INDICATOR_AUTO_HIDE_ENABLED: true,
                  DISABLE_PRESENCE_STATUS: true,
                  DISABLE_RINGING: true,
                  INITIAL_TOOLBAR_TIMEOUT: 20000,
                  TOOLBAR_TIMEOUT: 4000,
                  DEFAULT_BACKGROUND: '#040404'
                }}
              />
            )}
            
            {!isCallActive && (
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center">
                <div className="text-center text-white">
                  <div className="w-32 h-32 bg-white/20 rounded-full flex items-center justify-center mb-4 mx-auto">
                    <User size={48} />
                  </div>
                  <h3 className="text-xl font-semibold">Call Ended</h3>
                  <p className="text-blue-200">The consultation has been completed</p>
                </div>
              </div>
            )}

            {/* Call Status Indicators */}
            <div className="absolute top-4 left-4 flex space-x-2">
              {!isCallActive && (
                <div className="bg-red-500 text-white px-3 py-1 rounded-full text-sm flex items-center space-x-1">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  <span>Call Ended</span>
                </div>
              )}
              <div className="bg-black/50 text-white px-3 py-1 rounded-full text-sm">
                HD Quality
              </div>
            </div>

            {/* Quick Notes Toggle Button */}
            <div className="absolute bottom-4 left-4">
              <button
                onClick={() => setShowQuickNotes(!showQuickNotes)}
                className="bg-white/90 hover:bg-white backdrop-blur-sm rounded-lg p-2 flex items-center space-x-2 shadow-md transition-all"
              >
                <FileText size={16} className="text-blue-600" />
                <span className="text-sm font-medium">{showQuickNotes ? "Hide Notes" : "Show Notes"}</span>
              </button>
            </div>

            {/* Medical Notes Overlay - Conditionally rendered */}
            {showQuickNotes && (
              <div className="absolute bottom-20 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 max-w-xs shadow-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <FileText size={16} className="text-blue-600" />
                    <span className="text-sm font-medium">Quick Notes</span>
                  </div>
                  <button 
                    onClick={() => setShowQuickNotes(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={16} />
                  </button>
                </div>
                <textarea 
                  className="w-full text-xs border border-gray-200 rounded p-2 resize-none"
                  rows={3}
                  placeholder="Add consultation notes..."
                  value={notesContent}
                  onChange={(e) => setNotesContent(e.target.value)}
                />
              </div>
            )}
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
    </div>
  );
};

export default VideoCallPage; 