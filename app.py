import os
import json
import requests
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

# إرسال رسالة إلى تيليجرام
def send_telegram_message(text, parse_mode="Markdown"):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ متغيرات تيليجرام ناقصة")
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

# تحويل رابط إلى أفلييت
def convert_to_affiliate_link(product_url):
    api_url = "https://api.aliexpress.com/openapi/param2/2/portals.open/api.getPromotionLinks"
    params = {
        "app_key": ALI_APP_KEY,
        "tracking_id": ALI_TRACKING_ID,
        "urls": product_url
    }
    try:
        r = requests.get(api_url, params=params, timeout=5)
        print("📡 رد AliExpress API:", r.text)
        data = r.json()
        promo_link = data["result"]["promotion_links"][0]["promotion_link"]
        print("🔗 رابط الأفلييت المحول:", promo_link)
        return promo_link
    except Exception as e:
        print(f"❌ Affiliate error: {e}")
        return product_url  # fallback

# تخصيص الرسالة حسب نوع الحدث
def format_event_message(event_type, payload):
    if "product_url" in payload:
        print("📥 رابط المنتج الأصلي:", payload["product_url"])
        affiliate_link = convert_to_affiliate_link(payload["product_url"])
        return f"🔗 رابط الأفلييت:\n{affiliate_link}"

    if event_type == "order_created":
        order_id = payload.get("order_id", "غير معروف")
        amount = payload.get("amount", "؟")
        return f"🛒 تم إنشاء طلب جديد!\nرقم الطلب: `{order_id}`\nالقيمة: `{amount}`"
    
    elif event_type == "order_shipped":
        order_id = payload.get("order_id", "غير معروف")
        tracking = payload.get("tracking_number", "غير متوفر")
        date = payload.get("ship_date", "غير محدد")
        return f"📦 تم شحن الطلب رقم `{order_id}`\nرقم التتبع: `{tracking}`\nتاريخ الشحن: `{date}`"
    
    elif event_type == "product_updated":
        name = payload.get("product_name", "منتج غير معروف")
        price = payload.get("new_price", "؟")
        return f"🛍️ تم تحديث منتج:\n`{name}`\nالسعر الجديد: `{price}`"
    
    else:
        title = f"*AliExpress Event:* `{event_type or 'unknown'}`"
        body = f"```json\n{json.dumps(payload or {}, ensure_ascii=False, indent=2)}\n```"
        return f"{title}\n{body}"

# نقطة استقبال الأحداث
@app.route('/api/callback', methods=['POST'])
def callback():
    try:
        event_type = request.headers.get('x-ae-event')
        payload = request.get_json(silent=True)

        print(f"📦 Event: {event_type}")
        print(f"📄 Payload: {payload}")

        msg = format_event_message(event_type, payload)
        send_telegram_message(msg)

        return 'OK', 200
    except Exception as e:
        print(f"❌ Callback error: {e}")
        return 'OK', 200

# نقطة اختبار
@app.route('/test', methods=['GET'])
def test_telegram():
    msg = "✅ اختبار مباشر من /test يا نور الدين"
    success = send_telegram_message(msg)
    return "تم الإرسال" if success else "فشل الإرسال"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
