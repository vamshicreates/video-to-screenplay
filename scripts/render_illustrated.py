#!/usr/bin/env python3
"""Render a Fountain reconstruction with time-matched video stills beside its text."""

import argparse
import base64
import html
import json
import re
import subprocess
import tempfile
import time
from difflib import SequenceMatcher
from pathlib import Path

from render_fountain import is_cue, is_scene
from runtime import find_chrome
from selection import load_selection, selected_at


CSS = """
@page { size: Letter; margin: .52in .45in .55in .45in;
  @top-right { content: counter(page) "."; font: 11pt 'Courier New', monospace; }
}
@page :first { @top-right { content: none; } }
* { box-sizing: border-box; }
body { margin: 0; color: #171717;
  font: 11.5pt/1.2 'Courier New', 'Kohinoor Telugu', 'Telugu MN', 'Nirmala UI', 'Gautami', monospace; }
.title-page { text-align: center; break-after: page; padding-top: 2.7in; }
.title { font-weight: bold; margin-bottom: 1.4in; }
.credit { margin-bottom: .15in; }
.row { display: grid; grid-template-columns: 1.82in minmax(0, 1fr);
  gap: .18in; align-items: start; break-inside: avoid; margin: 0 0 .10in; }
.shot { margin: 0; }
.shot img { display: block; width: 1.82in; height: 1.025in;
  object-fit: contain; background: #111; border-radius: .07in; }
.shot figcaption { color: #666; font: 8pt 'Courier New', monospace;
  margin-top: 2pt; }
.text { min-width: 0; padding-top: .02in; }
.scene { font-weight: bold; padding-top: .12in; }
.action { white-space: pre-wrap; }
.cue { text-align: center; }
.dialogue { max-width: 3.55in; margin: .04in auto 0; white-space: pre-wrap; }
.parenthetical { max-width: 2.7in; margin: .04in auto 0; }
.transition { text-align: right; padding-top: .2in; }
"""


def seconds(clock: str) -> float:
    h, m, s = clock.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_srt(path: Path) -> list[dict]:
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        timing = next((line for line in lines if " --> " in line), None)
        if not timing:
            continue
        left, right = timing.split(" --> ", 1)
        cues.append({"start": seconds(left), "end": seconds(right),
                     "text": " ".join(lines[lines.index(timing) + 1:])})
    return cues


def parse_fountain(path: Path) -> tuple[dict, list[dict]]:
    raw = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").replace("\r\n", "\n").strip())
    metadata = {}
    if raw and all(":" in line for line in raw[0].splitlines()):
        for line in raw.pop(0).splitlines():
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
    blocks = []
    scene = -1
    for raw_block in raw:
        lines = [line.rstrip() for line in raw_block.splitlines() if line.strip()]
        if not lines:
            continue
        first = lines[0].lstrip(".").strip()
        if is_scene(first):
            scene += 1
            kind = "scene"
        elif len(lines) == 1 and (first.endswith("TO:") or first in {"FADE IN:", "FADE OUT."}):
            kind = "transition"
        elif len(lines) >= 2 and is_cue(first):
            kind = "dialogue"
        else:
            kind = "action"
        blocks.append({"index": len(blocks), "scene": max(scene, 0),
                       "kind": kind, "lines": lines})
    return metadata, blocks


def compact(s: str) -> str:
    return "".join(c.casefold() for c in s if c.isalnum())


def source_dialogue(lines: list[str]) -> str:
    """Match captions against original dialogue, not its Tinglish duplicate."""
    spoken = [line for line in lines[1:] if not (line.startswith("(") and line.endswith(")"))]
    telugu = [line for line in spoken if re.search(r"[\u0c00-\u0c7f]", line)]
    if telugu:
        return " ".join(telugu)
    return " ".join(line for line in spoken if not line.casefold().startswith("tinglish:"))


def scene_frame_time(time_seconds: float, span: dict, selection: dict) -> float:
    """Keep a frame inside the scene's dialogue or song selection interval."""
    scene_kind = span.get("kind", "dialogue")
    eligible = [part for part in selection["segments"] if part["kind"] == scene_kind
                and part["start"] < span["end"] and part["end"] > span["start"]]
    if not eligible:
        raise ValueError(f"Scene has no {scene_kind} interval")
    if any(part["start"] <= time_seconds < part["end"] for part in eligible):
        return time_seconds
    choices = [max(span["start"], part["start"]) for part in eligible]
    choices += [min(span["end"], part["end"]) - .01 for part in eligible]
    return min(choices, key=lambda value: abs(value - time_seconds))


def match_dialogues(blocks: list[dict], cues: list[dict], spans: list[dict]) -> None:
    """Find monotone caption matches within each scene; interpolate other beats."""
    for scene_id, span in enumerate(spans):
        scene_blocks = [b for b in blocks if b["scene"] == scene_id]
        dialogue = [b for b in scene_blocks if b["kind"] == "dialogue"]
        choices = [c for c in cues if span["start"] <= c["start"] < span["end"]]
        if dialogue and choices:
            texts = [compact(source_dialogue(b["lines"])) for b in dialogue]
            options = [compact(c["text"]) for c in choices]
            score = []
            for i, script_text in enumerate(texts):
                row = []
                expected = i / max(len(dialogue) - 1, 1)
                for j in range(len(choices)):
                    similarity = max(
                        SequenceMatcher(None, script_text, "".join(options[j:j + width]),
                                        autojunk=False).ratio()
                        for width in range(1, min(5, len(choices) - j) + 1)
                    )
                    position = j / max(len(choices) - 1, 1)
                    row.append(similarity - .12 * abs(position - expected))
                score.append(row)
            previous = score[0][:]
            parents = []
            for row in score[1:]:
                best_value, best_index = -1e9, 0
                best = []
                current = []
                for j, value in enumerate(row):
                    if previous[j] > best_value:
                        best_value, best_index = previous[j], j
                    current.append(value + best_value)
                    best.append(best_index)
                parents.append(best)
                previous = current
            j = max(range(len(previous)), key=previous.__getitem__)
            assignments = [j]
            for parent in reversed(parents):
                j = parent[j]
                assignments.append(j)
            assignments.reverse()
            for b, j, script_text in zip(dialogue, assignments, texts):
                b["time"] = choices[j]["start"]
                b["caption"] = choices[j]["text"]
                b["match"] = round(SequenceMatcher(
                    None, script_text, compact(choices[j]["text"]), autojunk=False).ratio(), 3)
        anchors = [(i, b["time"]) for i, b in enumerate(scene_blocks) if "time" in b]
        anchors = [(-1, span["start"])] + anchors + [(len(scene_blocks), span["end"])]
        for (left_i, left_t), (right_i, right_t) in zip(anchors, anchors[1:]):
            for i in range(left_i + 1, right_i):
                fraction = (i - left_i) / (right_i - left_i)
                scene_blocks[i]["time"] = left_t + fraction * (right_t - left_t)
        for b in scene_blocks:
            b["time"] = max(span["start"], min(span["end"] - .01, b["time"]))
            if b["kind"] == "scene":
                b["time"] = span["start"]


def extract_frames(video: Path, frames: Path, interval: float) -> None:
    frames.mkdir(parents=True, exist_ok=True)
    if list(frames.glob("frame-*.jpg")):
        return
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
        "-vf", f"fps=1/{interval},scale=480:-2", "-q:v", "4",
        str(frames / "frame-%05d.jpg"),
    ], check=True)


def still_for(t: float, frames: list[Path], interval: float) -> Path:
    index = min(max(round(t / interval), 0), len(frames) - 1)
    return frames[index]


def render(metadata: dict, blocks: list[dict], frames: list[Path], interval: float) -> str:
    parts = ["<!doctype html><html><head><meta charset='utf-8'><style>", CSS,
             "</style></head><body>"]
    if metadata:
        parts.append("<section class='title-page'>")
        parts.append(f"<div class='title'>{html.escape(metadata.get('title', 'SCREENPLAY'))}</div>")
        for key in ("credit", "author", "source"):
            if metadata.get(key):
                parts.append(f"<div class='credit'>{html.escape(metadata[key])}</div>")
        parts.append("</section>")
    cache = {}
    for b in blocks:
        if b["kind"] == "transition":
            parts.append(f"<div class='row'><div></div><div class='transition'>{html.escape(b['lines'][0])}</div></div>")
            continue
        still = still_for(b["time"], frames, interval)
        if still not in cache:
            cache[still] = base64.b64encode(still.read_bytes()).decode("ascii")
        stamp = f"{int(b['time'] // 60):02d}:{int(b['time'] % 60):02d}"
        shot = (f"<figure class='shot'><img alt='Video frame at {stamp}' "
                f"src='data:image/jpeg;base64,{cache[still]}'><figcaption>{stamp}</figcaption></figure>")
        lines = b["lines"]
        if b["kind"] == "scene":
            content = f"<div class='scene'>{html.escape(lines[0].lstrip('.'))}</div>"
        elif b["kind"] == "dialogue":
            rest = "".join(
                f"<div class='{'parenthetical' if x.startswith('(') and x.endswith(')') else 'dialogue'}'>{html.escape(x)}</div>"
                for x in lines[1:])
            content = f"<div class='cue'>{html.escape(lines[0])}</div>{rest}"
        else:
            content = f"<div class='action'>{html.escape(chr(10).join(lines))}</div>"
        parts.append(f"<div class='row'>{shot}<div class='text'>{content}</div></div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = find_chrome()
    if chrome is None:
        raise RuntimeError("Google Chrome is needed to print the illustrated PDF")
    pdf_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="illustrated-chrome-") as profile:
        process = subprocess.Popen([
            str(chrome), "--headless", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--no-pdf-header-footer",
            f"--user-data-dir={profile}", f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 90
            last_size, stable_since = 0, None
            while time.monotonic() < deadline:
                size = pdf_path.stat().st_size if pdf_path.exists() else 0
                if size and size == last_size:
                    stable_since = stable_since or time.monotonic()
                    if time.monotonic() - stable_since >= 1.5:
                        break
                else:
                    stable_since = None
                last_size = size
                if process.poll() is not None and not size:
                    raise RuntimeError(f"Chrome exited without a PDF (code {process.returncode})")
                time.sleep(.2)
            else:
                raise RuntimeError("Chrome PDF rendering timed out")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    if not pdf_path.is_file() or not pdf_path.stat().st_size:
        raise RuntimeError("Chrome did not create the PDF")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("fountain", type=Path)
    p.add_argument("video", type=Path)
    p.add_argument("output", type=Path, help="PDF output; matching HTML and alignment JSON are saved beside it")
    p.add_argument("--scene-times", type=Path, required=True,
                   help="JSON array of {start,end,kind} in Fountain scene order; kind is dialogue or song")
    p.add_argument("--captions", type=Path, help="Source-language SRT for dialogue alignment")
    p.add_argument("--selection", type=Path,
                   help="Reviewed selection; keep screenshots in each scene's dialogue or song interval")
    p.add_argument("--frame-interval", type=float, default=2)
    p.add_argument("--work-dir", type=Path, help="Cache sampled frames here")
    args = p.parse_args()
    if args.output.suffix.lower() != ".pdf" or args.frame_interval <= 0:
        p.error("Output must be a .pdf and frame interval must be positive")
    metadata, blocks = parse_fountain(args.fountain)
    spans = json.loads(args.scene_times.read_text(encoding="utf-8"))
    scene_count = sum(b["kind"] == "scene" for b in blocks)
    if len(spans) != scene_count:
        p.error(f"{len(spans)} scene spans supplied for {scene_count} Fountain scenes")
    if any(x["end"] <= x["start"] for x in spans):
        p.error("Every scene span needs end > start")
    if any(x.get("kind", "dialogue") not in {"dialogue", "song"} for x in spans):
        p.error("Scene kind must be dialogue or song")
    selection = load_selection(args.selection) if args.selection else None
    cues = parse_srt(args.captions) if args.captions else []
    if selection:
        cues = [cue for cue in cues if selected_at(selection, (cue["start"] + cue["end"]) / 2)]
    match_dialogues(blocks, cues, spans)
    if selection:
        for block in blocks:
            span = spans[block["scene"]]
            try:
                block["time"] = scene_frame_time(block["time"], span, selection)
            except ValueError as error:
                p.error(f"Fountain scene {block['scene'] + 1}: {error}")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work = args.work_dir or output.parent / (output.stem + "-frames")
    extract_frames(args.video, work, args.frame_interval)
    frames = sorted(work.glob("frame-*.jpg"))
    if not frames:
        raise RuntimeError("No video frames were extracted")
    html_path = output.with_suffix(".html")
    html_path.write_text(render(metadata, blocks, frames, args.frame_interval), encoding="utf-8")
    alignment = [{
        "block": b["index"], "scene": b["scene"] + 1, "kind": b["kind"],
        "time_seconds": round(b["time"], 2), "screenshot": str(still_for(b["time"], frames, args.frame_interval)),
        **({"caption_match": b["match"], "caption": b["caption"]} if "match" in b else {}),
    } for b in blocks if b["kind"] != "transition"]
    output.with_name(output.stem + "-alignment.json").write_text(
        json.dumps(alignment, ensure_ascii=False, indent=2), encoding="utf-8")
    print_pdf(html_path, output)
    print(html_path)
    print(output)


if __name__ == "__main__":
    main()
