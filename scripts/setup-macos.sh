#!/bin/bash
# Install the complete local runtime on macOS 14+.
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS. Use setup-windows.ps1 on Windows." >&2
  exit 1
fi
mac_major="$(sw_vers -productVersion | cut -d. -f1)"
if (( mac_major < 14 )); then
  echo "This setup supports macOS 14 or newer; the pinned PyAV wheel requires it on Apple Silicon." >&2
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Installing Homebrew (it may request administrator access and Command Line Tools)..."
  installer="$(mktemp)"
  trap 'rm -f "$installer"' EXIT
  curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o "$installer"
  /bin/bash "$installer"
fi
if [[ -x /opt/homebrew/bin/brew ]]; then
  brew_bin=/opt/homebrew/bin/brew
elif [[ -x /usr/local/bin/brew ]]; then
  brew_bin=/usr/local/bin/brew
else
  brew_bin="$(command -v brew || true)"
fi
if [[ -z "$brew_bin" ]]; then
  echo "Homebrew installation did not make brew available." >&2
  exit 1
fi
eval "$("$brew_bin" shellenv)"

if ! command -v uv >/dev/null 2>&1; then
  "$brew_bin" install uv
fi
if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  "$brew_bin" install ffmpeg
fi
if [[ ! -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]] &&
   [[ ! -x "$HOME/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]] &&
   ! command -v google-chrome >/dev/null 2>&1; then
  "$brew_bin" install --cask google-chrome
fi

cd "$skill_dir"
if [[ ! -x .venv/bin/python ]]; then
  uv venv --python 3.12 .venv
fi
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/check_install.py --download-model
echo "Video-to-screenplay is ready. Run .venv/bin/python scripts/check_install.py to check it again."
