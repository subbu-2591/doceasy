import React, { useState, useEffect } from 'react';
import { JitsiMeeting } from '@jitsi/react-sdk';
import { useNavigate } from 'react-router-dom';

interface MeetProps {
    doctorId: string;
    patientId: string;
    onEndCall?: () => void;
}

const Meet: React.FC<MeetProps> = ({ doctorId, patientId, onEndCall }) => {
    const [videoCall, setVideoCall] = useState<boolean>(true);
    const navigate = useNavigate();

    // Generate a unique room name based on doctorId and patientId
    // Ensure values are not undefined by using fallback empty strings
    const safeDocId = doctorId || 'unknown_doctor';
    const safePatId = patientId || 'unknown_patient';
    const roomName = `doceasy_consultation_${safeDocId}_${safePatId}`;
    
    // Get user display name from localStorage
    const userName = localStorage.getItem('user_name') || 'User';
    const userEmail = localStorage.getItem('user_email') || '';
    
    const handleJitsiIFrameRef = (iframeRef: any) => {
        iframeRef.style.height = '100%';
        iframeRef.style.width = '100%';
    };
    
    // Handle Jitsi errors
    const handleJitsiError = (error: any) => {
        console.error("Jitsi error:", error);
        // Inform the user
        alert("Could not access camera or microphone. Please check device permissions and try again.");
    };

    const handleReadyToClose = () => {
        setVideoCall(false);
        if (onEndCall) {
            onEndCall();
        }
        // Navigate back to appropriate page
        navigate(-1);
    };

    const styles = {
        container: {
            width: '100%',
            height: '100vh',
            display: 'flex',
            flex: 1,
            backgroundColor: '#007bff0a'
        },
        videoContainer: {
            width: '100%',
            height: '100%',
            display: 'flex',
            flex: 1
        },
        waitingMessage: {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            width: '100%',
            height: '100%',
            fontSize: '1.2rem',
            color: '#666'
        }
    };

    return (
        <div style={styles.container}>
            {videoCall ? (
                <div style={styles.videoContainer}>
                    <JitsiMeeting
                        domain="meet.jit.si"
                        roomName={roomName}
                        getIFrameRef={handleJitsiIFrameRef}
                        userInfo={{
                            displayName: userName,
                            email: userEmail
                        }}
                        onApiReady={(api) => {
                            // Set up error event listeners on the API
                            api.addListener('videoConferenceJoinError', (error: any) => {
                                console.error("Failed to join conference:", error);
                                alert("Could not join the meeting. Please check your device permissions.");
                            });
                            
                            api.addListener('connectionFailed', () => {
                                console.error("Connection failed");
                                alert("Connection to the meeting room failed. Please check your internet connection.");
                            });
                        }}
                        configOverwrite={{
                            startWithAudioMuted: false,
                            startWithVideoMuted: false,
                            prejoinPageEnabled: true,
                            disableDeepLinking: true,
                            // Add better device handling
                            p2p: {
                                enabled: true,
                                preferredCodec: 'VP8'
                            },
                            resolution: 720,
                            gumTimeoutMs: 15000, // Increase timeout for device initialization
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
                            websocket: 'wss://meet-jit-si-turnrelay.jitsi.net:443/colibri-ws'
                        }}
                        interfaceConfigOverwrite={{
                            TOOLBAR_BUTTONS: [
                                'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
                                'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
                                'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
                                'videoquality', 'filmstrip', 'feedback', 'stats', 'shortcuts',
                                'tileview', 'videobackgroundblur', 'download', 'help', 'mute-everyone',
                                'security'
                            ],
                            SHOW_CHROME_EXTENSION_BANNER: false,
                            CONNECTION_INDICATOR_AUTO_HIDE_ENABLED: true,
                            DISABLE_PRESENCE_STATUS: true,
                            DISABLE_RINGING: true
                        }}
                        onReadyToClose={handleReadyToClose}
                    />
                </div>
            ) : (
                <div style={styles.waitingMessage}>
                    Call has ended
                </div>
            )}
        </div>
    );
};

export default Meet; 