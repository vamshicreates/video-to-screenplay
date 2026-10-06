"""Locate external tools used by the screenplay renderers."""

import os
import shutil
from pathlib import Path


def find_chrome() -> Path | None:
    """Find Google Chrome on macOS or Windows, including non-PATH installs."""
    candidates = []
    override = os.environ.get("CHROME_PATH")
    if override:
        candidates.append(Path(override))
    for name in ("google-chrome", "google-chrome-stable", "chrome", "chrome.exe"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    if os.name == "nt":
        for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            root = os.environ.get(variable)
            if root:
                candidates.append(Path(root) / "Google" / "Chrome" / "Application" / "chrome.exe")
    else:
        candidates.extend((
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ))
    return next((path for path in candidates if path.is_file()), None)
