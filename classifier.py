from flask import Flask, request, jsonify
from ollama import Client
import system_message
import json
import time  # For potential retry logic
import requests  # Import the requests library
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Ollama client, connecting to the 'ollama_server' container
ollama_client = Client(host='http://ollama_server:11434')

app = Flask(__name__)

# Function to classify prompt into a category using Llama 3.2
def classify_prompt(prompt):
    messages = [
        {"role": "system", "content": system_message.system_message(
            "addresses.json", "actions.json")},
        {"role": "user", "content": prompt}
    ]

    try:
        logging.info(f"Calling Ollama with prompt: '{prompt}'")
        # Call Llama 3.2 via ollama
        response = ollama_client.chat(model="llama3.2", messages=messages)
        logging.info(f"Ollama response: {response}")
        if response and "message" in response and "content" in response["message"]:
            return response["message"]["content"].strip()
        else:
            logging.error(f"Unexpected response format from Ollama: {response}")
            return None  # Or raise a custom exception
    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama Request Error (Connection issues or API error): {e}")
        return None  # Handle potential connection or API errors
    except Exception as e:
        logging.error(f"An unexpected error occurred during Ollama call: {e}")
        return None  # Catch any other unexpected errors

# Define the POST endpoint
@app.route('/classify', methods=['POST'])
def classify():
    logging.info("Received POST request on /classify")
    # Get the prompt from the POST request's JSON body
    data = request.get_json()
    if not data or 'prompt' not in data:
        logging.warning("Missing 'prompt' in request body")
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    prompt = data['prompt']
    logging.info(f"Classifying prompt: '{prompt}'")
    category = classify_prompt(prompt)

    if category:
        logging.info(f"Classification result: '{category}'")
        # Return the category as a plain text response
        return category, 200, {'Content-Type': 'text/plain'}
    else:
        logging.error("Failed to classify prompt due to Ollama server issues")
        # Return a 503 Service Unavailable if Ollama call failed
        return jsonify({"error": "Failed to classify prompt due to Ollama server issues"}), 503

if __name__ == '__main__':
    # Run the Flask server on port 9000 (disable debug mode for production)
    app.run(host='0.0.0.0', port=9000, debug=False)