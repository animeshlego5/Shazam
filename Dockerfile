FROM python:3.13-slim

# Install system dependencies needed for PyAudio, audio processing
RUN apt-get update && apt-get install -y \
  portaudio19-dev \
  gcc \
  libsndfile1 \
  ffmpeg \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and build tools
RUN pip install --upgrade pip setuptools wheel

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your app code
COPY . .

# Expose port for FastAPI server
EXPOSE 8000

# Start the Uvicorn server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
