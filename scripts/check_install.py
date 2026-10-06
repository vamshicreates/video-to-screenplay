#!/usr/bin/env python3
"""Check the local video-to-screenplay runtime and optionally fetch the ASR model."""

import argparse
import shutil
import sys
from pathlib import Path

from runtime import find_chrome


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-model", action="store_true",
                        help="Download and load the multilingual small model (about 500 MB)")
    args = parser.parse_args()
    problems = []
    if sys.version_info < (3, 12):
        problems.append(f"Python 3.12+ required; found {sys.version.split()[0]}")
    else:
        print(f"Python: {sys.version.split()[0]}")
    for command in ("ffmpeg", "ffprobe"):
        found = shutil.which(command)
        if found:
            print(f"{command}: {found}")
        else:
            problems.append(f"{command} is missing from PATH")
    chrome = find_chrome()
    if chrome:
        print(f"Google Chrome: {chrome}")
    else:
        problems.append("Google Chrome was not found (set CHROME_PATH if installed elsewhere)")
    try:
        import av
        from faster_whisper import WhisperModel
    except ImportError as exc:
        problems.append(f"Python package missing: {exc}")
    else:
        print(f"PyAV: {av.__version__}")
        if args.download_model:
            model_dir = Path(__file__).resolve().parents[1] / "models"
            try:
                WhisperModel("small", device="cpu", compute_type="int8",
                             download_root=str(model_dir))
            except Exception as exc:
                problems.append(f"Whisper small model could not load or download: {exc}")
            else:
                print(f"Whisper small model: ready in {model_dir}")
        else:
            print("Whisper model: run with --download-model to fetch and verify it")
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if problems:
        return 1
    print("Runtime checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
