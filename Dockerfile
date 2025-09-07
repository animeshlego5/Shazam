FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
  portaudio19-dev \
  gcc \
  libsndfile1 \
  ffmpeg \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy ONLY the backend directory
COPY backend/ /app/

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
