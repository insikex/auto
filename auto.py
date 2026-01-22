import telebot
from telebot import types

# Ganti dengan token bot Anda dari @BotFather
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🎬 *Selamat Datang di VIP Premium Bot!* 🎬

Bergabunglah dengan kami untuk mengakses koleksi lebih dari *10.000 video premium* berkualitas tinggi!

✨ Dapatkan akses eksklusif ke konten terbaik
📱 Update konten setiap hari
🔒 Privasi terjamin

Klik tombol di bawah untuk bergabung! 👇
    """
    
    # Membuat inline keyboard
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton(
        "🚀 Gabung Sekarang!", 
        url="https://t.me/your_group_link"  # Ganti dengan link grup Anda
    )
    markup.add(join_button)
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Gunakan perintah /start untuk memulai!")

if __name__ == '__main__':
    print("Bot berjalan...")
    bot.infinity_polling()
