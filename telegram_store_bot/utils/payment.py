"""
💳 Pakasir Payment Gateway Integration
QRIS Payment Handler for Telegram Bot
"""

import aiohttp
import asyncio
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import config

class PakasirPayment:
    """
    Pakasir.com Payment Gateway Handler
    Documentation: https://pakasir.com/p/docs
    """
    
    def __init__(self):
        self.base_url = config.PAKASIR_BASE_URL
        self.project = config.PAKASIR_PROJECT
        self.api_key = config.PAKASIR_API_KEY
    
    async def create_qris_transaction(self, order_id: str, amount: int) -> Optional[Dict]:
        """
        Create QRIS payment transaction
        
        Args:
            order_id: Unique order ID
            amount: Payment amount in IDR
        
        Returns:
            Dict with payment details or None if failed
        """
        url = f"{self.base_url}/api/transactioncreate/qris"
        
        payload = {
            "project": self.project,
            "order_id": order_id,
            "amount": amount,
            "api_key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'payment' in data:
                            payment = data['payment']
                            return {
                                'success': True,
                                'order_id': payment.get('order_id'),
                                'amount': payment.get('amount'),
                                'fee': payment.get('fee', 0),
                                'total_payment': payment.get('total_payment'),
                                'payment_method': payment.get('payment_method'),
                                'qr_string': payment.get('payment_number'),
                                'expired_at': payment.get('expired_at')
                            }
                    
                    return {
                        'success': False,
                        'error': f"HTTP {response.status}"
                    }
                    
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def check_transaction_status(self, order_id: str, amount: int) -> Optional[Dict]:
        """
        Check transaction payment status
        
        Args:
            order_id: Order ID to check
            amount: Transaction amount
        
        Returns:
            Dict with transaction status
        """
        url = f"{self.base_url}/api/transactiondetail"
        
        params = {
            "project": self.project,
            "order_id": order_id,
            "amount": amount,
            "api_key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'transaction' in data:
                            txn = data['transaction']
                            return {
                                'success': True,
                                'order_id': txn.get('order_id'),
                                'amount': txn.get('amount'),
                                'status': txn.get('status'),
                                'payment_method': txn.get('payment_method'),
                                'completed_at': txn.get('completed_at')
                            }
                    
                    return {'success': False, 'status': 'not_found'}
                    
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def cancel_transaction(self, order_id: str, amount: int) -> bool:
        """
        Cancel a pending transaction
        
        Args:
            order_id: Order ID to cancel
            amount: Transaction amount
        
        Returns:
            True if cancelled successfully
        """
        url = f"{self.base_url}/api/transactioncancel"
        
        payload = {
            "project": self.project,
            "order_id": order_id,
            "amount": amount,
            "api_key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=15) as response:
                    return response.status == 200
                    
        except Exception:
            return False
    
    def generate_qr_image(self, qr_string: str) -> BytesIO:
        """
        Generate QR code image from QR string
        
        Args:
            qr_string: QRIS string from payment gateway
        
        Returns:
            BytesIO containing PNG image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    def get_payment_url(self, amount: int, order_id: str, qris_only: bool = True) -> str:
        """
        Get direct payment URL (redirect method)
        
        Args:
            amount: Payment amount
            order_id: Order ID
            qris_only: If True, only show QRIS option
        
        Returns:
            Payment URL string
        """
        url = f"{self.base_url}/pay/{self.project}/{amount}?order_id={order_id}"
        if qris_only:
            url += "&qris_only=1"
        return url


def format_currency(amount: int) -> str:
    """Format amount to Indonesian Rupiah"""
    return f"Rp {amount:,.0f}".replace(",", ".")


def generate_order_id(prefix: str = "TRX") -> str:
    """Generate unique order ID"""
    import random
    import string
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{timestamp}{random_str}"


def parse_expired_time(expired_str: str) -> Optional[datetime]:
    """Parse expired time from ISO format"""
    try:
        # Handle different ISO formats
        if 'Z' in expired_str:
            expired_str = expired_str.replace('Z', '+00:00')
        return datetime.fromisoformat(expired_str.replace('Z', '+00:00'))
    except:
        return None


def get_remaining_time(expired_at: datetime) -> Tuple[int, int]:
    """Get remaining minutes and seconds"""
    now = datetime.now(expired_at.tzinfo) if expired_at.tzinfo else datetime.now()
    diff = expired_at - now
    
    if diff.total_seconds() <= 0:
        return 0, 0
    
    minutes = int(diff.total_seconds() // 60)
    seconds = int(diff.total_seconds() % 60)
    return minutes, seconds


# Global payment instance
payment = PakasirPayment()
