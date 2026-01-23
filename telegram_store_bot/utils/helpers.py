"""
🛠️ Helper Utilities
Common functions for the bot
"""

from datetime import datetime
from typing import Optional
import config

def format_currency(amount: int) -> str:
    """Format amount to Indonesian Rupiah"""
    return f"Rp {amount:,.0f}".replace(",", ".")


def get_uptime(start_time: datetime) -> str:
    """Get bot uptime as formatted string"""
    delta = datetime.now() - start_time
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def get_wib_time() -> str:
    """Get current time in WIB (Indonesia Western Time)"""
    from datetime import timezone, timedelta
    wib = timezone(timedelta(hours=7))
    now = datetime.now(wib)
    return now.strftime("%d %B %Y, %H:%M:%S WIB")


def get_wib_datetime() -> datetime:
    """Get current datetime in WIB"""
    from datetime import timezone, timedelta
    wib = timezone(timedelta(hours=7))
    return datetime.now(wib)


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def build_menu_text(title: str, items: dict, footer: str = None) -> str:
    """Build formatted menu text"""
    lines = [f"<b>{title}</b>", ""]
    
    for key, value in items.items():
        lines.append(f"<b>{key}:</b> {value}")
    
    if footer:
        lines.extend(["", footer])
    
    return "\n".join(lines)


def format_user_info(user) -> str:
    """Format user info from telegram User object"""
    name = user.first_name or ""
    if user.last_name:
        name += f" {user.last_name}"
    
    username = f"@{user.username}" if user.username else "-"
    
    return f"""<b>👤 Info User</b>
├ <b>Nama:</b> {escape_html(name)}
├ <b>Username:</b> {username}
└ <b>ID:</b> <code>{user.id}</code>"""


def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a text-based progress bar"""
    if total == 0:
        return "░" * length
    
    filled = int((current / total) * length)
    empty = length - filled
    
    return "█" * filled + "░" * empty


def format_product_card(product: dict, show_stock: bool = False) -> str:
    """Format product info as card"""
    emoji = config.EMOJI
    
    text = f"""
╔══════════════════════════╗
║  {emoji['product']} <b>{escape_html(product['name'])}</b>
╠══════════════════════════╣
║  {emoji['money']} Harga: <b>{format_currency(product['price'])}</b>"""
    
    if product.get('description'):
        text += f"\n║  ℹ️ {escape_html(truncate_text(product['description'], 50))}"
    
    if show_stock:
        stock = product.get('stock', 0)
        if stock == -1:
            stock_text = "∞ Unlimited"
        else:
            stock_text = f"{stock} tersedia"
        text += f"\n║  📦 Stok: {stock_text}"
    
    text += "\n╚══════════════════════════╝"
    
    return text


def format_transaction_card(txn: dict) -> str:
    """Format transaction info as card"""
    emoji = config.EMOJI
    
    status_emoji = {
        'pending': '⏳',
        'completed': '✅',
        'expired': '⌛',
        'cancelled': '❌',
        'failed': '💥'
    }
    
    status_text = status_emoji.get(txn.get('status', 'pending'), '❓')
    
    return f"""
📋 <b>Detail Transaksi</b>
┌─────────────────────────
│ 🆔 Order ID: <code>{txn.get('order_id', '-')}</code>
│ 📦 Produk: {escape_html(txn.get('product_name', '-'))}
│ 💰 Jumlah: {format_currency(txn.get('amount', 0))}
│ 💳 Total Bayar: {format_currency(txn.get('total_payment', 0))}
│ {status_text} Status: <b>{txn.get('status', 'Unknown').upper()}</b>
└─────────────────────────"""


def format_stats_card(stats: dict) -> str:
    """Format statistics as card"""
    return f"""
📊 <b>Statistik Bot</b>
╔══════════════════════════╗
║  👥 Total Users: <b>{stats.get('total_users', 0)}</b>
║  📦 Total Produk: <b>{stats.get('total_products', 0)}</b>
║  💰 Total Transaksi: <b>{stats.get('total_transactions', 0)}</b>
║  ⏱️ Uptime: <b>{stats.get('uptime', '-')}</b>
╚══════════════════════════╝"""
