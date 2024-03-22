import React, {useState, useEffect} from 'react';
import './App.css';

function App() {
  const [predictions, setPredictions]: Array<Object<string, string>> = useState(
    [
      {"sentiment": "positive", "emotion": "grateful"},
      {"sentiment": "positive", "emotion": "happy"},
      {"sentiment": "positive", "emotion": "grateful"},
      {"sentiment": "positive", "emotion": "grateful"},
      {"sentiment": "positive", "emotion": "neutral"},
      {"sentiment": "positive", "emotion": "happy"},
      {"sentiment": "positive", "emotion": "neutral"},
      {"sentiment": "positive", "emotion": "relieved"},
      {"sentiment": "positive", "emotion": "relieved"},
      {"sentiment": "positive", "emotion": "neutral"},
      {"sentiment": "positive", "emotion": "neutral"},
      {"sentiment": "positive", "emotion": "neutral"},
      {"sentiment": "positive", "emotion": "grateful"},
      {"sentiment": "positive", "emotion": "neutral"},
      {"sentiment": "positive", "emotion": "neutral"},
      {"sentiment": "positive", "emotion": "happy"},
      {"sentiment": "negative", "emotion": "annoyed"},
      {"sentiment": "negative", "emotion": "angry"},
      {"sentiment": "neutral", "emotion": "neutral"},
      {"sentiment": "neutral", "emotion": "neutral"},
      {"sentiment": "neutral", "emotion": "neutral"},
    ]
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

      setPredictions(predictions => [...predictions, newPrediction]);
      console.log(predictions)
      setLastScore(score);
      setScore(predictions.reduce((score, sentiment) => {
        if (sentiment.sentiment === "positive") {
          score += 100;
        } else if (sentiment.sentiment === "negative") {
          score += 0;
        } else if (sentiment.sentiment === "neutral") {
          score += 50;
        }
        return score;
      }, 0) / total);
    };
    console.log(score)

    return () => {
      if (socket.readyState === 1) {
        socket.close();
      }
    };
  }, []);

  return (
    <div className={`bar-wrapper ${score > lastScore ? 'greenFade' : score < lastScore ? 'redFade' : null}`}>
      {score}
      <div className="bar-border">
        <div style={{
          width: `${(predictions.reduce((count, emotionObject) => {
            return emotionObject.sentiment === 'positive' ? count + 1 : count;
          }, 0) / total) * 100}%`, backgroundColor: '#68e86d'
        }}></div>
        <div style={{
          width: `${(predictions.reduce((count, emotionObject) => {
            return emotionObject.sentiment === 'neutral' ? count + 1 : count;
          }, 0) / total) * 100}%`, backgroundColor: '#dedede'
        }}></div>
        <div style={{
          width: `${(predictions.reduce((count, emotionObject) => {
            return emotionObject.sentiment === 'negative' ? count + 1 : count;
          }, 0) / total) * 100}%`, backgroundColor: '#ed8e8e'
        }}></div>
      </div>
    </div>
  )
}

export default App;
