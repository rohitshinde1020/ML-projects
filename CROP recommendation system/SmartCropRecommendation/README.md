# Smart Crop Recommendation

A beginner-friendly HTML/CSS + Flask interface for the saved crop classification model.

## 1. Project files

- `main.py`: Flask backend that loads models and predicts crop labels.
- `templates/index.html`: HTML form and result view.
- `static/style.css`: page styling.
- `models/best_crop_model.pkl`: the trained model used for predictions.
- `Procfile`: production start command for hosts such as Render and Railway.

The app loads only `models/best_crop_model.pkl` from this application directory.

## 2. Install packages

Open a terminal in this folder and run:

```bash
python -m pip install -r requirements.txt
```

For local development, use a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 3. Add the model

Place the already-trained model at `models/best_crop_model.pkl`. It must accept
these seven features, in this order:

`N, P, K, temperature, humidity, ph, rainfall`

The exported model already contains the preprocessing used during training. The
current artifact is a fitted Gaussian Naive Bayes model, so the app passes the
seven numeric features directly without adding a separate scaler.

## 4. Run

```bash
python main.py
```

Open the local address printed in the terminal (normally `http://127.0.0.1:5000`).

The app also exposes `GET /health`. It returns HTTP 200 when
`best_crop_model.pkl` is available, which can be used as a deployment health check.

## 5. Deploy to Render

1. Push the repository to GitHub, ensuring
   `CROP recommendation system/models/best_crop_model.pkl` is included.
2. Create a new **Web Service** on Render and select the repository.
3. Set **Root Directory** to `CROP recommendation system/SmartCropRecommendation`.
4. Set **Build Command** to:

   ```bash
   pip install -r requirements.txt
   ```

5. Set **Start Command** to:

   ```bash
   gunicorn --bind 0.0.0.0:$PORT main:app
   ```

6. Deploy and verify `https://your-service-url/health` returns a JSON response with
   `"status": "ok"` and `"model_available": true`.

Other hosts that support Python web services use the same build and start commands.
Do not run the notebook or retrain models during deployment; `Untitled.ipynb` and
`Crop_recommendation.csv` are training artifacts. Only the exported model files and
the Flask app are needed at runtime.

## Notes

- This app demonstrates model inference, not guaranteed agricultural advice.
- Use the same units and preprocessing as in training.
- Only load model files you trust. Joblib/pickle files can execute code when loaded.
