from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.environ.get("MONGODB_URI"))
db = client['tasdar']

@app.route('/')
def home():
    return jsonify({"message": "TAS.DAR Backend Active"})

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    return jsonify({
        "response": f"Sah, mesej anda '{data.get('prompt')}' telah diterima dan diproses oleh TAS.DAR."
    })

@app.route('/save_jiwa', methods=['POST'])
def save_jiwa():
    data = request.json
    result = db.folder_jiwa.insert_one(data)
    return jsonify({"status": "saved", "id": str(result.inserted_id)})

if __name__ == '__main__':
    app.run(debug=True)
