"""
🛒 Shop & Product Handlers
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from io import BytesIO
import asyncio
from datetime import datetime, timedelta
import config
from utils.database import db
from utils.payment import payment, format_currency, generate_order_id
from utils.helpers import escape_html, format_product_card


async def menu_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show shop menu"""
    query = update.callback_query
    await query.answer()
    
    e = config.EMOJI
    
    text = f"""
╔══════════════════════════════════╗
║     {e['cart']} <b>MENU LAYANAN</b> {e['cart']}     ║
╠══════════════════════════════════╣
║                                  ║
║  Silakan pilih layanan yang      ║
║  ingin Anda order:               ║
║                                  ║
║  💳 Pembayaran otomatis via QRIS ║
║  📦 Pengiriman data otomatis     ║
║                                  ║
╚══════════════════════════════════╝
"""
    
    keyboard = InlineKeyboardMarkup([
        # Script Bot option removed - automatic script delivery disabled
        [
            InlineKeyboardButton(f"📱 Apps Premium", callback_data="shop_apps")
        ],
        [
            InlineKeyboardButton(f"🖥️ Buy Panel", callback_data="shop_panel"),
            InlineKeyboardButton(f"👑 Admin Panel", callback_data="shop_admin_panel")
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


async def shop_scripts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available scripts"""
    query = update.callback_query
    await query.answer()
    
    products = await db.get_products(product_type='script')
    
    if not products:
        text = "📭 Belum ada script yang tersedia saat ini.\n\nSilakan cek lagi nanti!"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
        ])
    else:
        text = "📁 <b>DAFTAR SCRIPT</b>\n\nPilih script yang ingin Anda beli:\n"
        
        buttons = []
        for product in products:
            btn_text = f"{product['name']} - {format_currency(product['price'])}"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"buy_script_{product['id']}")])
        
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")])
        keyboard = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def shop_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available apps"""
    query = update.callback_query
    await query.answer()
    
    products = await db.get_products(product_type='app')
    
    if not products:
        text = "📭 Belum ada apps premium yang tersedia saat ini."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
        ])
    else:
        text = "📱 <b>DAFTAR APPS PREMIUM</b>\n\nPilih apps yang ingin Anda beli:\n"
        
        buttons = []
        for product in products:
            stock = await db.get_product_stock(product['id'])
            btn_text = f"{product['name']} ({stock} stok) - {format_currency(product['price'])}"
            if stock > 0:
                buttons.append([InlineKeyboardButton(btn_text, callback_data=f"buy_app_{product['id']}")])
            else:
                buttons.append([InlineKeyboardButton(f"❌ {product['name']} (HABIS)", callback_data="sold_out")])
        
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")])
        keyboard = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def shop_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show panel purchase menu"""
    query = update.callback_query
    await query.answer()
    
    is_open = await db.is_panel_open()
    
    if not is_open:
        text = "🚫 <b>Panel sedang tidak tersedia</b>\n\nSilakan coba lagi nanti atau hubungi owner."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Hubungi Owner", callback_data="menu_contact_owner")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
        ])
    else:
        price = config.PANEL_PRICES.get('unlimited', 2000)
        text = f"""
🖥️ <b>BELI PANEL PTERODACTYL</b>

<b>Fitur:</b>
✅ Panel Pterodactyl Gratis
✅ Unlimited Resources
✅ Node Berkualitas
✅ Support 24/7

<b>Harga:</b> {format_currency(price)}

Untuk melanjutkan, klik tombol di bawah.
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🛒 Beli Panel - {format_currency(price)}", callback_data="confirm_panel")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
        ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def shop_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel purchase"""
    query = update.callback_query
    await query.answer()
    
    price = config.PANEL_PRICES.get('admin', 10000)
    
    text = f"""
👑 <b>BELI AKUN ADMIN PANEL</b>

<b>Keuntungan Admin:</b>
✅ Akses Full Admin Panel
✅ Bisa Create Server
✅ Manage All Users
✅ Full Control

<b>Harga:</b> {format_currency(price)}
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🛒 Beli Admin - {format_currency(price)}", callback_data="confirm_admin_panel")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product purchase - Only supports Apps Premium now"""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    
    await query.answer()
    
    # Parse product type and ID - Script feature removed
    if data.startswith("buy_script_"):
        # Script buying disabled
        await query.edit_message_text(
            "❌ Fitur pembelian script telah dinonaktifkan.\n\nSilakan hubungi owner untuk informasi lebih lanjut.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Hubungi Owner", callback_data="menu_contact_owner")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
            ])
        )
        return
    elif data.startswith("buy_app_"):
        product_id = int(data.replace("buy_app_", ""))
        product_type = "app"
    else:
        return
    
    # Get product details
    product = await db.get_product(product_id)
    if not product:
        await query.edit_message_text("❌ Produk tidak ditemukan.")
        return
    
    # Check stock for apps
    if product_type == "app":
        stock = await db.get_product_stock(product_id)
        if stock <= 0:
            await query.edit_message_text(
                "❌ Maaf, stok produk ini sudah habis.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="shop_apps")]
                ])
            )
            return
    
    # Check user balance
    balance = await db.get_user_balance(user.id)
    price = product['price']
    
    text = format_product_card(product, show_stock=(product_type == "app"))
    text += f"\n\n💰 <b>Saldo Anda:</b> {format_currency(balance)}"
    
    if balance >= price:
        text += f"\n✅ Saldo cukup untuk membeli!"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Bayar dengan Saldo", callback_data=f"pay_balance_{product_type}_{product_id}")],
            [InlineKeyboardButton("💳 Bayar dengan QRIS", callback_data=f"pay_qris_{product_type}_{product_id}")],
            [InlineKeyboardButton("🔙 Kembali", callback_data=f"shop_{product_type}s")]
        ])
    else:
        text += f"\n⚠️ Saldo tidak cukup. Silakan bayar langsung dengan QRIS."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Bayar dengan QRIS", callback_data=f"pay_qris_{product_type}_{product_id}")],
            # Deposit option removed - QRIS deposit via Pakasir.com disabled
            [InlineKeyboardButton("🔙 Kembali", callback_data=f"shop_{product_type}s")]
        ])
    
    await query.edit_message_text(
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def pay_with_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment with balance"""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    
    await query.answer("⏳ Memproses pembayaran...")
    
    # Parse data
    parts = data.replace("pay_balance_", "").split("_")
    product_type = parts[0]
    product_id = int(parts[1])
    
    # Get product
    product = await db.get_product(product_id)
    if not product:
        await query.edit_message_text("❌ Produk tidak ditemukan.")
        return
    
    # Check balance
    balance = await db.get_user_balance(user.id)
    if balance < product['price']:
        await query.edit_message_text(
            "❌ Saldo tidak cukup!\n\nSilakan gunakan pembayaran QRIS langsung.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Bayar dengan QRIS", callback_data=f"pay_qris_{product_type}_{product_id}")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
            ])
        )
        return
    
    # Process payment
    try:
        # Deduct balance
        await db.update_balance(user.id, -product['price'])
        
        # Create transaction record
        order_id = generate_order_id("BAL")
        await db.create_transaction(
            order_id=order_id,
            user_id=user.id,
            product_type=product_type,
            product_id=product_id,
            product_name=product['name'],
            amount=product['price'],
            total_payment=product['price']
        )
        await db.update_transaction_status(order_id, 'completed')
        
        # Deliver product
        await deliver_product(update, context, product, product_type, order_id)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Terjadi kesalahan: {str(e)}")


async def pay_with_qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle QRIS payment"""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    
    await query.answer("⏳ Membuat pembayaran QRIS...")
    
    # Parse data
    parts = data.replace("pay_qris_", "").split("_")
    product_type = parts[0]
    product_id = int(parts[1])
    
    # Get product
    product = await db.get_product(product_id)
    if not product:
        await query.edit_message_text("❌ Produk tidak ditemukan.")
        return
    
    # Generate order ID
    order_id = generate_order_id("QRS")
    amount = product['price']
    
    # Create QRIS payment
    result = await payment.create_qris_transaction(order_id, amount)
    
    if not result or not result.get('success'):
        error_msg = result.get('error', 'Unknown error') if result else 'Connection failed'
        await query.edit_message_text(
            f"❌ Gagal membuat pembayaran: {error_msg}\n\nSilakan coba lagi.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Coba Lagi", callback_data=f"pay_qris_{product_type}_{product_id}")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_shop")]
            ])
        )
        return
    
    # Save transaction
    await db.create_transaction(
        order_id=order_id,
        user_id=user.id,
        product_type=product_type,
        product_id=product_id,
        product_name=product['name'],
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
💳 <b>PEMBAYARAN QRIS</b>

🆔 Order ID: <code>{order_id}</code>
📦 Produk: {product['name']}
💰 Harga: {format_currency(amount)}
💸 Fee: {format_currency(fee)}
━━━━━━━━━━━━━━━━━━━━
💵 <b>Total Bayar: {format_currency(total)}</b>

⏰ Berlaku 15 menit
📱 Scan QR dengan e-wallet/m-banking

⚠️ <i>Bayar sesuai nominal!</i>
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Cek Status Pembayaran", callback_data=f"check_payment_{order_id}")],
        [InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_payment_{order_id}")]
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
    
    # Start payment checker
    context.application.create_task(
        check_payment_loop(context, user.id, order_id, amount, product, product_type)
    )


async def check_payment_loop(context: ContextTypes.DEFAULT_TYPE, user_id: int, 
                             order_id: str, amount: int, product: dict, product_type: str):
    """Background task to check payment status"""
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
            
            # Deliver product
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ <b>Pembayaran Berhasil!</b>\n\nOrder ID: <code>{order_id}</code>",
                    parse_mode='HTML'
                )
                
                # Get product and deliver
                if product_type == 'script':
                    await deliver_script(context, user_id, product, order_id)
                elif product_type == 'app':
                    await deliver_app(context, user_id, product, order_id)
                
            except Exception as e:
                print(f"Delivery error: {e}")
            
            return
    
    # Expired
    txn = await db.get_transaction(order_id)
    if txn and txn['status'] == 'pending':
        await db.update_transaction_status(order_id, 'expired')
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"⏰ <b>Pembayaran Expired</b>\n\nOrder ID: <code>{order_id}</code>\n\nSilakan buat transaksi baru.",
                parse_mode='HTML'
            )
        except:
            pass


