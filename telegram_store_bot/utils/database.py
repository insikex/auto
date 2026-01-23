"""
📦 Database Handler
SQLite Database for Store Bot
"""

import aiosqlite
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import config

class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def init(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    balance INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products table (scripts, apps)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price INTEGER NOT NULL,
                    file_id TEXT,
                    stock INTEGER DEFAULT -1,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Product accounts (for app premium with stock)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS product_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    account_data TEXT NOT NULL,
                    is_sold INTEGER DEFAULT 0,
                    sold_to INTEGER,
                    sold_at TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            
            # Transactions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    product_type TEXT,
                    product_id INTEGER,
                    product_name TEXT,
                    amount INTEGER NOT NULL,
                    total_payment INTEGER,
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT DEFAULT 'qris',
                    qr_string TEXT,
                    expired_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    extra_data TEXT
                )
            ''')
            
            # Settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 👤 USER OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def add_user(self, user_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None) -> bool:
        """Add or update user"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id FROM users WHERE id = ?", (user_id,)
            )
            exists = await cursor.fetchone()
            
            if exists:
                await db.execute('''
                    UPDATE users SET username = ?, first_name = ?, 
                    last_name = ?, updated_at = ? WHERE id = ?
                ''', (username, first_name, last_name, datetime.now(), user_id))
                await db.commit()
                return False  # Not new user
            else:
                await db.execute('''
                    INSERT INTO users (id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                await db.commit()
                return True  # New user
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_user_balance(self, user_id: int) -> int:
        """Get user balance"""
        user = await self.get_user(user_id)
        return user['balance'] if user else 0
    
    async def update_balance(self, user_id: int, amount: int) -> int:
        """Add amount to user balance (can be negative)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users SET balance = balance + ?, updated_at = ?
                WHERE id = ?
            ''', (amount, datetime.now(), user_id))
            await db.commit()
            return await self.get_user_balance(user_id)
    
    async def set_balance(self, user_id: int, amount: int):
        """Set user balance to specific amount"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users SET balance = ?, updated_at = ?
                WHERE id = ?
            ''', (amount, datetime.now(), user_id))
            await db.commit()
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_count(self) -> int:
        """Get total user count"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📦 PRODUCT OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def add_product(self, product_type: str, name: str, price: int,
                         description: str = None, file_id: str = None) -> int:
        """Add new product"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO products (type, name, description, price, file_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_type, name, description, price, file_id))
            await db.commit()
            return cursor.lastrowid
    
    async def get_products(self, product_type: str = None) -> List[Dict]:
        """Get products, optionally filtered by type"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if product_type:
                cursor = await db.execute(
                    "SELECT * FROM products WHERE type = ? AND is_active = 1",
                    (product_type,)
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM products WHERE is_active = 1"
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_product(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def delete_product(self, product_id: int):
        """Delete product"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE products SET is_active = 0 WHERE id = ?", (product_id,)
            )
            await db.commit()
    
    async def add_product_account(self, product_id: int, account_data: str):
        """Add account to product stock"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO product_accounts (product_id, account_data)
                VALUES (?, ?)
            ''', (product_id, account_data))
            await db.commit()
    
    async def get_product_stock(self, product_id: int) -> int:
        """Get available stock count for product"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM product_accounts 
                WHERE product_id = ? AND is_sold = 0
            ''', (product_id,))
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    async def sell_product_account(self, product_id: int, user_id: int) -> Optional[str]:
        """Sell one account from product stock"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get available account
            cursor = await db.execute('''
                SELECT id, account_data FROM product_accounts 
                WHERE product_id = ? AND is_sold = 0 LIMIT 1
            ''', (product_id,))
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            account_id, account_data = row
            
            # Mark as sold
            await db.execute('''
                UPDATE product_accounts SET is_sold = 1, sold_to = ?, sold_at = ?
                WHERE id = ?
            ''', (user_id, datetime.now(), account_id))
            await db.commit()
            
            return account_data
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💳 TRANSACTION OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def create_transaction(self, order_id: str, user_id: int, amount: int,
                                 product_type: str = None, product_id: int = None,
                                 product_name: str = None, total_payment: int = None,
                                 qr_string: str = None, expired_at: datetime = None,
                                 extra_data: dict = None) -> int:
        """Create new transaction"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO transactions 
                (order_id, user_id, product_type, product_id, product_name, 
                 amount, total_payment, qr_string, expired_at, extra_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, user_id, product_type, product_id, product_name,
                  amount, total_payment or amount, qr_string, expired_at,
                  json.dumps(extra_data) if extra_data else None))
            await db.commit()
            return cursor.lastrowid
    
    async def get_transaction(self, order_id: str) -> Optional[Dict]:
        """Get transaction by order ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM transactions WHERE order_id = ?", (order_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_transaction_status(self, order_id: str, status: str):
        """Update transaction status"""
        async with aiosqlite.connect(self.db_path) as db:
            if status == 'completed':
                await db.execute('''
                    UPDATE transactions SET status = ?, completed_at = ?
                    WHERE order_id = ?
                ''', (status, datetime.now(), order_id))
            else:
                await db.execute(
                    "UPDATE transactions SET status = ? WHERE order_id = ?",
                    (status, order_id)
                )
            await db.commit()
    
    async def get_pending_transactions(self) -> List[Dict]:
        """Get all pending transactions"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM transactions WHERE status = 'pending'"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_transactions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's transaction history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM transactions WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ⚙️ SETTINGS OPERATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(value) if not isinstance(value, str) else value, 
                  datetime.now()))
            await db.commit()
    
    async def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except:
                    return row[0]
            return default
    
    async def is_panel_open(self) -> bool:
        """Check if panel is open for purchase"""
        return await self.get_setting('panel_open', True)
    
    async def toggle_panel(self) -> bool:
        """Toggle panel open/close"""
        current = await self.is_panel_open()
        await self.set_setting('panel_open', not current)
        return not current


# Global database instance
db = Database()
