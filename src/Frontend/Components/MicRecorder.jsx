import { useState, useRef } from "react";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000"; 

const MicRecorder = ({ setMessages }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, {mimeType: 'audio/wav'} );
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        try {
          const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" });
          const formData = new FormData();
          formData.append("file", audioBlob);

          // Send to WhisperAPI for transcription
          const response = await axios.post(
            `${API_BASE_URL}/api/speech/transcribe`,
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
            }
          );

          if (response.data.status === "success") {
            const { transcription, response_text } = response.data.data;
            setTranscription(transcription);
            
            // Add to chat messages
            setMessages((prev) => [
              ...prev,
              { text: transcription, sender: "user" },
              { text: response_text, sender: "bot" }
            ]);
            
            // Get voice response from ElevenLabs
            try {
              console.log("Getting voice response for:", response_text);
              const ttsResponse = await axios.post(
                `${API_BASE_URL}/api/speech/text-to-speech/`, 
                { text: response_text },
                { 
                  responseType: 'blob',
                  headers: { "Content-Type": "application/json" } 
                }
              );
              console.log("TTS response received:", ttsResponse);
              if (ttsResponse.data instanceof Blob) {
                const audioUrl = URL.createObjectURL(ttsResponse.data);
                const audio = new Audio(audioUrl);
                audio.play();
              }
            } catch (error) {
              console.error("Error playing audio:", error);
            }
          }
        } catch (error) {
          console.error("Error:", error);
          setTranscription("Error processing audio");
        }
      };

      audioChunks.current = [];
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  return (
    <div className="voice-listener" onClick={isRecording ? stopRecording : startRecording}>
      <div className={`voice-circle ${isRecording ? "recording" : ""}`}>
        <img src="/assets/ruhhhh.png" alt="Mic" className="mic-image" />
      </div>
      {transcription && <p><b>Transcription:</b> {transcription}</p>}
    </div>
  );
};

export default MicRecorder;
