---
name: video-to-screenplay
description: Reconstruct a supplied film, video clip, or audio file as a dialogue-focused screenplay with brief visual song montages, scene locations, Telugu/Tinglish dialogue, and optional source-video screenshots.
---

# Video to screenplay

Create an **unofficial dialogue-focused reconstruction of the supplied cut**, not a claim to have the original shooting script. Account for the entire source timeline. Write retained dialogue and brief, source-grounded visual montages for songs in chronological order. Do not transcribe song lyrics. Preserve spoken dialogue in its source language; when it is Telugu, put a Tinglish (Romanized Telugu) version immediately below each Telugu line, without translating its meaning. Put scene headings and brief connective action in the user's requested language, or English if unspecified. Keep subtitles, visual observations, and inferred context distinct.

## Setup

On a new laptop, run the matching installer once from the skill directory. It installs FFmpeg/ffprobe, Google Chrome, uv-managed Python 3.12, the Python packages, and the multilingual Whisper `small` model. It needs internet access, disk space for the model, and may request administrator access for system packages. Run it again safely if setup is interrupted.

- macOS 14+: `bash scripts/setup-macos.sh`
- Windows 10/11 x64 (PowerShell, with WinGet/App Installer): `powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1`

The installers finish by running `scripts/check_install.py --download-model` in the skill's `.venv`. Do not assume setup succeeded if that check fails. Windows uses `.venv\Scripts\python.exe`; macOS uses `.venv/bin/python`. The standard-library media and rendering scripts can run with the environment's Python on either platform.

## Workflow

1. **Ingest.** For a local video or audio file, verify it and run `scripts/prepare_video.py INPUT --output-dir WORKDIR`. An audio-only file produces audio and metadata without contact sheets. For a link, first use an accessible caption/transcript source; download footage only when authorized and needed. Inspect video contact sheets and replay unclear spans. Contact sheets are an index, not a substitute for checking action in motion. For audio-only input, never claim visual verification.
2. **Select dialogue and songs.** Review the full duration and create `selection.json` with contiguous source-time intervals classified as `dialogue`, `action`, `song`, `title`, `credits`, or `other`. Retain spoken exchanges and the minimum action needed to understand them. For each song, retain only a concise visual montage: location or location changes, visible performers/characters, and what they do. Omit lyrics and repetitive shot-by-shot description. Omit fight/chase passages without meaningful dialogue, title animation, end credits, and unrelated silent montage. If intelligible dialogue occurs inside an action or song passage, split at the spoken turn and retain that short interval. Do not classify solely from ASR or captions: lyrics and sound effects can produce false speech. Use visual and audio evidence when available; for audio-only input, do not invent song visuals or locations. See [selection rules](references/dialogue-selection.md). Run `scripts/filter_dialogue.py selection.json --captions SOURCE.srt --output-dir WORKDIR` when subtitles exist; it preserves source timestamps and writes a selection report.
3. **Transcribe.** Use the filtered source-language subtitles when available, but compare them with audio. Otherwise run `scripts/transcribe.py INPUT --selection selection.json --language CODE --output-dir WORKDIR` with the platform-specific `.venv` Python; it transcribes only selected intervals and preserves source timestamps. Its default `small` model is multilingual. For difficult dialogue, try `medium` only if the added time and model download are appropriate. Treat ASR as a draft and never invent missing lines.
4. **Map the retained scenes.** Create `scene-ledger.md` with source time spans, visible or audible locations, speakers, dialogue evidence, song montage beats, and uncertainty. Link each dialogue or song row to the corresponding `selection.json` interval. Keep a character roster with `seen as`, `heard as`, and `name evidence`. Match a voice to a face only where footage supports it. Confirm named characters from spoken address, on-screen text, credits, or reliable film metadata. Use role cues until a name is supported.
5. **Write.** Create a `.fountain` file from retained dialogue and song intervals in chronological order. Give each scene an `INT./EXT. LOCATION - DAY/NIGHT` heading; when the exact location or time is unclear, use a truthful broad heading such as `EXT. STREET - TIME UNKNOWN`. Add a new heading when a song montage changes location. Use brief present-tense filmable action for context, ALL-CAPS character cues, dialogue, sparing parentheticals, and meaningful transitions. For Telugu dialogue, put `Tinglish: ...` directly below the corresponding Telugu text in the same dialogue block. Romanize names and wording consistently; do not substitute an English translation. Describe song action and performers under `MONTAGE - SONG` without lyrics. Omit the other excluded segments. Mark unclear speech as `[inaudible]` and uncertain attribution in the ledger. Do not add unseen events or motivations. See [format and evidence rules](references/screenplay-and-evidence.md).
6. **Review and deliver.** Check that `selection.json` covers the whole source and that every dialogue and song interval appears in the screenplay or is explained in the ledger. Record excluded intervals and reasons in the selection ledger/report. If no dialogue remains, report that plainly; a video song can still have a visual montage. For a full film, work in ordered 15–30 minute batches and merge the same roster and scene ledger. Deliver `selection.json`, the ledger, editable `.fountain`, and a PDF. Render with `scripts/render_fountain.py SCRIPT.fountain OUTPUT.pdf`. If the source has video, render an illustrated PDF with `scripts/render_illustrated.py` below. For audio-only input, deliver text screenplay/PDF without invented screenshots or visuals. Inspect the title/first scene, dialogue-heavy pages, song pages, and last page; state which lines/names/locations remain uncertain.

## Illustrated screenplay

For a reference layout with screenshots to the left of the text, keep the `.fountain` source as the editable screenplay and create a separate illustrated PDF. Use this only when the source has video. Make a JSON array with one `{"start": seconds, "end": seconds, "kind": "dialogue"}` or `"kind": "song"` entry for every retained Fountain scene heading, in order, using the scene ledger and original source timestamps. Song scene spans must point to actual song intervals. Then run:

```bash
python3 scripts/render_illustrated.py SCRIPT.fountain VIDEO.mp4 ILLUSTRATED.pdf \
  --scene-times scene-times.json --selection selection.json --captions source-language.srt
```

The renderer pairs each screenplay beat with an actual frame from its scene, including song montage frames; it aligns spoken dialogue to source-language captions when supplied and saves an alignment JSON for review. Use `--work-dir` to retain sampled frames in the project work folder. Check dialogue match scores and visually inspect a range of pages; correct scene times or screenshot choices if an image shows the wrong person or moment. Do not imply the screenshots verify an uncertain dialogue line.

## Local tools

- `ffmpeg` and `ffprobe` are needed for media preparation.
- `scripts/prepare_video.py`, `scripts/filter_dialogue.py`, and `scripts/selection.py` use only the Python standard library plus FFmpeg for media preparation.
- `scripts/transcribe.py` needs `faster-whisper` and the multilingual model. The installers create the environment and prefetch the `small` model into `models/`. It writes timestamped `.txt` and `.srt` files. It does not identify speakers.
- `scripts/render_fountain.py` and `scripts/render_illustrated.py` need local Google Chrome for PDF output. `CHROME_PATH` can point to a custom Chrome executable. HTML output is retained if PDF printing fails. Preserve the Fountain source for edits.

If a tool or model is missing, use an available equivalent or install in an isolated environment when authorized. Keep original media and generated files separate. Do not publish or send the reconstruction elsewhere without the user's instruction.
