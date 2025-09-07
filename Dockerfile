FROM python:3.13-slim

# Install system dependencies needed for PyAudio
RUN apt-get update && apt-get install -y portaudio19-dev gcc

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
