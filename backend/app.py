from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

from bandits.bandit_manager import MultiArmedBandit


app = FastAPI()
bandit = MultiArmedBandit()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emotion_fallback = {
    "neutral": "happy",
    "disgusted": "sad",
    "fearful": "surprised"
}
gender_map = {
    "male": "men",
    "female": "women"
}

@app.get("/api/recommendations/{emotion}")
async def get_recommendations(emotion: str, request: Request):
    gender = request.query_params.get("gender", "").lower()
    mapped_emotion = emotion_fallback.get(emotion.lower(), emotion.lower())
    mapped_gender = gender_map.get(gender, gender)

    filepath = Path("recommendations/recommendations.json")
    if not filepath.exists():
        return {"error": "No se encontraron recomendaciones."}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get(mapped_emotion, [])
    if mapped_gender:
        items = [item for item in items if item.get("gender", "").lower() == mapped_gender]

    if not items:
        return []

    # Seleccionar múltiples recomendaciones usando Multi-Armed Bandit
    # num_recommendations = min(6, len(items))
    # selected_items = [bandit.choose(mapped_emotion, items) for _ in range(num_recommendations)]

    # return [item for item in selected_items if item]
    selected_items = bandit.choose_multiple(mapped_emotion, items, k=6)
    return selected_items

# ---------------------
# Persistencia de feedback nuevo
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

     # Guardar en archivo JSON nuevo
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

app.mount("/data", StaticFiles(directory="data"), name="data")
