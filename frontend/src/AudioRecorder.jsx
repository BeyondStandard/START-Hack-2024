import React, { useState } from 'react';
import axios from 'axios';

const AudioRecorder = () => {
  const [recorder, setRecorder] = useState(null);

  // Start Recording
  const startRecording = async () => {

    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    const newRecorder = new MediaRecorder(stream);
    newRecorder.start();

    newRecorder.ondataavailable = e => {
      if(e.data.size > 0) {
        sendAudioToServer(e.data);
      }
    };

    setRecorder(newRecorder);

  };

  const stopRecording = () => {
    if (recorder) {
      recorder.stop();
      setRecorder(null);
    }
  };

  const sendAudioToServer = async (audioData) => {
    const formData = new FormData();
    formData.append('file', audioData);

    // Send the audio data to the server
    await axios.post('http://localhost:8000/voice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  };

  return (
    <div>
      <button onClick={startRecording}>Start</button>
      <button onClick={stopRecording}>Stop</button>
    </div>
  );
};

export default AudioRecorder;
