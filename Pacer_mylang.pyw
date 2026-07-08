"""
Pacer + mylang  v0.5.1
A production-ready code editor for the mylang language.
"""

import sys
import os
import re
import io
import json
import shutil
import tempfile
import datetime
import traceback

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QFileSystemModel, QTreeView,
    QTextEdit, QDockWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLineEdit, QLabel, QTabWidget, QMenuBar, QAction, QFileDialog,
    QMessageBox, QPlainTextEdit, QComboBox, QDialog, QDialogButtonBox,
    QSpinBox, QCheckBox, QGroupBox, QFormLayout, QScrollArea,
    QColorDialog, QStackedWidget, QListWidget, QListWidgetItem, QInputDialog
)
from PyQt5.QtCore import Qt, QRect, QDir, QSize, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QColor, QSyntaxHighlighter,
    QPainter, QTextCursor, QIcon, QKeySequence
)

# ── LLM provider clients (each is optional — only required if selected) ──────
try:
    import anthropic as _anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

try:
    import openai as _openai
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

try:
    import google.generativeai as _google_genai
    _GOOGLE_AVAILABLE = True
except ImportError:
    _GOOGLE_AVAILABLE = False

# Groq and other OpenAI-compatible providers reuse the openai package's
# client with a custom base_url, so they share _OPENAI_AVAILABLE.


# ── Provider registry ─────────────────────────────────────────────────────────
# Each provider entry describes how Settings → AI should present it and how
# AIWorker should call it. Adding a new provider means adding one entry here.

PROVIDERS = {
    "anthropic": {
        "label":     "Anthropic (Claude)",
        "models":    ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-6"],
        "env_var":   "ANTHROPIC_API_KEY",
        "key_field": "api_key_anthropic",
        "key_hint":  "sk-ant-...",
        "available": lambda: _ANTHROPIC_AVAILABLE,
        "pip_name":  "anthropic",
    },
    "openai": {
        "label":     "OpenAI (GPT)",
        "models":    ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "o3-mini"],
        "env_var":   "OPENAI_API_KEY",
        "key_field": "api_key_openai",
        "key_hint":  "sk-...",
        "available": lambda: _OPENAI_AVAILABLE,
        "pip_name":  "openai",
    },
    "google": {
        "label":     "Google (Gemini)",
        "models":    ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"],
        "env_var":   "GOOGLE_API_KEY",
        "key_field": "api_key_google",
        "key_hint":  "AIza...",
        "available": lambda: _GOOGLE_AVAILABLE,
        "pip_name":  "google-generativeai",
    },
    "groq": {
        "label":     "Groq",
        "models":    ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
        "env_var":   "GROQ_API_KEY",
        "key_field": "api_key_groq",
        "key_hint":  "gsk_...",
        "available": lambda: _OPENAI_AVAILABLE,   # uses the openai SDK with a custom base_url
        "pip_name":  "openai",
        "base_url":  "https://api.groq.com/openai/v1",
    },
    "openrouter": {
        "label":     "OpenRouter (multi-model)",
        "models":    ["anthropic/claude-sonnet-4.6", "openai/gpt-4.1", "meta-llama/llama-3.3-70b-instruct"],
        "env_var":   "OPENROUTER_API_KEY",
        "key_field": "api_key_openrouter",
        "key_hint":  "sk-or-...",
        "available": lambda: _OPENAI_AVAILABLE,   # OpenRouter is OpenAI-API-compatible
        "pip_name":  "openai",
        "base_url":  "https://openrouter.ai/api/v1",
    },
}

PROVIDER_ORDER = ["anthropic", "openai", "google", "groq", "openrouter"]

# ── Import mylang pipeline ────────────────────────────────────────────────────
_MYLANG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mylang")
if _MYLANG_DIR not in sys.path:
    sys.path.insert(0, _MYLANG_DIR)

try:
    from lexer       import Lexer,  LexerError
    from parser      import Parser, ParseError
    from interpreter import Interpreter, RuntimeError as MylangRuntimeError
    MYLANG_AVAILABLE = True
except ImportError:
    MYLANG_AVAILABLE = False


# =============================================================================
# Settings engine
# =============================================================================

SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".pacer_settings.json")

DEFAULTS = {
    "font_family":        "Consolas",
    "font_size":          11,
    "tab_width":          4,
    "word_wrap":          False,
    "auto_indent":        True,
    "show_line_numbers":  True,
    "highlight_line":     True,
    "theme":              "dark",
    "accent_color":       "#007ACC",
    "ai_provider":         "anthropic",
    "api_key_anthropic":   "",
    "api_key_openai":      "",
    "api_key_google":      "",
    "api_key_groq":        "",
    "api_key_openrouter":  "",
    "ai_model":            "claude-sonnet-4-6",
    "ai_max_tokens":       2048,
    "auto_save_on_run":   True,
    "clear_output_on_run":True,
    "default_save_dir":   "",
    "last_project_folder":"",
    "auto_backup":        False,
    "backup_interval":    5,
    "backup_dir":         "",
    "keys": {
        "new_ml":     "Ctrl+N",
        "new_other":  "Ctrl+Shift+N",
        "open":       "Ctrl+O",
        "open_folder":"Ctrl+K Ctrl+O",
        "save":       "Ctrl+S",
        "save_as":    "Ctrl+Shift+S",
        "run":        "F5",
        "settings":   "Ctrl+,",
    },
}


