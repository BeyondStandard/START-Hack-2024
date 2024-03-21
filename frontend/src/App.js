import React, {useState, useEffect} from 'react';
import './App.css';
import AudioRecorder from "./AudioRecorder";

function App() {
  const [predictions, setPredictions]: Object<string, number> = useState(
    {
      "positive": 16,
      "negative": 2,
      "neutral": 3,
    }
  );
  const [total, setTotal]: number = useState(21)
  const [score, setScore]: number = useState(83.3)
  const [lastScore, setLastScore] = useState(score);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');

    socket.onmessage = (event) => {
      console.log(event)
      const newPrediction = JSON.parse(event.data);
      console.log(newPrediction);
      setTotal(total + 1)

      switch (newPrediction) {
        case "positive":
          setPredictions({...predictions, positive: predictions.positive + 1})
          break;
        case "negative":
          setPredictions({...predictions, negative: predictions.negative + 1})
          break;
        case "neutral":
          setPredictions({...predictions, neutral: predictions.neutral + 1})
          break;
        default:
          console.log(newPrediction);
      }
      setPredictions(predictions => [...predictions, newPrediction.value]);
      setLastScore(score);
      setScore((predictions.positive * 100 + predictions.neutral * 50) / total)
    };

    return () => {
      if (socket.readyState === 1) {
        socket.close();
      }
    };
  }, []);

  console.log(score)
  console.log(lastScore)
  return (
    <div className={`bar-wrapper ${score > lastScore ? 'greenFade' :  score < lastScore ? 'redFade' : null}`}>
      {score}
      <div className="bar-border">
        <div style={{width: `${(predictions.positive / total) * 100}%`, backgroundColor: '#68e86d'}}></div>
        <div style={{width: `${(predictions.neutral / total) * 100}%`, backgroundColor: '#dedede'}}></div>
        <div style={{width: `${(predictions.negative / total) * 100}%`, backgroundColor: '#ed8e8e'}}></div>
      </div>
      <AudioRecorder/>
    </div>
  )
}

export default App;
