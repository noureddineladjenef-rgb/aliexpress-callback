import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

# قراءة المتغيرات من بيئة Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# دالة إرسال رسالة إلى تيليجرام
def send_telegram_message(text, parse_mode="Markdown"):
    print(f"📌 TOKEN: {TELEGRAM_TOKEN}")
    print(f"📌 CHAT_ID: {TELEGRAM_CHAT_ID}")
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ متغيرات تيليجرام غير موجودة")
        return False
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

# تنسيق الرسالة حسب نوع الحدث
def format_event_message(event_type, payload):
    title = f"*AliExpress Event:* `{event_type or 'unknown'}`"
    body = f"```json\n{json.dumps(payload or {}, ensure_ascii=False, indent=2)}\n```"
    return f"{title}\n{body}"

# نقطة استقبال الأحداث من AliExpress
@app.route('/api/callback', methods=['POST'])
def callback():
    try:
        event_type = request.headers.get('x-ae-event')
        signature = request.headers.get('x-ae-signature')
        timestamp = request.headers.get('x-ae-timestamp')
        payload = request.get_json(silent=True)

        print(f"📦 Event: {event_type}")
        print(f"🔐 Signature: {signature}")
        print(f"🕒 Timestamp: {timestamp}")
        print(f"📄 Payload: {payload}")

        # إرسال إلى تيليجرام
        msg = format_event_message(event_type, payload)
        send_telegram_message(msg)

        return 'OK', 200
    except Exception as e:
        print(f"❌ Callback error: {e}")
        return 'OK', 200

# نقطة اختبار مباشرة
@app.route('/test', methods=['GET'])
def test_telegram():
    msg = "✅ اختبار مباشر من /test يا نور الدين"
    success = send_telegram_message(msg)
    return "تم الإرسال" if success else "فشل الإرسال"

# تشغيل التطبيق على Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
