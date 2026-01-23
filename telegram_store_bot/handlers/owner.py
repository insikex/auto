"""
👑 Owner Menu Handlers
Admin controls for the bot
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
import config
from utils.database import db
from utils.helpers import format_currency, escape_html, get_uptime
from handlers.start import BOT_START_TIME

# Conversation states
WAITING_SCRIPT_FILE = 1
WAITING_SCRIPT_DETAILS = 2
WAITING_APP_NAME = 3
WAITING_APP_PRICE = 4
WAITING_ACCOUNT_DATA = 5
WAITING_BROADCAST = 6
WAITING_ADD_BALANCE_USER = 7
WAITING_ADD_BALANCE_AMOUNT = 8


def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    return user_id == config.OWNER_ID


async def menu_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show owner menu"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Kamu bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    e = config.EMOJI
    
    # Get stats
    user_count = await db.get_user_count()
    products = await db.get_products()
    pending_txns = await db.get_pending_transactions()
    panel_status = "🟢 BUKA" if await db.is_panel_open() else "🔴 TUTUP"
    uptime = get_uptime(BOT_START_TIME)
    
    text = f"""
╔══════════════════════════════════╗
║     {e['crown']} <b>OWNER PANEL</b> {e['crown']}     ║
╠══════════════════════════════════╣
║  📊 <b>STATISTIK</b>
║  ├ Total Users: {user_count}
║  ├ Total Produk: {len(products)}
║  ├ Pending Transaksi: {len(pending_txns)}
║  └ Uptime: {uptime}
║
║  🖥️ Status Panel: {panel_status}
╚══════════════════════════════════╝
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Toggle Panel", callback_data="owner_toggle_panel"),
            InlineKeyboardButton("📢 Broadcast", callback_data="owner_broadcast")
        ],
        [
            InlineKeyboardButton("➕ Add Script", callback_data="owner_add_script"),
            InlineKeyboardButton("➕ Add Apps", callback_data="owner_add_app")
        ],
        [
            InlineKeyboardButton("📋 List Produk", callback_data="owner_list_products"),
            InlineKeyboardButton("🗑️ Hapus Produk", callback_data="owner_delete_product")
        ],
        [
            InlineKeyboardButton("➕ Add Account", callback_data="owner_add_account")
        ],
        [
            InlineKeyboardButton("📜 Transaksi Pending", callback_data="owner_pending_txns"),
            InlineKeyboardButton("👥 List Users", callback_data="owner_list_users")
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


async def owner_toggle_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle panel open/close"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    new_status = await db.toggle_panel()
    status_text = "🟢 DIBUKA" if new_status else "🔴 DITUTUP"
    
    await query.answer(f"Panel {status_text}", show_alert=True)
    await menu_owner(update, context)


async def owner_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    await query.edit_message_text(
        "📢 <b>BROADCAST</b>\n\n"
        "Kirim pesan yang ingin di-broadcast ke semua user.\n\n"
        "Ketik /cancel untuk membatalkan.",
        parse_mode='HTML'
    )
    
    context.user_data['waiting_broadcast'] = True
    return WAITING_BROADCAST


async def owner_broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send broadcast message"""
    if not context.user_data.get('waiting_broadcast'):
        return ConversationHandler.END
    
    if not is_owner(update.effective_user.id):
        return ConversationHandler.END
    
    context.user_data['waiting_broadcast'] = False
    message = update.message
    
    users = await db.get_all_users()
    
    success = 0
    failed = 0
    
    status_msg = await message.reply_text(
        f"📢 Broadcasting ke {len(users)} users..."
    )
    
    for user in users:
        try:
            # Forward the message
            await message.copy(chat_id=user['id'])
            success += 1
        except Exception:
            failed += 1
        
        # Update status every 50 users
        if (success + failed) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"📢 Broadcasting... {success + failed}/{len(users)}"
                )
            except:
                pass
    
    await status_msg.edit_text(
        f"✅ <b>Broadcast Selesai!</b>\n\n"
        f"✓ Berhasil: {success}\n"
        f"✗ Gagal: {failed}",
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


async def owner_add_script_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding script"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    await query.edit_message_text(
        "📁 <b>TAMBAH SCRIPT</b>\n\n"
        "Kirim file script (.zip) yang ingin dijual.\n\n"
        "Ketik /cancel untuk membatalkan.",
        parse_mode='HTML'
    )
    
    context.user_data['adding_script'] = True
    return WAITING_SCRIPT_FILE


async def owner_receive_script_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive script file"""
    if not context.user_data.get('adding_script'):
        return ConversationHandler.END
    
    if not is_owner(update.effective_user.id):
        return ConversationHandler.END
    
    document = update.message.document
    
    if not document:
        await update.message.reply_text("❌ Kirim file dokumen!")
        return WAITING_SCRIPT_FILE
    
    if not document.file_name.endswith('.zip'):
        await update.message.reply_text("❌ File harus berformat .zip!")
        return WAITING_SCRIPT_FILE
    
    context.user_data['script_file_id'] = document.file_id
    context.user_data['script_file_name'] = document.file_name
    
    await update.message.reply_text(
        "✅ File diterima!\n\n"
        "Sekarang kirim detail script:\n"
        "<code>Nama | Harga | Deskripsi</code>\n\n"
        "Contoh:\n"
        "<code>Bot WhatsApp | 50000 | Bot WA dengan fitur lengkap</code>",
        parse_mode='HTML'
    )
    
    return WAITING_SCRIPT_DETAILS


async def owner_receive_script_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive script details"""
    if not context.user_data.get('adding_script'):
        return ConversationHandler.END
    
    text = update.message.text
    parts = [p.strip() for p in text.split('|')]
    
    if len(parts) < 2:
        await update.message.reply_text(
            "❌ Format salah!\n"
            "Gunakan: <code>Nama | Harga | Deskripsi</code>",
            parse_mode='HTML'
        )
        return WAITING_SCRIPT_DETAILS
    
    name = parts[0]
    try:
        price = int(parts[1].replace('.', '').replace(',', ''))
    except ValueError:
        await update.message.reply_text("❌ Harga harus angka!")
        return WAITING_SCRIPT_DETAILS
    
    description = parts[2] if len(parts) > 2 else ""
    
    # Save to database
    product_id = await db.add_product(
        product_type='script',
        name=name,
        price=price,
        description=description,
        file_id=context.user_data.get('script_file_id')
    )
    
    context.user_data['adding_script'] = False
    
    await update.message.reply_text(
        f"✅ <b>Script Berhasil Ditambahkan!</b>\n\n"
        f"📦 ID: {product_id}\n"
        f"📝 Nama: {name}\n"
        f"💰 Harga: {format_currency(price)}\n"
        f"📄 Deskripsi: {description or '-'}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Menu Owner", callback_data="menu_owner")]
        ])
    )
    
    return ConversationHandler.END


async def owner_add_app_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding app"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    await query.edit_message_text(
        "📱 <b>TAMBAH APPS PREMIUM</b>\n\n"
        "Kirim nama apps:\n\n"
        "Ketik /cancel untuk membatalkan.",
        parse_mode='HTML'
    )
    
    context.user_data['adding_app'] = True
    return WAITING_APP_NAME


async def owner_receive_app_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive app name"""
    if not context.user_data.get('adding_app'):
        return ConversationHandler.END
    
    context.user_data['app_name'] = update.message.text
    
    await update.message.reply_text(
        "Sekarang kirim harga apps (angka saja):\n"
        "Contoh: <code>25000</code>",
        parse_mode='HTML'
    )
    
    return WAITING_APP_PRICE


async def owner_receive_app_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive app price"""
    try:
        price = int(update.message.text.replace('.', '').replace(',', ''))
    except ValueError:
        await update.message.reply_text("❌ Harga harus angka!")
        return WAITING_APP_PRICE
    
    name = context.user_data.get('app_name')
    
    # Save to database
    product_id = await db.add_product(
        product_type='app',
        name=name,
        price=price,
        description=""
    )
    
    context.user_data['adding_app'] = False
    
    await update.message.reply_text(
        f"✅ <b>Apps Berhasil Ditambahkan!</b>\n\n"
        f"📦 ID: {product_id}\n"
        f"📱 Nama: {name}\n"
        f"💰 Harga: {format_currency(price)}\n\n"
        f"⚠️ Jangan lupa tambahkan akun dengan menu 'Add Account'!",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Account", callback_data="owner_add_account")],
            [InlineKeyboardButton("👑 Menu Owner", callback_data="menu_owner")]
        ])
    )
    
    return ConversationHandler.END


async def owner_list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all products"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    products = await db.get_products()
    
    if not products:
        text = "📭 Belum ada produk."
    else:
        text = "📋 <b>DAFTAR PRODUK</b>\n\n"
        
        for i, p in enumerate(products, 1):
            if p['type'] == 'app':
                stock = await db.get_product_stock(p['id'])
                text += f"{i}. [{p['type'].upper()}] {p['name']}\n"
                text += f"   💰 {format_currency(p['price'])} | 📦 Stok: {stock}\n\n"
            else:
                text += f"{i}. [{p['type'].upper()}] {p['name']}\n"
                text += f"   💰 {format_currency(p['price'])}\n\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑️ Hapus Produk", callback_data="owner_delete_product")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_owner")]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def owner_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show delete product menu"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    products = await db.get_products()
    
    if not products:
        await query.edit_message_text(
            "📭 Tidak ada produk untuk dihapus.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_owner")]
            ])
        )
        return
    
    text = "🗑️ <b>HAPUS PRODUK</b>\n\nPilih produk yang ingin dihapus:\n"
    
    buttons = []
    for p in products:
        btn_text = f"❌ {p['name']}"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"delete_product_{p['id']}")])
    
    buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="menu_owner")])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def owner_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete product"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    product_id = int(query.data.replace("delete_product_", ""))
    product = await db.get_product(product_id)
    
    if product:
        await db.delete_product(product_id)
        await query.answer(f"✅ {product['name']} dihapus!", show_alert=True)
    else:
        await query.answer("❌ Produk tidak ditemukan", show_alert=True)
    
    await owner_delete_product(update, context)


async def owner_add_account_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding account to product"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    # Get apps
    apps = await db.get_products(product_type='app')
    
    if not apps:
        await query.edit_message_text(
            "📭 Belum ada apps. Tambahkan apps dulu!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Apps", callback_data="owner_add_app")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_owner")]
            ])
        )
        return
    
    text = "📱 <b>PILIH APPS</b>\n\nPilih apps untuk menambahkan akun:\n"
    
    buttons = []
    for app in apps:
        stock = await db.get_product_stock(app['id'])
        buttons.append([
            InlineKeyboardButton(
                f"{app['name']} (stok: {stock})", 
                callback_data=f"add_acc_to_{app['id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="menu_owner")])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def owner_select_app_for_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select app to add account"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    product_id = int(query.data.replace("add_acc_to_", ""))
    context.user_data['adding_account_to'] = product_id
    
    product = await db.get_product(product_id)
    
    await query.edit_message_text(
        f"📱 <b>TAMBAH AKUN KE: {product['name']}</b>\n\n"
        "Kirim data akun (satu per baris untuk multiple):\n\n"
        "Format:\n"
        "<code>email:password</code>\n\n"
        "Atau multiple:\n"
        "<code>email1:pass1\nemail2:pass2</code>\n\n"
        "Ketik /cancel untuk membatalkan.",
        parse_mode='HTML'
    )
    
    return WAITING_ACCOUNT_DATA


async def owner_receive_account_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive account data"""
    if not context.user_data.get('adding_account_to'):
        return ConversationHandler.END
    
    product_id = context.user_data.get('adding_account_to')
    text = update.message.text
    
    # Parse multiple accounts
    accounts = [acc.strip() for acc in text.split('\n') if acc.strip()]
    
    added = 0
    for account in accounts:
        await db.add_product_account(product_id, account)
        added += 1
    
    context.user_data['adding_account_to'] = None
    
    product = await db.get_product(product_id)
    new_stock = await db.get_product_stock(product_id)
    
    await update.message.reply_text(
        f"✅ <b>Akun Berhasil Ditambahkan!</b>\n\n"
        f"📱 Apps: {product['name']}\n"
        f"➕ Ditambahkan: {added} akun\n"
        f"📦 Total Stok: {new_stock}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Tambah Lagi", callback_data=f"add_acc_to_{product_id}")],
            [InlineKeyboardButton("👑 Menu Owner", callback_data="menu_owner")]
        ])
    )
    
    return ConversationHandler.END


