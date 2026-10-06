# Screenplay format and evidence

## Source ledger

Use a table with `ID | In–out | Heading | Action/beat | Speakers | Dialogue source | Open questions | Reviewed`.

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

Keep scene headings on their own lines. Introduce a character in ALL CAPS in action only at first appearance. Use `(O.S.)` for speech from someone outside the scene and `(V.O.)` for narration or interior voice when that distinction is supported. Keep one character cue per spoken turn. Avoid constant `CUT TO:` transitions. If the source contains dialogue in Telugu, retain Telugu script by default; translate or Romanize only at the user's request. Label a translated version separately from the source-language reconstruction.

## Completion check

Before calling the screenplay complete, confirm: the last ledger out-time reaches the end of the requested cut; all major visual beats appear; dialogue turns are assigned or explicitly unresolved; names have evidence; action stays in present tense; formatting survives PDF rendering; and the result is described as a reconstruction of the supplied video.
