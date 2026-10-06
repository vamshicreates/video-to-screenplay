import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from render_illustrated import scene_frame_time, source_dialogue


class SongScreenshotTests(unittest.TestCase):
    def setUp(self):
        self.selection = {"segments": [
            {"start": 0, "end": 10, "kind": "dialogue"},
            {"start": 10, "end": 30, "kind": "song"},
            {"start": 30, "end": 40, "kind": "dialogue"},
        ]}

    def test_song_scene_uses_song_frames(self):
        span = {"start": 10, "end": 30, "kind": "song"}
        self.assertEqual(scene_frame_time(20, span, self.selection), 20)
        self.assertGreaterEqual(scene_frame_time(9, span, self.selection), 10)
        self.assertLess(scene_frame_time(31, span, self.selection), 30)

    def test_dialogue_scene_does_not_use_song_frames(self):
        span = {"start": 0, "end": 10, "kind": "dialogue"}
        self.assertLess(scene_frame_time(15, span, self.selection), 10)

    def test_tinglish_not_used_for_caption_match(self):
        lines = ["MEERA", "నువ్వు ఎక్కడికి వెళ్తున్నావు?", "Tinglish: Nuvvu ekkadiki velthunnavu?"]
        self.assertEqual(source_dialogue(lines), lines[1])


if __name__ == "__main__":
    unittest.main()
