# Screenplay format and evidence

## Source ledger

Use a table with `ID | In–out | Kind | Heading/location | Action or montage beat | Speakers | Dialogue source | Open questions | Reviewed`.

- A scene is a continuous dramatic unit; a cutaway does not always require a new scene. Preserve sequence order and use source timestamps even if exact scene boundaries are approximate.
- Subtitle text establishes possible words, not who said them or what happened visually. ASR may hallucinate on music or silence. Check lip movement, shot context, vocal continuity, and the scene's exchange before assigning a cue.
- Distinguish an actor's real name from a character's name. If reliable names conflict with the video, use the video's evidence and flag the conflict.
- Any dialogue that cannot be heard confidently remains `[inaudible]` or is summarized in an uncertainty note; it is not rewritten as a plausible quotation.
- An action line reports visible or audible events. Inferred intention can be included only when the video makes it unambiguous and is best expressed through observable behavior.

## Fountain conventions

```fountain
Title: Example Clip
Credit: Unofficial video reconstruction
Author: Prepared for the user

INT. FAMILY HOME - DAY

RAVI enters carrying a parcel. MEERA looks up from the table.

MEERA
Where did you find it?

RAVI
(showing the label)
Outside the gate.

EXT. FRONT GATE - DAY

The empty street stretches beyond the open gate.
```

For Telugu dialogue, pair each source line with a Romanized Tinglish line in the **same dialogue block**:

```fountain
INT. FAMILY HOME - DAY

MEERA
నువ్వు ఎక్కడికి వెళ్తున్నావు?
Tinglish: Nuvvu ekkadiki velthunnavu?
```

The Tinglish line follows the words and order of the Telugu, not an English translation. If part of the original line is inaudible, mark the same gap in both forms; do not guess a Romanization. Keep scene headings on their own lines and state the visible location whenever supported. Use a broad truthful heading when the location or time is unclear. Introduce a character in ALL CAPS in action only at first appearance. Use `(O.S.)` for speech from someone outside the scene and `(V.O.)` for narration or interior voice when that distinction is supported. Keep one character cue per spoken turn. Avoid constant `CUT TO:` transitions. Label any separately requested English translation as a translation.

For a video song, use one or more location headings and a compact visual montage. Identify visible characters or performers by supported character/role names, describe their observable actions and location changes, and omit lyrics. For example:

```fountain
EXT. HILL ROAD - DAY

MONTAGE - SONG: RAVI walks beside MEERA along the ridge. They stop at an overlook as dancers pass behind them.

EXT. VILLAGE SQUARE - DAY

The song continues. RAVI and MEERA join the crowd dancing around the fountain.
```

If the source is audio-only, do not invent visual montage beats or locations. Record the audible song span and that its visuals are unavailable.

## Completion check

Before calling the screenplay complete, confirm: the last ledger out-time reaches the end of the requested cut; each song has a source-grounded montage or an audio-only limitation note; dialogue turns are assigned or explicitly unresolved; Telugu lines have matching Tinglish; names and locations have evidence; action stays in present tense; formatting survives PDF rendering; and the result is described as a reconstruction of the supplied video.
