import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from filter_dialogue import filter_srt
from selection import load_selection


CAPTIONS = """1
00:00:01,000 --> 00:00:02,000
Hello.

2
00:00:05,000 --> 00:00:06,000
Sung lyric.

3
00:00:07,000 --> 00:00:08,000
Goodbye.
"""

SELECTION = {
    "duration_seconds": 8,
    "segments": [
        {"start": 0, "end": 1, "kind": "title", "note": "Opening animation"},
        {"start": 1, "end": 4, "kind": "dialogue"},
        {"start": 4, "end": 6.5, "kind": "song", "note": "Music and lyrics"},
        {"start": 6.5, "end": 8, "kind": "dialogue"},
    ],
}


class SelectionTests(unittest.TestCase):
    def load(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "selection.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return load_selection(path, 8)

    def test_keeps_dialogue_and_excludes_song(self):
        selection = self.load(SELECTION)
        output, kept, total = filter_srt(CAPTIONS, selection)
        self.assertEqual((kept, total), (2, 3))
        self.assertIn("Hello.", output)
        self.assertIn("Goodbye.", output)
        self.assertNotIn("Sung lyric.", output)

    def test_rejects_unclassified_gap(self):
        data = json.loads(json.dumps(SELECTION))
        data["segments"][1]["start"] = 2
        with self.assertRaisesRegex(ValueError, "Gap or overlap"):
            self.load(data)


if __name__ == "__main__":
    unittest.main()
