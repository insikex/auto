"""
VIP Premium Bot - Clean & Private Edition
==========================================

功能:
- 隐私保护（管理员信息隐藏）
- 简洁整齐的响应
- 支持测试网进行测试
- 更好的用户界面/用户体验

设置:
1. 从 @BotFather 获取 BOT_TOKEN
2. 从 @CryptoBot -> Crypto Pay -> My Apps 获取 CRYPTOPAY_TOKEN
3. 设置 USE_TESTNET = True 进行测试（使用 @CryptoTestnetBot）
4. 设置 USE_TESTNET = False 用于生产环境
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
# 主要配置
# ══════════════════════════════════════════════════════════════

# 从 @BotFather 获取的 Bot Token
BOT_TOKEN = '7829954744:AAEJgjBWRTdaJmh7gsnLlE_cNo1TXl0i6EU'

# CryptoPay Token
# 测试网：从 @CryptoTestnetBot -> Crypto Pay -> My Apps 获取
# 主网：从 @CryptoBot -> Crypto Pay -> My Apps 获取
CRYPTOPAY_TOKEN = '519883:AAJsQ1LRbcYeeGw0RivIRdACWjpZGW8VGfL'

# ⚠️ 测试网模式 - 设置 True 进行测试，设置 False 用于生产环境
USE_TESTNET = False

# 高级频道链接（私密邀请链接）
PREMIUM_LINK = 'https://t.me/+V2JE9sIz35ZmZGNl'

# 管理员ID（仅用于内部通知，不向用户显示）
ADMIN_ID = 6683929810

# 定价
ORIGINAL_PRICE = 300
DISCOUNT_PERCENT = 50
FINAL_PRICE = ORIGINAL_PRICE * (100 - DISCOUNT_PERCENT) / 100

# 数据库文件
PREMIUM_DB = 'premium_users.json'
INVOICES_DB = 'pending_invoices.json'

# ══════════════════════════════════════════════════════════════
# 初始化
# ══════════════════════════════════════════════════════════════

bot = telebot.TeleBot(BOT_TOKEN)
NETWORK = Networks.TEST_NET if USE_TESTNET else Networks.MAIN_NET

# ══════════════════════════════════════════════════════════════
# 数据库辅助函数
# ══════════════════════════════════════════════════════════════

def load_json(file):
    """从JSON文件加载数据"""
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(file, data):
    """保存数据到JSON文件"""
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# 高级用户
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

# 待处理发票
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
# CRYPTOPAY 函数
# ══════════════════════════════════════════════════════════════

async def create_invoice(user_id):
    """创建付款发票"""
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
            allow_anonymous=True  # 用户隐私
        )
        return invoice
    finally:
        await crypto.close()

async def check_invoice(invoice_id):
    """检查发票状态"""
    crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=NETWORK)
    
    try:
        invoices = await crypto.get_invoices(invoice_ids=[invoice_id])
        return invoices[0] if invoices else None
    finally:
        await crypto.close()

async def get_app_info():
    """获取CryptoPay应用信息"""
    crypto = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=NETWORK)
    
    try:
        return await crypto.get_me()
    finally:
        await crypto.close()

def run_async(coro):
    """异步运行助手"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        raise e

# ══════════════════════════════════════════════════════════════
# 消息模板（简洁整齐）
# ══════════════════════════════════════════════════════════════

def msg_welcome():
    """新用户欢迎消息"""
    mode = "🧪 测试网" if USE_TESTNET else "🔐 安全"
    return f"""
🎬 *VIP高级机器人* {mode}

访问 *10,000+ 高质量高级视频*！

✨ *优势：*
• 终身独家访问权限
• 每日更新 & 100%隐私保护

💰 *价格：* ~~${ORIGINAL_PRICE}~~ → *${int(FINAL_PRICE)}* (-{DISCOUNT_PERCENT}%)
"""

def msg_welcome_premium():
    """高级会员消息"""
    return """
🎉 *欢迎回来，VIP！*

状态：✅ *终身高级会员*

点击按钮访问内容 👇
"""

def msg_invoice(invoice_id):
    """付款发票消息"""
    mode = "🧪 模式：测试网" if USE_TESTNET else ""
    return f"""
💳 *付款发票*

📦 VIP终身高级会员
💵 总计：*${int(FINAL_PRICE)}*
🔢 ID：`{invoice_id}`
{mode}

*付款方式：*
1️⃣ 点击"立即支付"
2️⃣ 选择加密货币并支付
3️⃣ 支付后点击"验证"

⏰ 有效期60分钟
"""

