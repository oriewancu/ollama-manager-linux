import os
import json
import subprocess
import threading
import re
import time
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "models_db.json")
CONFIG_PATH = os.path.join(PROJECT_DIR, "config.json")

# Palet Warna Dominan Biru Lembut (Soft Blue Palette)
THEME = {
    "bg_main": "#EDF4FC",          # Latar utama biru es lembut
    "bg_header": "#D6E6F9",        # Header biru langit lembut
    "bg_nav": "#E2EEFB",           # Bar navigasi biru muda
    "bg_card": "#FFFFFF",          # Permukaan kartu putih bersih
    "bg_card_tint": "#F5F9FF",     # Latar sekunder kebiruan
    "border": "#BDD5F0",           # Garis tepi biru lembut
    "primary": "#2563EB",          # Biru utama (tab aktif & tombol utama)
    "primary_hover": "#1D4ED8",    # Biru hover
    "primary_soft": "#DBEAFE",     # Biru lembut untuk seleksi / tombol sekunder
    "primary_soft_hover": "#BFDBFE",
    "accent_sky": "#0284C7",       # Biru laut untuk aksi tambahan
    "accent_sky_hover": "#0369A1",
    "text_dark": "#0F172A",        # Teks utama navy gelap (kontras tinggi)
    "text_muted": "#475569",       # Teks sekunder abu-biru
    "term_bg": "#0F172A",          # Latar terminal midnight navy
    "term_fg": "#7DD3FC",          # Teks terminal biru langit cerah
    "success_bg": "#DCFCE7",
    "success_fg": "#166534",
    "warn_bg": "#FEF3C7",
    "warn_fg": "#92400E",
    "danger_bg": "#FEE2E2",
    "danger_fg": "#991B1B",
}

GENERAL_MODELS_DB = [
    {
        "name": "qwen2.5-coder:1.5b-instruct",
        "min_ram_gb": 4,
        "min_vram_gb": 2,
        "size": "986 MB",
        "description_id": "Sangat cepat & ringan untuk laptop standar.",
        "description_en": "Very fast & lightweight for standard laptops.",
        "category": "Coding / Ringan"
    },
    {
        "name": "gemma2:2b",
        "min_ram_gb": 6,
        "min_vram_gb": 3,
        "size": "1.6 GB",
        "description_id": "Responsif, general chat & bahasa Indonesia bagus.",
        "description_en": "Responsive, general chat & great Indonesian support.",
        "category": "General / Ringan"
    },
    {
        "name": "phi3:3.8b",
        "min_ram_gb": 8,
        "min_vram_gb": 4,
        "size": "2.2 GB",
        "description_id": "Kuat untuk logika, matematika & koding.",
        "description_en": "Strong for logic, math & coding.",
        "category": "Coding / Sedang"
    },
    {
        "name": "llama3.2:3b",
        "min_ram_gb": 8,
        "min_vram_gb": 4,
        "size": "2.0 GB",
        "description_id": "Sangat pintar untuk teks umum & asisten harian.",
        "description_en": "Very smart for general text & daily assistant.",
        "category": "General / Sedang"
    },
    {
        "name": "qwen2.5:7b-instruct",
        "min_ram_gb": 16,
        "min_vram_gb": 6,
        "size": "4.7 GB",
        "description_id": "Performa tinggi, butuh RAM/VRAM lebih besar.",
        "description_en": "High performance, requires more RAM/VRAM.",
        "category": "General / Berat"
    },
    {
        "name": "deepseek-r1:7b",
        "min_ram_gb": 16,
        "min_vram_gb": 6,
        "size": "4.7 GB",
        "description_id": "Model reasoning dengan kemampuan analitis.",
        "description_en": "Reasoning model with analytical capabilities.",
        "category": "Reasoning / Berat"
    }
]


def init_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(GENERAL_MODELS_DB, f, indent=4)


def load_db():
    init_db()
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return GENERAL_MODELS_DB


def load_config():
    default_cfg = {"lang": "id"}
    if not os.path.exists(CONFIG_PATH):
        save_config(default_cfg)
        return default_cfg
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return default_cfg
        if data.get("lang") not in ("id", "en"):
            data["lang"] = "id"
        return data
    except Exception:
        return default_cfg


def save_config(cfg_data):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, indent=2)
        return True
    except Exception:
        return False


