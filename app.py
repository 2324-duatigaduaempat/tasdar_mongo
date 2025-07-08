from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Sambung MongoDB
client = MongoClient(os.environ.get("MONGODB_URI"))
db = client['tasdar']
folder_jiwa = db.folder_jiwa

# Sambung OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def home():
    return jsonify({"message": "TAS.DAR Backend Active"})

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    prompt = data.get("prompt")
    user_id = data.get("user_id", "anonymous")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Sambung ke GPT
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = gpt_response['choices'][0]['message']['content']

    # Simpan ke MongoDB Folder Jiwa
    folder_jiwa.insert_one({
        "user_id": user_id,
        "prompt": prompt,
        "response": response_text,
        "timestamp": datetime.now()
    })

    return jsonify({"response": response_text})

@app.route('/save_jiwa', methods=['POST'])
def save_jiwa():
    data = request.json
    result = folder_jiwa.insert_one(data)
    return jsonify({"status": "saved", "id": str(result.inserted_id)})

if __name__ == '__main__':
    app.run(debug=True)
