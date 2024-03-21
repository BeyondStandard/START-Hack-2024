import React, { useState, useEffect } from 'react';

function App() {
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');

    socket.onmessage = (event) => {
      console.log(event)
      const newPrediction = JSON.parse(event.data);
      console.log(newPrediction);
      setPredictions(predictions => [...predictions, newPrediction.value]);
    };

    return () => {
      if (socket.readyState === 1) {
        socket.close();
      }
    };
  }, []);

  return (
    <div>
      <h1>Sentiment Analysis Predictions</h1>
      <ul>
        {predictions.map((prediction, index) => (
          <li key={index}>{prediction}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
