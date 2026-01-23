#!/usr/bin/env python3
"""
🏪 PREMIUM APPS STORE - Sistem Penjualan Aplikasi Premium
Terintegrasi dengan Payment Gateway Pakasir.com (QRIS Only)

Author: Auto Generated
Version: 1.0.0
"""

import os
import json
import sqlite3
import hashlib
import hmac
import secrets
import asyncio
import logging
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps

import requests
from flask import Flask, request, jsonify, render_template_string
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
    CallbackQuery
)

# ================================
# 📋 KONFIGURASI
# ================================

class Config:
    """Konfigurasi aplikasi"""
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Pakasir.com Payment Gateway
    PAKASIR_PROJECT_SLUG = os.getenv("PAKASIR_PROJECT_SLUG", "your_project_slug")
    PAKASIR_API_KEY = os.getenv("PAKASIR_API_KEY", "your_api_key")
    PAKASIR_BASE_URL = "https://app.pakasir.com"
    
    # Webhook URL (untuk menerima notifikasi pembayaran)
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://your-domain.com")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 5000))
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "premium_store.db")
    
    # Admin Telegram IDs (pisahkan dengan koma)
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]
    
    # Order Settings
    ORDER_EXPIRY_MINUTES = 30
    
    # Store Info
    STORE_NAME = "🚀 Premium Apps Store"
    STORE_DESCRIPTION = "Toko Aplikasi Premium Terpercaya"


# ================================
# 📊 ENUMS & DATA CLASSES
# ================================

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    DELIVERED = "delivered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ProductCategory(Enum):
    STREAMING = "🎬 Streaming"
    PRODUCTIVITY = "💼 Produktivitas"
    EDUCATION = "📚 Edukasi"
    GAMING = "🎮 Gaming"
    VPN = "🔐 VPN & Keamanan"
    DESIGN = "🎨 Desain"
    OTHER = "📦 Lainnya"


@dataclass
class Product:
    id: int
    name: str
    description: str
    price: int
    category: str
    duration: str  # e.g., "1 Bulan", "1 Tahun", "Lifetime"
    stock: int
    is_active: bool
    created_at: str
    image_url: Optional[str] = None


@dataclass
class Order:
    id: str
    user_id: int
    username: str
    product_id: int
    product_name: str
    amount: int
    status: str
    payment_qr: Optional[str]
    payment_url: Optional[str]
    license_key: Optional[str]
    created_at: str
    expired_at: str
    paid_at: Optional[str] = None
    delivered_at: Optional[str] = None


@dataclass
class User:
    id: int
    username: str
    first_name: str
    last_name: Optional[str]
    total_orders: int
    total_spent: int
    joined_at: str
    is_banned: bool = False


# ================================
# 🗄️ DATABASE MANAGER
# ================================

class DatabaseManager:
    """Manager untuk operasi database SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inisialisasi tabel-tabel database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabel Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                total_orders INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                joined_at TEXT,
                is_banned INTEGER DEFAULT 0
            )
        """)
        
        # Tabel Products
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                category TEXT,
                duration TEXT,
                stock INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                image_url TEXT,
                created_at TEXT
            )
        """)
        
        # Tabel Orders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                username TEXT,
                product_id INTEGER,
                product_name TEXT,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                payment_qr TEXT,
                payment_url TEXT,
                license_key TEXT,
                created_at TEXT,
                expired_at TEXT,
                paid_at TEXT,
                delivered_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Tabel License Keys (Pre-generated)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS license_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                key_value TEXT UNIQUE,
                is_used INTEGER DEFAULT 0,
                order_id TEXT,
                created_at TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Tabel Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Tambahkan produk sample jika belum ada
        self._add_sample_products()
    
    def _add_sample_products(self):
        """Tambahkan produk sample"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ("Netflix Premium 4K", "Akses lengkap ke semua film dan series Netflix dengan kualitas 4K UHD. Sharing slot aman.", 45000, "🎬 Streaming", "1 Bulan", 50),
                ("Spotify Premium Family", "Musik tanpa batas tanpa iklan. Dapat digunakan hingga 6 akun dalam 1 family.", 25000, "🎬 Streaming", "1 Bulan", 100),
                ("YouTube Premium", "Nonton YouTube tanpa iklan + YouTube Music Premium. Fitur download & background play.", 35000, "🎬 Streaming", "1 Bulan", 75),
                ("Canva Pro", "Desain professional dengan akses ke jutaan template, foto, dan video premium.", 30000, "🎨 Desain", "1 Bulan", 40),
                ("NordVPN Premium", "VPN tercepat dan teraman. Lindungi privasi online Anda dengan enkripsi tingkat militer.", 50000, "🔐 VPN & Keamanan", "1 Bulan", 30),
                ("Microsoft 365", "Akses penuh ke Word, Excel, PowerPoint, dan 1TB OneDrive cloud storage.", 40000, "💼 Produktivitas", "1 Bulan", 60),
                ("ChatGPT Plus", "Akses GPT-4 dan fitur premium lainnya untuk produktivitas maksimal.", 150000, "💼 Produktivitas", "1 Bulan", 20),
                ("Grammarly Premium", "Koreksi grammar dan writing assistant terbaik untuk professional.", 35000, "📚 Edukasi", "1 Bulan", 45),
                ("Skillshare Premium", "Akses ribuan kelas online dari kreator dan expert terbaik dunia.", 25000, "📚 Edukasi", "1 Bulan", 55),
                ("Discord Nitro", "Boost server, emoji kustom, upload file besar, dan fitur premium Discord.", 40000, "🎮 Gaming", "1 Bulan", 80),
            ]
            
            for name, desc, price, category, duration, stock in sample_products:
                cursor.execute("""
                    INSERT INTO products (name, description, price, category, duration, stock, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """, (name, desc, price, category, duration, stock, datetime.now().isoformat()))
            
            conn.commit()
        
        conn.close()


