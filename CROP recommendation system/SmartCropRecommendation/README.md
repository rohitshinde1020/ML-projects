# Smart Crop Recommendation

A beginner-friendly HTML/CSS + Flask interface for your saved crop classification models.

## 1. Project files

- `main.py`: Flask backend that loads models and predicts crop labels.
- `templates/index.html`: HTML form and result view.
- `static/style.css`: page styling.
- `models/`: put your trained model files here.
- `Procfile`: production start command for hosts such as Render and Railway.

Expected model filenames:

- `models/random_forest_model.pkl`
- `models/logistic_model.pkl`

If your files have different names, change `rf_path` and `lr_path` near the top of `main.py`.

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

## 3. Add your models

Copy your already-trained `.pkl` files into `models/`. The models must have been trained with these seven features, in this order:

`N, P, K, temperature, humidity, ph, rainfall`

If your Logistic Regression model was trained with `StandardScaler`, save/load the fitted pipeline containing both the scaler and classifier, not only the classifier.

## 4. Run

```bash
python main.py
```

Open the local address printed in the terminal (normally `http://127.0.0.1:5000`).

The app also exposes `GET /health`. It returns HTTP 200 only when both model files
are available, which can be used as a deployment health check.

## 5. Deploy to Render

1. Push the repository to GitHub, ensuring the two files in `models/` are included.
2. Create a new **Web Service** on Render and select the repository.
3. Set **Root Directory** to `ML Foundation/CROP recommendation system/SmartCropRecommendation`.
4. Set **Build Command** to:

   ```bash
   pip install -r requirements.txt
   ```

5. Set **Start Command** to:

   ```bash
   gunicorn --bind 0.0.0.0:$PORT main:app
   ```

6. Deploy and verify `https://your-service-url/health` returns a JSON response with
   `"status": "ok"`.

Other hosts that support Python web services use the same build and start commands.
Do not run the notebook or retrain models during deployment; `Untitled.ipynb` and
`Crop_recommendation.csv` are training artifacts. Only the exported model files and
the Flask app are needed at runtime.

## Notes

- This app demonstrates model inference, not guaranteed agricultural advice.
- Use the same units and preprocessing as in training.
- Only load model files you trust. Joblib/pickle files can execute code when loaded.
