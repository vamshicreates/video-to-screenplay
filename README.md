# Video to Screenplay

A Codex skill that turns a film, short clip, or audio recording into a dialogue-focused screenplay. Video songs appear as concise visual montages without lyrics. Scene headings show supported locations, and Telugu dialogue includes a matching Tinglish line. The skill omits action-only passages, titles, credits, and other unrelated non-dialogue material. It prepares contact sheets when video is available, transcribes selected speech locally, and renders editable Fountain to a standard or screenshot-illustrated PDF. The output is an unofficial reconstruction of the supplied cut.

## Supported systems

- macOS 14 or newer, Intel or Apple Silicon.
- Windows 10/11, 64-bit x86, with [Windows Package Manager (WinGet)](https://learn.microsoft.com/windows/package-manager/winget/) available.

The macOS installer uses [Homebrew](https://brew.sh/) (and installs it if missing). The Windows installer uses WinGet. Both install FFmpeg, Google Chrome, [uv](https://docs.astral.sh/uv/getting-started/installation/), an isolated Python 3.12 environment, the pinned Python packages, and the multilingual Whisper `small` model. System installs may prompt for administrator approval. The model is roughly 500 MB, and internet access is needed during setup. No API key or paid speech service is required.

## Install for Codex

Place this repository at the global skill path, then run its setup script. If the skill was installed through Codex, start at the `cd` command.

**macOS (Terminal)**

```bash
git clone https://github.com/vamshicreates/video-to-screenplay.git ~/.codex/skills/video-to-screenplay
cd ~/.codex/skills/video-to-screenplay
bash scripts/setup-macos.sh
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/vamshicreates/video-to-screenplay.git "$HOME\.codex\skills\video-to-screenplay"
cd "$HOME\.codex\skills\video-to-screenplay"
powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1
```

The setup scripts are safe to rerun. They finish by checking all commands and Python packages and by loading the speech model. To recheck later:

```bash
# macOS
.venv/bin/python scripts/check_install.py --download-model
```

```powershell
# Windows
.venv\Scripts\python.exe scripts\check_install.py --download-model
```

If Chrome is installed in a custom location, set `CHROME_PATH` to its executable before rendering. The virtual environment and model weights stay on the laptop and are not tracked by Git.

## Use

Give Codex a local video, audio file, or accessible link and ask for a screenplay. Codex follows [SKILL.md](SKILL.md): it reviews the entire source, records dialogue, song, and excluded time ranges in `selection.json`, and keeps a timestamped scene ledger. Songs receive brief visual montage descriptions with locations and visible actions, but no lyrics. Telugu dialogue is followed by Tinglish transliteration. Dialogue briefly embedded in action or music can be retained as its own interval. For audio-only input, the standard text PDF is produced without invented visuals or screenshots.

On macOS, the helpers can also be run directly:

```bash
.venv/bin/python scripts/prepare_video.py /path/to/video.mp4 --output-dir /path/to/work
.venv/bin/python scripts/filter_dialogue.py /path/to/selection.json --captions /path/to/source.srt --output-dir /path/to/work
.venv/bin/python scripts/transcribe.py /path/to/video.mp4 --selection /path/to/selection.json --language te --output-dir /path/to/work
.venv/bin/python scripts/render_fountain.py /path/to/script.fountain /path/to/script.pdf
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe` and use Windows file paths. For a screenshot-illustrated PDF, provide retained scene time spans as described in [SKILL.md](SKILL.md). PDF rendering uses local Chrome; HTML is generated alongside the PDF. Transcription and segment classification require review, especially where speech overlaps music or action.
