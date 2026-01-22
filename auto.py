"""
VIP Premium Bot dengan CryptoPay Integration
=============================================

PANDUAN SETUP CRYPTO PAY API:

1. Buka @CryptoBot di Telegram
2. Klik "Crypto Pay" -> "My Apps" -> Pilih app Anda
3. Klik "API Token" untuk mendapatkan token
4. Copy token dan paste di CRYPTOPAY_TOKEN di bawah

PENGATURAN SECURITY (Opsional):
- Checks: Aktifkan untuk validasi tambahan
- Transfers: Aktifkan jika ingin transfer antar akun
- IP Allowlist: Jika diaktifkan, masukkan IP VPS Anda
  * Untuk mengetahui IP VPS: curl ifconfig.me
  * Masukkan IP di pengaturan CryptoPay -> Security -> IP Allowlist

PENGATURAN WEBHOOKS (Opsional):
- Webhooks memungkinkan notifikasi otomatis saat pembayaran
- Untuk aktivasi, perlu endpoint HTTPS yang valid
- Bot ini sudah memiliki polling, jadi webhooks opsional

TROUBLESHOOTING:
- Error "Unauthorized": Token API tidak valid
- Error "Bad Request": Parameter tidak valid
- Error "IP not allowed": Tambahkan IP VPS ke allowlist
"""

import telebot
from telebot import types
import asyncio
import json
import os
import traceback
from datetime import datetime
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import Assets, PaidButtons, CurrencyType

# ==================== KONFIGURASI ====================
# Ganti dengan token bot Anda dari @BotFather
BOT_TOKEN = '7829954744:AAEJgjBWRTdaJmh7gsnLlE_cNo1TXl0i6EU'

# Ganti dengan API token CryptoPay dari @CryptoBot
# Format: APP_ID:TOKEN (contoh: 519883:AAJsQ1LRbcYeeGw0RivIRdACWjpZGW8VGfL)
CRYPTOPAY_TOKEN = '519883:AAJsQ1LRbcYeeGw0RivIRdACWjpZGW8VGfL'

# Link premium channel/group
PREMIUM_LINK = 'https://t.me/+V2JE9sIz35ZmZGNl'

# Admin user ID (untuk notifikasi)
# Gunakan /setadmin atau ganti manual dengan user ID Anda
# Cara mendapatkan user ID: kirim pesan ke @userinfobot
ADMIN_ID = 6683929810  # Ganti dengan user ID admin

# Harga Premium
ORIGINAL_PRICE = 300  # Harga asli dalam USD
DISCOUNT_PERCENT = 50  # Diskon 50%
FINAL_PRICE = ORIGINAL_PRICE * (100 - DISCOUNT_PERCENT) / 100  # $150

# File untuk menyimpan data user premium
PREMIUM_DB_FILE = 'premium_users.json'

# File untuk menyimpan pending invoices
PENDING_INVOICES_FILE = 'pending_invoices.json'

# Debug mode (True untuk melihat error detail)
DEBUG_MODE = True

# ==================== INISIALISASI ====================
bot = telebot.TeleBot(BOT_TOKEN)

