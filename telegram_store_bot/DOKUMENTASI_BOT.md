# 📚 DOKUMENTASI LENGKAP BOT TELEGRAM STORE

## 📋 DAFTAR ISI
1. [Semua Respond Bot](#semua-respond-bot)
2. [Semua Fungsi Button](#semua-fungsi-button)
3. [Commands yang Tersedia](#commands-yang-tersedia)
4. [Panduan Deployment VPS Debian 13](#panduan-deployment-vps-debian-13)

---

## 🤖 SEMUA RESPOND BOT

### 1. `/start` - Pesan Selamat Datang
```
╔══════════════════════════════════╗
║     ⭐ SELAMAT DATANG ⭐     ║
╠══════════════════════════════════╣
║                                  ║
║   🛒 Smart Store Bot    ║
║                                  ║
╠══════════════════════════════════╣
║  🚀 INFO BOT                  ║
║  ├ Owner: [OWNER_NAME]
║  ├ Version: 1.0.0
║  └ Status: 🟢 Online
║                                  ║
║  📊 STATISTIK                 ║
║  ├ Total Users: [count]
║  └ Uptime: [uptime]
╚══════════════════════════════════╝

🔥 Selamat berbelanja!
Silakan pilih menu di bawah ini.
```

### 2. Respond untuk Private Chat Only
```
🚫 Bot ini hanya bisa digunakan di Private Chat.
Silakan chat saya langsung di @[bot_username]
```

### 3. Notifikasi User Baru (ke Owner)
```
👤 USER BARU TERDAFTAR!
━━━━━━━━━━━━━━━━━━━━━
Nama: [nama]
Username: [username]
ID: [user_id]
Waktu: [timestamp]

📊 Total User: [count]
```

### 4. Menu Profil (menu_profile)
```
╔══════════════════════════════════╗
║     👤 PROFIL SAYA 👤     ║
╠══════════════════════════════════╣
║  Nama: [nama]
║  Username: [username]
║  ID: [user_id]
╠══════════════════════════════════╣
║  📦 Total Transaksi: [count]
║                                  ║
║  💳 Pembayaran via QRIS Pakasir  ║
╚══════════════════════════════════╝
```

### 5. Riwayat Transaksi (menu_history)
```
📜 RIWAYAT TRANSAKSI

1. ⏳/✅/⌛/❌ [order_id]
   💰 Rp X.XXX - [product_name]

2. ...
```

Jika kosong:
```
📭 Belum ada riwayat transaksi.
```

### 6. Menu Contact Owner (menu_contact_owner)
```
╔══════════════════════════════════╗
║     📞 HUBUNGI OWNER 📞     ║
╠══════════════════════════════════╣
║  Nama: [owner_name]
║  Telegram: [owner_username]
╚══════════════════════════════════╝

ℹ️ Silakan hubungi owner untuk bantuan
atau pertanyaan seputar layanan.
```

### 7. Menu Shop (menu_shop)
```
╔══════════════════════════════════╗
║     🛍️ MENU LAYANAN 🛍️     ║
╠══════════════════════════════════╣
║                                  ║
║  Silakan pilih layanan yang      ║
║  ingin Anda order:               ║
║                                  ║
║  💳 Pembayaran otomatis via QRIS ║
║  📦 Pengiriman data otomatis     ║
║                                  ║
╚══════════════════════════════════╝
```

### 8. Daftar Apps Premium (shop_apps)
```
📱 DAFTAR APPS PREMIUM

Pilih apps yang ingin Anda beli:
```

Jika kosong:
```
📭 Belum ada apps premium yang tersedia saat ini.
```

### 9. Buy Panel (shop_panel)
```
🖥️ BELI PANEL PTERODACTYL

Fitur:
✅ Panel Pterodactyl Gratis
✅ Unlimited Resources
✅ Node Berkualitas
✅ Support 24/7

Harga: Rp X.XXX

Untuk melanjutkan, klik tombol di bawah.
```

Panel Tutup:
```
🚫 Panel sedang tidak tersedia

Silakan coba lagi nanti atau hubungi owner.
```

### 10. Admin Panel (shop_admin_panel)
```
👑 BELI AKUN ADMIN PANEL

Keuntungan Admin:
✅ Akses Full Admin Panel
✅ Bisa Create Server
✅ Manage All Users
✅ Full Control

Harga: Rp X.XXX
```

### 11. Pembelian Script Disabled
```
❌ Fitur pembelian script telah dinonaktifkan.

Silakan hubungi owner untuk informasi lebih lanjut.
```

### 12. Pembayaran QRIS (buy_product)
```
💳 PEMBAYARAN QRIS

🆔 Order ID: [order_id]
📦 Produk: [product_name]
💰 Harga: Rp X.XXX
💸 Fee: Rp XXX
━━━━━━━━━━━━━━━━━━━━
💵 Total Bayar: Rp X.XXX

⏰ Berlaku 15 menit
📱 Scan QR dengan e-wallet/m-banking

⚠️ Bayar sesuai nominal!
```

### 13. Gagal Buat Pembayaran
```
❌ Gagal membuat pembayaran: [error_message]

Silakan coba lagi.
```

### 14. Fitur Saldo Tidak Tersedia (pay_with_balance)
```
❌ Fitur Saldo Tidak Tersedia

Pembayaran hanya dapat dilakukan melalui QRIS.
Silakan pilih produk dan bayar langsung dengan QRIS.
```

### 15. Pembayaran Berhasil
```
✅ Pembayaran Berhasil!

Order ID: [order_id]
```

### 16. Pembayaran Expired
```
⏰ Pembayaran Expired

Order ID: [order_id]

Silakan buat transaksi baru.
```

### 17. Transaksi Dibatalkan
```
❌ Transaksi Dibatalkan

Order ID: [order_id]
```

### 18. Pengiriman Script Berhasil
```
✅ PEMBELIAN BERHASIL!

📦 Produk: [product_name]
🆔 Order ID: [order_id]

Terima kasih sudah berbelanja! 🙏
```

### 19. Pengiriman App Account Berhasil
```
✅ PEMBELIAN BERHASIL!

📱 Produk: [product_name]
🆔 Order ID: [order_id]

━━━━━━━━━━━━━━━━━━━━
📋 DATA AKUN:
[account_data]
━━━━━━━━━━━━━━━━━━━━

⚠️ Segera ganti password!
Terima kasih sudah berbelanja! 🙏
```

### 20. Stok Habis
```
❌ Maaf, stok produk ini sudah habis.
```

### 21. Notifikasi Pembelian (ke Owner)
```
💰 PEMBELIAN BARU!
━━━━━━━━━━━━━━━━━━━━
Produk: [product_name]
Harga: Rp X.XXX
Order ID: [order_id]

Pembeli:
├ ID: [user_id]
└ Username: [username]
```

### 22. Cek Status Pembayaran
Belum diterima:
```
⏳ Pembayaran belum diterima.

Pastikan Anda sudah membayar sesuai nominal.
```

Berhasil:
```
✅ Pembayaran Berhasil!

Produk akan segera dikirim.
```

---

## 🔘 SEMUA FUNGSI BUTTON

### Menu Utama (Main Menu)
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| 🛍️ Menu Layanan | `menu_shop` | Buka menu shop |
| 🛠️ Menu Tools | `menu_tools` | Buka menu tools |
| 👤 Profil Saya | `menu_profile` | Tampilkan profil user |
| 📢 Channel Info | URL | Link ke channel |
| 💬 Grup Diskusi | URL | Link ke grup |
| 📞 Hubungi Owner | `menu_contact_owner` | Tampilkan info owner |
| 👑 Menu Owner | `menu_owner` | Buka panel owner (Owner only) |

### Menu Profil
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| 📜 Riwayat Transaksi | `menu_history` | Tampilkan riwayat |
| 🛒 Belanja Sekarang | `menu_shop` | Ke menu shop |
| 🔙 Kembali | `back_main` | Kembali ke menu utama |

### Menu Shop
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| 📱 Apps Premium | `shop_apps` | Lihat daftar apps |
| 🖥️ Buy Panel | `shop_panel` | Beli panel Pterodactyl |
| 👑 Admin Panel | `shop_admin_panel` | Beli admin panel |
| 🔙 Kembali | `back_main` | Kembali ke menu utama |

### Menu Apps
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| [Nama App] | `buy_app_[id]` | Beli app (generate QRIS) |
| ❌ [Nama] (HABIS) | `sold_out` | Produk habis |
| 🔙 Kembali | `menu_shop` | Kembali ke menu shop |

### Panel Pembayaran QRIS
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| 🔄 Cek Status Pembayaran | `check_payment_[order_id]` | Cek status pembayaran |
| ❌ Batalkan | `cancel_payment_[order_id]` | Batalkan transaksi |

### Menu Tools
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| 📱 Make QR | `tool_makeqr` | Buat QR Code |
| 🔗 Shorten URL | `tool_shorten` | Pendekkan URL |
| 📸 Screenshot Web | `tool_ssweb` | Screenshot website |
| 🔙 Kembali | `back_main` | Kembali ke menu utama |

### Menu Owner
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| 🟢 Toggle Panel | `owner_toggle_panel` | Buka/tutup panel |
| 📢 Broadcast | `owner_broadcast` | Broadcast ke semua user |
| ➕ Add Script | `owner_add_script` | Tambah produk script |
| ➕ Add Apps | `owner_add_app` | Tambah produk apps |
| 📋 List Produk | `owner_list_products` | Lihat semua produk |
| 🗑️ Hapus Produk | `owner_delete_product` | Hapus produk |
| ➕ Add Account | `owner_add_account` | Tambah akun ke stok |
| 📜 Transaksi Pending | `owner_pending_txns` | Lihat transaksi pending |
| 👥 List Users | `owner_list_users` | Lihat daftar user |
| 🔙 Kembali | `back_main` | Kembali ke menu utama |

### Add Account
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| [Nama App] (stok: X) | `add_acc_to_[id]` | Pilih app untuk tambah akun |

### Delete Product
| Button | Callback Data | Fungsi |
|--------|--------------|--------|
| ❌ [Nama Produk] | `delete_product_[id]` | Hapus produk |

---

## ⌨️ COMMANDS YANG TERSEDIA

| Command | Fungsi | Contoh |
|---------|--------|--------|
| `/start` | Mulai bot, tampilkan menu utama | `/start` |
| `/makeqr [text/url]` | Buat QR Code | `/makeqr https://google.com` |
| `/shorten [url]` | Pendekkan URL | `/shorten https://very-long-url.com/path` |
| `/ssweb [url]` | Screenshot website | `/ssweb https://google.com` |
| `/cancel` | Batalkan aksi yang sedang berlangsung | `/cancel` |

---

## 🚀 PANDUAN DEPLOYMENT VPS DEBIAN 13

### Langkah 1: Login ke VPS via Termius

1. Buka Termius di HP/PC
2. Tambah host baru:
   - Hostname: IP VPS Anda
   - Username: root (atau username Anda)
   - Password: Password VPS Anda
3. Connect ke VPS

### Langkah 2: Update Sistem

```bash
# Update package list
apt update

# Upgrade semua package
apt upgrade -y
```

### Langkah 3: Install Python 3.11+

```bash
# Install Python dan pip
apt install python3 python3-pip python3-venv -y

# Cek versi Python
python3 --version
```

### Langkah 4: Install Git

```bash
apt install git -y
```

### Langkah 5: Clone/Upload Bot

**Opsi A: Upload via SFTP (Termius)**
1. Di Termius, buka SFTP
2. Navigate ke `/root/`
3. Upload folder `telegram_store_bot`

**Opsi B: Clone dari Git (jika ada repo)**
```bash
git clone [URL_REPO] /root/telegram_store_bot
```

**Opsi C: Upload file ZIP lalu extract**
```bash
# Setelah upload zip
apt install unzip -y
unzip telegram_store_bot.zip -d /root/
```

### Langkah 6: Setup Virtual Environment

```bash
# Masuk ke folder bot
cd /root/telegram_store_bot

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Langkah 7: Konfigurasi Bot

```bash
# Copy file .env.example ke .env
cp .env.example .env

# Edit file .env
nano .env
```

Isi dengan konfigurasi Anda:
```env
# Telegram Bot Settings
BOT_TOKEN=123456789:ABCDefgh-ijklmnopqrstuvwxyz
OWNER_ID=987654321
OWNER_NAME=Nama Anda
OWNER_USERNAME=@username_anda

# Store Settings
CHANNEL_USERNAME=nama_channel_tanpa_@
GROUP_USERNAME=nama_grup_tanpa_@
TESTIMONI_CHANNEL=@testimoni_channel
START_PHOTO=https://link-foto-welcome.jpg

# Pakasir Payment Gateway
PAKASIR_PROJECT=project_slug_dari_pakasir
PAKASIR_API_KEY=api_key_dari_pakasir
```

Simpan: `Ctrl+X`, lalu `Y`, lalu `Enter`

### Langkah 8: Buat Folder Database

```bash
mkdir -p database
```

### Langkah 9: Test Jalankan Bot

```bash
# Pastikan masih di folder bot dan venv aktif
cd /root/telegram_store_bot
source venv/bin/activate

# Jalankan bot
python3 bot.py
```

Jika berhasil, akan muncul:
```
╔══════════════════════════════════════════════╗
║                                              ║
║     🛒 SMART STORE BOT v1.0.0                ║
║     Powered by Pakasir.com Payment           ║
║                                              ║
╠══════════════════════════════════════════════╣
║  Starting bot...                             ║
╚══════════════════════════════════════════════╝

✅ Bot started successfully!
📱 Bot: @nama_bot_anda
👑 Owner ID: 987654321
```

Tekan `Ctrl+C` untuk stop bot.

### Langkah 10: Setup Systemd Service (Agar Bot Jalan Otomatis)

```bash
# Buat file service
nano /etc/systemd/system/storebot.service
```

Isi dengan:
```ini
[Unit]
Description=Telegram Store Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram_store_bot
Environment="PATH=/root/telegram_store_bot/venv/bin"
ExecStart=/root/telegram_store_bot/venv/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Simpan: `Ctrl+X`, lalu `Y`, lalu `Enter`

### Langkah 11: Aktifkan dan Jalankan Service

```bash
# Reload systemd
systemctl daemon-reload

# Aktifkan service agar jalan saat boot
systemctl enable storebot

# Jalankan bot
systemctl start storebot

# Cek status
systemctl status storebot
```

### Langkah 12: Perintah Berguna

```bash
# Lihat status bot
systemctl status storebot

# Stop bot
systemctl stop storebot

# Restart bot
systemctl restart storebot

# Lihat log bot secara real-time
journalctl -u storebot -f

# Lihat 50 baris log terakhir
journalctl -u storebot -n 50
```

---

## ⚠️ TROUBLESHOOTING

### Error: Module not found
```bash
# Pastikan virtual environment aktif
source /root/telegram_store_bot/venv/bin/activate

# Install ulang dependencies
pip install -r requirements.txt
```

### Error: Permission denied
```bash
chmod +x /root/telegram_store_bot/bot.py
```

### Bot tidak merespond
1. Cek token bot sudah benar
2. Pastikan BOT_TOKEN di .env sudah benar
3. Cek log: `journalctl -u storebot -n 100`

### Database error
```bash
# Buat folder database
mkdir -p /root/telegram_store_bot/database

# Set permission
chmod 755 /root/telegram_store_bot/database
```

### Tidak bisa install Pillow
```bash
# Install dependencies untuk Pillow
apt install libjpeg-dev zlib1g-dev -y

# Install ulang
pip install Pillow
```

---

## 📝 CARA DAPAT TOKEN BOT & OWNER ID

### Mendapatkan Bot Token:
1. Buka Telegram, cari `@BotFather`
2. Kirim `/newbot`
3. Ikuti instruksi, beri nama bot
4. Copy token yang diberikan

### Mendapatkan Owner ID:
1. Buka Telegram, cari `@userinfobot`
2. Kirim `/start`
3. Copy ID Anda

### Mendapatkan API Pakasir:
1. Daftar di https://pakasir.com
2. Buat project baru
3. Copy Project Slug dan API Key

---

## ✅ CHECKLIST SEBELUM LIVE

- [ ] Bot Token sudah benar
- [ ] Owner ID sudah benar
- [ ] Pakasir API sudah di-setup
- [ ] Channel dan Group sudah dibuat
- [ ] Database folder sudah ada
- [ ] Service sudah aktif
- [ ] Test beli produk berhasil

---

**Selamat! Bot Anda sudah siap digunakan! 🎉**
