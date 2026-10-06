---
name: video-to-screenplay
description: Reconstruct a supplied video or accessible video link as a scene-by-scene screenplay with source-grounded action, attributed dialogue, and standard Fountain/PDF formatting. Use when asked to turn footage into a screenplay or script; not for writing a new story from a premise.
---

# Video to screenplay

Create an **unofficial reconstruction of the supplied cut**, not a claim to have the original shooting script. Cover the entire requested video in order. Preserve the spoken language unless the user requests translation or Romanization. Put scene headings and action in the user's requested language, or English if unspecified. Keep subtitles, visual observations, and inferred context distinct.

## Setup

On a new laptop, run the matching installer once from the skill directory. It installs FFmpeg/ffprobe, Google Chrome, uv-managed Python 3.12, the Python packages, and the multilingual Whisper `small` model. It needs internet access, disk space for the model, and may request administrator access for system packages. Run it again safely if setup is interrupted.

- macOS 14+: `bash scripts/setup-macos.sh`
- Windows 10/11 x64 (PowerShell, with WinGet/App Installer): `powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1`

The installers finish by running `scripts/check_install.py --download-model` in the skill's `.venv`. Do not assume setup succeeded if that check fails. Windows uses `.venv\Scripts\python.exe`; macOS uses `.venv/bin/python`. The standard-library media and rendering scripts can run with the environment's Python on either platform.

## Workflow

1. **Ingest.** For a local file, verify it and run `scripts/prepare_video.py INPUT --output-dir WORKDIR`. For a link, first use an accessible caption/transcript source if available; download footage only when authorized and needed for visual analysis. Inspect the generated metadata and contact sheets. For short cuts or unclear moments, seek to additional frames or replay the relevant span. Contact sheets are an index, not a substitute for checking action in motion.
2. **Transcribe.** Use source subtitles when available, but compare them with the audio. Otherwise run `scripts/transcribe.py INPUT --language CODE --output-dir WORKDIR` with the skill's platform-specific `.venv` Python. Its default `small` model is multilingual. For difficult dialogue, try `medium` only if the added time and model download are appropriate. Treat ASR output as a draft, especially for music, overlap, accents, and names. Never invent missing lines to make the exchange read smoothly.
3. **Map the film.** Create `scene-ledger.md` with one row per scene: stable scene ID, source time span, location/time, visible action, speakers, dialogue evidence, and uncertainty. Build a character roster with `seen as`, `heard as`, and `name evidence`. Match a voice to a face only where the footage supports it. Confirm named characters from on-screen text, spoken address, credits, or reliable film metadata when available. Use `UNIDENTIFIED MAN/WOMAN`, a role cue, or `VOICE (O.S.)` until a name is supported.
4. **Write.** Create a `.fountain` file in chronological order. Use `INT./EXT. LOCATION - DAY/NIGHT`, present-tense filmable action, ALL-CAPS character cues, dialogue, sparing parentheticals, and transitions only when meaningful. Describe what the video shows; mark unclear speech as `[inaudible]` and uncertain attribution in the ledger. Do not add plot events, unseen motivations, or camera directions as fact. See [format and evidence rules](references/screenplay-and-evidence.md).
5. **Review.** Recheck every scene boundary and each dialogue exchange against the source. Compare the ledger's time spans with the video duration so no stretch is silently omitted. Record unresolved issues and the coverage status. Do not call a partial reconstruction complete. For a long video, work in ordered batches and keep the same ledger and roster across batches.
6. **Deliver.** Provide the editable `.fountain`, `scene-ledger.md`, and a PDF when requested or useful. Render the standard PDF with `scripts/render_fountain.py SCRIPT.fountain OUTPUT.pdf`; the script also saves print-ready HTML and uses local Chrome for PDF, which preserves Telugu glyph shaping. When the user wants visual context beside the dialogue, render an additional illustrated PDF with `scripts/render_illustrated.py` as described below. Inspect at least the title/first scene, a dialogue-heavy page, and the last page. State which lines/names remain uncertain and whether the whole cut was reviewed.

## Illustrated screenplay

For a reference layout with screenshots to the left of the text, keep the `.fountain` source as the editable screenplay and create a separate illustrated PDF. Make a JSON array with one `{"start": seconds, "end": seconds}` entry for every Fountain scene heading, in order, using the scene ledger. Then run:

```bash
python3 scripts/render_illustrated.py SCRIPT.fountain VIDEO.mp4 ILLUSTRATED.pdf \
  --scene-times scene-times.json --captions source-language.srt
```

The renderer pairs each screenplay beat with an actual frame from its scene, aligns dialogue to source-language captions when supplied, and saves an alignment JSON for review. Use `--work-dir` to retain sampled frames in the project work folder. Check dialogue match scores and visually inspect a range of pages; correct scene times or screenshot choices if an image shows the wrong person or moment. Do not imply the screenshots verify an uncertain dialogue line.

## Local tools

- `ffmpeg` and `ffprobe` are needed for media preparation.
- `scripts/prepare_video.py` uses only the Python standard library plus FFmpeg.
- `scripts/transcribe.py` needs `faster-whisper` and the multilingual model. The installers create the environment and prefetch the `small` model into `models/`. It writes timestamped `.txt` and `.srt` files. It does not identify speakers.
- `scripts/render_fountain.py` and `scripts/render_illustrated.py` need local Google Chrome for PDF output. `CHROME_PATH` can point to a custom Chrome executable. HTML output is retained if PDF printing fails. Preserve the Fountain source for edits.

If a tool or model is missing, use an available equivalent or install in an isolated environment when authorized. Keep original media and generated files separate. Do not publish or send the reconstruction elsewhere without the user's instruction.
