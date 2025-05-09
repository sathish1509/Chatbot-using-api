from flask import Flask, request, jsonify, render_template
import os
import requests
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_ENDPOINT = 'https://api.deepseek.com/v1/chat/completions'
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

system_prompt = """You are a helpful assistant for a social media boosting service. 
You help customers with questions about growing their social media presence, 
including followers, likes, engagement, and pricing. Keep responses concise and professional.
Always maintain a friendly and helpful tone."""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Prepare the chat message payload
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            'temperature': 0.7,
            'max_tokens': 500
        }

        # Call DeepSeek API with proper headers
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            DEEPSEEK_API_ENDPOINT,
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            return jsonify({
                'error': f'API Error: {response.status_code}',
                'message': response.text
            }), response.status_code

        response_data = response.json()
        bot_response = response_data['choices'][0]['message']['content']

        return jsonify({
            'response': bot_response
        })

    except requests.RequestException as e:
        return jsonify({'error': f'Request error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
