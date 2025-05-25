# 👕 Emotion-Based Fashion Recommender

Este proyecto es una aplicación fullstack que recomienda ropa según las emociones del usuario detectadas mediante la cámara. Combina visión por computadora con técnicas de aprendizaje por refuerzo para ofrecer una experiencia personalizada e inteligente.

---

## 🎯 Características principales

- 📷 Detección de emociones faciales en tiempo real usando **FaceAPI.js**
- 🧠 Motor de recomendación adaptativo mediante **Multi-Armed Bandit**
- 👦 Reconocimiento de **género** para filtrar prendas relevantes
- ♻️ Feedback del usuario que entrena al sistema para mejorar sus sugerencias
- 🗂️ Recomendaciones extraídas del dataset de Kaggle: [Fashion Product Images Dataset](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset)
- 🔄 Backend en **FastAPI**, frontend en **React + Vite**

---

## 📁 Estructura del proyecto

```
proyectoRopaJordi/
├── backend/
│   ├── app.py
│   ├── bandits/
│   │   └── bandit_manager.py
│   ├── recommendations/
│   │   └── recommendations.json
│   └── data/
│       ├── images/
│       └── styles.csv
├── my-react-app/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       └── ui/
│   │           ├── button.jsx
│   │           └── card.jsx
│   └── public/
│       └── models/  ← modelos de FaceAPI.js
```

---

## 🚀 Cómo ejecutar el proyecto

### 1. Backend (FastAPI + Recomendaciones)

```bash
cd backend
mkdir data
python -m venv venv
venv\Scripts\activate        # En Windows
pip install -r requirements.txt
uvicorn app:app --reload
```

Asegúrate de tener:
- El archivo `styles.csv` en `backend/data/`
- Las imágenes del dataset en `backend/data/images/`
- El archivo `recommendations.json` generado por `generate_recommendations.py`

---

### 2. Frontend (React)

```bash
cd my-react-app
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install firebase
npm install firebase@latest
npm install react-router-dom
npm install papaparse
npm run dev
```

---

## 🧠 Inteligencia incorporada (IA)

Este sistema utiliza:

- 📊 **Multi-Armed Bandit (ε-greedy)**: selecciona las mejores prendas con base en la retroalimentación (rewards) del usuario.
- 👁️‍🗨️ **FaceAPI.js**: para detección de emociones y género desde la cámara.
- 🧠 En el futuro, se puede migrar a **Firebase** o **MongoDB** para guardar el feedback y el historial.

---

## 📝 Feedback

El feedback se registra mediante un POST a:

```
POST /api/feedback/
Body:
{
  "emotion": "happy",
  "item_id": "12345",
  "reward": 1.0
}
```

Esto permite que el sistema aprenda qué prendas gustaron más a cada emoción.

---

## ✅ Pendientes / Ideas futuras

- [ ] Sección de “Recomendaciones populares”
- [ ] Guardar historial del usuario
- [ ] Migración a base de datos persistente (Firebase o MongoDB)
- [ ] Incorporar edad como filtro adicional
- [ ] Sistema de autenticación para perfiles únicos

---

## 📸 Capturas

![Demo](demo_1.png)
![Detección](demo_2.png)

---

## 📄 Licencia

MIT © [Jordi Ledesma, Diego Llanos]
