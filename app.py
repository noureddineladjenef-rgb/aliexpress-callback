@app.route('/debug', methods=['GET'])
def debug():
    debug_info = {
        "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "ALI_APP_KEY": os.getenv("ALI_APP_KEY"),
        "ALI_APP_SECRET": os.getenv("ALI_APP_SECRET"),
        "ALI_TRACKING_ID": os.getenv("ALI_TRACKING_ID"),
    }
    return json.dumps(debug_info, ensure_ascii=False, indent=2), 200
