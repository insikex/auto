#!/bin/bash

# Script untuk menjalankan TukartonBot dengan virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Warna output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=================================="
echo "🤖 TukartonBot Runner"
echo "=================================="

# Cek apakah venv sudah ada
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Virtual environment tidak ditemukan. Membuat...${NC}"
    python3 -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Gagal membuat virtual environment!${NC}"
        echo "Coba install: apt install python3-venv python3-full"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Virtual environment berhasil dibuat${NC}"
    
    # Aktifkan venv dan install dependencies
    echo -e "${YELLOW}📥 Menginstall dependencies...${NC}"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Gagal install dependencies!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependencies berhasil diinstall${NC}"
else
    source "$VENV_DIR/bin/activate"
fi

echo "=================================="
echo -e "${GREEN}🚀 Menjalankan bot...${NC}"
echo "=================================="

# Jalankan bot
python3 "$SCRIPT_DIR/auto.py"
