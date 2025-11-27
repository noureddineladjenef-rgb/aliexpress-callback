import os
import json
import requests
import hashlib
from flask import Flask, request

app = Flask(__name__)

# إعدادات تيليجرام
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# إعدادات AliExpress Affiliate
ALI_APP_KEY = os.getenv("ALI_APP_KEY")
ALI_APP_SECRET = os.getenv("ALI_APP_SECRET")
ALI_TRACKING_ID = os.getenv("ALI_TRACKING_ID")

# توليد التوقيع
def generate_signature(secret, params):
    sorted_params = sorted(params.items())
    base_string = secret + ''.join(f"{k}{v}" for k, v in sorted_params) + secret
    return hashlib.md5(base_string.encode('utf-8')).hexdigest().upper()

# إرسال رسالة إلى تيليجرام
def send_telegram_message(text, parse_mode="Markdown"):
    print(f"📤 رابط تيليجرام المستخدم: {TELEGRAM_API}")
    print(f"📤 معرف الشات: {TELEGRAM_CHAT_ID}")
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(TELEGRAM_API, json=payload, timeout=5)
        print(f"✅ Telegram status: {response.status_code}")
        print(f"📨 Telegram response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

# تحويل روابط إلى أفلييت
def convert_to_affiliate_links(urls):
    api_url = "https://api.aliexpress.com/openapi/param2/2/portals.open/api.getPromotionLinks"
    params = {
        "app_key": ALI_APP_KEY,
        "tracking_id": ALI_TRACKING_ID,
        "urls": ','.join(urls)
    }
    params["sign"] = generate_signature(ALI_APP_SECRET, params)

    try:
        r = requests.get(api_url, params=params, timeout=5)
        print("📡 رد AliExpress API:", r.text)
        data = r.json()
        links = [item["promotion_link"] for item in data["result"]["promotion_links"]]
        return links
    except Exception as e:
        print(f"❌ Affiliate error: {e}")
        return urls

# تخصيص الرسالة حسب نوع الحدث
def format_event_message(event_type, payload):
    if "urls" in payload:
        print("📥 روابط المنتجات:", payload["urls"])
        affiliate_links = convert_to_affiliate_links(payload["urls"])
        msg = "🔗 روابط الأفلييت:\n" + "\n".join(affiliate_links)
        return msg

    if "product_url" in payload:
        affiliate_links = convert_to_affiliate_links([payload["product_url"]])
        return f"🔗 رابط الأفلييت:\n{affiliate_links[0]}"

    return f"*AliExpress Event:* `{event_type}`\n```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"

# نقطة استقبال الأحداث
@app.route('/api/callback', methods=['POST'])
def callback():
    event_type = request.headers.get('x-ae-event')
    payload = request.get_json(silent=True)

    print(f"📦 Event: {event_type}")
    print(f"📄 Payload: {payload}")

    msg = format_event_message(event_type, payload)
    send_telegram_message(msg)

    return 'OK', 200

# نقطة—
