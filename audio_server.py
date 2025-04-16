import http.server
import socketserver
import io
import numpy as np
import soundfile as sf
import model_handler
import requests
import json

PORT = 8000
URL_CLASSIFY = 'http://agent_classifier_app:9000/classify'
URL_LAMBDA = "https://sw4rjffj5y5tiiem2c6gmzevkm0zkmwd.lambda-url.eu-west-2.on.aws/"
HEADERS = {'Content-Type': 'application/json'}

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        super().do_GET()

    def do_POST(self):
        print("Server hit for POST")
        content_length = int(self.headers['Content-Length'])
        audio_blob = self.rfile.read(content_length)
        final_response_data = None  # Initialize the final response

        try:
            audio_data, samplerate = sf.read(io.BytesIO(audio_blob))
            transcription_result = model_handler.transcribe_from_memory(audio_data.astype(np.float32))
            prompt = transcription_result["text"]
            print(f"Transcription: {prompt}")

            try:
                response_classify = requests.post(URL_CLASSIFY, json={"prompt": prompt}, headers=HEADERS)
                response_classify.raise_for_status()
                classify_data = response_classify.json()  # Parse JSON response
                print(f"Response from classify: {classify_data}")
                final_response_data = classify_data # Store for final response

                try:
                    response_lambda = requests.post(URL_LAMBDA, json=classify_data, headers=HEADERS) # Send parsed JSON
                    response_lambda.raise_for_status()
                    lambda_response = response_lambda.json() # Parse Lambda's JSON response
                    print(f"Response from Lambda: {lambda_response}")
                    final_response_data = lambda_response # Update with Lambda's response

                except requests.exceptions.RequestException as e:
                    print(f"Error communicating with Lambda: {e}")
                    self._send_response(500, json.dumps({"error": f"Error communicating with Lambda: {e}"}))
                    return
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from Lambda")
                    self._send_response(500, json.dumps({"error": "Error decoding JSON from Lambda"}))
                    return

            except requests.exceptions.RequestException as e:
                print(f"Error communicating with classify endpoint: {e}")
                self._send_response(500, json.dumps({"error": f"Error communicating with classify endpoint: {e}"}))
                return
            except json.JSONDecodeError:
                print(f"Error decoding JSON from classify")
                self._send_response(500, json.dumps({"error": "Error decoding JSON from classify"}))
                return

            # Send the final response back to the original client
            self._send_response(200, json.dumps(final_response_data)) # Send JSON

        except sf.LibsndfileError as e:
            print(f"Error reading audio data: {e}")
            self._send_response(400, json.dumps({"error": f"Invalid audio format or corrupted data: {e}"}))
            return
        except Exception as e:
            print(f"Error processing request: {e}")
            self._send_response(500, json.dumps({"error": f"Error processing request: {e}"}))
            return

    def do_OPTIONS(self):
        self._send_cors_headers()

    def _send_cors_headers(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json") # Send as JSON
        self.end_headers()
        self.wfile.write(message.encode())

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()