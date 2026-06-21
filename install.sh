#!/usr/bin/env bash
# Pacer + mylang  v0.4.0  —  macOS / Linux installer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "============================================"
echo "  Pacer + mylang  v0.4.0  |  Unix Setup"
echo "============================================"
echo ""

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Install from https://python.org"
    exit 1
fi
PY=$(python3 --version)
echo "[OK] $PY found."

# ── Install Python packages ───────────────────────────────────────────────────
echo ""
echo "[1/3] Installing Python packages..."
python3 -m pip install --upgrade pip --quiet
python3 -m pip install PyQt5 anthropic --quiet
echo "[OK] Packages installed."

# ── Install mylang CLI ────────────────────────────────────────────────────────
echo ""
echo "[2/3] Installing mylang CLI..."
cd "$SCRIPT_DIR/mylang"
python3 -m pip install -e . --quiet
cd "$SCRIPT_DIR"
echo "[OK] 'mylang' command available."

# ── API key setup ─────────────────────────────────────────────────────────────
echo ""
echo "[3/3] API Key Setup"
echo ""
echo "To use AI features, set your Anthropic API key."
echo "You can also do this later via Settings (Ctrl+,) inside Pacer."
echo ""
read -rp "Enter your Anthropic API key (or press Enter to skip): " APIKEY

if [ -n "$APIKEY" ]; then
    # Detect shell and write to the correct rc file
    RCFILE=""
    if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "$(which zsh)" ]; then
        RCFILE="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        RCFILE="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        RCFILE="$HOME/.bash_profile"
    fi

    if [ -n "$RCFILE" ]; then
        # Remove any existing ANTHROPIC_API_KEY line, then append
        grep -v "ANTHROPIC_API_KEY" "$RCFILE" > /tmp/_pacer_rc && mv /tmp/_pacer_rc "$RCFILE" 2>/dev/null || true
        echo "export ANTHROPIC_API_KEY=\"$APIKEY\"" >> "$RCFILE"
        echo "[OK] API key added to $RCFILE"
        echo "     Run: source $RCFILE  (or restart your terminal)"
    else
        export ANTHROPIC_API_KEY="$APIKEY"
        echo "[OK] API key set for this session."
        echo "     Add to your shell profile manually:"
        echo "     export ANTHROPIC_API_KEY=\"$APIKEY\""
    fi
else
    echo "[SKIP] No key entered. Add it later via Pacer Settings."
fi

# ── Neovim bonus ──────────────────────────────────────────────────────────────
if command -v nvim &>/dev/null; then
    FTDETECT="$HOME/.config/nvim/ftdetect"
    mkdir -p "$FTDETECT"
    echo 'au BufRead,BufNewFile *.ml set filetype=javascript' > "$FTDETECT/mylang.vim"
    echo "[OK] Neovim .ml filetype detection added (uses JS highlighting)."
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  Setup complete!"
echo ""
echo "  Launch Pacer (no console window):"
echo "    pythonw Pacer_mylang.pyw     (Windows)"
echo "    python3 Pacer_mylang.pyw     (macOS/Linux)"
echo ""
echo "  Run a mylang file:"
echo "    mylang mylang/examples/hello.ml"
echo ""
echo "  Open the REPL:"
echo "    mylang --repl"
echo "============================================"
echo ""
