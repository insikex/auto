# 📋 Dokumentasi Fitur Pembayaran dan Pengiriman Otomatis

## 📌 Ringkasan Perubahan

Fitur-fitur berikut telah **DIHAPUS** dari bot:
1. ❌ **Deposit Saldo via QRIS (Pakasir.com)** - Fitur deposit saldo telah dinonaktifkan
2. ❌ **Beli Script dengan Pengiriman Otomatis** - Fitur pembelian script bot telah dinonaktifkan

---

## ✅ Fitur yang Masih Aktif: Apps Premium

### 1. Apakah User Dapat Membayar Secara Otomatis?

**YA, user dapat membayar secara otomatis** saat membeli produk Apps Premium.

#### Alur Pembayaran Otomatis:

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALUR PEMBAYARAN QRIS                        │
├─────────────────────────────────────────────────────────────────┤
│  1. User memilih produk Apps Premium dari menu                  │
│  2. User klik "💳 Bayar dengan QRIS"                            │
│  3. Bot membuat transaksi via Pakasir.com Payment Gateway       │
│  4. Bot menampilkan QR Code QRIS kepada user                    │
│  5. User scan dan bayar menggunakan e-wallet/m-banking          │
│  6. Bot otomatis mengecek status pembayaran setiap 15 detik     │
│  7. Jika pembayaran terdeteksi → Produk langsung dikirim        │
└─────────────────────────────────────────────────────────────────┘
```

#### Metode Pembayaran yang Didukung:
- **QRIS** - Dapat dibayar menggunakan:
  - GoPay
  - OVO
  - DANA
  - ShopeePay
  - LinkAja
  - Bank Mobile (BCA, BNI, BRI, Mandiri, dll)
  - Semua e-wallet yang mendukung QRIS

#### Waktu Kadaluarsa Pembayaran:
- **15 menit** dari waktu pembuatan transaksi
- Jika tidak dibayar dalam waktu tersebut, transaksi otomatis expired

---

### 2. Apakah Bot Akan Mengirim Data Secara Otomatis?

**YA, bot akan mengirim data secara otomatis** kepada user yang telah membayar.

#### Alur Pengiriman Otomatis:

```
┌─────────────────────────────────────────────────────────────────┐
│                  ALUR PENGIRIMAN OTOMATIS                       │
├─────────────────────────────────────────────────────────────────┤
│  SETELAH PEMBAYARAN BERHASIL:                                   │
│                                                                 │
│  1. Bot menerima konfirmasi pembayaran dari Pakasir.com         │
│  2. Bot update status transaksi menjadi "completed"             │
│  3. Bot mengirim notifikasi "✅ Pembayaran Berhasil!"           │
│  4. Bot mengambil data akun dari database (stok)                │
│  5. Bot mengirim data akun ke user via pesan Telegram           │
│  6. Bot menandai akun sebagai "sold" di database                │
│  7. Bot mengirim notifikasi pembelian ke Owner                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Format Pesan Pengiriman Data Akun:

```
✅ PEMBELIAN BERHASIL!

📱 Produk: [Nama App Premium]
🆔 Order ID: QRS20260123120000ABCDEF

━━━━━━━━━━━━━━━━━━━━
📋 DATA AKUN:
[username:password atau data akun lainnya]
━━━━━━━━━━━━━━━━━━━━

⚠️ Segera ganti password!
Terima kasih sudah berbelanja! 🙏
```

---

## 📊 Detail Teknis

### Database Tables yang Digunakan:

| Table | Fungsi |
|-------|--------|
| `users` | Menyimpan data user dan saldo |
| `products` | Menyimpan daftar produk (apps premium) |
| `product_accounts` | Menyimpan stok akun untuk setiap produk |
| `transactions` | Menyimpan riwayat transaksi |
| `settings` | Menyimpan konfigurasi bot |

### Payment Gateway:

| Setting | Value |
|---------|-------|
| Provider | Pakasir.com |
| Method | QRIS (QR Indonesian Standard) |
| Timeout | 15 menit |
| Check Interval | 15 detik |
| Max Checks | 60 kali (15 menit / 15 detik) |

### Background Task - Payment Checker:

