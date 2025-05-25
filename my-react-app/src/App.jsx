import { useState, useRef, useEffect } from "react";
import * as faceapi from "face-api.js";
import { Button } from "./components/ui/button";
import { Card, CardContent } from "./components/ui/card";

export default function EmotionBasedFashion() {
  const [emotion, setEmotion] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [feedbackMsg, setFeedbackMsg] = useState("");
  const [selectedGender, setSelectedGender] = useState("male");
  const [selectedCategory, setSelectedCategory] = useState("tshirts");
  const videoRef = useRef(null);

  const genderCategories = {
    male: ["jackets", "shirts", "tshirts", "trousers", "shorts"],
    female: [
      "jackets",
      "shirts",
      "tshirts",
      "trousers",
      "skirts",
      "shorts",
      "tops",
      "dresses",
      "shrug"
    ],
    boys: ["jackets", "shirts", "tshirts", "trousers", "shorts"],
    girls: ["jackets", "shirts", "tshirts", "trousers", "skirts", "dresses", "shorts"],
    unisex: ["tshirts", "jackets", "shorts", "trousers", "shirts"],
  };

  const availableCategories = genderCategories[selectedGender] || [];

  useEffect(() => {
    const loadModels = async () => {
      await faceapi.nets.tinyFaceDetector.loadFromUri("/models");
      await faceapi.nets.faceExpressionNet.loadFromUri("/models");
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
        .withFaceExpressions();
      if (detections) {
        const detectedEmotion = Object.entries(detections.expressions).reduce(
          (a, b) => (a[1] > b[1] ? a : b)
        )[0];

        setEmotion(detectedEmotion);

        const res = await fetch(
          `http://localhost:8000/api/recommendations/${detectedEmotion}?gender=${selectedGender}&categoria=${selectedCategory}`
        );
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

      <div className="flex flex-col md:flex-row items-center gap-4 mb-6">
        <Button onClick={startCamera}>Activar Cámara</Button>
        <Button onClick={detectEmotion}>Detectar Emoción</Button>

        <select
          value={selectedGender}
          onChange={(e) => {
            const newGender = e.target.value;
            setSelectedGender(newGender);
            const newAvailable = genderCategories[newGender];
            if (!newAvailable.includes(selectedCategory)) {
              setSelectedCategory(newAvailable[0]);
            }
          }}
          className="border px-3 py-2 rounded"
        >
          <option value="male">Hombre</option>
          <option value="female">Mujer</option>
          <option value="boys">Niño</option>
          <option value="girls">Niña</option>
          <option value="unisex">Unisex</option>
        </select>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="border px-3 py-2 rounded"
        >
          {availableCategories.map((cat) => (
            <option key={cat} value={cat}>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>
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
                  src={item.image_url}
                  alt={item.name}
                  className="w-full h-48 object-cover rounded-t-xl"
                  style={{ width: "200px", height: "auto", objectFit: "contain" }}
                />
                <CardContent>
                  <p className="font-medium">{item.name}</p>
                  <p className="text-sm text-gray-600">
                    {item.gender} - {item.category}
                  </p>
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
