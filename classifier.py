from flask import Flask, request, jsonify
import ollama
import system_message
import json

app = Flask(__name__)

# Function to classify prompt into a category using Llama 3.2


def classify_prompt(prompt):

    
    # Prepare the message for Llama 3.2
    messages = [
        {"role": "system", "content": system_message.system_message(
        "addresses.json", "actions.json")},
        {"role": "user", "content": prompt}
    ]

    # Call Llama 3.2 via ollama (adjust model name if needed, e.g., "llama3.2:8b")
    response = ollama.chat(model="llama3.2", messages=messages)

    # Extract and return the single-word response
    print(response)
    return response["message"]["content"].strip()

# Define the POST endpoint


@app.route('/classify', methods=['POST'])
def classify():
    # Get the prompt from the POST request's JSON body
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    prompt = data['prompt']
    category = classify_prompt(prompt)

    # Return the category as a plain text response
    return category, 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    # Run the Flask server on port 9000
    app.run(host='0.0.0.0', port=9000, debug=True)
