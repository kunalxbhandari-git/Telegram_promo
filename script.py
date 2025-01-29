from telethon import TelegramClient
import asyncio
import sqlite3
import time

# Predefined API credentials
PREDEFINED_API_ID = 22208067  # Replace with your actual API ID (integer)
PREDEFINED_API_HASH = 'c1d96491b12fbad78446e81b3ed53a78'  # Replace with your actual API hash (string)

# Connect to the database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create table for storing API keys if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key TEXT UNIQUE,
    phone TEXT,
    expiration INTEGER
)''')
conn.commit()

# Function to validate API key
def validate_api_key(api_key):
    cursor.execute("SELECT phone, expiration FROM users WHERE api_key=?", (api_key,))
    user = cursor.fetchone()
    if user:
        phone, expiration = user
        if time.time() < expiration:
            return phone
    return None

async def main():
    phone = input("Enter your phone number: ")
    api_key = input("Enter your private API key: ")

    # Check if API key is valid
    valid_phone = validate_api_key(api_key)
    if not valid_phone or valid_phone != phone:
        print("Invalid or expired API key. Please contact the administrator.")
        return

    # Create Telegram client dynamically
    client = TelegramClient(f'session_{phone}', PREDEFINED_API_ID, PREDEFINED_API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        code = input("Enter the code you received: ")
        await client.sign_in(phone, code)

    print("Access granted!")

    while True:
        print("\n1. Extract Usernames (Chats)")
        print("2. Extract Group Usernames")
        print("3. Send Messages to Users")
        print("4. Send Messages to Groups")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            await extract_usernames(client)
        elif choice == "2":
            await extract_group_usernames(client)
        elif choice == "3":
            await send_messages_to_users(client)
        elif choice == "4":
            await send_messages_to_groups(client)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

async def extract_usernames(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_user and dialog.entity.username:
            print(dialog.entity.username)

async def extract_group_usernames(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.entity.username:
            print(dialog.entity.username)

async def send_messages_to_users(client):
    message = input("Enter the message to send: ")
    async for dialog in client.iter_dialogs():
        if dialog.is_user:
            await client.send_message(dialog.entity.id, message)
            print(f"Message sent to {dialog.entity.username}")
            await asyncio.sleep(5)

async def send_messages_to_groups(client):
    message = input("Enter the message to send: ")
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            await client.send_message(dialog.entity.id, message)
            print(f"Message sent to group {dialog.entity.title}")
            await asyncio.sleep(5)

with TelegramClient('session_name', PREDEFINED_API_ID, PREDEFINED_API_HASH) as client:
    client.loop.run_until_complete(main())
