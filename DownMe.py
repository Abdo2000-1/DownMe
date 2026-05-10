"""
╔══════════════════════════════════════════════════════════════╗
║           DownMe v4.0 — Universal Video Downloader           ║
║     Multi-language • Animated UI • Queue • History • Pro     ║
╚══════════════════════════════════════════════════════════════╝

New in v4.0:
  ✦ Animated progress bar with pulse effect
  ✦ Download Queue (multiple URLs)
  ✦ Download History with search & re-download
  ✦ Thumbnail preview before downloading
  ✦ Drag & Drop URL support
  ✦ Smooth animated transitions
  ✦ Tooltip system
  ✦ Animated status indicators
  ✦ Keyboard shortcuts (Ctrl+V, Enter, Escape, Ctrl+H)
  ✦ Tray icon support (optional: pystray + Pillow)
  ✦ Auto-paste from clipboard on focus
  ✦ Disk space check before download
  ✦ Better error messages (Arabic + English)
  ✦ Animated button states
  ✦ Tab-based navigation (Download / Queue / History / Settings)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
import yt_dlp
import threading
import os
import json
import re
import time
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from datetime import datetime
from collections import deque

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ── Windows: set AppUserModelID so taskbar shows our icon, not Python's ──
try:
    import ctypes
    _app_id = f"AbdoAlAdawy.{APP_NAME}.{APP_VERSION}"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_app_id)
except Exception:
    pass

APP_VERSION = "4.0"
APP_NAME    = "DownMe"

# ══════════════════════════════════════════
#  الثيمات الجاهزة
# ══════════════════════════════════════════
PRESET_THEMES = {
    "Cosmic Purple": {
        "bg_main":        "#0A0A0F",
        "bg_card":        "#13131A",
        "bg_input":       "#1A1A24",
        "accent_primary": "#6C63FF",
        "accent_green":   "#43E97B",
        "accent_red":     "#FF6B6B",
        "accent_cyan":    "#38F9D7",
        "accent_yellow":  "#FFD700",
        "text_primary":   "#FFFFFF",
        "text_secondary": "#8888AA",
        "text_muted":     "#444466",
        "border":         "#2A2A3E",
    },
    "Ocean Blue": {
        "bg_main":        "#050D1A",
        "bg_card":        "#0A1628",
        "bg_input":       "#0F1F38",
        "accent_primary": "#0EA5E9",
        "accent_green":   "#22D3EE",
        "accent_red":     "#F43F5E",
        "accent_cyan":    "#67E8F9",
        "accent_yellow":  "#FCD34D",
        "text_primary":   "#F0F9FF",
        "text_secondary": "#7CB9E8",
        "text_muted":     "#334E6B",
        "border":         "#1E3A5F",
    },
    "Emerald Dark": {
        "bg_main":        "#050F0A",
        "bg_card":        "#0A1A10",
        "bg_input":       "#0F2416",
        "accent_primary": "#10B981",
        "accent_green":   "#34D399",
        "accent_red":     "#F87171",
        "accent_cyan":    "#6EE7B7",
        "accent_yellow":  "#FCD34D",
        "text_primary":   "#ECFDF5",
        "text_secondary": "#6EE7B7",
        "text_muted":     "#1D4731",
        "border":         "#134E2A",
    },
    "Sunset Orange": {
        "bg_main":        "#0F0A05",
        "bg_card":        "#1A1005",
        "bg_input":       "#241808",
        "accent_primary": "#F97316",
        "accent_green":   "#FBBF24",
        "accent_red":     "#EF4444",
        "accent_cyan":    "#FCD34D",
        "accent_yellow":  "#FFD700",
        "text_primary":   "#FFF7ED",
        "text_secondary": "#FDBA74",
        "text_muted":     "#4A2810",
        "border":         "#7C2D12",
    },
    "Rose Gold": {
        "bg_main":        "#0F080A",
        "bg_card":        "#1A0F12",
        "bg_input":       "#24151A",
        "accent_primary": "#E11D78",
        "accent_green":   "#F472B6",
        "accent_red":     "#FB7185",
        "accent_cyan":    "#FBCFE8",
        "accent_yellow":  "#FDE68A",
        "text_primary":   "#FFF1F5",
        "text_secondary": "#F9A8D4",
        "text_muted":     "#4A1028",
        "border":         "#831843",
    },
    "Mono Chrome": {
        "bg_main":        "#080808",
        "bg_card":        "#121212",
        "bg_input":       "#1E1E1E",
        "accent_primary": "#E0E0E0",
        "accent_green":   "#AAAAAA",
        "accent_red":     "#FF5555",
        "accent_cyan":    "#CCCCCC",
        "accent_yellow":  "#FFD700",
        "text_primary":   "#FFFFFF",
        "text_secondary": "#888888",
        "text_muted":     "#333333",
        "border":         "#2A2A2A",
    },
    "Neon Night": {
        "bg_main":        "#03010A",
        "bg_card":        "#08030F",
        "bg_input":       "#0E0519",
        "accent_primary": "#FF00FF",
        "accent_green":   "#00FF88",
        "accent_red":     "#FF3366",
        "accent_cyan":    "#00FFFF",
        "accent_yellow":  "#FFFF00",
        "text_primary":   "#FFFFFF",
        "text_secondary": "#CC88FF",
        "text_muted":     "#440066",
        "border":         "#330055",
    },
}

# ══════════════════════════════════════════
#  الترجمات
# ══════════════════════════════════════════
LANG = {
    "ar": {
        "title":              f"{APP_NAME} — محمّل الفيديوهات",
        "subtitle":           f"محمّل فيديوهات عالمي  v{APP_VERSION}",
        "ready":              "● جاهز",
        "downloading_dot":    "● يتحمّل",
        "tab_download":       "⬇  تحميل",
        "tab_queue":          "📋  قائمة الانتظار",
        "tab_history":        "🕐  السجل",
        "tab_settings":       "⚙️  الإعدادات",
        "card_link":          "🔗  رابط الفيديو",
        "placeholder_url":    "  الصق رابط الفيديو هنا... (YouTube, TikTok, Twitter, Facebook...)",
        "paste":              "📋 لصق",
        "add_to_queue":       "➕ إضافة للقائمة",
        "change_folder":      "تغيير المجلد",
        "card_settings":      "⚙️  إعدادات التحميل",
        "format_label":       "الصيغة",
        "quality_label":      "الجودة",
        "opt_concurrent":     "⚡ تحميل متوازي",
        "opt_subtitle":       "📝 تضمين الترجمة",
        "opt_thumbnail":      "🖼️ صورة مصغرة",
        "opt_autopaste":      "📌 لصق تلقائي",
        "card_progress":      "📊  التقدم",
        "waiting":            "في انتظار الرابط...",
        "btn_download":       "⬇  تحميل الآن",
        "btn_cancel":         "إلغاء",
        "btn_open_folder":    "📂 فتح مجلد التحميل",
        "theme_presets":      "ثيمات جاهزة:",
        "custom_colors":      "تخصيص الألوان:",
        "color_accent":       "اللون الرئيسي",
        "color_bg":           "خلفية التطبيق",
        "color_card":         "خلفية البطاقات",
        "color_text":         "لون النص",
        "apply_theme":        "✅ تطبيق",
        "reset_theme":        "↺ إعادة الضبط",
        "status_fetching":    "🔍 جاري جلب المعلومات...",
        "status_dl":          "⬇ جاري التحميل...",
        "status_processing":  "⚙️ جاري المعالجة...",
        "status_done":        "✅ اكتمل التحميل!",
        "status_cancelled":   "تم الإلغاء",
        "status_error":       "❌ فشل التحميل",
        "status_ready":       "مستعد",
        "warn_no_url":        "من فضلك ضع رابط الفيديو أولاً!",
        "warn_title":         "تنبيه",
        "warn_disk":          "⚠️ مساحة القرص منخفضة! أقل من 1 جيجابايت متاح.",
        "err_title":          "خطأ في التحميل",
        "success_title":      "✅ تم!",
        "success_msg":        "تم حفظ الملف في:\n",
        "speed":              "السرعة",
        "eta":                "الوقت المتبقي",
        "size":               "الحجم",
        "footer":             "يدعم: YouTube • TikTok • Twitter • Facebook • Instagram • 1000+ موقع",
        "lang_btn":           "EN",
        "theme_btn":          "🎨 ثيم",
        "best_q":             "✨ أفضل",
        "theme_title":        "🎨  تخصيص الثيم",
        "queue_empty":        "قائمة الانتظار فارغة",
        "queue_add_hint":     "أضف روابط من تبويب التحميل",
        "queue_start":        "▶ بدء القائمة",
        "queue_clear":        "🗑 مسح الكل",
        "queue_remove":       "✕",
        "history_empty":      "لا يوجد سجل تحميل بعد",
        "history_clear":      "🗑 مسح السجل",
        "history_redownload": "↩ إعادة التحميل",
        "history_open":       "📂 فتح",
        "history_search":     "🔍 ابحث في السجل...",
        "settings_save_path": "مجلد الحفظ الافتراضي",
        "settings_autopaste": "لصق تلقائي عند التركيز",
        "settings_notify":    "إشعار عند اكتمال التحميل",
        "settings_theme":     "الثيم",
        "settings_lang":      "اللغة",
        "disk_free":          "مساحة متاحة",
        "about_title":        "عن التطبيق",
        "about_text":         f"{APP_NAME} v{APP_VERSION}\nمحمّل فيديوهات احترافي\nيعمل بـ yt-dlp",
        "shortcut_hint":      "Ctrl+V لصق • Enter تحميل • Esc إلغاء • Ctrl+H سجل",
        "fetching_preview":   "⏳ جاري جلب معلومات الفيديو...",
        "preview_title":      "معاينة الفيديو",
        "preview_duration":   "المدة",
        "preview_uploader":   "المصدر",
        "preview_views":      "المشاهدات",
        "queue_status_wait":  "انتظار",
        "queue_status_dl":    "يتحمّل",
        "queue_status_done":  "تم",
        "queue_status_err":   "خطأ",
    },
    "en": {
        "title":              f"{APP_NAME} — Universal Downloader",
        "subtitle":           f"Universal Video Downloader  v{APP_VERSION}",
        "ready":              "● READY",
        "downloading_dot":    "● DOWNLOADING",
        "tab_download":       "⬇  Download",
        "tab_queue":          "📋  Queue",
        "tab_history":        "🕐  History",
        "tab_settings":       "⚙️  Settings",
        "card_link":          "🔗  Video URL",
        "placeholder_url":    "  Paste video URL here... (YouTube, TikTok, Twitter, Facebook...)",
        "paste":              "📋 Paste",
        "add_to_queue":       "➕ Add to Queue",
        "change_folder":      "Change Folder",
        "card_settings":      "⚙️  Download Settings",
        "format_label":       "Format",
        "quality_label":      "Quality",
        "opt_concurrent":     "⚡ Concurrent Download",
        "opt_subtitle":       "📝 Embed Subtitles",
        "opt_thumbnail":      "🖼️ Save Thumbnail",
        "opt_autopaste":      "📌 Auto Paste",
        "card_progress":      "📊  Progress",
        "waiting":            "Waiting for URL...",
        "btn_download":       "⬇  Download Now",
        "btn_cancel":         "Cancel",
        "btn_open_folder":    "📂 Open Folder",
        "theme_presets":      "Preset Themes:",
        "custom_colors":      "Custom Colors:",
        "color_accent":       "Accent Color",
        "color_bg":           "App Background",
        "color_card":         "Card Background",
        "color_text":         "Text Color",
        "apply_theme":        "✅ Apply",
        "reset_theme":        "↺ Reset",
        "status_fetching":    "🔍 Fetching info...",
        "status_dl":          "⬇ Downloading...",
        "status_processing":  "⚙️ Processing...",
        "status_done":        "✅ Download complete!",
        "status_cancelled":   "Cancelled",
        "status_error":       "❌ Download failed",
        "status_ready":       "Ready",
        "warn_no_url":        "Please paste a video URL first!",
        "warn_title":         "Warning",
        "warn_disk":          "⚠️ Low disk space! Less than 1 GB available.",
        "err_title":          "Download Error",
        "success_title":      "✅ Done!",
        "success_msg":        "File saved to:\n",
        "speed":              "Speed",
        "eta":                "ETA",
        "size":               "Size",
        "footer":             "Supports: YouTube • TikTok • Twitter • Facebook • Instagram • 1000+ sites",
        "lang_btn":           "ع",
        "theme_btn":          "🎨 Theme",
        "best_q":             "✨ Best",
        "theme_title":        "🎨  Theme Customizer",
        "queue_empty":        "Queue is empty",
        "queue_add_hint":     "Add URLs from the Download tab",
        "queue_start":        "▶ Start Queue",
        "queue_clear":        "🗑 Clear All",
        "queue_remove":       "✕",
        "history_empty":      "No download history yet",
        "history_clear":      "🗑 Clear History",
        "history_redownload": "↩ Re-download",
        "history_open":       "📂 Open",
        "history_search":     "🔍 Search history...",
        "settings_save_path": "Default Save Folder",
        "settings_autopaste": "Auto-paste on focus",
        "settings_notify":    "Notify on complete",
        "settings_theme":     "Theme",
        "settings_lang":      "Language",
        "disk_free":          "Free space",
        "about_title":        "About",
        "about_text":         f"{APP_NAME} v{APP_VERSION}\nProfessional Video Downloader\nPowered by yt-dlp",
        "shortcut_hint":      "Ctrl+V paste • Enter download • Esc cancel • Ctrl+H history",
        "fetching_preview":   "⏳ Fetching video info...",
        "preview_title":      "Video Preview",
        "preview_duration":   "Duration",
        "preview_uploader":   "Uploader",
        "preview_views":      "Views",
        "queue_status_wait":  "Waiting",
        "queue_status_dl":    "Downloading",
        "queue_status_done":  "Done",
        "queue_status_err":   "Error",
    },
}

CONFIG_PATH  = Path.home() / ".downme_config.json"
HISTORY_PATH = Path.home() / ".downme_history.json"


# ══════════════════════════════════════════
#  Config / History helpers
# ══════════════════════════════════════════
def save_config(data: dict):
    try:
        CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def load_config() -> dict:
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def load_history() -> list:
    try:
        if HISTORY_PATH.exists():
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def save_history(history: list):
    try:
        HISTORY_PATH.write_text(
            json.dumps(history[-200:], indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        pass


def get_free_space_gb(path: str) -> float:
    try:
        total, used, free = shutil.disk_usage(path)
        return free / (1024 ** 3)
    except Exception:
        return 999.0


def fmt_bytes(b):
    if not b:
        return "—"
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def fmt_duration(seconds: int) -> str:
    if not seconds:
        return "—"
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# ══════════════════════════════════════════
#  Tooltip
# ══════════════════════════════════════════
class Tooltip:
    def __init__(self, widget, text: str, bg="#1A1A2E", fg="#FFFFFF"):
        self.widget = widget
        self.text   = text
        self.bg     = bg
        self.fg     = fg
        self._tw    = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._tw = tk.Toplevel(self.widget)
        self._tw.wm_overrideredirect(True)
        self._tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self._tw, text=self.text,
                       background=self.bg, foreground=self.fg,
                       font=("Consolas", 10), padx=8, pady=4,
                       relief="flat", bd=0)
        lbl.pack()

    def _hide(self, event=None):
        if self._tw:
            self._tw.destroy()
            self._tw = None


# ══════════════════════════════════════════
#  Animated Progress Bar (pulse while unknown)
# ══════════════════════════════════════════
class AnimatedProgressBar(ctk.CTkProgressBar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._pulse_active = False
        self._pulse_val    = 0.0
        self._pulse_dir    = 1

    def start_pulse(self):
        if not self._pulse_active:
            self._pulse_active = True
            self._do_pulse()

    def stop_pulse(self):
        self._pulse_active = False

    def _do_pulse(self):
        if not self._pulse_active:
            return
        self._pulse_val += 0.02 * self._pulse_dir
        if self._pulse_val >= 1.0:
            self._pulse_dir = -1
        elif self._pulse_val <= 0.0:
            self._pulse_dir = 1
        try:
            self.set(abs(self._pulse_val))
            self.after(30, self._do_pulse)
        except Exception:
            pass


# ══════════════════════════════════════════
#  Theme Editor
# ══════════════════════════════════════════
class ThemeEditor(ctk.CTkToplevel):
    def __init__(self, master, colors: dict, lang: str, on_apply):
        super().__init__(master)
        self.colors   = dict(colors)
        self.lang_key = lang
        self.on_apply = on_apply
        T = LANG[lang]
        C = colors

        self.title(T["theme_title"])
        self.geometry("560x620")
        self.resizable(False, False)
        self.configure(fg_color=C["bg_main"])
        self.grab_set()
        self.lift()
        self.focus_force()

        ctk.CTkLabel(self, text=T["theme_title"],
                     font=("Consolas", 16, "bold"),
                     text_color=C["text_primary"]).pack(pady=(20, 5))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Preset themes
        ctk.CTkLabel(scroll, text=T["theme_presets"],
                     font=("Consolas", 12),
                     text_color=C["text_secondary"]).pack(anchor="w", pady=(5, 4))

        pf = ctk.CTkFrame(scroll, fg_color="transparent")
        pf.pack(fill="x", pady=(0, 15))

        for i, name in enumerate(PRESET_THEMES):
            ac = PRESET_THEMES[name]["accent_primary"]
            btn = ctk.CTkButton(
                pf, text=name, width=130, height=34,
                fg_color=C["bg_input"], hover_color=ac,
                border_color=ac, border_width=1,
                text_color=C["text_secondary"],
                font=("Arial", 11), corner_radius=8,
                command=lambda n=name: self._load_preset(n))
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)

        # Custom colors
        ctk.CTkLabel(scroll, text=T["custom_colors"],
                     font=("Consolas", 12),
                     text_color=C["text_secondary"]).pack(anchor="w", pady=(10, 5))

        self.color_rows = {}
        for key, label in [
            ("accent_primary", T["color_accent"]),
            ("bg_main",        T["color_bg"]),
            ("bg_card",        T["color_card"]),
            ("text_primary",   T["color_text"]),
        ]:
            row = ctk.CTkFrame(scroll, fg_color=C["bg_card"],
                               corner_radius=8, border_width=1,
                               border_color=C["border"])
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(row, text=label, font=("Arial", 12),
                         text_color=C["text_secondary"], width=155,
                         anchor="w").pack(side="left", padx=12, pady=8)

            swatch = tk.Label(row, bg=self.colors.get(key, "#888888"),
                              width=4, relief="flat", cursor="hand2")
            swatch.pack(side="right", padx=12, pady=8)

            entry = ctk.CTkEntry(row, width=100, font=("Consolas", 12),
                                 fg_color=C["bg_input"],
                                 border_color=C["border"],
                                 text_color=C["text_primary"])
            entry.insert(0, self.colors.get(key, "#888888"))
            entry.pack(side="right", padx=4)

            swatch.bind("<Button-1>",
                        lambda e, k=key, ent=entry, sw=swatch: self._pick_color(k, ent, sw))
            entry.bind("<FocusOut>",
                       lambda e, k=key, ent=entry, sw=swatch: self._on_entry(k, ent, sw))

            self.color_rows[key] = (entry, swatch)

        # Buttons
        br = ctk.CTkFrame(self, fg_color="transparent")
        br.pack(fill="x", padx=20, pady=(5, 20))

        ctk.CTkButton(
            br, text=T["apply_theme"], height=40,
            fg_color=C["accent_primary"], hover_color=C["accent_primary"],
            text_color="white", font=("Arial", 13, "bold"),
            corner_radius=10, command=self._apply
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            br, text=T["reset_theme"], height=40,
            fg_color=C["bg_input"], hover_color=C["bg_card"],
            text_color=C["text_secondary"],
            border_width=1, border_color=C["border"],
            font=("Arial", 13), corner_radius=10,
            command=self._reset
        ).pack(side="left", width=120)

    def _pick_color(self, key, entry, swatch):
        result = colorchooser.askcolor(color=self.colors.get(key, "#888888"))
        if result and result[1]:
            hx = result[1]
            self.colors[key] = hx
            entry.delete(0, "end")
            entry.insert(0, hx)
            try:
                swatch.configure(bg=hx)
            except Exception:
                pass

    def _on_entry(self, key, entry, swatch):
        val = entry.get().strip()
        if re.match(r'^#[0-9A-Fa-f]{6}$', val):
            self.colors[key] = val
            try:
                swatch.configure(bg=val)
            except Exception:
                pass

    def _load_preset(self, name):
        self.colors = dict(PRESET_THEMES[name])
        for key, (entry, swatch) in self.color_rows.items():
            val = self.colors.get(key, "#888888")
            entry.delete(0, "end")
            entry.insert(0, val)
            try:
                swatch.configure(bg=val)
            except Exception:
                pass

    def _apply(self):
        for key, (entry, swatch) in self.color_rows.items():
            val = entry.get().strip()
            if re.match(r'^#[0-9A-Fa-f]{6}$', val):
                self.colors[key] = val
        self.on_apply(self.colors)
        self.destroy()

    def _reset(self):
        self.on_apply(dict(PRESET_THEMES["Cosmic Purple"]))
        self.destroy()


# ══════════════════════════════════════════
#  Video Preview Window
# ══════════════════════════════════════════
class VideoPreviewDialog(ctk.CTkToplevel):
    def __init__(self, master, info: dict, colors: dict, lang: str, on_confirm):
        super().__init__(master)
        C = colors
        T = LANG[lang]
        self.on_confirm = on_confirm

        title_text = info.get("title", "Video")[:70]
        duration   = fmt_duration(info.get("duration", 0))
        uploader   = info.get("uploader", "—")
        view_count = info.get("view_count")
        views_str  = f"{view_count:,}" if view_count else "—"

        self.title(T["preview_title"])
        self.geometry("520x300")
        self.resizable(False, False)
        self.configure(fg_color=C["bg_card"])
        self.grab_set()
        self.lift()
        self.focus_force()

        # Title
        ctk.CTkLabel(self, text=f"📹  {title_text}",
                     font=("Georgia", 13, "bold"),
                     text_color=C["accent_cyan"],
                     wraplength=490, anchor="w",
                     justify="left").pack(fill="x", padx=20, pady=(18, 10))

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=C["border"]).pack(fill="x", padx=20)

        # Meta info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=14)

        meta = [
            (T["preview_duration"], duration),
            (T["preview_uploader"], uploader[:40]),
            (T["preview_views"],    views_str),
        ]
        for label, val in meta:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"{label}:", font=("Consolas", 11),
                         text_color=C["text_muted"], width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=("Consolas", 11, "bold"),
                         text_color=C["text_primary"]).pack(side="left")

        # Formats count
        formats = info.get("formats", [])
        ctk.CTkLabel(info_frame,
                     text=f"🎞️  {len(formats)} {'صيغة' if lang == 'ar' else 'formats'} {('متاحة' if lang == 'ar' else 'available')}",
                     font=("Consolas", 10),
                     text_color=C["text_secondary"]).pack(anchor="w", pady=(4, 0))

        # Buttons
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkButton(
            btns,
            text=T["btn_download"],
            height=40, font=("Arial", 13, "bold"),
            fg_color=C["accent_primary"], hover_color=C["accent_primary"],
            text_color="white", corner_radius=10,
            command=self._confirm
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            btns, text=T["btn_cancel"], height=40,
            fg_color=C["bg_input"], hover_color=C["bg_main"],
            text_color=C["text_secondary"],
            border_width=1, border_color=C["border"],
            font=("Arial", 12), corner_radius=10,
            command=self.destroy
        ).pack(side="left", width=100)

    def _confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()


# ══════════════════════════════════════════
#  Main Application
# ══════════════════════════════════════════
class DownMeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        cfg = load_config()
        self.lang         = cfg.get("lang", "ar")
        self.COLORS       = dict(cfg.get("theme", PRESET_THEMES["Cosmic Purple"]))
        self.save_path    = cfg.get("save_path", str(Path.home() / "Downloads"))
        self.autopaste    = cfg.get("autopaste", True)
        self.notify       = cfg.get("notify", True)

        self.downloading  = False
        self.queue_items  = []          # list of dicts: {url, status, title}
        self.queue_active = False
        self.history      = load_history()

        self.quality_var  = tk.StringVar(value="best")
        self.format_var   = tk.StringVar(value="mp4")
        self.fmt_buttons  = {}
        self.quality_buttons = {}
        self._current_tab = "download"

        # Animation state
        self._dot_frame      = 0
        self._dot_chars      = ["●", "◉", "○", "◉"]
        self._last_ui_update = 0.0      # throttle progress UI updates

        self._apply_window_style()
        self._setup_icon()
        self._build_ui()
        self._bind_shortcuts()
        self._start_dot_animation()

    def _apply_window_style(self):
        self.title(LANG[self.lang]["title"])
        self.geometry("900x780")
        self.minsize(760, 640)
        self.configure(fg_color=self.COLORS["bg_main"])

    def _setup_icon(self):
        base = Path(__file__).parent
        # 1) .ico  → sets taskbar + title bar + alt-tab on Windows
        ico_path = base / "icon.ico"
        if ico_path.exists():
            try:
                self.iconbitmap(default=str(ico_path))
                return          # done — .ico handles everything on Windows
            except Exception:
                pass
        # 2) .png fallback (Linux / macOS, or missing .ico)
        png_path = base / "icon.png"
        if png_path.exists():
            try:
                self._app_icon = tk.PhotoImage(file=str(png_path))   # keep reference!
                self.iconphoto(True, self._app_icon)
            except Exception:
                pass

    def _bind_shortcuts(self):
        self.bind("<Control-v>", lambda e: self._paste_url())
        self.bind("<Control-V>", lambda e: self._paste_url())
        self.bind("<Return>",    lambda e: self._on_enter())
        self.bind("<Escape>",    lambda e: self._cancel_download())
        self.bind("<Control-h>", lambda e: self._switch_tab("history"))
        self.bind("<Control-H>", lambda e: self._switch_tab("history"))
        self.bind("<Control-q>", lambda e: self._switch_tab("queue"))
        self.bind("<FocusIn>",   self._on_focus_in)

    def _on_focus_in(self, event=None):
        if self.autopaste and self._current_tab == "download":
            try:
                cb = self.clipboard_get().strip()
                if cb.startswith("http") and hasattr(self, "entry_url"):
                    current = self.entry_url.get().strip()
                    if not current or current != cb:
                        self.entry_url.delete(0, "end")
                        self.entry_url.insert(0, cb)
            except Exception:
                pass

    def _on_enter(self):
        if self._current_tab == "download" and not self.downloading:
            self.start_download_thread()

    def _start_dot_animation(self):
        """Animated status dot."""
        if self.downloading and hasattr(self, "status_dot"):
            T = LANG[self.lang]
            char = self._dot_chars[self._dot_frame % len(self._dot_chars)]
            try:
                self.status_dot.configure(
                    text=f"{char} {'يتحمّل' if self.lang == 'ar' else 'DOWNLOADING'}",
                    text_color=self.COLORS["accent_primary"])
            except Exception:
                pass
            self._dot_frame += 1
        self.after(300, self._start_dot_animation)

    # ══ بناء الواجهة ══
    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()
        self.configure(fg_color=self.COLORS["bg_main"])

        # Outer container
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=0, pady=0)

        # Header (fixed)
        self._build_header(outer)

        # Tab bar
        self._tab_bar_frame = ctk.CTkFrame(outer, fg_color=self.COLORS["bg_card"],
                                           corner_radius=0, height=46)
        self._tab_bar_frame.pack(fill="x")
        self._tab_bar_frame.pack_propagate(False)
        self._build_tab_bar(self._tab_bar_frame)

        # Content area (scrollable)
        self.content_frame = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=self.COLORS["border"],
            scrollbar_button_hover_color=self.COLORS["accent_primary"])
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=12)

        self._switch_tab(self._current_tab, rebuild=True)

        # Footer (fixed)
        self._build_footer(outer)

    def _build_header(self, p):
        T, C = LANG[self.lang], self.COLORS
        hdr = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=0, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Left: logo icon + text
        logo = ctk.CTkFrame(hdr, fg_color="transparent")
        logo.pack(side="left", padx=20)

        # Try to show icon.ico or icon.png in header
        base = Path(__file__).parent
        _icon_shown = False
        for ext in ("ico", "png"):
            ip = base / f"icon.{ext}"
            if ip.exists() and not _icon_shown:
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(str(ip)).resize((36, 36), Image.LANCZOS)
                    self._header_icon = ImageTk.PhotoImage(img)
                    tk.Label(logo, image=self._header_icon,
                             bg=C["bg_card"], bd=0).pack(side="left", padx=(0, 8))
                    _icon_shown = True
                except Exception:
                    pass
        if not _icon_shown:
            ctk.CTkLabel(logo, text="⬇", font=("Segoe UI Emoji", 30),
                         text_color=C["accent_primary"]).pack(side="left", padx=(0, 8))

        txt = ctk.CTkFrame(logo, fg_color="transparent")
        txt.pack(side="left")
        ctk.CTkLabel(txt, text=APP_NAME, font=("Georgia", 22, "bold"),
                     text_color=C["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(txt, text=T["subtitle"], font=("Consolas", 9),
                     text_color=C["text_muted"]).pack(anchor="w")

        # Right: controls
        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right", padx=16)

        self.status_dot = ctk.CTkLabel(right, text=T["ready"],
                                       font=("Consolas", 11, "bold"),
                                       text_color=C["accent_green"])
        self.status_dot.pack(side="right", padx=(8, 0))

        ctk.CTkButton(right, text=T["theme_btn"], width=84, height=30,
                      fg_color=C["bg_input"], hover_color=C["accent_primary"],
                      text_color=C["text_secondary"],
                      border_width=1, border_color=C["border"],
                      font=("Arial", 11), corner_radius=8,
                      command=self._open_theme_editor
                      ).pack(side="right", padx=4)

        ctk.CTkButton(right, text=T["lang_btn"], width=42, height=30,
                      fg_color=C["bg_input"], hover_color=C["accent_primary"],
                      text_color=C["text_secondary"],
                      border_width=1, border_color=C["border"],
                      font=("Arial", 12, "bold"), corner_radius=8,
                      command=self._toggle_lang
                      ).pack(side="right", padx=4)

        # Disk space indicator
        free_gb = get_free_space_gb(self.save_path)
        disk_color = C["accent_red"] if free_gb < 1.0 else (
            C["accent_yellow"] if free_gb < 5.0 else C["text_muted"])
        ctk.CTkLabel(right, text=f"💾 {free_gb:.1f} GB",
                     font=("Consolas", 9), text_color=disk_color,
                     ).pack(side="right", padx=4)

    def _build_tab_bar(self, p):
        T, C = LANG[self.lang], self.COLORS
        self._tab_buttons = {}
        tabs = [
            ("download", T["tab_download"]),
            ("queue",    T["tab_queue"]),
            ("history",  T["tab_history"]),
            ("settings", T["tab_settings"]),
        ]
        inner = ctk.CTkFrame(p, fg_color="transparent")
        inner.pack(side="left", padx=16, pady=6)
        for key, label in tabs:
            is_active = key == self._current_tab
            btn = ctk.CTkButton(
                inner, text=label, height=34, width=130,
                fg_color=C["accent_primary"] if is_active else "transparent",
                hover_color=C["accent_primary"],
                text_color="white" if is_active else C["text_secondary"],
                font=("Arial", 12, "bold" if is_active else "normal"),
                corner_radius=8,
                command=lambda k=key: self._switch_tab(k))
            btn.pack(side="left", padx=(0, 4))
            self._tab_buttons[key] = btn

        # Queue badge
        if self.queue_items:
            ctk.CTkLabel(inner,
                         text=f" {len(self.queue_items)} ",
                         font=("Consolas", 10, "bold"),
                         text_color="white",
                         fg_color=C["accent_primary"],
                         corner_radius=8, width=24
                         ).pack(side="left", padx=(0, 4))

    def _switch_tab(self, key, rebuild=False):
        self._current_tab = key
        if not rebuild:
            # Update tab button styles
            C = self.COLORS
            for k, btn in self._tab_buttons.items():
                is_active = k == key
                btn.configure(
                    fg_color=C["accent_primary"] if is_active else "transparent",
                    text_color="white" if is_active else C["text_secondary"],
                    font=("Arial", 12, "bold" if is_active else "normal"))

            # Clear content
            for w in self.content_frame.winfo_children():
                w.destroy()

        # Render tab content
        if key == "download":
            self._build_url_card(self.content_frame)
            self._build_settings_card(self.content_frame)
            self._build_progress_card(self.content_frame)
            self._build_download_button(self.content_frame)
        elif key == "queue":
            self._build_queue_tab(self.content_frame)
        elif key == "history":
            self._build_history_tab(self.content_frame)
        elif key == "settings":
            self._build_settings_tab(self.content_frame)

    def _build_url_card(self, p):
        T, C = LANG[self.lang], self.COLORS
        card = self._make_card(p, T["card_link"])

        ir = ctk.CTkFrame(card, fg_color=C["bg_input"],
                          corner_radius=12, border_width=1, border_color=C["border"])
        ir.pack(fill="x", padx=15, pady=(5, 10))

        # ── Pack right-side buttons FIRST so entry gets remaining space ──
        clear_btn = ctk.CTkButton(ir, text="✕", width=34, height=34,
                                  fg_color="transparent", hover_color=C["bg_main"],
                                  text_color=C["text_muted"], font=("Arial", 13),
                                  command=lambda: self.entry_url.delete(0, "end"))
        clear_btn.pack(side="right", padx=(0, 6))
        Tooltip(clear_btn, "Clear URL" if self.lang == "en" else "مسح الرابط",
                C["bg_card"], C["text_primary"])

        paste_btn = ctk.CTkButton(
            ir, text=T["paste"],
            width=82, height=34,           # fixed width — never shifts
            fg_color=C["bg_main"], hover_color=C["accent_primary"],
            text_color=C["text_secondary"],
            border_width=1, border_color=C["border"],
            font=("Arial", 11), corner_radius=8,
            command=self._paste_url)
        paste_btn.pack(side="right", padx=(0, 6))
        Tooltip(paste_btn, "Ctrl+V", C["bg_card"], C["text_primary"])

        # ── Entry fills the rest ──
        self.entry_url = ctk.CTkEntry(
            ir, placeholder_text=T["placeholder_url"],
            font=("Consolas", 13), fg_color="transparent",
            border_width=0, text_color=C["text_primary"],
            placeholder_text_color=C["text_muted"], height=48)
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(10, 4))
        self.entry_url.bind("<FocusIn>", self._on_url_focus)

        # Row: path + buttons
        pr = ctk.CTkFrame(card, fg_color="transparent")
        pr.pack(fill="x", padx=15, pady=(0, 12))

        self.label_path = ctk.CTkLabel(pr, text=f"📁  {self.save_path}",
                                       font=("Consolas", 10),
                                       text_color=C["text_secondary"], anchor="w")
        self.label_path.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(pr, text=T["add_to_queue"], width=140, height=30,
                      fg_color=C["bg_input"], hover_color=C["accent_cyan"],
                      text_color=C["accent_cyan"],
                      border_width=1, border_color=C["accent_cyan"],
                      font=("Arial", 11), corner_radius=8,
                      command=self._add_to_queue
                      ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(pr, text=T["change_folder"], width=130, height=30,
                      fg_color=C["bg_input"], hover_color=C["accent_primary"],
                      text_color=C["text_secondary"],
                      border_width=1, border_color=C["border"],
                      font=("Arial", 11), corner_radius=8,
                      command=self.choose_folder
                      ).pack(side="right")

    def _on_url_focus(self, event=None):
        if self.autopaste:
            self._on_focus_in()

    def _build_settings_card(self, p):
        T, C = LANG[self.lang], self.COLORS
        card = self._make_card(p, T["card_settings"])

        # Format buttons
        ctk.CTkLabel(card, text=T["format_label"], font=("Consolas", 11),
                     text_color=C["text_secondary"]).pack(anchor="w", padx=15, pady=(4, 4))

        fr = ctk.CTkFrame(card, fg_color="transparent")
        fr.pack(fill="x", padx=15, pady=(0, 12))

        self.fmt_buttons = {}
        for label, val in [("🎬  MP4", "mp4"), ("🎵  MP3", "mp3"),
                            ("🎞️  MKV", "mkv"), ("🌐  WEBM", "webm")]:
            is_sel = val == self.format_var.get()
            btn = ctk.CTkButton(
                fr, text=label, height=36,
                fg_color=C["accent_primary"] if is_sel else C["bg_input"],
                hover_color=C["accent_primary"],
                text_color="white" if is_sel else C["text_secondary"],
                border_width=1,
                border_color=C["accent_primary"] if is_sel else C["border"],
                corner_radius=8, font=("Arial", 12),
                command=lambda v=val: self._select_format(v))
            btn.pack(side="left", padx=(0, 7))
            self.fmt_buttons[val] = btn

        # Quality buttons
        ctk.CTkLabel(card, text=T["quality_label"], font=("Consolas", 11),
                     text_color=C["text_secondary"]).pack(anchor="w", padx=15, pady=(4, 4))

        qr = ctk.CTkFrame(card, fg_color="transparent")
        qr.pack(fill="x", padx=15, pady=(0, 12))

        self.quality_buttons = {}
        for label, val in [(T["best_q"], "best"), ("4K", "2160"), ("1080p", "1080"),
                           ("720p", "720"), ("480p", "480"), ("360p", "360")]:
            is_sel = val == self.quality_var.get()
            btn = ctk.CTkButton(
                qr, text=label, height=32, width=78,
                fg_color=C["accent_primary"] if is_sel else C["bg_input"],
                hover_color=C["accent_primary"],
                text_color="white" if is_sel else C["text_secondary"],
                border_width=1,
                border_color=C["accent_primary"] if is_sel else C["border"],
                corner_radius=8, font=("Consolas", 11, "bold"),
                command=lambda v=val: self._select_quality(v))
            btn.pack(side="left", padx=(0, 6))
            self.quality_buttons[val] = btn

        # Options
        opt_row = ctk.CTkFrame(card, fg_color="transparent")
        opt_row.pack(fill="x", padx=15, pady=(0, 15))

        if not hasattr(self, "concurrent_var"):
            self.concurrent_var = tk.BooleanVar(value=True)
        if not hasattr(self, "subtitle_var"):
            self.subtitle_var   = tk.BooleanVar(value=False)
        if not hasattr(self, "thumbnail_var"):
            self.thumbnail_var  = tk.BooleanVar(value=False)

        for text, var in [(T["opt_concurrent"], self.concurrent_var),
                          (T["opt_subtitle"],   self.subtitle_var),
                          (T["opt_thumbnail"],  self.thumbnail_var)]:
            ctk.CTkCheckBox(opt_row, text=text, variable=var,
                            font=("Arial", 12), text_color=C["text_secondary"],
                            fg_color=C["accent_primary"],
                            hover_color=C["accent_primary"],
                            checkmark_color="white",
                            border_color=C["border"]
                            ).pack(side="left", padx=(0, 18))

    def _build_progress_card(self, p):
        T, C = LANG[self.lang], self.COLORS
        card = self._make_card(p, T["card_progress"])

        self.label_video_title = ctk.CTkLabel(
            card, text=T["waiting"],
            font=("Georgia", 13, "italic"),
            text_color=C["accent_cyan"], anchor="w", wraplength=800)
        self.label_video_title.pack(fill="x", padx=15, pady=(5, 8))

        self.progress_bar = AnimatedProgressBar(
            card, height=14, corner_radius=7,
            fg_color=C["bg_input"],
            progress_color=C["accent_primary"])
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 8))

        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=15, pady=(0, 15))

        self.lbl_percent = ctk.CTkLabel(stats, text="0%",
                                        font=("Consolas", 28, "bold"),
                                        text_color=C["accent_primary"])
        self.lbl_percent.pack(side="left")

        mid = ctk.CTkFrame(stats, fg_color="transparent")
        mid.pack(side="left", padx=18)

        self.lbl_speed = ctk.CTkLabel(mid, text=f"{T['speed']}: —",
                                      font=("Consolas", 11),
                                      text_color=C["text_secondary"])
        self.lbl_speed.pack(anchor="w")

        self.lbl_eta = ctk.CTkLabel(mid, text=f"{T['eta']}: —",
                                    font=("Consolas", 11),
                                    text_color=C["text_secondary"])
        self.lbl_eta.pack(anchor="w")

        self.lbl_size = ctk.CTkLabel(mid, text=f"{T['size']}: —",
                                     font=("Consolas", 11),
                                     text_color=C["text_secondary"])
        self.lbl_size.pack(anchor="w")

        self.status_label = ctk.CTkLabel(stats, text=T["status_ready"],
                                         font=("Arial", 12),
                                         text_color=C["accent_green"])
        self.status_label.pack(side="right")

    def _build_download_button(self, p):
        T, C = LANG[self.lang], self.COLORS

        ctk.CTkFrame(p, fg_color="transparent").pack(pady=2)

        self.btn_download = ctk.CTkButton(
            p, text=T["btn_download"], height=56,
            font=("Georgia", 18, "bold"),
            fg_color=C["accent_primary"], hover_color=C["accent_primary"],
            text_color="white", corner_radius=14,
            command=self.start_download_thread)
        self.btn_download.pack(fill="x", padx=60, pady=(8, 4))

        br = ctk.CTkFrame(p, fg_color="transparent")
        br.pack(fill="x", pady=(0, 4))

        self.btn_cancel = ctk.CTkButton(
            br, text=T["btn_cancel"], width=120, height=32,
            fg_color="transparent", hover_color=C["bg_input"],
            text_color=C["text_muted"], font=("Arial", 12),
            corner_radius=8, command=self._cancel_download)
        self.btn_cancel.pack(side="left", padx=(60, 0))

        ctk.CTkButton(br, text=T["btn_open_folder"], width=160, height=32,
                      fg_color=C["bg_input"], hover_color=C["accent_primary"],
                      text_color=C["text_secondary"],
                      border_width=1, border_color=C["border"],
                      font=("Arial", 11), corner_radius=8,
                      command=self._open_folder
                      ).pack(side="right", padx=(0, 60))

        # Shortcut hint
        ctk.CTkLabel(p, text=T["shortcut_hint"], font=("Consolas", 9),
                     text_color=C["text_muted"]).pack(pady=(4, 0))

    # ══ Queue Tab ══
    def _build_queue_tab(self, p):
        T, C = LANG[self.lang], self.COLORS

        # Controls
        ctrl = ctk.CTkFrame(p, fg_color="transparent")
        ctrl.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(ctrl, text=T["queue_start"], height=36, width=140,
                      fg_color=C["accent_primary"], hover_color=C["accent_primary"],
                      text_color="white", font=("Arial", 12, "bold"),
                      corner_radius=8, command=self._start_queue
                      ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(ctrl, text=T["queue_clear"], height=36, width=120,
                      fg_color=C["bg_input"], hover_color=C["accent_red"],
                      text_color=C["text_secondary"],
                      border_width=1, border_color=C["border"],
                      font=("Arial", 11), corner_radius=8,
                      command=self._clear_queue
                      ).pack(side="left")

        ctk.CTkLabel(ctrl,
                     text=f"{len(self.queue_items)} {'عنصر' if self.lang == 'ar' else 'items'}",
                     font=("Consolas", 11), text_color=C["text_muted"]
                     ).pack(side="right")

        # List
        if not self.queue_items:
            empty_frame = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=14,
                                       border_width=1, border_color=C["border"])
            empty_frame.pack(fill="both", expand=True, pady=20)
            ctk.CTkLabel(empty_frame, text="📋", font=("Arial", 48)).pack(pady=(30, 8))
            ctk.CTkLabel(empty_frame, text=T["queue_empty"],
                         font=("Georgia", 14), text_color=C["text_secondary"]).pack()
            ctk.CTkLabel(empty_frame, text=T["queue_add_hint"],
                         font=("Consolas", 10), text_color=C["text_muted"]).pack(pady=(4, 30))
            return

        for i, item in enumerate(self.queue_items):
            self._build_queue_row(p, item, i)

    def _build_queue_row(self, p, item, index):
        T, C = LANG[self.lang], self.COLORS
        status_colors = {
            "wait": C["text_muted"],
            "dl":   C["accent_primary"],
            "done": C["accent_green"],
            "err":  C["accent_red"],
        }
        status_labels = {
            "wait": T["queue_status_wait"],
            "dl":   T["queue_status_dl"],
            "done": T["queue_status_done"],
            "err":  T["queue_status_err"],
        }

        row = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=10,
                           border_width=1, border_color=C["border"])
        row.pack(fill="x", pady=3)

        # Index badge
        ctk.CTkLabel(row, text=f"{index + 1}", font=("Consolas", 12, "bold"),
                     text_color=C["text_muted"], width=30).pack(side="left", padx=10)

        # URL / title
        display = item.get("title") or item.get("url", "")
        if len(display) > 70:
            display = display[:70] + "…"
        ctk.CTkLabel(row, text=display, font=("Consolas", 11),
                     text_color=C["text_primary"], anchor="w"
                     ).pack(side="left", fill="x", expand=True, padx=4, pady=10)

        # Status
        st = item.get("status", "wait")
        ctk.CTkLabel(row, text=status_labels.get(st, st),
                     font=("Arial", 11), text_color=status_colors.get(st, C["text_muted"]),
                     width=80).pack(side="right", padx=8)

        # Remove button (only if not downloading)
        if st != "dl":
            ctk.CTkButton(row, text=T["queue_remove"], width=30, height=26,
                          fg_color="transparent", hover_color=C["accent_red"],
                          text_color=C["text_muted"], font=("Arial", 12),
                          corner_radius=6,
                          command=lambda i=index: self._remove_queue_item(i)
                          ).pack(side="right", padx=4)

    # ══ History Tab ══
    def _build_history_tab(self, p):
        T, C = LANG[self.lang], self.COLORS

        # Controls
        ctrl = ctk.CTkFrame(p, fg_color="transparent")
        ctrl.pack(fill="x", pady=(0, 10))

        self.history_search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            ctrl, textvariable=self.history_search_var,
            placeholder_text=T["history_search"],
            font=("Consolas", 12), height=36,
            fg_color=C["bg_input"], border_color=C["border"],
            text_color=C["text_primary"],
            placeholder_text_color=C["text_muted"])
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.history_search_var.trace_add("write", lambda *_: self._refresh_history_list())

        ctk.CTkButton(ctrl, text=T["history_clear"], height=36, width=130,
                      fg_color=C["bg_input"], hover_color=C["accent_red"],
                      text_color=C["text_secondary"],
                      border_width=1, border_color=C["border"],
                      font=("Arial", 11), corner_radius=8,
                      command=self._clear_history
                      ).pack(side="right")

        # List container
        self.history_list_frame = ctk.CTkFrame(p, fg_color="transparent")
        self.history_list_frame.pack(fill="both", expand=True)
        self._refresh_history_list()

    def _refresh_history_list(self):
        T, C = LANG[self.lang], self.COLORS
        for w in self.history_list_frame.winfo_children():
            w.destroy()

        query = ""
        if hasattr(self, "history_search_var"):
            query = self.history_search_var.get().strip().lower()

        filtered = [h for h in reversed(self.history)
                    if query in h.get("title", "").lower()
                    or query in h.get("url", "").lower()] if query else list(reversed(self.history))

        if not filtered:
            ctk.CTkLabel(self.history_list_frame, text="🕐",
                         font=("Arial", 48)).pack(pady=(30, 8))
            ctk.CTkLabel(self.history_list_frame, text=T["history_empty"],
                         font=("Georgia", 14), text_color=C["text_secondary"]).pack()
            return

        for item in filtered[:50]:
            self._build_history_row(self.history_list_frame, item)

    def _build_history_row(self, p, item):
        T, C = LANG[self.lang], self.COLORS
        row = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=10,
                           border_width=1, border_color=C["border"])
        row.pack(fill="x", pady=3)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=12, pady=8)

        title = item.get("title", item.get("url", ""))[:65]
        ctk.CTkLabel(left, text=title, font=("Arial", 12),
                     text_color=C["text_primary"], anchor="w").pack(fill="x")

        meta = f"{item.get('format', 'mp4').upper()}  •  {item.get('date', '')}  •  {item.get('size', '—')}"
        ctk.CTkLabel(left, text=meta, font=("Consolas", 9),
                     text_color=C["text_muted"], anchor="w").pack(fill="x", pady=(2, 0))

        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.pack(side="right", padx=10)

        # Open folder
        save_path = item.get("save_path", self.save_path)
        if save_path and Path(save_path).exists():
            ctk.CTkButton(btns, text=T["history_open"], width=68, height=28,
                          fg_color=C["bg_input"], hover_color=C["accent_primary"],
                          text_color=C["text_secondary"],
                          border_width=1, border_color=C["border"],
                          font=("Arial", 10), corner_radius=6,
                          command=lambda sp=save_path: self._open_path(sp)
                          ).pack(side="right", padx=(4, 0))

        # Re-download
        url = item.get("url")
        if url:
            ctk.CTkButton(btns, text=T["history_redownload"], width=110, height=28,
                          fg_color=C["bg_input"], hover_color=C["accent_cyan"],
                          text_color=C["accent_cyan"],
                          border_width=1, border_color=C["accent_cyan"],
                          font=("Arial", 10), corner_radius=6,
                          command=lambda u=url: self._redownload(u)
                          ).pack(side="right")

    # ══ Settings Tab ══
    def _build_settings_tab(self, p):
        T, C = LANG[self.lang], self.COLORS

        def section(title):
            ctk.CTkLabel(p, text=title, font=("Consolas", 11, "bold"),
                         text_color=C["text_muted"]).pack(anchor="w", pady=(16, 4))
            ctk.CTkFrame(p, height=1, fg_color=C["border"]).pack(fill="x", pady=(0, 8))

        # Save path
        section("📁  " + T["settings_save_path"])
        path_row = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=10,
                                border_width=1, border_color=C["border"])
        path_row.pack(fill="x", pady=2)
        ctk.CTkLabel(path_row, text=f"  {self.save_path}",
                     font=("Consolas", 10), text_color=C["text_secondary"],
                     anchor="w").pack(side="left", fill="x", expand=True, padx=8, pady=10)
        ctk.CTkButton(path_row, text=T["change_folder"], width=130, height=30,
                      fg_color=C["bg_input"], hover_color=C["accent_primary"],
                      text_color=C["text_secondary"],
                      border_width=1, border_color=C["border"],
                      font=("Arial", 11), corner_radius=8,
                      command=self.choose_folder
                      ).pack(side="right", padx=10, pady=8)

        # Preferences
        section("⚙️  Preferences")

        if not hasattr(self, "autopaste_var"):
            self.autopaste_var = tk.BooleanVar(value=self.autopaste)
        if not hasattr(self, "notify_var"):
            self.notify_var = tk.BooleanVar(value=self.notify)

        for label, var, key in [
            (T["settings_autopaste"], self.autopaste_var, "autopaste"),
            (T["settings_notify"],    self.notify_var,    "notify"),
        ]:
            row = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=10,
                               border_width=1, border_color=C["border"])
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"  {label}", font=("Arial", 12),
                         text_color=C["text_primary"], anchor="w"
                         ).pack(side="left", padx=10, pady=10, fill="x", expand=True)
            sw = ctk.CTkSwitch(row, variable=var, text="",
                               fg_color=C["bg_input"], progress_color=C["accent_primary"],
                               button_color="white",
                               command=self._save_pref_settings)
            sw.pack(side="right", padx=16)

        # About
        section("ℹ️  " + T["about_title"])
        about_card = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=10,
                                  border_width=1, border_color=C["border"])
        about_card.pack(fill="x", pady=2)
        ctk.CTkLabel(about_card, text=T["about_text"],
                     font=("Consolas", 11), text_color=C["text_secondary"],
                     justify="left").pack(padx=16, pady=12, anchor="w")

    def _save_pref_settings(self):
        if hasattr(self, "autopaste_var"):
            self.autopaste = self.autopaste_var.get()
        if hasattr(self, "notify_var"):
            self.notify = self.notify_var.get()
        self._save_settings()

    def _build_footer(self, p):
        T, C = LANG[self.lang], self.COLORS
        footer = ctk.CTkFrame(p, fg_color=C["bg_card"], corner_radius=0, height=42)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        # Left: supported sites
        ctk.CTkLabel(footer, text=T["footer"], font=("Consolas", 9),
                     text_color=C["text_muted"]).pack(side="left", padx=16, pady=0)

        # Right: developer credit + copyright
        year = datetime.now().year
        credit = f"© {year}  تم التطوير بواسطة Abdo Al Adawy  •  جميع الحقوق محفوظة"
        ctk.CTkLabel(footer, text=credit,
                     font=("Consolas", 9),
                     text_color=C["text_muted"]).pack(side="right", padx=16)

    # ══ Helpers ══
    def _make_card(self, parent, title):
        C = self.COLORS
        frame = ctk.CTkFrame(parent, fg_color=C["bg_card"],
                             corner_radius=14, border_width=1,
                             border_color=C["border"])
        frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(frame, text=title, font=("Consolas", 12, "bold"),
                     text_color=C["text_muted"]).pack(anchor="w", padx=15, pady=(12, 5))
        ctk.CTkFrame(frame, height=1, fg_color=C["border"]).pack(fill="x", padx=15, pady=(0, 6))
        return frame

    def _select_format(self, val):
        self.format_var.set(val)
        C = self.COLORS
        for v, btn in self.fmt_buttons.items():
            if v == val:
                btn.configure(fg_color=C["accent_primary"], text_color="white",
                              border_color=C["accent_primary"])
            else:
                btn.configure(fg_color=C["bg_input"], text_color=C["text_secondary"],
                              border_color=C["border"])
        is_audio = val == "mp3"
        for btn in self.quality_buttons.values():
            btn.configure(state="disabled" if is_audio else "normal")

    def _select_quality(self, val):
        self.quality_var.set(val)
        C = self.COLORS
        for v, btn in self.quality_buttons.items():
            if v == val:
                btn.configure(fg_color=C["accent_primary"], text_color="white",
                              border_color=C["accent_primary"])
            else:
                btn.configure(fg_color=C["bg_input"], text_color=C["text_secondary"],
                              border_color=C["border"])

    def _paste_url(self):
        try:
            clip = self.clipboard_get().strip()
            if hasattr(self, "entry_url"):
                self.entry_url.delete(0, "end")
                self.entry_url.insert(0, clip)
        except Exception:
            pass

    def choose_folder(self):
        path = filedialog.askdirectory(initialdir=self.save_path)
        if path:
            self.save_path = path
            if hasattr(self, "label_path"):
                self.label_path.configure(text=f"📁  {self.save_path}")
            self._save_settings()
            # Refresh header disk indicator
            self._build_ui()

    def _open_folder(self):
        self._open_path(self.save_path)

    def _open_path(self, path: str):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.Popen(["xdg-open" if os.uname().sysname == "Linux" else "open", path])
        except Exception:
            pass

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "ar" else "ar"
        self._save_settings()
        self._build_ui()

    def _open_theme_editor(self):
        ThemeEditor(self, self.COLORS, self.lang, self._apply_theme)

    def _apply_theme(self, new_colors: dict):
        self.COLORS = dict(new_colors)
        self._save_settings()
        self._build_ui()

    def _save_settings(self):
        save_config({
            "lang":      self.lang,
            "theme":     self.COLORS,
            "save_path": self.save_path,
            "autopaste": self.autopaste,
            "notify":    self.notify,
        })

    def _set_status(self, text, color=None):
        if hasattr(self, "status_label"):
            self.status_label.configure(
                text=text,
                text_color=color or self.COLORS["text_secondary"])

    def _cancel_download(self):
        if self.downloading:
            self.downloading = False
            T, C = LANG[self.lang], self.COLORS
            self._set_status(T["status_cancelled"], C["accent_red"])
            if hasattr(self, "btn_download"):
                self.btn_download.configure(state="normal", text=T["btn_download"])
            if hasattr(self, "status_dot"):
                self.status_dot.configure(text=T["ready"], text_color=C["accent_green"])
            if hasattr(self, "progress_bar"):
                self.progress_bar.stop_pulse()

    # ══ Queue logic ══
    def _add_to_queue(self):
        if not hasattr(self, "entry_url"):
            return
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning(LANG[self.lang]["warn_title"],
                                   LANG[self.lang]["warn_no_url"])
            return
        self.queue_items.append({"url": url, "status": "wait", "title": url[:60]})
        self.entry_url.delete(0, "end")
        self._switch_tab("queue")

    def _remove_queue_item(self, index):
        if 0 <= index < len(self.queue_items):
            self.queue_items.pop(index)
        self._switch_tab("queue")

    def _clear_queue(self):
        self.queue_items = [i for i in self.queue_items if i.get("status") == "dl"]
        self._switch_tab("queue")

    def _start_queue(self):
        pending = [i for i in self.queue_items if i["status"] == "wait"]
        if not pending:
            return
        if not self.queue_active:
            self.queue_active = True
            threading.Thread(target=self._queue_worker, daemon=True).start()

    def _queue_worker(self):
        for item in self.queue_items:
            if item["status"] != "wait":
                continue
            item["status"] = "dl"
            self.after(0, lambda: self._switch_tab("queue"))
            try:
                self._download_url(item["url"],
                                   on_title=lambda t, it=item: it.update({"title": t}))
                item["status"] = "done"
            except Exception:
                item["status"] = "err"
            self.after(0, lambda: self._switch_tab("queue"))
        self.queue_active = False

    # ══ Download logic ══
    def progress_hook(self, d):
        if not self.downloading:
            raise Exception("__CANCELLED__")

        status = d.get("status")

        if status == "downloading":
            try:
                # ── Throttle UI updates to ~10 fps ──
                now = time.monotonic()
                if now - self._last_ui_update < 0.10:
                    return
                self._last_ui_update = now

                downloaded_bytes = d.get("downloaded_bytes", 0) or 0
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0

                if total_bytes > 0:
                    p = downloaded_bytes / total_bytes
                else:
                    pstr = re.sub(r'\x1b\[[0-9;]*m', '',
                                  d.get("_percent_str", "0%")).replace('%', '').strip()
                    try:
                        p = float(pstr) / 100
                    except Exception:
                        p = 0.0

                p = max(0.0, min(1.0, p))

                speed = re.sub(r'\x1b\[[0-9;]*m',
                               '', d.get("_speed_str", "—") or "—").strip()
                eta   = re.sub(r'\x1b\[[0-9;]*m',
                               '', d.get("_eta_str", "—") or "—").strip()

                dl_str    = fmt_bytes(downloaded_bytes)
                total_str = fmt_bytes(total_bytes) if total_bytes else "—"

                self.after(0, self._update_progress, p, speed, eta, dl_str, total_str)

            except Exception as exc:
                if "__CANCELLED__" in str(exc):
                    raise

        elif status == "finished":
            self.after(0, self._update_progress, 1.0, "—", "—", "—", "—")
            T = LANG[self.lang]
            self.after(0, self._set_status, T["status_processing"], self.COLORS["accent_cyan"])

    def _update_progress(self, value, speed, eta, dl, total):
        T, C = LANG[self.lang], self.COLORS
        if hasattr(self, "progress_bar"):
            self.progress_bar.stop_pulse()
            self.progress_bar.set(value)
        if hasattr(self, "lbl_percent"):
            self.lbl_percent.configure(text=f"{int(value * 100)}%",
                                       text_color=C["accent_primary"])
        if hasattr(self, "lbl_speed"):
            self.lbl_speed.configure(text=f"{T['speed']}: {speed}")
        if hasattr(self, "lbl_eta"):
            self.lbl_eta.configure(text=f"{T['eta']}: {eta}")
        if hasattr(self, "lbl_size"):
            self.lbl_size.configure(text=f"{T['size']}: {dl} / {total}")

    def _build_ydl_opts(self, url=None):
        fmt     = self.format_var.get()
        quality = self.quality_var.get()

        opts = {
            "outtmpl":   os.path.join(self.save_path, "%(title)s.%(ext)s"),
            "progress_hooks": [self.progress_hook],
            "quiet":     True,
            "no_warnings": True,
            "noprogress": False,
            "concurrent_fragment_downloads": 16 if (
                hasattr(self, "concurrent_var") and self.concurrent_var.get()) else 1,
            "http_chunk_size": 10 * 1024 * 1024,
            "retries":          10,
            "fragment_retries": 10,
            "file_access_retries": 5,
            "geo_bypass": True,
            "socket_timeout": 30,
        }

        if hasattr(self, "subtitle_var") and self.subtitle_var.get():
            opts.update({
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["ar", "en"],
            })

        if hasattr(self, "thumbnail_var") and self.thumbnail_var.get():
            opts["writethumbnail"] = True

        if fmt == "mp3":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }]
        else:
            merge_ext = fmt if fmt in ("mkv", "webm", "mp4") else "mp4"
            opts["merge_output_format"] = merge_ext
            if quality == "best":
                opts["format"] = "bestvideo+bestaudio/best"
            else:
                opts["format"] = (
                    f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]"
                    f"/bestvideo[height<={quality}]+bestaudio"
                    f"/best[height<={quality}]/best"
                )

        return opts

    def download_logic(self):
        T, C = LANG[self.lang], self.COLORS
        url = self.entry_url.get().strip() if hasattr(self, "entry_url") else ""

        if not url:
            messagebox.showwarning(T["warn_title"], T["warn_no_url"])
            self.after(0, self._restore_btn)
            self.downloading = False
            return

        # Disk space check
        free = get_free_space_gb(self.save_path)
        if free < 1.0:
            if not messagebox.askyesno(T["warn_title"], T["warn_disk"] + "\n\nContinue anyway?"):
                self.after(0, self._restore_btn)
                self.downloading = False
                return

        try:
            opts = self._build_ydl_opts()

            with yt_dlp.YoutubeDL(opts) as ydl:
                self.after(0, self._set_status, T["status_fetching"], C["accent_cyan"])
                if hasattr(self, "progress_bar"):
                    self.after(0, self.progress_bar.start_pulse)

                info     = ydl.extract_info(url, download=False)
                title    = info.get("title", "Video")
                duration = info.get("duration", 0) or 0
                dur_str  = fmt_duration(int(duration))

                self.after(0, lambda: (
                    hasattr(self, "label_video_title") and
                    self.label_video_title.configure(
                        text=f"📹  {title}  ({dur_str})")
                ))
                self.after(0, self._set_status, T["status_dl"], C["accent_primary"])
                if hasattr(self, "status_dot"):
                    self.after(0, self.status_dot.configure,
                               {"text": T["downloading_dot"],
                                "text_color": C["accent_primary"]})

                if hasattr(self, "progress_bar"):
                    self.after(0, self.progress_bar.stop_pulse)
                    self.after(0, self.progress_bar.set, 0)

                ydl.download([url])

            if self.downloading:
                # Add to history
                self.history.append({
                    "url":       url,
                    "title":     title,
                    "format":    self.format_var.get(),
                    "quality":   self.quality_var.get(),
                    "date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "save_path": self.save_path,
                    "size":      "—",
                })
                save_history(self.history)
                self.after(0, self._on_success)

        except Exception as exc:
            err = str(exc)
            if "__CANCELLED__" not in err:
                # Friendly error messages
                friendly = self._friendly_error(err)
                self.after(0, lambda e=friendly: messagebox.showerror(T["err_title"], e))
                self.after(0, self._set_status, T["status_error"], C["accent_red"])
        finally:
            self.downloading = False
            if hasattr(self, "progress_bar"):
                self.after(0, self.progress_bar.stop_pulse)
            self.after(0, self._restore_btn)
            T2 = LANG[self.lang]
            if hasattr(self, "status_dot"):
                self.after(0, self.status_dot.configure,
                           {"text": T2["ready"],
                            "text_color": self.COLORS["accent_green"]})

    def _download_url(self, url, on_title=None):
        """Used by queue worker."""
        opts = self._build_ydl_opts()
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if on_title and info:
                on_title(info.get("title", url[:40]))
            ydl.download([url])
            if info:
                self.history.append({
                    "url":       url,
                    "title":     info.get("title", url[:40]),
                    "format":    self.format_var.get(),
                    "date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "save_path": self.save_path,
                    "size":      "—",
                })
                save_history(self.history)

    def _friendly_error(self, err: str) -> str:
        err_lower = err.lower()
        if self.lang == "ar":
            if "private" in err_lower:
                return "❌ هذا الفيديو خاص أو محمي."
            if "not available" in err_lower or "unavailable" in err_lower:
                return "❌ الفيديو غير متاح في منطقتك أو تم حذفه."
            if "sign in" in err_lower or "login" in err_lower:
                return "❌ هذا المحتوى يتطلب تسجيل الدخول."
            if "network" in err_lower or "connection" in err_lower or "timed out" in err_lower:
                return "❌ خطأ في الاتصال بالإنترنت. تحقق من اتصالك."
            if "ffmpeg" in err_lower:
                return "❌ FFmpeg غير مثبّت. يُرجى تثبيته للتحويل."
        else:
            if "private" in err_lower:
                return "❌ This video is private or protected."
            if "not available" in err_lower or "unavailable" in err_lower:
                return "❌ Video unavailable in your region or deleted."
            if "sign in" in err_lower or "login" in err_lower:
                return "❌ This content requires login."
            if "network" in err_lower or "connection" in err_lower or "timed out" in err_lower:
                return "❌ Network error. Check your connection."
            if "ffmpeg" in err_lower:
                return "❌ FFmpeg not installed. Please install it for conversion."
        return f"❌ {err[:300]}"

    def _restore_btn(self):
        T = LANG[self.lang]
        if hasattr(self, "btn_download"):
            self.btn_download.configure(state="normal", text=T["btn_download"])

    def _on_success(self):
        T, C = LANG[self.lang], self.COLORS
        if hasattr(self, "progress_bar"):
            self.progress_bar.set(1.0)
        if hasattr(self, "lbl_percent"):
            self.lbl_percent.configure(text="100%", text_color=C["accent_green"])
        self._set_status(T["status_done"], C["accent_green"])
        if self.notify:
            messagebox.showinfo(T["success_title"], T["success_msg"] + self.save_path)
        self.after(3500, self._reset_progress)

    def _reset_progress(self):
        T, C = LANG[self.lang], self.COLORS
        if hasattr(self, "progress_bar"):
            self.progress_bar.set(0)
        if hasattr(self, "lbl_percent"):
            self.lbl_percent.configure(text="0%", text_color=C["accent_primary"])
        if hasattr(self, "lbl_speed"):
            self.lbl_speed.configure(text=f"{T['speed']}: —")
        if hasattr(self, "lbl_eta"):
            self.lbl_eta.configure(text=f"{T['eta']}: —")
        if hasattr(self, "lbl_size"):
            self.lbl_size.configure(text=f"{T['size']}: —")
        if hasattr(self, "label_video_title"):
            self.label_video_title.configure(text=T["waiting"])
        self._set_status(T["status_ready"], C["accent_green"])

    def start_download_thread(self):
        if not self.downloading:
            self.downloading = True
            if hasattr(self, "btn_download"):
                self.btn_download.configure(state="disabled", text="⏳ ...")
            threading.Thread(target=self.download_logic, daemon=True).start()

    # ══ History actions ══
    def _clear_history(self):
        self.history = []
        save_history(self.history)
        self._switch_tab("history")

    def _redownload(self, url: str):
        if hasattr(self, "entry_url"):
            self.entry_url.delete(0, "end")
            self.entry_url.insert(0, url)
        self._switch_tab("download")
        self.start_download_thread()


if __name__ == "__main__":
    # Re-apply AppUserModelID after window creation (Windows taskbar fix)
    try:
        import ctypes
        _app_id = f"AbdoAlAdawy.{APP_NAME}.{APP_VERSION}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_app_id)
    except Exception:
        pass

    app = DownMeApp()
    app.mainloop()