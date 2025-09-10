import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from gemini_client import GeminiClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
CORS(app, resources={r"/api/*": {"origins": "*"}})

try:
    client = GeminiClient()
except Exception as e:
    logger.error(f"GeminiClient initialization failed: {e}")
    client = None

@app.route('/')
def index():
    """
    Renders the 'index.html' template for the application's home page.

    Returns:
        Response: The rendered HTML page for the index route.
    """
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles chat requests by processing user messages and generating responses using an LLM client.

    Returns:
        Response: A JSON response containing either the generated reply or an error message.

    Request JSON:
        {
            "message": "<user's message>"
        }

    Responses:
        200: {'status': 'success', 'response': <response_text>}
        400: {'status': 'error', 'error': 'No message provided' or 'Message too long'}
        500: {'status': 'error', 'error': 'LLM client not available' or 'Error generating response'}
    """
    payload = request.get_json(silent=True) or {}
    user_message = payload.get('message', '').strip()

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
    app.run(debug=os.environ.get("FLASK_DEBUG", "False") == "True")