"""Read and validate a complete, time-ordered dialogue selection."""

import json
import math
from pathlib import Path


KINDS = {"dialogue", "action", "song", "title", "credits", "other"}
TOLERANCE = 0.05


def load_selection(path: Path, media_duration: float | None = None) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        raise ValueError("Selection must be an object with a segments array")
    duration = data.get("duration_seconds")
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration_seconds must be a positive number")
    if media_duration is not None and abs(duration - media_duration) > 1:
        raise ValueError(f"Selection duration {duration} differs from media duration {media_duration}")
    segments = data["segments"]
    if not segments:
        raise ValueError("Selection has no segments")
    position = 0.0
    for index, segment in enumerate(segments, 1):
        if not isinstance(segment, dict) or segment.get("kind") not in KINDS:
            raise ValueError(f"Segment {index} needs a kind: {', '.join(sorted(KINDS))}")
        if segment["kind"] != "dialogue" and not str(segment.get("note", "")).strip():
            raise ValueError(f"Excluded segment {index} needs a note explaining the decision")
        start, end = segment.get("start"), segment.get("end")
        if any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in (start, end)):
            raise ValueError(f"Segment {index} needs numeric start and end")
        if start < 0 or end <= start or end > duration + TOLERANCE:
            raise ValueError(f"Segment {index} has invalid times")
        if abs(start - position) > TOLERANCE:
            raise ValueError(f"Gap or overlap before segment {index}: expected {position}, got {start}")
        position = end
    if abs(position - duration) > TOLERANCE:
        raise ValueError(f"Selection ends at {position}, media ends at {duration}")
    return data


def dialogue_segments(data: dict) -> list[dict]:
    return [segment for segment in data["segments"] if segment["kind"] == "dialogue"]


def selected_at(data: dict, time_seconds: float) -> bool:
    return any(s["start"] <= time_seconds < s["end"] for s in dialogue_segments(data))
