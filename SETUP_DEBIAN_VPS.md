# 🚀 Panduan Setup VIP Premium Bot di Debian 13 VPS

## 📋 Persyaratan
- VPS dengan Debian 13 (Trixie)
- Minimal 512MB RAM
- Akses root atau sudo
- Koneksi internet stabil

---

## 🔧 Langkah 1: Update Sistem

```bash
# Login ke VPS sebagai root
ssh root@IP_VPS_ANDA

# Update package list dan upgrade sistem
apt update && apt upgrade -y
```

---

## 🐍 Langkah 2: Install Python dan Dependencies

```bash
# Install Python 3, pip, dan virtual environment
apt install -y python3 python3-pip python3-venv git

# Verifikasi instalasi
python3 --version
pip3 --version
```

---

## 📁 Langkah 3: Setup Project

```bash
# Buat direktori untuk bot
mkdir -p /root/tukartonbot
cd /root/tukartonbot

# Clone atau copy file auto.py ke direktori ini
# Jika menggunakan git:
# git clone https://github.com/insikex/auto.git .

# Atau upload file auto.py secara manual menggunakan:
# scp auto.py root@IP_VPS_ANDA:/root/tukartonbot/
```

---

## 🌐 Langkah 4: Buat Virtual Environment

```bash
cd /root/tukartonbot

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Verifikasi (akan muncul (venv) di awal prompt)
which python
```

---

## 📦 Langkah 5: Install Python Dependencies

```bash
# Pastikan virtual environment aktif
source venv/bin/activate

# Install dependencies yang dibutuhkan
pip install pyTelegramBotAPI aiocryptopay

# Atau buat file requirements.txt dan install:
cat > requirements.txt << 'EOF'
pyTelegramBotAPI>=4.14.0
aiocryptopay>=0.3.5
aiohttp>=3.9.0
EOF

pip install -r requirements.txt

# Verifikasi instalasi
pip list
```

---

## ⚙️ Langkah 6: Konfigurasi Bot

Edit file `auto.py` untuk mengatur konfigurasi:

```bash
nano auto.py
```

### Yang perlu diubah:

```python
# 1. Token bot dari @BotFather
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'

# 2. Token CryptoPay dari @CryptoBot
CRYPTOPAY_TOKEN = 'YOUR_CRYPTOPAY_TOKEN_HERE'

# 3. Link channel/group premium Anda
PREMIUM_LINK = 'https://t.me/+YOUR_INVITE_LINK'

# 4. Admin ID (dapatkan dari @userinfobot)
ADMIN_ID = YOUR_USER_ID  # contoh: 123456789
```

Simpan dengan `Ctrl+X`, lalu `Y`, lalu `Enter`.

---

## 🧪 Langkah 7: Test Bot

```bash
# Pastikan virtual environment aktif
cd /root/tukartonbot
source venv/bin/activate

# Jalankan bot untuk test
python3 auto.py
```

Jika berhasil, Anda akan melihat:
```
==================================================
🤖 VIP Premium Bot dengan CryptoPay
==================================================
💰 Harga Asli: $300
🔥 Diskon: 50%
✅ Harga Final: $150
⏰ Durasi: LIFETIME
==================================================
Bot berjalan...
==================================================
```

Tekan `Ctrl+C` untuk menghentikan bot.

---

## 🔄 Langkah 8: Setup Systemd Service (Auto-Start)

Buat service file agar bot otomatis berjalan:

```bash
# Buat file service
cat > /etc/systemd/system/tukartonbot.service << 'EOF'
[Unit]
Description=TukartonBot - VIP Premium Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/tukartonbot
ExecStart=/root/tukartonbot/venv/bin/python3 /root/tukartonbot/auto.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment variables (optional)
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
```

---

## ▶️ Langkah 9: Aktifkan dan Jalankan Service

```bash
# Reload systemd
systemctl daemon-reload

# Aktifkan service untuk auto-start saat boot
systemctl enable tukartonbot

# Jalankan bot
systemctl start tukartonbot

# Cek status
systemctl status tukartonbot
```

---

## 📊 Langkah 10: Perintah Manajemen Bot

### Melihat Status Bot
```bash
systemctl status tukartonbot
```

### Melihat Log Real-time
```bash
journalctl -u tukartonbot -f
```

### Melihat Log Terakhir (100 baris)
```bash
journalctl -u tukartonbot -n 100
```

### Restart Bot
```bash
systemctl restart tukartonbot
```

### Stop Bot
```bash
systemctl stop tukartonbot
```

### Start Bot
```bash
systemctl start tukartonbot
```

---

## 🔐 Langkah 11: Setup Firewall (Opsional tapi Disarankan)

```bash
# Install UFW
apt install -y ufw

# Allow SSH (PENTING! Jangan sampai terkunci)
ufw allow ssh
ufw allow 22/tcp

# Enable firewall
ufw enable

# Cek status
ufw status
```

---

## 🔑 Langkah 12: Mendapatkan Token dan Konfigurasi

### A. Bot Token dari @BotFather
1. Buka Telegram, cari `@BotFather`
2. Kirim `/newbot`
3. Ikuti instruksi untuk membuat bot baru
4. Copy token yang diberikan

### B. CryptoPay Token dari @CryptoBot
1. Buka Telegram, cari `@CryptoBot`
2. Klik "Crypto Pay"
3. Klik "My Apps" → "Create App" (jika belum ada)
4. Klik app Anda → "API Token"
5. Copy token (format: `APP_ID:TOKEN`)

### C. Premium Channel Link
1. Buat channel/group private
2. Dapatkan invite link: Settings → Invite Links → Create Link
3. Copy link yang dimulai dengan `https://t.me/+...`

### D. Admin User ID
1. Cari `@userinfobot` di Telegram
2. Kirim pesan apapun
3. Bot akan mengirim User ID Anda

---

## ❗ Troubleshooting

### Error: "SyntaxError: name 'ADMIN_ID' is used prior to global declaration"
- Pastikan menggunakan versi `auto.py` yang sudah diperbaiki
- Bug ini sudah diperbaiki di commit terakhir

### Error: "ModuleNotFoundError: No module named 'telebot'"
```bash
source venv/bin/activate
pip install pyTelegramBotAPI
```

### Error: "ModuleNotFoundError: No module named 'aiocryptopay'"
```bash
source venv/bin/activate
pip install aiocryptopay
```

### Error: CryptoPay "Unauthorized"
- Periksa CRYPTOPAY_TOKEN sudah benar
- Pastikan format: `APP_ID:TOKEN`

### Error: CryptoPay "IP not allowed"
1. Dapatkan IP VPS: `curl ifconfig.me`
2. Buka @CryptoBot → Crypto Pay → My Apps → App Anda
3. Security → IP Allowlist → Tambahkan IP VPS

### Bot tidak merespon
```bash
# Cek status service
systemctl status tukartonbot

# Cek log error
journalctl -u tukartonbot -n 50

# Restart bot
systemctl restart tukartonbot
```

### Database tidak tersimpan
- Pastikan working directory benar
- File `premium_users.json` dan `pending_invoices.json` akan dibuat otomatis
- Cek permission: `ls -la /root/tukartonbot/`

---

## 📝 Struktur File

Setelah setup selesai, struktur direktori akan seperti ini:

```
/root/tukartonbot/
├── auto.py                    # File utama bot
├── venv/                      # Virtual environment
│   ├── bin/
│   ├── lib/
│   └── ...
├── premium_users.json         # Database user premium (auto-created)
├── pending_invoices.json      # Pending invoices (auto-created)
└── requirements.txt           # Dependencies
```

---

## 🎯 Perintah Bot yang Tersedia

| Perintah | Deskripsi |
|----------|-----------|
| `/start` | Menu utama |
| `/premium` | Info premium membership |
| `/status` | Cek status membership |
| `/cek <id>` | Cek status invoice |
| `/help` | Bantuan |
| `/setadmin` | Set admin (pertama kali) |
| `/testapi` | Test koneksi CryptoPay (admin) |
| `/stats` | Statistik bot (admin) |

---

## 🔄 Update Bot

Untuk update bot ke versi terbaru:

```bash
# Stop bot
systemctl stop tukartonbot

# Backup file lama (opsional)
cp /root/tukartonbot/auto.py /root/tukartonbot/auto.py.backup

# Download/copy file baru
# git pull (jika menggunakan git)
# atau upload file baru

# Restart bot
systemctl start tukartonbot

# Cek status
systemctl status tukartonbot
```

---

## ✅ Checklist Setup

- [ ] VPS Debian 13 ready
- [ ] Python 3 dan pip terinstall
- [ ] Virtual environment dibuat
- [ ] Dependencies terinstall (pyTelegramBotAPI, aiocryptopay)
- [ ] BOT_TOKEN dikonfigurasi
- [ ] CRYPTOPAY_TOKEN dikonfigurasi
- [ ] PREMIUM_LINK dikonfigurasi
- [ ] ADMIN_ID dikonfigurasi (atau gunakan /setadmin)
- [ ] Systemd service dibuat
- [ ] Bot berjalan dengan baik
- [ ] Test pembayaran berhasil

---

## 🆘 Butuh Bantuan?

Jika mengalami masalah, cek:
1. Log bot: `journalctl -u tukartonbot -f`
2. Status service: `systemctl status tukartonbot`
3. Syntax Python: `python3 -m py_compile auto.py`

---

**Selamat! Bot Anda sekarang sudah berjalan di VPS Debian 13!** 🎉
