import math
import os
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

app = Flask(__name__)

# Put your saved model files in the models/ folder.
# These filenames must match the files you actually saved.
rf_path = MODEL_DIR / "random_forest_model.pkl"
lr_path = MODEL_DIR / "logistic_model.pkl"

rf_model = joblib.load(rf_path) if rf_path.exists() else None
lr_model = joblib.load(lr_path) if lr_path.exists() else None

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
MODEL_NAMES = {"random_forest", "logistic"}


@app.get("/health")
def health():
    models_ready = rf_model is not None and lr_model is not None
    return jsonify(
        status="ok" if models_ready else "degraded",
        models={
            "random_forest": rf_model is not None,
            "logistic": lr_model is not None,
        },
    ), 200 if models_ready else 503


@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    error = None
    values = {}
    selected_model = request.form.get("model", "random_forest")

    if request.method == "POST":
        try:
            if selected_model not in MODEL_NAMES:
                raise ValueError("Please select one of the available models.")

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

            model = rf_model if selected_model == "random_forest" else lr_model
            if model is None:
                raise FileNotFoundError(
                    "The selected model file was not found. Add your saved .pkl file to the models/ folder."
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

    models_available = {
        "random_forest": rf_model is not None,
        "logistic": lr_model is not None,
    }
    return render_template(
        "index.html",
        prediction=prediction,
        error=error,
        values=values,
        selected_model=selected_model,
        models_available=models_available,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug)