async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual check payment status"""
    query = update.callback_query
    order_id = query.data.replace("check_payment_", "")
    
    await query.answer("⏳ Mengecek status...")
    
    txn = await db.get_transaction(order_id)
    if not txn:
        await query.message.reply_text("❌ Transaksi tidak ditemukan.")
        return
    
    if txn['status'] == 'completed':
        await query.message.reply_text("✅ Pembayaran sudah berhasil!")
        return
    
    if txn['status'] == 'expired':
        await query.message.reply_text("⏰ Pembayaran sudah expired.")
        return
    
    # Check with gateway
    result = await payment.check_transaction_status(order_id, txn['amount'])
    
    if result and result.get('status') == 'completed':
        await db.update_transaction_status(order_id, 'completed')
        await query.message.reply_text(
            f"✅ <b>Pembayaran Berhasil!</b>\n\nProduk akan segera dikirim.",
            parse_mode='HTML'
        )
        
        # Deliver product
        product = await db.get_product(txn['product_id'])
        if product:
            await deliver_product(update, context, product, txn['product_type'], order_id)
    else:
        await query.message.reply_text(
            "⏳ Pembayaran belum diterima.\n\nPastikan Anda sudah membayar sesuai nominal."
        )


async def cancel_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel payment"""
    query = update.callback_query
    order_id = query.data.replace("cancel_payment_", "")
    
    await query.answer("⏳ Membatalkan...")
    
    txn = await db.get_transaction(order_id)
    if txn and txn['status'] == 'pending':
        await db.update_transaction_status(order_id, 'cancelled')
        
        # Try to cancel on gateway
        await payment.cancel_transaction(order_id, txn['amount'])
        
        await query.message.edit_caption(
            f"❌ <b>Transaksi Dibatalkan</b>\n\nOrder ID: <code>{order_id}</code>",
            parse_mode='HTML'
        )
    else:
        await query.message.reply_text("Transaksi tidak dapat dibatalkan.")


