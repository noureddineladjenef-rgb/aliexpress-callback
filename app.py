from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


# ========= Webhook Telegram =========
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # رد بسيط للتجربة
        requests.post(TELEGRAM_API, json={
            "chat_id": chat_id,
            "text": f"لقد وصلني: {text}"
        })

    return "OK", 200