class UniversalOllamaManager:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.lang = self.config.get("lang", "id")
        self.preferred_terminal = self.config.get("terminal") or self.detect_default_terminal()

        self.texts = {
            "id": {
                "title": "Ollama Hub (Linux Edition)",
                "checking": "Memeriksa sistem...",
                "tab_models": "📦 Model & Matriks",
                "tab_api": "🔌 API & Integrasi",
                "tab_hints": "📘 Tentang Ollama",
                "tab_pref": "⚙️ Preferences",
                "header_title": "Ollama & Hardware Compatibility Hub",
                "header_subtitle": "Manajemen Model Lokal, Endpoint API & Kompatibilitas Perangkat",
                "btn_install": "📥 Install Ollama",
                "btn_open_store": "🚀 Rekomendasi Model",
                "btn_custom_install": "📥 Install Model Kustom",
                "frame_installed": "Model yang Sudah Terinstal (Installed)",
                "btn_refresh": "🔄 Muat Ulang",
                "col_model_name": "Nama Model",
                "col_size": "Ukuran",
                "col_modified": "Terakhir Diubah",
                "col_status": "Status Kompatibilitas",
                "col_desc": "Deskripsi Singkat",
                "copied_title": "Disalin",
                "copied_msg": "Nama model berhasil disalin ke clipboard:",
                "frame_logs": "Live Terminal & Output Proses",
                "api_title": "Konfigurasi API & Integrasi Universal",
                "api_left_card": "Endpoint Lokal & Keterangan",
                "api_right_card": "Konfigurasi Integrasi Continue (config.yaml)",
                "api_desc": (
                    "Aplikasi ini dikhususkan untuk sistem operasi Linux.\n"
                    "Endpoint lokal dapat langsung digunakan untuk Agent atau Web UI:\n\n"
                    "• Base URL        : http://localhost:11434\n"
                    "• OpenAI Endpoint : http://localhost:11434/v1\n"
                    "• Format Model    : qwen2.5-coder:1.5b-instruct, gemma2:2b, dll."
                ),
                "continue_config_title": "Contoh Konfigurasi Integrasi Continue (config.yaml):",
                "btn_copy_config": "📋 Salin Config Continue",
                "config_copied_title": "Disalin",
                "config_copied_msg": "Contoh konfigurasi Continue berhasil disalin ke clipboard!",
                "btn_ping": "🩺 Uji Ping API Ollama",
                "hints_title": "Tentang Ollama",
                "hints_card_title": "Informasi & Dokumentasi Resmi Ollama",
                "hints_header_desc": (
                    "Tentang Ollama:\n"
                    "Ollama adalah runtime open-source yang dirancang untuk memudahkan pengguna menjalankan, "
                    "membuat, dan mendistribusikan Large Language Models (LLM) secara lokal di perangkat Anda "
                    "secara offline, aman, dan tanpa latensi cloud.\n\n"
                    "Dokumentasi Resmi:\n"
                    "• Website & Docs Resmi : https://ollama.com/docs\n"
                    "• Repositori GitHub    : https://github.com/ollama/ollama\n"
                ),
                "pref_title": "Pengaturan Preferensi Aplikasi (Preferences)",
                "pref_card_title": "Konfigurasi Umum & Lingkungan",
                "pref_lang_label": "Pilih Bahasa (Language):",
                "pref_term_label": "Aplikasi Terminal untuk Chat:",
                "pref_config_note": f"Konfigurasi dibaca & disimpan otomatis ke: {CONFIG_PATH}",
                "pref_save_btn": "💾 Simpan Preferensi",
                "pref_saved_title": "Tersimpan",
                "pref_saved_msg": "Pengaturan preferensi berhasil disimpan ke config.json!",
                "pref_save_err": "Gagal menyimpan file config.json.",
                "status_running": "● Ollama: BERJALAN",
                "status_stopped": "● Ollama: BERHENTI (Klik untuk Jalankan)",
                "status_not_installed": "● Ollama: TIDAK TERINSTAL",
                "confirm_title": "Konfirmasi",
                "confirm_stop_server": "Matikan layanan server Ollama?",
                "confirm_delete_model": "Hapus model",
                "deleted_msg": "berhasil dihapus.",
                "delete_failed_msg": "Gagal menghapus model.",
                "warning": "Peringatan",
                "warning_msg": "Pilih baris model dari tabel terlebih dahulu!",
                "custom_empty_msg": "Masukkan nama model dengan benar!",
                "downloading_title": "Mengunduh",
                "downloading_msg": "Memulai pengunduhan model",
                "success_title": "Berhasil",
                "success_msg": "Model berhasil diunduh:",
                "error_title": "Error",
                "error_msg": "Gagal mengunduh model",
                "install_info": "Menginstal Ollama via skrip resmi...",
                "install_success": "Ollama berhasil diinstal!",
                "install_error": "Gagal menginstal Ollama",
                "api_status_ok": "Status API",
                "api_status_ok_msg": "Ollama API aktif dan merespon dengan baik (HTTP 200)!",
                "api_error_title": "Koneksi Gagal",
                "api_error": "Gagal terhubung ke Ollama API",
                "modal_title": "🚀 Rekomendasi Model & Installer Universal",
                "modal_header_hw": "Perangkat Terdeteksi -> Sistem",
                "modal_log_title": "Log Pengunduhan Model",
                "modal_btn_download": "⬇️ Unduh Model Pilihan",
                "modal_btn_close": "Tutup",
                "status_very_suitable": "[SANGAT COCOK / CEPAT]",
                "status_suitable": "[COCOK / CPU BOUND]",
                "status_heavy": "[BERAT / RAM TERBATAS]",
                "status_not_recommended": "[TIDAK DISARANKAN]",
                "status_installed_badge": "[✓ TERINSTAL]",
                "custom_install_title": "📥 Input & Install Model Baru",
                "custom_install_prompt": "Masukkan nama model Ollama (contoh: llama3.2:3b, mistral:7b):",
                "custom_install_log_title": "Log Proses Download Model",
                "custom_install_btn": "⬇️ Mulai Install",
                "custom_cancel_btn": "✕ Batal",
                "custom_success_msg": "Model berhasil diinstal!",
                "ctx_copy": "📋 Salin Nama Model",
                "ctx_delete": "🗑 Hapus Model",
                "ctx_chat": "💬 Buka Chat di Terminal"
            },
            "en": {
                "title": "Ollama Hub (Linux Edition)",
                "checking": "Checking system...",
                "tab_models": "📦 Models & Matrix",
                "tab_api": "🔌 API & Integration",
                "tab_hints": "📘 About Ollama",
                "tab_pref": "⚙️ Preferences",
                "header_title": "Ollama & Hardware Compatibility Hub",
                "header_subtitle": "Local Model Management, API Endpoints & Hardware Compatibility",
                "btn_install": "📥 Install Ollama",
                "btn_open_store": "🚀 Recommended Models",
                "btn_custom_install": "📥 Custom Model Install",
                "frame_installed": "Installed Models",
                "btn_refresh": "🔄 Refresh List",
                "col_model_name": "Model Name",
                "col_size": "Size",
                "col_modified": "Last Modified",
                "col_status": "Compatibility Status",
                "col_desc": "Short Description",
                "copied_title": "Copied",
                "copied_msg": "Model name copied to clipboard:",
                "frame_logs": "Live Terminal & Process Output",
                "api_title": "Universal API & Integration Config",
                "api_left_card": "Local Endpoints & Details",
                "api_right_card": "Continue Integration Config (config.yaml)",
                "api_desc": (
                    "This application is built specifically for Linux systems.\n"
                    "Local endpoints can be used directly for Agents or Web UIs:\n\n"
                    "• Base URL        : http://localhost:11434\n"
                    "• OpenAI Endpoint : http://localhost:11434/v1\n"
                    "• Model Format    : qwen2.5-coder:1.5b-instruct, gemma2:2b, etc."
                ),
                "continue_config_title": "Continue Integration Config Example (config.yaml):",
                "btn_copy_config": "📋 Copy Continue Config",
                "config_copied_title": "Copied",
                "config_copied_msg": "Continue config example copied to clipboard!",
                "btn_ping": "🩺 Ping Ollama API",
                "hints_title": "About Ollama",
                "hints_card_title": "Official Ollama Information & Documentation",
                "hints_header_desc": (
                    "About Ollama:\n"
                    "Ollama is an open-source runtime designed to make it easy to run, create, "
                    "and distribute Large Language Models (LLMs) locally on your own device offline, "
                    "securely, and without cloud latency.\n\n"
                    "Official Documentation:\n"
                    "• Official Website & Docs : https://ollama.com/docs\n"
                    "• GitHub Repository       : https://github.com/ollama/ollama\n"
                ),
                "pref_title": "Application Preferences",
                "pref_card_title": "General & Environment Settings",
                "pref_lang_label": "Select Language:",
                "pref_term_label": "Terminal App for Chat:",
                "pref_config_note": f"Configuration is automatically loaded & saved to: {CONFIG_PATH}",
                "pref_save_btn": "💾 Save Preferences",
                "pref_saved_title": "Saved",
                "pref_saved_msg": "Preferences saved to config.json!",
                "pref_save_err": "Failed to save config.json.",
                "status_running": "● Ollama: RUNNING",
                "status_stopped": "● Ollama: STOPPED (Click to Start)",
                "status_not_installed": "● Ollama: NOT INSTALLED",
                "confirm_title": "Confirmation",
                "confirm_stop_server": "Stop the Ollama server service?",
                "confirm_delete_model": "Delete model",
                "deleted_msg": "successfully deleted.",
                "delete_failed_msg": "Failed to delete model.",
                "warning": "Warning",
                "warning_msg": "Please select a model row from the table first!",
                "custom_empty_msg": "Please enter a valid model name!",
                "downloading_title": "Downloading",
                "downloading_msg": "Starting download for model",
                "success_title": "Success",
                "success_msg": "Model downloaded:",
                "error_title": "Error",
                "error_msg": "Failed to download model",
                "install_info": "Installing Ollama via official script...",
                "install_success": "Ollama successfully installed!",
                "install_error": "Failed to install Ollama",
                "api_status_ok": "API Status",
                "api_status_ok_msg": "Ollama API is active and responding properly (HTTP 200)!",
                "api_error_title": "Connection Failed",
                "api_error": "Failed to connect to Ollama API",
                "modal_title": "🚀 Recommended Models & Universal Installer",
                "modal_header_hw": "Detected Hardware -> System",
                "modal_log_title": "Model Download Logs",
                "modal_btn_download": "⬇️ Download Selected Model",
                "modal_btn_close": "Close",
                "status_very_suitable": "[VERY SUITABLE / FAST]",
                "status_suitable": "[SUITABLE / CPU BOUND]",
                "status_heavy": "[HEAVY / LOW RAM]",
                "status_not_recommended": "[NOT RECOMMENDED]",
                "status_installed_badge": "[✓ INSTALLED]",
                "custom_install_title": "📥 Input & Install New Model",
                "custom_install_prompt": "Enter Ollama model name (e.g. llama3.2:3b, mistral:7b):",
                "custom_install_log_title": "Model Download Process Log",
                "custom_install_btn": "⬇️ Start Install",
                "custom_cancel_btn": "✕ Cancel",
                "custom_success_msg": "Model successfully installed!",
                "ctx_copy": "📋 Copy Model Name",
                "ctx_delete": "🗑 Delete Model",
                "ctx_chat": "💬 Open Chat in Terminal"
            }
        }

        self.root.title(self.texts[self.lang]["title"])
        self.root.geometry("1040x800")
        self.root.minsize(900, 680)
        self.root.configure(bg=THEME["bg_main"])

        # Dropdown listbox styling untuk Linux ttk.Combobox
        self.root.option_add("*TCombobox*Listbox.background", THEME["bg_card"])
        self.root.option_add("*TCombobox*Listbox.foreground", THEME["text_dark"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", THEME["primary"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

        self.setup_styles()

        # Header Frame (Soft Periwinkle / Sky Blue)
        header_frame = tk.Frame(
            root,
            bg=THEME["bg_header"],
            padx=22,
            pady=14,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        header_frame.pack(fill=tk.X)

        title_box = tk.Frame(header_frame, bg=THEME["bg_header"])
        title_box.pack(side=tk.LEFT)

        self.title_lbl = tk.Label(
            title_box,
            text=self.texts[self.lang]["header_title"],
            font=("Segoe UI", 14, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_header"]
        )
        self.title_lbl.pack(anchor=tk.W)

        self.subtitle_lbl = tk.Label(
            title_box,
            text=self.texts[self.lang]["header_subtitle"],
            font=("Segoe UI", 9),
            fg=THEME["text_muted"],
            bg=THEME["bg_header"]
        )
        self.subtitle_lbl.pack(anchor=tk.W, pady=(2, 0))

        header_right = tk.Frame(header_frame, bg=THEME["bg_header"])
        header_right.pack(side=tk.RIGHT)

        self.status_btn = tk.Button(
            header_right,
            text=self.texts[self.lang]["checking"],
            bg=THEME["warn_bg"],
            fg=THEME["warn_fg"],
            activebackground=THEME["primary_soft"],
            activeforeground=THEME["text_dark"],
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.on_status_click
        )
        self.status_btn.pack(side=tk.LEFT)

        # Navigation Bar Frame
        nav_frame = tk.Frame(
            root,
            bg=THEME["bg_nav"],
            padx=16,
            pady=9,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        nav_frame.pack(fill=tk.X)

        self.btn_nav_models = self._create_nav_button(nav_frame, 0)
        self.btn_nav_api = self._create_nav_button(nav_frame, 1)
        self.btn_nav_hints = self._create_nav_button(nav_frame, 2)
        self.btn_nav_pref = self._create_nav_button(nav_frame, 3)

        # Content Container
        self.content_container = tk.Frame(root, bg=THEME["bg_main"])
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        self.tab_models = tk.Frame(self.content_container, bg=THEME["bg_main"])
        self.tab_api = tk.Frame(self.content_container, bg=THEME["bg_main"])
        self.tab_hints = tk.Frame(self.content_container, bg=THEME["bg_main"])
        self.tab_pref = tk.Frame(self.content_container, bg=THEME["bg_main"])

        self.setup_models_tab()
        self.setup_api_tab()
        self.setup_hints_tab()
        self.setup_pref_tab()

        self.current_tab_index = 0
        self.switch_tab(0)

        # Bottom Status Bar
        self.bottom_bar = tk.Frame(
            root,
            bg=THEME["bg_header"],
            padx=18,
            pady=8,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_install_ollama = tk.Button(
            self.bottom_bar,
            text=self.texts[self.lang]["btn_install"],
            bg=THEME["danger_bg"],
            fg=THEME["danger_fg"],
            activebackground="#FECACA",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.install_ollama_action
        )
        self.btn_install_ollama.pack(side=tk.LEFT)
        self.btn_install_ollama.pack_forget()

        self.footer_lbl = tk.Label(
            self.bottom_bar,
            text="Ollama Hub • Linux Soft-Blue Edition",
            font=("Segoe UI", 9),
            fg=THEME["text_muted"],
            bg=THEME["bg_header"]
        )
        self.footer_lbl.pack(side=tk.RIGHT)

        init_db()
        self.apply_language()
        self.refresh_all_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            ".",
            background=THEME["bg_main"],
            foreground=THEME["text_dark"],
            font=("Segoe UI", 10)
        )

        style.configure(
            "TButton",
            background=THEME["primary_soft"],
            foreground=THEME["text_dark"],
            bordercolor=THEME["border"],
            borderwidth=1,
            focusthickness=2,
            focuscolor=THEME["primary"],
            padding=(12, 6),
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "TButton",
            background=[("pressed", THEME["primary"]), ("active", THEME["primary_soft_hover"])],
            foreground=[("pressed", "#FFFFFF"), ("active", THEME["text_dark"])]
        )

        style.configure(
            "SoftBlue.TCombobox",
            fieldbackground=THEME["bg_card_tint"],
            background=THEME["primary_soft"],
            foreground=THEME["text_dark"],
            bordercolor=THEME["border"],
            arrowcolor=THEME["primary"],
            borderwidth=1,
            padding=5,
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "SoftBlue.TCombobox",
            fieldbackground=[("readonly", THEME["bg_card_tint"]), ("focus", "#FFFFFF")],
            background=[("readonly", THEME["primary_soft"]), ("active", THEME["primary_soft_hover"])],
            foreground=[("readonly", THEME["text_dark"])]
        )

        style.configure(
            "SoftBlue.Treeview",
            background=THEME["bg_card"],
            foreground=THEME["text_dark"],
            fieldbackground=THEME["bg_card"],
            bordercolor=THEME["border"],
            rowheight=32,
            font=("Segoe UI", 10)
        )
        style.configure(
            "SoftBlue.Treeview.Heading",
            background=THEME["bg_header"],
            foreground=THEME["text_dark"],
            bordercolor=THEME["border"],
            relief="flat",
            padding=(8, 6),
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "SoftBlue.Treeview.Heading",
            background=[("active", THEME["primary_soft_hover"])]
        )
        style.map(
            "SoftBlue.Treeview",
            background=[("selected", THEME["primary_soft"])],
            foreground=[("selected", THEME["primary_hover"])]
        )

        style.configure(
            "Vertical.TScrollbar",
            background=THEME["primary_soft"],
            troughcolor=THEME["bg_card_tint"],
            bordercolor=THEME["border"],
            arrowcolor=THEME["primary"]
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=THEME["primary_soft"],
            troughcolor=THEME["bg_card_tint"],
            bordercolor=THEME["border"],
            arrowcolor=THEME["primary"]
        )

    def _create_nav_button(self, parent, index):
        btn = tk.Button(
            parent,
            text="",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            activebackground=THEME["primary_soft"],
            activeforeground=THEME["primary_hover"],
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=7,
            cursor="hand2",
            command=lambda: self.switch_tab(index)
        )
        btn.pack(side=tk.LEFT, padx=4)
        return btn

    def _make_card(self, parent, title_text="", accent_color=None):
        wrapper = tk.Frame(
            parent,
            bg=THEME["bg_card"],
            highlightthickness=1,
            highlightbackground=THEME["border"],
            padx=16,
            pady=14
        )
        header_lbl = None
        if title_text is not None:
            header_lbl = tk.Label(
                wrapper,
                text=title_text,
                font=("Segoe UI", 10, "bold"),
                fg=accent_color or THEME["primary_hover"],
                bg=THEME["bg_card"]
            )
            header_lbl.pack(anchor=tk.W, pady=(0, 10))
        return wrapper, header_lbl

    def detect_default_terminal(self):
        terminals = [
            "gnome-terminal",
            "xfce4-terminal",
            "mate-terminal",
            "konsole",
            "tilix",
            "alacritty",
            "kitty",
            "terminator",
            "xterm"
        ]
        for term in terminals:
            _, _, code = self.run_cmd(f"which {term}")
            if code == 0:
                return term
        return "xterm"

    def apply_language(self):
        """Memperbarui seluruh komponen teks UI sesuai self.lang secara menyeluruh."""
        t = self.texts[self.lang]

        self.root.title(t["title"])
        self.title_lbl.config(text=t["header_title"])
        self.subtitle_lbl.config(text=t["header_subtitle"])

        self.btn_nav_models.config(text=t["tab_models"])
        self.btn_nav_api.config(text=t["tab_api"])
        self.btn_nav_hints.config(text=t["tab_hints"])
        self.btn_nav_pref.config(text=t["tab_pref"])

        self.btn_install_ollama.config(text=t["btn_install"])

        # Tab Models
        if hasattr(self, "lbl_card_inst"):
            self.lbl_card_inst.config(text=t["frame_installed"])
            self.btn_refresh.config(text=t["btn_refresh"])
            self.btn_open_store.config(text=t["btn_open_store"])
            self.btn_custom_install.config(text=t["btn_custom_install"])

            self.list_installed.heading("name", text=t["col_model_name"], anchor=tk.W)
            self.list_installed.heading("size", text=t["col_size"], anchor=tk.W)
            self.list_installed.heading("modified", text=t["col_modified"], anchor=tk.W)

        if hasattr(self, "context_menu"):
            self.context_menu.entryconfig(0, label=t["ctx_copy"])
            self.context_menu.entryconfig(1, label=t["ctx_chat"])
            self.context_menu.entryconfig(2, label=t["ctx_delete"])

        if hasattr(self, "lbl_card_log"):
            self.lbl_card_log.config(text=t["frame_logs"])

        # Tab API
        if hasattr(self, "api_title_lbl"):
            self.api_title_lbl.config(text=t["api_title"])
            self.lbl_api_left.config(text=t["api_left_card"])
            self.lbl_api_right.config(text=t["api_right_card"])

            self.api_desc_txt.config(state=tk.NORMAL)
            self.api_desc_txt.delete("1.0", tk.END)
            self.api_desc_txt.insert(tk.END, t["api_desc"])
            self.api_desc_txt.config(state=tk.DISABLED)

            self.btn_ping.config(text=t["btn_ping"])
            self.btn_copy_config.config(text=t["btn_copy_config"])

        # Tab About Ollama
        if hasattr(self, "hints_title_lbl"):
            self.hints_title_lbl.config(text=t["hints_title"])
            self.lbl_hints_card.config(text=t["hints_card_title"])

            self.hints_txt.config(state=tk.NORMAL)
            self.hints_txt.delete("1.0", tk.END)
            self.hints_txt.insert(tk.END, t["hints_header_desc"])
            self.highlight_urls_in_hints()
            self.hints_txt.config(state=tk.DISABLED)

        # Tab Preferences
        if hasattr(self, "pref_title_lbl"):
            self.pref_title_lbl.config(text=t["pref_title"])
            self.lbl_pref_card.config(text=t["pref_card_title"])
            self.pref_lang_lbl.config(text=t["pref_lang_label"])
            self.pref_term_lbl.config(text=t["pref_term_label"])
            self.pref_note_lbl.config(text=t["pref_config_note"])
            self.pref_save_btn.config(text=t["pref_save_btn"])
            self.lang_combobox.set("Bahasa Indonesia" if self.lang == "id" else "English")

    def switch_tab(self, index):
        self.current_tab_index = index
        for tab in (self.tab_models, self.tab_api, self.tab_hints, self.tab_pref):
            tab.pack_forget()

        nav_buttons = (
            self.btn_nav_models,
            self.btn_nav_api,
            self.btn_nav_hints,
            self.btn_nav_pref
        )
        for btn in nav_buttons:
            btn.config(bg=THEME["bg_card"], fg=THEME["text_muted"])

        tabs = (self.tab_models, self.tab_api, self.tab_hints, self.tab_pref)
        tabs[index].pack(fill=tk.BOTH, expand=True)
        nav_buttons[index].config(bg=THEME["primary"], fg="#FFFFFF")

    def run_cmd(self, cmd, timeout=15):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), 1

    def log_to_terminal(self, message):
        def _log():
            self.log_txt.config(state=tk.NORMAL)
            self.log_txt.insert(tk.END, message + "\n")
            self.log_txt.see(tk.END)
            self.log_txt.config(state=tk.DISABLED)
        self.root.after(0, _log)

    def refresh_all_data(self):
        t = self.texts[self.lang]
        _, _, code = self.run_cmd("ollama --version")
        if code != 0:
            _, _, c2 = self.run_cmd("which ollama")
            if c2 != 0:
                self.status_btn.config(
                    text=t["status_not_installed"],
                    bg=THEME["danger_bg"],
                    fg=THEME["danger_fg"]
                )
                self.btn_install_ollama.pack(side=tk.LEFT)
            else:
                self.update_running_status()
                self.btn_install_ollama.pack_forget()
        else:
            self.update_running_status()
            self.btn_install_ollama.pack_forget()

        self.load_installed_models()

    def update_running_status(self):
        t = self.texts[self.lang]
        _, _, rc = self.run_cmd("pgrep ollama")
        if rc == 0:
            self.status_btn.config(
                text=t["status_running"],
                bg=THEME["success_bg"],
                fg=THEME["success_fg"]
            )
        else:
            self.status_btn.config(
                text=t["status_stopped"],
                bg=THEME["warn_bg"],
                fg=THEME["warn_fg"]
            )

    def on_status_click(self):
        t = self.texts[self.lang]
        _, _, rc = self.run_cmd("pgrep ollama")

        if rc != 0:
            self.log_to_terminal("[*] Starting Ollama server...")

            def start_server():
                try:
                    self.run_cmd("pkexec systemctl start ollama")
                    time.sleep(2)
                    self.root.after(0, self.refresh_all_data)
                    self.log_to_terminal("[+] Ollama server started successfully!")
                except Exception as e:
                    self.log_to_terminal(f"[!] Failed to start Ollama server: {e}")

            threading.Thread(target=start_server, daemon=True).start()
        else:
            if messagebox.askyesno(t["confirm_title"], t["confirm_stop_server"]):
                self.log_to_terminal("[*] Stopping Ollama server via systemctl...")

                def stop_server():
                    _, err, kill_rc = self.run_cmd("pkexec systemctl stop ollama")
                    time.sleep(1)
                    self.root.after(0, self.refresh_all_data)
                    if kill_rc == 0:
                        self.log_to_terminal("[+] Ollama server stopped properly.")
                    else:
                        self.log_to_terminal(f"[!] Failed to stop server: {err}")

                threading.Thread(target=stop_server, daemon=True).start()

    def install_ollama_action(self):
        def worker():
            t = self.texts[self.lang]
            self.log_to_terminal(f"[*] {t['install_info']}")
            self.root.after(0, lambda: messagebox.showinfo("Install", t["install_info"]))
            _, err, code = self.run_cmd("curl -fsSL https://ollama.com/install.sh | sh", timeout=300)
            if code == 0:
                self.log_to_terminal(f"[+] {t['install_success']}")
                self.root.after(0, lambda: messagebox.showinfo(t["success_title"], t["install_success"]))
            else:
                self.log_to_terminal(f"[!] {t['install_error']}: {err}")
                self.root.after(0, lambda: messagebox.showerror(t["error_title"], f"{t['install_error']}: {err}"))
            self.root.after(0, self.refresh_all_data)

        threading.Thread(target=worker, daemon=True).start()

    def setup_models_tab(self):
        t = self.texts[self.lang]

        # Kartu Atas: Daftar Model Terinstal
        card_inst, self.lbl_card_inst = self._make_card(self.tab_models, t["frame_installed"])
        card_inst.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        inst_container = tk.Frame(card_inst, bg=THEME["bg_card"])
        inst_container.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "size", "modified")
        self.list_installed = ttk.Treeview(
            inst_container,
            columns=columns,
            show="headings",
            style="SoftBlue.Treeview",
            height=8
        )

        self.list_installed.heading("name", text=t["col_model_name"], anchor=tk.W)
        self.list_installed.heading("size", text=t["col_size"], anchor=tk.W)
        self.list_installed.heading("modified", text=t["col_modified"], anchor=tk.W)

        self.list_installed.column("name", width=360, anchor=tk.W)
        self.list_installed.column("size", width=160, anchor=tk.W)
        self.list_installed.column("modified", width=340, anchor=tk.W)

        self.list_installed.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        inst_scroll = ttk.Scrollbar(inst_container, orient=tk.VERTICAL, command=self.list_installed.yview)
        inst_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_installed.config(yscrollcommand=inst_scroll.set)

        # Context Menu (Klik Kanan) bernuansa biru lembut
        self.context_menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=THEME["bg_card"],
            fg=THEME["text_dark"],
            activebackground=THEME["primary"],
            activeforeground="#FFFFFF",
            font=("Segoe UI", 10, "bold")
        )
        self.context_menu.add_command(label=t["ctx_copy"], command=self.copy_model_name_action)
        self.context_menu.add_command(label=t["ctx_chat"], command=self.open_chat_in_terminal_action)
        self.context_menu.add_command(label=t["ctx_delete"], command=self.delete_model_action)

        def show_context_menu(event):
            item = self.list_installed.identify_row(event.y)
            if item:
                self.list_installed.selection_set(item)
                try:
                    self.context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.context_menu.grab_release()
            else:
                try:
                    self.context_menu.unpost()
                except Exception:
                    pass

        def on_table_click(event):
            item = self.list_installed.identify_row(event.y)
            if not item:
                self.list_installed.selection_remove(self.list_installed.selection())
                try:
                    self.context_menu.unpost()
                except Exception:
                    pass

        self.list_installed.bind("<Button-3>", show_context_menu)
        self.list_installed.bind("<Button-2>", show_context_menu)
        self.list_installed.bind("<Button-1>", on_table_click)

        def global_click_handler(event):
            try:
                self.context_menu.unpost()
            except Exception:
                pass

        self.root.bind("<Button-1>", global_click_handler, add="+")

        # Bar Tombol Aksi
        btn_frame = tk.Frame(card_inst, bg=THEME["bg_card"])
        btn_frame.pack(fill=tk.X, pady=(12, 0))

        self.btn_refresh = tk.Button(
            btn_frame,
            text=t["btn_refresh"],
            bg=THEME["primary_soft"],
            fg=THEME["primary_hover"],
            activebackground=THEME["primary_soft_hover"],
            activeforeground=THEME["text_dark"],
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.refresh_all_data
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_open_store = tk.Button(
            btn_frame,
            text=t["btn_open_store"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.open_model_store_modal
        )
        self.btn_open_store.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_custom_install = tk.Button(
            btn_frame,
            text=t["btn_custom_install"],
            bg=THEME["accent_sky"],
            fg="#FFFFFF",
            activebackground=THEME["accent_sky_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.open_custom_install_modal
        )
        self.btn_custom_install.pack(side=tk.LEFT)

        # Kartu Bawah: Live Terminal Output Log
        card_log, self.lbl_card_log = self._make_card(self.tab_models, t["frame_logs"])
        card_log.pack(fill=tk.BOTH, expand=True)

        self.log_txt = scrolledtext.ScrolledText(
            card_log,
            bg=THEME["term_bg"],
            fg=THEME["term_fg"],
            font=("JetBrains Mono", 9),
            height=9,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=8
        )
        self.log_txt.pack(fill=tk.BOTH, expand=True)
        self.log_txt.config(state=tk.DISABLED)

    def open_custom_install_modal(self):
        t = self.texts[self.lang]
        modal = tk.Toplevel(self.root)
        modal.title(t["custom_install_title"])
        modal.geometry("720x500")
        modal.configure(bg=THEME["bg_main"])
        modal.transient(self.root)
        modal.grab_set()

        input_card, _ = self._make_card(modal, None)
        input_card.pack(fill=tk.X, padx=16, pady=(16, 10))

        lbl_prompt = tk.Label(
            input_card,
            text=t["custom_install_prompt"],
            font=("Segoe UI", 10, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_prompt.pack(anchor=tk.W, pady=(0, 8))

        entry_frame = tk.Frame(input_card, bg=THEME["bg_card"])
        entry_frame.pack(fill=tk.X)

        model_entry = tk.Entry(
            entry_frame,
            font=("JetBrains Mono", 11),
            bg=THEME["bg_card_tint"],
            fg=THEME["text_dark"],
            insertbackground=THEME["primary"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["primary"]
        )
        model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        model_entry.focus()

        action_frame = tk.Frame(
            modal,
            bg=THEME["bg_header"],
            padx=16,
            pady=10,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        action_frame.pack(side=tk.BOTTOM, fill=tk.X)

        log_card, _ = self._make_card(modal, t["custom_install_log_title"])
        log_card.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=16, pady=(0, 14))

        log_txt = scrolledtext.ScrolledText(
            log_card,
            bg=THEME["term_bg"],
            fg=THEME["term_fg"],
            font=("JetBrains Mono", 9),
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=8
        )
        log_txt.pack(fill=tk.BOTH, expand=True)
        log_txt.config(state=tk.DISABLED)

        def log_to_custom_modal(msg):
            def _w():
                log_txt.config(state=tk.NORMAL)
                log_txt.insert(tk.END, msg + "\n")
                log_txt.see(tk.END)
                log_txt.config(state=tk.DISABLED)
            modal.after(0, _w)

        proc_holder = {"process": None, "cancelled": False}

        def start_custom_download():
            model_name = model_entry.get().strip()
            if not model_name:
                messagebox.showwarning(t["warning"], t["custom_empty_msg"], parent=modal)
                return

            btn_start.config(state=tk.DISABLED)
            model_entry.config(state=tk.DISABLED)

            def worker():
                log_to_custom_modal(f"[*] {t['downloading_msg']}: {model_name}...")
                process = subprocess.Popen(
                    f"ollama pull {model_name}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                proc_holder["process"] = process
                ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

                for line in iter(process.stdout.readline, ""):
                    if proc_holder["cancelled"]:
                        break
                    clean_line = ansi_escape.sub("", line).replace("\r", "").strip()
                    if clean_line:
                        log_to_custom_modal(f"    {clean_line}")

                process.wait()

                if proc_holder["cancelled"]:
                    log_to_custom_modal("[!] Download cancelled.")
                    return

                if process.returncode == 0:
                    log_to_custom_modal(f"[+] {t['custom_success_msg']} ({model_name})")
                    self.root.after(0, self.refresh_all_data)
                    modal.after(0, lambda: [
                        messagebox.showinfo(t["success_title"], f"{t['custom_success_msg']}\n\n{model_name}", parent=modal),
                        modal.destroy()
                    ])
                else:
                    log_to_custom_modal(f"[!] {t['error_msg']}: {model_name}")
                    modal.after(0, lambda: [
                        messagebox.showerror(t["error_title"], f"{t['error_msg']}: {model_name}", parent=modal),
                        btn_start.config(state=tk.NORMAL),
                        model_entry.config(state=tk.NORMAL)
                    ])

            threading.Thread(target=worker, daemon=True).start()

        def cancel_action():
            if proc_holder["process"] and proc_holder["process"].poll() is None:
                proc_holder["cancelled"] = True
                try:
                    proc_holder["process"].terminate()
                except Exception:
                    pass
            modal.destroy()

        btn_start = tk.Button(
            entry_frame,
            text=t["custom_install_btn"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=6,
            cursor="hand2",
            command=start_custom_download
        )
        btn_start.pack(side=tk.RIGHT)

        btn_cancel = tk.Button(
            action_frame,
            text=t["custom_cancel_btn"],
            bg=THEME["danger_bg"],
            fg=THEME["danger_fg"],
            activebackground="#FECACA",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=7,
            cursor="hand2",
            command=cancel_action
        )
        btn_cancel.pack(side=tk.RIGHT)

        modal.protocol("WM_DELETE_WINDOW", cancel_action)

    def open_model_store_modal(self):
        t = self.texts[self.lang]
        modal = tk.Toplevel(self.root)
        modal.title(t["modal_title"])
        modal.geometry("1020x660")
        modal.configure(bg=THEME["bg_main"])
        modal.transient(self.root)
        modal.grab_set()

        top_frame = tk.Frame(
            modal,
            bg=THEME["bg_header"],
            padx=18,
            pady=12,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        top_frame.pack(side=tk.TOP, fill=tk.X)

        total_ram_gb = 8
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "MemTotal" in line:
                        total_ram_gb = round(int(line.split()[1]) / (1024 ** 2))
                        break
        except Exception:
            pass

        vram_gb = 0
        try:
            out, _, code = self.run_cmd("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits")
            if code == 0 and out.strip():
                vram_mb = int(out.strip().splitlines()[0])
                vram_gb = round(vram_mb / 1024)
        except Exception:
            pass

        hw_lbl = tk.Label(
            top_frame,
            text=f"💻 {t['modal_header_hw']} RAM ~{total_ram_gb} GB  |  GPU VRAM ~{vram_gb} GB",
            font=("Segoe UI", 11, "bold"),
            fg=THEME["primary_hover"],
            bg=THEME["bg_header"]
        )
        hw_lbl.pack(anchor=tk.W)

        action_frame = tk.Frame(
            modal,
            bg=THEME["bg_header"],
            padx=16,
            pady=10,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        action_frame.pack(side=tk.BOTTOM, fill=tk.X)

        log_card, _ = self._make_card(modal, t["modal_log_title"])
        log_card.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 12))

        modal_log_txt = scrolledtext.ScrolledText(
            log_card,
            bg=THEME["term_bg"],
            fg=THEME["term_fg"],
            font=("JetBrains Mono", 9),
            height=6,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=6
        )
        modal_log_txt.pack(fill=tk.BOTH, expand=True)
        modal_log_txt.config(state=tk.DISABLED)

        list_card, _ = self._make_card(modal, None)
        list_card.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=16, pady=12)

        list_container = tk.Frame(list_card, bg=THEME["bg_card"])
        list_container.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "size", "status", "desc")
        self.modal_list = ttk.Treeview(
            list_container,
            columns=columns,
            show="headings",
            style="SoftBlue.Treeview"
        )

        self.modal_list.heading("name", text=t["col_model_name"], anchor=tk.W)
        self.modal_list.heading("size", text=t["col_size"], anchor=tk.W)
        self.modal_list.heading("status", text=t["col_status"], anchor=tk.W)
        self.modal_list.heading("desc", text=t["col_desc"], anchor=tk.W)

        self.modal_list.column("name", width=230, anchor=tk.W, stretch=False)
        self.modal_list.column("size", width=95, anchor=tk.W, stretch=False)
        self.modal_list.column("status", width=235, anchor=tk.W, stretch=False)
        self.modal_list.column("desc", width=550, anchor=tk.W, stretch=True)

        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        self.modal_list.grid(row=0, column=0, sticky="nsew")

        modal_scroll_y = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.modal_list.yview)
        modal_scroll_y.grid(row=0, column=1, sticky="ns")
        self.modal_list.config(yscrollcommand=modal_scroll_y.set)

        modal_scroll_x = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.modal_list.xview)
        modal_scroll_x.grid(row=1, column=0, sticky="ew")
        self.modal_list.config(xscrollcommand=modal_scroll_x.set)

        out, _, code = self.run_cmd("ollama list")
        installed_models = []
        if code == 0:
            for line in out.splitlines()[1:]:
                if line.strip():
                    installed_models.append(line.split()[0])

        db = load_db()
        for item in db:
            min_ram = item.get("min_ram_gb", 4)
            min_vram = item.get("min_vram_gb", 2)

            if vram_gb >= min_vram:
                status = t["status_very_suitable"]
            elif total_ram_gb >= min_ram:
                status = t["status_suitable"]
            elif total_ram_gb >= (min_ram - 2):
                status = t["status_heavy"]
            else:
                status = t["status_not_recommended"]

            if item["name"] in installed_models:
                status = t["status_installed_badge"]

            desc = item.get("description_id") if self.lang == "id" else item.get("description_en")
            if not desc:
                desc = item.get("desc", "-")

            self.modal_list.insert("", tk.END, values=(item["name"], item["size"], status, desc))

        def log_to_modal(msg):
            def _w():
                modal_log_txt.config(state=tk.NORMAL)
                modal_log_txt.insert(tk.END, msg + "\n")
                modal_log_txt.see(tk.END)
                modal_log_txt.config(state=tk.DISABLED)
            modal.after(0, _w)

        def install_selected_model():
            selection = self.modal_list.selection()
            if not selection:
                messagebox.showwarning(t["warning"], t["warning_msg"], parent=modal)
                return

            item_id = selection[0]
            values = self.modal_list.item(item_id, "values")
            model_name = values[0]

            def worker():
                log_to_modal(f"[*] {t['downloading_msg']}: {model_name}...")
                process = subprocess.Popen(
                    f"ollama pull {model_name}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

                for line in iter(process.stdout.readline, ""):
                    clean_line = ansi_escape.sub("", line).replace("\r", "").strip()
                    if clean_line:
                        log_to_modal(f"    {clean_line}")

                process.wait()
                if process.returncode == 0:
                    log_to_modal(f"[+] {t['success_msg']} {model_name}")
                    self.root.after(0, self.refresh_all_data)
                    modal.after(0, lambda: [
                        messagebox.showinfo(t["success_title"], f"{t['success_msg']} {model_name}!", parent=modal),
                        self.modal_list.item(item_id, values=(model_name, values[1], t["status_installed_badge"], values[3]))
                    ])
                else:
                    log_to_modal(f"[!] {t['error_msg']}: {model_name}")
                    modal.after(0, lambda: messagebox.showerror(t["error_title"], f"{t['error_msg']}: {model_name}", parent=modal))

            threading.Thread(target=worker, daemon=True).start()

        btn_install = tk.Button(
            action_frame,
            text=t["modal_btn_download"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
            cursor="hand2",
            command=install_selected_model
        )
        btn_install.pack(side=tk.LEFT)

        btn_close = ttk.Button(action_frame, text=t["modal_btn_close"], command=modal.destroy)
        btn_close.pack(side=tk.RIGHT)

    def load_installed_models(self):
        for row in self.list_installed.get_children():
            self.list_installed.delete(row)

        out, _, code = self.run_cmd("ollama list")
        if code == 0:
            for line in out.splitlines()[1:]:
                if line.strip():
                    cols = re.split(r"\s{2,}", line.strip())
                    if len(cols) >= 4:
                        self.list_installed.insert("", tk.END, values=(cols[0], cols[2], cols[3]))

    def copy_model_name_action(self):
        try:
            t = self.texts[self.lang]
            selection = self.list_installed.selection()
            if not selection:
                messagebox.showwarning(t["warning"], t["warning_msg"])
                return

            model_name = self.list_installed.item(selection[0], "values")[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(model_name)
            self.root.update()

            self.log_to_terminal(f"[+] Copied model name to clipboard: {model_name}")
            messagebox.showinfo(t["copied_title"], f"{t['copied_msg']}\n\n{model_name}")
        except Exception as e:
            messagebox.showerror(self.texts[self.lang]["error_title"], str(e))

    def open_chat_in_terminal_action(self):
        try:
            t = self.texts[self.lang]
            selection = self.list_installed.selection()
            if not selection:
                messagebox.showwarning(t["warning"], t["warning_msg"])
                return

            model_name = self.list_installed.item(selection[0], "values")[0]
            terminal_cmd = self.preferred_terminal.strip() or "gnome-terminal"

            if "gnome-terminal" in terminal_cmd:
                full_cmd = f"{terminal_cmd} -- bash -c 'ollama run {model_name}; exec bash'"
            elif "konsole" in terminal_cmd:
                full_cmd = f"{terminal_cmd} -e bash -c 'ollama run {model_name}; exec bash'"
            elif "xfce4-terminal" in terminal_cmd or "mate-terminal" in terminal_cmd:
                full_cmd = f"{terminal_cmd} -e 'bash -c \"ollama run {model_name}; exec bash\"'"
            elif any(term in terminal_cmd for term in ("alacritty", "kitty", "tilix", "terminator")):
                full_cmd = f"{terminal_cmd} -e bash -c 'ollama run {model_name}; exec bash'"
            else:
                full_cmd = f"{terminal_cmd} -e 'ollama run {model_name}; bash'"

            self.log_to_terminal(f"[*] Opening chat in terminal for {model_name} using: {terminal_cmd}")
            threading.Thread(target=lambda: subprocess.Popen(full_cmd, shell=True), daemon=True).start()
        except Exception as e:
            messagebox.showerror(self.texts[self.lang]["error_title"], str(e))

    def delete_model_action(self):
        try:
            t = self.texts[self.lang]
            selection = self.list_installed.selection()
            if not selection:
                messagebox.showwarning(t["warning"], t["warning_msg"])
                return

            model_name = self.list_installed.item(selection[0], "values")[0]
            if messagebox.askyesno(t["confirm_title"], f"{t['confirm_delete_model']} {model_name}?"):
                self.log_to_terminal(f"[*] Deleting model {model_name}...")
                _, _, code = self.run_cmd(f"ollama rm {model_name}")
                if code == 0:
                    self.log_to_terminal(f"[+] Model {model_name} successfully deleted.")
                    messagebox.showinfo(t["success_title"], f"Model {model_name} {t['deleted_msg']}")
                    self.refresh_all_data()
                else:
                    self.log_to_terminal(f"[!] Failed to delete model {model_name}")
                    messagebox.showerror(t["error_title"], t["delete_failed_msg"])
        except Exception as e:
            messagebox.showerror(self.texts[self.lang]["error_title"], str(e))

    def setup_api_tab(self):
        t = self.texts[self.lang]
        frame = tk.Frame(self.tab_api, bg=THEME["bg_main"])
        frame.pack(fill=tk.BOTH, expand=True)

        self.api_title_lbl = tk.Label(
            frame,
            text=t["api_title"],
            font=("Segoe UI", 12, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_main"]
        )
        self.api_title_lbl.pack(anchor=tk.W, pady=(0, 12))

        api_container = tk.Frame(frame, bg=THEME["bg_main"])
        api_container.pack(fill=tk.BOTH, expand=True)
        api_container.grid_columnconfigure(0, weight=1, uniform="group1")
        api_container.grid_columnconfigure(1, weight=1, uniform="group1")
        api_container.grid_rowconfigure(0, weight=1)

        # Kartu Kiri: Endpoint Lokal
        left_card, self.lbl_api_left = self._make_card(api_container, t["api_left_card"])
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.api_desc_txt = scrolledtext.ScrolledText(
            left_card,
            bg=THEME["bg_card_tint"],
            fg=THEME["text_dark"],
            font=("JetBrains Mono", 10),
            height=14,
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.api_desc_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        self.api_desc_txt.insert(tk.END, t["api_desc"])
        self.api_desc_txt.config(state=tk.DISABLED)

        self.btn_ping = tk.Button(
            left_card,
            text=t["btn_ping"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.test_api
        )
        self.btn_ping.pack(anchor=tk.W)

        # Kartu Kanan: Konfigurasi Continue YAML
        right_card, self.lbl_api_right = self._make_card(api_container, t["api_right_card"])
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        continue_yaml_content = (
            "name: Ollama Local\n"
            "version: 1.0.0\n"
            "schema: v1\n"
            "models:\n"
            "  - name: Local Qwen2.5 Coder 3B (Fast Edit)\n"
            "    provider: ollama\n"
            "    model: qwen2.5-coder:3b\n"
            "    apiBase: http://127.0.0.1:11434\n"
            "    roles:\n"
            "      - chat\n"
            "      - edit\n"
            "      - apply\n"
            "    defaultCompletionOptions:\n"
            "      contextLength: 8192\n"
            "      temperature: 0.1\n"
            "  - name: Local Gemma 2 2B (General)\n"
            "    provider: ollama\n"
            "    model: gemma2:2b\n"
            "    apiBase: http://127.0.0.1:11434\n"
            "    roles:\n"
            "      - chat\n"
            "    defaultCompletionOptions:\n"
            "      contextLength: 8192\n"
            "      temperature: 0.2"
        )

        self.continue_txt = scrolledtext.ScrolledText(
            right_card,
            bg=THEME["term_bg"],
            fg=THEME["term_fg"],
            font=("JetBrains Mono", 9),
            height=14,
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=10
        )
        self.continue_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        self.continue_txt.insert(tk.END, continue_yaml_content)
        self.continue_txt.config(state=tk.DISABLED)

        def copy_continue_config():
            cur_t = self.texts[self.lang]
            self.root.clipboard_clear()
            self.root.clipboard_append(continue_yaml_content)
            self.root.update()
            self.log_to_terminal("[+] Copied Continue config example to clipboard.")
            messagebox.showinfo(cur_t["config_copied_title"], cur_t["config_copied_msg"])

        self.btn_copy_config = tk.Button(
            right_card,
            text=t["btn_copy_config"],
            bg=THEME["primary_soft"],
            fg=THEME["primary_hover"],
            activebackground=THEME["primary_soft_hover"],
            activeforeground=THEME["text_dark"],
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
            cursor="hand2",
            command=copy_continue_config
        )
        self.btn_copy_config.pack(anchor=tk.W)

    def test_api(self):
        t = self.texts[self.lang]
        try:
            req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
            if req.status == 200:
                self.log_to_terminal("[+] Ollama API Ping OK: Status 200")
                messagebox.showinfo(t["api_status_ok"], t["api_status_ok_msg"])
        except Exception as e:
            self.log_to_terminal(f"[!] Ollama API Ping Failed: {e}")
            messagebox.showerror(t["api_error_title"], f"{t['api_error']}:\n{e}")

    def setup_hints_tab(self):
        t = self.texts[self.lang]
        frame = tk.Frame(self.tab_hints, bg=THEME["bg_main"])
        frame.pack(fill=tk.BOTH, expand=True)

        self.hints_title_lbl = tk.Label(
            frame,
            text=t["hints_title"],
            font=("Segoe UI", 12, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_main"]
        )
        self.hints_title_lbl.pack(anchor=tk.W, pady=(0, 12))

        hints_card, self.lbl_hints_card = self._make_card(frame, t["hints_card_title"])
        hints_card.pack(fill=tk.BOTH, expand=True)

        self.hints_txt = scrolledtext.ScrolledText(
            hints_card,
            bg=THEME["bg_card_tint"],
            fg=THEME["text_dark"],
            font=("Segoe UI", 10),
            height=18,
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.hints_txt.pack(fill=tk.BOTH, expand=True)
        self.hints_txt.insert(tk.END, t["hints_header_desc"])

        self.hints_txt.tag_config("link", foreground=THEME["primary"], underline=True, font=("Segoe UI", 10, "bold"))
        self.hints_txt.tag_bind("link", "<Enter>", lambda e: self.hints_txt.config(cursor="hand2"))
        self.hints_txt.tag_bind("link", "<Leave>", lambda e: self.hints_txt.config(cursor=""))
        self.hints_txt.tag_bind("link", "<Button-1>", self.on_hints_link_click)

        self.highlight_urls_in_hints()
        self.hints_txt.config(state=tk.DISABLED)

    def setup_pref_tab(self):
        t = self.texts[self.lang]
        frame = tk.Frame(self.tab_pref, bg=THEME["bg_main"])
        frame.pack(fill=tk.BOTH, expand=True)

        self.pref_title_lbl = tk.Label(
            frame,
            text=t["pref_title"],
            font=("Segoe UI", 12, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_main"]
        )
        self.pref_title_lbl.pack(anchor=tk.W, pady=(0, 12))

        pref_card, self.lbl_pref_card = self._make_card(frame, t["pref_card_title"])
        pref_card.pack(fill=tk.X)

        # Baris Pilihan Bahasa
        lang_frame = tk.Frame(pref_card, bg=THEME["bg_card"])
        lang_frame.pack(fill=tk.X, pady=8)

        self.pref_lang_lbl = tk.Label(
            lang_frame,
            text=t["pref_lang_label"],
            font=("Segoe UI", 10, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_card"],
            width=36,
            anchor=tk.W
        )
        self.pref_lang_lbl.pack(side=tk.LEFT)

        self.lang_combobox = ttk.Combobox(
            lang_frame,
            values=["Bahasa Indonesia", "English"],
            state="readonly",
            width=24,
            font=("Segoe UI", 10, "bold"),
            style="SoftBlue.TCombobox"
        )
        self.lang_combobox.pack(side=tk.LEFT, padx=8)
        self.lang_combobox.set("Bahasa Indonesia" if self.lang == "id" else "English")

        # Baris Pilihan Terminal
        term_frame = tk.Frame(pref_card, bg=THEME["bg_card"])
        term_frame.pack(fill=tk.X, pady=8)

        self.pref_term_lbl = tk.Label(
            term_frame,
            text=t["pref_term_label"],
            font=("Segoe UI", 10, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_card"],
            width=36,
            anchor=tk.W
        )
        self.pref_term_lbl.pack(side=tk.LEFT)

        self.term_entry = tk.Entry(
            term_frame,
            font=("JetBrains Mono", 10),
            bg=THEME["bg_card_tint"],
            fg=THEME["text_dark"],
            insertbackground=THEME["primary"],
            relief=tk.FLAT,
            width=26,
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["primary"]
        )
        self.term_entry.pack(side=tk.LEFT, padx=8, ipady=5)
        self.term_entry.insert(0, self.preferred_terminal)

        # Info path config.json
        self.pref_note_lbl = tk.Label(
            pref_card,
            text=t["pref_config_note"],
            font=("Segoe UI", 9, "italic"),
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        self.pref_note_lbl.pack(anchor=tk.W, pady=(12, 0))

        # Tombol Simpan
        btn_frame = tk.Frame(pref_card, bg=THEME["bg_card"])
        btn_frame.pack(fill=tk.X, pady=(18, 4))

        self.pref_save_btn = tk.Button(
            btn_frame,
            text=t["pref_save_btn"],
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.save_preferences_action
        )
        self.pref_save_btn.pack(anchor=tk.W)

    def save_preferences_action(self):
        selected_lang_str = self.lang_combobox.get()
        self.lang = "id" if selected_lang_str == "Bahasa Indonesia" else "en"
        self.preferred_terminal = self.term_entry.get().strip() or self.detect_default_terminal()

        # Perbarui & simpan ke config.json
        self.config["lang"] = self.lang
        self.config["terminal"] = self.preferred_terminal
        saved = save_config(self.config)

        # Terapkan bahasa & perbarui status bar
        self.apply_language()
        self.refresh_all_data()

        t = self.texts[self.lang]
        if saved:
            self.log_to_terminal(f"[+] Saved to config.json -> lang: '{self.lang}', terminal: '{self.preferred_terminal}'")
            messagebox.showinfo(t["pref_saved_title"], t["pref_saved_msg"])
        else:
            self.log_to_terminal("[!] Failed writing to config.json")
            messagebox.showerror(t["error_title"], t["pref_save_err"])

    def highlight_urls_in_hints(self):
        urls = ["https://ollama.com/docs", "https://github.com/ollama/ollama"]
        for url in urls:
            idx = "1.0"
            while True:
                idx = self.hints_txt.search(url, idx, stopindex=tk.END)
                if not idx:
                    break
                end_idx = f"{idx}+{len(url)}c"
                self.hints_txt.tag_add("link", idx, end_idx)
                idx = end_idx

    def on_hints_link_click(self, event):
        try:
            index = self.hints_txt.index(f"@{event.x},{event.y}")
            if "link" in self.hints_txt.tag_names(index):
                line_string = self.hints_txt.get(f"{index} linestart", f"{index} lineend")
                for url in ["https://ollama.com/docs", "https://github.com/ollama/ollama"]:
                    if url in line_string:
                        webbrowser.open(url)
                        self.log_to_terminal(f"[*] Opening official doc URL: {url}")
                        break
        except Exception as e:
            self.log_to_terminal(f"[!] URL click error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalOllamaManager(root)
    root.mainloop()