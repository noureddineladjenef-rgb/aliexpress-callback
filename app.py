from flask import Flask, request

app = Flask(__name__)

@app.route('/api/callback', methods=['POST'])
def callback():
    # قراءة الترويسات
    event_type = request.headers.get('x-ae-event')
    signature = request.headers.get('x-ae-signature')
    timestamp = request.headers.get('x-ae-timestamp')

    # قراءة الجسم (Body)
    payload = request.get_json()

    # طباعة البيانات في السجل
    print(f"📦 Event: {event_type}")
    print(f"🔐 Signature: {signature}")
    print(f"🕒 Timestamp: {timestamp}")
    print(f"📄 Payload: {payload}")

    # رد سريع لتجنب timeout
    return 'OK', 200

# تعديل مهم لتشغيل التطبيق على Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
