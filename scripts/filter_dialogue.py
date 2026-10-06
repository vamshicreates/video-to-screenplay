#!/usr/bin/env python3
"""Keep source subtitle cues that fall inside reviewed dialogue intervals."""

import argparse
import json
import re
from pathlib import Path

from selection import dialogue_segments, load_selection, selected_at


def seconds(clock: str) -> float:
    hours, minutes, seconds_part = clock.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds_part)


def filter_srt(source: str, selection: dict) -> tuple[str, int, int]:
    kept = []
    total = 0
    for block in re.split(r"\n\s*\n", source.strip()):
        lines = block.splitlines()
        timing = next((line for line in lines if " --> " in line), None)
        if timing is None:
            continue
        total += 1
        start, end = (seconds(piece.strip()) for piece in timing.split(" --> ", 1))
        if selected_at(selection, (start + end) / 2):
            spoken = lines[lines.index(timing) + 1:]
            kept.append(f"{len(kept) + 1}\n{timing}\n" + "\n".join(spoken))
    return ("\n\n".join(kept) + ("\n" if kept else ""), len(kept), total)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("selection", type=Path, help="Reviewed selection JSON")
    parser.add_argument("--captions", type=Path, help="Source-language SRT, if available")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    selection = load_selection(args.selection)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    retained = dialogue_segments(selection)
    report = {
        "duration_seconds": selection["duration_seconds"],
        "dialogue_seconds": round(sum(s["end"] - s["start"] for s in retained), 3),
        "dialogue_intervals": len(retained),
        "excluded_intervals": len(selection["segments"]) - len(retained),
        "excluded_segments": [
            segment for segment in selection["segments"] if segment["kind"] != "dialogue"
        ],
    }
    if args.captions:
        text, kept, total = filter_srt(
            args.captions.read_text(encoding="utf-8-sig"), selection)
        output = args.output_dir / "dialogue-only.srt"
        output.write_text(text, encoding="utf-8")
        report["caption_cues_kept"] = kept
        report["caption_cues_total"] = total
        print(output)
    report_path = args.output_dir / "selection-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
