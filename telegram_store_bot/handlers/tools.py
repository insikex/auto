"""
🛠️ Tools Menu Handlers
Utility tools for users
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
import aiohttp
import qrcode
from io import BytesIO
import config
from utils.helpers import escape_html

# Conversation states
WAITING_QR_TEXT = 1
WAITING_SHORT_URL = 2


async def menu_tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show tools menu"""
    query = update.callback_query
    await query.answer()
    
    e = config.EMOJI
    
    text = f"""
╔══════════════════════════════════╗
║     {e['tools']} <b>MENU TOOLS</b> {e['tools']}     ║
╠══════════════════════════════════╣
║                                  ║
║  🛠️ Tools yang tersedia:         ║
║                                  ║
║  📱 /makeqr - Buat QR Code       ║
║  🔗 /shorten - Pendekkan URL     ║
║  📸 /ssweb - Screenshot Website  ║
║                                  ║
╚══════════════════════════════════╝

<i>Klik tombol atau ketik command!</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Make QR", callback_data="tool_makeqr"),
            InlineKeyboardButton("🔗 Shorten URL", callback_data="tool_shorten")
        ],
        [
            InlineKeyboardButton("📸 Screenshot Web", callback_data="tool_ssweb")
        ],
        [
            InlineKeyboardButton(f"{e['back']} Kembali", callback_data="back_main")
        ]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def tool_makeqr_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start QR code generation"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📱 <b>BUAT QR CODE</b>\n\n"
        "Kirim teks atau URL yang ingin dijadikan QR Code:\n\n"
        "Ketik /cancel untuk membatalkan.",
        parse_mode='HTML'
    )
    
    context.user_data['waiting_qr'] = True
    return WAITING_QR_TEXT


async def tool_makeqr_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR code"""
    if not context.user_data.get('waiting_qr'):
        return ConversationHandler.END
    
    text = update.message.text
    context.user_data['waiting_qr'] = False
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    await update.message.reply_photo(
        photo=buffer,
        caption=f"📱 <b>QR Code Berhasil Dibuat!</b>\n\n"
                f"📝 Isi: <code>{escape_html(text[:100])}{'...' if len(text) > 100 else ''}</code>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Buat Lagi", callback_data="tool_makeqr")],
            [InlineKeyboardButton("🔙 Menu Tools", callback_data="menu_tools")]
        ])
    )
    
    return ConversationHandler.END


async def makeqr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /makeqr command"""
    args = update.message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await update.message.reply_text(
            "📱 <b>BUAT QR CODE</b>\n\n"
            "Gunakan: <code>/makeqr [teks/url]</code>\n\n"
            "Contoh:\n"
            "<code>/makeqr https://google.com</code>",
            parse_mode='HTML'
        )
        return
    
    text = args[1]
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    await update.message.reply_photo(
        photo=buffer,
        caption=f"📱 <b>QR Code Berhasil Dibuat!</b>\n\n"
                f"📝 Isi: <code>{escape_html(text[:100])}{'...' if len(text) > 100 else ''}</code>",
        parse_mode='HTML'
    )


async def tool_shorten_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start URL shortening"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔗 <b>PENDEKKAN URL</b>\n\n"
        "Kirim URL yang ingin dipendekkan:\n\n"
        "Contoh: <code>https://www.example.com/very/long/url</code>\n\n"
        "Ketik /cancel untuk membatalkan.",
        parse_mode='HTML'
    )
    
    context.user_data['waiting_shorten'] = True
    return WAITING_SHORT_URL


async def tool_shorten_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process URL shortening"""
    if not context.user_data.get('waiting_shorten'):
        return ConversationHandler.END
    
    url = update.message.text.strip()
    context.user_data['waiting_shorten'] = False
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    processing_msg = await update.message.reply_text("⏳ Memproses...")
    
    try:
        # Using TinyURL API
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://tinyurl.com/api-create.php?url={url}",
                timeout=10
            ) as response:
                if response.status == 200:
                    short_url = await response.text()
                    
                    await processing_msg.edit_text(
                        f"🔗 <b>URL Berhasil Dipendekkan!</b>\n\n"
                        f"📎 Original:\n<code>{escape_html(url[:100])}{'...' if len(url) > 100 else ''}</code>\n\n"
                        f"✂️ Short URL:\n<code>{short_url}</code>",
                        parse_mode='HTML',
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔗 Pendekkan Lagi", callback_data="tool_shorten")],
                            [InlineKeyboardButton("🔙 Menu Tools", callback_data="menu_tools")]
                        ])
                    )
                else:
                    await processing_msg.edit_text(
                        "❌ Gagal mempendekkan URL. Coba lagi nanti.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 Menu Tools", callback_data="menu_tools")]
                        ])
                    )
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Error: {str(e)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Menu Tools", callback_data="menu_tools")]
            ])
        )
    
    return ConversationHandler.END


async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /shorten command"""
    args = update.message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await update.message.reply_text(
            "🔗 <b>PENDEKKAN URL</b>\n\n"
            "Gunakan: <code>/shorten [url]</code>\n\n"
            "Contoh:\n"
            "<code>/shorten https://google.com</code>",
            parse_mode='HTML'
        )
        return
    
    url = args[1].strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    processing_msg = await update.message.reply_text("⏳ Memproses...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://tinyurl.com/api-create.php?url={url}",
                timeout=10
            ) as response:
                if response.status == 200:
                    short_url = await response.text()
                    
                    await processing_msg.edit_text(
                        f"🔗 <b>URL Berhasil Dipendekkan!</b>\n\n"
                        f"📎 Original:\n<code>{escape_html(url[:100])}</code>\n\n"
                        f"✂️ Short URL:\n<code>{short_url}</code>",
                        parse_mode='HTML'
                    )
                else:
                    await processing_msg.edit_text("❌ Gagal mempendekkan URL.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {str(e)}")


async def tool_ssweb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Screenshot website info"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📸 <b>SCREENSHOT WEBSITE</b>\n\n"
        "Gunakan command:\n"
        "<code>/ssweb [url]</code>\n\n"
        "Contoh:\n"
        "<code>/ssweb https://google.com</code>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Menu Tools", callback_data="menu_tools")]
        ])
    )


async def ssweb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ssweb command"""
    args = update.message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await update.message.reply_text(
            "📸 <b>SCREENSHOT WEBSITE</b>\n\n"
            "Gunakan: <code>/ssweb [url]</code>\n\n"
            "Contoh:\n"
            "<code>/ssweb https://google.com</code>",
            parse_mode='HTML'
        )
        return
    
    url = args[1].strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    processing_msg = await update.message.reply_text("📸 Mengambil screenshot...")
    
    try:
        # Using free screenshot API
        screenshot_url = f"https://image.thum.io/get/width/1280/crop/720/noanimate/{url}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(screenshot_url, timeout=30) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    await processing_msg.delete()
                    await update.message.reply_photo(
                        photo=BytesIO(image_data),
                        caption=f"📸 <b>Screenshot Website</b>\n\n"
                                f"🔗 URL: <code>{escape_html(url[:50])}</code>",
                        parse_mode='HTML'
                    )
                else:
                    await processing_msg.edit_text("❌ Gagal mengambil screenshot.")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {str(e)}")


async def cancel_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel tool action"""
    context.user_data['waiting_qr'] = False
    context.user_data['waiting_shorten'] = False
    
    await update.message.reply_text(
        "❌ Dibatalkan.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Menu Tools", callback_data="menu_tools")]
        ])
    )
    return ConversationHandler.END
