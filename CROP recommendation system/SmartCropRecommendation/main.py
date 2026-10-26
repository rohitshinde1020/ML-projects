import math
import os
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_crop_model.pkl"

app = Flask(__name__)

model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


@app.get("/health")
def health():
    model_ready = model is not None
    return jsonify(
        status="ok" if model_ready else "degraded",
        model="best_crop_model.pkl",
        model_available=model_ready,
    ), 200 if model_ready else 503


@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    error = None
    values = {}

    if request.method == "POST":
        try:
            values = {
                "N": float(request.form["N"]),
                "P": float(request.form["P"]),
                "K": float(request.form["K"]),
                "temperature": float(request.form["temperature"]),
                "humidity": float(request.form["humidity"]),
                "ph": float(request.form["ph"]),
                "rainfall": float(request.form["rainfall"]),
            }

            if any(not math.isfinite(v) for v in values.values()):
                raise ValueError("Please enter finite numeric values.")
            if any(v < 0 for v in values.values()):
                raise ValueError("All measurements must be non-negative.")
            if not 0 <= values["humidity"] <= 100:
                raise ValueError("Humidity must be between 0 and 100.")
            if not 0 <= values["ph"] <= 14:
                raise ValueError("Soil pH must be between 0 and 14.")

            if model is None:
                raise FileNotFoundError(
                    "The model file was not found. Add models/best_crop_model.pkl to the project."
                )

            input_df = pd.DataFrame([[values[f] for f in FEATURES]], columns=FEATURES)
            prediction = model.predict(input_df)[0]

        except (ValueError, KeyError) as exc:
            error = str(exc) or "Please enter valid numeric values in all fields."
        except FileNotFoundError as exc:
            error = str(exc)
        except Exception as exc:
            error = (
                "Prediction failed. Check that the model was trained with these seven "
                "features in this order (N, P, K, temperature, humidity, ph, rainfall). "
                f"Details: {exc}"
            )

    return render_template(
        "index.html",
        prediction=prediction,
        error=error,
        values=values,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug)
