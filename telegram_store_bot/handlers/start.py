"""
🚀 Start & Main Menu Handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import config
from utils.database import db
from utils.helpers import format_currency, get_uptime, escape_html

# Bot start time for uptime tracking
BOT_START_TIME = datetime.now()


async def get_welcome_text(user_count: int) -> str:
    """Generate welcome message text"""
    e = config.EMOJI
    uptime = get_uptime(BOT_START_TIME)
    
    return f"""
╔══════════════════════════════════╗
║     {e['star']} <b>SELAMAT DATANG</b> {e['star']}     ║
╠══════════════════════════════════╣
║                                  ║
║   {e['store']} <b>{config.BOT_NAME}</b>    ║
║                                  ║
╠══════════════════════════════════╣
║  {e['rocket']} <b>INFO BOT</b>                  ║
║  ├ Owner: {config.OWNER_NAME}
║  ├ Version: {config.BOT_VERSION}
║  └ Status: 🟢 Online
║                                  ║
║  {e['stats']} <b>STATISTIK</b>                 ║
║  ├ Total Users: {user_count}
║  └ Uptime: {uptime}
╚══════════════════════════════════╝

{e['fire']} <b>Selamat berbelanja!</b>
Silakan pilih menu di bawah ini.
"""


def get_main_keyboard(is_owner: bool = False) -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    e = config.EMOJI
    
    keyboard = [
        [
            InlineKeyboardButton(f"{e['cart']} Menu Layanan", callback_data="menu_shop"),
            InlineKeyboardButton(f"{e['tools']} Menu Tools", callback_data="menu_tools")
        ],
        [
            InlineKeyboardButton(f"{e['user']} Profil Saya", callback_data="menu_profile")
            # Deposit button removed - QRIS deposit via Pakasir.com disabled
        ],
        [
            InlineKeyboardButton(f"📢 Channel Info", url=f"https://t.me/{config.CHANNEL_USERNAME}"),
            InlineKeyboardButton(f"💬 Grup Diskusi", url=f"https://t.me/{config.GROUP_USERNAME}")
        ],
        [
            InlineKeyboardButton(f"📞 Hubungi Owner", callback_data="menu_contact_owner")
        ]
    ]
    
    if is_owner:
        keyboard.append([
            InlineKeyboardButton(f"{e['crown']} Menu Owner", callback_data="menu_owner")
        ])
    
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Only work in private chat
    if chat.type != 'private':
        await update.message.reply_text(
            f"🚫 Bot ini hanya bisa digunakan di <b>Private Chat</b>.\n"
            f"Silakan chat saya langsung di @{context.bot.username}",
            parse_mode='HTML'
        )
        return
    
    # Add user to database
    is_new = await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Notify owner about new user
    if is_new:
        await notify_new_user(context, user)
    
    # Get user count
    user_count = await db.get_user_count()
    
    # Generate welcome message
    welcome_text = await get_welcome_text(user_count)
    is_owner = user.id == config.OWNER_ID
    keyboard = get_main_keyboard(is_owner)
    
    # Send welcome message
    if config.START_PHOTO:
        try:
            await update.message.reply_photo(
                photo=config.START_PHOTO,
                caption=welcome_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except Exception:
            await update.message.reply_text(
                text=welcome_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
    else:
        await update.message.reply_text(
            text=welcome_text,
            parse_mode='HTML',
            reply_markup=keyboard
        )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to main menu callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_count = await db.get_user_count()
    
    welcome_text = await get_welcome_text(user_count)
    is_owner = user.id == config.OWNER_ID
    keyboard = get_main_keyboard(is_owner)
    
    try:
        await query.edit_message_text(
            text=welcome_text,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    except Exception:
        # If there was a photo, delete and send new message
        try:
            await query.message.delete()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except Exception:
            pass


async def notify_new_user(context: ContextTypes.DEFAULT_TYPE, user):
    """Notify owner about new user"""
    try:
        username = f"@{user.username}" if user.username else "-"
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        user_count = await db.get_user_count()
        
        text = f"""
👤 <b>USER BARU TERDAFTAR!</b>
━━━━━━━━━━━━━━━━━━━━━
<b>Nama:</b> {escape_html(name)}
<b>Username:</b> {username}
<b>ID:</b> <code>{user.id}</code>
<b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📊 <b>Total User:</b> {user_count}
"""
        
        await context.bot.send_message(
            chat_id=config.OWNER_ID,
            text=text,
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Failed to notify owner: {e}")


async def menu_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    e = config.EMOJI
    
    # Get user data
    user_data = await db.get_user(user.id)
    balance = user_data['balance'] if user_data else 0
    transactions = await db.get_user_transactions(user.id, limit=5)
    
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "-"
    
    text = f"""
╔══════════════════════════════════╗
║     {e['user']} <b>PROFIL SAYA</b> {e['user']}     ║
╠══════════════════════════════════╣
║  <b>Nama:</b> {escape_html(name)}
║  <b>Username:</b> {username}
║  <b>ID:</b> <code>{user.id}</code>
╠══════════════════════════════════╣
║  {e['money']} <b>Saldo:</b> {format_currency(balance)}
║  📦 <b>Total Transaksi:</b> {len(transactions)}
╚══════════════════════════════════╝
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📜 Riwayat Transaksi", callback_data="menu_history")
            # Deposit button removed - QRIS deposit via Pakasir.com disabled
        ],
        [InlineKeyboardButton(f"{e['back']} Kembali", callback_data="back_main")]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def menu_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show transaction history"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    transactions = await db.get_user_transactions(user.id, limit=10)
    
    if not transactions:
        text = "📭 Belum ada riwayat transaksi."
    else:
        text = "📜 <b>RIWAYAT TRANSAKSI</b>\n\n"
        
        for i, txn in enumerate(transactions, 1):
            status_emoji = {
                'pending': '⏳',
                'completed': '✅',
                'expired': '⌛',
                'cancelled': '❌'
            }.get(txn['status'], '❓')
            
            text += f"{i}. {status_emoji} <code>{txn['order_id']}</code>\n"
            text += f"   💰 {format_currency(txn['amount'])} - {txn['product_name'] or 'Deposit'}\n\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_profile")]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def menu_contact_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show contact owner menu"""
    query = update.callback_query
    await query.answer()
    
    e = config.EMOJI
    
    text = f"""
╔══════════════════════════════════╗
║     📞 <b>HUBUNGI OWNER</b> 📞     ║
╠══════════════════════════════════╣
║  <b>Nama:</b> {config.OWNER_NAME}
║  <b>Telegram:</b> {config.OWNER_USERNAME}
╚══════════════════════════════════╝

{e['info']} Silakan hubungi owner untuk bantuan
atau pertanyaan seputar layanan.
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Chat Owner", url=f"https://t.me/{config.OWNER_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton(f"{e['back']} Kembali", callback_data="back_main")]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )
