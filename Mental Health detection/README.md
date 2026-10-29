# Mindful Measure — Mental Health Score Detection

A deployment-ready React/Tailwind frontend and FastAPI backend for the supplied `Mental_Health_Model.pkl`. The application uses the existing fitted Random Forest pipeline; it does not retrain or reorder the model features.

## What the model uses

The notebook trains a regression model for `Mental_Health_Score`. The API accepts these original dataset inputs:

`Age`, `Gender`, `Country`, `Academic_Level`, `Most_Used_Platform`, `Purpose_Of_Use`, `Avg_Daily_Usage_Hours`, `Daily_Unlocks`, `Study_Hours`, `Physical_Activity_Hours`, `Sleep_Hours_Per_Night`, and `Stress_Level`.

The notebook-derived preprocessing is preserved by the model artifact: `Study_Hours` is log-transformed and scaled; numeric fields are scaled; `Stress_Level` is ordinal-encoded (`Low`, `Medium`, `High`, `Very High`); and the categorical fields are one-hot encoded. `Country` is grouped into the notebook's top countries or `other` before prediction.

The returned value is the model's estimated `Mental_Health_Score`. It is not a diagnosis, clinical assessment, confidence value, or risk category. This tool is for informational purposes only and is not a substitute for professional mental health care.

## Local setup

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload --port 8000
```

The model file must remain at the project root unless `MODEL_PATH` is set. Check `http://localhost:8000/health`.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_API_URL` to the backend URL when it is not `http://localhost:8000`.

## API

`GET /health` returns `{"status":"ok","model":"loaded"}` when startup successfully loaded the model.

`POST /predict` accepts JSON:

```json
{
  "age": 21,
  "gender": "Female",
  "country": "India",
  "academic_level": "Undergraduate",
  "most_used_platform": "Instagram",
  "purpose_of_use": "Education",
  "avg_daily_usage_hours": 4,
  "daily_unlocks": 120,
  "study_hours": 4,
  "physical_activity_hours": 1.5,
  "sleep_hours_per_night": 7,
  "stress_level": "Medium"
}
```

The response contains `score`, `target`, and an interpretation of the returned value. Invalid enum values, missing fields, extra fields, and invalid numeric values return a validation error.

## Deployment

### Render

Create a Web Service rooted at `backend` (or configure the repository root with `--app-dir backend`), use Python 3.11, and set:

```text
Build command: pip install -r backend/requirements.txt
Start command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
CORS_ORIGINS: https://your-vercel-app.vercel.app
```

If deploying with the included `backend/Dockerfile`, use the repository root as the Docker build context (the Dockerfile copies `backend/main.py` and the model from that context). Set `CORS_ORIGINS` to the exact Vercel origin.

### Vercel

Import the `frontend` directory as the project root, keep the default Vite build settings (`npm run build`, output `dist`), and set:

```text
VITE_API_URL=https://your-render-service.onrender.com
```

## Verification

From `frontend`, run `npm run build`. From `backend`, run `python -c "from main import app"` after installing requirements. Use the real model and a request like the example above to verify `/predict`; no mock prediction path is included.
