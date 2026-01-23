# 🛒 Smart Store Bot

Bot Telegram Store/Toko Online dengan integrasi Payment Gateway **Pakasir.com** (QRIS).

## ✨ Fitur Utama

### 🛍️ Untuk User
- **Deposit Saldo** - Deposit dengan QRIS otomatis
- **Beli Script** - Pembelian script bot otomatis
- **Beli Apps Premium** - Akun premium dengan stok otomatis
- **Beli Panel** - Panel Pterodactyl otomatis
- **Tools** - QR Generator, URL Shortener, Screenshot Website

### 👑 Untuk Owner
- **Dashboard Admin** - Statistik lengkap
- **Manage Produk** - Tambah/hapus script dan apps
- **Manage Stok** - Tambah akun untuk apps premium
- **Broadcast** - Kirim pesan ke semua user
- **Add Saldo** - Tambah saldo user manual
- **Toggle Panel** - Buka/tutup penjualan panel

### 💳 Payment Gateway
- Integrasi **Pakasir.com** QRIS
- Pembayaran otomatis dengan QR Code
- Pengecekan status real-time
- Notifikasi pembayaran otomatis

## 🚀 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd telegram_store_bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi
Salin file `.env.example` ke `.env` dan isi konfigurasi:

```bash
cp .env.example .env
nano .env
```

Isi konfigurasi berikut:
```env
# Telegram Bot
BOT_TOKEN=your_bot_token_from_botfather
OWNER_ID=your_telegram_user_id
OWNER_NAME=Your Name
OWNER_USERNAME=@yourusername

# Store Settings
CHANNEL_USERNAME=yourchannel
GROUP_USERNAME=yourgroup
TESTIMONI_CHANNEL=@yourtestimoni

# Pakasir Payment Gateway
PAKASIR_PROJECT=your_project_slug
PAKASIR_API_KEY=your_api_key
```

### 4. Daftar Pakasir
1. Buka https://app.pakasir.com
2. Daftar/Login
3. Buat **Proyek** baru
4. Catat **Slug** dan **API Key**
5. Masukkan ke file `.env`

### 5. Jalankan Bot
```bash
python bot.py
```

## 📖 Dokumentasi Pakasir

Untuk integrasi payment gateway, baca dokumentasi lengkap di:
https://pakasir.com/p/docs

### Endpoint yang Digunakan
- `POST /api/transactioncreate/qris` - Buat transaksi QRIS
- `GET /api/transactiondetail` - Cek status transaksi
- `POST /api/transactioncancel` - Batalkan transaksi

## 📁 Struktur Folder

```
telegram_store_bot/
├── bot.py              # Main bot file
├── config.py           # Konfigurasi
├── requirements.txt    # Dependencies
├── .env.example        # Template environment
├── database/           # SQLite database
├── handlers/           # Handler modules
│   ├── start.py       # Start & menu handlers
│   ├── shop.py        # Shop handlers
│   ├── deposit.py     # Deposit handlers
│   ├── owner.py       # Owner menu handlers
│   └── tools.py       # Tools handlers
└── utils/              # Utility modules
    ├── database.py    # Database handler
    ├── payment.py     # Pakasir payment
    └── helpers.py     # Helper functions
```

## 🎮 Commands

### User Commands
| Command | Deskripsi |
|---------|-----------|
| `/start` | Mulai bot |
| `/makeqr [text]` | Buat QR Code |
| `/shorten [url]` | Pendekkan URL |
| `/ssweb [url]` | Screenshot website |

### Owner Commands
Owner dapat mengakses menu admin melalui tombol **Menu Owner** di menu utama.

## 💰 Cara Kerja Pembayaran

1. User pilih produk atau deposit
2. Bot buat transaksi QRIS via Pakasir API
3. QR Code dikirim ke user
4. User scan dan bayar
5. Bot cek status setiap 15 detik
6. Jika sukses, produk/saldo dikirim otomatis

## 🔧 Kustomisasi

### Mengubah Tampilan
Edit emoji dan text di `config.py`:
```python
EMOJI = {
    "store": "🛒",
    "money": "💰",
    ...
}
```

### Menambah Produk
1. Buka bot sebagai owner
2. Klik **Menu Owner**
3. Pilih **Add Script** atau **Add Apps**
4. Ikuti instruksi

## ⚠️ Catatan Penting

- Pastikan bot token valid
- Jangan share API key Pakasir
- Backup database secara berkala
- Test di mode sandbox dulu sebelum production

## 📞 Support

Jika ada pertanyaan atau kendala:
- Dokumentasi Pakasir: https://pakasir.com/p/docs
- Issue di repository ini

## 📜 License

MIT License - Bebas digunakan dan dimodifikasi.

---
Made with ❤️ for Indonesian Telegram Store Owners