class Settings:
    def __init__(self):
        self._data = dict(DEFAULTS)
        self._data["keys"] = dict(DEFAULTS["keys"])
        self.load()

    def load(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for k, v in saved.items():
                    if k == "keys" and isinstance(v, dict):
                        self._data["keys"].update(v)
                    else:
                        self._data[k] = v
                # Migrate pre-multi-provider configs: a bare "api_key" field
                # from older Pacer versions held the Anthropic key directly.
                old_key = saved.get("api_key", "")
                if old_key and not self._data.get("api_key_anthropic"):
                    self._data["api_key_anthropic"] = old_key
        except Exception:
            pass

    def save(self):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def key(self, action: str) -> str:
        return self._data["keys"].get(action, "")

    def set_key(self, action: str, shortcut: str):
        self._data["keys"][action] = shortcut


_settings = Settings()


# =============================================================================
# Settings Dialog
# =============================================================================

class SettingsDialog(QDialog):
    applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pacer — Settings")
        self.setMinimumSize(700, 540)
        self.setModal(True)
        self._accent_color = _settings.get("accent_color", "#007ACC")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 12)

        body = QHBoxLayout()
        root.addLayout(body)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(152)
        self.sidebar.setStyleSheet("""
            QListWidget { background:#1E1E1E; color:#CCC; border:none; font-size:13px; }
            QListWidget::item { padding:10px 14px; }
            QListWidget::item:selected { background:#094771; color:#FFF;
                                         border-left:3px solid #007ACC; }
        """)
        body.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:#252526;")
        body.addWidget(self.stack)

        for label, page in [
            ("🖊  Editor",      self._page_editor()),
            ("🎨  Appearance",  self._page_appearance()),
            ("🤖  AI",          self._page_ai()),
            ("▶  Run",          self._page_run()),
            ("📁  Files",       self._page_files()),
            ("⌨  Keybindings", self._page_keys()),
            ("ℹ  About",       self._page_about()),
        ]:
            self.sidebar.addItem(QListWidgetItem(label))
            self.stack.addWidget(page)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(12, 0, 12, 0)
        root.addLayout(btn_row)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet("background:#555; color:#CCC; padding:5px 12px;")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch()

        self.btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        self.btn_box.button(QDialogButtonBox.Apply).clicked.connect(self._apply)
        self.btn_box.accepted.connect(self._ok)
        self.btn_box.rejected.connect(self.reject)
        for b in self.btn_box.buttons():
            b.setStyleSheet(
                "QPushButton{background:#0E639C;color:white;border:none;"
                "padding:5px 16px;border-radius:3px;}"
                "QPushButton:hover{background:#1177BB;}")
        btn_row.addWidget(self.btn_box)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _scroll(self, w):
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setStyleSheet("QScrollArea{border:none;background:#252526;}")
        sa.setWidget(w)
        return sa

    def _group(self, title):
        g = QGroupBox(title)
        g.setStyleSheet("""
            QGroupBox{color:#CCC;border:1px solid #444;margin-top:10px;
                      border-radius:4px;font-weight:bold;}
            QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 4px;}
        """)
        f = QFormLayout(g)
        f.setLabelAlignment(Qt.AlignRight)
        f.setContentsMargins(12, 18, 12, 10)
        f.setSpacing(10)
        return g, f

    def _lbl(self, t):
        l = QLabel(t); l.setStyleSheet("color:#CCC;"); return l

    def _combo(self, items, current):
        c = QComboBox(); c.addItems(items)
        i = c.findText(str(current))
        if i >= 0: c.setCurrentIndex(i)
        c.setStyleSheet("background:#3C3C3C;color:#D4D4D4;padding:3px;"); return c

    def _check(self, label, checked):
        cb = QCheckBox(label); cb.setChecked(bool(checked))
        cb.setStyleSheet("color:#CCC;"); return cb

    def _spin(self, lo, hi, val, suffix=""):
        s = QSpinBox(); s.setRange(lo, hi); s.setValue(int(val))
        if suffix: s.setSuffix(suffix)
        s.setStyleSheet("background:#3C3C3C;color:#D4D4D4;padding:3px;"); return s

    def _le(self, text="", ph="", pw=False):
        le = QLineEdit(str(text)); le.setPlaceholderText(ph)
        if pw: le.setEchoMode(QLineEdit.Password)
        le.setStyleSheet(
            "background:#3C3C3C;color:#D4D4D4;padding:4px;border:1px solid #555;")
        return le

    # ── Pages ─────────────────────────────────────────────────────────────────

    def _page_editor(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16,16,16,16)

        g, f = self._group("Font")
        self.font_family = self._combo(
            ["Consolas","Courier New","Fira Code","JetBrains Mono",
             "Source Code Pro","Cascadia Code","Monaco","Inconsolata"],
            _settings.get("font_family"))
        self.font_size = self._spin(6, 32, _settings.get("font_size"), " pt")
        f.addRow(self._lbl("Family:"), self.font_family)
        f.addRow(self._lbl("Size:"),   self.font_size)
        v.addWidget(g)

        g2, f2 = self._group("Behaviour")
        self.tab_width   = self._spin(2, 8, _settings.get("tab_width"), " spaces")
        self.word_wrap   = self._check("Word wrap", _settings.get("word_wrap"))
        self.auto_indent = self._check("Auto-indent on Enter", _settings.get("auto_indent"))
        f2.addRow(self._lbl("Tab width:"), self.tab_width)
        f2.addRow("", self.word_wrap)
        f2.addRow("", self.auto_indent)
        v.addWidget(g2)

        g3, f3 = self._group("Display")
        self.show_lines = self._check("Show line numbers",      _settings.get("show_line_numbers"))
        self.hl_line    = self._check("Highlight current line", _settings.get("highlight_line"))
        f3.addRow("", self.show_lines)
        f3.addRow("", self.hl_line)
        v.addWidget(g3)

        v.addStretch(); return self._scroll(w)

    def _page_appearance(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16,16,16,16)

        g, f = self._group("Theme")
        self.theme_combo = self._combo(
            ["dark", "light", "high_contrast"], _settings.get("theme"))
        f.addRow(self._lbl("Theme:"), self.theme_combo)
        v.addWidget(g)

        g2, f2 = self._group("Accent Colour")
        row = QHBoxLayout()
        self.accent_preview = QLabel()
        self.accent_preview.setFixedSize(36, 24)
        self._refresh_accent()
        pick_btn = QPushButton("Choose…"); pick_btn.setFixedWidth(80)
        pick_btn.clicked.connect(self._pick_accent)
        row.addWidget(self.accent_preview); row.addWidget(pick_btn); row.addStretch()
        rw = QWidget(); rw.setLayout(row)
        f2.addRow(self._lbl("Accent:"), rw)
        v.addWidget(g2)

        note = QLabel("Theme changes apply when you click Apply or OK.")
        note.setStyleSheet("color:#888;font-style:italic;")
        v.addWidget(note); v.addStretch(); return self._scroll(w)

    def _refresh_accent(self):
        self.accent_preview.setStyleSheet(
            f"background:{self._accent_color};border:1px solid #888;border-radius:3px;")

    def _pick_accent(self):
        c = QColorDialog.getColor(QColor(self._accent_color), self, "Accent Colour")
        if c.isValid():
            self._accent_color = c.name()
            self._refresh_accent()

    def _page_ai(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16,16,16,16)

        g, f = self._group("Provider")
        provider_labels = [PROVIDERS[p]["label"] for p in PROVIDER_ORDER]
        current_provider = _settings.get("ai_provider", "anthropic")
        current_label = PROVIDERS.get(current_provider, PROVIDERS["anthropic"])["label"]
        self.provider_combo = self._combo(provider_labels, current_label)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        f.addRow(self._lbl("LLM Provider:"), self.provider_combo)

        self.provider_status_lbl = QLabel("")
        self.provider_status_lbl.setStyleSheet("color:#888; font-size:11px;")
        self.provider_status_lbl.setWordWrap(True)
        f.addRow("", self.provider_status_lbl)
        v.addWidget(g)

        g2, f2 = self._group("API Key")
        self.api_key_edit = self._le("", "", pw=True)
        eye = QPushButton("👁"); eye.setFixedWidth(32); eye.setCheckable(True)
        eye.setStyleSheet("background:#444;color:#CCC;border:none;padding:2px;")
        eye.toggled.connect(lambda on: self.api_key_edit.setEchoMode(
            QLineEdit.Normal if on else QLineEdit.Password))
        kr = QHBoxLayout(); kr.addWidget(self.api_key_edit); kr.addWidget(eye)
        kw = QWidget(); kw.setLayout(kr)
        self.api_key_note_lbl = QLabel("")
        self.api_key_note_lbl.setStyleSheet("color:#888;font-size:11px;")
        self.api_key_note_lbl.setWordWrap(True)
        f2.addRow(self._lbl("API Key:"), kw)
        f2.addRow("", self.api_key_note_lbl)
        v.addWidget(g2)

        g3, f3 = self._group("Model")
        self.model_edit = self._combo([], "")
        self.max_tokens = self._spin(256, 32768, _settings.get("ai_max_tokens", 2048), " tokens")
        f3.addRow(self._lbl("Model:"),      self.model_edit)
        f3.addRow(self._lbl("Max tokens:"), self.max_tokens)
        v.addWidget(g3)

        # Populate provider-specific fields for the initially selected provider
        self._refresh_provider_fields(current_provider)

        v.addStretch(); return self._scroll(w)

    def _on_provider_changed(self, index: int):
        if index < 0 or index >= len(PROVIDER_ORDER):
            return
        provider_key = PROVIDER_ORDER[index]
        self._refresh_provider_fields(provider_key)

    def _refresh_provider_fields(self, provider_key: str):
        """Swap the API key field, model list, and status note for the chosen provider."""
        info = PROVIDERS.get(provider_key, PROVIDERS["anthropic"])

        # API key field — load the key already saved for THIS provider
        saved_key = _settings.get(info["key_field"], "")
        self.api_key_edit.setText(saved_key)
        self.api_key_edit.setPlaceholderText(info["key_hint"])
        self.api_key_note_lbl.setText(
            f"Stored in ~/.pacer_settings.json under its own key per provider.\n"
            f"{info['env_var']} environment variable also works and takes priority.")

        # Model list — repopulate with this provider's models
        self.model_edit.clear()
        self.model_edit.addItems(info["models"])
        saved_model = _settings.get("ai_model", "")
        idx = self.model_edit.findText(saved_model)
        self.model_edit.setCurrentIndex(idx if idx >= 0 else 0)

        # Availability status note
        if info["available"]():
            self.provider_status_lbl.setText(f"✓ {info['label']} SDK is installed and ready.")
        else:
            self.provider_status_lbl.setText(
                f"⚠ {info['label']} SDK not installed. Run:  pip install {info['pip_name']}")

    def _selected_provider_key(self) -> str:
        idx = self.provider_combo.currentIndex()
        if 0 <= idx < len(PROVIDER_ORDER):
            return PROVIDER_ORDER[idx]
        return "anthropic"

    def _page_run(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16,16,16,16)

        g, f = self._group("Run Behaviour")
        self.auto_save_run = self._check(
            "Auto-save file before running",       _settings.get("auto_save_on_run"))
        self.clear_on_run  = self._check(
            "Clear output panel before each run",  _settings.get("clear_output_on_run"))
        f.addRow("", self.auto_save_run)
        f.addRow("", self.clear_on_run)
        v.addWidget(g); v.addStretch(); return self._scroll(w)

    def _page_files(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16,16,16,16)

        g, f = self._group("Default Save Location")
        dr = QHBoxLayout()
        self.default_dir_edit = self._le(
            _settings.get("default_save_dir",""), "Leave blank for last-used folder")
        bb = QPushButton("Browse…"); bb.setFixedWidth(80)
        bb.clicked.connect(lambda: (
            d := QFileDialog.getExistingDirectory(self, "Default Save Directory")) and
            self.default_dir_edit.setText(d))
        dr.addWidget(self.default_dir_edit); dr.addWidget(bb)
        dw = QWidget(); dw.setLayout(dr)
        f.addRow(self._lbl("Directory:"), dw)
        v.addWidget(g)

        g2, f2 = self._group("Auto-Backup")
        self.auto_backup     = self._check("Enable auto-backup", _settings.get("auto_backup"))
        self.backup_interval = self._spin(1, 60, _settings.get("backup_interval"), " min")
        br = QHBoxLayout()
        self.backup_dir_edit = self._le(_settings.get("backup_dir",""), "Backup folder path")
        bb2 = QPushButton("Browse…"); bb2.setFixedWidth(80)
        bb2.clicked.connect(lambda: (
            d := QFileDialog.getExistingDirectory(self, "Backup Directory")) and
            self.backup_dir_edit.setText(d))
        br.addWidget(self.backup_dir_edit); br.addWidget(bb2)
        bw = QWidget(); bw.setLayout(br)
        f2.addRow("",                            self.auto_backup)
        f2.addRow(self._lbl("Interval:"),        self.backup_interval)
        f2.addRow(self._lbl("Backup folder:"),   bw)
        v.addWidget(g2); v.addStretch(); return self._scroll(w)

    def _page_keys(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16,16,16,16)

        g, f = self._group("Keyboard Shortcuts")
        self._key_edits = {}
        for action, label in [
            ("new_ml",    "New mylang file"),
            ("new_other", "New file (choose type)"),
            ("open",      "Open file"),
            ("save",      "Save"),
            ("save_as",   "Save As"),
            ("run",       "Run file"),
            ("settings",  "Open Settings"),
        ]:
            le = self._le(_settings.key(action)); le.setFixedWidth(160)
            self._key_edits[action] = le
            f.addRow(self._lbl(label + ":"), le)

        note = QLabel("Standard Qt key names: Ctrl+S, F5, Ctrl+Shift+N …\n"
                       "Shortcut changes take effect after restarting Pacer.")
        note.setStyleSheet("color:#888;font-style:italic;")
        v.addWidget(g); v.addWidget(note); v.addStretch(); return self._scroll(w)

    def _page_about(self):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(24,24,24,24)

        for text, style in [
            ("Pacer + mylang",
             "color:#D4D4D4;font-size:22px;font-weight:bold;"),
            ("A production-ready code editor for the mylang language",
             "color:#888;font-size:12px;"),
            ("Version 0.5.1",
             "color:#569CD6;font-size:12px;"),
        ]:
            l = QLabel(text); l.setStyleSheet(style); v.addWidget(l)
        v.addSpacing(16)

        configured_providers = ", ".join(
            PROVIDERS[p]["label"] for p in PROVIDER_ORDER if _get_api_key(p)
        ) or "None configured"

        g, f = self._group("System Information")
        base = os.path.dirname(os.path.abspath(__file__))
        for label, value in [
            ("Python",          sys.version.split()[0]),
            ("Editor file",     os.path.abspath(__file__)),
            ("mylang folder",   os.path.join(base, "mylang")),
            ("Settings file",   SETTINGS_PATH),
            ("Backup dir",      _settings.get("backup_dir") or "(not set)"),
            ("Active provider", PROVIDERS.get(_settings.get("ai_provider","anthropic"),
                                 PROVIDERS["anthropic"])["label"]),
            ("Configured keys", configured_providers),
            ("mylang engine",   "Available ✓" if MYLANG_AVAILABLE else "NOT FOUND ✗"),
        ]:
            vl = QLabel(value)
            vl.setStyleSheet("color:#4EC9B0;font-family:Consolas;")
            vl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            f.addRow(self._lbl(label + ":"), vl)
        v.addWidget(g)

        ob = QPushButton("Open settings file in editor"); ob.setFixedWidth(230)
        ob.clicked.connect(lambda: self.parent() and
                           os.path.exists(SETTINGS_PATH) and
                           self.parent().load_file(SETTINGS_PATH))
        v.addWidget(ob); v.addStretch(); return self._scroll(w)

    # ── Collect / apply ───────────────────────────────────────────────────────

    def _collect(self):
        _settings.set("font_family",        self.font_family.currentText())
        _settings.set("font_size",          self.font_size.value())
        _settings.set("tab_width",          self.tab_width.value())
        _settings.set("word_wrap",          self.word_wrap.isChecked())
        _settings.set("auto_indent",        self.auto_indent.isChecked())
        _settings.set("show_line_numbers",  self.show_lines.isChecked())
        _settings.set("highlight_line",     self.hl_line.isChecked())
        _settings.set("theme",              self.theme_combo.currentText())
        _settings.set("accent_color",       self._accent_color)
        provider_key = self._selected_provider_key()
        _settings.set("ai_provider", provider_key)
        key = self.api_key_edit.text().strip()
        if key:
            _settings.set(PROVIDERS[provider_key]["key_field"], key)
        _settings.set("ai_model",           self.model_edit.currentText())
        _settings.set("ai_max_tokens",      self.max_tokens.value())
        _settings.set("auto_save_on_run",   self.auto_save_run.isChecked())
        _settings.set("clear_output_on_run",self.clear_on_run.isChecked())
        _settings.set("default_save_dir",   self.default_dir_edit.text().strip())
        _settings.set("auto_backup",        self.auto_backup.isChecked())
        _settings.set("backup_interval",    self.backup_interval.value())
        _settings.set("backup_dir",         self.backup_dir_edit.text().strip())
        for action, le in self._key_edits.items():
            _settings.set_key(action, le.text().strip())
        _settings.save()

    def _apply(self):
        self._collect(); self.applied.emit()

    def _ok(self):
        self._collect(); self.applied.emit(); self.accept()

    def _reset_defaults(self):
        if QMessageBox.question(self, "Reset Settings",
                "Reset ALL settings to defaults?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            _settings._data = dict(DEFAULTS)
            _settings._data["keys"] = dict(DEFAULTS["keys"])
            _settings.save()
            self.applied.emit()
            self.accept()
            QMessageBox.information(
                self.parent(), "Reset", "Defaults restored. Restart Pacer to apply all changes.")


# =============================================================================
# Mylang runner
# =============================================================================

class MylangRunner:
    def run(self, source: str) -> tuple:
        if not MYLANG_AVAILABLE:
            return "", "mylang not found — place the mylang/ folder next to Pacer_mylang.py"
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            tokens = Lexer(source).tokenize()
            ast    = Parser(tokens).parse()
            interp = Interpreter()
            interp.run(ast)
            return buf.getvalue(), ""
        except (LexerError, ParseError, MylangRuntimeError) as e:
            return "", str(e)
        except Exception:
            return "", f"Internal error:\n{traceback.format_exc()}"
        finally:
            sys.stdout = old


# =============================================================================
# AI worker thread
# =============================================================================

_clients: dict = {}   # provider_key → live SDK client instance, built lazily


def _get_api_key(provider_key: str) -> str:
    info = PROVIDERS.get(provider_key)
    if not info:
        return ""
    return os.environ.get(info["env_var"], "") or _settings.get(info["key_field"], "")


def _build_client(provider_key: str):
    """Lazily construct and cache an SDK client for the given provider."""
    info = PROVIDERS.get(provider_key)
    if not info or not info["available"]():
        return None
    key = _get_api_key(provider_key)
    if not key:
        return None

    if provider_key == "anthropic":
        return _anthropic.Anthropic(api_key=key)

    if provider_key == "openai":
        return _openai.OpenAI(api_key=key)

    if provider_key == "google":
        _google_genai.configure(api_key=key)
        return _google_genai   # module itself acts as the "client" for Gemini

    if provider_key in ("groq", "openrouter"):
        # Both are OpenAI-API-compatible — same SDK, different base_url
        return _openai.OpenAI(api_key=key, base_url=info["base_url"])

    return None


def _make_client(provider_key: str = None):
    """(Re)build the cached client for one provider, or all configured providers."""
    global _clients
    keys = [provider_key] if provider_key else list(PROVIDERS.keys())
    for pk in keys:
        client = _build_client(pk)
        if client is not None:
            _clients[pk] = client
        else:
            _clients.pop(pk, None)


def _any_provider_ready() -> bool:
    return len(_clients) > 0


_make_client()


class AIWorker(QThread):
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, prompt: str, model: str, max_tokens: int = 2048,
                 provider: str = None):
        super().__init__()
        self.prompt     = prompt
        self.model      = model
        self.max_tokens = max_tokens
        self.provider    = provider or _settings.get("ai_provider", "anthropic")

    def run(self):
        info = PROVIDERS.get(self.provider)
        if info is None:
            self.error.emit(f"Unknown provider '{self.provider}'.")
            return

        if not info["available"]():
            self.error.emit(
                f"{info['label']} SDK is not installed.\n"
                f"Run:  pip install {info['pip_name']}")
            return

        client = _clients.get(self.provider)
        if client is None:
            self.error.emit(
                f"No API key configured for {info['label']}.\n"
                f"Open Settings (Ctrl+,) → AI tab and select {info['label']} "
                f"to add its API key, or set {info['env_var']}.")
            return

        try:
            text = self._call_provider(client)
            if text:
                self.finished.emit(text)
            else:
                self.error.emit("Empty response from API")
        except Exception as e:
            self.error.emit(f"{info['label']} API error: {e}")

    def _call_provider(self, client) -> str:
        if self.provider == "anthropic":
            resp = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": self.prompt}]
            )
            for block in resp.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if self.provider in ("openai", "groq", "openrouter"):
            resp = client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": self.prompt}]
            )
            return resp.choices[0].message.content or ""

        if self.provider == "google":
            model = client.GenerativeModel(self.model)
            resp = model.generate_content(
                self.prompt,
                generation_config={"max_output_tokens": self.max_tokens}
            )
            return resp.text or ""

        return ""


