from flask import Flask, request, jsonify
import sqlite3
import secrets
import time

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return "Welcome to the API Key System!"

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content (204 status code)

@app.route('/generate_key', methods=['POST'])
def generate_key():
    data = request.json
    api_id = data.get('api_id')
    api_hash = data.get('api_hash')
    phone = data.get('phone')
    valid_days = data.get('valid_days', 30)

    api_key = secrets.token_hex(16)
    expiration = int(time.time()) + (valid_days * 86400)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (api_key, api_id, api_hash, phone, expiration) VALUES (?, ?, ?, ?, ?)",
                   (api_key, api_id, api_hash, phone, expiration))
    conn.commit()
    conn.close()

    return jsonify({"api_key": api_key, "expiration": expiration})

@app.route('/check_key/<api_key>', methods=['GET'])
def check_key(api_key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT expiration FROM users WHERE api_key=?", (api_key,))
    user = cursor.fetchone()
    conn.close()

    if user:
        expiration = user["expiration"]
        if time.time() < expiration:
            return jsonify({"status": "Valid", "expires_at": expiration})
        else:
            return jsonify({"status": "Expired"})
    return jsonify({"status": "Invalid API Key"})

if __name__ == '__main__':
    app.run(debug=True)
