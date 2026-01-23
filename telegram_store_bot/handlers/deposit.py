"""
💰 Deposit & Balance Handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
import asyncio
import config
from utils.database import db
from utils.payment import payment, format_currency, generate_order_id

# Conversation states
WAITING_DEPOSIT_AMOUNT = 1


async def menu_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show deposit menu"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    balance = await db.get_user_balance(user.id)
    
    e = config.EMOJI
    
    text = f"""
╔══════════════════════════════════╗
║     {e['money']} <b>DEPOSIT SALDO</b> {e['money']}     ║
╠══════════════════════════════════╣
║                                  ║
║  💰 Saldo Saat Ini:              ║
║  <b>{format_currency(balance)}</b>
║                                  ║
║  Pilih nominal deposit:          ║
║                                  ║
╚══════════════════════════════════╝
"""
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Rp 10.000", callback_data="deposit_10000"),
            InlineKeyboardButton("Rp 25.000", callback_data="deposit_25000")
        ],
        [
            InlineKeyboardButton("Rp 50.000", callback_data="deposit_50000"),
            InlineKeyboardButton("Rp 100.000", callback_data="deposit_100000")
        ],
        [
            InlineKeyboardButton("💵 Nominal Lain", callback_data="deposit_custom")
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


async def process_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process deposit request"""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    
    await query.answer("⏳ Membuat pembayaran...")
    
    # Parse amount
    if data.startswith("deposit_") and data != "deposit_custom":
        amount = int(data.replace("deposit_", ""))
    else:
        return
    
    # Generate order ID
    order_id = generate_order_id("DEP")
    
    # Create QRIS payment
    result = await payment.create_qris_transaction(order_id, amount)
    
    if not result or not result.get('success'):
        error_msg = result.get('error', 'Unknown error') if result else 'Connection failed'
        await query.edit_message_text(
            f"❌ Gagal membuat pembayaran: {error_msg}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Coba Lagi", callback_data="menu_deposit")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="back_main")]
            ])
        )
        return
    
    # Save transaction
    await db.create_transaction(
        order_id=order_id,
        user_id=user.id,
        product_type='deposit',
        product_name='Deposit Saldo',
        amount=amount,
        total_payment=result.get('total_payment', amount),
        qr_string=result.get('qr_string'),
        expired_at=result.get('expired_at'),
        extra_data={'fee': result.get('fee', 0)}
    )
    
    # Generate QR image
    qr_string = result.get('qr_string')
    qr_image = payment.generate_qr_image(qr_string)
    
    total = result.get('total_payment', amount)
    fee = result.get('fee', 0)
    
    caption = f"""
💳 <b>DEPOSIT SALDO</b>

🆔 Order ID: <code>{order_id}</code>
💰 Deposit: {format_currency(amount)}
💸 Fee: {format_currency(fee)}
━━━━━━━━━━━━━━━━━━━━
💵 <b>Total Bayar: {format_currency(total)}</b>

⏰ Berlaku 15 menit
📱 Scan QR dengan e-wallet/m-banking

⚠️ <i>Bayar sesuai nominal!</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Cek Status", callback_data=f"check_deposit_{order_id}")],
        [InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_deposit_{order_id}")]
    ])
    
    # Delete old message and send QR
    try:
        await query.message.delete()
    except:
        pass
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=qr_image,
        caption=caption,
        parse_mode='HTML',
        reply_markup=keyboard
    )
    
    # Start deposit checker
    context.application.create_task(
        check_deposit_loop(context, user.id, order_id, amount)
    )


async def deposit_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom deposit amount"""
    query = update.callback_query
    await query.answer()
    
    text = """
💵 <b>DEPOSIT CUSTOM</b>

Silakan kirim nominal deposit yang diinginkan.

<b>Minimal:</b> Rp 5.000
<b>Maksimal:</b> Rp 10.000.000

Contoh: <code>50000</code>

Ketik /cancel untuk membatalkan.
"""
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML'
    )
    
    context.user_data['waiting_deposit'] = True
    return WAITING_DEPOSIT_AMOUNT


