#!/usr/bin/env python3
"""Create timestamped text and SRT using a local multilingual Whisper model."""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel
from selection import dialogue_segments, load_selection


def stamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--language", default="auto", help="Language code such as te, or auto")
    parser.add_argument("--model", default="small", help="Multilingual Whisper model")
    parser.add_argument("--selection", type=Path,
                        help="Reviewed selection JSON; transcribe dialogue intervals only")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"File not found: {args.input}")

    selected = None
    if args.selection:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json",
             str(args.input)], capture_output=True, text=True, check=True)
        duration = float(json.loads(probe.stdout)["format"]["duration"])
        selected = dialogue_segments(load_selection(args.selection, duration))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.output_dir / args.input.stem
    txt_path, srt_path = stem.with_suffix(".txt"), stem.with_suffix(".srt")
    if selected == []:
        txt_path.write_text("", encoding="utf-8")
        srt_path.write_text("", encoding="utf-8")
        print(f"No dialogue intervals selected.\n{txt_path}\n{srt_path}")
        return

    model_dir = Path(os.environ.get("WHISPER_MODEL_DIR", Path(__file__).resolve().parents[1] / "models"))
    model = WhisperModel(args.model, device="cpu", compute_type="int8", download_root=str(model_dir))
    languages = set()
    with txt_path.open("w", encoding="utf-8") as txt, srt_path.open("w", encoding="utf-8") as srt:
        number = 0
        ranges = selected if selected is not None else [{"start": 0, "end": None}]
        with tempfile.TemporaryDirectory(prefix="screenplay-dialogue-") as temp_dir:
            for interval in ranges:
                offset = interval["start"]
                source = args.input
                if selected is not None:
                    source = Path(temp_dir) / "dialogue.wav"
                    subprocess.run([
                        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-ss", f"{offset:.3f}", "-i", str(args.input),
                        "-t", f"{interval['end'] - offset:.3f}",
                        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(source),
                    ], check=True)
                segments, info = model.transcribe(
                    str(source), language=None if args.language == "auto" else args.language,
                    task="transcribe", vad_filter=True)
                languages.add(info.language)
                for segment in segments:
                    words = segment.text.strip()
                    if not words:
                        continue
                    start = offset + segment.start
                    end = offset + segment.end
                    if interval["end"] is not None:
                        end = min(end, interval["end"])
                    if end <= start:
                        continue
                    number += 1
                    txt.write(f"[{stamp(start)}] {words}\n")
                    srt.write(f"{number}\n{stamp(start)} --> {stamp(end)}\n{words}\n\n")
    print(f"Language: {', '.join(sorted(languages))}\n{txt_path}\n{srt_path}")


if __name__ == "__main__":
    main()
