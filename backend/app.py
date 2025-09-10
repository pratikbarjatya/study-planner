import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from gemini_client import GeminiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='../templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

try:
    client = GeminiClient()
except Exception as e:
    logger.error(f"GeminiClient initialization failed: {e}")
    client = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get('message', '').strip()

    # Input validation
    if not user_message:
        return jsonify({'status': 'error', 'error': 'No message provided'}), 400
    if len(user_message) > 1000:
        return jsonify({'status': 'error', 'error': 'Message too long'}), 400
    if client is None:
        return jsonify({'status': 'error', 'error': 'LLM client not available'}), 500

    try:
        response_text = client.generate_response(user_message)
        return jsonify({'status': 'success', 'response': response_text})
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({'status': 'error', 'error': 'Error generating response'}), 500

if __name__ == '__main__':
    # For production, use Gunicorn: gunicorn -w 4 app:app
    app.run(debug=os.environ.get("FLASK_DEBUG", "False") == "True")