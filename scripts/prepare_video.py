#!/usr/bin/env python3
"""Prepare audio and time-indexed contact sheets for video analysis."""

import argparse
import json
import math
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=10, help="Seconds between sampled frames")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"File not found: {args.input}")
    if args.interval <= 0:
        parser.error("--interval must be positive")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(args.input)],
        check=True, capture_output=True, text=True,
    )
    data = json.loads(probe.stdout)
    duration = float(data["format"]["duration"])
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    if video is None:
        parser.error("Input has no video stream")

    audio_path = output / "audio-16k.wav"
    if audio and not audio_path.exists():
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-i", str(args.input),
             "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(audio_path)])

    sheets = sorted(output.glob("contact-*.jpg"))
    if not sheets:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-i", str(args.input),
             "-vf", f"fps=1/{args.interval},scale=320:-2,tile=4x4",
             "-fps_mode", "vfr", str(output / "contact-%03d.jpg")])
        sheets = sorted(output.glob("contact-*.jpg"))

    frame_count = math.ceil(duration / args.interval)
    manifest = {
        "source": str(args.input.resolve()),
        "duration_seconds": duration,
        "video": {"width": video.get("width"), "height": video.get("height"), "codec": video.get("codec_name")},
        "audio": {"present": bool(audio), "codec": audio.get("codec_name") if audio else None,
                  "extracted": str(audio_path) if audio else None},
        "interval_seconds": args.interval,
        "contact_sheets": [
            {"file": str(sheet), "cells_row_major_seconds": [
                round(i * args.interval, 3)
                for i in range(index * 16, min((index + 1) * 16, frame_count))
            ]}
            for index, sheet in enumerate(sheets)
        ],
    }
    (output / "media-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(output / "media-manifest.json")


if __name__ == "__main__":
    main()
