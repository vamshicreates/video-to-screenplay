#!/usr/bin/env python3
"""Create timestamped text and SRT using a local multilingual Whisper model."""

import argparse
import os
from pathlib import Path

from faster_whisper import WhisperModel


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
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"File not found: {args.input}")

    model_dir = Path(os.environ.get("WHISPER_MODEL_DIR", Path(__file__).resolve().parents[1] / "models"))
    model = WhisperModel(args.model, device="cpu", compute_type="int8", download_root=str(model_dir))
    segments, info = model.transcribe(str(args.input),
                                      language=None if args.language == "auto" else args.language,
                                      task="transcribe", vad_filter=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.output_dir / args.input.stem
    txt_path, srt_path = stem.with_suffix(".txt"), stem.with_suffix(".srt")
    with txt_path.open("w", encoding="utf-8") as txt, srt_path.open("w", encoding="utf-8") as srt:
        for number, segment in enumerate(segments, 1):
            words = segment.text.strip()
            txt.write(f"[{stamp(segment.start)}] {words}\n")
            srt.write(f"{number}\n{stamp(segment.start)} --> {stamp(segment.end)}\n{words}\n\n")
    print(f"Language: {info.language}\n{txt_path}\n{srt_path}")


if __name__ == "__main__":
    main()
