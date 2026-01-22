"""
VIP Premium Bot - Clean & Private Edition
==========================================

Fitur:
- Privasi terjamin (admin info tersembunyi)
- Respon singkat & rapi
- Support Testnet untuk testing
- UI/UX yang lebih baik

SETUP:
1. Dapatkan BOT_TOKEN dari @BotFather
2. Dapatkan CRYPTOPAY_TOKEN dari @CryptoBot -> Crypto Pay -> My Apps
3. Set USE_TESTNET = True untuk testing (gunakan @CryptoTestnetBot)
4. Set USE_TESTNET = False untuk production
"""

import telebot
from telebot import types
import asyncio
import json
import os
from datetime import datetime
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import PaidButtons, CurrencyType

# ══════════════════════════════════════════════════════════════
# KONFIGURASI UTAMA
# ══════════════════════════════════════════════════════════════

# Bot Token dari @BotFather
BOT_TOKEN = '7829954744:AAEJgjBWRTdaJmh7gsnLlE_cNo1TXl0i6EU'

# CryptoPay Token
# TESTNET: Dari @CryptoTestnetBot -> Crypto Pay -> My Apps
# MAINNET: Dari @CryptoBot -> Crypto Pay -> My Apps
CRYPTOPAY_TOKEN = '519883:AAJsQ1LRbcYeeGw0RivIRdACWjpZGW8VGfL'

# ⚠️ TESTNET MODE - Set True untuk testing, False untuk production
USE_TESTNET = False

# Link Premium Channel (private invite link)
PREMIUM_LINK = 'https://t.me/+V2JE9sIz35ZmZGNl'

# Admin ID (untuk notifikasi internal saja, tidak ditampilkan ke user)
ADMIN_ID = 6683929810

# Pricing
ORIGINAL_PRICE = 300
DISCOUNT_PERCENT = 50
FINAL_PRICE = ORIGINAL_PRICE * (100 - DISCOUNT_PERCENT) / 100

# Database Files
PREMIUM_DB = 'premium_users.json'
INVOICES_DB = 'pending_invoices.json'

# ══════════════════════════════════════════════════════════════
# INISIALISASI
# ══════════════════════════════════════════════════════════════

bot = telebot.TeleBot(BOT_TOKEN)
NETWORK = Networks.TEST_NET if USE_TESTNET else Networks.MAIN_NET

# ══════════════════════════════════════════════════════════════
# DATABASE HELPERS
# ══════════════════════════════════════════════════════════════

def load_json(file):
    """Load data dari JSON file"""
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(file, data):
    """Simpan data ke JSON file"""
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Premium Users
def is_premium(user_id):
    return str(user_id) in load_json(PREMIUM_DB)

def get_premium_data(user_id):
    return load_json(PREMIUM_DB).get(str(user_id))

def add_premium(user_id, invoice_id):
    data = load_json(PREMIUM_DB)
    data[str(user_id)] = {
        'invoice_id': invoice_id,
        'activated': datetime.now().isoformat(),
        'amount': FINAL_PRICE
    }
    save_json(PREMIUM_DB, data)

# Pending Invoices
def get_invoice(user_id):
    return load_json(INVOICES_DB).get(str(user_id))

def save_invoice(user_id, invoice_id, url):
    data = load_json(INVOICES_DB)
    data[str(user_id)] = {
        'id': invoice_id,
        'url': url,
        'created': datetime.now().isoformat()
    }
    save_json(INVOICES_DB, data)

def remove_invoice(user_id):
    data = load_json(INVOICES_DB)
    if str(user_id) in data:
        del data[str(user_id)]
        save_json(INVOICES_DB, data)

# ══════════════════════════════════════════════════════════════
# CRYPTOPAY FUNCTIONS
# ══════════════════════════════════════════════════════════════

async def create_invoice(user_id):
    """Buat invoice pembayaran"""
    crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=NETWORK)
    
    try:
        bot_info = bot.get_me().username
        invoice = await crypto.create_invoice(
            amount=FINAL_PRICE,
            fiat='USD',
            currency_type=CurrencyType.FIAT,
            description='VIP Premium Lifetime',
            paid_btn_name=PaidButtons.CALLBACK,
            paid_btn_url=f'https://t.me/{bot_info}?start=paid',
            payload=str(user_id),
            allow_comments=False,
            allow_anonymous=True  # Privasi user
        )
        return invoice
    finally:
        await crypto.close()

async def check_invoice(invoice_id):
    """Cek status invoice"""
    crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=NETWORK)
    
    try:
        invoices = await crypto.get_invoices(invoice_ids=[invoice_id])
        return invoices[0] if invoices else None
    finally:
        await crypto.close()

