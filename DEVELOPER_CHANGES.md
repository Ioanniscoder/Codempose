Changelog — recent development notes

2025-09-24
- Accept `\relative <pitch>` and `\relative <pitch>'` as valid study-file inputs.
  The template may append a single apostrophe to the `\relative` base when the base
  lacks explicit octave marks (this "base-nudge" makes the reference octave
  unambiguous for engraving).

- Emission change: when a part contains an original `\relative` snippet the
  template now emits a complete LilyPond `\score` that wraps the (possibly
  adjusted) snippet inside a `Staff` and includes `\layout` and `\midi` blocks.
  This preserves LilyPond's native relative-octave semantics and improves
  fidelity between user input and engraved PDF/MIDI.

Notes:
- The project still prints a small comparison comment block at the top of the
  generated `.ly` file (tinyNotation + lilyTokens) so the sequence is clearly
  readable for auditing purposes.

If you prefer this note appended into `DEVELOPMENT.md` instead, tell me and I
will merge it into that file (the file is currently wrapped in a fenced
block; I avoided modifying it directly to preserve formatting).