```python
async def check_payment_loop():
    """
    Background task yang berjalan setelah QR dibuat:
    - Mengecek status pembayaran setiap 15 detik
    - Jika terdeteksi paid → kirim produk otomatis
    - Jika 15 menit tidak dibayar → mark as expired
    """
```

---

## 🔄 Respons Bot

### Saat User Membeli Produk:

1. **Menampilkan Detail Produk**
   ```
   ╔══════════════════════════╗
   ║  📦 [Nama Produk]
   ╠══════════════════════════╣
   ║  💰 Harga: Rp XX.XXX
   ║  📦 Stok: X tersedia
   ╚══════════════════════════╝
   
   💰 Saldo Anda: Rp XX.XXX
   ⚠️ Saldo tidak cukup. Silakan bayar langsung dengan QRIS.
   ```

2. **Menampilkan QR Code Pembayaran**
   ```
   💳 PEMBAYARAN QRIS
   
   🆔 Order ID: QRSXXXXXXXXXXXX
   📦 Produk: [Nama Produk]
   💰 Harga: Rp XX.XXX
   💸 Fee: Rp XXX
   ━━━━━━━━━━━━━━━━━━━━
   💵 Total Bayar: Rp XX.XXX
   
   ⏰ Berlaku 15 menit
   📱 Scan QR dengan e-wallet/m-banking
   
   ⚠️ Bayar sesuai nominal!
   
   [Tombol: 🔄 Cek Status Pembayaran]
   [Tombol: ❌ Batalkan]
   ```

3. **Setelah Pembayaran Berhasil**
   ```
   ✅ Pembayaran Berhasil!
   
   Order ID: QRSXXXXXXXXXXXX
   ```
   
   Diikuti dengan:
   ```
   ✅ PEMBELIAN BERHASIL!
   
   📱 Produk: [Nama Produk]
   🆔 Order ID: QRSXXXXXXXXXXXX
   
   ━━━━━━━━━━━━━━━━━━━━
   📋 DATA AKUN:
   [Data akun yang dibeli]
   ━━━━━━━━━━━━━━━━━━━━
   
   ⚠️ Segera ganti password!
   Terima kasih sudah berbelanja! 🙏
   ```

4. **Jika Pembayaran Expired**
   ```
   ⏰ Pembayaran Expired
   
   Order ID: QRSXXXXXXXXXXXX
   
   Silakan buat transaksi baru.
   ```

5. **Jika Stok Habis**
   ```
   ❌ Maaf, stok habis. Silakan hubungi owner untuk refund.
   ```

---

## 📱 Menu Bot yang Tersedia

### Menu Utama:
- 🛍️ Menu Layanan
- 🛠️ Menu Tools
- 👤 Profil Saya
- 📢 Channel Info
- 💬 Grup Diskusi
- 📞 Hubungi Owner
- 👑 Menu Owner (khusus owner)

### Menu Layanan (Aktif):
- 📱 Apps Premium (dengan pembayaran dan pengiriman otomatis)
- 🖥️ Buy Panel
- 👑 Admin Panel

### Fitur yang Dihapus:
- ~~💰 Deposit Saldo~~ (DIHAPUS)
- ~~📁 Script Bot~~ (DIHAPUS)

---

## 🔐 Keamanan

1. **Validasi Pembayaran**: Pembayaran diverifikasi langsung dari Pakasir.com
2. **Stok Akun**: Akun yang terjual ditandai sebagai "sold" dan tidak dapat dijual ulang
3. **Transaction ID**: Setiap transaksi memiliki ID unik untuk tracking
4. **Owner Notification**: Owner mendapat notifikasi setiap ada pembelian

---

## 📝 Catatan Penting

1. **Pembayaran hanya via QRIS** - User harus membayar langsung saat membeli, tidak bisa deposit terlebih dahulu
2. **Pengiriman instan** - Data akun dikirim otomatis dalam hitungan detik setelah pembayaran terverifikasi
3. **Stok terbatas** - Pastikan ada stok akun yang tersedia sebelum user dapat membeli
4. **15 menit timeout** - User harus menyelesaikan pembayaran dalam 15 menit

---

*Dokumentasi ini dibuat pada: 23 Januari 2026*
*Bot Version: 1.0.0*