# ==================== DATABASE FUNCTIONS ====================
def load_premium_users():
    """Load premium users dari file JSON"""
    if os.path.exists(PREMIUM_DB_FILE):
        try:
            with open(PREMIUM_DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_premium_users(data):
    """Simpan premium users ke file JSON"""
    with open(PREMIUM_DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_premium_user(user_id, username, invoice_id):
    """Tambah user ke database premium"""
    users = load_premium_users()
    users[str(user_id)] = {
        'username': username,
        'invoice_id': invoice_id,
        'activated_at': datetime.now().isoformat(),
        'duration': 'lifetime',
        'amount_paid': FINAL_PRICE
    }
    save_premium_users(users)

def is_premium_user(user_id):
    """Cek apakah user adalah premium member"""
    users = load_premium_users()
    return str(user_id) in users

def get_premium_user(user_id):
    """Get data premium user"""
    users = load_premium_users()
    return users.get(str(user_id))

# ==================== PENDING INVOICES FUNCTIONS ====================
def load_pending_invoices():
    """Load pending invoices dari file JSON"""
    if os.path.exists(PENDING_INVOICES_FILE):
        try:
            with open(PENDING_INVOICES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_pending_invoices(data):
    """Simpan pending invoices ke file JSON"""
    with open(PENDING_INVOICES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_pending_invoice(user_id, invoice_id, invoice_url):
    """Tambah pending invoice untuk user"""
    invoices = load_pending_invoices()
    invoices[str(user_id)] = {
        'invoice_id': invoice_id,
        'invoice_url': invoice_url,
        'created_at': datetime.now().isoformat()
    }
    save_pending_invoices(invoices)

def get_pending_invoice(user_id):
    """Get pending invoice untuk user"""
    invoices = load_pending_invoices()
    return invoices.get(str(user_id))

def remove_pending_invoice(user_id):
    """Hapus pending invoice setelah pembayaran sukses"""
    invoices = load_pending_invoices()
    if str(user_id) in invoices:
        del invoices[str(user_id)]
        save_pending_invoices(invoices)

# ==================== CRYPTOPAY FUNCTIONS ====================

# Cache untuk bot username (agar tidak perlu request berulang)
_bot_username_cache = None

def get_bot_username():
    """Get bot username dengan caching"""
    global _bot_username_cache
    if _bot_username_cache is None:
        try:
            _bot_username_cache = bot.get_me().username
        except Exception as e:
            print(f"Error getting bot username: {e}")
            _bot_username_cache = "unknown_bot"
    return _bot_username_cache

async def create_payment_invoice(user_id, username):
    """Buat invoice pembayaran CryptoPay"""
    crypto = None
    invoice = None
    
    try:
        crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=Networks.MAIN_NET)
        
        # Verifikasi koneksi API dulu
        try:
            app_info = await crypto.get_me()
            print(f"✅ Connected to CryptoPay App: {app_info.name}")
        except Exception as api_error:
            print(f"❌ CryptoPay API Error: {api_error}")
            raise Exception(f"Gagal terhubung ke CryptoPay API: {str(api_error)}")
        
        # Get bot username untuk callback URL
        bot_username = get_bot_username()
        
        # Buat invoice dengan fiat USD
        # Catatan: paid_btn_url akan diupdate setelah invoice dibuat dengan ID spesifik
        invoice = await crypto.create_invoice(
            amount=FINAL_PRICE,
            fiat='USD',
            currency_type=CurrencyType.FIAT,
            description=f'VIP Premium Lifetime Access - User: {username}',
            paid_btn_name=PaidButtons.CALLBACK,
            paid_btn_url=f'https://t.me/{bot_username}?start=check_payment',
            payload=f'{user_id}:{username}',
            allow_comments=True,
            allow_anonymous=False
        )
        
        # Update paid_btn_url dengan invoice ID untuk tracking yang lebih baik
        # (Ini hanya logging, URL sudah diset di atas)
        print(f"📝 Invoice URL akan redirect ke: https://t.me/{bot_username}?start=paid_{invoice.invoice_id}")
        
        print(f"✅ Invoice created: {invoice.invoice_id}")
        return invoice
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error creating invoice: {error_msg}")
        
        # Re-raise dengan pesan yang lebih jelas
        if "Unauthorized" in error_msg:
            raise Exception("Token API tidak valid. Periksa konfigurasi CRYPTOPAY_TOKEN.")
        elif "Bad Request" in error_msg:
            raise Exception(f"Request tidak valid: {error_msg}")
        elif "terhubung" in error_msg.lower() or "connect" in error_msg.lower():
            raise Exception("Tidak dapat terhubung ke server CryptoPay. Coba lagi nanti.")
        else:
            raise Exception(f"Error CryptoPay: {error_msg}")
    
    finally:
        if crypto:
            try:
                await crypto.close()
            except:
                pass

async def check_invoice_status(invoice_id):
    """Cek status pembayaran invoice"""
    crypto = None
    
    try:
        crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=Networks.MAIN_NET)
        invoices = await crypto.get_invoices(invoice_ids=[invoice_id])
        
        if invoices and len(invoices) > 0:
            return invoices[0]
        return None
        
    except Exception as e:
        print(f"❌ Error checking invoice {invoice_id}: {e}")
        raise Exception(f"Gagal mengecek invoice: {str(e)}")
    
    finally:
        if crypto:
            try:
                await crypto.close()
            except:
                pass

async def get_crypto_balance():
    """Cek saldo aplikasi CryptoPay"""
    crypto = None
    
    try:
        crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=Networks.MAIN_NET)
        balance = await crypto.get_balance()
        return balance
        
    except Exception as e:
        print(f"❌ Error getting balance: {e}")
        return None
    
    finally:
        if crypto:
            try:
                await crypto.close()
            except:
                pass

def run_async(coro):
    """Helper untuk menjalankan async function"""
    try:
        # Coba dapatkan existing event loop
        try:
            loop = asyncio.get_running_loop()
            # Jika loop sudah running, kita tidak bisa menggunakan run_until_complete
            # Buat loop baru
            loop = asyncio.new_event_loop()
        except RuntimeError:
            # Tidak ada running loop, coba get atau buat baru
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    except Exception as e:
        print(f"❌ Async error: {e}")
        if DEBUG_MODE:
            traceback.print_exc()
        raise

# ==================== BOT HANDLERS ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Cek jika ada parameter dari deep link
    args = message.text.split()
    if len(args) > 1:
        param = args[1]
        # Handle paid_ prefix (dari callback setelah bayar)
        if param.startswith('paid_'):
            invoice_id = param.replace('paid_', '')
            check_payment(message, invoice_id)
            return
        # Handle check_payment (dari tombol setelah bayar di CryptoPay)
        elif param == 'check_payment':
            # Cek apakah user punya pending invoice
            pending = get_pending_invoice(user_id)
            if pending:
                check_payment(message, pending['invoice_id'])
                return
            # Jika tidak ada pending, lanjut ke welcome message
    
    # Cek apakah sudah premium
    if is_premium_user(user_id):
        premium_data = get_premium_user(user_id)
        welcome_text = f"""
🎉 *Selamat Datang Kembali, VIP Member!* 🎉

👤 User: @{username}
🌟 Status: *PREMIUM LIFETIME*
📅 Aktif sejak: {premium_data['activated_at'][:10]}

Klik tombol di bawah untuk akses konten premium! 👇
        """
        
        markup = types.InlineKeyboardMarkup()
        premium_btn = types.InlineKeyboardButton("🔓 Akses Premium", url=PREMIUM_LINK)
        markup.add(premium_btn)
        
        bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    welcome_text = f"""
🎬 *Selamat Datang di VIP Premium Bot!* 🎬

Bergabunglah dengan kami untuk mengakses koleksi lebih dari *10.000 video premium* berkualitas tinggi!

✨ *Keuntungan Premium:*
• Akses eksklusif ke konten terbaik
• Update konten setiap hari
• Privasi terjamin 100%
• Durasi: *SEUMUR HIDUP* 🔥

💰 *Harga Spesial:*
┌─────────────────────┐
│ Harga Normal: ~${ORIGINAL_PRICE}~        │
│ 🔥 DISKON {DISCOUNT_PERCENT}%! 🔥          │
│ Harga Sekarang: *${int(FINAL_PRICE)}*  │
│ Durasi: *LIFETIME*       │
└─────────────────────┘

Bayar dengan Crypto untuk akses instant! 🚀
    """
    
    markup = types.InlineKeyboardMarkup()
    buy_btn = types.InlineKeyboardButton("💎 Beli Premium - $150", callback_data='buy_premium')
    check_btn = types.InlineKeyboardButton("🔍 Cek Pembayaran", callback_data='check_payment')
    markup.add(buy_btn)
    markup.add(check_btn)
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['premium'])
def premium_info(message):
    """Info tentang premium membership"""
    info_text = f"""
💎 *PREMIUM MEMBERSHIP INFO* 💎

🌟 *Apa yang kamu dapatkan:*
• Akses ke 10.000+ video premium
• Update konten harian
• Kualitas HD/4K
• Download unlimited
• Support prioritas 24/7
• Tanpa iklan

💰 *Harga:*
• Harga Asli: ${ORIGINAL_PRICE}
• Diskon: {DISCOUNT_PERCENT}%
• *Harga Final: ${int(FINAL_PRICE)}*

⏰ *Durasi:*
🔥 *SEUMUR HIDUP* - Bayar sekali, akses selamanya!

💳 *Metode Pembayaran:*
Cryptocurrency via CryptoPay:
• USDT (TRC20/BEP20)
• TON
• BTC
• ETH
• Dan lainnya...

Klik /start untuk mulai pembelian!
    """
    
    bot.send_message(message.chat.id, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def check_status(message):
    """Cek status membership"""
    user_id = message.from_user.id
    
    if is_premium_user(user_id):
        premium_data = get_premium_user(user_id)
        status_text = f"""
✅ *STATUS MEMBERSHIP*

👤 User ID: `{user_id}`
🌟 Status: *PREMIUM ACTIVE*
⏰ Durasi: *LIFETIME*
📅 Aktif Sejak: {premium_data['activated_at'][:10]}
💰 Jumlah Bayar: ${premium_data['amount_paid']}

Nikmati akses premium kamu! 🎉
        """
        
        markup = types.InlineKeyboardMarkup()
        premium_btn = types.InlineKeyboardButton("🔓 Akses Premium", url=PREMIUM_LINK)
        markup.add(premium_btn)
        
    else:
        status_text = f"""
❌ *STATUS MEMBERSHIP*

👤 User ID: `{user_id}`
🌟 Status: *FREE USER*

Upgrade ke Premium untuk menikmati:
• 10.000+ video premium
• Akses seumur hidup
• Hanya ${int(FINAL_PRICE)} (Diskon {DISCOUNT_PERCENT}%!)

Klik tombol di bawah untuk upgrade! 👇
        """
        
        markup = types.InlineKeyboardMarkup()
        buy_btn = types.InlineKeyboardButton("💎 Upgrade Premium", callback_data='buy_premium')
        markup.add(buy_btn)
    
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'buy_premium')
def handle_buy_premium(call):
    """Handle tombol beli premium"""
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name
    
    # Cek apakah sudah premium
    if is_premium_user(user_id):
        bot.answer_callback_query(call.id, "Kamu sudah menjadi premium member! ✅", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "Membuat invoice pembayaran... 💳")
    
    # Kirim pesan loading
    try:
        bot.edit_message_text(
            "⏳ *Membuat invoice pembayaran...*\n\nMohon tunggu sebentar.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    except:
        pass
    
    # Buat invoice
    invoice = None
    error_message = None
    
    try:
        invoice = run_async(create_payment_invoice(user_id, username))
    except Exception as e:
        error_message = str(e)
        print(f"❌ Invoice creation failed: {error_message}")
    
    if invoice is not None:
        try:
            # Simpan pending invoice untuk tracking
            add_pending_invoice(user_id, invoice.invoice_id, invoice.bot_invoice_url)
            
            payment_text = f"""
💳 *INVOICE PEMBAYARAN*

📋 *Detail Pesanan:*
┌─────────────────────┐
│ Produk: VIP Premium    │
│ Durasi: LIFETIME       │
│ Harga Asli: ${ORIGINAL_PRICE}        │
│ Diskon: {DISCOUNT_PERCENT}%             │
│ *Total: ${int(FINAL_PRICE)}*          │
└─────────────────────┘

🔢 Invoice ID: `{invoice.invoice_id}`

💡 *Cara Bayar:*
1. Klik tombol "💰 Bayar Sekarang"
2. Pilih cryptocurrency
3. Selesaikan pembayaran
4. Klik "✅ Sudah Bayar" untuk verifikasi

⚠️ *Penting:*
• Pembayaran akan diverifikasi otomatis
• Link premium dikirim setelah pembayaran sukses
• Invoice berlaku 60 menit

Terima kasih! 🙏
            """
            
            markup = types.InlineKeyboardMarkup()
            pay_btn = types.InlineKeyboardButton("💰 Bayar Sekarang", url=invoice.bot_invoice_url)
            check_btn = types.InlineKeyboardButton("✅ Sudah Bayar", callback_data=f'verify_{invoice.invoice_id}')
            cancel_btn = types.InlineKeyboardButton("❌ Batal", callback_data='cancel_payment')
            markup.add(pay_btn)
            markup.add(check_btn)
            markup.add(cancel_btn)
            
            bot.edit_message_text(
                payment_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            print(f"❌ Error sending payment message: {e}")
            bot.edit_message_text(
                "❌ Gagal menampilkan invoice. Silakan coba lagi.",
                call.message.chat.id,
                call.message.message_id
            )
    else:
        # Invoice gagal dibuat
        error_display = error_message[:150] if error_message else "Unknown error"
        
        error_text = f"""
❌ *Terjadi Kesalahan*

Tidak dapat membuat invoice saat ini.

🔍 *Detail Error:*
`{error_display}`

💡 *Solusi:*
• Coba lagi beberapa saat
• Pastikan koneksi internet stabil
• Hubungi admin jika masalah berlanjut

Klik tombol di bawah untuk mencoba lagi.
        """
        
        markup = types.InlineKeyboardMarkup()
        retry_btn = types.InlineKeyboardButton("🔄 Coba Lagi", callback_data='buy_premium')
        back_btn = types.InlineKeyboardButton("🔙 Kembali", callback_data='back_to_menu')
        markup.add(retry_btn)
        markup.add(back_btn)
        
        bot.edit_message_text(
            error_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def handle_verify_payment(call):
    """Verifikasi pembayaran"""
    invoice_id = call.data.replace('verify_', '')
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name
    
    bot.answer_callback_query(call.id, "Memeriksa pembayaran... 🔍")
    
    invoice = None
    error_message = None
    
    try:
        invoice = run_async(check_invoice_status(int(invoice_id)))
    except Exception as e:
        error_message = str(e)
        print(f"❌ Error checking invoice: {error_message}")
        if DEBUG_MODE:
            traceback.print_exc()
    
    if invoice is not None:
        try:
            if invoice.status == 'paid':
                # Pembayaran sukses!
                add_premium_user(user_id, username, invoice_id)
                remove_pending_invoice(user_id)  # Hapus dari pending
                
                success_text = f"""
🎉 *PEMBAYARAN BERHASIL!* 🎉

✅ Status: *PAID*
💰 Jumlah: ${int(FINAL_PRICE)}
🔢 Invoice: `{invoice_id}`

🌟 *Selamat! Kamu sekarang VIP Premium Member!*
Durasi: *SEUMUR HIDUP* 🔥

Klik tombol di bawah untuk akses konten premium! 👇
                """
                
                markup = types.InlineKeyboardMarkup()
                premium_btn = types.InlineKeyboardButton("🔓 Akses Premium Sekarang!", url=PREMIUM_LINK)
                markup.add(premium_btn)
                
                bot.edit_message_text(
                    success_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
                
                # Notifikasi ke admin
                try:
                    admin_text = f"""
🔔 *PEMBAYARAN BARU!*

👤 User: @{username}
🆔 User ID: `{user_id}`
💰 Jumlah: ${int(FINAL_PRICE)}
📦 Produk: VIP Premium Lifetime
🔢 Invoice: `{invoice_id}`
⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    if ADMIN_ID != 123456789:
                        bot.send_message(ADMIN_ID, admin_text, parse_mode='Markdown')
                except Exception as e:
                    print(f"Failed to notify admin: {e}")
                    
            elif invoice.status == 'active':
                pending_text = f"""
⏳ *MENUNGGU PEMBAYARAN*

🔢 Invoice ID: `{invoice_id}`
💰 Jumlah: ${int(FINAL_PRICE)}
📊 Status: *Belum Dibayar*

Silakan selesaikan pembayaran terlebih dahulu, 
kemudian klik "✅ Sudah Bayar" lagi.
                """
                
                markup = types.InlineKeyboardMarkup()
                pay_btn = types.InlineKeyboardButton("💰 Bayar Sekarang", url=invoice.bot_invoice_url)
                check_btn = types.InlineKeyboardButton("✅ Sudah Bayar", callback_data=f'verify_{invoice_id}')
                markup.add(pay_btn)
                markup.add(check_btn)
                
                bot.edit_message_text(
                    pending_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
                
            elif invoice.status == 'expired':
                expired_text = f"""
❌ *INVOICE EXPIRED*

🔢 Invoice ID: `{invoice_id}`
📊 Status: *Kadaluarsa*

Invoice sudah tidak berlaku.
Silakan buat invoice baru.
                """
                
                markup = types.InlineKeyboardMarkup()
                new_btn = types.InlineKeyboardButton("🔄 Buat Invoice Baru", callback_data='buy_premium')
                markup.add(new_btn)
                
                bot.edit_message_text(
                    expired_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            else:
                # Status lain (cancelled, dll)
                other_text = f"""
⚠️ *STATUS INVOICE*

🔢 Invoice ID: `{invoice_id}`
📊 Status: *{invoice.status.upper()}*

Silakan buat invoice baru jika diperlukan.
                """
                
                markup = types.InlineKeyboardMarkup()
                new_btn = types.InlineKeyboardButton("🔄 Buat Invoice Baru", callback_data='buy_premium')
                markup.add(new_btn)
                
                bot.edit_message_text(
                    other_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
                
        except Exception as e:
            print(f"❌ Error processing invoice status: {e}")
            bot.answer_callback_query(call.id, "❌ Gagal memproses. Coba lagi.", show_alert=True)
    else:
        # Invoice tidak ditemukan atau error
        error_display = error_message[:100] if error_message else "Invoice tidak ditemukan"
        
        error_text = f"""
❌ *GAGAL MENGECEK INVOICE*

🔢 Invoice ID: `{invoice_id}`

🔍 *Detail:*
`{error_display}`

💡 Silakan coba lagi atau buat invoice baru.
        """
        
        markup = types.InlineKeyboardMarkup()
        retry_btn = types.InlineKeyboardButton("🔄 Coba Lagi", callback_data=f'verify_{invoice_id}')
        new_btn = types.InlineKeyboardButton("📝 Invoice Baru", callback_data='buy_premium')
        markup.add(retry_btn)
        markup.add(new_btn)
        
        try:
            bot.edit_message_text(
                error_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except:
            bot.answer_callback_query(call.id, f"❌ Error: {error_display[:50]}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'check_payment')
def handle_check_payment(call):
    """Handle cek pembayaran dari menu utama"""
    check_text = """
🔍 *CEK PEMBAYARAN*

Untuk mengecek status pembayaran, 
kirim Invoice ID kamu:

Contoh: `/cek 12345`

Atau klik tombol "💎 Beli Premium" 
untuk membuat pembayaran baru.
    """
    
    markup = types.InlineKeyboardMarkup()
    buy_btn = types.InlineKeyboardButton("💎 Beli Premium", callback_data='buy_premium')
    back_btn = types.InlineKeyboardButton("🔙 Kembali", callback_data='back_to_menu')
    markup.add(buy_btn)
    markup.add(back_btn)
    
    bot.edit_message_text(
        check_text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def handle_back_to_menu(call):
    """Kembali ke menu utama"""
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name
    
    if is_premium_user(user_id):
        premium_data = get_premium_user(user_id)
        welcome_text = f"""
🎉 *Selamat Datang Kembali, VIP Member!* 🎉

👤 User: @{username}
🌟 Status: *PREMIUM LIFETIME*
📅 Aktif sejak: {premium_data['activated_at'][:10]}

Klik tombol di bawah untuk akses konten premium! 👇
        """
        
        markup = types.InlineKeyboardMarkup()
        premium_btn = types.InlineKeyboardButton("🔓 Akses Premium", url=PREMIUM_LINK)
        markup.add(premium_btn)
    else:
        welcome_text = f"""
🎬 *Selamat Datang di VIP Premium Bot!* 🎬

Bergabunglah dengan kami untuk mengakses koleksi lebih dari *10.000 video premium* berkualitas tinggi!

💰 *Harga Spesial:*
┌─────────────────────┐
│ Harga Normal: ~${ORIGINAL_PRICE}~        │
│ 🔥 DISKON {DISCOUNT_PERCENT}%! 🔥          │
│ Harga Sekarang: *${int(FINAL_PRICE)}*  │
│ Durasi: *LIFETIME*       │
└─────────────────────┘
        """
        
        markup = types.InlineKeyboardMarkup()
        buy_btn = types.InlineKeyboardButton("💎 Beli Premium - $150", callback_data='buy_premium')
        check_btn = types.InlineKeyboardButton("🔍 Cek Pembayaran", callback_data='check_payment')
        markup.add(buy_btn)
        markup.add(check_btn)
    
    bot.edit_message_text(
        welcome_text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_payment')
def handle_cancel_payment(call):
    """Handle pembatalan pembayaran"""
    cancel_text = """
❌ *Pembayaran Dibatalkan*

Kamu telah membatalkan proses pembayaran.
Kamu dapat memulai kembali kapan saja dengan klik /start

Terima kasih! 🙏
    """
    
    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 Kembali ke Menu", callback_data='back_to_menu')
    markup.add(back_btn)
    
    bot.edit_message_text(
        cancel_text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['cek'])
def check_invoice_cmd(message):
    """Cek invoice berdasarkan ID"""
    args = message.text.split()
    
    if len(args) < 2:
        bot.reply_to(message, "❌ Format salah!\n\nGunakan: `/cek <invoice_id>`\nContoh: `/cek 12345`", parse_mode='Markdown')
        return
    
    invoice_id = args[1]
    
    try:
        invoice = run_async(check_invoice_status(int(invoice_id)))
        
        if invoice:
            status_emoji = {
                'active': '⏳',
                'paid': '✅',
                'expired': '❌'
            }.get(invoice.status, '❓')
            
            check_text = f"""
🔍 *DETAIL INVOICE*

🔢 Invoice ID: `{invoice_id}`
{status_emoji} Status: *{invoice.status.upper()}*
💰 Jumlah: ${int(FINAL_PRICE)}
            """
            
            if invoice.status == 'active':
                markup = types.InlineKeyboardMarkup()
                pay_btn = types.InlineKeyboardButton("💰 Bayar Sekarang", url=invoice.bot_invoice_url)
                verify_btn = types.InlineKeyboardButton("✅ Sudah Bayar", callback_data=f'verify_{invoice_id}')
                markup.add(pay_btn)
                markup.add(verify_btn)
                bot.send_message(message.chat.id, check_text, parse_mode='Markdown', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, check_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Invoice tidak ditemukan!")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

def check_payment(message, invoice_id):
    """Cek pembayaran dari deep link"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    try:
        invoice = run_async(check_invoice_status(int(invoice_id)))
        
        if invoice and invoice.status == 'paid':
            if not is_premium_user(user_id):
                add_premium_user(user_id, username, invoice_id)
            remove_pending_invoice(user_id)  # Hapus dari pending
            
            success_text = f"""
🎉 *PEMBAYARAN BERHASIL!* 🎉

✅ Status: *PAID*
🔢 Invoice: `{invoice_id}`

🌟 *Selamat! Kamu sekarang VIP Premium Member!*
Durasi: *SEUMUR HIDUP* 🔥

Klik tombol di bawah untuk akses! 👇
            """
            
            markup = types.InlineKeyboardMarkup()
            premium_btn = types.InlineKeyboardButton("🔓 Akses Premium Sekarang!", url=PREMIUM_LINK)
            markup.add(premium_btn)
            
            bot.send_message(message.chat.id, success_text, parse_mode='Markdown', reply_markup=markup)
        elif invoice and invoice.status == 'active':
            # Invoice masih aktif, belum dibayar
            pending_text = f"""
⏳ *MENUNGGU PEMBAYARAN*

🔢 Invoice ID: `{invoice_id}`
💰 Jumlah: ${int(FINAL_PRICE)}
📊 Status: *Belum Dibayar*

Silakan selesaikan pembayaran terlebih dahulu.
            """
            
            markup = types.InlineKeyboardMarkup()
            pay_btn = types.InlineKeyboardButton("💰 Bayar Sekarang", url=invoice.bot_invoice_url)
            verify_btn = types.InlineKeyboardButton("✅ Sudah Bayar", callback_data=f'verify_{invoice_id}')
            markup.add(pay_btn)
            markup.add(verify_btn)
            
            bot.send_message(message.chat.id, pending_text, parse_mode='Markdown', reply_markup=markup)
        else:
            # Invoice expired atau tidak ditemukan
            send_welcome(message)
            
    except Exception as e:
        print(f"❌ Error in check_payment: {e}")
        if DEBUG_MODE:
            traceback.print_exc()
        send_welcome(message)

@bot.message_handler(commands=['help'])
def send_help(message):
    """Tampilkan bantuan"""
    help_text = """
📚 *BANTUAN*

*Perintah Tersedia:*
/start - Mulai bot & menu utama
/premium - Info tentang premium
/status - Cek status membership
/cek <id> - Cek status invoice
/help - Tampilkan bantuan ini

*Cara Membeli Premium:*
1. Klik /start
2. Pilih "💎 Beli Premium"
3. Klik "💰 Bayar Sekarang"
4. Pilih crypto & bayar
5. Klik "✅ Sudah Bayar"
6. Nikmati akses premium!

*Metode Pembayaran:*
• USDT, TON, BTC, ETH, dll
• Via CryptoPay (@CryptoBot)

*Support:*
Hubungi admin jika ada masalah.
    """
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# ==================== ADMIN COMMANDS ====================
@bot.message_handler(commands=['testapi'])
def test_cryptopay_api(message):
    """Test koneksi ke CryptoPay API (Admin only)"""
    user_id = message.from_user.id
    
    # Cek apakah admin
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Perintah ini hanya untuk admin.")
        return
    
    bot.reply_to(message, "🔄 Testing CryptoPay API connection...")
    
    async def test_api():
        crypto = None
        results = []
        
        try:
            crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=Networks.MAIN_NET)
            
            # Test 1: Get app info
            try:
                app_info = await crypto.get_me()
                results.append(f"✅ App Name: {app_info.name}")
                results.append(f"✅ App ID: {app_info.app_id}")
            except Exception as e:
                results.append(f"❌ Get App Info Error: {str(e)[:100]}")
            
            # Test 2: Get balance
            try:
                balances = await crypto.get_balance()
                if balances:
                    results.append("✅ Balances:")
                    for bal in balances:
                        results.append(f"   • {bal.currency_code}: {bal.available}")
                else:
                    results.append("⚠️ No balance data")
            except Exception as e:
                results.append(f"❌ Get Balance Error: {str(e)[:100]}")
            
            # Test 3: Get exchange rates
            try:
                rates = await crypto.get_exchange_rates()
                if rates:
                    results.append(f"✅ Exchange Rates Available: {len(rates)} pairs")
                else:
                    results.append("⚠️ No exchange rates data")
            except Exception as e:
                results.append(f"❌ Get Rates Error: {str(e)[:100]}")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ Connection Error: {str(e)}"
        
        finally:
            if crypto:
                try:
                    await crypto.close()
                except:
                    pass
    
    try:
        result = run_async(test_api())
        
        test_text = f"""
🔧 *CRYPTOPAY API TEST RESULTS*

{result}

📋 *Configuration:*
• Token: `{CRYPTOPAY_TOKEN[:10]}...{CRYPTOPAY_TOKEN[-5:]}`
• Network: MAIN_NET
• Price: ${int(FINAL_PRICE)}
        """
        
        bot.send_message(message.chat.id, test_text, parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Test failed: {str(e)}")

@bot.message_handler(commands=['stats'])
def admin_stats(message):
    """Statistik bot (Admin only)"""
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Perintah ini hanya untuk admin.")
        return
    
    users = load_premium_users()
    total_users = len(users)
    total_revenue = sum(u.get('amount_paid', 0) for u in users.values())
    
    stats_text = f"""
📊 *STATISTIK BOT*

👥 Total Premium Users: {total_users}
💰 Total Revenue: ${total_revenue}
💵 Harga Saat Ini: ${int(FINAL_PRICE)}
🔖 Diskon: {DISCOUNT_PERCENT}%

🤖 Bot Status: Online
    """
    
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['setadmin'])
def set_admin_id(message):
    """Set admin ID (hanya sekali untuk setup awal)"""
    global ADMIN_ID
    current_id = message.from_user.id
    
    # Jika ADMIN_ID masih default (123456789), izinkan siapa saja untuk set
    if ADMIN_ID == 123456789:
        ADMIN_ID = current_id
        bot.reply_to(
            message, 
            f"✅ Admin ID berhasil diset!\n\n"
            f"User ID: `{current_id}`\n\n"
            f"⚠️ PENTING: Update file auto.py, ganti:\n"
            f"`ADMIN_ID = 123456789`\n"
            f"dengan:\n"
            f"`ADMIN_ID = {current_id}`",
            parse_mode='Markdown'
        )
    elif current_id == ADMIN_ID:
        bot.reply_to(message, f"✅ Kamu sudah menjadi admin.\n\nUser ID: `{current_id}`", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Tidak diizinkan.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Handler untuk pesan lainnya"""
    bot.reply_to(
        message, 
        "Gunakan perintah /start untuk memulai!\n\n"
        "📋 *Perintah:*\n"
        "/start - Menu utama\n"
        "/premium - Info premium\n"
        "/status - Cek status\n"
        "/help - Bantuan",
        parse_mode='Markdown'
    )

# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 50)
    print("🤖 VIP Premium Bot dengan CryptoPay")
    print("=" * 50)
    print(f"💰 Harga Asli: ${ORIGINAL_PRICE}")
    print(f"🔥 Diskon: {DISCOUNT_PERCENT}%")
    print(f"✅ Harga Final: ${int(FINAL_PRICE)}")
    print(f"⏰ Durasi: LIFETIME")
    print("=" * 50)
    print("Bot berjalan...")
    print("=" * 50)
    bot.infinity_polling()