async def owner_add_balance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding balance to user - DISABLED (balance feature removed)"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer("❌ Fitur saldo sudah dihapus!", show_alert=True)
    
    await query.edit_message_text(
        "❌ <b>FITUR SALDO DIHAPUS</b>\n\n"
        "Fitur saldo user sudah tidak tersedia.\n"
        "Pembayaran sekarang langsung melalui QRIS Pakasir.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Menu Owner", callback_data="menu_owner")]
        ])
    )
    
    return ConversationHandler.END


async def owner_receive_balance_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive user ID for balance - DISABLED"""
    await update.message.reply_text(
        "❌ Fitur saldo sudah dihapus.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Menu Owner", callback_data="menu_owner")]
        ])
    )
    return ConversationHandler.END


async def owner_receive_balance_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive balance amount - DISABLED"""
    await update.message.reply_text(
        "❌ Fitur saldo sudah dihapus.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Menu Owner", callback_data="menu_owner")]
        ])
    )
    return ConversationHandler.END


async def owner_pending_txns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending transactions"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    pending = await db.get_pending_transactions()
    
    if not pending:
        text = "📭 Tidak ada transaksi pending."
    else:
        text = f"⏳ <b>TRANSAKSI PENDING ({len(pending)})</b>\n\n"
        
        for txn in pending[:10]:  # Show max 10
            text += f"🆔 <code>{txn['order_id']}</code>\n"
            text += f"   👤 {txn['user_id']} | 💰 {format_currency(txn['amount'])}\n"
            text += f"   📦 {txn['product_name'] or 'Deposit'}\n\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_owner")]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def owner_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user list"""
    query = update.callback_query
    
    if not is_owner(update.effective_user.id):
        await query.answer("🚫 Bukan owner!", show_alert=True)
        return
    
    await query.answer()
    
    users = await db.get_all_users()
    
    if not users:
        text = "📭 Belum ada user terdaftar."
    else:
        text = f"👥 <b>DAFTAR USER ({len(users)})</b>\n\n"
        
        for i, user in enumerate(users[:20], 1):  # Show max 20
            username = f"@{user['username']}" if user.get('username') else "-"
            name = user.get('first_name') or '-'
            text += f"{i}. <code>{user['id']}</code>\n"
            text += f"   👤 {escape_html(name)} | {username}\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_owner")]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def cancel_owner_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any owner action"""
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Dibatalkan.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Menu Owner", callback_data="menu_owner")]
        ])
    )
    return ConversationHandler.END