def msg_success(invoice_id):
    """付款成功消息"""
    return f"""
✅ *付款成功！*

🎉 恭喜！您现在是 *VIP会员*
⏰ 期限：*终身*

点击按钮访问高级内容 👇
"""

def msg_pending(invoice_id):
    """等待付款消息"""
    return f"""
⏳ *等待付款*

🔢 发票：`{invoice_id}`
📊 状态：未付款

请先完成付款。
"""

def msg_expired():
    """发票过期消息"""
    return """
⌛ *发票已过期*

请创建新发票继续。
"""

def msg_error():
    """错误消息"""
    return """
❌ *发生错误*

请重试或联系客服。
"""

def msg_cancelled():
    """取消消息"""
    return """
🚫 *已取消*

输入 /start 重新开始。
"""

def msg_status_free():
    """免费用户状态"""
    return f"""
📊 *会员状态*

🔓 状态：*免费*

升级到高级会员：
• 10,000+ 视频
• 终身访问权限
• 仅需 *${int(FINAL_PRICE)}*
"""

def msg_status_premium(data):
    """高级用户状态"""
    date = data['activated'][:10]
    return f"""
📊 *会员状态*

✅ 状态：*高级会员*
📅 开通日期：{date}
⏰ 期限：*终身*
"""

def msg_help():
    """帮助消息"""
    return """
📚 *帮助*

/start - 主菜单
/status - 查看会员状态
/help - 帮助

*购买方式：*
1. 点击"购买高级会员"
2. 使用加密货币支付
3. 验证付款
4. 访问高级内容！

*支付方式：*
USDT • TON • BTC • ETH • 等
"""

# ══════════════════════════════════════════════════════════════
# 键盘按钮
# ══════════════════════════════════════════════════════════════

def kb_main():
    """主菜单键盘"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💎 购买高级会员", callback_data='buy'),
        types.InlineKeyboardButton("📊 状态", callback_data='status'),
        types.InlineKeyboardButton("❓ 帮助", callback_data='help')
    )
    return kb

def kb_premium():
    """高级用户键盘"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🔓 访问高级内容", url=PREMIUM_LINK),
        types.InlineKeyboardButton("📊 状态", callback_data='status')
    )
    return kb

def kb_invoice(invoice_url, invoice_id):
    """发票键盘"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💰 立即支付", url=invoice_url),
        types.InlineKeyboardButton("✅ 验证", callback_data=f'verify_{invoice_id}'),
        types.InlineKeyboardButton("❌ 取消", callback_data='cancel')
    )
    return kb

def kb_pending(invoice_url, invoice_id):
    """等待付款键盘"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💰 支付", url=invoice_url),
        types.InlineKeyboardButton("🔄 重新检查", callback_data=f'verify_{invoice_id}')
    )
    return kb

def kb_success():
    """成功键盘"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔓 访问高级内容", url=PREMIUM_LINK))
    return kb

def kb_retry():
    """重试键盘"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔄 重试", callback_data='buy'),
        types.InlineKeyboardButton("🏠 菜单", callback_data='menu')
    )
    return kb

def kb_back():
    """返回键盘"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🏠 主菜单", callback_data='menu'))
    return kb

def kb_status_free():
    """免费状态键盘"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💎 升级高级会员", callback_data='buy'),
        types.InlineKeyboardButton("🏠 菜单", callback_data='menu')
    )
    return kb

# ══════════════════════════════════════════════════════════════
# 机器人处理程序
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def cmd_start(message):
    """处理 /start 命令"""
    user_id = message.from_user.id
    args = message.text.split()
    
    # 深度链接处理
    if len(args) > 1:
        if args[1] == 'paid' or args[1].startswith('paid_'):
            pending = get_invoice(user_id)
            if pending:
                verify_payment(message.chat.id, pending['id'], user_id)
                return
    
    # 检查高级会员状态
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
    """处理 /status 命令"""
    show_status(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['help'])
def cmd_help(message):
    """处理 /help 命令"""
    bot.send_message(
        message.chat.id,
        msg_help(),
        parse_mode='Markdown',
        reply_markup=kb_back()
    )

