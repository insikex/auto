"""
🛒 Smart Store Bot
Telegram Store Bot with Pakasir.com Payment Gateway

Author: Smart Bot Developer
Version: 1.0.0
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

import config
from utils.database import db

# Import handlers
from handlers.start import (
    start_command,
    back_to_main,
    menu_profile,
    menu_history,
    menu_contact_owner
)
from handlers.shop import (
    menu_shop,
    # shop_scripts,  # Script Bot feature removed - automatic script delivery disabled
    shop_apps,
    shop_panel,
    shop_admin_panel,
    buy_product,
    pay_with_balance,
    pay_with_qris,
    check_payment_callback,
    cancel_payment_callback,
    sold_out_callback
)
# Deposit feature removed - QRIS deposit via Pakasir.com disabled
# from handlers.deposit import (
#     menu_deposit,
#     process_deposit,
#     deposit_conversation,
#     check_deposit_callback,
#     cancel_deposit_callback
# )
from handlers.owner import (
    menu_owner,
    owner_toggle_panel,
    owner_broadcast_start,
    owner_broadcast_send,
    owner_add_script_start,
    owner_receive_script_file,
    owner_receive_script_details,
    owner_add_app_start,
    owner_receive_app_name,
    owner_receive_app_price,
    owner_list_products,
    owner_delete_product,
    owner_confirm_delete,
    owner_add_account_start,
    owner_select_app_for_account,
    owner_receive_account_data,
    owner_add_balance_start,
    owner_receive_balance_user,
    owner_receive_balance_amount,
    owner_pending_txns,
    owner_list_users,
    cancel_owner_action,
    WAITING_SCRIPT_FILE,
    WAITING_SCRIPT_DETAILS,
    WAITING_APP_NAME,
    WAITING_APP_PRICE,
    WAITING_ACCOUNT_DATA,
    WAITING_BROADCAST,
    WAITING_ADD_BALANCE_USER,
    WAITING_ADD_BALANCE_AMOUNT
)
from handlers.tools import (
    menu_tools,
    tool_makeqr_start,
    tool_makeqr_generate,
    makeqr_command,
    tool_shorten_start,
    tool_shorten_process,
    shorten_command,
    tool_ssweb,
    ssweb_command,
    cancel_tool,
    WAITING_QR_TEXT,
    WAITING_SHORT_URL
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the bot"""
    
    print("""
╔══════════════════════════════════════════════╗
║                                              ║
║     🛒 SMART STORE BOT v1.0.0                ║
║     Powered by Pakasir.com Payment           ║
║                                              ║
╠══════════════════════════════════════════════╣
║  Starting bot...                             ║
╚══════════════════════════════════════════════╝
    """)
    
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📌 COMMAND HANDLERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("makeqr", makeqr_command))
    application.add_handler(CommandHandler("shorten", shorten_command))
    application.add_handler(CommandHandler("ssweb", ssweb_command))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💬 CONVERSATION HANDLERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Owner: Add Script
    add_script_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(owner_add_script_start, pattern="^owner_add_script$")],
        states={
            WAITING_SCRIPT_FILE: [
                MessageHandler(filters.Document.ALL, owner_receive_script_file),
                CommandHandler("cancel", cancel_owner_action)
            ],
            WAITING_SCRIPT_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, owner_receive_script_details),
                CommandHandler("cancel", cancel_owner_action)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_owner_action)],
        per_user=True,
        per_chat=True
    )
    application.add_handler(add_script_conv)
    
    # Owner: Add App
    add_app_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(owner_add_app_start, pattern="^owner_add_app$")],
        states={
            WAITING_APP_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, owner_receive_app_name),
                CommandHandler("cancel", cancel_owner_action)
            ],
            WAITING_APP_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, owner_receive_app_price),
                CommandHandler("cancel", cancel_owner_action)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_owner_action)],
        per_user=True,
        per_chat=True
    )
    application.add_handler(add_app_conv)
    
    # Owner: Add Account
    add_account_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(owner_select_app_for_account, pattern="^add_acc_to_")],
        states={
            WAITING_ACCOUNT_DATA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, owner_receive_account_data),
                CommandHandler("cancel", cancel_owner_action)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_owner_action)],
        per_user=True,
        per_chat=True
    )
    application.add_handler(add_account_conv)
    
    # Owner: Broadcast
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(owner_broadcast_start, pattern="^owner_broadcast$")],
        states={
            WAITING_BROADCAST: [
                MessageHandler(filters.ALL & ~filters.COMMAND, owner_broadcast_send),
                CommandHandler("cancel", cancel_owner_action)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_owner_action)],
        per_user=True,
        per_chat=True
    )
    application.add_handler(broadcast_conv)
    
    # Owner: Add Balance
    add_balance_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(owner_add_balance_start, pattern="^owner_add_balance$")],
        states={
            WAITING_ADD_BALANCE_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, owner_receive_balance_user),
                CommandHandler("cancel", cancel_owner_action)
            ],
            WAITING_ADD_BALANCE_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, owner_receive_balance_amount),
                CommandHandler("cancel", cancel_owner_action)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_owner_action)],
        per_user=True,
        per_chat=True
    )
    application.add_handler(add_balance_conv)
    
    # Tools: Make QR
    makeqr_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(tool_makeqr_start, pattern="^tool_makeqr$")],
        states={
            WAITING_QR_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, tool_makeqr_generate),
                CommandHandler("cancel", cancel_tool)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_tool)],
        per_user=True,
        per_chat=True
    )
    application.add_handler(makeqr_conv)
    
    # Tools: Shorten URL
    shorten_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(tool_shorten_start, pattern="^tool_shorten$")],
        states={
            WAITING_SHORT_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, tool_shorten_process),
                CommandHandler("cancel", cancel_tool)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_tool)],
        per_user=True,
        per_chat=True
    )
    application.add_handler(shorten_conv)
    
    # Deposit conversation - REMOVED
    # application.add_handler(deposit_conversation)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔘 CALLBACK HANDLERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Navigation
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_main$"))
    
    # Profile
    application.add_handler(CallbackQueryHandler(menu_profile, pattern="^menu_profile$"))
    application.add_handler(CallbackQueryHandler(menu_history, pattern="^menu_history$"))
    application.add_handler(CallbackQueryHandler(menu_contact_owner, pattern="^menu_contact_owner$"))
    
    # Shop
    application.add_handler(CallbackQueryHandler(menu_shop, pattern="^menu_shop$"))
    # application.add_handler(CallbackQueryHandler(shop_scripts, pattern="^shop_scripts$"))  # Script Bot feature removed
    application.add_handler(CallbackQueryHandler(shop_apps, pattern="^shop_apps$"))
    application.add_handler(CallbackQueryHandler(shop_panel, pattern="^shop_panel$"))
    application.add_handler(CallbackQueryHandler(shop_admin_panel, pattern="^shop_admin_panel$"))
    application.add_handler(CallbackQueryHandler(buy_product, pattern="^buy_(script|app)_"))
    application.add_handler(CallbackQueryHandler(pay_with_balance, pattern="^pay_balance_"))
    application.add_handler(CallbackQueryHandler(pay_with_qris, pattern="^pay_qris_"))
    application.add_handler(CallbackQueryHandler(check_payment_callback, pattern="^check_payment_"))
    application.add_handler(CallbackQueryHandler(cancel_payment_callback, pattern="^cancel_payment_"))
    application.add_handler(CallbackQueryHandler(sold_out_callback, pattern="^sold_out$"))
    
    # Deposit - REMOVED (QRIS deposit via Pakasir.com disabled)
    # application.add_handler(CallbackQueryHandler(menu_deposit, pattern="^menu_deposit$"))
    # application.add_handler(CallbackQueryHandler(process_deposit, pattern="^deposit_\\d+$"))
    # application.add_handler(CallbackQueryHandler(check_deposit_callback, pattern="^check_deposit_"))
    # application.add_handler(CallbackQueryHandler(cancel_deposit_callback, pattern="^cancel_deposit_"))
    
    # Owner
    application.add_handler(CallbackQueryHandler(menu_owner, pattern="^menu_owner$"))
    application.add_handler(CallbackQueryHandler(owner_toggle_panel, pattern="^owner_toggle_panel$"))
    application.add_handler(CallbackQueryHandler(owner_list_products, pattern="^owner_list_products$"))
    application.add_handler(CallbackQueryHandler(owner_delete_product, pattern="^owner_delete_product$"))
    application.add_handler(CallbackQueryHandler(owner_confirm_delete, pattern="^delete_product_"))
    application.add_handler(CallbackQueryHandler(owner_add_account_start, pattern="^owner_add_account$"))
    application.add_handler(CallbackQueryHandler(owner_pending_txns, pattern="^owner_pending_txns$"))
    application.add_handler(CallbackQueryHandler(owner_list_users, pattern="^owner_list_users$"))
    
    # Tools
    application.add_handler(CallbackQueryHandler(menu_tools, pattern="^menu_tools$"))
    application.add_handler(CallbackQueryHandler(tool_ssweb, pattern="^tool_ssweb$"))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🚀 RUN BOT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def post_init(application):
        """Post initialization tasks"""
        # Initialize database
        await db.init()
        logger.info("Database initialized")
        
        # Set default settings
        panel_status = await db.get_setting('panel_open')
        if panel_status is None:
            await db.set_setting('panel_open', True)
        
        logger.info("Bot is ready!")
        print(f"\n✅ Bot started successfully!")
        print(f"📱 Bot: @{(await application.bot.get_me()).username}")
        print(f"👑 Owner ID: {config.OWNER_ID}\n")
    
    application.post_init = post_init
    
    # Run polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
