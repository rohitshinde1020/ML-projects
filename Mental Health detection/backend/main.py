from __future__ import annotations

import logging
import math
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

#what is logging? Logging is a built-in Python module that provides a flexible framework for emitting log messages from Python programs. It allows developers to track events that happen during the execution of a program, which can be useful for debugging and monitoring the application's behavior. The logging module supports different log levels (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL) and can be configured to output log messages to various destinations, such as the console, files, or external logging systems.
#what is logging.getLogger("mental-health-api")? It creates a logger object with the name "mental-health-api" that can be used to log messages for this specific application. The logger can be configured to log messages at different levels (e.g., DEBUG, INFO, WARNING, ERROR) and can be used to track the application's behavior and diagnose issues.

logger = logging.getLogger("mental-health-api")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE_DIR / "Mental_Health_Model.pkl")))
TOP_COUNTRIES = {
    "Other",
    "India",
    "USA",
    "Canada",
    "Australia",
    "UK",
    "Germany",
    "Mexico",
    "Turkey",
    "France",
}

Gender = Literal["Female", "Male"]
AcademicLevel = Literal["Graduate", "High School", "Undergraduate"]
Platform = Literal[
    "Facebook",
    "Instagram",
    "KakaoTalk",
    "LINE",
    "LinkedIn",
    "Snapchat",
    "TikTok",
    "Twitter",
    "VKontakte",
    "WeChat",
    "WhatsApp",
    "YouTube",
]
Purpose = Literal["Education", "Entertainment", "Networking", "News"]
StressLevel = Literal["Low", "Medium", "High", "Very High"]


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: Annotated[int, Field(gt=0, le=120)]
    gender: Gender
    country: Annotated[str, Field(min_length=1, max_length=100)]
    academic_level: AcademicLevel
    most_used_platform: Platform
    purpose_of_use: Purpose
    avg_daily_usage_hours: Annotated[float, Field(ge=0, le=24)]
    daily_unlocks: Annotated[int, Field(ge=0, le=10000)]
    study_hours: Annotated[float, Field(ge=0, le=24)]
    physical_activity_hours: Annotated[float, Field(ge=0, le=24)]
    sleep_hours_per_night: Annotated[float, Field(ge=0, le=24)]
    stress_level: StressLevel

    @field_validator(
        "avg_daily_usage_hours",
        "study_hours",
        "physical_activity_hours",
        "sleep_hours_per_night",
    )
    @classmethod
    def reject_non_finite(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Value must be a finite number.")
        return value


class PredictionResponse(BaseModel):
    score: float
    target: str = "Mental_Health_Score"
    interpretation: str = (
        "A model-estimated Mental_Health_Score based on the provided inputs."
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.is_file():
        logger.error("Model file was not found at %s", MODEL_PATH)
        raise RuntimeError(f"Model file was not found at {MODEL_PATH}")
    try:
        app.state.model = joblib.load(MODEL_PATH)
    except Exception:
        logger.exception("Could not load the model from %s", MODEL_PATH)
        raise
    logger.info("Loaded model from %s", MODEL_PATH)
    yield


app = FastAPI(
    title="Mental Health Score Detection API",
    version="1.0.0",
    description="Prediction API backed by the supplied trained model.",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health(request: Request) -> dict[str, str]:
    if not hasattr(request.app.state, "model"):
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    return {"status": "ok", "model": "loaded"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    country_group = payload.country if payload.country in TOP_COUNTRIES else "other"
    model_input = pd.DataFrame(
        [
            {
                "Study_Hours": payload.study_hours,
                "Age": payload.age,
                "Avg_Daily_Usage_Hours": payload.avg_daily_usage_hours,
                "Daily_Unlocks": payload.daily_unlocks,
                "Physical_Activity_Hours": payload.physical_activity_hours,
                "Sleep_Hours_Per_Night": payload.sleep_hours_per_night,
                "Stress_Level": payload.stress_level,
                "Gender": payload.gender,
                "Academic_Level": payload.academic_level,
                "Most_Used_Platform": payload.most_used_platform,
                "Purpose_Of_Use": payload.purpose_of_use,
                "Grouped_country": country_group,
            }
        ]
    )
    try:
        score = float(model.predict(model_input)[0])
    except Exception:
        logger.exception("Prediction failed for a valid request.")
        raise HTTPException(
            status_code=500, detail="The model could not produce a prediction."
        )
    return PredictionResponse(score=score)
