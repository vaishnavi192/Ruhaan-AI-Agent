import { useState, useRef } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; 

const MicRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);

    mediaRecorderRef.current.ondataavailable = (event) => {
      audioChunks.current.push(event.data);
    };

    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" });
      const formData = new FormData();
      formData.append("file", audioBlob);

      try {
        const response = await axios.post(`${API_BASE_URL}/transcribe/`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        withCredentials: true,
      });
        
        setTranscription(response.data.transcription);
      } catch (error) {
        console.error("Error transcribing:", error);
      }
    };

    audioChunks.current = [];
    mediaRecorderRef.current.start();
    setIsRecording(true);
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