async def deliver_product(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                         product: dict, product_type: str, order_id: str):
    """Deliver purchased product"""
    user = update.effective_user
    
    if product_type == 'script':
        await deliver_script(context, user.id, product, order_id)
    elif product_type == 'app':
        await deliver_app(context, user.id, product, order_id)


async def deliver_script(context: ContextTypes.DEFAULT_TYPE, user_id: int, 
                        product: dict, order_id: str):
    """Deliver script product"""
    try:
        if product.get('file_id'):
            await context.bot.send_document(
                chat_id=user_id,
                document=product['file_id'],
                caption=f"""
✅ <b>PEMBELIAN BERHASIL!</b>

📦 Produk: {product['name']}
🆔 Order ID: <code>{order_id}</code>

Terima kasih sudah berbelanja! 🙏
""",
                parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"""
✅ <b>PEMBELIAN BERHASIL!</b>

📦 Produk: {product['name']}
🆔 Order ID: <code>{order_id}</code>

📝 {product.get('description', 'Hubungi owner untuk menerima produk.')}

Terima kasih sudah berbelanja! 🙏
""",
                parse_mode='HTML'
            )
            
        # Notify owner
        await notify_purchase(context, user_id, product, order_id)
        
    except Exception as e:
        print(f"Script delivery error: {e}")


