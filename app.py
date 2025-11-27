import os
import json
import requests
import hashlib
from flask import Flask, request

app = Flask(__name__)

# ==========================
# إعدادات تيليجرام
# ==========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ==========================
# إعدادات AliExpress Affiliate
# ==========================
ALI_APP_KEY = os.getenv("ALI
