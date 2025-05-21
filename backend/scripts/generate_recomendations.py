# generate_recommendations.py

import pandas as pd
import json
from collections import defaultdict
from pathlib import Path

# Cargar datos
df = pd.read_csv("./data/styles.csv", on_bad_lines='skip')

# Diccionario mejorado de estilos por emoción
emotion_styles = {
    "happy": ["Floral", "Yellow", "Casual", "Sneakers", "Tshirt", "Kurta"],
    "sad": ["Blue", "Gray", "Jacket", "Hoodie", "Sweatshirt"],
    "angry": ["Black", "Leather", "Boots", "Denim", "Biker"],
    "surprised": ["Bright", "Colorful", "Party", "Shirt", "Dress", "Skirt"]
}

# Para almacenar recomendaciones
recommendations = defaultdict(list)

for emotion, keywords in emotion_styles.items():
    seen_ids = set()
    gender_counts = defaultdict(int)

    for kw in keywords:
        matches = df[df['productDisplayName'].str.contains(kw, case=False, na=False)]
        for _, row in matches.iterrows():
            product_id = str(row['id'])
            gender = row.get("gender", "Unisex")
            if product_id in seen_ids:
                continue

            # Limitar a 6 de un mismo género por emoción
            if gender_counts[gender] >= 6:
                continue

            seen_ids.add(product_id)
            gender_counts[gender] += 1

            recommendations[emotion].append({
                "id": product_id,
                "name": row["productDisplayName"],
                "gender": gender,
                "masterCategory": row.get("masterCategory", "Other")
            })

            if len(recommendations[emotion]) >= 15:
                break
        if len(recommendations[emotion]) >= 15:
            break

# Guardar resultados
Path("./recommendations").mkdir(exist_ok=True)
with open("./recommendations/recommendations.json", "w", encoding="utf-8") as f:
    json.dump(recommendations, f, indent=2, ensure_ascii=False)

print("Recomendaciones generadas.")
