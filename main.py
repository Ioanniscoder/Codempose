"""Refactored orchestrator for the parse → transform → engrave pipeline.

This module intentionally separates three concerns into explicit
functions so the dataflow is easy to reason about and test:

1. load_musical_input(path) -- read or import the user's study file and
   return a simple descriptor of the input.
2. parse_station(input_desc, part_name) -- produce the canonical
   score_data dictionary from the input descriptor.
3. engrave_station(score_data, out_basename) -- call the existing
   engraving driver.

The previous implementation mixed file loading, dynamic importing, and
parsing logic into a single helper. The refactor keeps the same
behaviour but exposes clear points of inspection and easier unit tests.
"""

from pathlib import Path
import argparse
import importlib.util
import re
import music21
import project_template as pt
from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part

OUTPUT_BASENAME = 'refactored_score'


def load_musical_input(path: Path):
    """Load a study file and return a descriptor dict with keys:
    - kind: 'lily' | 'tinynotation' | 'part'
    - value: the payload (string for lily/tinynotation, music21.Part for part)
    - source_name: a short name for the input (used as default title)

    This preserves the previous heuristics but keeps the logic separate
    from parsing/engraving responsibilities.
    """
    if not path.exists():
        raise FileNotFoundError(str(path))

    # Prefer .py modules which may export helpers or constants
    if path.suffix == '.py':
        try:
            spec = importlib.util.spec_from_file_location('study_module', str(path))
            mod = importlib.util.module_from_spec(spec)
            loader = spec.loader
            if loader is None:
                raise ImportError(f"Cannot load module from {path}")
            loader.exec_module(mod)
            # Prefer SOURCE_MELODY_LILY variable
            if hasattr(mod, 'SOURCE_MELODY_LILY'):
                return {'kind': 'lily', 'value': getattr(mod, 'SOURCE_MELODY_LILY'), 'source_name': path.stem}
            # If module provides a build_part() function, call it and return the part
            if hasattr(mod, 'build_part'):
                try:
                    part = mod.build_part()
                    return {'kind': 'part', 'value': part, 'source_name': path.stem}
                except Exception:
                    # fall through to other heuristics
                    pass
            # If module provides a get_tinynotation() helper
            if hasattr(mod, 'get_tinynotation'):
                try:
                    tn = mod.get_tinynotation()
                    return {'kind': 'tinynotation', 'value': tn, 'source_name': path.stem}
                except Exception:
                    pass
        except Exception:
            # Importing the module failed; fall back to reading file text and
            # using heuristics to decide how to interpret it.
            text = path.read_text(encoding='utf8')
            m = re.search(r"SOURCE_MELODY_LILY\s*=\s*r?([\"'])([\s\S]*?)\1", text)
            if m:
                return {'kind': 'lily', 'value': m.group(2), 'source_name': path.stem}
            if '\\' in text or '<' in text or '>' in text:
                return {'kind': 'lily', 'value': text, 'source_name': path.stem}
            return {'kind': 'tinynotation', 'value': text, 'source_name': path.stem}

    # Non-Python file: read text and heuristically decide
    text = path.read_text(encoding='utf8')
    if '\\' in text or '<' in text or '>' in text:
        return {'kind': 'lily', 'value': text, 'source_name': path.stem}
    return {'kind': 'tinynotation', 'value': text, 'source_name': path.stem}


def parse_station(input_desc, part_name='Main Melody'):
    """Convert an input descriptor (as returned by load_musical_input)
    into the canonical score_data dictionary used by the engraver.
    """
    kind = input_desc['kind']
    val = input_desc['value']
    source_name = input_desc.get('source_name', OUTPUT_BASENAME)

    if kind == 'part':
        # Already a music21.Part
        events = extract_data_from_part(val)
        return {'metadata': {'title': source_name}, 'parts': {part_name: events}}

    if kind == 'lily':
        lily_input = val
        print('Original LilyPond input:')
        print(lily_input)
        score_data = parse_lilypond_to_data(lily_input, part_name=part_name)
        # Preserve original input for auditing
        score_data.setdefault('metadata', {})
        score_data['metadata']['original_input'] = lily_input
        return score_data

    # tinynotation
    try:
        part = music21.converter.parse('tinynotation: ' + val)
        events = extract_data_from_part(part)
        return {'metadata': {'title': source_name}, 'parts': {part_name: events}}
    except Exception:
        # fallback: treat the text as Lily snippet
        score_data = parse_lilypond_to_data(val, part_name=part_name)
        score_data.setdefault('metadata', {})
        score_data['metadata']['original_input'] = val
        return score_data


def engrave_station(score_data, out_basename):
    """Delegate engraving to the existing project_template. This keeps the
    engraving implementation in one place and makes main.py a thin
    orchestrator.
    """
    print('\nParsed score_data metadata:')
    print(score_data.get('metadata', {}))
    pt.engrave_with_abjad(score_data, out_basename)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the engraving pipeline')
    parser.add_argument('--input', '-i', help='Path to a study file or snippet (py, txt). If omitted, a built-in snippet is used.')
    parser.add_argument('--output', '-o', default=None, help='Output basename (defaults to input file stem or refactored_score)')
    parser.add_argument('--force-verbatim', action='store_true', help='Always use the verbatim/manual .ly emission path')
    parser.add_argument('--force-hybrid', action='store_true', help='Always use the hybrid Abjad programmatic emission path')
    args = parser.parse_args(argv)

    # Station A: obtain an input descriptor
    if args.input:
        p = Path(args.input)
        try:
            input_desc = load_musical_input(p)
        except Exception as e:
            print(f'Failed to load input {p}: {e}')
            return
    else:
        # Default built-in snippet for quick runs
        lily_input = r"\relative c' { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 | b2. f'2. | e2. c2. | e2 b2 c2 }"
        input_desc = {'kind': 'lily', 'value': lily_input, 'source_name': OUTPUT_BASENAME}

    # Station B: parse into canonical score_data
    score_data = parse_station(input_desc, part_name='Main Melody')

    # Apply user overrides from CLI flags into metadata so the engraver
    # can honor them without changing its signature.
    if args.force_verbatim:
        score_data.setdefault('metadata', {})
        score_data['metadata']['force_verbatim'] = True
    if args.force_hybrid:
        score_data.setdefault('metadata', {})
        score_data['metadata']['force_hybrid'] = True

    # Determine output basename
    if args.output:
        out_basename = args.output
    elif args.input:
        # Use the input file stem directly as the output basename. Do not
        # invent or mangle names (previously we split on '_' which could
        # produce unexpected basenames like 'first' -> 'first' but also
        # truncated names for other files). This keeps output names
        # deterministic and tied to the input filename.
        out_basename = Path(args.input).stem
    else:
        out_basename = OUTPUT_BASENAME

    # Station D: engrave
    engrave_station(score_data, out_basename)


if __name__ == '__main__':
    main()
