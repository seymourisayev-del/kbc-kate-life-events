FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Cloud Run sets $PORT; API keys come in as environment variables, never from .env.
ENV PORT=8080
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