async def get_app_info():
    """Get CryptoPay app info"""
    crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=NETWORK)
    
    try:
        return await crypto.get_me()
    finally:
        await crypto.close()

def run_async(coro):
    """Helper async runner"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        raise e

# ══════════════════════════════════════════════════════════════
# MESSAGE TEMPLATES (Singkat & Rapi)
# ══════════════════════════════════════════════════════════════

def msg_welcome():
    """Pesan welcome untuk user baru"""
    mode = "🧪 TESTNET" if USE_TESTNET else "🔐 SECURE"
    return f"""
🎬 *VIP Premium Bot* {mode}

Akses *10.000+ video premium* berkualitas tinggi!

✨ *Keuntungan:*
• Akses eksklusif seumur hidup
• Update harian & privasi 100%

💰 *Harga:* ~~${ORIGINAL_PRICE}~~ → *${int(FINAL_PRICE)}* (-{DISCOUNT_PERCENT}%)
"""

def msg_welcome_premium():
    """Pesan untuk member premium"""
    return """
🎉 *Welcome Back, VIP!*

Status: ✅ *PREMIUM LIFETIME*

Klik tombol untuk akses konten 👇
"""

def msg_invoice(invoice_id):
    """Pesan invoice pembayaran"""
    mode = "🧪 Mode: TESTNET" if USE_TESTNET else ""
    return f"""
💳 *Invoice Pembayaran*

📦 VIP Premium Lifetime
💵 Total: *${int(FINAL_PRICE)}*
🔢 ID: `{invoice_id}`
{mode}

*Cara Bayar:*
1️⃣ Klik "Bayar Sekarang"
2️⃣ Pilih crypto & bayar
3️⃣ Klik "Verifikasi" setelah bayar

⏰ Berlaku 60 menit
"""

def msg_success(invoice_id):
    """Pesan pembayaran sukses"""
    return f"""
✅ *Pembayaran Berhasil!*

🎉 Selamat! Kamu sekarang *VIP Member*
⏰ Durasi: *LIFETIME*

Klik tombol untuk akses premium 👇
"""

def msg_pending(invoice_id):
    """Pesan menunggu pembayaran"""
    return f"""
⏳ *Menunggu Pembayaran*

🔢 Invoice: `{invoice_id}`
📊 Status: Belum dibayar

Selesaikan pembayaran terlebih dahulu.
"""

def msg_expired():
    """Pesan invoice expired"""
    return """
⌛ *Invoice Kadaluarsa*

Buat invoice baru untuk melanjutkan.
"""

def msg_error():
    """Pesan error"""
    return """
❌ *Terjadi Kesalahan*

Coba lagi atau hubungi support.
"""

def msg_cancelled():
    """Pesan dibatalkan"""
    return """
🚫 *Dibatalkan*

Ketik /start untuk memulai kembali.
"""

def msg_status_free():
    """Status user free"""
    return f"""
📊 *Status Keanggotaan*

🔓 Status: *FREE*

Upgrade ke Premium:
• 10.000+ video
• Akses lifetime
• Hanya *${int(FINAL_PRICE)}*
"""

def msg_status_premium(data):
    """Status user premium"""
    date = data['activated'][:10]
    return f"""
📊 *Status Keanggotaan*

✅ Status: *PREMIUM*
📅 Sejak: {date}
⏰ Durasi: *LIFETIME*
"""

def msg_help():
    """Pesan bantuan"""
    return """
📚 *Bantuan*

/start - Menu utama
/status - Cek keanggotaan
/help - Bantuan

*Cara Beli:*
1. Klik "Beli Premium"
2. Bayar dengan crypto
3. Verifikasi pembayaran
4. Akses premium!

*Pembayaran:*
USDT • TON • BTC • ETH • dll
"""

# ══════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════

def kb_main():
    """Keyboard menu utama"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💎 Beli Premium", callback_data='buy'),
        types.InlineKeyboardButton("📊 Status", callback_data='status'),
        types.InlineKeyboardButton("❓ Bantuan", callback_data='help')
    )
    return kb

def kb_premium():
    """Keyboard untuk premium user"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🔓 Akses Premium", url=PREMIUM_LINK),
        types.InlineKeyboardButton("📊 Status", callback_data='status')
    )
    return kb

def kb_invoice(invoice_url, invoice_id):
    """Keyboard invoice"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💰 Bayar Sekarang", url=invoice_url),
        types.InlineKeyboardButton("✅ Verifikasi", callback_data=f'verify_{invoice_id}'),
        types.InlineKeyboardButton("❌ Batal", callback_data='cancel')
    )
    return kb

