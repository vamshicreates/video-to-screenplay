#!/usr/bin/env python3
"""Render a Fountain screenplay to print-ready HTML and, with Chrome, PDF."""

import argparse
import html
import re
import subprocess
import tempfile
import time
from pathlib import Path

from runtime import find_chrome


CSS = """
@page { size: Letter; margin: 1in 1in 1in 1.5in;
  @top-right { content: counter(page) "."; font: 12pt 'Courier New', monospace; }
}
@page :first { @top-right { content: none; } }
body { font: 12pt/1.15 'Courier New', 'Kohinoor Telugu', 'Telugu MN', 'Nirmala UI', 'Gautami', monospace; color:#111; }
.title-page { text-align:center; break-after:page; padding-top:2.7in; }
.title { font-weight:bold; margin-bottom:1.5in; }
.credit { margin-bottom:.15in; }
.scene { font-weight:bold; margin:18pt 0 12pt; break-after:avoid; }
.action { margin:0 0 12pt; white-space:pre-wrap; }
.dialogue-block { margin:0 0 12pt; break-inside:avoid; }
.cue { margin-left:2.2in; }
.dialogue { margin-left:1in; width:3.5in; white-space:pre-wrap; }
.parenthetical { margin-left:1.6in; width:2.7in; }
.transition { text-align:right; margin:12pt 0; }
"""


def is_scene(text: str) -> bool:
    return bool(re.match(r"^\.?\s*(INT\.|EXT\.|INT/EXT\.|INT\./EXT\.|I/E\.|EST\.)", text, re.I))


def is_cue(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and len(text) <= 48 and text == text.upper() and not is_scene(text)


def render(source: str) -> str:
    blocks = re.split(r"\n\s*\n", source.replace("\r\n", "\n").strip())
    metadata = {}
    if blocks and all(":" in line for line in blocks[0].splitlines()):
        for line in blocks.pop(0).splitlines():
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()

    parts = ["<!doctype html><html><head><meta charset='utf-8'><style>", CSS,
             "</style></head><body>"]
    if metadata:
        parts.append("<section class='title-page'>")
        parts.append(f"<div class='title'>{html.escape(metadata.get('title', 'SCREENPLAY'))}</div>")
        for key in ("credit", "author", "source"):
            if metadata.get(key):
                parts.append(f"<div class='credit'>{html.escape(metadata[key])}</div>")
        parts.append("</section>")

    for block in blocks:
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        first = lines[0].lstrip(".").strip()
        if is_scene(first):
            parts.append(f"<div class='scene'>{html.escape(first)}</div>")
        elif len(lines) == 1 and (first.endswith("TO:") or first == "FADE OUT."):
            parts.append(f"<div class='transition'>{html.escape(first)}</div>")
        elif len(lines) >= 2 and is_cue(first):
            parts.append("<div class='dialogue-block'>")
            parts.append(f"<div class='cue'>{html.escape(first)}</div>")
            for line in lines[1:]:
                class_name = "parenthetical" if line.startswith("(") and line.endswith(")") else "dialogue"
                parts.append(f"<div class='{class_name}'>{html.escape(line)}</div>")
            parts.append("</div>")
        else:
            parts.append(f"<div class='action'>{html.escape(chr(10).join(lines))}</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, help="Output .pdf or .html")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"File not found: {args.input}")
    if args.output.suffix.lower() not in {".pdf", ".html"}:
        parser.error("Output must end in .pdf or .html")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    html_path = args.output if args.output.suffix.lower() == ".html" else args.output.with_suffix(".html")
    html_path.write_text(render(args.input.read_text(encoding="utf-8")), encoding="utf-8")
    print(html_path)
    if args.output.suffix.lower() == ".html":
        return

    chrome = find_chrome()
    if chrome is None:
        parser.error("Google Chrome is needed for PDF output; print the generated HTML in a browser")
    with tempfile.TemporaryDirectory(prefix="screenplay-chrome-") as profile:
        process = subprocess.Popen(
            [str(chrome), "--headless", "--disable-gpu", "--no-first-run",
             "--no-default-browser-check", "--no-pdf-header-footer",
             f"--user-data-dir={profile}", f"--print-to-pdf={args.output.resolve()}",
             html_path.resolve().as_uri()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            deadline = time.monotonic() + 45
            last_size, stable_since = 0, None
            while time.monotonic() < deadline:
                size = args.output.stat().st_size if args.output.exists() else 0
                if size and size == last_size:
                    stable_since = stable_since or time.monotonic()
                    if time.monotonic() - stable_since >= 1:
                        break
                else:
                    stable_since = None
                last_size = size
                if process.poll() is not None and not size:
                    raise RuntimeError(f"Chrome exited without a PDF (code {process.returncode})")
                time.sleep(0.2)
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
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError("Chrome did not create a PDF")
    print(args.output)


if __name__ == "__main__":
    main()
