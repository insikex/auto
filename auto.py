import telebot
from telebot import types
import asyncio
import json
import os
from datetime import datetime
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import Assets, PaidButtons, CurrencyType

# ==================== KONFIGURASI ====================
# Ganti dengan token bot Anda dari @BotFather
BOT_TOKEN = '7829954744:AAEJgjBWRTdaJmh7gsnLlE_cNo1TXl0i6EU'

# Ganti dengan API token CryptoPay dari @CryptoBot
CRYPTOPAY_TOKEN = '519883:AAJsQ1LRbcYeeGw0RivIRdACWjpZGW8VGfL'

# Link premium channel/group
PREMIUM_LINK = 'https://t.me/+V2JE9sIz35ZmZGNl'

# Admin user ID (untuk notifikasi)
ADMIN_ID = 123456789  # Ganti dengan user ID admin

# Harga Premium
ORIGINAL_PRICE = 300  # Harga asli dalam USD
DISCOUNT_PERCENT = 50  # Diskon 50%
FINAL_PRICE = ORIGINAL_PRICE * (100 - DISCOUNT_PERCENT) / 100  # $150

# File untuk menyimpan data user premium
PREMIUM_DB_FILE = 'premium_users.json'

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

# ==================== CRYPTOPAY FUNCTIONS ====================
async def create_payment_invoice(user_id, username):
    """Buat invoice pembayaran CryptoPay"""
    crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=Networks.MAIN_NET)
    
    try:
        # Buat invoice dengan fiat USD
        invoice = await crypto.create_invoice(
            amount=FINAL_PRICE,
            fiat='USD',
            currency_type=CurrencyType.FIAT,
            description=f'🌟 VIP Premium Lifetime Access\n'
                       f'👤 User: {username}\n'
                       f'💰 Harga Asli: ${ORIGINAL_PRICE}\n'
                       f'🔥 Diskon: {DISCOUNT_PERCENT}%\n'
                       f'✅ Final: ${FINAL_PRICE}',
            paid_btn_name=PaidButtons.CALLBACK,
            paid_btn_url=f'https://t.me/{bot.get_me().username}?start=paid_{invoice.invoice_id if hasattr(invoice, "invoice_id") else "check"}',
            payload=f'{user_id}:{username}',
            allow_comments=True,
            allow_anonymous=False
        )
        
        return invoice
    finally:
        await crypto.close()

async def check_invoice_status(invoice_id):
    """Cek status pembayaran invoice"""
    crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=Networks.MAIN_NET)
    
    try:
        invoices = await crypto.get_invoices(invoice_ids=[invoice_id])
        if invoices:
            return invoices[0]
        return None
    finally:
        await crypto.close()

def run_async(coro):
    """Helper untuk menjalankan async function"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ==================== BOT HANDLERS ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Cek jika ada parameter paid
    args = message.text.split()
    if len(args) > 1 and args[1].startswith('paid_'):
        invoice_id = args[1].replace('paid_', '')
        check_payment(message, invoice_id)
        return
    
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
    
    # Buat invoice
    try:
        invoice = run_async(create_payment_invoice(user_id, username))
        
        if invoice:
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
        else:
            bot.edit_message_text(
                "❌ Gagal membuat invoice. Silakan coba lagi nanti.",
                call.message.chat.id,
                call.message.message_id
            )
            
    except Exception as e:
        error_text = f"""
❌ *Terjadi Kesalahan*

Tidak dapat membuat invoice saat ini.
Silakan coba lagi nanti atau hubungi admin.

Error: `{str(e)[:100]}`
        """
        bot.edit_message_text(
            error_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def handle_verify_payment(call):
    """Verifikasi pembayaran"""
    invoice_id = call.data.replace('verify_', '')
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name
    
    bot.answer_callback_query(call.id, "Memeriksa pembayaran... 🔍")
    
    try:
        invoice = run_async(check_invoice_status(int(invoice_id)))
        
        if invoice:
            if invoice.status == 'paid':
                # Pembayaran sukses!
                add_premium_user(user_id, username, invoice_id)
                
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
                    bot.send_message(ADMIN_ID, admin_text, parse_mode='Markdown')
                except:
                    pass
                    
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
            bot.answer_callback_query(call.id, "❌ Invoice tidak ditemukan!", show_alert=True)
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Error: {str(e)[:50]}", show_alert=True)

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
        else:
            # Redirect ke menu utama
            send_welcome(message)
            
    except:
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
