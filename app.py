import os
import json
import time
import hmac
import hashlib
import base64
import requests
from flask import Flask, request

app = Flask(__name__)

# ==========================
#   TELEGRAM SETTINGS
# ==========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


# ==========================
#   AE API SETTINGS
# ==========================
ALI_APP_KEY = os.getenv("ALI_APP_KEY")
ALI_APP_SECRET = os.getenv("ALI_APP_SECRET")
ALI_TRACKING_ID = os.getenv("ALI_TRACKING_ID", "default")

AE_API_URL = "https://api.aliexpress.com/sync"


# ==========================
#   SIGNATURE GENERATION
# ==========================
def generate_signature(app_secret, data_str):
    h = hmac.new(app_secret.encode("utf-8"),
                 data_str.encode("utf-8"),
                 digestmod=hashlib.sha256)
    return base64.b64encode(h.digest()).decode()


# ==========================
#   TELEGRAM SENDER
# ==========================
def send_telegram_message(text):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(TELEGRAM_URL, json=payload, timeout=5)
        print("Telegram:", r.text)
    except Exception as e:
        print("Telegram Error:", e)


# ==========================
#   ALIEXPRESS LINK GENERATOR
# ==========================
def generate_affiliate_links(url_list):

    body = {
        "promotion_link_request": {
            "tracking_id": ALI_TRACKING_ID,
            "source_values": url_list
        }
    }

    body_str = json.dumps(body, separators=(',', ':'))
    data_to_sign = f"{ALI_APP_KEY}{body_str}"
    signature = generate_signature(ALI_APP_SECRET, data_to_sign)

    headers = {
        "Content-Type": "application/json",
        "x-ae-app-key": ALI_APP_KEY,
        "x-ae-signature": signature
    }

    r = requests.post(AE_API_URL, headers=headers, data=body_str)
    print("AliExpress API Response:", r.text)

    try:
        jd = r.json()

        links = []
        promotion_list = jd["resp_result"]["result"]["promotion_links"]

        for item in promotion_list:
            links.append(item["promotion_link"])

        return links

    except:
        return url_list


# ==========================
#   EVENT FORMATTER
# ==========================
def format_event_message(event_type, payload):

    if not payload:
        return "📭 لا يوجد Payload"

    # Payload فيه روابط مباشرة
    if "urls" in payload:
        urls = payload["urls"]
        aff = generate_affiliate_links(urls)
        return "🔗 *روابط الأفلييت:*\n" + "\n".join(aff)

    if "product_url" in payload:
        aff = generate_affiliate_links([payload["product_url"]])
        return "🔗 *الرابط:* \n" + aff[0]

    return f"*AliExpress Event:* `{event_type}`"


# ==========================
#   WEBHOOK ROUTE
# ==========================
@app.route('/api/callback', methods=['POST'])
def callback():
    event = request.headers.get("x-ae-event")
    payload = request.get_json(silent=True)

    print("EVENT:", event)
    print("PAYLOAD:", payload)

    msg = format_event_message(event, payload)
    send_telegram_message(msg)

    return "OK", 200


# ==========================
#   TEST ROUTE
# ==========================
@app.route('/test', methods=['GET'])
def test():
    send_telegram_message("🔔 اختبار ناجح يا نور الدين!")
    return "تم الإرسال بنجاح", 200


# ==========================
#   RUN SERVER
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
