import os
import json
import subprocess
import threading
import re
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "models_db.json")

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
        with open(DB_PATH, "w") as f:
            json.dump(GENERAL_MODELS_DB, f, indent=4)

def load_db():
    init_db()
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except:
        return GENERAL_MODELS_DB

class UniversalOllamaManager:
    def __init__(self, root):
        self.root = root
        self.lang = "id"  # Default Bahasa Indonesia
        self.preferred_terminal = self.detect_default_terminal()

        self.texts = {
            "id": {
                "title": "Ollama Hub (Linux Edition)",
                "checking": "Memeriksa sistem...",
                "tab_models": "Model & Matriks ",
                "tab_api": "API & Integrasi ",
                "tab_hints": "Tentang  Ollama ",
                "tab_pref": "Preferences ",
                "header_title": "Ollama & Hardware Compatibility Hub",
                "btn_install": "📥 Install Ollama",
                "btn_open_store": "🚀 Rekomendasi Install Model",
                "frame_installed": " Model yang Sudah Terinstal (Installed) ",
                "btn_refresh": "🔄 Muat Ulang",
                "copied_title": "Disalin",
                "copied_msg": "Nama model berhasil disalin ke clipboard:",
                "frame_logs": " Live Terminal & Proses Output ",
                "api_title": "Konfigurasi API & Integrasi Universal",
                "api_desc": (
                    "Aplikasi ini dikhususkan untuk sistem operasi Linux.\n"
                    "Endpoint lokal dapat langsung digunakan untuk Hermes Agent atau Web UI:\n\n"
                    "• Base URL        : http://localhost:11434\n"
                    "• OpenAI Endpoint : http://localhost:11434/v1\n"
                    "• Format Model    : qwen2.5-coder:1.5b-instruct, gemma2:2b, dll."
                ),
                "continue_config_title": "Contoh Konfigurasi Integrasi Continue (config.yaml):",
                "btn_copy_config": "📋 Salin Config Continue",
                "config_copied_title": "Disalin",
                "config_copied_msg": "Contoh konfigurasi Continue berhasil disalin ke clipboard!",
                "btn_ping": "Uji Ping API Ollama",
                "hints_title": "Tentang Ollama",
                "hints_header_desc": (
                    "Tentang Ollama:\n"
                    "Ollama adalah alat/runtime open-source yang dirancang untuk memudahkan pengguna menjalankan, membuat, "
                    "dan mendistribusikan Large Language Models (LLM) secara lokal di perangkat Anda sendiri secara offline, "
                    "aman, dan tanpa latensi cloud.\n\n"
                    "Dokumentasi Resmi:\n"
                    "• Website & Docs Resmi : https://ollama.com/docs\n"
                    "• Repositori GitHub    : https://github.com/ollama/ollama\n\n"
                ),
                "pref_title": "Pengaturan Preferensi Aplikasi (Preferences)",
                "pref_lang_label": "Pilih Bahasa (Language):",
                "pref_term_label": "Aplikasi Terminal untuk Chat (Terminal Command):",
                "pref_save_btn": "💾 Simpan Preferensi",
                "pref_saved_title": "Tersimpan",
                "pref_saved_msg": "Pengaturan preferensi berhasil disimpan!",
                "status_running": "Ollama: BERJALAN",
                "status_stopped": "Ollama: BERHENTI (Klik untuk Jalankan Server)",
                "status_not_installed": "Ollama: TIDAK TERINSTAL",
                "warning": "Peringatan",
                "warning_msg": "Pilih baris model dari tabel di atas!",
                "downloading_title": "Mengunduh",
                "downloading_msg": "Memulai pengunduhan model",
                "success_title": "Berhasil",
                "success_msg": "Model",
                "error_title": "Error",
                "error_msg": "Gagal mengunduh",
                "install_info": "Menginstal Ollama via skrip resmi...",
                "install_success": "Ollama berhasil diinstal!",
                "install_error": "Gagal instal",
                "api_status_ok": "Status",
                "api_status_ok_msg": "Ollama API Aktif dan merespon dengan baik!",
                "api_error_title": "Error",
                "api_error": "Gagal terhubung ke Ollama",
                "detected_hw": "Terdeteksi Hardware",
                "detected_ram": "Sistem RAM",
                "detected_vram": "GPU VRAM",
                "modal_title": "🚀 Toko Model & Installer Universal",
                "modal_header_hw": "Perangkat Terdeteksi -> Sistem RAM",
                "modal_log_title": " Log Pengunduhan Model ",
                "modal_btn_download": "⬇️ Unduh Model Pilihan",
                "modal_btn_close": "Tutup",
                "btn_custom_install": "📥 Install Model",
                "custom_install_title": "📥 Input & Install Model Baru",
                "custom_install_prompt": "Masukkan nama model Ollama (contoh: llama3:8b, mistral:7b):",
                "custom_install_log_title": " Log Proses Download Model ",
                "custom_install_btn": "⬇️ Mulai Install",
                "custom_cancel_btn": "❌ Batal",
                "custom_success_msg": "Model berhasil diinstal!",
                "ctx_copy": "📋 Salin Nama Model",
                "ctx_delete": "🗑 Hapus Model",
                "ctx_chat": "💬 Open Chat In Terminal"
            },
            "en": {
                "title": "Ollama Hub (Linux Edition)",
                "checking": "Checking system...",
                "tab_models": "Models & Matrix ",
                "tab_api": "API & Integration ",
                "tab_hints": "About Ollama ",
                "tab_pref": "Preferences ",
                "header_title": "Ollama & Hardware Compatibility Hub",
                "btn_install": "📥 Install Ollama",
                "btn_open_store": "🚀 Install Recommendation Model",
                "frame_installed": " Installed Models ",
                "btn_refresh": "🔄 Refresh List",
                "copied_title": "Copied",
                "copied_msg": "Model name successfully copied to clipboard:",
                "frame_logs": " Live Terminal & Proses Output ",
                "api_title": "Universal API & Integration Config",
                "api_desc": (
                    "This application is dedicated for Linux operating systems.\n"
                    "Local endpoints can be directly used for Hermes Agent or Web UI:\n\n"
                    "• Base URL        : http://localhost:11434\n"
                    "• OpenAI Endpoint : http://localhost:11434/v1\n"
                    "• Model Format    : qwen2.5-coder:1.5b-instruct, gemma2:2b, etc."
                ),
                "continue_config_title": "Continue Integration Config Example (config.yaml):",
                "btn_copy_config": "📋 Copy Continue Config",
                "config_copied_title": "Copied",
                "config_copied_msg": "Continue config example successfully copied to clipboard!",
                "btn_ping": "Ping Ollama API",
                "hints_title": "About Ollama",
                "hints_header_desc": (
                    "About Ollama:\n"
                    "Ollama is an open-source runtime designed to make it easy to run, create, "
                    "and distribute Large Language Models (LLMs) locally on your own device offline, "
                    "securely, and without cloud latency.\n\n"
                    "Official Documentation:\n"
                    "• Official Website & Docs : https://ollama.com/docs\n"
                    "• GitHub Repository       : https://github.com/ollama/ollama\n\n"
                ),
                "pref_title": "Application Preferences",
                "pref_lang_label": "Select Language:",
                "pref_term_label": "Terminal App for Chat (Terminal Command):",
                "pref_save_btn": "💾 Save Preferences",
                "pref_saved_title": "Saved",
                "pref_saved_msg": "Preferences successfully saved!",
                "status_running": "Ollama: RUNNING",
                "status_stopped": "Ollama: STOPPED (Click to Start Server)",
                "status_not_installed": "Ollama: NOT INSTALLED",
                "warning": "Warning",
                "warning_msg": "Please select a model from the table above!",
                "downloading_title": "Downloading",
                "downloading_msg": "Downloading model",
                "success_title": "Success",
                "success_msg": "Model",
                "error_title": "Error",
                "error_msg": "Failed to download",
                "install_info": "Installing Ollama via official script...",
                "install_success": "Ollama successfully installed!",
                "install_error": "Installation failed",
                "api_status_ok": "Status",
                "api_status_ok_msg": "Ollama API is Active and responding properly!",
                "api_error_title": "Error",
                "api_error": "Failed to connect to Ollama",
                "detected_hw": "Detected Hardware",
                "detected_ram": "System RAM",
                "detected_vram": "GPU VRAM",
                "modal_title": "🚀 Model Store & Universal Installer",
                "modal_header_hw": "Detected Hardware -> System RAM",
                "modal_log_title": " Model Download Logs ",
                "modal_btn_download": "⬇️ Download Selected Model",
                "modal_btn_close": "Close",
                "btn_custom_install": "📥 Install Model",
                "custom_install_title": "📥 Input & Install New Model",
                "custom_install_prompt": "Enter Ollama model name (e.g. llama3:8b, mistral:7b):",
                "custom_install_log_title": " Model Download Process Log ",
                "custom_install_btn": "⬇️ Start Install",
                "custom_cancel_btn": "❌ Cancel",
                "custom_success_msg": "Model successfully installed!",
                "ctx_copy": "📋 Copy Model Name",
                "ctx_delete": "🗑 Delete Model",
                "ctx_chat": "💬 Open Chat In Terminal"
            }
        }

        self.root.title(self.texts[self.lang]["title"])
        self.root.geometry("1000x800")
        self.root.configure(bg="#1e1e2f")

        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(".", background="#1e1e2f", foreground="#f8f9fa", font=("Segoe UI", 10))
        
        # Style ttk Button untuk efek Hover yang jelas & kontras di semua Dialog / MessageBox / Widget ttk
        style.configure("TButton", 
                        background="#313244", 
                        foreground="#ffffff", 
                        borderwidth=1, 
                        focusthickness=3, 
                        focuscolor="#4f46e5",
                        font=("Segoe UI", 10, "bold"))
        style.map("TButton", 
                  background=[('pressed', '#4f46e5'), ('active', '#4f46e5')], 
                  foreground=[('pressed', '#ffffff'), ('active', '#ffffff')])

        # Style untuk Combobox pilihan bahasa agar lebih jelas & kontras
        style.configure("Lang.TCombobox", 
                        fieldbackground="#11111b", 
                        background="#11111b", 
                        foreground="#a6e3a1", 
                        borderwidth=1, 
                        font=("Segoe UI", 10, "bold"),
                        arrowcolor="#a6e3a1")
        style.map("Lang.TCombobox",
                  fieldbackground=[('readonly', '#11111b'), ('focus', '#11111b')],
                  background=[('readonly', '#11111b'), ('focus', '#11111b')],
                  foreground=[('readonly', '#a6e3a1'), ('focus', '#a6e3a1')])

        style.configure("Custom.Treeview", 
                        background="#11111b", 
                        foreground="#a6e3a1",
                        fieldbackground="#11111b",
                        rowheight=30,
                        font=("Segoe UI", 10))
        style.configure("Custom.Treeview.Heading", 
                        background="#313244", 
                        foreground="#ffffff", 
                        font=("Segoe UI", 10, "bold"))
        style.map("Custom.Treeview", 
                  background=[('selected', '#4f46e5')], 
                  foreground=[('selected', '#ffffff')])

        # Header Frame
        header_frame = tk.Frame(root, bg="#181825", padx=20, pady=12)
        header_frame.pack(fill=tk.X)

        self.title_lbl = tk.Label(header_frame, text=self.texts[self.lang]["header_title"], font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#181825")
        self.title_lbl.pack(side=tk.LEFT)

        header_right = tk.Frame(header_frame, bg="#181825")
        header_right.pack(side=tk.RIGHT)

        self.status_btn = tk.Button(header_right, text=self.texts[self.lang]["checking"], bg="#45475a", fg="#f9e2af", activebackground="#585b70", activeforeground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2", command=self.on_status_click)
        self.status_btn.pack(side=tk.LEFT)

        # Custom Navigation Bar Frame
        nav_frame = tk.Frame(root, bg="#11111b", padx=12, pady=8)
        nav_frame.pack(fill=tk.X)

        self.btn_nav_models = tk.Button(nav_frame, text=self.texts[self.lang]["tab_models"], bg="#4f46e5", fg="#ffffff", activebackground="#6366f1", activeforeground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=14, pady=6, cursor="hand2", command=lambda: self.switch_tab(0))
        self.btn_nav_models.pack(side=tk.LEFT, padx=4)

        self.btn_nav_api = tk.Button(nav_frame, text=self.texts[self.lang]["tab_api"], bg="#313244", fg="#cdd6f4", activebackground="#45475a", activeforeground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=14, pady=6, cursor="hand2", command=lambda: self.switch_tab(1))
        self.btn_nav_api.pack(side=tk.LEFT, padx=4)

        self.btn_nav_hints = tk.Button(nav_frame, text=self.texts[self.lang]["tab_hints"], bg="#313244", fg="#cdd6f4", activebackground="#45475a", activeforeground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=14, pady=6, cursor="hand2", command=lambda: self.switch_tab(2))
        self.btn_nav_hints.pack(side=tk.LEFT, padx=4)

        self.btn_nav_pref = tk.Button(nav_frame, text=self.texts[self.lang]["tab_pref"], bg="#313244", fg="#cdd6f4", activebackground="#45475a", activeforeground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=14, pady=6, cursor="hand2", command=lambda: self.switch_tab(3))
        self.btn_nav_pref.pack(side=tk.LEFT, padx=4)

        # Content Container (Frames)
        self.content_container = tk.Frame(root, bg="#1e1e2f")
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.tab_models = tk.Frame(self.content_container, bg="#1e1e2f")
        self.tab_api = tk.Frame(self.content_container, bg="#1e1e2f")
        self.tab_hints = tk.Frame(self.content_container, bg="#1e1e2f")
        self.tab_pref = tk.Frame(self.content_container, bg="#1e1e2f")

        self.setup_models_tab()
        self.setup_api_tab()
        self.setup_hints_tab()
        self.setup_pref_tab()

        self.current_tab_index = 0
        self.switch_tab(0)

        # Bottom status / install button bar if needed
        self.bottom_bar = tk.Frame(root, bg="#181825", padx=15, pady=6)
        self.bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.btn_install_ollama = tk.Button(self.bottom_bar, text=self.texts[self.lang]["btn_install"], bg="#f38ba8", fg="#1e1e2f", activebackground="#eba0ac", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2", command=self.install_ollama_action)
        self.btn_install_ollama.pack(side=tk.LEFT)
        self.btn_install_ollama.pack_forget()

        self.footer_lbl = tk.Label(self.bottom_bar, text="Ollama Manager (Linux Edition)", font=("Segoe UI", 9), fg="#9399b2", bg="#181825")
        self.footer_lbl.pack(side=tk.RIGHT)

        init_db()
        self.refresh_all_data()

    def detect_default_terminal(self):
        terminals = ["gnome-terminal", "konsole", "xfce4-terminal", "tilix", "alacritty", "kitty", "terminator", "xterm"]
        for term in terminals:
            _, _, code = self.run_cmd(f"which {term}")
            if code == 0:
                return term
        return "xterm"

    def toggle_language(self):
        self.lang = "en" if self.lang == "id" else "id"
        t = self.texts[self.lang]
        
        self.root.title(t["title"])
        self.title_lbl.config(text=t["header_title"])
        
        self.btn_nav_models.config(text=t["tab_models"])
        self.btn_nav_api.config(text=t["tab_api"])
        self.btn_nav_hints.config(text=t["tab_hints"])
        self.btn_nav_pref.config(text=t["tab_pref"])
        
        self.btn_install_ollama.config(text=t["btn_install"])

        if hasattr(self, 'frame_inst'):
            self.frame_inst.config(text=t["frame_installed"])
            self.btn_refresh.config(text=t["btn_refresh"])
            self.btn_open_store.config(text=t["btn_open_store"])
            self.btn_custom_install.config(text=t["btn_custom_install"])
        
        if hasattr(self, 'frame_log'):
            self.frame_log.config(text=t["frame_logs"])
        
        if hasattr(self, 'api_title_lbl'):
            self.api_title_lbl.config(text=t["api_title"])
            self.api_desc_txt.config(state=tk.NORMAL)
            self.api_desc_txt.delete("1.0", tk.END)
            self.api_desc_txt.insert(tk.END, t["api_desc"])
            self.api_desc_txt.config(state=tk.DISABLED)
            self.btn_ping.config(text=t["btn_ping"])
            
        if hasattr(self, 'hints_title_lbl'):
            self.hints_title_lbl.config(text=t["hints_title"])
            self.hints_txt.config(state=tk.NORMAL)
            self.hints_txt.delete("1.0", tk.END)
            self.hints_txt.insert(tk.END, t["hints_header_desc"])
            self.hints_txt.config(state=tk.DISABLED)
            
            self.hints_txt.tag_config("link", foreground="#89b4fa", underline=True)
            self.hints_txt.tag_bind("link", "<Enter>", lambda e: self.hints_txt.config(cursor="hand2"))
            self.hints_txt.tag_bind("link", "<Leave>", lambda e: self.hints_txt.config(cursor=""))
            self.hints_txt.tag_bind("link", "<Button-1>", self.on_hints_link_click)

        if hasattr(self, 'continue_lbl'):
            self.continue_lbl.config(text=t["continue_config_title"])
            self.btn_copy_config.config(text=t["btn_copy_config"])
            self.pref_title_lbl.config(text=t["pref_title"])
            self.pref_lang_lbl.config(text=t["pref_lang_label"])
            self.pref_term_lbl.config(text=t["pref_term_label"])
            self.pref_save_btn.config(text=t["pref_save_btn"])
            self.lang_combobox.set("Bahasa Indonesia" if self.lang == "id" else "English")

        self.refresh_all_data()

    def switch_tab(self, index):
        self.current_tab_index = index
        for tab in (self.tab_models, self.tab_api, self.tab_hints, self.tab_pref):
            tab.pack_forget()

        for btn in (self.btn_nav_models, self.btn_nav_api, self.btn_nav_hints, self.btn_nav_pref):
            btn.config(bg="#313244", fg="#cdd6f4")

        if index == 0:
            self.tab_models.pack(fill=tk.BOTH, expand=True)
            self.btn_nav_models.config(bg="#4f46e5", fg="#ffffff")
        elif index == 1:
            self.tab_api.pack(fill=tk.BOTH, expand=True)
            self.btn_nav_api.config(bg="#4f46e5", fg="#ffffff")
        elif index == 2:
            self.tab_hints.pack(fill=tk.BOTH, expand=True)
            self.btn_nav_hints.config(bg="#4f46e5", fg="#ffffff")
        elif index == 3:
            self.tab_pref.pack(fill=tk.BOTH, expand=True)
            self.btn_nav_pref.config(bg="#4f46e5", fg="#ffffff")

    def run_cmd(self, cmd, timeout=15):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
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
                self.status_btn.config(text=t["status_not_installed"], bg="#f38ba8", fg="#1e1e2e")
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
            self.status_btn.config(text=t["status_running"], bg="#a6e3a1", fg="#1e1e2e")
        else:
            self.status_btn.config(text=t["status_stopped"], bg="#fab387", fg="#1e1e2e")

    def on_status_click(self):
        t = self.texts[self.lang]
        _, _, rc = self.run_cmd("pgrep ollama")
        
        if rc != 0:
            self.log_to_terminal("[*] Starting Ollama server...")
            def start_server():
                try:
                    self.run_cmd("pkexec systemctl start ollama")
                    import time
                    time.sleep(2)
                    self.root.after(0, self.refresh_all_data)
                    self.log_to_terminal("[+] Ollama server started successfully!")
                except Exception as e:
                    self.log_to_terminal(f"[!] Failed to start Ollama server: {e}")
            threading.Thread(target=start_server, daemon=True).start()
        else:
            konfirmasi_teks = "Matikan server Ollama?" if self.lang == "id" else "Stop Ollama server?"
            if messagebox.askyesno("Konfirmasi", konfirmasi_teks):
                self.log_to_terminal("[*] Stopping Ollama server via systemctl...")
                
                def stop_server():
                    _, err, kill_rc = self.run_cmd("pkexec systemctl stop ollama")
                    
                    import time
                    time.sleep(1)
                    self.root.after(0, self.refresh_all_data)
                    
                    if kill_rc == 0:
                        self.log_to_terminal("[+] Ollama server stopped properly.")
                    else:
                        self.log_to_terminal(f"[!] Gagal mematikan server: {err}")
                        
                threading.Thread(target=stop_server, daemon=True).start()

    def install_ollama_action(self):
        def worker():
            t = self.texts[self.lang]
            self.log_to_terminal(f"[*] {t['install_info']}")
            messagebox.showinfo("Install", t["install_info"])
            _, err, code = self.run_cmd("curl -fsSL https://ollama.com/install.sh | sh")
            if code == 0:
                self.log_to_terminal(f"[+] {t['install_success']}")
                messagebox.showinfo("Success", t["install_success"])
            else:
                self.log_to_terminal(f"[!] {t['install_error']}: {err}")
                messagebox.showerror("Error", f"{t['install_error']}: {err}")
            self.root.after(0, self.refresh_all_data)
        threading.Thread(target=worker, daemon=True).start()

    def setup_models_tab(self):
        t = self.texts[self.lang]
        
        # Top section: Installed Models
        self.frame_inst = tk.LabelFrame(self.tab_models, text=t["frame_installed"], fg="#cdd6f4", bg="#1e1e2f", font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        self.frame_inst.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        inst_container = tk.Frame(self.frame_inst, bg="#1e1e2f")
        inst_container.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "size", "modified")
        self.list_installed = ttk.Treeview(inst_container, columns=columns, show="headings", style="Custom.Treeview", height=8)

        self.list_installed.heading("name", text="Nama Model", anchor=tk.W)
        self.list_installed.heading("size", text="Ukuran", anchor=tk.W)
        self.list_installed.heading("modified", text="Terakhir Diubah", anchor=tk.W)

        self.list_installed.column("name", width=350, anchor=tk.W)
        self.list_installed.column("size", width=150, anchor=tk.W)
        self.list_installed.column("modified", width=350, anchor=tk.W)

        self.list_installed.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4), pady=2)

        inst_scroll = ttk.Scrollbar(inst_container, orient=tk.VERTICAL, command=self.list_installed.yview)
        inst_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_installed.config(yscrollcommand=inst_scroll.set)

        # Context Menu (Right click menu) with larger font (Segoe UI, 11)
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#313244", fg="#ffffff", activebackground="#4f46e5", activeforeground="#ffffff", font=("Segoe UI", 11, "bold"))
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
                except:
                    pass

        def on_table_click(event):
            item = self.list_installed.identify_row(event.y)
            if not item:
                self.list_installed.selection_remove(self.list_installed.selection())
                try:
                    self.context_menu.unpost()
                except:
                    pass

        self.list_installed.bind("<Button-3>", show_context_menu)
        self.list_installed.bind("<Button-2>", show_context_menu)
        self.list_installed.bind("<Button-1>", on_table_click)

        def global_click_handler(event):
            try:
                self.context_menu.unpost()
            except:
                pass
        self.root.bind("<Button-1>", global_click_handler, add="+")

        btn_frame = tk.Frame(self.frame_inst, bg="#1e1e2f")
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_refresh = tk.Button(btn_frame, text=t["btn_refresh"], bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2d5", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=self.refresh_all_data)
        self.btn_refresh.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_open_store = tk.Button(btn_frame, text=t["btn_open_store"], bg="#b4befe", fg="#1e1e2e", activebackground="#cba6f7", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=self.open_model_store_modal)
        self.btn_open_store.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_custom_install = tk.Button(btn_frame, text=t["btn_custom_install"], bg="#89b4fa", fg="#1e1e2e", activebackground="#74c7ec", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=self.open_custom_install_modal)
        self.btn_custom_install.pack(side=tk.LEFT)

        # Bottom section: Live Terminal Output Log
        self.frame_log = tk.LabelFrame(self.tab_models, text=t["frame_logs"], fg="#cdd6f4", bg="#1e1e2f", font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        self.frame_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_txt = scrolledtext.ScrolledText(self.frame_log, bg="#11111b", fg="#89b4fa", font=("JetBrains Mono", 9), height=10, relief=tk.FLAT, bd=0)
        self.log_txt.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.log_txt.config(state=tk.DISABLED)

    def open_custom_install_modal(self):
        t = self.texts[self.lang]
        modal = tk.Toplevel(self.root)
        modal.title(t["custom_install_title"])
        modal.geometry("700x500")
        modal.configure(bg="#1e1e2f")
        modal.transient(self.root)
        modal.grab_set()

        # Top Frame for Model Name Input
        input_frame = tk.Frame(modal, bg="#1e1e2f", padx=20, pady=15)
        input_frame.pack(fill=tk.X)

        lbl_prompt = tk.Label(input_frame, text=t["custom_install_prompt"], font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#1e1e2f")
        lbl_prompt.pack(anchor=tk.W, pady=(0, 5))

        entry_frame = tk.Frame(input_frame, bg="#1e1e2f")
        entry_frame.pack(fill=tk.X)

        model_entry = tk.Entry(entry_frame, font=("JetBrains Mono", 11), bg="#313244", fg="#ffffff", insertbackground="white", relief=tk.FLAT)
        model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        model_entry.focus()

        # Bottom Action / Buttons Frame
        action_frame = tk.Frame(modal, bg="#181825", padx=15, pady=10)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Log Frame
        log_frame = tk.LabelFrame(modal, text=t["custom_install_log_title"], fg="#cdd6f4", bg="#1e1e2f", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)

        log_txt = scrolledtext.ScrolledText(log_frame, bg="#11111b", fg="#89b4fa", font=("JetBrains Mono", 9), relief=tk.FLAT, bd=0)
        log_txt.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        log_txt.config(state=tk.DISABLED)

        def log_to_custom_modal(msg):
            def _w():
                log_txt.config(state=tk.NORMAL)
                log_txt.insert(tk.END, msg + "\n")
                log_txt.see(tk.END)
                log_txt.config(state=tk.DISABLED)
            modal.after(0, _w)

        # Cancellation flag/process reference holder
        proc_holder = {"process": None, "cancelled": False}

        def start_custom_download():
            model_name = model_entry.get().strip()
            if not model_name:
                messagebox.showwarning(t["warning"], "Masukkan nama model dengan benar!", parent=modal)
                return

            btn_start.config(state=tk.DISABLED)
            model_entry.config(state=tk.DISABLED)

            def worker():
                log_to_custom_modal(f"[*] Starting download / pull for custom model: {model_name}...")
                
                cmd = f"ollama pull {model_name}"
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                proc_holder["process"] = process

                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                
                for line in iter(process.stdout.readline, ''):
                    if proc_holder["cancelled"]:
                        break
                    clean_line = ansi_escape.sub('', line).replace('\r', '').strip()
                    if clean_line:
                        log_to_custom_modal(f"    {clean_line}")
                
                process.wait()

                if proc_holder["cancelled"]:
                    log_to_custom_modal("[!] Proses download dibatalkan oleh pengguna.")
                    return

                if process.returncode == 0:
                    log_to_custom_modal(f"[+] Model {model_name} berhasil diunduh!")
                    messagebox.showinfo(t["success_title"], f"{t['custom_success_msg']}\n\n{model_name}", parent=modal)
                    self.refresh_all_data()
                    modal.destroy()
                else:
                    log_to_custom_modal(f"[!] Gagal mengunduh model {model_name}")
                    messagebox.showerror(t["error_title"], f"{t['error_msg']}: {model_name}", parent=modal)
                    btn_start.config(state=tk.NORMAL)
                    model_entry.config(state=tk.NORMAL)

            threading.Thread(target=worker, daemon=True).start()

        def cancel_action():
            if proc_holder["process"] and proc_holder["process"].poll() is None:
                proc_holder["cancelled"] = True
                try:
                    proc_holder["process"].terminate()
                except:
                    pass
            modal.destroy()

        btn_start = tk.Button(entry_frame, text=t["custom_install_btn"], bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2d5", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=14, pady=6, cursor="hand2", command=start_custom_download)
        btn_start.pack(side=tk.RIGHT)

        btn_cancel = tk.Button(action_frame, text=t["custom_cancel_btn"], bg="#f38ba8", fg="#1e1e2e", activebackground="#eba0ac", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=cancel_action)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

        modal.protocol("WM_DELETE_WINDOW", cancel_action)

    def open_model_store_modal(self):
        t = self.texts[self.lang]
        modal = tk.Toplevel(self.root)
        modal.title(t["modal_title"])
        modal.geometry("1000x650") 
        modal.configure(bg="#1e1e2f")
        modal.transient(self.root)
        modal.grab_set()

        top_frame = tk.Frame(modal, bg="#181825", padx=15, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        total_ram_gb = 8
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        total_ram_gb = round(int(line.split()[1]) / (1024**2))
                        break
        except:
            pass

        vram_gb = 0
        try:
            out, _, code = self.run_cmd("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits")
            if code == 0 and out.strip():
                vram_mb = int(out.strip().splitlines()[0])
                vram_gb = round(vram_mb / 1024)
        except:
            pass

        hw_lbl = tk.Label(top_frame, text=f"💻 {t['modal_header_hw']} RAM ~{total_ram_gb} GB | VRAM ~{vram_gb} GB", font=("Segoe UI", 11, "bold"), fg="#f9e2af", bg="#181825")
        hw_lbl.pack(anchor=tk.W)

        action_frame = tk.Frame(modal, bg="#181825", padx=15, pady=10)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X)

        log_frame = tk.LabelFrame(modal, text=t["modal_log_title"], fg="#cdd6f4", bg="#1e1e2f", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 10))

        modal_log_txt = scrolledtext.ScrolledText(log_frame, bg="#11111b", fg="#89b4fa", font=("JetBrains Mono", 9), height=7, relief=tk.FLAT, bd=0)
        modal_log_txt.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        modal_log_txt.config(state=tk.DISABLED)

        list_frame = tk.Frame(modal, bg="#1e1e2f", padx=15, pady=10)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        list_container = tk.Frame(list_frame, bg="#1e1e2f")
        list_container.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "size", "status", "desc")
        self.modal_list = ttk.Treeview(list_container, columns=columns, show="headings", style="Custom.Treeview")
        
        self.modal_list.heading("name", text="Nama Model", anchor=tk.W)
        self.modal_list.heading("size", text="Ukuran", anchor=tk.W)
        self.modal_list.heading("status", text="Status Kompatibilitas", anchor=tk.W)
        self.modal_list.heading("desc", text="Deskripsi Singkat", anchor=tk.W)

        self.modal_list.column("name", width=220, anchor=tk.W, stretch=False)
        self.modal_list.column("size", width=100, anchor=tk.W, stretch=False)
        self.modal_list.column("status", width=240, anchor=tk.W, stretch=False)
        self.modal_list.column("desc", width=1200, anchor=tk.W, stretch=False)

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
            lines = out.splitlines()[1:] 
            for line in lines:
                if line.strip():
                    installed_models.append(line.split()[0])

        db = load_db()
        for item in db:
            min_ram = item.get("min_ram_gb", 4)
            min_vram = item.get("min_vram_gb", 2)

            if vram_gb >= min_vram:
                status = "[SANGAT COCOK / FAST]" if self.lang == "id" else "[VERY SUITABLE / FAST]"
            elif total_ram_gb >= min_ram:
                status = "[COCOK / CPU BOUND]" if self.lang == "id" else "[SUITABLE / CPU BOUND]"
            elif total_ram_gb >= (min_ram - 2):
                status = "[BERAT / LOW RAM]" if self.lang == "id" else "[HEAVY / LOW RAM]"
            else:
                status = "[TIDAK DISARANKAN]" if self.lang == "id" else "[NOT RECOMMENDED]"

            if item['name'] in installed_models:
                status = "[* TERINSTAL / INSTALLED *]"

            desc = item.get("desc", "- Tidak ada deskripsi -")
            if self.lang == "id":
                desc = item.get("description_id", desc)
            else:
                desc = item.get("description_en", item.get("description", desc))

            self.modal_list.insert("", tk.END, values=(item['name'], item['size'], status, desc))

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
                log_to_modal(f"[*] Starting download / pull for model: {model_name}...")
                
                process = subprocess.Popen(
                    f"ollama pull {model_name}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                
                for line in iter(process.stdout.readline, ''):
                    clean_line = ansi_escape.sub('', line).replace('\r', '').strip()
                    if clean_line:
                        log_to_modal(f"    {clean_line}")
                
                process.wait()
                if process.returncode == 0:
                    log_to_modal(f"[+] Model {model_name} successfully downloaded!")
                    messagebox.showinfo(t["success_title"], f"{t['success_msg']} {model_name}!", parent=modal)
                    self.refresh_all_data()
                    self.modal_list.item(item_id, values=(model_name, values[1], "[* TERINSTAL / INSTALLED *]", values[3]))
                else:
                    log_to_modal(f"[!] Failed to download model {model_name}")
                    messagebox.showerror(t["error_title"], f"{t['error_msg']}: {model_name}", parent=modal)

            threading.Thread(target=worker, daemon=True).start()

        btn_ins_frame = tk.Frame(self.frame_inst, bg="#1e1e2f")
        btn_ins_frame.pack(fill=tk.X, pady=(10, 0))

        btn_install = tk.Button(action_frame, text=t["modal_btn_download"], bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2d5", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=install_selected_model)
        btn_install.pack(side=tk.LEFT, padx=(0, 10))

        btn_close = ttk.Button(action_frame, text=t["modal_btn_close"], command=modal.destroy)
        btn_close.pack(side=tk.RIGHT) 

    def load_installed_models(self):
        for row in self.list_installed.get_children():
            self.list_installed.delete(row)
            
        out, _, code = self.run_cmd("ollama list")
        if code == 0:
            lines = out.splitlines()[1:] 
            for line in lines:
                if line.strip():
                    cols = re.split(r'\s{2,}', line.strip())
                    if len(cols) >= 4:
                        model_name = cols[0]
                        model_size = cols[2]
                        model_modified = cols[3]
                        self.list_installed.insert("", tk.END, values=(model_name, model_size, model_modified))

    def copy_model_name_action(self):
        try:
            t = self.texts[self.lang]
            selection = self.list_installed.selection()
            if not selection:
                messagebox.showwarning(t["warning"], t["warning_msg"])
                return
                
            item_id = selection[0]
            values = self.list_installed.item(item_id, "values")
            model_name = values[0]

            self.root.clipboard_clear()
            self.root.clipboard_append(model_name)
            self.root.update() 

            self.log_to_terminal(f"[+] Copied model name to clipboard: {model_name}")
            messagebox.showinfo(t["copied_title"], f"{t['copied_msg']}\n\n{model_name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_chat_in_terminal_action(self):
        try:
            t = self.texts[self.lang]
            selection = self.list_installed.selection()
            if not selection:
                messagebox.showwarning(t["warning"], t["warning_msg"])
                return
            item_id = selection[0]
            values = self.list_installed.item(item_id, "values")
            model_name = values[0]

            terminal_cmd = self.preferred_terminal.strip() or "gnome-terminal"
            
            if "gnome-terminal" in terminal_cmd:
                full_cmd = f"{terminal_cmd} -- bash -c 'ollama run {model_name}; exec bash'"
            elif "konsole" in terminal_cmd:
                full_cmd = f"{terminal_cmd} -e bash -c 'ollama run {model_name}; exec bash'"
            elif "xfce4-terminal" in terminal_cmd:
                full_cmd = f"{terminal_cmd} -e 'bash -c \"ollama run {model_name}; exec bash\"'"
            elif "alacritty" in terminal_cmd or "kitty" in terminal_cmd or "tilix" in terminal_cmd:
                full_cmd = f"{terminal_cmd} -e bash -c 'ollama run {model_name}; exec bash'"
            else:
                full_cmd = f"xterm -e 'ollama run {model_name}; bash'"

            self.log_to_terminal(f"[*] Opening chat in terminal for {model_name} using: {terminal_cmd}")
            
            def run_term():
                subprocess.Popen(full_cmd, shell=True)
            threading.Thread(target=run_term, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_model_action(self):
        try:
            t = self.texts[self.lang]
            selection = self.list_installed.selection()
            if not selection:
                messagebox.showwarning(t["warning"], t["warning_msg"])
                return
            item_id = selection[0]
            values = self.list_installed.item(item_id, "values")
            model_name = values[0]

            konfirmasi_teks = f"Hapus model {model_name}?" if self.lang == "id" else f"Delete model {model_name}?"
            if messagebox.askyesno("Konfirmasi", konfirmasi_teks):
                self.log_to_terminal(f"[*] Deleting model {model_name}...")
                _, _, code = self.run_cmd(f"ollama rm {model_name}")
                if code == 0:
                    self.log_to_terminal(f"[+] Model {model_name} successfully deleted.")
                    messagebox.showinfo("Success", f"Model {model_name} dihapus.")
                    self.refresh_all_data()
                else:
                    self.log_to_terminal(f"[!] Failed to delete model {model_name}")
                    messagebox.showerror("Error", f"Gagal menghapus model.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_api_tab(self):
        t = self.texts[self.lang]
        frame = tk.Frame(self.tab_api, bg="#1e1e2f", padx=15, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        self.api_title_lbl = tk.Label(frame, text=t["api_title"], font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#1e1e2f")
        self.api_title_lbl.pack(anchor=tk.W, pady=(0, 12))

        # Main Split Container using 2 Equal Columns (Cards)
        api_container = tk.Frame(frame, bg="#1e1e2f")
        api_container.pack(fill=tk.BOTH, expand=True)
        api_container.grid_columnconfigure(0, weight=1, uniform="group1")
        api_container.grid_columnconfigure(1, weight=1, uniform="group1")
        api_container.grid_rowconfigure(0, weight=1)

        # Left Card: Universal API Info & Endpoint Details
        left_card = tk.LabelFrame(api_container, text=" Endpoint Lokal & Keterangan ", fg="#a6e3a1", bg="#1e1e2f", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        self.api_desc_txt = scrolledtext.ScrolledText(left_card, bg="#11111b", fg="#f9e2af", font=("JetBrains Mono", 10), height=14, relief=tk.FLAT, bd=0)
        self.api_desc_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        self.api_desc_txt.insert(tk.END, t["api_desc"])
        self.api_desc_txt.config(state=tk.DISABLED)

        self.btn_ping = tk.Button(left_card, text=t["btn_ping"], bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2d5", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=self.test_api)
        self.btn_ping.pack(anchor=tk.W)

        # Right Card: Continue Configuration (YAML)
        right_card = tk.LabelFrame(api_container, text=" Konfigurasi Integrasi Continue (config.yaml) ", fg="#b4befe", bg="#1e1e2f", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        continue_yaml_content = (
            "name: Ollama Local\n"
            "version: 1.0.0\n"
            "schema: v1\n"
            "models:\n"
            "  - name: Local Qwen3.5 4B (Debug & Trace)\n"
            "    provider: ollama\n"
            "    model: qwen3.5:4b\n"
            "    apiBase: http://127.0.0.1:11434\n"
            "    roles:\n"
            "      - chat\n"
            "      - edit\n"
            "      - apply\n"
            "    capabilities:\n"
            "      - tool_use\n"
            "    defaultCompletionOptions:\n"
            "      contextLength: 8192\n"
            "      temperature: 0.2\n"
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
            "    requestOptions:\n"
            "      extraBodyProperties:\n"
            "        tools: []"
        )

        self.continue_txt = scrolledtext.ScrolledText(right_card, bg="#11111b", fg="#89b4fa", font=("JetBrains Mono", 9), height=14, relief=tk.FLAT, bd=0)
        self.continue_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        self.continue_txt.insert(tk.END, continue_yaml_content)
        self.continue_txt.config(state=tk.DISABLED)

        def copy_continue_config():
            self.root.clipboard_clear()
            self.root.clipboard_append(continue_yaml_content)
            self.root.update()
            self.log_to_terminal("[+] Copied Continue config example to clipboard.")
            messagebox.showinfo(t["config_copied_title"], t["config_copied_msg"])

        self.btn_copy_config = tk.Button(right_card, text=t["btn_copy_config"], bg="#b4befe", fg="#1e1e2e", activebackground="#cba6f7", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=copy_continue_config)
        self.btn_copy_config.pack(anchor=tk.W)

    def test_api(self):
        import urllib.request
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
        frame = tk.Frame(self.tab_hints, bg="#1e1e2f", padx=15, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        self.hints_title_lbl = tk.Label(frame, text=t["hints_title"], font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#1e1e2f")
        self.hints_title_lbl.pack(anchor=tk.W, pady=(0, 12))

        # Card container for About Ollama tab to match API & Integration style
        hints_card = tk.LabelFrame(frame, text=" Informasi & Dokumentasi Resmi Ollama ", fg="#f9e2af", bg="#1e1e2f", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        hints_card.pack(fill=tk.BOTH, expand=True)

        self.hints_txt = scrolledtext.ScrolledText(hints_card, bg="#11111b", fg="#f9e2af", font=("JetBrains Mono", 10), height=18, relief=tk.FLAT, bd=0)
        self.hints_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        full_text = t["hints_header_desc"]
        self.hints_txt.insert(tk.END, full_text)

        self.hints_txt.tag_config("link", foreground="#89b4fa", underline=True)
        self.hints_txt.tag_bind("link", "<Enter>", lambda e: self.hints_txt.config(cursor="hand2"))
        self.hints_txt.tag_bind("link", "<Leave>", lambda e: self.hints_txt.config(cursor=""))
        self.hints_txt.tag_bind("link", "<Button-1>", self.on_hints_link_click)

        self.highlight_urls_in_hints()
        self.hints_txt.config(state=tk.DISABLED)

    def setup_pref_tab(self):
        t = self.texts[self.lang]
        frame = tk.Frame(self.tab_pref, bg="#1e1e2f", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.pref_title_lbl = tk.Label(frame, text=t["pref_title"], font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#1e1e2f")
        self.pref_title_lbl.pack(anchor=tk.W, pady=(0, 20))

        # Language preference
        lang_frame = tk.Frame(frame, bg="#1e1e2f")
        lang_frame.pack(fill=tk.X, pady=10)

        self.pref_lang_lbl = tk.Label(lang_frame, text=t["pref_lang_label"], font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#1e1e2f", width=45, anchor=tk.W)
        self.pref_lang_lbl.pack(side=tk.LEFT)

        lang_inner = tk.Frame(lang_frame, bg="#1e1e2f")
        lang_inner.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lang_combobox = ttk.Combobox(lang_inner, values=["Bahasa Indonesia", "English"], state="readonly", width=20, font=("Segoe UI", 10, "bold"), style="Lang.TCombobox")
        self.lang_combobox.pack(side=tk.LEFT, padx=10, ipady=4)
        self.lang_combobox.set("Bahasa Indonesia" if self.lang == "id" else "English")

        # Terminal app preference
        term_frame = tk.Frame(frame, bg="#1e1e2f")
        term_frame.pack(fill=tk.X, pady=10)

        self.pref_term_lbl = tk.Label(term_frame, text=t["pref_term_label"], font=("Segoe UI", 11, "bold"), fg="#cdd6f4", bg="#1e1e2f", width=45, anchor=tk.W)
        self.pref_term_lbl.pack(side=tk.LEFT)

        self.term_entry = tk.Entry(term_frame, font=("JetBrains Mono", 10), bg="#313244", fg="#ffffff", insertbackground="white", relief=tk.FLAT, width=28)
        self.term_entry.pack(side=tk.LEFT, padx=10, ipady=4)
        self.term_entry.insert(0, self.preferred_terminal)

        # Save button
        btn_frame = tk.Frame(frame, bg="#1e1e2f")
        btn_frame.pack(fill=tk.X, pady=(25, 0))

        self.pref_save_btn = tk.Button(btn_frame, text=t["pref_save_btn"], bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2d5", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=8, cursor="hand2", command=self.save_preferences_action)
        self.pref_save_btn.pack(anchor=tk.W)

    def save_preferences_action(self):
        t = self.texts[self.lang]
        selected_lang_str = self.lang_combobox.get()
        new_lang = "id" if selected_lang_str.startswith("Ba") else "en"
        
        self.preferred_terminal = self.term_entry.get().strip() or "gnome-terminal"

        if new_lang != self.lang:
            self.toggle_language()
        else:
            messagebox.showinfo(t["pref_saved_title"], t["pref_saved_msg"])

        self.log_to_terminal(f"[+] Preferences saved. Language: {self.lang}, Terminal: {self.preferred_terminal}")

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
            tag_names = self.hints_txt.tag_names(index)
            if "link" in tag_names:
                line_string = self.hints_txt.get(f"{index} linestart", f"{index} lineend")
                for url in ["https://ollama.com/docs", "https://github.com/ollama/ollama"]:
                    if url in line_string:
                        webbrowser.open(url)
                        self.log_to_terminal(f"[*] Opening official doc URL: {url}")
                        break
        except Exception as e:
            print(e)

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalOllamaManager(root)
    root.mainloop()