def kb_pending(invoice_url, invoice_id):
    """Keyboard pending payment"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💰 Bayar", url=invoice_url),
        types.InlineKeyboardButton("🔄 Cek Ulang", callback_data=f'verify_{invoice_id}')
    )
    return kb

def kb_success():
    """Keyboard sukses"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔓 Akses Premium", url=PREMIUM_LINK))
    return kb

def kb_retry():
    """Keyboard retry"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔄 Coba Lagi", callback_data='buy'),
        types.InlineKeyboardButton("🏠 Menu", callback_data='menu')
    )
    return kb

def kb_back():
    """Keyboard back"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data='menu'))
    return kb

def kb_status_free():
    """Keyboard status free"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💎 Upgrade Premium", callback_data='buy'),
        types.InlineKeyboardButton("🏠 Menu", callback_data='menu')
    )
    return kb

# ══════════════════════════════════════════════════════════════
# BOT HANDLERS
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def cmd_start(message):
    """Handle /start command"""
    user_id = message.from_user.id
    args = message.text.split()
    
    # Deep link handler
    if len(args) > 1:
        if args[1] == 'paid' or args[1].startswith('paid_'):
            pending = get_invoice(user_id)
            if pending:
                verify_payment(message.chat.id, pending['id'], user_id)
                return
    
    # Check premium status
    if is_premium(user_id):
        bot.send_message(
            message.chat.id,
            msg_welcome_premium(),
            parse_mode='Markdown',
            reply_markup=kb_premium()
        )
    else:
        bot.send_message(
            message.chat.id,
            msg_welcome(),
            parse_mode='Markdown',
            reply_markup=kb_main()
        )

@bot.message_handler(commands=['status'])
def cmd_status(message):
    """Handle /status command"""
    show_status(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['help'])
def cmd_help(message):
    """Handle /help command"""
    bot.send_message(
        message.chat.id,
        msg_help(),
        parse_mode='Markdown',
        reply_markup=kb_back()
    )

# ══════════════════════════════════════════════════════════════
# CALLBACK HANDLERS
# ══════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == 'menu')
def cb_menu(call):
    """Back to menu"""
    user_id = call.from_user.id
    
    if is_premium(user_id):
        bot.edit_message_text(
            msg_welcome_premium(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=kb_premium()
        )
    else:
        bot.edit_message_text(
            msg_welcome(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=kb_main()
        )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == 'buy')
def cb_buy(call):
    """Handle buy premium"""
    user_id = call.from_user.id
    
    if is_premium(user_id):
        bot.answer_callback_query(call.id, "✅ Kamu sudah premium!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "⏳ Membuat invoice...")
    
    try:
        bot.edit_message_text(
            "⏳ *Membuat invoice...*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    except:
        pass
    
    try:
        invoice = run_async(create_invoice(user_id))
        save_invoice(user_id, invoice.invoice_id, invoice.bot_invoice_url)
        
        bot.edit_message_text(
            msg_invoice(invoice.invoice_id),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=kb_invoice(invoice.bot_invoice_url, invoice.invoice_id)
        )
        
    except Exception as e:
        print(f"Error creating invoice: {e}")
        bot.edit_message_text(
            msg_error(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=kb_retry()
        )

@bot.callback_query_handler(func=lambda c: c.data.startswith('verify_'))
def cb_verify(call):
    """Verify payment"""
    invoice_id = call.data.replace('verify_', '')
    user_id = call.from_user.id
    
    bot.answer_callback_query(call.id, "🔍 Memeriksa pembayaran...")
    verify_payment(call.message.chat.id, invoice_id, user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == 'status')
def cb_status(call):
    """Show status"""
    show_status(call.message.chat.id, call.from_user.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == 'help')
def cb_help(call):
    """Show help"""
    bot.edit_message_text(
        msg_help(),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=kb_back()
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == 'cancel')
def cb_cancel(call):
    """Cancel payment"""
    bot.edit_message_text(
        msg_cancelled(),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=kb_back()
    )
    bot.answer_callback_query(call.id)

# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════

def verify_payment(chat_id, invoice_id, user_id, msg_id=None):
    """Verify payment status"""
    try:
        invoice = run_async(check_invoice(int(invoice_id)))
        
        if not invoice:
            text = msg_error()
            kb = kb_retry()
        elif invoice.status == 'paid':
            # Payment successful!
            if not is_premium(user_id):
                add_premium(user_id, invoice_id)
            remove_invoice(user_id)
            
            text = msg_success(invoice_id)
            kb = kb_success()
            
            # Notify admin (internal, no user info exposed)
            notify_admin(user_id, invoice_id)
            
        elif invoice.status == 'active':
            text = msg_pending(invoice_id)
            kb = kb_pending(invoice.bot_invoice_url, invoice_id)
        else:
            # Expired or cancelled
            text = msg_expired()
            kb = kb_retry()
        
        if msg_id:
            bot.edit_message_text(
                text, chat_id, msg_id,
                parse_mode='Markdown',
                reply_markup=kb
            )
        else:
            bot.send_message(
                chat_id, text,
                parse_mode='Markdown',
                reply_markup=kb
            )
            
    except Exception as e:
        print(f"Error verifying: {e}")
        if msg_id:
            bot.edit_message_text(
                msg_error(), chat_id, msg_id,
                parse_mode='Markdown',
                reply_markup=kb_retry()
            )
        else:
            bot.send_message(
                chat_id, msg_error(),
                parse_mode='Markdown',
                reply_markup=kb_retry()
            )

def show_status(chat_id, user_id, msg_id=None):
    """Show membership status"""
    if is_premium(user_id):
        data = get_premium_data(user_id)
        text = msg_status_premium(data)
        kb = kb_premium()
    else:
        text = msg_status_free()
        kb = kb_status_free()
    
    if msg_id:
        bot.edit_message_text(
            text, chat_id, msg_id,
            parse_mode='Markdown',
            reply_markup=kb
        )
    else:
        bot.send_message(
            chat_id, text,
            parse_mode='Markdown',
            reply_markup=kb
        )

def notify_admin(user_id, invoice_id):
    """Notify admin about new payment (private, no user data exposed to users)"""
    try:
        # Internal notification only
        text = f"""
