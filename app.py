from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env configuration
load_dotenv()

app = Flask(__name__)
CORS(app)

# Sambungan MongoDB
mongo_uri = os.environ.get("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client['tasdar']
messages_collection = db['folder_jiwa']  # Folder Jiwa = memori

# Sambungan GPT OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Laluan Root
@app.route('/')
def home():
    return jsonify({"message": "TAS.DAR Backend Active ✅"})

# Laluan Prompt Ringkas
@app.route('/prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    return jsonify({
        "response": f"Sah, mesej anda '{data.get('prompt')}' telah diterima dan diproses oleh TAS.DAR."
    })

# Laluan Simpan Jiwa (manual save)
@app.route('/save_jiwa', methods=['POST'])
def save_jiwa():
    data = request.json
    result = messages_collection.insert_one({
        "role": "user",
        "message": data.get('message'),
        "timestamp": datetime.utcnow()
    })
    return jsonify({"status": "saved", "id": str(result.inserted_id)})

# Laluan GPT Chatboard
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "Mesej kosong"}), 400

    # Simpan input ke Folder Jiwa
    messages_collection.insert_one({
        "role": "user",
        "message": user_input,
        "timestamp": datetime.utcnow()
    })

    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Kau adalah TAS.DAR, sahabat reflektif yang memahami perasaan manusia."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = gpt_response['choices'][0]['message']['content']

        # Simpan balasan ke Folder Jiwa
        messages_collection.insert_one({
            "role": "assistant",
            "message": reply,
            "timestamp": datetime.utcnow()
        })

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Local
if __name__ == '__main__':
    app.run(debug=True)
