import os
import json
import requests
import hashlib
from flask import Flask, request

app = Flask(__name__)

# إعدادات تيليجرام
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# إعدادات AliExpress Affiliate
ALI_APP_KEY = os.getenv("ALI_APP_KEY")
ALI_APP_SECRET = os.getenv("ALI_APP_SECRET")
ALI_TRACKING_ID = os.getenv("ALI_TRACKING_ID", "default")

def generate_signature(app_secret, params):
    sorted_params = sorted(params.items())
    base_string = app_secret + ''.join(f"{k}{v}" for k, v in sorted_params) + app_secret
    return hashlib.md5(base_string.encode('utf-8')).hexdigest().upper()

def convert_to_affiliate_links(urls):
    api_url = "https://api.aliexpress.com/openapi/param2/2/portals.open/api.getPromotionLinks"
    params = {
        "app_key": ALI_APP_KEY,
        "tracking_id": ALI_TRACKING_ID,
        "urls": ','.join(urls)
    }
    params["sign"] = generate_signature(ALI_APP_SECRET, params)

    try:
        r = requests.get(api_url, params=params)
        print("AliExpress API response:", r.text)
        data = r.json()
        links = [item["promotion_link"] for item in data["result"]["promotion_links"]]
        return links
    except:
        return urls

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    })

# =======================
#  استقبال رسائل التلغرام
# =======================
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    print(update)

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # استخراج أي رابط من الرسالة
        urls = [word for word in text.split() if "aliexpress" in word or "a.aliexpress" in word]

        if urls:
            aff_links = convert_to_affiliate_links(urls)
            msg = "🔗 روابط الأفلييت:\n" + "\n".join(aff_links)
            send_message(chat_id, msg)
        else:
            send_message(chat_id, "أرسل رابط AliExpress لتحويله 🌟")

    return "OK"

# =======================
#  AliExpress Callback
# =======================
@app.route("/api/callback", methods=["POST"])
def callback():
    event_type = request.headers.get('x-ae-event')
    payload = request.json
    print("Event:", event_type, "Payload:", payload)

    message = f"📦 Event: {event_type}\n```json\n{json.dumps(payload, indent=2)}\n```"
    send_message(os.getenv("TELEGRAM_CHAT_ID"), message)
    return "OK"

@app.route("/test")
def test():
    send_message(os.getenv("TELEGRAM_CHAT_ID"), "✅ الاختبار ناجح يا نور الدين!")
    return "OK"

if __name__ == "__main__":
    app.run()
