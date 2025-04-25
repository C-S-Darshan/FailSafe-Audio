import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css"; // Importing the CSS file

function App() {
  const [audioFiles, setAudioFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);

  // Fetch audio files from the backend
  useEffect(() => {
    async function fetchAudioFiles() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/audio-files");
        setAudioFiles(response.data);
      } catch (error) {
        console.error("Error fetching audio files", error);
      }
    }
    fetchAudioFiles();
  }, []);

  // Handle file selection
  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setTranscription(""); // Reset transcription when a new file is selected
  };

  // Transcribe the selected audio file
  const handleTranscribe = async () => {
    if (!selectedFile) return;
  
    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/transcribe", 
        { file_key: selectedFile }, // Ensure it's wrapped in an object
        { headers: { "Content-Type": "application/json" } } // Explicitly set JSON header
      );
      setTranscription(response.data.transcription);
    } catch (error) {
      console.error("Error transcribing audio", error);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Audio Transcriber</h1>

      {/* Audio File List */}
      <div className="audio-list">
        <h2>Available Audio Files</h2>
        <ul>
          {audioFiles.length > 0 ? (
            audioFiles.map((file) => (
              <li
                key={file}
                className={`file-item ${selectedFile === file ? "selected" : ""}`}
                onClick={() => handleFileSelect(file)}
              >
                {file}
              </li>
            ))
          ) : (
            <p>No audio files available.</p>
          )}
        </ul>
      </div>

      {/* Selected File & Transcribe Button */}
      {selectedFile && (
        <div className="selected-file">
          <h2>Selected File:</h2>
          <p>{selectedFile}</p>
          <button onClick={handleTranscribe} className="transcribe-btn">
            {loading ? "Transcribing..." : "Get Transcription"}
          </button>
        </div>
      )}

      {/* Transcription Result */}
      {transcription && (
        <div className="transcription">
          <h2>Transcription:</h2>
          <p>{transcription}</p>
        </div>
      )}
    </div>
  );
}

export default App;
