# Video to Screenplay

A Codex skill that reconstructs a supplied video as a scene-by-scene screenplay. It prepares contact sheets and audio, transcribes speech locally, guides scene and character verification, and renders editable Fountain to print-ready HTML and PDF. The output is an unofficial reconstruction of the supplied cut.

## Install for Codex

Clone this repository into `~/.codex/skills/video-to-screenplay`, or place a symlink there pointing to the repository. The skill is then available as `$video-to-screenplay` and can be selected automatically for video-to-screenplay requests.

For local transcription, install [uv](https://docs.astral.sh/uv/) and FFmpeg, then run from this directory:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

The multilingual Whisper `small` model downloads on first use into `models/`. Neither the environment nor model weights are tracked by Git.

## Use

Give Codex a local video or accessible link and ask for a screenplay. Codex follows [SKILL.md](SKILL.md), keeping a timestamped scene ledger and marking dialogue or identities it cannot verify.

The helpers can also be run directly:

```bash
python3 scripts/prepare_video.py /path/to/video.mp4 --output-dir /path/to/work
.venv/bin/python scripts/transcribe.py /path/to/work/audio-16k.wav --language te --output-dir /path/to/work
python3 scripts/render_fountain.py /path/to/script.fountain /path/to/script.pdf
```

PDF rendering uses local Google Chrome; HTML output is generated alongside the PDF. Telugu dialogue is supported in the PDF through browser font shaping. Transcription is a draft and requires review against the video, especially when voices overlap or music is present.
