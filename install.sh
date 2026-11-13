#!/bin/bash

# Mendapatkan absolute path dari direktori tempat script dan aplikasi berada
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PY="$SCRIPT_DIR/ollama_manager.py"
DESKTOP_SRC="$SCRIPT_DIR/ollama-manager.desktop"
DESKTOP_USER_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"

echo "[*] Memulai instalasi Ollama Manager untuk Linux..."
echo "[*] Path direktori aplikasi terdeteksi di: $SCRIPT_DIR"

# 1. Validasi file utama
if [ ! -f "$APP_PY" ]; then
    echo "[!] Error: File ollama_manager.py tidak ditemukan di $SCRIPT_DIR!"
    exit 1
fi

# 2. Buat direktori aplikasi user jika belum ada
mkdir -p "$DESKTOP_USER_DIR"
mkdir -p "$ICON_DIR"

# 3. Generate file .desktop secara dinamis berdasarkan path saat ini
echo "[*] Menulis ulang file konfigurasi desktop (.desktop)..."
cat << EOF > "$DESKTOP_SRC"
[Desktop Entry]
Name=Ollama Local AI Manager
Comment=Manage Ollama models, VRAM matching recommendations, and local endpoints
Exec=python3 "$APP_PY"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;Development;AI;
EOF

# 4. Salin file .desktop ke direktori aplikasi sistem/user Linux
cp "$DESKTOP_SRC" "$DESKTOP_USER_DIR/ollama-manager.desktop"
chmod +x "$DESKTOP_USER_DIR/ollama-manager.desktop"

# 5. Update database shortcut aplikasi desktop
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_USER_DIR"
    echo "[*] Database desktop berhasil diperbarui."
fi

echo "=================================================="
echo "[+] Instalasi Selesai!"
echo "[+] Ollama Manager kini terdaftar sebagai aplikasi Linux."
echo "[+] Anda dapat mencarinya melalui App Menu / Application Launcher."
echo "=================================================="
