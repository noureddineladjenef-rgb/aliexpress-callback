import os, json, hmac, hashlib, time, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# إعدادات البيئة
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ALI_APP_KEY = os.getenv("ALI_APP_KEY")
ALI_APP_SECRET = os.getenv("ALI_APP_SECRET")
ALI_TRACKING_ID = os.getenv("ALI_TRACKING_ID")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    base_string = app_secret + ''.join(f"{k}{v}" for k, v in sorted_params) + app_secret
    return hashlib.md5(base_string.encode('utf-8')).hexdigest().upper()

def convert_urls_to_affiliate(urls):
    timestamp = str(int(time.time() * 1000))
    params = {
        "app_key": ALI_APP_KEY,
        "timestamp": timestamp,
        "tracking_id": ALI_TRACKING_ID,
        "urls": ','.join(urls)
    }
    sign = generate_signature(params, ALI_APP_SECRET)
    params["sign"] = sign

    print("📡 إرسال طلب إلى AliExpress:", params)
    response = requests.get("https://api.aliexpress.com/sync/convertLinks", params=params)
    print("📡 رد AliExpress API:", response.text)

    data = response.json()
    links = [item["promotion_link"] for item in data.get("promotion_links", [])]
    return links

def send_to_telegram(text):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    print("📤 رابط تيليجرام المستخدم:", TELEGRAM_API)
    response = requests.post(TELEGRAM_API, json=payload)
    print("📨 Telegram response:", response.text)

@app.route("/api/callback", methods=["POST"])
def callback():
    body = request.get_json()
    print("📥 استلام من AliExpress:", body)

    urls = body.get("urls", [])
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    links = convert_urls_to_affiliate(urls)
    if links:
        message = "🔗 روابط الأفلييت:\n" + "\n".join(links)
        send_to_telegram(message)
        return jsonify({"status": "sent", "links": links}), 200
    else:
        return jsonify({"error": "No affiliate links returned"}), 500

@app.route("/convert", methods=["POST"])
def convert():
    body = request.get_json()
    urls = body.get("urls", [])
    links = convert_urls_to_affiliate(urls)
    return jsonify({"converted": links})

@app.route("/debug", methods=["GET"])
def debug():
    debug_info = {
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "ALI_APP_KEY": ALI_APP_KEY,
        "ALI_APP_SECRET": ALI_APP_SECRET,
        "ALI_TRACKING_ID": ALI_TRACKING_ID
    }
    return json.dumps(debug_info, ensure_ascii=False, indent=2), 200