async def deliver_app(context: ContextTypes.DEFAULT_TYPE, user_id: int, 
                     product: dict, order_id: str):
    """Deliver app account"""
    try:
        # Get account from stock
        account_data = await db.sell_product_account(product['id'], user_id)
        
        if account_data:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"""
✅ <b>PEMBELIAN BERHASIL!</b>

📱 Produk: {product['name']}
🆔 Order ID: <code>{order_id}</code>

━━━━━━━━━━━━━━━━━━━━
📋 <b>DATA AKUN:</b>
<code>{account_data}</code>
━━━━━━━━━━━━━━━━━━━━

⚠️ Segera ganti password!
Terima kasih sudah berbelanja! 🙏
""",
                parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Maaf, stok habis. Silakan hubungi owner untuk refund."
            )
        
        # Notify owner
        await notify_purchase(context, user_id, product, order_id)
        
    except Exception as e:
        print(f"App delivery error: {e}")


async def notify_purchase(context: ContextTypes.DEFAULT_TYPE, user_id: int, 
                         product: dict, order_id: str):
    """Notify owner about purchase"""
    try:
        user = await context.bot.get_chat(user_id)
        username = f"@{user.username}" if user.username else "-"
        
        text = f"""
💰 <b>PEMBELIAN BARU!</b>
━━━━━━━━━━━━━━━━━━━━
<b>Produk:</b> {product['name']}
<b>Harga:</b> {format_currency(product['price'])}
<b>Order ID:</b> <code>{order_id}</code>

<b>Pembeli:</b>
├ ID: <code>{user_id}</code>
└ Username: {username}
"""
        
        await context.bot.send_message(
            chat_id=config.OWNER_ID,
            text=text,
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Purchase notification error: {e}")


async def sold_out_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sold out product click"""
    query = update.callback_query
    await query.answer("❌ Produk ini sudah habis!", show_alert=True)
