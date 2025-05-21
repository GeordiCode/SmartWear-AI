import { useState, useRef, useEffect } from "react";
import * as faceapi from "face-api.js";
import { Button } from "./components/ui/button";
import { Card, CardContent } from "./components/ui/card";

export default function EmotionBasedFashion() {
  const [emotion, setEmotion] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [feedbackMsg, setFeedbackMsg] = useState("");
  const videoRef = useRef(null);

  useEffect(() => {
    const loadModels = async () => {
      await faceapi.nets.tinyFaceDetector.loadFromUri("/models");
      await faceapi.nets.faceExpressionNet.loadFromUri("/models");
      await faceapi.nets.ageGenderNet.loadFromUri("/models");
    };
    loadModels();
  }, []);

  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const detectEmotion = async () => {
    if (videoRef.current) {
      const detections = await faceapi
        .detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
        .withFaceExpressions()
        .withAgeAndGender();
      if (detections) {
        const detectedEmotion = Object.entries(detections.expressions).reduce(
          (a, b) => (a[1] > b[1] ? a : b)
        )[0];

        const gender = detections.gender;
        setEmotion(detectedEmotion);

        const res = await fetch(`http://localhost:8000/api/recommendations/${detectedEmotion}?gender=${gender}`);
        const data = await res.json();
        setRecommendations(data);
      }
    }
  };

  const sendFeedback = async (itemId) => {
    const res = await fetch("http://localhost:8000/api/feedback/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        emotion,
        item_id: itemId,
        reward: 1.0,
      }),
    });

    if (res.ok) {
      setFeedbackMsg("¡Gracias por tu feedback!");
      setTimeout(() => setFeedbackMsg(""), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-4">Recomendador de Ropa por Emoción</h1>

      <video
        ref={videoRef}
        autoPlay
        className="w-64 h-64 rounded-lg shadow-lg bg-black mb-4"
      />

      <div className="flex space-x-4 mb-6">
        <Button onClick={startCamera}>Activar Cámara</Button>
        <Button onClick={detectEmotion}>Detectar Emoción</Button>
      </div>

      {feedbackMsg && <p className="text-green-600 font-semibold mb-4">{feedbackMsg}</p>}

      {emotion && (
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-2">
            Emoción detectada: <span className="capitalize">{emotion}</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            {recommendations.map((item, index) => (
              <Card key={index} className="shadow-md">
                <img
                  src={`http://localhost:8000/data/images/${item.id}.jpg`}
                  alt={item.name}
                  className="w-full h-48 object-cover rounded-t-xl"
                  style={{ width: "200px", height: "auto", objectFit: "contain" }}
                />
                <CardContent>
                  <p className="font-medium">{item.name}</p>
                  <p className="text-sm text-gray-600">{item.gender} - {item.masterCategory}</p>
                  <Button
                    onClick={() => sendFeedback(item.id)}
                    className="mt-2 bg-green-500 hover:bg-green-600"
                  >
                    Me gusta
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
