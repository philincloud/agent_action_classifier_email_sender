# Dockerfile.app
FROM python:3.12-slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "waitress", "--listen=0.0.0.0:9000", "classifier:app"]