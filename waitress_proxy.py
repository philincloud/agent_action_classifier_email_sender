import os
import requests
from waitress import serve
from flask import Flask

app = Flask(__name__)

FLASK_APP_HOST = os.environ.get('FLASK_APP_HOST', 'agent_classifier_app')
FLASK_APP_PORT = int(os.environ.get('FLASK_APP_PORT', 9000))
FLASK_APP_URL = f"http://{FLASK_APP_HOST}:{FLASK_APP_PORT}"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
def proxy(path):
    url = f"{FLASK_APP_URL}/{path}"
    headers = dict(request.headers)
    method = request.method
    data = request.get_data()
    try:
        resp = requests.request(method, url, headers=headers, data=data, stream=True)
        response = app.response_class(resp.raw, mimetype=resp.headers.get('Content-Type'))
        response.status_code = resp.status_code
        for header, value in resp.headers.items():
            response.headers[header] = value
        return response
    except requests.exceptions.ConnectionError as e:
        return f"Error connecting to Flask app: {e}", 503
    except Exception as e:
        return f"Proxy error: {e}", 500

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