🔔 *Pembayaran Baru*

💰 ${int(FINAL_PRICE)}
🔢 Invoice: `{invoice_id}`
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        bot.send_message(ADMIN_ID, text, parse_mode='Markdown')
    except:
        pass

# ══════════════════════════════════════════════════════════════
# ADMIN COMMANDS (Hidden from regular users)
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    """Admin panel"""
    if message.from_user.id != ADMIN_ID:
        return
    
    users = load_json(PREMIUM_DB)
    total = len(users)
    revenue = sum(u.get('amount', 0) for u in users.values())
    mode = "🧪 TESTNET" if USE_TESTNET else "🔐 MAINNET"
    
    text = f"""
🔧 *Admin Panel*

{mode}
👥 Premium: {total}
💰 Revenue: ${revenue}
💵 Price: ${int(FINAL_PRICE)}

/testapi - Test CryptoPay
/broadcast <msg> - Broadcast
"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['testapi'])
def cmd_testapi(message):
    """Test CryptoPay API"""
    if message.from_user.id != ADMIN_ID:
        return
    
    bot.reply_to(message, "🔄 Testing API...")
    
    try:
        info = run_async(get_app_info())
        mode = "TESTNET" if USE_TESTNET else "MAINNET"
        text = f"""
✅ *API Connected*

📱 App: {info.name}
🌐 Network: {mode}
"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    """Broadcast message to all premium users"""
    if message.from_user.id != ADMIN_ID:
        return
    
    text = message.text.replace('/broadcast', '').strip()
    if not text:
        bot.reply_to(message, "Usage: /broadcast <message>")
        return
    
    users = load_json(PREMIUM_DB)
    sent = 0
    
    for uid in users.keys():
        try:
            bot.send_message(int(uid), f"📢 *Pengumuman*\n\n{text}", parse_mode='Markdown')
            sent += 1
        except:
            pass
    
    bot.reply_to(message, f"✅ Broadcast sent to {sent}/{len(users)} users")

# ══════════════════════════════════════════════════════════════
# DEFAULT HANDLER
# ══════════════════════════════════════════════════════════════

@bot.message_handler(func=lambda m: True)
def default_handler(message):
    """Handle unknown messages"""
    bot.reply_to(
        message,
        "Ketik /start untuk memulai 👆",
        parse_mode='Markdown'
    )

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    mode = "🧪 TESTNET MODE" if USE_TESTNET else "🔐 PRODUCTION MODE"
    
    print("═" * 40)
    print("🤖 VIP Premium Bot")
    print("═" * 40)
    print(f"Mode: {mode}")
    print(f"Price: ${int(FINAL_PRICE)} (was ${ORIGINAL_PRICE})")
    print("═" * 40)
    print("Bot running...")
    print("═" * 40)
    
    bot.infinity_polling()
