import json
import os
from flask import Flask, request
import requests
from app import send 
from dotenv import load_dotenv
from threading import Timer
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TOKEN","123456:AAFdMW5A6a2e7y3A-valFNq9VMZUbDOrG98")
PORT = int(os.getenv("PORT", 5000))
UPDATE_TIME = int(os.getenv("UPDATE_TIME", 60))
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'
DATA_FILE = 'users.json'
app = Flask(__name__)
# Load or initialize user list
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(list(users), f)

# Send message to one user
def send_message(chat_ids, text):    
    send(chat_ids, TOKEN)
# Send message to all users
def broadcast_message():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    users = load_users()   
    send_message(users, "")
    for user_id in users:
       print(user_id)    
    Timer(UPDATE_TIME, broadcast_message).start()

@app.route('/', methods=['GET'])
def index():
    broadcast_message() 
    return "Bot is running."

@app.route(f"/webhook/{TOKEN}", methods=['POST'])
def webhook():
    data = request.json
    print(f"Add new user")
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        users = load_users()
        users.add(chat_id)
        save_users(users)

        # Example echo response
        send_message(users, f"You said: {text}")

    return 200

if __name__ == "__main__":
    # app.run(debug=False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
