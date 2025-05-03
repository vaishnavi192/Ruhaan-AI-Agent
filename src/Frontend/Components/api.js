import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; 

//Speech-to-Text 
export const transcribeAudio = async (audioFile) => {
  const formData = new FormData();
  formData.append("file", audioFile);

  try {
    const response = await axios.post(`${API_BASE_URL}/transcribe/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data; // { transcription: "...", groq_response: "..." }
  } catch (error) {
    console.error("Error in transcription:", error);
    return null;
  }
};

// Process Text Query (AI Response from Llama-3)
export const processTextQuery = async (message) => {  // Rename parameter as message for clarity
    try {
    const response = await axios.post(`${API_BASE_URL}/process/`, 
      { message },  
      { headers: { "Content-Type": "application/json" } }
    )
    return response.data;
  } catch (error) {
    console.error("Error:", error.response ? error.response.data : error.message);
    throw error;
  }
};
// export const processTextQuery = async (query) => {
//     try {
//     console.log("Sending query:", query);
//     const response = await axios.post(
//       `${API_BASE_URL}/process/`,
//       { query }, // FastAPI will expect JSON input, and { query } ensures that query is sent as JSON.
//       { headers: { "Content-Type": "application/json" } }
//     );
//     console.log("Full API response:", response);
//     return response.data; 
//   } catch (error) {
//     console.error("Full Error", error);
//     throw error;
//   }
// };

//  Convert Text to Speech 
export const textToSpeech = async (text) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/text-to-speech`, {
      params: { transcription: text }, // Send text as query param
    });
    return response.data; 
  } catch (error) {
    console.error("Error in text-to-speech:", error);
    return null;
  }
};