# ================================
# 💳 PAKASIR PAYMENT GATEWAY
# ================================

class PakasirPayment:
    """Handler untuk integrasi dengan Pakasir.com Payment Gateway"""
    
    def __init__(self):
        self.base_url = Config.PAKASIR_BASE_URL
        self.project_slug = Config.PAKASIR_PROJECT_SLUG
        self.api_key = Config.PAKASIR_API_KEY
    
    def create_qris_transaction(self, order_id: str, amount: int) -> Dict[str, Any]:
        """
        Membuat transaksi QRIS baru
        
        Args:
            order_id: ID order unik
            amount: Jumlah pembayaran dalam Rupiah
            
        Returns:
            Dict dengan informasi pembayaran (QR string, total, expired_at)
        """
        url = f"{self.base_url}/api/transactioncreate/qris"
        
        payload = {
            "project": self.project_slug,
            "order_id": order_id,
            "amount": amount,
            "api_key": self.api_key
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "payment" in data:
                payment = data["payment"]
                return {
                    "success": True,
                    "order_id": payment.get("order_id"),
                    "amount": payment.get("amount"),
                    "fee": payment.get("fee", 0),
                    "total_payment": payment.get("total_payment"),
                    "payment_number": payment.get("payment_number"),  # QR String
                    "expired_at": payment.get("expired_at"),
                    "payment_method": payment.get("payment_method")
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid response from payment gateway"
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Payment gateway error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment_url(self, order_id: str, amount: int, redirect_url: Optional[str] = None) -> str:
        """
        Generate URL pembayaran langsung ke Pakasir
        
        Args:
            order_id: ID order
            amount: Jumlah pembayaran
            redirect_url: URL redirect setelah pembayaran
            
        Returns:
            URL pembayaran
        """
        url = f"{self.base_url}/pay/{self.project_slug}/{amount}?order_id={order_id}&qris_only=1"
        
        if redirect_url:
            url += f"&redirect={redirect_url}"
        
        return url
    
    def check_transaction_status(self, order_id: str, amount: int) -> Dict[str, Any]:
        """
        Cek status transaksi
        
        Args:
            order_id: ID order
            amount: Jumlah pembayaran
            
        Returns:
            Dict dengan status transaksi
        """
        url = f"{self.base_url}/api/transactiondetail"
        
        params = {
            "project": self.project_slug,
            "order_id": order_id,
            "amount": amount,
            "api_key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "transaction" in data:
                return {
                    "success": True,
                    "transaction": data["transaction"]
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction not found"
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Check status error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_transaction(self, order_id: str, amount: int) -> Dict[str, Any]:
        """
        Batalkan transaksi
        
        Args:
            order_id: ID order
            amount: Jumlah pembayaran
            
        Returns:
            Dict dengan hasil pembatalan
        """
        url = f"{self.base_url}/api/transactioncancel"
        
        payload = {
            "project": self.project_slug,
            "order_id": order_id,
            "amount": amount,
            "api_key": self.api_key
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            return {"success": response.status_code == 200}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def generate_qr_image(qr_string: str) -> bytes:
        """
        Generate gambar QR Code dari QR string
        
        Args:
            qr_string: String QRIS
            
        Returns:
            Bytes gambar PNG
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer.getvalue()


# ================================
# 🤖 TELEGRAM BOT HANDLER
# ================================

class PremiumStoreBot:
    """Handler untuk Telegram Bot"""
    
    def __init__(self):
        self.bot = TeleBot(Config.TELEGRAM_BOT_TOKEN)
        self.db = DatabaseManager(Config.DATABASE_PATH)
        self.payment = PakasirPayment()
        self.user_states = {}  # Untuk menyimpan state user
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup semua handler bot"""
        
        # Command handlers
        @self.bot.message_handler(commands=['start'])
        def handle_start(message: Message):
            self._handle_start(message)
        
        @self.bot.message_handler(commands=['menu', 'katalog'])
        def handle_menu(message: Message):
            self._show_main_menu(message)
        
        @self.bot.message_handler(commands=['pesanan', 'orders'])
        def handle_orders(message: Message):
            self._show_user_orders(message)
        
        @self.bot.message_handler(commands=['bantuan', 'help'])
        def handle_help(message: Message):
            self._show_help(message)
        
        @self.bot.message_handler(commands=['admin'])
        def handle_admin(message: Message):
            self._show_admin_panel(message)
        
        @self.bot.message_handler(commands=['cekstatus'])
        def handle_check_status(message: Message):
            self._handle_check_payment_status(message)
        
        # Callback query handlers
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call: CallbackQuery):
            self._handle_callback_query(call)
    
    def _generate_order_id(self) -> str:
        """Generate ID order unik"""
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        random_part = secrets.token_hex(3).upper()
        return f"PRE{timestamp}{random_part}"
    
    def _save_user(self, user: Message):
        """Simpan atau update data user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE id = ?", (user.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO users (id, username, first_name, last_name, joined_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user.from_user.id,
                user.from_user.username or "",
                user.from_user.first_name or "",
                user.from_user.last_name or "",
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def _is_admin(self, user_id: int) -> bool:
        """Cek apakah user adalah admin"""
        return user_id in Config.ADMIN_IDS
    
    def _handle_start(self, message: Message):
        """Handler untuk command /start"""
        self._save_user(message)
        
        welcome_text = f"""
🎉 *Selamat Datang di {Config.STORE_NAME}!*

{Config.STORE_DESCRIPTION}

━━━━━━━━━━━━━━━━━━━━━━

✨ *Mengapa Memilih Kami?*
• ✅ Harga Termurah & Terjangkau
• ✅ Proses Instan & Otomatis
• ✅ Garansi Full Masa Aktif
• ✅ Support 24/7

💳 *Metode Pembayaran:*
• 📱 QRIS (Semua E-Wallet & Bank)

━━━━━━━━━━━━━━━━━━━━━━

Gunakan tombol di bawah untuk mulai berbelanja! 👇
"""
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🛒 Lihat Katalog", callback_data="catalog"),
            InlineKeyboardButton("📋 Pesanan Saya", callback_data="my_orders")
        )
        keyboard.row(
            InlineKeyboardButton("💬 Bantuan", callback_data="help"),
            InlineKeyboardButton("ℹ️ Tentang", callback_data="about")
        )
        
        self.bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _show_main_menu(self, message: Message):
        """Tampilkan menu utama"""
        self._save_user(message)
        
        menu_text = f"""
🏪 *{Config.STORE_NAME}*

Pilih kategori produk yang Anda inginkan:
"""
        
        keyboard = InlineKeyboardMarkup()
        
        # Tampilkan kategori
        categories = [
            ("🎬 Streaming", "cat_streaming"),
            ("💼 Produktivitas", "cat_productivity"),
            ("📚 Edukasi", "cat_education"),
            ("🎮 Gaming", "cat_gaming"),
            ("🔐 VPN & Keamanan", "cat_vpn"),
            ("🎨 Desain", "cat_design"),
        ]
        
        for i in range(0, len(categories), 2):
            row = [InlineKeyboardButton(categories[i][0], callback_data=categories[i][1])]
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[i+1][0], callback_data=categories[i+1][1]))
            keyboard.row(*row)
        
        keyboard.row(
            InlineKeyboardButton("📦 Semua Produk", callback_data="catalog")
        )
        keyboard.row(
            InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
        )
        
        self.bot.send_message(
            message.chat.id,
            menu_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _show_catalog(self, chat_id: int, category: Optional[str] = None, message_id: Optional[int] = None):
        """Tampilkan katalog produk"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT * FROM products WHERE is_active = 1 AND category = ? ORDER BY name
            """, (category,))
        else:
            cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY category, name")
        
        products = cursor.fetchall()
        conn.close()
        
        if not products:
            text = "😔 Tidak ada produk yang tersedia saat ini."
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton("🏠 Menu Utama", callback_data="home"))
        else:
            category_title = category if category else "Semua Produk"
            text = f"📦 *{category_title}*\n\n"
            text += "Pilih produk untuk melihat detail:\n\n"
            
            keyboard = InlineKeyboardMarkup()
            
            for product in products:
                stock_status = "✅" if product['stock'] > 0 else "❌"
                price_formatted = f"Rp {product['price']:,}".replace(",", ".")
                btn_text = f"{stock_status} {product['name']} - {price_formatted}"
                keyboard.row(
                    InlineKeyboardButton(btn_text, callback_data=f"product_{product['id']}")
                )
            
            keyboard.row(
                InlineKeyboardButton("🔙 Kembali", callback_data="menu"),
                InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
            )
        
        if message_id:
            self.bot.edit_message_text(
                text,
                chat_id,
                message_id,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            self.bot.send_message(
                chat_id,
                text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    
    def _show_product_detail(self, chat_id: int, product_id: int, message_id: int):
        """Tampilkan detail produk"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        
        if not product:
            self.bot.edit_message_text(
                "❌ Produk tidak ditemukan.",
                chat_id,
                message_id
            )
            return
        
        stock_emoji = "✅ Tersedia" if product['stock'] > 0 else "❌ Habis"
        price_formatted = f"Rp {product['price']:,}".replace(",", ".")
        
        text = f"""
📱 *{product['name']}*

━━━━━━━━━━━━━━━━━━━━━━

📝 *Deskripsi:*
{product['description']}

💰 *Harga:* {price_formatted}
⏱️ *Durasi:* {product['duration']}
📦 *Stok:* {stock_emoji} ({product['stock']} unit)

━━━━━━━━━━━━━━━━━━━━━━

💳 *Pembayaran via QRIS*
(Semua E-Wallet & Mobile Banking)
"""
        
        keyboard = InlineKeyboardMarkup()
        
        if product['stock'] > 0:
            keyboard.row(
                InlineKeyboardButton(f"🛒 Beli Sekarang - {price_formatted}", callback_data=f"buy_{product['id']}")
            )
        else:
            keyboard.row(
                InlineKeyboardButton("📢 Notify Stok", callback_data=f"notify_{product['id']}")
            )
        
        keyboard.row(
            InlineKeyboardButton("🔙 Kembali", callback_data="catalog"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
        )
        
        self.bot.edit_message_text(
            text,
            chat_id,
            message_id,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _process_order(self, chat_id: int, user_id: int, username: str, product_id: int, message_id: int):
        """Proses pembuatan order"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get product
        cursor.execute("SELECT * FROM products WHERE id = ? AND is_active = 1", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            self.bot.edit_message_text(
                "❌ Produk tidak tersedia.",
                chat_id,
                message_id
            )
            return
        
        if product['stock'] <= 0:
            self.bot.edit_message_text(
                "❌ Maaf, stok produk habis.",
                chat_id,
                message_id
            )
            return
        
        # Generate order ID
        order_id = self._generate_order_id()
        amount = product['price']
        
        # Create payment
        self.bot.edit_message_text(
            "⏳ *Memproses pesanan Anda...*\n\nMohon tunggu sebentar.",
            chat_id,
            message_id,
            parse_mode="Markdown"
        )
        
        # Buat transaksi QRIS via Pakasir
        payment_result = self.payment.create_qris_transaction(order_id, amount)
        
        if not payment_result.get("success"):
            # Fallback ke payment URL
            payment_url = self.payment.get_payment_url(order_id, amount)
            
            expired_at = (datetime.now() + timedelta(minutes=Config.ORDER_EXPIRY_MINUTES)).isoformat()
            
            # Simpan order
            cursor.execute("""
                INSERT INTO orders (id, user_id, username, product_id, product_name, amount, status, payment_url, created_at, expired_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
            """, (order_id, user_id, username, product_id, product['name'], amount, payment_url, datetime.now().isoformat(), expired_at))
            
            conn.commit()
            conn.close()
            
            price_formatted = f"Rp {amount:,}".replace(",", ".")
            
            text = f"""
📋 *INVOICE PEMBAYARAN*

━━━━━━━━━━━━━━━━━━━━━━

🆔 *Order ID:* `{order_id}`
📦 *Produk:* {product['name']}
💰 *Total:* {price_formatted}
⏱️ *Durasi:* {product['duration']}

━━━━━━━━━━━━━━━━━━━━━━

💳 *Cara Pembayaran:*
Klik tombol di bawah untuk membayar via QRIS

⚠️ *Penting:*
• Bayar sesuai nominal
• Pembayaran akan expired dalam {Config.ORDER_EXPIRY_MINUTES} menit
• Pesanan otomatis diproses setelah pembayaran

━━━━━━━━━━━━━━━━━━━━━━
"""
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton("💳 Bayar Sekarang", url=payment_url)
            )
            keyboard.row(
                InlineKeyboardButton("🔄 Cek Status", callback_data=f"check_{order_id}"),
                InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_{order_id}")
            )
            keyboard.row(
                InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
            )
            
            self.bot.edit_message_text(
                text,
                chat_id,
                message_id,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
        else:
            # Berhasil buat QRIS
            qr_string = payment_result.get("payment_number")
            total_payment = payment_result.get("total_payment", amount)
            expired_at = payment_result.get("expired_at", (datetime.now() + timedelta(minutes=Config.ORDER_EXPIRY_MINUTES)).isoformat())
            
            payment_url = self.payment.get_payment_url(order_id, amount)
            
            # Simpan order
            cursor.execute("""
                INSERT INTO orders (id, user_id, username, product_id, product_name, amount, status, payment_qr, payment_url, created_at, expired_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
            """, (order_id, user_id, username, product_id, product['name'], amount, qr_string, payment_url, datetime.now().isoformat(), expired_at))
            
            conn.commit()
            conn.close()
            
            # Generate QR Image
            qr_image = PakasirPayment.generate_qr_image(qr_string)
            
            total_formatted = f"Rp {total_payment:,}".replace(",", ".")
            fee = payment_result.get("fee", 0)
            fee_formatted = f"Rp {fee:,}".replace(",", ".") if fee else "Rp 0"
            
            text = f"""
📋 *INVOICE PEMBAYARAN*

━━━━━━━━━━━━━━━━━━━━━━

🆔 *Order ID:* `{order_id}`
📦 *Produk:* {product['name']}
⏱️ *Durasi:* {product['duration']}

━━━━━━━━━━━━━━━━━━━━━━

💰 *Rincian Pembayaran:*
• Harga: Rp {amount:,}
• Biaya Admin: {fee_formatted}
• *Total Bayar: {total_formatted}*

━━━━━━━━━━━━━━━━━━━━━━

📱 *SCAN QRIS DI ATAS*
Gunakan aplikasi E-Wallet atau Mobile Banking

⚠️ *PENTING:*
• Bayar sesuai nominal yang tertera
• Pembayaran expired dalam {Config.ORDER_EXPIRY_MINUTES} menit
• Otomatis terverifikasi setelah pembayaran

━━━━━━━━━━━━━━━━━━━━━━
"""
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton("🔄 Cek Status", callback_data=f"check_{order_id}"),
                InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_{order_id}")
            )
            keyboard.row(
                InlineKeyboardButton("💳 Buka Link Pembayaran", url=payment_url)
            )
            keyboard.row(
                InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
            )
            
            # Hapus pesan loading
            self.bot.delete_message(chat_id, message_id)
            
            # Kirim gambar QR
            self.bot.send_photo(
                chat_id,
                qr_image,
                caption=text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    
    def _check_order_status(self, chat_id: int, order_id: str, message_id: Optional[int] = None):
        """Cek status pembayaran order"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            text = "❌ Order tidak ditemukan."
            if message_id:
                self.bot.edit_message_text(text, chat_id, message_id)
            else:
                self.bot.send_message(chat_id, text)
            return
        
        # Cek status dari Pakasir
        status_result = self.payment.check_transaction_status(order_id, order['amount'])
        
        if status_result.get("success"):
            transaction = status_result.get("transaction", {})
            status = transaction.get("status", "pending")
            
            if status == "completed" and order['status'] == 'pending':
                # Update order status
                cursor.execute("""
                    UPDATE orders SET status = 'paid', paid_at = ? WHERE id = ?
                """, (datetime.now().isoformat(), order_id))
                conn.commit()
                
                # Kurangi stok
                cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (order['product_id'],))
                conn.commit()
                
                # Update user stats
                cursor.execute("""
                    UPDATE users SET total_orders = total_orders + 1, total_spent = total_spent + ?
                    WHERE id = ?
                """, (order['amount'], order['user_id']))
                conn.commit()
                
                # Ambil license key (jika ada)
                cursor.execute("""
                    SELECT key_value FROM license_keys 
                    WHERE product_id = ? AND is_used = 0 
                    LIMIT 1
                """, (order['product_id'],))
                license_row = cursor.fetchone()
                
                license_key = None
                if license_row:
                    license_key = license_row['key_value']
                    cursor.execute("""
                        UPDATE license_keys SET is_used = 1, order_id = ? WHERE key_value = ?
                    """, (order_id, license_key))
                    cursor.execute("""
                        UPDATE orders SET license_key = ?, status = 'delivered', delivered_at = ? WHERE id = ?
                    """, (license_key, datetime.now().isoformat(), order_id))
                    conn.commit()
                
                conn.close()
                
                # Kirim notifikasi sukses
                text = f"""
✅ *PEMBAYARAN BERHASIL!*

━━━━━━━━━━━━━━━━━━━━━━

🆔 *Order ID:* `{order_id}`
📦 *Produk:* {order['product_name']}
💰 *Jumlah:* Rp {order['amount']:,}

━━━━━━━━━━━━━━━━━━━━━━

"""
                if license_key:
                    text += f"""
🔐 *AKUN / LICENSE KEY:*
`{license_key}`

━━━━━━━━━━━━━━━━━━━━━━

📌 Simpan informasi ini dengan baik!
Jika ada kendala, hubungi admin.
"""
                else:
                    text += """
⏳ *Pesanan sedang diproses...*
Admin akan mengirim akun/license key Anda segera.

━━━━━━━━━━━━━━━━━━━━━━
"""
                
                keyboard = InlineKeyboardMarkup()
                keyboard.row(
                    InlineKeyboardButton("📋 Pesanan Saya", callback_data="my_orders"),
                    InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
                )
                
                if message_id:
                    try:
                        self.bot.edit_message_text(
                            text, chat_id, message_id,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                    except:
                        self.bot.send_message(
                            chat_id, text,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                else:
                    self.bot.send_message(
                        chat_id, text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                
                # Notifikasi ke admin
                self._notify_admin_new_order(order_id)
                
            else:
                conn.close()
                
                status_text = {
                    "pending": "⏳ Menunggu Pembayaran",
                    "completed": "✅ Sudah Dibayar",
                    "expired": "❌ Kadaluarsa",
                    "cancelled": "🚫 Dibatalkan"
                }.get(order['status'], "❓ Unknown")
                
                text = f"""
📋 *STATUS PESANAN*

━━━━━━━━━━━━━━━━━━━━━━

🆔 *Order ID:* `{order_id}`
📦 *Produk:* {order['product_name']}
💰 *Jumlah:* Rp {order['amount']:,}
📊 *Status:* {status_text}

━━━━━━━━━━━━━━━━━━━━━━
"""
                
                keyboard = InlineKeyboardMarkup()
                if order['status'] == 'pending':
                    keyboard.row(
                        InlineKeyboardButton("🔄 Refresh Status", callback_data=f"check_{order_id}"),
                        InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_{order_id}")
                    )
                    if order['payment_url']:
                        keyboard.row(
                            InlineKeyboardButton("💳 Bayar", url=order['payment_url'])
                        )
                keyboard.row(
                    InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
                )
                
                if message_id:
                    try:
                        self.bot.edit_message_text(
                            text, chat_id, message_id,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                    except:
                        self.bot.send_message(
                            chat_id, text,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                else:
                    self.bot.send_message(
                        chat_id, text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
        else:
            conn.close()
            text = f"⚠️ Tidak dapat memeriksa status pembayaran saat ini.\n\nOrder ID: `{order_id}`"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton("🔄 Coba Lagi", callback_data=f"check_{order_id}")
            )
            
            if message_id:
                self.bot.edit_message_text(
                    text, chat_id, message_id,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            else:
                self.bot.send_message(
                    chat_id, text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
    
    def _cancel_order(self, chat_id: int, order_id: str, message_id: int):
        """Batalkan order"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM orders WHERE id = ? AND status = 'pending'", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            self.bot.edit_message_text(
                "❌ Order tidak ditemukan atau sudah tidak dapat dibatalkan.",
                chat_id,
                message_id
            )
            conn.close()
            return
        
        # Cancel di Pakasir
        self.payment.cancel_transaction(order_id, order['amount'])
        
        # Update status
        cursor.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()
        
        text = f"""
🚫 *ORDER DIBATALKAN*

━━━━━━━━━━━━━━━━━━━━━━

🆔 *Order ID:* `{order_id}`
📦 *Produk:* {order['product_name']}
💰 *Jumlah:* Rp {order['amount']:,}

━━━━━━━━━━━━━━━━━━━━━━

Order Anda telah dibatalkan.
Silakan buat pesanan baru jika berminat.
"""
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🛒 Lihat Katalog", callback_data="catalog"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
        )
        
        self.bot.edit_message_text(
            text,
            chat_id,
            message_id,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _show_user_orders(self, message: Message):
        """Tampilkan riwayat pesanan user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10
        """, (message.from_user.id,))
        
        orders = cursor.fetchall()
        conn.close()
        
        if not orders:
            text = """
📋 *RIWAYAT PESANAN*

━━━━━━━━━━━━━━━━━━━━━━

Anda belum memiliki pesanan.
Yuk mulai belanja! 🛒
"""
        else:
            text = "📋 *RIWAYAT PESANAN*\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for order in orders:
                status_emoji = {
                    "pending": "⏳",
                    "paid": "✅",
                    "delivered": "📦",
                    "expired": "❌",
                    "cancelled": "🚫"
                }.get(order['status'], "❓")
                
                created = datetime.fromisoformat(order['created_at']).strftime("%d/%m/%Y %H:%M")
                
                text += f"{status_emoji} `{order['id']}`\n"
                text += f"📦 {order['product_name']}\n"
                text += f"💰 Rp {order['amount']:,}\n"
                text += f"📅 {created}\n\n"
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🛒 Lihat Katalog", callback_data="catalog"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
        )
        
        self.bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _show_help(self, message: Message):
        """Tampilkan bantuan"""
        text = f"""
📚 *BANTUAN - {Config.STORE_NAME}*

━━━━━━━━━━━━━━━━━━━━━━

📌 *Cara Order:*
1️⃣ Pilih produk dari katalog
2️⃣ Klik "Beli Sekarang"
3️⃣ Scan QRIS dengan E-Wallet/M-Banking
4️⃣ Pembayaran otomatis terverifikasi
5️⃣ Terima akun/license via bot

━━━━━━━━━━━━━━━━━━━━━━

📌 *Perintah Bot:*
• /start - Menu utama
• /menu - Lihat katalog
• /pesanan - Riwayat pesanan
• /cekstatus - Cek status pembayaran
• /bantuan - Halaman bantuan

━━━━━━━━━━━━━━━━━━━━━━

💳 *Metode Pembayaran:*
QRIS - Support semua E-Wallet & Bank:
• GoPay, OVO, DANA, ShopeePay
• BCA, Mandiri, BNI, BRI, dll

━━━━━━━━━━━━━━━━━━━━━━

⚠️ *Ketentuan:*
• Pembayaran harus sesuai nominal
• Pesanan expired dalam {Config.ORDER_EXPIRY_MINUTES} menit
• Garansi berlaku selama masa aktif
• Tidak ada refund setelah akun dikirim

━━━━━━━━━━━━━━━━━━━━━━

📩 Butuh bantuan? Hubungi admin!
"""
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("💬 Hubungi Admin", url="https://t.me/admin_username")
        )
        keyboard.row(
            InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
        )
        
        self.bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _handle_check_payment_status(self, message: Message):
        """Handler untuk cek status pembayaran via command"""
        text = message.text.replace("/cekstatus", "").strip()
        
        if not text:
            self.bot.send_message(
                message.chat.id,
                "📋 Masukkan Order ID untuk cek status:\n\nFormat: `/cekstatus ORDER_ID`\n\nContoh: `/cekstatus PRE2401231234ABC`",
                parse_mode="Markdown"
            )
            return
        
        self._check_order_status(message.chat.id, text)
    
    def _show_admin_panel(self, message: Message):
        """Tampilkan panel admin"""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Akses ditolak.")
            return
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Stats
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'paid'")
        paid_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
        pending_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status IN ('paid', 'delivered')")
        total_revenue = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
        active_products = cursor.fetchone()[0]
        
        conn.close()
        
        text = f"""
👑 *ADMIN PANEL*

━━━━━━━━━━━━━━━━━━━━━━

📊 *Statistik:*
👥 Total Users: {total_users}
📦 Produk Aktif: {active_products}
✅ Pesanan Selesai: {paid_orders}
⏳ Pesanan Pending: {pending_orders}
💰 Total Revenue: Rp {total_revenue:,}

━━━━━━━━━━━━━━━━━━━━━━

Pilih menu admin:
"""
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("📦 Kelola Produk", callback_data="admin_products"),
            InlineKeyboardButton("📋 Pesanan", callback_data="admin_orders")
        )
        keyboard.row(
            InlineKeyboardButton("🔑 License Keys", callback_data="admin_keys"),
            InlineKeyboardButton("👥 Users", callback_data="admin_users")
        )
        keyboard.row(
            InlineKeyboardButton("📊 Laporan", callback_data="admin_report"),
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
        )
        keyboard.row(
            InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
        )
        
        self.bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    def _notify_admin_new_order(self, order_id: str):
        """Kirim notifikasi ke admin untuk pesanan baru yang sudah dibayar"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if order:
            text = f"""
🔔 *PESANAN BARU DIBAYAR!*

━━━━━━━━━━━━━━━━━━━━━━

🆔 Order ID: `{order_id}`
👤 User: @{order['username'] or 'N/A'} ({order['user_id']})
📦 Produk: {order['product_name']}
💰 Jumlah: Rp {order['amount']:,}
📅 Waktu: {datetime.now().strftime('%d/%m/%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━
"""
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton("📋 Lihat Detail", callback_data=f"admin_order_{order_id}")
            )
            
            for admin_id in Config.ADMIN_IDS:
                try:
                    self.bot.send_message(
                        admin_id,
                        text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logging.error(f"Failed to notify admin {admin_id}: {e}")
    
    def _handle_callback_query(self, call: CallbackQuery):
        """Handler untuk callback query"""
        data = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = call.from_user.id
        username = call.from_user.username or ""
        
        try:
            self.bot.answer_callback_query(call.id)
            
            if data == "home":
                self._handle_start(call.message)
                self.bot.delete_message(chat_id, message_id)
                
            elif data == "catalog":
                self._show_catalog(chat_id, message_id=message_id)
                
            elif data == "menu":
                self._show_main_menu(call.message)
                self.bot.delete_message(chat_id, message_id)
                
            elif data.startswith("cat_"):
                category_map = {
                    "cat_streaming": "🎬 Streaming",
                    "cat_productivity": "💼 Produktivitas",
                    "cat_education": "📚 Edukasi",
                    "cat_gaming": "🎮 Gaming",
                    "cat_vpn": "🔐 VPN & Keamanan",
                    "cat_design": "🎨 Desain",
                }
                category = category_map.get(data)
                if category:
                    self._show_catalog(chat_id, category=category, message_id=message_id)
                    
            elif data.startswith("product_"):
                product_id = int(data.replace("product_", ""))
                self._show_product_detail(chat_id, product_id, message_id)
                
            elif data.startswith("buy_"):
                product_id = int(data.replace("buy_", ""))
                self._process_order(chat_id, user_id, username, product_id, message_id)
                
            elif data.startswith("check_"):
                order_id = data.replace("check_", "")
                self._check_order_status(chat_id, order_id, message_id)
                
            elif data.startswith("cancel_"):
                order_id = data.replace("cancel_", "")
                self._cancel_order(chat_id, order_id, message_id)
                
            elif data == "my_orders":
                self._show_user_orders(call.message)
                self.bot.delete_message(chat_id, message_id)
                
            elif data == "help":
                self._show_help(call.message)
                self.bot.delete_message(chat_id, message_id)
                
            elif data == "about":
                text = f"""
ℹ️ *TENTANG {Config.STORE_NAME.upper()}*

━━━━━━━━━━━━━━━━━━━━━━

{Config.STORE_DESCRIPTION}

Kami menyediakan berbagai aplikasi premium dengan harga terjangkau dan proses yang cepat.

✨ *Keunggulan Kami:*
• Harga Termurah
• Proses Otomatis 24/7
• Garansi Full Masa Aktif
• Customer Support Responsif
• Pembayaran Aman via QRIS

━━━━━━━━━━━━━━━━━━━━━━

🔒 Powered by Pakasir.com
Payment Gateway Terpercaya
"""
                keyboard = InlineKeyboardMarkup()
                keyboard.row(
                    InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
                )
                
                self.bot.edit_message_text(
                    text,
                    chat_id,
                    message_id,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logging.error(f"Callback error: {e}")
    
    def run(self):
        """Jalankan bot"""
        logging.info("🤖 Bot started!")
        self.bot.infinity_polling()


# ================================
# 🌐 WEBHOOK SERVER (Flask)
# ================================

app = Flask(__name__)
db = DatabaseManager(Config.DATABASE_PATH)


@app.route("/")
def index():
    """Homepage"""
    return jsonify({
        "status": "running",
        "service": Config.STORE_NAME,
        "version": "1.0.0"
    })


@app.route("/webhook/pakasir", methods=["POST"])
def webhook_pakasir():
    """
    Webhook endpoint untuk menerima notifikasi pembayaran dari Pakasir
    
    Payload example:
    {
        "amount": 22000,
        "order_id": "240910HDE7C9",
        "project": "depodomain",
        "status": "completed",
        "payment_method": "qris",
        "completed_at": "2024-09-10T08:07:02.819+07:00"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Invalid payload"}), 400
        
        order_id = data.get("order_id")
        amount = data.get("amount")
        status = data.get("status")
        project = data.get("project")
        payment_method = data.get("payment_method")
        completed_at = data.get("completed_at")
        
        logging.info(f"Webhook received: order_id={order_id}, status={status}, amount={amount}")
        
        # Validasi project
        if project != Config.PAKASIR_PROJECT_SLUG:
            logging.warning(f"Invalid project: {project}")
            return jsonify({"error": "Invalid project"}), 400
        
        if status == "completed":
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Cari order
            cursor.execute("SELECT * FROM orders WHERE id = ? AND amount = ?", (order_id, amount))
            order = cursor.fetchone()
            
            if order and order['status'] == 'pending':
                # Update order status
                cursor.execute("""
                    UPDATE orders SET status = 'paid', paid_at = ? WHERE id = ?
                """, (completed_at or datetime.now().isoformat(), order_id))
                
                # Kurangi stok
                cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (order['product_id'],))
                
                # Update user stats
                cursor.execute("""
                    UPDATE users SET total_orders = total_orders + 1, total_spent = total_spent + ?
                    WHERE id = ?
                """, (amount, order['user_id']))
                
                # Ambil license key
                cursor.execute("""
                    SELECT key_value FROM license_keys 
                    WHERE product_id = ? AND is_used = 0 
                    LIMIT 1
                """, (order['product_id'],))
                license_row = cursor.fetchone()
                
                license_key = None
                if license_row:
                    license_key = license_row['key_value']
                    cursor.execute("""
                        UPDATE license_keys SET is_used = 1, order_id = ? WHERE key_value = ?
                    """, (order_id, license_key))
                    cursor.execute("""
                        UPDATE orders SET license_key = ?, status = 'delivered', delivered_at = ? WHERE id = ?
                    """, (license_key, datetime.now().isoformat(), order_id))
                
                conn.commit()
                conn.close()
                
                # Kirim notifikasi ke user via Telegram
                try:
                    bot = TeleBot(Config.TELEGRAM_BOT_TOKEN)
                    
                    text = f"""
✅ *PEMBAYARAN BERHASIL!*

━━━━━━━━━━━━━━━━━━━━━━

🆔 *Order ID:* `{order_id}`
📦 *Produk:* {order['product_name']}
💰 *Jumlah:* Rp {amount:,}

━━━━━━━━━━━━━━━━━━━━━━

"""
                    if license_key:
                        text += f"""
🔐 *AKUN / LICENSE KEY:*
`{license_key}`

━━━━━━━━━━━━━━━━━━━━━━

📌 Simpan informasi ini dengan baik!
"""
                    else:
                        text += """
⏳ *Pesanan sedang diproses...*
Admin akan mengirim akun Anda segera.
"""
                    
                    keyboard = InlineKeyboardMarkup()
                    keyboard.row(
                        InlineKeyboardButton("📋 Pesanan Saya", callback_data="my_orders"),
                        InlineKeyboardButton("🏠 Menu Utama", callback_data="home")
                    )
                    
                    bot.send_message(
                        order['user_id'],
                        text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                    
                    # Notify admin
                    for admin_id in Config.ADMIN_IDS:
                        try:
                            admin_text = f"""
🔔 *PEMBAYARAN DITERIMA!*

🆔 Order: `{order_id}`
👤 User: {order['user_id']}
📦 {order['product_name']}
💰 Rp {amount:,}
"""
                            bot.send_message(admin_id, admin_text, parse_mode="Markdown")
                        except:
                            pass
                            
                except Exception as e:
                    logging.error(f"Failed to send notification: {e}")
                
                logging.info(f"Order {order_id} marked as paid")
            else:
                conn.close()
                logging.warning(f"Order not found or already processed: {order_id}")
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/products", methods=["GET"])
def get_products():
    """API untuk mendapatkan daftar produk"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY category, name")
    products = cursor.fetchall()
    conn.close()
    
    result = []
    for p in products:
        result.append({
            "id": p['id'],
            "name": p['name'],
            "description": p['description'],
            "price": p['price'],
            "category": p['category'],
            "duration": p['duration'],
            "stock": p['stock']
        })
    
    return jsonify({"products": result})


@app.route("/api/order/<order_id>", methods=["GET"])
def get_order_status(order_id: str):
    """API untuk cek status order"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify({
        "order_id": order['id'],
        "product_name": order['product_name'],
        "amount": order['amount'],
        "status": order['status'],
        "created_at": order['created_at'],
        "paid_at": order['paid_at']
    })


# ================================
# 🎬 MAIN
# ================================

def run_webhook_server():
    """Jalankan webhook server"""
    logging.info(f"🌐 Webhook server starting on port {Config.WEBHOOK_PORT}")
    app.run(host="0.0.0.0", port=Config.WEBHOOK_PORT, debug=False)


def run_telegram_bot():
    """Jalankan Telegram bot"""
    bot = PremiumStoreBot()
    bot.run()


if __name__ == "__main__":
    import sys
    import threading
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 PREMIUM APPS STORE - Telegram Bot + Webhook Server     ║
║                                                              ║
║   💳 Payment Gateway: Pakasir.com (QRIS)                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "bot":
            # Jalankan bot saja
            run_telegram_bot()
            
        elif mode == "webhook":
            # Jalankan webhook server saja
            run_webhook_server()
            
        elif mode == "both":
            # Jalankan keduanya (dalam thread terpisah)
            webhook_thread = threading.Thread(target=run_webhook_server)
            webhook_thread.daemon = True
            webhook_thread.start()
            
            run_telegram_bot()
    else:
        print("""
Usage:
    python premium_apps_store.py bot      # Run Telegram bot only
    python premium_apps_store.py webhook  # Run webhook server only  
    python premium_apps_store.py both     # Run both bot and webhook server

Environment Variables:
    TELEGRAM_BOT_TOKEN      - Token bot Telegram dari @BotFather
    PAKASIR_PROJECT_SLUG    - Slug proyek dari Pakasir.com
    PAKASIR_API_KEY         - API Key dari Pakasir.com
    ADMIN_IDS               - ID Telegram admin (pisahkan dengan koma)
    WEBHOOK_HOST            - URL webhook (untuk notifikasi pembayaran)
    WEBHOOK_PORT            - Port webhook server (default: 5000)
    DATABASE_PATH           - Path database SQLite (default: premium_store.db)
""")
