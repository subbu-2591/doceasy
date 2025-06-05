import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Video, VideoOff, Mic, MicOff, Phone, PhoneOff, MessageCircle, Settings, ArrowLeft, Clock, User } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import axios from 'axios';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

interface ConsultationData {
  appointment_id: string;
  video_call_id: string;
  consultation_type: string;
  patient_name: string;
  doctor_name: string;
  appointment_date: string;
  call_url: string;
  chat_url: string;
}

const VideoCall = () => {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();

  // State
  const [consultation, setConsultation] = useState<ConsultationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [callActive, setCallActive] = useState(false);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [callStartTime, setCallStartTime] = useState<Date | null>(null);
  const [callDuration, setCallDuration] = useState('00:00');

  useEffect(() => {
    fetchConsultationData();
  }, [appointmentId]);

  // Update call duration
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (callActive && callStartTime) {
      interval = setInterval(() => {
        const now = new Date();
        const diff = now.getTime() - callStartTime.getTime();
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        setCallDuration(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [callActive, callStartTime]);

  const fetchConsultationData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/api/consultations/join/${appointmentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setConsultation(response.data.consultation);
    } catch (error: any) {
      toast({
        title: "Access Denied",
        description: error.response?.data?.error || "Unable to join consultation",
        variant: "destructive"
      });
      navigate('/dashboard/patient');
    } finally {
      setLoading(false);
    }
  };

  const startCall = () => {
    setCallActive(true);
    setCallStartTime(new Date());
    toast({
      title: "Call Started",
      description: "You are now connected to the consultation",
    });
  };

  const endCall = async () => {
    setCallActive(false);
    setCallStartTime(null);
    setCallDuration('00:00');
    
    toast({
      title: "Call Ended",
      description: "Thank you for using our consultation service",
    });
    
    // Navigate back to dashboard after a short delay
    setTimeout(() => {
      navigate('/dashboard/patient');
    }, 2000);
  };

  const toggleVideo = () => {
    setVideoEnabled(!videoEnabled);
    toast({
      title: videoEnabled ? "Video Disabled" : "Video Enabled",
      description: videoEnabled ? "Your camera is now off" : "Your camera is now on",
    });
  };

  const toggleAudio = () => {
    setAudioEnabled(!audioEnabled);
    toast({
      title: audioEnabled ? "Microphone Muted" : "Microphone Unmuted",
      description: audioEnabled ? "Your microphone is now muted" : "Your microphone is now unmuted",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <div className="flex-grow flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical-blue mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading consultation...</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  if (!consultation) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <div className="flex-grow flex items-center justify-center">
          <Card className="w-full max-w-md">
            <CardContent className="pt-6 text-center">
              <h2 className="text-xl font-semibold mb-2">Consultation Not Found</h2>
              <p className="text-gray-600 mb-4">Unable to find the consultation details.</p>
              <Button onClick={() => navigate('/dashboard/patient')}>
                Return to Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-900">
      <Navbar />
      
      <div className="flex-grow flex flex-col">
        {/* Header */}
        <div className="bg-white border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate('/dashboard/patient')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-lg font-semibold">Video Consultation</h1>
                <p className="text-sm text-gray-600">with Dr. {consultation.doctor_name}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {callActive && (
                <div className="flex items-center space-x-2 text-sm">
                  <Clock className="h-4 w-4 text-green-600" />
                  <span className="font-mono text-green-600">{callDuration}</span>
                  <Badge variant="default" className="bg-green-600">Live</Badge>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Video Area */}
        <div className="flex-grow flex">
          <div className="flex-grow bg-gray-900 relative">
            {/* Main video area */}
            <div className="h-full flex items-center justify-center">
              {!callActive ? (
                <Card className="w-full max-w-md mx-4">
                  <CardHeader className="text-center">
                    <CardTitle>Ready to Start Consultation?</CardTitle>
                    <CardDescription>
                      Dr. {consultation.doctor_name} is waiting to begin your {consultation.consultation_type} consultation
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-center space-y-2">
                      <div className="w-20 h-20 bg-medical-blue rounded-full flex items-center justify-center mx-auto">
                        <User className="h-10 w-10 text-white" />
                      </div>
                      <p className="font-medium">{consultation.patient_name}</p>
                      <p className="text-sm text-gray-600">Patient</p>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span>Consultation Type:</span>
                        <Badge variant="outline" className="capitalize">
                          {consultation.consultation_type}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Scheduled Time:</span>
                        <span>{new Date(consultation.appointment_date).toLocaleTimeString()}</span>
            </div>
          </div>
          
                    <Button 
                      onClick={startCall} 
                      className="w-full bg-green-600 hover:bg-green-700"
                      size="lg"
                    >
                      <Video className="h-5 w-5 mr-2" />
                      Start Consultation
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="h-full w-full flex flex-col">
                  {/* Video feeds */}
                  <div className="flex-grow flex">
                    {/* Doctor video (main) */}
                    <div className="flex-grow bg-gray-800 relative border border-gray-600 rounded-lg mx-4 my-4">
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center text-white">
                          <div className="w-24 h-24 bg-medical-blue rounded-full flex items-center justify-center mx-auto mb-4">
                            <User className="h-12 w-12 text-white" />
                          </div>
                          <h3 className="text-lg font-medium">Dr. {consultation.doctor_name}</h3>
                          <p className="text-gray-300">Doctor</p>
                        </div>
                      </div>
                      <div className="absolute top-4 left-4">
                        <Badge className="bg-green-600">Doctor</Badge>
                </div>
              </div>
              
                    {/* Patient video (small) */}
                    <div className="w-64 h-48 bg-gray-800 border border-gray-600 rounded-lg absolute bottom-20 right-6">
                      <div className="h-full flex items-center justify-center">
                        <div className="text-center text-white">
                          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">
                            <User className="h-8 w-8 text-white" />
                          </div>
                          <p className="text-sm">You</p>
                        </div>
                      </div>
                      <div className="absolute top-2 left-2">
                        <Badge variant="secondary" className="text-xs">You</Badge>
                      </div>
                      {!videoEnabled && (
                        <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center">
                          <VideoOff className="h-8 w-8 text-white" />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
                </div>
              </div>
              
        {/* Controls */}
        {callActive && (
          <div className="bg-white border-t px-6 py-4">
            <div className="flex items-center justify-center space-x-4">
                <Button 
                variant={audioEnabled ? "default" : "destructive"}
                size="lg"
                onClick={toggleAudio}
                className="rounded-full w-12 h-12 p-0"
              >
                {audioEnabled ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
                </Button>
                
                <Button 
                variant={videoEnabled ? "default" : "destructive"}
                size="lg"
                onClick={toggleVideo}
                className="rounded-full w-12 h-12 p-0"
              >
                {videoEnabled ? <Video className="h-5 w-5" /> : <VideoOff className="h-5 w-5" />}
                </Button>
                
                <Button 
                variant="destructive"
                size="lg"
                onClick={endCall}
                className="rounded-full w-12 h-12 p-0"
                >
                <PhoneOff className="h-5 w-5" />
                </Button>
                
                <Button 
                  variant="outline" 
                size="lg"
                className="rounded-full w-12 h-12 p-0"
                >
                  <MessageCircle className="h-5 w-5" />
                </Button>
                
                <Button 
                  variant="outline" 
                size="lg"
                className="rounded-full w-12 h-12 p-0"
              >
                <Settings className="h-5 w-5" />
                </Button>
            </div>
            
            <div className="text-center mt-3">
              <p className="text-sm text-gray-600">
                {audioEnabled ? '🎤' : '🔇'} {videoEnabled ? '📹' : '📷'} 
                {callActive ? ' • Call in progress' : ' • Call not started'}
              </p>
                </div>
              </div>
            )}
      </div>
      
      <Footer />
    </div>
  );
};

export default VideoCall;
