FROM python:3.12-slim-bullseye

WORKDIR /app

# Copy your application code into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# CMD to run the Flask development server (for internal use by the proxy)
CMD ["python", "classifier.py"]
