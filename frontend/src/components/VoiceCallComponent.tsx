import React, { useState, useEffect, useRef } from 'react';
import { JitsiMeeting } from '@jitsi/react-sdk';
import { Mic, MicOff, Phone, PhoneOff, Loader2 } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

interface VoiceCallProps {
  appointmentId: string;
  userRole: 'doctor' | 'patient';
  onCallEnd?: () => void;
}

const VoiceCallComponent: React.FC<VoiceCallProps> = ({ appointmentId, userRole, onCallEnd }) => {
  const { toast } = useToast();
  const jitsiContainerRef = useRef<HTMLDivElement>(null);
  
  const [joinState, setJoinState] = useState<boolean>(false);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [jitsiApi, setJitsiApi] = useState<any>(null);
  const [participantCount, setParticipantCount] = useState<number>(0);

  // Generate a room name for the voice call
  const roomName = `doceasy_voice_${appointmentId}`;
  
  // Get user display name from localStorage
  const userName = localStorage.getItem('user_name') || (userRole === 'doctor' ? 'Doctor' : 'Patient');
  const userEmail = localStorage.getItem('user_email') || '';

  // Handle Jitsi iframe reference
  const handleJitsiIFrameRef = (iframeRef: any) => {
    if (iframeRef) {
      iframeRef.style.height = '0';
      iframeRef.style.width = '0';
      iframeRef.style.border = 'none';
      iframeRef.style.position = 'absolute';
    }
  };

  // Add error handling for media access issues
  const handleJitsiError = (error: any) => {
    console.error("Jitsi error encountered:", error);
    setIsLoading(false);
    
    toast({
      title: "Media access error",
      description: "Could not access microphone. Please check device permissions and try again.",
      variant: "destructive"
    });
  };

  // Handle Jitsi API ready event
  const handleJitsiApiReady = (api: any) => {
    setJitsiApi(api);
    setJoinState(true);
    setIsLoading(false);
    
    // Listen for mute/unmute events
    api.addListener('audioMuteStatusChanged', (muted: boolean) => {
      setIsMuted(muted);
    });
    
    // Force video off for voice calls
    api.executeCommand('toggleVideo');
    
    // Listen for participant count changes
    api.addListener('participantJoined', () => {
      const participants = api.getParticipantsInfo();
      setParticipantCount(participants.length);
    });
    
    api.addListener('participantLeft', () => {
      const participants = api.getParticipantsInfo();
      setParticipantCount(participants.length);
    });
    
    toast({
      title: "Connected to voice call",
      description: "You have joined the consultation successfully",
    });
  };

  // Join the call
  const joinCall = () => {
    setIsLoading(true);
  };

  // Leave the call
  const leaveCall = () => {
    if (jitsiApi) {
      jitsiApi.executeCommand('hangup');
      jitsiApi.dispose();
      setJitsiApi(null);
    }
    
    setJoinState(false);
    setParticipantCount(0);
    
    // Notify parent component
    if (onCallEnd) onCallEnd();

    toast({
      title: "Call ended",
      description: "You have left the voice consultation",
    });
  };

  // Toggle mute
  const toggleMute = () => {
    if (jitsiApi) {
      jitsiApi.executeCommand('toggleAudio');
    }
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (jitsiApi) {
        jitsiApi.dispose();
      }
    };
  }, [jitsiApi]);

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      {/* Hidden Jitsi container */}
      <div ref={jitsiContainerRef} className="hidden">
        {isLoading && !joinState && (
          <JitsiMeeting
            domain="meet.jit.si"
            roomName={roomName}
            getIFrameRef={handleJitsiIFrameRef}
            onApiReady={(api) => {
              handleJitsiApiReady(api);
              // Set up error event listeners on the API
              api.addListener('videoConferenceJoinError', (error: any) => {
                console.error("Jitsi join error:", error);
                setIsLoading(false);
                toast({
                  title: "Connection error",
                  description: "Failed to join call. Please check your microphone permissions.",
                  variant: "destructive"
                });
              });
              
              api.addListener('connectionFailed', () => {
                console.error("Jitsi connection failed");
                setIsLoading(false);
                toast({
                  title: "Connection failed",
                  description: "Failed to connect to the call server. Please try again.",
                  variant: "destructive"
                });
              });
            }}
            userInfo={{
              displayName: userName,
              email: userEmail
            }}
            configOverwrite={{
              startWithAudioMuted: false,
              startWithVideoMuted: true,
              prejoinPageEnabled: false,
              disableDeepLinking: true,
              startAudioOnly: true,
              disableVideo: true,
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
              enableAuth: false,
              authDomain: false,
              // Add improved device handling options
              p2p: {
                enabled: true,
                preferredCodec: 'VP8'
              },
              gumTimeoutMs: 15000, // Increase timeout for device initialization
              disableAudioLevels: true,
              websocket: 'wss://meet-jit-si-turnrelay.jitsi.net:443/colibri-ws',
              // Reduce video quality requirements for better compatibility
              resolution: 480,
              constraints: {
                video: {
                  height: {
                    ideal: 480,
                    max: 480,
                    min: 240
                  }
                }
              }
            }}
            interfaceConfigOverwrite={{
              TOOLBAR_BUTTONS: [
                'microphone', 'hangup', 'settings',
                'raisehand', 'fodeviceselection'
              ],
              HIDE_INVITE_MORE_HEADER: true,
              DISABLE_JOIN_LEAVE_NOTIFICATIONS: true,
              SHOW_JITSI_WATERMARK: false,
              TOOLBAR_ALWAYS_VISIBLE: true,
              AUTHENTICATION_REQUIRED: false
            }}
          />
        )}
      </div>
      
      {/* Connection Status */}
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${joinState ? 'bg-green-500' : 'bg-gray-300'}`} />
        <span className="text-sm text-gray-600">
          {joinState ? 'Connected' : 'Not Connected'}
        </span>
        {participantCount > 0 && (
          <span className="text-sm text-green-600">
            ({participantCount} participant{participantCount !== 1 ? 's' : ''} connected)
          </span>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center space-x-4">
        {joinState && (
          <Button
            variant={isMuted ? "destructive" : "outline"}
            size="lg"
            className="rounded-full w-12 h-12"
            onClick={toggleMute}
          >
            {isMuted ? <MicOff /> : <Mic />}
          </Button>
        )}

        <Button
          variant={joinState ? "destructive" : "default"}
          size="lg"
          className="rounded-full"
          onClick={joinState ? leaveCall : joinCall}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : joinState ? (
            <>
              <PhoneOff className="mr-2" />
              End Call
            </>
          ) : (
            <>
              <Phone className="mr-2" />
              Join Call
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default VoiceCallComponent;