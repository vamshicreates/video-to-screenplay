# Dialogue selection

Classify the **source timeline**, not the subtitles alone. Write a `selection.json` beside the scene ledger:

```json
{
  "duration_seconds": 600.0,
  "segments": [
    {"start": 0, "end": 12.5, "kind": "title", "note": "Animated opening"},
    {"start": 12.5, "end": 95, "kind": "dialogue", "note": "Family conversation"},
    {"start": 95, "end": 140, "kind": "song", "note": "Sung performance"},
    {"start": 140, "end": 600, "kind": "dialogue", "note": "Remaining spoken scenes"}
  ]
}
```

The segments must be in source order, without unclassified gaps or overlapping intervals, and end at the media duration. Use seconds, including decimals where useful. `dialogue` supplies spoken lines; `song` supplies only a concise visual montage in the screenplay, never lyrics. `action` means action without an intelligible exchange; `title` and `credits` cover their on-screen sequences; `other` covers non-dialogue material such as silent establishing shots. If a character speaks during action or music, split out the spoken exchange as `dialogue`. A title or credit sequence is excluded even if it contains spoken promotion or announcements.

Use the video and audio to decide what each interval is. A speech recognizer can mistake singing for dialogue, and subtitles can contain lyrics. For audio-only input, identify speech versus music/effects by listening and mark any title/credit identification as audio-based or unknown. Keep original source times in captions and the scene ledger so a reviewer can locate both retained and omitted material.

After reviewing the selection, run `scripts/filter_dialogue.py selection.json --captions source.srt --output-dir work` when captions exist. The helper keeps cues whose midpoint falls within a dialogue interval and emits a coverage report; song lyrics remain excluded from transcription. When no captions exist, pass `--selection selection.json` to `scripts/transcribe.py` so only dialogue intervals are sent to Whisper. Review boundary cues manually; a spoken line crossing a cut may need to be restored or removed. Visually review every song interval separately to record its locations, visible performers/characters, and distinct montage actions. For audio-only input, describe only audible music or performance evidence and mark visual details unknown.
