"""
🛒 Telegram Store Bot Configuration
Powered by Pakasir.com Payment Gateway
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 TELEGRAM BOT SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))  # Your Telegram User ID
OWNER_NAME = os.getenv("OWNER_NAME", "Admin")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@admin")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏪 STORE SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT_NAME = "🛒 Smart Store Bot"
BOT_VERSION = "1.0.0"
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "yourchannel")
GROUP_USERNAME = os.getenv("GROUP_USERNAME", "yourgroup")
TESTIMONI_CHANNEL = os.getenv("TESTIMONI_CHANNEL", "@yourtestimoni")

# Welcome Photo URL (optional)
START_PHOTO = os.getenv("START_PHOTO", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💳 PAKASIR PAYMENT GATEWAY (QRIS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAKASIR_PROJECT = os.getenv("PAKASIR_PROJECT", "your_project_slug")
PAKASIR_API_KEY = os.getenv("PAKASIR_API_KEY", "your_api_key")
PAKASIR_BASE_URL = "https://app.pakasir.com"

# Payment timeout in seconds (15 minutes)
PAYMENT_TIMEOUT = 900

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 PRODUCT SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pterodactyl Panel Settings
PANEL_DOMAIN = os.getenv("PANEL_DOMAIN", "https://panel.example.com")
PANEL_API_KEY = os.getenv("PANEL_API_KEY", "")
PANEL_NEST_ID = int(os.getenv("PANEL_NEST_ID", "5"))
PANEL_EGG_ID = int(os.getenv("PANEL_EGG_ID", "15"))
PANEL_LOCATION_ID = int(os.getenv("PANEL_LOCATION_ID", "1"))

# Panel Pricing
PANEL_PRICES = {
    "unlimited": 2000,
    "per_gb": 750,
    "admin": 10000,
    "reseller": 5000
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 UI SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMOJI = {
    "store": "🛒",
    "money": "💰",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "user": "👤",
    "admin": "👑",
    "payment": "💳",
    "qris": "📱",
    "back": "🔙",
    "menu": "📋",
    "product": "📦",
    "script": "📁",
    "panel": "🖥️",
    "app": "📱",
    "tools": "🛠️",
    "stats": "📊",
    "time": "⏰",
    "check": "✓",
    "cross": "✗",
    "star": "⭐",
    "fire": "🔥",
    "rocket": "🚀",
    "gem": "💎",
    "crown": "👑",
    "gift": "🎁",
    "cart": "🛍️",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📂 DATABASE SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATABASE_PATH = "database/store.db"