# ══════════════════════════════════════════════════════════════
# 回调处理程序
# ══════════════════════════════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == 'menu')
def cb_menu(call):
    """返回菜单"""
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
    """处理购买高级会员"""
    user_id = call.from_user.id
    
    if is_premium(user_id):
        bot.answer_callback_query(call.id, "✅ 您已经是高级会员！", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "⏳ 正在创建发票...")
    
    try:
        bot.edit_message_text(
            "⏳ *正在创建发票...*",
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
    """验证付款"""
    invoice_id = call.data.replace('verify_', '')
    user_id = call.from_user.id
    
    bot.answer_callback_query(call.id, "🔍 正在检查付款...")
    verify_payment(call.message.chat.id, invoice_id, user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == 'status')
def cb_status(call):
    """显示状态"""
    show_status(call.message.chat.id, call.from_user.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == 'help')
def cb_help(call):
    """显示帮助"""
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
    """取消付款"""
    bot.edit_message_text(
        msg_cancelled(),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=kb_back()
    )
    bot.answer_callback_query(call.id)

# ══════════════════════════════════════════════════════════════
# 辅助函数
# ══════════════════════════════════════════════════════════════

def verify_payment(chat_id, invoice_id, user_id, msg_id=None):
    """验证付款状态"""
    try:
        invoice = run_async(check_invoice(int(invoice_id)))
        
        if not invoice:
            text = msg_error()
            kb = kb_retry()
        elif invoice.status == 'paid':
            # 付款成功！
            if not is_premium(user_id):
                add_premium(user_id, invoice_id)
            remove_invoice(user_id)
            
            text = msg_success(invoice_id)
            kb = kb_success()
            
            # 通知管理员（内部，不暴露用户信息）
            notify_admin(user_id, invoice_id)
            
        elif invoice.status == 'active':
            text = msg_pending(invoice_id)
            kb = kb_pending(invoice.bot_invoice_url, invoice_id)
        else:
            # 已过期或已取消
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
    """显示会员状态"""
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
    """通知管理员新付款（私密，不向用户公开用户数据）"""
    try:
        # 仅内部通知
        text = f"""
🔔 *新付款*

💰 ${int(FINAL_PRICE)}
🔢 发票：`{invoice_id}`
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        bot.send_message(ADMIN_ID, text, parse_mode='Markdown')
    except:
        pass

# ══════════════════════════════════════════════════════════════
# 管理员命令（对普通用户隐藏）
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    """管理员面板"""
    if message.from_user.id != ADMIN_ID:
        return
    
    users = load_json(PREMIUM_DB)
    total = len(users)
    revenue = sum(u.get('amount', 0) for u in users.values())
    mode = "🧪 测试网" if USE_TESTNET else "🔐 主网"
    
    text = f"""
🔧 *管理员面板*

{mode}
👥 高级会员：{total}
💰 收入：${revenue}
💵 价格：${int(FINAL_PRICE)}

/testapi - 测试CryptoPay
/broadcast <消息> - 广播
"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['testapi'])
def cmd_testapi(message):
    """测试CryptoPay API"""
    if message.from_user.id != ADMIN_ID:
        return
    
    bot.reply_to(message, "🔄 正在测试API...")
    
    try:
        info = run_async(get_app_info())
        mode = "测试网" if USE_TESTNET else "主网"
        text = f"""
✅ *API已连接*

📱 应用：{info.name}
🌐 网络：{mode}
"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ 错误：{str(e)[:100]}")

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    """向所有高级用户广播消息"""
    if message.from_user.id != ADMIN_ID:
        return
    
    text = message.text.replace('/broadcast', '').strip()
    if not text:
        bot.reply_to(message, "用法：/broadcast <消息>")
        return
    
    users = load_json(PREMIUM_DB)
    sent = 0
    
    for uid in users.keys():
        try:
            bot.send_message(int(uid), f"📢 *公告*\n\n{text}", parse_mode='Markdown')
            sent += 1
        except:
            pass
    
    bot.reply_to(message, f"✅ 广播已发送给 {sent}/{len(users)} 用户")

# ══════════════════════════════════════════════════════════════
# 默认处理程序
# ══════════════════════════════════════════════════════════════

@bot.message_handler(func=lambda m: True)
def default_handler(message):
    """处理未知消息"""
    bot.reply_to(
        message,
        "输入 /start 开始 👆",
        parse_mode='Markdown'
    )

# ══════════════════════════════════════════════════════════════
# 主程序
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    mode = "🧪 测试网模式" if USE_TESTNET else "🔐 生产模式"
    
    print("═" * 40)
    print("🤖 VIP高级机器人")
    print("═" * 40)
    print(f"模式：{mode}")
    print(f"价格：${int(FINAL_PRICE)}（原价 ${ORIGINAL_PRICE}）")
    print("═" * 40)
    print("机器人运行中...")
    print("═" * 40)
    
    bot.infinity_polling()