async def receive_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive custom deposit amount"""
    if not context.user_data.get('waiting_deposit'):
        return ConversationHandler.END
    
    text = update.message.text.strip()
    user = update.effective_user
    
    # Parse amount
    try:
        amount = int(text.replace(".", "").replace(",", "").replace("Rp", "").strip())
    except ValueError:
        await update.message.reply_text(
            "❌ Format tidak valid. Kirim angka saja.\nContoh: <code>50000</code>",
            parse_mode='HTML'
        )
        return WAITING_DEPOSIT_AMOUNT
    
    # Validate amount
    if amount < 5000:
        await update.message.reply_text("❌ Minimal deposit Rp 5.000")
        return WAITING_DEPOSIT_AMOUNT
    
    if amount > 10000000:
        await update.message.reply_text("❌ Maksimal deposit Rp 10.000.000")
        return WAITING_DEPOSIT_AMOUNT
    
    context.user_data['waiting_deposit'] = False
    
    # Generate order ID
    order_id = generate_order_id("DEP")
    
    # Create QRIS payment
    result = await payment.create_qris_transaction(order_id, amount)
    
    if not result or not result.get('success'):
        error_msg = result.get('error', 'Unknown error') if result else 'Connection failed'
        await update.message.reply_text(
            f"❌ Gagal membuat pembayaran: {error_msg}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Coba Lagi", callback_data="deposit_custom")],
                [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
            ])
        )
        return ConversationHandler.END
    
    # Save transaction
    await db.create_transaction(
        order_id=order_id,
        user_id=user.id,
        product_type='deposit',
        product_name='Deposit Saldo',
        amount=amount,
        total_payment=result.get('total_payment', amount),
        qr_string=result.get('qr_string'),
        expired_at=result.get('expired_at'),
        extra_data={'fee': result.get('fee', 0)}
    )
    
    # Generate QR image
    qr_string = result.get('qr_string')
    qr_image = payment.generate_qr_image(qr_string)
    
    total = result.get('total_payment', amount)
    fee = result.get('fee', 0)
    
    caption = f"""
💳 <b>DEPOSIT SALDO</b>

🆔 Order ID: <code>{order_id}</code>
💰 Deposit: {format_currency(amount)}
💸 Fee: {format_currency(fee)}
━━━━━━━━━━━━━━━━━━━━
💵 <b>Total Bayar: {format_currency(total)}</b>

⏰ Berlaku 15 menit
📱 Scan QR dengan e-wallet/m-banking

⚠️ <i>Bayar sesuai nominal!</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Cek Status", callback_data=f"check_deposit_{order_id}")],
        [InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_deposit_{order_id}")]
    ])
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=qr_image,
        caption=caption,
        parse_mode='HTML',
        reply_markup=keyboard
    )
    
    # Start deposit checker
    context.application.create_task(
        check_deposit_loop(context, user.id, order_id, amount)
    )
    
    return ConversationHandler.END


async def cancel_deposit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel deposit input"""
    context.user_data['waiting_deposit'] = False
    
    await update.message.reply_text(
        "❌ Deposit dibatalkan.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Menu Utama", callback_data="back_main")]
        ])
    )
    return ConversationHandler.END


async def check_deposit_loop(context: ContextTypes.DEFAULT_TYPE, user_id: int, 
                             order_id: str, amount: int):
    """Background task to check deposit status"""
    max_checks = 60  # 15 minutes / 15 seconds
    
    for i in range(max_checks):
        await asyncio.sleep(15)  # Check every 15 seconds
        
        # Check transaction status
        txn = await db.get_transaction(order_id)
        if not txn or txn['status'] != 'pending':
            return  # Already processed
        
        # Check with payment gateway
        result = await payment.check_transaction_status(order_id, amount)
        
        if result and result.get('status') == 'completed':
            # Update transaction
            await db.update_transaction_status(order_id, 'completed')
            
            # Add balance
            new_balance = await db.update_balance(user_id, amount)
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"""
✅ <b>DEPOSIT BERHASIL!</b>

