from flask import Flask, request

app = Flask(__name__)

@app.route('/api/callback', methods=['POST'])
def callback():
    event_type = request.headers.get('x-ae-event')
    signature = request.headers.get('x-ae-signature')
    timestamp = request.headers.get('x-ae-timestamp')
    payload = request.get_json()

    print(f"📦 Event: {event_type}")
    print(f"🔐 Signature: {signature}")
    print(f"🕒 Timestamp: {timestamp}")
    print(f"📄 Payload: {payload}")

    return 'OK', 200

if __name__ == '__main__':
    app.run()
