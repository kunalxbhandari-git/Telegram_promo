import sqlite3
import secrets
import time

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

def create_api_key(api_id, api_hash, phone, valid_days):
    api_key = secrets.token_hex(16)  # Generate a secure API key
    expiration = int(time.time()) + (valid_days * 86400)  # Convert days to seconds

    cursor.execute("INSERT INTO users (api_key, api_id, api_hash, phone, expiration) VALUES (?, ?, ?, ?, ?)",
                   (api_key, api_id, api_hash, phone, expiration))
    conn.commit()

    return api_key

# Example usage
api_id = input("Enter API ID: ")
api_hash = input("Enter API Hash: ")
phone = input("Enter phone number: ")
valid_days = int(input("Enter number of valid days: "))

new_api_key = create_api_key(api_id, api_hash, phone, valid_days)
print(f"Generated API Key: {new_api_key}")
