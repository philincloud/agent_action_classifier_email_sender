from flask import Flask, request, jsonify
from ollama import Client
from ollama.exceptions import OllamaAPIError, OllamaRequestError
import system_message
import json
import time  # For potential retry logic

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
        # Call Llama 3.2 via ollama
        response = ollama_client.chat(model="llama3.2", messages=messages)
        print(response)
        if response and "message" in response and "content" in response["message"]:
            return response["message"]["content"].strip()
        else:
            print(f"Error: Unexpected response format from Ollama: {response}")
            return None  # Or raise a custom exception
    except OllamaAPIError as e:
        print(f"Ollama API Error: {e}")
        return None  # Or raise a custom exception
    except OllamaRequestError as e:
        print(f"Ollama Request Error (Connection issues?): {e}")
        return None  # Or raise a custom exception
    except Exception as e:
        print(f"An unexpected error occurred during Ollama call: {e}")
        return None  # Or raise a custom exception

# Define the POST endpoint
@app.route('/classify', methods=['POST'])
def classify():
    # Get the prompt from the POST request's JSON body
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    prompt = data['prompt']
    category = classify_prompt(prompt)

    if category:
        # Return the category as a plain text response
        return category, 200, {'Content-Type': 'text/plain'}
    else:
        # Return a 503 Service Unavailable if Ollama call failed
        return jsonify({"error": "Failed to classify prompt due to Ollama server issues"}), 503

if __name__ == '__main__':
    # Run the Flask server on port 9000 (disable debug mode for production)
    app.run(host='0.0.0.0', port=9000, debug=False)