🆔 Order ID: <code>{order_id}</code>
💰 Jumlah: {format_currency(amount)}
💳 Saldo Baru: <b>{format_currency(new_balance)}</b>

Terima kasih! 🙏
""",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🛒 Belanja Sekarang", callback_data="menu_shop")],
                        [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_main")]
                    ])
                )
            except Exception as e:
                print(f"Deposit notification error: {e}")
            
            # Notify owner
            try:
                await context.bot.send_message(
                    chat_id=config.OWNER_ID,
                    text=f"""
💰 <b>DEPOSIT BARU!</b>

🆔 Order ID: <code>{order_id}</code>
👤 User ID: <code>{user_id}</code>
💵 Jumlah: {format_currency(amount)}
""",
                    parse_mode='HTML'
                )
            except:
                pass
            
            return
    
    # Expired
    txn = await db.get_transaction(order_id)
    if txn and txn['status'] == 'pending':
        await db.update_transaction_status(order_id, 'expired')
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"⏰ <b>Deposit Expired</b>\n\nOrder ID: <code>{order_id}</code>\n\nSilakan buat transaksi baru.",
                parse_mode='HTML'
            )
        except:
            pass


async def check_deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual check deposit status"""
    query = update.callback_query
    order_id = query.data.replace("check_deposit_", "")
    user = update.effective_user
    
    await query.answer("⏳ Mengecek status...")
    
    txn = await db.get_transaction(order_id)
    if not txn:
        await query.message.reply_text("❌ Transaksi tidak ditemukan.")
        return
    
    if txn['status'] == 'completed':
        await query.message.reply_text("✅ Deposit sudah berhasil!")
        return
    
    if txn['status'] == 'expired':
        await query.message.reply_text("⏰ Transaksi sudah expired.")
        return
    
    # Check with gateway
    result = await payment.check_transaction_status(order_id, txn['amount'])
    
    if result and result.get('status') == 'completed':
        await db.update_transaction_status(order_id, 'completed')
        
        # Add balance
        new_balance = await db.update_balance(user.id, txn['amount'])
        
        await query.message.reply_text(
            f"""
✅ <b>DEPOSIT BERHASIL!</b>

🆔 Order ID: <code>{order_id}</code>
💰 Jumlah: {format_currency(txn['amount'])}
💳 Saldo Baru: <b>{format_currency(new_balance)}</b>
""",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Belanja", callback_data="menu_shop")],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_main")]
            ])
        )
    else:
        await query.message.reply_text(
            "⏳ Pembayaran belum diterima.\n\nPastikan Anda sudah membayar sesuai nominal."
        )


async def cancel_deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel deposit"""
    query = update.callback_query
    order_id = query.data.replace("cancel_deposit_", "")
    
    await query.answer("⏳ Membatalkan...")
    
    txn = await db.get_transaction(order_id)
    if txn and txn['status'] == 'pending':
        await db.update_transaction_status(order_id, 'cancelled')
        
        # Try to cancel on gateway
        await payment.cancel_transaction(order_id, txn['amount'])
        
        await query.message.edit_caption(
            f"❌ <b>Deposit Dibatalkan</b>\n\nOrder ID: <code>{order_id}</code>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Menu Deposit", callback_data="menu_deposit")]
            ])
        )
    else:
        await query.message.reply_text("Transaksi tidak dapat dibatalkan.")


# Conversation handler for custom deposit
deposit_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(deposit_custom, pattern="^deposit_custom$")],
    states={
        WAITING_DEPOSIT_AMOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_deposit_amount),
            CommandHandler("cancel", cancel_deposit_input)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel_deposit_input)],
    per_user=True,
    per_chat=True
)
