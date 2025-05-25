# === app.py ===
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

from bandits.bandit_manager import MultiArmedBandit

app = FastAPI()
bandit = MultiArmedBandit()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fallbacks de emociones y géneros
emotion_fallback = {
    "neutral": "happy",
    "disgusted": "sad",
    "fearful": "surprised"
}
gender_map = {
    "male": "men",
    "female": "women"
}

# Cargar recomendaciones desde archivo JSON
recom_path = Path("recommendations/recommendations.json")
if not recom_path.exists():
    raise FileNotFoundError("❌ El archivo recommendations.json no existe.")

with open(recom_path, "r", encoding="utf-8") as f:
    RECOMMENDATIONS = json.load(f)

# === Endpoint de recomendaciones ===
@app.get("/api/recommendations/{emotion}")
async def get_recommendations(emotion: str, request: Request):
    gender = request.query_params.get("gender", "").lower()
    categoria = request.query_params.get("categoria", "").lower()

    mapped_emotion = emotion_fallback.get(emotion.lower(), emotion.lower())
    mapped_gender = gender_map.get(gender, gender)

    filepath = Path("recommendations/recommendations.json")
    if not filepath.exists():
        return JSONResponse(content={"error": "No se encontró el archivo de recomendaciones."}, status_code=404)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    emotion_data = data.get(mapped_emotion, [])

    # Filtrar por género y categoría
    filtered_items = [
        item for item in emotion_data
        if (not mapped_gender or item.get("gender", "").lower() == mapped_gender)
        and (not categoria or item.get("category", "").lower() == categoria)
    ]

    if not filtered_items:
        return JSONResponse(content={"error": "No se encontraron recomendaciones."}, status_code=404)

    selected = bandit.choose_multiple(mapped_emotion, filtered_items, k=10)
    return selected


# === Feedback con persistencia en archivo JSON ===
feedback_path = Path("feedback.json")
if not feedback_path.exists():
    feedback_path.write_text("[]", encoding="utf-8")

@app.post("/api/feedback/")
async def register_feedback(request: Request):
    body = await request.json()
    emotion = body.get("emotion")
    item_id = body.get("item_id")
    reward = float(body.get("reward", 1.0))

    if not emotion or not item_id:
        return {"error": "Faltan datos para registrar feedback."}

    bandit.update(emotion, item_id, reward)

    with open(feedback_path, "r", encoding="utf-8") as f:
        feedbacks = json.load(f)

    feedbacks.append({
        "emotion": emotion,
        "item_id": item_id,
        "reward": reward
    })

    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    return {"message": "Feedback recibido"}

# (opcional: si manejas imágenes locales)
app.mount("/data", StaticFiles(directory="data"), name="data")
