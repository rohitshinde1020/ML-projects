FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=300 --retries=10 -r requirements.txt
COPY backend/main.py .
COPY Mental_Health_Model.pkl /app/Mental_Health_Model.pkl

ENV MODEL_PATH=/app/Mental_Health_Model.pkl
ENV CORS_ORIGINS=http://localhost:5173
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
