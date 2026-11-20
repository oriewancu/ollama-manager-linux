#!/bin/bash
# ==============================================================================
# OLLAMA MANAGER (LINUX EDITION) - AUTOMATED INSTALLER SCRIPT
# ==============================================================================

set -e

# Get the absolute path of the directory where the script and application are located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PY="$SCRIPT_DIR/ollama_manager.py"
APP_TUI="$SCRIPT_DIR/ollama-manager-tui.sh"

DESKTOP_USER_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"
APP_SHARE_DIR="$HOME/.local/share/ollama-manager"

echo "=================================================="
echo "[*] Starting Ollama Manager installation for Linux..."
echo "[*] Application directory path detected at: $SCRIPT_DIR"
echo "=================================================="

# 1. Validate main application files
if [ ! -f "$APP_PY" ]; then
    echo "[!] Error: File $APP_PY not found!"
    exit 1
fi

if [ ! -f "$APP_TUI" ]; then
    echo "[!] Error: File $APP_TUI not found!"
    exit 1
fi

# 2. Ensure all required libraries (Python3, Tkinter, curl, etc.) are installed
echo "[*] Step 1: Checking and installing required dependencies..."

# Detect package manager
if command -v apt-get &> /dev/null; then
    echo "[*] Debian/Ubuntu-based system detected (APT)."
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-tk python3-pip curl jq bc lshw pciutils xclip || true
elif command -v dnf &> /dev/null; then
    echo "[*] Fedora/RHEL-based system detected (DNF)."
    sudo dnf install -y python3 python3-tkinter python3-pip curl jq bc lshw pciutils xclip || true
elif command -v pacman &> /dev/null; then
    echo "[*] Arch Linux-based system detected (Pacman)."
    sudo pacman -Sy --noconfirm python python-tkinter python-pip curl jq bc lshw pciutils xclip || true
elif command -v zypper &> /dev/null; then
    echo "[*] openSUSE-based system detected (Zypper)."
    sudo zypper install -y python3 python3-tk python3-pip curl jq bc lshw pciutils xclip || true
else
    echo "[!] Warning: Package manager could not be automatically identified."
    echo "[!] Please ensure Python 3, python3-tk, curl, and jq are installed on your system."
fi

# 3. Copy application sources to ~/.local/share/ollama-manager
echo "[*] Step 2: Copying application sources to $APP_SHARE_DIR..."
mkdir -p "$APP_SHARE_DIR"
cp -f "$APP_PY" "$APP_SHARE_DIR/"
cp -f "$APP_TUI" "$APP_SHARE_DIR/"
chmod +x "$APP_SHARE_DIR/ollama_manager.py"
chmod +x "$APP_SHARE_DIR/ollama-manager-tui.sh"

if [ -f "$SCRIPT_DIR/models_db.json" ]; then
    cp -f "$SCRIPT_DIR/models_db.json" "$APP_SHARE_DIR/"
fi
if [ -f "$SCRIPT_DIR/config.json" ]; then
    cp -f "$SCRIPT_DIR/config.json" "$APP_SHARE_DIR/"
fi
if [ -f "$SCRIPT_DIR/preview.png" ]; then
    cp -f "$SCRIPT_DIR/preview.png" "$APP_SHARE_DIR/"
fi

# 4. Detect available terminal emulator on the system
# Priority order: gnome-terminal -> konsole -> xfce4-terminal -> alacritty -> kitty -> terminator -> xterm
DETECTED_TERM=""
for t in gnome-terminal konsole xfce4-terminal alacritty kitty terminator xterm; do
    if command -v "$t" &> /dev/null; then
        DETECTED_TERM="$t"
        break
    fi
done

# If none are found, use x-terminal-emulator as a fallback
if [ -z "$DETECTED_TERM" ]; then
    DETECTED_TERM="x-terminal-emulator"
fi

echo "[*] Terminal emulator detected / selected for TUI: $DETECTED_TERM"

# Build the Exec command according to the terminal used so arguments execute properly
if [ "$DETECTED_TERM" = "gnome-terminal" ]; then
    TUI_EXEC="gnome-terminal -- bash -c \"$APP_SHARE_DIR/ollama-manager-tui.sh; exec bash\""
elif [ "$DETECTED_TERM" = "konsole" ]; then
    TUI_EXEC="konsole -e bash -c \"$APP_SHARE_DIR/ollama-manager-tui.sh; exec bash\""
elif [ "$DETECTED_TERM" = "xfce4-terminal" ]; then
    TUI_EXEC="xfce4-terminal -e \"bash -c '$APP_SHARE_DIR/ollama-manager-tui.sh; exec bash'\""
elif [ "$DETECTED_TERM" = "alacritty" ] || [ "$DETECTED_TERM" = "kitty" ]; then
    TUI_EXEC="$DETECTED_TERM -e bash -c \"$APP_SHARE_DIR/ollama-manager-tui.sh; exec bash\""
else
    TUI_EXEC="$DETECTED_TERM -e bash -c \"$APP_SHARE_DIR/ollama-manager-tui.sh; exec bash\""
fi

# 5. Create .desktop shortcuts for the main application (Python GUI) and TUI (Terminal UI)
echo "[*] Step 3: Creating .desktop shortcut files for GUI and TUI..."
mkdir -p "$DESKTOP_USER_DIR"
mkdir -p "$ICON_DIR"

DESKTOP_GUI="$DESKTOP_USER_DIR/ollama-manager.desktop"
DESKTOP_TUI="$DESKTOP_USER_DIR/ollama-manager-tui.desktop"

# GUI Shortcut (Python Tkinter)
cat << EOF > "$DESKTOP_GUI"
[Desktop Entry]
Name=Ollama Local AI Manager
Comment=Manage Ollama models, VRAM matching recommendations, and local endpoints
Exec=python3 "$APP_SHARE_DIR/ollama_manager.py"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;Development;AI;
StartupNotify=true
EOF

# TUI Shortcut (Bash Terminal UI)
cat << EOF > "$DESKTOP_TUI"
[Desktop Entry]
Name=Ollama Neural TUI Manager
Comment=Terminal User Interface for Ollama models and neural agents
Exec=$TUI_EXEC
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;Development;ConsoleOnly;AI;
StartupNotify=true
EOF

chmod +x "$DESKTOP_GUI"
chmod +x "$DESKTOP_TUI"

# 6. Update desktop application shortcut database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_USER_DIR" 2>/dev/null || true
    echo "[*] Desktop database successfully updated."
fi

echo "=================================================="
echo "[+] Ollama Manager Installation Complete!"
echo "[+] 1. System dependencies have been checked/installed."
echo "[+] 2. Application sources copied to: $APP_SHARE_DIR"
echo "[+] 3. GUI (.desktop) & TUI (.desktop) shortcuts created at:"
echo "       - $DESKTOP_GUI"
echo "       - $DESKTOP_TUI"
echo "[+] TUI terminal using: $DETECTED_TERM"
echo "[+] You can search for 'Ollama Local AI Manager' or"
echo "[+] 'Ollama Neural TUI Manager' in your Application Launcher."
echo "=================================================="