# =============================================================================
# Line number gutter
# =============================================================================

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


# =============================================================================
# Syntax highlighter
# =============================================================================

class SyntaxHighlighter(QSyntaxHighlighter):
    BLUE   = QColor("#569CD6")
    ORANGE = QColor("#CE9178")
    GREEN  = QColor("#6A9955")
    YELLOW = QColor("#DCDCAA")
    PURPLE = QColor("#C586C0")
    TEAL   = QColor("#4EC9B0")
    NUMCOL = QColor("#B5CEA8")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.language = "text"
        self._build_rules("text")

    def set_language(self, lang: str):
        if lang != self.language:
            self.language = lang
            self._build_rules(lang)
            self.rehighlight()

    def _fmt(self, color, bold=False, italic=False):
        f = QTextCharFormat()
        f.setForeground(color)
        if bold:   f.setFontWeight(QFont.Bold)
        if italic: f.setFontItalic(True)
        return f

    def _build_rules(self, lang):
        self.rules = []
        kw  = self._fmt(self.BLUE, bold=True)
        cf  = self._fmt(self.PURPLE, bold=True)
        bi  = self._fmt(self.TEAL)
        fn  = self._fmt(self.YELLOW)
        sf  = self._fmt(self.ORANGE)
        com = self._fmt(self.GREEN, italic=True)
        num = self._fmt(self.NUMCOL)

        self.rules.append((r'\b[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)?\b', num))
        self.rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', sf))

        if lang == "mylang":
            for w in ["if","else","while","for","in","return"]:
                self.rules.append((r'\b'+w+r'\b', cf))
            for w in ["let","fn"]:
                self.rules.append((r'\b'+w+r'\b', kw))
            for w in ["print","len","type","str","num","push","pop",
                      "keys","values","has","del","range","sqrt","sin",
                      "cos","tan","log","exp","abs","round","floor","ceil",
                      "mean","stdev","median","complex","matrix"]:
                self.rules.append((r'\b'+w+r'\b', bi))
            for w in ["true","false","null","PI","E","TAU","PHI"]:
                self.rules.append((r'\b'+w+r'\b', self._fmt(self.BLUE)))
            self.rules.append((r'\bfn\s+([a-zA-Z_]\w*)\s*\(', fn))
            self.rules.append((r'\.([a-zA-Z_]\w*)\s*\(', fn))
            self.rules.append((r'//[^\n]*', com))

        elif lang == "python":
            for w in ["def","class","import","from","as","lambda","with",
                      "pass","raise","yield","async","await","global","nonlocal","assert"]:
                self.rules.append((r'\b'+w+r'\b', kw))
            for w in ["if","else","elif","for","while","try","except",
                      "finally","return","break","continue","in","not","and","or","del"]:
                self.rules.append((r'\b'+w+r'\b', cf))
            for w in ["print","len","range","type","str","int","float",
                      "list","dict","set","tuple","bool","enumerate","zip",
                      "map","filter","open","super","self"]:
                self.rules.append((r'\b'+w+r'\b', bi))
            for w in ["True","False","None"]:
                self.rules.append((r'\b'+w+r'\b', self._fmt(self.BLUE)))
            self.rules.append((r'\bdef\s+([a-zA-Z_]\w*)', fn))
            self.rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", sf))
            self.rules.append((r'#[^\n]*', com))

        elif lang in ("javascript", "react"):
            for w in ["function","class","import","export","default","extends",
                      "new","this","typeof","instanceof","void","yield","async","await"]:
                self.rules.append((r'\b'+w+r'\b', kw))
            for w in ["var","let","const"]:
                self.rules.append((r'\b'+w+r'\b', kw))
            for w in ["if","else","for","while","do","switch","case",
                      "break","continue","return","try","catch","finally","throw","in","of"]:
                self.rules.append((r'\b'+w+r'\b', cf))
            for w in ["console","Math","Array","Object","String",
                      "Number","Boolean","JSON","Promise","setTimeout","fetch"]:
                self.rules.append((r'\b'+w+r'\b', bi))
            for w in ["true","false","null","undefined","NaN","Infinity"]:
                self.rules.append((r'\b'+w+r'\b', self._fmt(self.BLUE)))
            self.rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", sf))
            self.rules.append((r'`[^`\\]*(\\.[^`\\]*)*`', sf))
            self.rules.append((r'//[^\n]*', com))

        elif lang == "html":
            tf = self._fmt(self.BLUE, bold=True)
            af = self._fmt(self.TEAL)
            self.rules += [
                (r'</?[a-zA-Z][a-zA-Z0-9]*', tf),
                (r'/?>', tf),
                (r'\b[a-zA-Z-]+=', af),
                (r'<!--.*?-->', com),
            ]

        elif lang == "xml":
            tf = self._fmt(self.BLUE, bold=True)
            self.rules += [
                (r'</?[a-zA-Z_][\w:.-]*', tf),
                (r'/?>', tf),
                (r'<!--.*?-->', com),
            ]

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for m in re.finditer(pattern, text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# =============================================================================
# Code editor widget
# =============================================================================

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.highlighter    = SyntaxHighlighter(self.document())
        self._apply_settings()

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def apply_settings(self):
        self._apply_settings()

    def _apply_settings(self):
        font = QFont(_settings.get("font_family","Consolas"),
                     _settings.get("font_size", 11))
        self.setFont(font)
        self.lineNumberArea.setFont(font)
        wrap = QPlainTextEdit.WidgetWidth if _settings.get("word_wrap") \
               else QPlainTextEdit.NoWrap
        self.setLineWrapMode(wrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                selection-background-color: #264F78;
                border: none;
            }
        """)

    def set_language(self, lang: str):
        self.highlighter.set_language(lang)

    # ── Gutter ────────────────────────────────────────────────────────────────

    def lineNumberAreaWidth(self):
        if not _settings.get("show_line_numbers", True):
            return 0
        digits = len(str(max(1, self.blockCount())))
        return 6 + self.fontMetrics().horizontalAdvance('9') * digits

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(
                0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        if not _settings.get("show_line_numbers", True):
            return
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#1E1E1E"))
        block   = self.firstVisibleBlock()
        bn      = block.blockNumber()
        top     = self.blockBoundingGeometry(block).translated(
                      self.contentOffset()).top()
        bottom  = top + self.blockBoundingRect(block).height()
        cur_bn  = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                color = QColor("#C6C6C6") if bn == cur_bn else QColor("#6E6E6E")
                painter.setPen(color)
                painter.drawText(
                    0, int(top),
                    self.lineNumberArea.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignRight, str(bn + 1))
            block  = block.next()
            top    = bottom
            bottom = top + self.blockBoundingRect(block).height()
            bn    += 1

    def highlightCurrentLine(self):
        if not _settings.get("highlight_line", True):
            self.setExtraSelections([])
            return
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(QColor("#2A2D2E"))
        sel.format.setProperty(QTextCharFormat.FullWidthSelection, True)
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        self.setExtraSelections([sel] if not self.isReadOnly() else [])

    # ── Key handling ──────────────────────────────────────────────────────────

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if _settings.get("auto_indent", True):
                cursor = self.textCursor()
                text   = cursor.block().text()
                indent = len(text) - len(text.lstrip())
                if text.rstrip().endswith("{"):
                    indent += _settings.get("tab_width", 4)
                super().keyPressEvent(event)
                self.insertPlainText(" " * indent)
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Tab:
            self.insertPlainText(" " * _settings.get("tab_width", 4))
        else:
            super().keyPressEvent(event)


# =============================================================================
# Main window
# =============================================================================

THEMES = {
    "dark": {
        "app":     "#252526", "editor":  "#1E1E1E", "text":    "#D4D4D4",
        "sidebar": "#252526", "tab_bg":  "#2D2D2D", "tab_sel": "#1E1E1E",
        "border":  "#3C3C3C", "input":   "#3C3C3C", "select":  "#094771",
    },
    "light": {
        "app":     "#F3F3F3", "editor":  "#FFFFFF", "text":    "#1E1E1E",
        "sidebar": "#EEEEEE", "tab_bg":  "#E0E0E0", "tab_sel": "#FFFFFF",
        "border":  "#CCCCCC", "input":   "#FFFFFF", "select":  "#ADD6FF",
    },
    "high_contrast": {
        "app":     "#000000", "editor":  "#000000", "text":    "#FFFFFF",
        "sidebar": "#000000", "tab_bg":  "#000000", "tab_sel": "#000000",
        "border":  "#FFFFFF", "input":   "#000000", "select":  "#0078D4",
    },
}


class MainWindow(QMainWindow):

    BUILTINS_HELP = (
        "Built-ins: len  type  str  num  push  pop  range  keys  values  has  del\n"
        "Math:      sqrt  cbrt  pow  abs  floor  ceil  round  sign  clamp\n"
        "           sin  cos  tan  asin  acos  atan  exp  log  log2  log10\n"
        "           factorial  gcd  lcm  comb  perm  random  rand_int  quadratic\n"
        "           PI  E  TAU  PHI\n"
        "Stats:     mean  median  mode  stdev  variance  min  max  sum\n"
        "           percentile  quartiles  correlation  linreg  zscore  normalize\n"
        "           normal_pdf  normal_cdf  histogram\n"
        "EE:        voltage  current  resistance  power  series  parallel\n"
        "           xc  xl  impedance_rc  impedance_rl  impedance_rlc\n"
        "           resonant_freq  q_factor  rc_tau  rl_tau  rc_charge  rc_discharge\n"
        "           to_db  vrms  vpeak  phasor  voltage_divider  thevenin\n"
        "           energy_cap  energy_ind  complex()  matrix()\n"
        "Crypto:    crypto.sha256(text)  crypto.hmac(msg,key)\n"
        "           crypto.pbkdf2(pwd,salt[,iter])  crypto.encrypt_aes(text,key)\n"
        "           crypto.decrypt_aes(hex,key)  crypto.secure_store(label,secret)\n"
        "           crypto.secure_retrieve(label)  crypto.secure_wipe(label)\n"
        "Image:     image.blank(w,h[,color])  image.rect(x,y,w,h[,color])\n"
        "           image.circle(cx,cy,r[,color])  image.line(x1,y1,x2,y2[,color,w])\n"
        "           image.text(msg,x,y[,size,color])  image.show([title])\n"
        "           image.load(url[,title])\n"
        "CSV:       csv.parse(string) → array-of-arrays\n"
        "           csv.stringify(array) → string\n"
        "Complex:   3+4j  z.real()  z.imag()  z.abs()  z.conj()  z.angle()\n"
        "           z1+z2  z1-z2  z1*z2  z1/z2  (native arithmetic)\n"
        "Namespaces: math.*  stats.*  ee.*  crypto.*  image.*  csv.*"
    )

    _untitled_counter = 0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pacer — mylang Editor")
        self.setGeometry(100, 100, 1400, 900)
        self._ai_workers    = []
        self.open_files     = {}
        self._unsaved_names = {}
        self.runner         = MylangRunner()

        self._reload_api_key()
        self._apply_theme()
        self.set_window_icon()

        # Central splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # File Explorer panel (header + tree)
        self.explorer_panel = QWidget()
        explorer_layout = QVBoxLayout(self.explorer_panel)
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_layout.setSpacing(0)

        # Header bar — shows current project folder name + navigation buttons
        self.explorer_header = QWidget()
        self.explorer_header.setObjectName("explorerHeader")
        header_layout = QHBoxLayout(self.explorer_header)
        header_layout.setContentsMargins(8, 4, 4, 4)
        header_layout.setSpacing(2)

        self.explorer_label = QLabel("EXPLORER")
        self.explorer_label.setStyleSheet(
            "font-weight:bold; font-size:11px; letter-spacing:1px;")
        header_layout.addWidget(self.explorer_label)
        header_layout.addStretch()

        up_btn = QPushButton("⬆")
        up_btn.setFixedSize(22, 22)
        up_btn.setToolTip("Go to parent folder")
        up_btn.setStyleSheet("padding:0; font-size:11px;")
        up_btn.clicked.connect(self._explorer_go_up)
        header_layout.addWidget(up_btn)

        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedSize(22, 22)
        refresh_btn.setToolTip("Refresh")
        refresh_btn.setStyleSheet("padding:0; font-size:11px;")
        refresh_btn.clicked.connect(self._explorer_refresh)
        header_layout.addWidget(refresh_btn)

        explorer_layout.addWidget(self.explorer_header)

        # Folder path label (shown under the header, truncated if long)
        self.explorer_path_lbl = QLabel("")
        self.explorer_path_lbl.setObjectName("explorerPathLabel")
        self.explorer_path_lbl.setStyleSheet(
            "font-size:10px; padding:0 8px 4px 8px;")
        self.explorer_path_lbl.setToolTip("")
        explorer_layout.addWidget(self.explorer_path_lbl)

        # File tree
        self.file_model = QFileSystemModel()
        self.file_model.setReadOnly(False)
        self.file_tree  = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setMaximumWidth(280)
        self.file_tree.setMinimumWidth(160)
        self.file_tree.clicked.connect(self.on_file_clicked)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self._explorer_context_menu)
        for col in range(1, 4):
            self.file_tree.hideColumn(col)
        explorer_layout.addWidget(self.file_tree)

        self.explorer_panel.setMaximumWidth(280)
        self.splitter.addWidget(self.explorer_panel)

        # NOTE: set_project_folder is called AFTER the status bar is created
        # (further down in __init__) to avoid AttributeError on self.status.

        # Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.splitter.addWidget(self.tab_widget)
        self.splitter.setSizes([200, 1000])

        self.create_output_panel()
        self.create_command_panel()
        self.create_visual_panel()

        # Hook image.show() and html.show(["panel"]) into the Visual Panel
        import stdlib as _stdlib
        _stdlib._IMAGE_SHOW_HOOK    = self._show_svg
        _stdlib._HTML_PANEL_HOOK    = self._show_html_panel
        _stdlib._HTML_FILE_DIR_HOOK = self._html_output_dir

        # Status bar — must be created BEFORE set_project_folder is called
        self.status = self.statusBar()
        self._cursor_lbl = QLabel("Ln 1, Col 1")
        self._cursor_lbl.setStyleSheet("padding-right:8px;")
        self._lang_lbl   = QLabel("lang: —")
        self.status.addPermanentWidget(self._cursor_lbl)
        self.status.addPermanentWidget(self._lang_lbl)
        self.status.showMessage(
            "Ready  |  F5=Run  Ctrl+,=Settings  /help for commands")

        # Open the last-used project folder now that self.status exists
        _start_dir = _settings.get("last_project_folder") or QDir.currentPath()
        if not os.path.isdir(_start_dir):
            _start_dir = QDir.currentPath()
        self.set_project_folder(_start_dir)

        self.create_menu()

        # Auto-backup timer
        self._backup_timer = QTimer(self)
        self._backup_timer.timeout.connect(self._do_backup)
        self._restart_backup_timer()

        # Startup warnings
        if not MYLANG_AVAILABLE:
            self.status.showMessage(
                "⚠  mylang/ folder not found — place it next to Pacer_mylang.py")
        elif not _any_provider_ready():
            self.status.showMessage(
                "⚠  No AI provider configured — open Settings (Ctrl+,) → AI tab to add a key")

    # ── Theme ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        name   = _settings.get("theme", "dark")
        t      = THEMES.get(name, THEMES["dark"])
        accent = _settings.get("accent_color", "#007ACC")
        self.setStyleSheet(f"""
            QMainWindow, QWidget          {{ background:{t['app']}; color:{t['text']}; }}
            QTreeView                     {{ background:{t['sidebar']}; color:{t['text']};
                                             border:none; }}
            QTreeView::item:selected      {{ background:{t['select']}; }}
            #explorerHeader                {{ background:{t['tab_bg']}; }}
            #explorerPathLabel              {{ color:#888; }}
            QTabWidget::pane              {{ border:1px solid {t['border']}; }}
            QTabBar::tab                  {{ background:{t['tab_bg']}; color:#AAA;
                                             padding:5px 14px; margin-right:2px; }}
            QTabBar::tab:selected         {{ background:{t['tab_sel']}; color:{t['text']};
                                             border-top:2px solid {accent}; }}
            QDockWidget                   {{ color:{t['text']}; }}
            QDockWidget::title            {{ background:{t['tab_bg']}; padding:4px; }}
            QPlainTextEdit, QTextEdit     {{ background:{t['editor']}; color:{t['text']}; }}
            QLineEdit                     {{ background:{t['input']}; color:{t['text']};
                                             border:1px solid {t['border']}; padding:3px; }}
            QPushButton                   {{ background:{accent}; color:white;
                                             border:none; padding:4px 12px;
                                             border-radius:3px; }}
            QPushButton:hover             {{ background:#1177BB; }}
            QStatusBar                    {{ background:{accent}; color:white; }}
            QLabel                        {{ color:{t['text']}; }}
            QMenuBar                      {{ background:{t['tab_bg']}; color:{t['text']}; }}
            QMenuBar::item:selected       {{ background:{t['select']}; }}
            QMenu                         {{ background:{t['app']}; color:{t['text']}; }}
            QMenu::item:selected          {{ background:{t['select']}; }}
            QComboBox                     {{ background:{t['input']}; color:{t['text']};
                                             border:1px solid {t['border']};
                                             padding:2px 6px; }}
            QScrollBar:vertical           {{ background:{t['app']}; width:10px; }}
            QScrollBar::handle:vertical   {{ background:{t['border']}; border-radius:4px; }}
        """)

    def _reload_api_key(self):
        _make_client()

    def _apply_settings_to_editors(self):
        """Push font/wrap/display changes to every open editor tab."""
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if isinstance(ed, CodeEditor):
                ed.apply_settings()

    def _on_settings_applied(self):
        self._apply_theme()
        self._reload_api_key()
        self._apply_settings_to_editors()
        self._restart_backup_timer()
        self._refresh_provider_status_btn()
        self.status.showMessage("Settings applied.")

    # ── Icon ──────────────────────────────────────────────────────────────────

    def set_window_icon(self):
        base = os.path.dirname(os.path.abspath(__file__))
        for name in ["pacer_logo.png","pacer_logo.ico",
                     "icon.png","icon.ico","icons/icon.png"]:
            p = os.path.join(base, name)
            if os.path.exists(p):
                self.setWindowIcon(QIcon(p))
                return

    # ── Menu ──────────────────────────────────────────────────────────────────

    def create_menu(self):
        mb = self.menuBar()

        # ── File ──────────────────────────────────────────────────────────────
        fm = mb.addMenu("File")
        for label, shortcut, slot in [
            ("New mylang File  (.ml)", _settings.key("new_ml"),    self.new_ml_file),
            ("New File (choose type)…",_settings.key("new_other"), self.new_other_file),
        ]:
            a = QAction(label, self)
            if shortcut: a.setShortcut(shortcut)
            a.triggered.connect(slot)
            fm.addAction(a)
        fm.addSeparator()
        for label, key, slot in [
            ("Open",         _settings.key("open"),        self.open_file),
            ("Open Folder…", _settings.key("open_folder"), self.open_folder),
            ("Save",         _settings.key("save"),        self.save_file),
            ("Save As",      _settings.key("save_as"),     self.save_file_as),
        ]:
            a = QAction(label, self)
            if key: a.setShortcut(key)
            a.triggered.connect(slot)
            fm.addAction(a)
        fm.addSeparator()
        ea = QAction("Exit", self); ea.triggered.connect(self.close); fm.addAction(ea)

        # ── Run ───────────────────────────────────────────────────────────────
        rm = mb.addMenu("Run")
        ra = QAction("Run File", self)
        ra.setShortcut(_settings.key("run") or "F5")
        ra.triggered.connect(self.run_current_file)
        rm.addAction(ra)
        rm.addSeparator()
        ca = QAction("Clear Output", self)
        ca.triggered.connect(lambda: self.output_area.clear())
        rm.addAction(ca)

        # ── View / Mode ───────────────────────────────────────────────────────
        vm = mb.addMenu("View")

        # Theme submenu
        tm = vm.addMenu("🎨  Theme")
        for theme_name, label in [
            ("dark",           "🌙  Dark  (default)"),
            ("light",          "☀  Light"),
            ("high_contrast",  "⚡  High Contrast"),
        ]:
            a = QAction(label, self)
            a.setCheckable(True)
            a.setChecked(_settings.get("theme") == theme_name)
            # Capture theme_name in closure
            a.triggered.connect(
                lambda checked, tn=theme_name: self._switch_theme(tn))
            tm.addAction(a)
        self._theme_actions = tm.actions()

        vm.addSeparator()

        # Mode submenu — editor layout presets
        mm = vm.addMenu("🖥  Mode")
        for mode_key, mode_label in [
            ("editor",    "📝  Editor Only"),
            ("split",     "⚡  Editor + Output"),
            ("canvas",    "🎨  Editor + Visual Panel"),
            ("fullscreen","🔲  Full Screen"),
        ]:
            a = QAction(mode_label, self)
            a.triggered.connect(
                lambda checked, mk=mode_key: self._switch_mode(mk))
            mm.addAction(a)

        vm.addSeparator()

        # Panel toggles
        for label, slot in [
            ("Toggle Output Panel",       self._toggle_output_panel),
            ("Toggle AI Assistant Panel", self._toggle_ai_panel),
            ("Toggle Visual Panel",       self._toggle_visual_panel),
            ("Toggle File Tree",          self._toggle_file_tree),
        ]:
            a = QAction(label, self); a.triggered.connect(slot); vm.addAction(a)

        vm.addSeparator()
        zoom_in  = QAction("Zoom In  (Ctrl++)", self)
        zoom_out = QAction("Zoom Out (Ctrl+-)", self)
        zoom_rst = QAction("Reset Zoom",        self)
        zoom_in.setShortcut("Ctrl+=")
        zoom_out.setShortcut("Ctrl+-")
        zoom_rst.setShortcut("Ctrl+0")
        zoom_in.triggered.connect(lambda: self._zoom(+1))
        zoom_out.triggered.connect(lambda: self._zoom(-1))
        zoom_rst.triggered.connect(lambda: self._zoom(0))
        for a in (zoom_in, zoom_out, zoom_rst):
            vm.addAction(a)

        # ── mylang ────────────────────────────────────────────────────────────
        ml = mb.addMenu("mylang")
        for label, slot in [
            ("Show Built-ins Reference", lambda: self._append_output(
                "── mylang built-ins ──\n" + self.BUILTINS_HELP, "#4EC9B0")),
            ("Open Documentation", self._open_docs),
        ]:
            a = QAction(label, self); a.triggered.connect(slot); ml.addAction(a)

        # ── Settings ──────────────────────────────────────────────────────────
        sm = mb.addMenu("Settings")
        sa = QAction("Preferences…", self)
        sa.setShortcut(_settings.key("settings") or "Ctrl+,")
        sa.triggered.connect(self.open_settings)
        sm.addAction(sa)

    # ── Panels ────────────────────────────────────────────────────────────────

    def create_output_panel(self):
        self._output_dock = QDockWidget("Output", self)
        self._output_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._output_dock)

        panel = QWidget(); layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Program Output:"))
        cb = QPushButton("Clear"); cb.setFixedWidth(60)
        cb.clicked.connect(lambda: self.output_area.clear())
        hdr.addStretch(); hdr.addWidget(cb)
        layout.addLayout(hdr)

        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        self.output_area.setMaximumHeight(180)
        layout.addWidget(self.output_area)
        self._output_dock.setWidget(panel)

    def create_command_panel(self):
        self._ai_dock = QDockWidget("AI Assistant & Commands", self)
        self._ai_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self._ai_dock)

        panel = QWidget(); layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)

        row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText(
            "/run  /debug  /fix  /complete  /explain  /mylang <q>  /help")
        self.cmd_input.returnPressed.connect(self.execute_command)

        self.provider_status_btn = QPushButton()
        self.provider_status_btn.setFixedWidth(230)
        self.provider_status_btn.setToolTip("Click to change AI provider or model")
        self.provider_status_btn.setStyleSheet(
            "text-align:left; padding:4px 8px; background:#3C3C3C; color:#D4D4D4;")
        self.provider_status_btn.clicked.connect(self.open_settings)
        self._refresh_provider_status_btn()

        run_btn = QPushButton("▶ Run"); run_btn.setFixedWidth(70)
        run_btn.clicked.connect(self.run_current_file)

        row.addWidget(self.cmd_input)
        row.addWidget(self.provider_status_btn)
        row.addWidget(run_btn)
        layout.addLayout(row)

        self.cmd_output = QTextEdit()
        self.cmd_output.setReadOnly(True)
        self.cmd_output.setFont(QFont("Consolas", 10))
        self.cmd_output.setMaximumHeight(200)
        layout.addWidget(self.cmd_output)
        self._ai_dock.setWidget(panel)

    def _refresh_provider_status_btn(self):
        """Update the command-bar button to show the active provider · model."""
        provider_key = _settings.get("ai_provider", "anthropic")
        info  = PROVIDERS.get(provider_key, PROVIDERS["anthropic"])
        model = _settings.get("ai_model", info["models"][0])
        ready = "●" if _clients.get(provider_key) else "○"
        self.provider_status_btn.setText(f"{ready} {info['label']} · {model}")

    def create_visual_panel(self):
        """SVG canvas panel — shown when image.show() is called from mylang."""
        self._visual_dock = QDockWidget("Visual Output", self)
        self._visual_dock.setAllowedAreas(
            Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self._visual_dock)

        panel = QWidget()
        vbox  = QVBoxLayout(panel)
        vbox.setContentsMargins(4, 4, 4, 4)

        hdr = QHBoxLayout()
        self._visual_title_lbl = QLabel("Canvas")
        self._visual_title_lbl.setStyleSheet("font-weight:bold; color:#4EC9B0;")
        clear_btn = QPushButton("Clear"); clear_btn.setFixedWidth(55)
        clear_btn.clicked.connect(self._clear_visual)
        hdr.addWidget(self._visual_title_lbl)
        hdr.addStretch()
        hdr.addWidget(clear_btn)
        vbox.addLayout(hdr)

        self._visual_view = QTextEdit()
        self._visual_view.setReadOnly(True)
        self._visual_view.setAcceptRichText(True)
        self._visual_view.setMinimumWidth(320)
        self._visual_view.setStyleSheet(
            "background:#1E1E1E; border:none;")
        vbox.addWidget(self._visual_view)

        self._visual_dock.setWidget(panel)
        self._visual_dock.hide()   # hidden until image.show() is called

    # ── View mode helpers ──────────────────────────────────────────────────────

    def _switch_theme(self, theme_name: str):
        _settings.set("theme", theme_name)
        _settings.save()
        self._apply_theme()
        # Update checkmarks in the theme submenu
        labels = {"dark": "🌙  Dark  (default)",
                  "light": "☀  Light",
                  "high_contrast": "⚡  High Contrast"}
        for a in getattr(self, "_theme_actions", []):
            a.setChecked(a.text() == labels.get(theme_name, ""))
        self.status.showMessage(f"Theme: {theme_name}")

    def _switch_mode(self, mode: str):
        """Layout presets for different working styles."""
        if mode == "editor":
            self._output_dock.hide()
            self._ai_dock.hide()
            self._visual_dock.hide()
            self.explorer_panel.show()
            self.status.showMessage("Mode: Editor Only")

        elif mode == "split":
            self._output_dock.show()
            self._ai_dock.show()
            self._visual_dock.hide()
            self.explorer_panel.show()
            self.status.showMessage("Mode: Editor + Output")

        elif mode == "canvas":
            self._output_dock.show()
            self._ai_dock.hide()
            self._visual_dock.show()
            self.explorer_panel.hide()
            self.status.showMessage("Mode: Editor + Visual Canvas")

        elif mode == "fullscreen":
            if self.isFullScreen():
                self.showNormal()
                self.status.showMessage("Fullscreen: off")
            else:
                self.showFullScreen()
                self.status.showMessage("Mode: Full Screen  (F11 or Esc to exit)")

    def _toggle_output_panel(self):
        self._output_dock.setVisible(not self._output_dock.isVisible())

    def _toggle_ai_panel(self):
        self._ai_dock.setVisible(not self._ai_dock.isVisible())

    def _toggle_visual_panel(self):
        self._visual_dock.setVisible(not self._visual_dock.isVisible())

    def _toggle_file_tree(self):
        self.explorer_panel.setVisible(not self.explorer_panel.isVisible())

    def _zoom(self, direction: int):
        """direction: +1 increase, -1 decrease, 0 reset."""
        current = _settings.get("font_size", 11)
        if direction == 0:
            new_size = 11
        else:
            new_size = max(6, min(32, current + direction))
        _settings.set("font_size", new_size)
        _settings.save()
        self._apply_settings_to_editors()
        self.status.showMessage(f"Font size: {new_size}pt")

    def _show_svg(self, title: str, svg_text: str):
        """Called by image.show() / image.load() to render SVG in the Visual Panel."""
        self._visual_title_lbl.setText(f"Canvas — {title}")
        self._visual_view.setHtml(
            f'<div style="background:#1e1e1e; padding:8px;">{svg_text}</div>')
        self._visual_dock.show()

    def _show_html_panel(self, title: str, html_document: str):
        """Called by html.show(["panel"]) to render a full mylang HTML page
        in the same Visual Panel used by image.show(). Qt's QTextEdit only
        supports a subset of CSS (no flexbox/grid), so layout is simplified
        compared to the file/browser output, but content and styling carry
        over fine for headings, tables, result boxes, and code blocks."""
        self._visual_title_lbl.setText(f"HTML — {title}")
        self._visual_view.setHtml(html_document)
        self._visual_dock.show()

    def _html_output_dir(self) -> str:
        """Where html.show(["file"]) saves generated pages. Prefers an
        'output/' folder next to the currently open file's project root,
        falling back to the system temp directory if no file is open."""
        root = getattr(self, "_project_root", None)
        if root and os.path.isdir(root):
            return os.path.join(root, "output")
        return tempfile.gettempdir()

    def _clear_visual(self):
        self._visual_view.clear()
        self._visual_title_lbl.setText("Canvas")

    # ── Settings dialog ───────────────────────────────────────────────────────

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.applied.connect(self._on_settings_applied)
        dlg.exec_()

    # ── File operations ───────────────────────────────────────────────────────

    def new_file(self, language="mylang"):
        MainWindow._untitled_counter += 1
        n   = MainWindow._untitled_counter
        ext = {"mylang":".ml","python":".py","javascript":".js",
               "react":".jsx","html":".html","xml":".xml"}.get(language, ".ml")
        name = f"Untitled-{n}{ext}"

        editor = CodeEditor()
        editor.set_language(language)
        if language == "mylang":
            editor.setPlainText(
                '// New mylang file\n'
                '// Press F5 or type /run to execute\n\n'
                'print("Hello, World!");\n')

        idx = self.tab_widget.addTab(editor, "● " + name)
        self.tab_widget.setCurrentIndex(idx)
        self.open_files[idx]     = None
        self._unsaved_names[idx] = name
        self._lang_lbl.setText(f"lang: {language}")

        editor.document().modificationChanged.connect(
            lambda mod, i=idx: self._on_mod_changed(i, mod))
        editor.cursorPositionChanged.connect(self._update_cursor_label)
        return idx

    def new_ml_file(self):
        self.new_file("mylang")

    def new_other_file(self):
        options = ["mylang (.ml)","Python (.py)","JavaScript (.js)",
                   "React (.jsx)","HTML (.html)","Plain text"]
        choice, ok = QInputDialog.getItem(
            self, "New File", "Choose file type:", options, 0, False)
        if ok:
            self.new_file({
                "mylang (.ml)":"mylang","Python (.py)":"python",
                "JavaScript (.js)":"javascript","React (.jsx)":"react",
                "HTML (.html)":"html","Plain text":"text"
            }.get(choice, "mylang"))

    def _on_mod_changed(self, idx, modified):
        name = self._unsaved_names.get(idx)
        if not name:
            p = self.open_files.get(idx)
            name = os.path.basename(p) if p else "Untitled.ml"
        cur = self.tab_widget.tabText(idx)
        if modified and not cur.startswith("●"):
            self.tab_widget.setTabText(idx, "● " + name)
        elif not modified and cur.startswith("●"):
            self.tab_widget.setTabText(idx, name)

    # ── Folder / Explorer navigation ──────────────────────────────────────────

    def open_folder(self):
        """File → Open Folder… — switch the Explorer panel to a new project root."""
        start = _settings.get("last_project_folder") or QDir.currentPath()
        folder = QFileDialog.getExistingDirectory(
            self, "Open Folder", start)
        if folder:
            self.set_project_folder(folder)

    def set_project_folder(self, folder_path: str):
        """Point the Explorer tree at folder_path and remember it for next launch."""
        folder_path = os.path.abspath(folder_path)
        if not os.path.isdir(folder_path):
            return
        self.file_model.setRootPath(folder_path)
        self.file_tree.setRootIndex(self.file_model.index(folder_path))
        self._project_root = folder_path

        # Header label shows just the folder name, uppercased, VS-Code style
        name = os.path.basename(folder_path.rstrip(os.sep)) or folder_path
        self.explorer_label.setText(name.upper())
        self.explorer_path_lbl.setText(self._shorten_path(folder_path))
        self.explorer_path_lbl.setToolTip(folder_path)

        _settings.set("last_project_folder", folder_path)
        _settings.save()
        if hasattr(self, "status"):
            self.status.showMessage(f"Project folder: {folder_path}")

    def _shorten_path(self, path: str, max_len: int = 38) -> str:
        if len(path) <= max_len:
            return path
        return "…" + path[-(max_len - 1):]

    def _explorer_go_up(self):
        """Navigate the Explorer root up one directory level."""
        current = getattr(self, "_project_root", QDir.currentPath())
        parent = os.path.dirname(current.rstrip(os.sep))
        if parent and os.path.isdir(parent) and parent != current:
            self.set_project_folder(parent)

    def _explorer_refresh(self):
        """Force the file system model to re-read the current folder."""
        current = getattr(self, "_project_root", QDir.currentPath())
        # Re-setting the root path forces QFileSystemModel to refresh
        self.file_model.setRootPath("")
        self.file_model.setRootPath(current)
        self.file_tree.setRootIndex(self.file_model.index(current))
        self.status.showMessage("Explorer refreshed.")

    def _explorer_context_menu(self, pos):
        """Right-click menu in the Explorer tree: open, reveal, new file/folder."""
        index = self.file_tree.indexAt(pos)
        menu_parent = self.file_tree

        from PyQt5.QtWidgets import QMenu
        menu = QMenu(menu_parent)

        if index.isValid():
            path = self.file_model.filePath(index)
            is_dir = os.path.isdir(path)

            if not is_dir:
                open_a = menu.addAction("Open")
                open_a.triggered.connect(lambda: self.load_file(path))
            else:
                set_root_a = menu.addAction("Set as Project Folder")
                set_root_a.triggered.connect(lambda: self.set_project_folder(path))

            menu.addSeparator()
            reveal_a = menu.addAction("Reveal in File Explorer")
            reveal_a.triggered.connect(lambda: self._reveal_in_os(path))

            rename_a = menu.addAction("Rename")
            rename_a.triggered.connect(lambda: self.file_tree.edit(index))

            delete_a = menu.addAction("Delete")
            delete_a.triggered.connect(lambda: self._delete_path(path))

            menu.addSeparator()

        new_file_a = menu.addAction("New mylang File Here…")
        new_file_a.triggered.connect(lambda: self._new_file_in_explorer(index))

        new_folder_a = menu.addAction("New Folder…")
        new_folder_a.triggered.connect(lambda: self._new_folder_in_explorer(index))

        menu.exec_(self.file_tree.viewport().mapToGlobal(pos))

    def _reveal_in_os(self, path: str):
        folder = path if os.path.isdir(path) else os.path.dirname(path)
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)
            elif sys.platform == "darwin":
                import subprocess; subprocess.Popen(["open", folder])
            else:
                import subprocess; subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            self._append_output(f"Could not open file manager: {e}", "#CE9178")

    def _delete_path(self, path: str):
        name = os.path.basename(path)
        reply = QMessageBox.question(
            self, "Delete",
            f"Delete '{name}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.status.showMessage(f"Deleted: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete:\n{e}")

    def _new_file_in_explorer(self, index):
        target_dir = self._dir_for_index(index)
        name, ok = QInputDialog.getText(
            self, "New File", "File name:", text="untitled.ml")
        if not ok or not name.strip():
            return
        if not os.path.splitext(name)[1]:
            name += ".ml"
        full_path = os.path.join(target_dir, name)
        if os.path.exists(full_path):
            QMessageBox.warning(self, "Exists", "A file with that name already exists.")
            return
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                if name.endswith(".ml"):
                    f.write('print("Hello, World!");\n')
            self.load_file(full_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create file:\n{e}")

    def _new_folder_in_explorer(self, index):
        target_dir = self._dir_for_index(index)
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if not ok or not name.strip():
            return
        full_path = os.path.join(target_dir, name)
        try:
            os.makedirs(full_path, exist_ok=False)
        except FileExistsError:
            QMessageBox.warning(self, "Exists", "A folder with that name already exists.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create folder:\n{e}")

    def _dir_for_index(self, index) -> str:
        if not index.isValid():
            return getattr(self, "_project_root", QDir.currentPath())
        path = self.file_model.filePath(index)
        return path if os.path.isdir(path) else os.path.dirname(path)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File",
            _settings.get("default_save_dir", ""),
            "mylang Files (*.ml);;Python (*.py);;JavaScript (*.js);;All Files (*)")
        if path: self.load_file(path)

    def load_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Bring to front if already open
            for idx, p in self.open_files.items():
                if p == file_path:
                    self.tab_widget.setCurrentIndex(idx); return

            editor = CodeEditor()
            editor.setPlainText(content)
            lang = self._lang_for_path(file_path)
            editor.set_language(lang)
            name    = os.path.basename(file_path)
            tab_idx = self.tab_widget.addTab(editor, name)
            self.tab_widget.setCurrentIndex(tab_idx)
            self.open_files[tab_idx]      = file_path
            self._unsaved_names[tab_idx]  = name
            self._lang_lbl.setText(f"lang: {lang}")
            self.status.showMessage(f"Opened: {file_path}")

            editor.document().modificationChanged.connect(
                lambda mod, i=tab_idx: self._on_mod_changed(i, mod))
            editor.cursorPositionChanged.connect(self._update_cursor_label)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def save_file(self):
        idx = self.tab_widget.currentIndex()
        if idx == -1: return
        path = self.open_files.get(idx)
        self.save_to_path(path) if path else self.save_file_as()

    def save_file_as(self):
        idx = self.tab_widget.currentIndex()
        if idx == -1: return
        existing = self.open_files.get(idx)
        intended = self._unsaved_names.get(idx, "Untitled.ml")
        default  = existing or os.path.join(
            _settings.get("default_save_dir") or QDir.currentPath(), intended)

        path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", default,
            "mylang Files (*.ml);;Python (*.py);;All Files (*)")
        if path:
            if not os.path.splitext(path)[1]:
                path += ".ml"
            self.save_to_path(path)
            name = os.path.basename(path)
            self.open_files[idx]     = path
            self._unsaved_names[idx] = name
            self.tab_widget.setTabText(idx, name)
            lang = self._lang_for_path(path)
            ed   = self.tab_widget.widget(idx)
            if isinstance(ed, CodeEditor):
                ed.set_language(lang)
                ed.document().setModified(False)
            self._lang_lbl.setText(f"lang: {lang}")

    def save_to_path(self, file_path):
        idx = self.tab_widget.currentIndex()
        if idx == -1: return
        ed = self.tab_widget.widget(idx)
        if not isinstance(ed, CodeEditor): return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(ed.toPlainText())
            ed.document().setModified(False)
            self.tab_widget.setTabText(idx, os.path.basename(file_path))
            self.status.showMessage(f"Saved: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save:\n{e}")

    def close_tab(self, index):
        ed = self.tab_widget.widget(index)
        if isinstance(ed, CodeEditor) and ed.document().isModified():
            name  = self.tab_widget.tabText(index).lstrip("● ")
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f"'{name}' has unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel: return
            if reply == QMessageBox.Save:   self.save_file()

        self.open_files     = {(i if i < index else i-1): p
                                for i, p in self.open_files.items() if i != index}
        self._unsaved_names = {(i if i < index else i-1): n
                                for i, n in self._unsaved_names.items() if i != index}
        self.tab_widget.removeTab(index)

    # ── Navigation ────────────────────────────────────────────────────────────

    def on_file_clicked(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.load_file(path)

    def _on_tab_changed(self, index):
        path = self.open_files.get(index)
        if path:
            self._lang_lbl.setText(f"lang: {self._lang_for_path(path)}")

    def _update_cursor_label(self):
        idx = self.tab_widget.currentIndex()
        ed  = self.tab_widget.widget(idx) if idx >= 0 else None
        if isinstance(ed, CodeEditor):
            cur = ed.textCursor()
            self._cursor_lbl.setText(
                f"Ln {cur.blockNumber()+1}, Col {cur.columnNumber()+1}")

    def _open_docs(self):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MYLANG_DOCS.md")
        if os.path.exists(p):
            self.load_file(p)
        else:
            self._append_output("MYLANG_DOCS.md not found next to Pacer_mylang.py", "#CE9178")

    # ── Language detection ────────────────────────────────────────────────────

    def _lang_for_path(self, path):
        ext = os.path.splitext(path)[1].lower()
        return {
            ".ml":"mylang", ".py":"python", ".js":"javascript",
            ".jsx":"react", ".tsx":"react", ".ts":"javascript",
            ".html":"html", ".htm":"html", ".xml":"xml",
        }.get(ext, "text")

    def _current_context(self):
        idx = self.tab_widget.currentIndex()
        if idx == -1: return {"code":"","language":"text","path":None}
        ed  = self.tab_widget.widget(idx)
        if not isinstance(ed, CodeEditor): return {"code":"","language":"text","path":None}
        path = self.open_files.get(idx)
        lang = self._lang_for_path(path) if path else ed.highlighter.language
        return {"code": ed.toPlainText(), "language": lang, "path": path}

    # ── Run ───────────────────────────────────────────────────────────────────

    def run_current_file(self):
        ctx = self._current_context()
        if ctx["language"] != "mylang":
            self._append_output(
                "⚠  /run only works for .ml files.\n"
                "   Save with a .ml extension first.", "#CE9178")
            return

        # Auto-save
        if _settings.get("auto_save_on_run") and ctx["path"]:
            self.save_file()

        # Clear output
        if _settings.get("clear_output_on_run"):
            self.output_area.clear()

        self._append_output("▶  Running…", "#6A9955", output=True)
        output, error = self.runner.run(ctx["code"])

        if error:
            self._append_output(f"✖  Error:\n{error}", "#F44747", output=True)
            self._append_output("Runtime error — see Output panel.", "#F44747")
        else:
            self._append_output(output or "(no output)", "#D4D4D4", output=True)
            self._append_output("✔  Finished.", "#6A9955")

        self.status.showMessage("Run complete")

    # ── Command bar ───────────────────────────────────────────────────────────

    def execute_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd: return
        self.cmd_input.clear()
        self._append_output(f"> {cmd}", "#569CD6")

        if   cmd == "/run":                self.run_current_file()
        elif cmd == "/help":               self._show_help()
        elif cmd.startswith("/debug"):     self._ai_command("debug")
        elif cmd.startswith("/complete"):  self._ai_command("complete")
        elif cmd.startswith("/fix"):       self._ai_command("fix")
        elif cmd.startswith("/explain"):   self._ai_command("explain")
        elif cmd.startswith("/mylang"):
            self._ai_mylang(cmd[len("/mylang"):].strip())
        elif cmd.startswith("/settings"):  self.open_settings()
        else:
            self._append_output(
                "Unknown command. Type /help for a list.", "#CE9178")

    def _show_help(self):
        self._append_output(
            "── Pacer Commands ─────────────────────────────\n"
            "  /run           Run the current .ml file\n"
            "  /debug         AI: find bugs\n"
            "  /fix           AI: repair errors (offers to apply)\n"
            "  /complete      AI: finish your code\n"
            "  /explain       AI: explain what the code does\n"
            "  /mylang <q>    Ask any mylang question\n"
            "  /settings      Open Settings dialog\n"
            "  /help          Show this message\n"
            "───────────────────────────────────────────────\n"
            "  F5             Run file\n"
            "  Ctrl+N         New .ml file\n"
            "  Ctrl+Shift+N   New file (choose type)\n"
            "  Ctrl+S         Save\n"
            "  Ctrl+,         Settings\n",
            "#4EC9B0")

    # ── AI commands ───────────────────────────────────────────────────────────

    def _ai_command(self, action):
        ctx  = self._current_context()
        lang = ctx["language"]
        code = ctx["code"]
        ctx_note = ""
        if lang == "mylang":
            ctx_note = (
                "\n\nThis is mylang — a custom language. Syntax:\n"
                "  let x = 5;   fn f(a,b){ return a+b; }   for(x in arr){}\n"
                "  [1,2,3]  {\"k\":v}  complex(3,4)  matrix([[1,2],[3,4]])\n"
                + self.BUILTINS_HELP)

        prompts = {
            "debug":    f"Debug this {lang} code. List each issue and fix:{ctx_note}\n```{lang}\n{code}\n```",
            "complete": f"Complete this {lang} code. Return ONLY the completion:{ctx_note}\n```{lang}\n{code}\n```",
            "fix":      f"Fix all errors in this {lang} code. Return ONLY corrected code:{ctx_note}\n```{lang}\n{code}\n```",
            "explain":  f"Explain step by step what this {lang} code does:{ctx_note}\n```{lang}\n{code}\n```",
        }

        self._append_output(f"⏳ Asking AI ({action})…", "#DCDCAA")
        provider = _settings.get("ai_provider", "anthropic")
        model    = _settings.get("ai_model", PROVIDERS[provider]["models"][0])
        tokens   = _settings.get("ai_max_tokens", 2048)
        worker = AIWorker(prompts[action], model, tokens, provider=provider)
        worker.finished.connect(lambda t: self._on_ai_done(action, t, ctx))
        worker.error.connect(lambda e: self._append_output(f"AI error: {e}", "#F44747"))
        worker.finished.connect(lambda _: self._safe_remove_worker(worker))
        worker.error.connect(lambda _: self._safe_remove_worker(worker))
        self._ai_workers.append(worker)
        worker.start()

    def _ai_mylang(self, question):
        if not question:
            self._append_output(
                "Usage: /mylang <question>  e.g. /mylang how do I use .map()?",
                "#CE9178")
            return
        prompt = (
            "You are an expert on the mylang custom language. Answer concisely.\n\n"
            "Syntax: let x=5; fn f(a){return a*2;} for(x in arr){} while(c){}\n"
            "if(c){} else{} [1,2,3] {\"k\":v} complex(3,4) matrix([[1,2]])\n"
            + self.BUILTINS_HELP + "\n\nQuestion: " + question)
        self._append_output("⏳ Asking AI about mylang…", "#DCDCAA")
        provider = _settings.get("ai_provider", "anthropic")
        model    = _settings.get("ai_model", PROVIDERS[provider]["models"][0])
        tokens   = _settings.get("ai_max_tokens", 2048)
        worker = AIWorker(prompt, model, tokens, provider=provider)
        worker.finished.connect(lambda t: self._append_output(t, "#D4D4D4"))
        worker.error.connect(lambda e: self._append_output(f"AI error: {e}", "#F44747"))
        worker.finished.connect(lambda _: self._safe_remove_worker(worker))
        worker.error.connect(lambda _: self._safe_remove_worker(worker))
        self._ai_workers.append(worker)
        worker.start()

    def _safe_remove_worker(self, worker):
        try: self._ai_workers.remove(worker)
        except ValueError: pass

    def _on_ai_done(self, action, text, ctx):
        if action in ("fix", "complete"):
            idx = self.tab_widget.currentIndex()
            if idx != -1:
                ed = self.tab_widget.widget(idx)
                if isinstance(ed, CodeEditor):
                    if QMessageBox.question(
                            self, f"AI {action}",
                            f"Apply AI {action} to the editor?",
                            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                        clean = re.sub(r'^```[a-zA-Z]*\n?', '', text, flags=re.MULTILINE)
                        clean = re.sub(r'```\s*$', '', clean, flags=re.MULTILINE).strip()
                        ed.setPlainText(
                            ctx["code"] + "\n" + clean if action == "complete" else clean)
                        self._append_output(f"✔  Applied AI {action}.", "#6A9955")
                        return
        self._append_output(text, "#D4D4D4")

    # ── Auto-backup ───────────────────────────────────────────────────────────

    def _restart_backup_timer(self):
        self._backup_timer.stop()
        if _settings.get("auto_backup"):
            mins = max(1, _settings.get("backup_interval", 5))
            self._backup_timer.start(mins * 60 * 1000)

    def _do_backup(self):
        bdir = _settings.get("backup_dir", "")
        if not bdir or not os.path.isdir(bdir):
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        for idx, path in self.open_files.items():
            if not path: continue
            ed = self.tab_widget.widget(idx)
            if not isinstance(ed, CodeEditor): continue
            fname = os.path.basename(path)
            dest  = os.path.join(bdir, f"{fname}.{ts}.bak")
            try:
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(ed.toPlainText())
            except Exception:
                pass

    # ── Output helper ─────────────────────────────────────────────────────────

    def _append_output(self, text, color="#D4D4D4", output=False):
        target  = self.output_area if output else self.cmd_output
        escaped = (text.replace("&","&amp;").replace("<","&lt;")
                       .replace(">","&gt;").replace("\n","<br>"))
        target.append(
            f'<span style="color:{color};font-family:Consolas,monospace">'
            f'{escaped}</span>')

    # ── Close event ───────────────────────────────────────────────────────────

    def closeEvent(self, event):
        # Check all tabs for unsaved changes
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if isinstance(ed, CodeEditor) and ed.document().isModified():
                name  = self.tab_widget.tabText(i).lstrip("● ")
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"'{name}' has unsaved changes. Save before quitting?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    event.ignore(); return
                if reply == QMessageBox.Save:
                    self.tab_widget.setCurrentIndex(i)
                    self.save_file()
        event.accept()


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # App-level icon (taskbar, Alt+Tab, dock)
    _base = os.path.dirname(os.path.abspath(__file__))
    for _logo in ["pacer_logo.png","pacer_logo.ico","icon.png","icon.ico"]:
        _p = os.path.join(_base, _logo)
        if os.path.exists(_p):
            app.setWindowIcon(QIcon(_p))
            break

    window = MainWindow()
    window.show()
    window.new_ml_file()

    sys.exit(app.exec_())
