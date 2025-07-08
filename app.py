from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import openai
import os

app = Flask(__name__, static_url_path='/static')

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['tasdar_ai']
core = db['identity_core']

openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/gpt_reply', methods=['POST'])
def gpt_reply():
    user_input = request.json.get('message')
    system_prompt_doc = core.find_one({'id': 'tasdar_v1.0'})
    system_prompt = system_prompt_doc.get('system_prompt', {}).get('prompt', 'You are TAS.DAR.')
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input}
        ]
    )
    reply = response['choices'][0]['message']['content']
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
