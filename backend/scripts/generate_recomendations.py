# generate_recommendations.py

import pandas as pd
import json
from collections import defaultdict
from pathlib import Path
import random

# === Cargar datos ===
csv_path = Path("data/ropa_filtrada_con_links.csv")
df = pd.read_csv(csv_path)

# === Normalización ===
df["articleType"] = df["articleType"].str.lower()
df["productDisplayName"] = df["productDisplayName"].str.lower()
df["gender"] = df["gender"].str.lower()

# === Nuevas keywords optimizadas ===
emotion_keywords = {
    "happy": [
        "colorful", "yellow", "bright", "floral", "print", "kurti", "t-shirt", "dress", "cheerful", "joy", "top"
    ],
    "sad": [
        "blue", "gray", "dark", "jacket", "hoodie", "sweater", "coat", "trousers", "pants"
    ],
    "angry": [
        "black", "leather", "biker", "boots", "shirt", "jacket", "denim", "bold", "shorts", "graphic"
    ],
    "surprised": [
        "glitter", "metallic", "party", "top", "shirt", "stylish", "shine", "colorful", "dress"
    ],
    "fearful": [
        "cover", "hoodie", "jacket", "long", "trousers", "coat", "soft", "comfortable", "sweater"
    ],
    "disgusted": [
        "plain", "basic", "clean", "minimal", "simple", "shirt", "sweater", "casual", "t-shirt"
    ],
    "neutral": [
        "t-shirt", "jeans", "basic", "white", "casual", "simple", "shirt", "pants"
    ]
}

# === Configuración ===
MAX_PER_CATEGORY = 20
recommendations = defaultdict(list)
output_rows = []
seen_ids = defaultdict(set)

# === Generación ===
for emotion, keywords in emotion_keywords.items():
    for category in df["articleType"].unique():
        subset = df[df["articleType"] == category]

        if subset.empty:
            continue

        mask = subset["productDisplayName"].apply(
            lambda name: any(kw in name for kw in keywords)
        )
        matches = subset[mask]

        # Completar si no hay suficientes coincidencias
        if len(matches) < MAX_PER_CATEGORY:
            extra = subset[~mask].sample(min(MAX_PER_CATEGORY - len(matches), len(subset[~mask])), random_state=42)
            matches = pd.concat([matches, extra])

        # Barajar resultados
        matches = matches.sample(frac=1).head(MAX_PER_CATEGORY)

        for _, row in matches.iterrows():
            item_id = str(row["id"])
            if item_id in seen_ids[emotion]:
                continue

            seen_ids[emotion].add(item_id)

            item = {
                "id": item_id,
                "name": row["productDisplayName"],
                "gender": row.get("gender", "unisex"),
                "masterCategory": row.get("masterCategory", "other"),
                "category": row["articleType"],
                "image_url": row["link"]
            }

            recommendations[emotion].append(item)

            output_rows.append({
                "emotion": emotion,
                "id": item_id,
                "name": row["productDisplayName"],
                "gender": item["gender"],
                "category": item["category"]
            })

# === Guardar JSON ===
Path("recommendations").mkdir(exist_ok=True)
with open("recommendations/recommendations.json", "w", encoding="utf-8") as f:
    json.dump(recommendations, f, indent=2, ensure_ascii=False)

# === Guardar CSV para análisis ===
csv_output_path = Path("recommendations/recomendaciones_emocion_categoria.csv")
pd.DataFrame(output_rows).to_csv(csv_output_path, index=False)

print("✅ Recomendaciones generadas.")
