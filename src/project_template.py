# project_template.py

import music21
import abjad
from pathlib import Path
import subprocess
import re
from fractions import Fraction
from lily_converter import _add_articulations_and_dynamics

# ============================================================================
# ABSOLUTE PATHS - Ensures outputs always go to correct location
# ============================================================================
# These paths are absolute and based on this module's location, so they work
# regardless of where Python is invoked from (root, studies/, or elsewhere)
# Also works whether this module is in root or src/ directory

if Path(__file__).parent.name == 'src':
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()  # src/ -> root
else:
    PROJECT_ROOT = Path(__file__).parent.resolve()  # already in root

OUTPUTS_DIR = PROJECT_ROOT / 'outputs'

def ql_to_lily_duration_string(ql: float) -> str:
    # Try the exact representation first (fraction of whole note)
    frac = Fraction(ql).limit_denominator(1024)
    try:
        dur = abjad.Duration(Fraction(frac, 4))
        return dur.lilypond_duration_string()  # FIX: Added () to actually call the method
    except Exception:
        # Fall back: approximate with power-of-two base durations and dots
        candidates = []
        # LilyPond duration numbers (1,2,4,8,16...) correspond to whole-note denominators
        bases = [1, 2, 4, 8, 16, 32, 64]
        for base in bases:
            for dots in range(0, 4):
                factor = 2 - 1 / (2 ** dots) if dots > 0 else 1
                ql_candidate = 4 / base * factor
                diff = abs(ql_candidate - float(ql))
                candidates.append((diff, base, dots, ql_candidate))
        candidates.sort(key=lambda x: x[0])
        best = candidates[0]
        diff, base, dots, ql_candidate = best
        # Build lilypond duration string (e.g. 4., 8..)
        dur_str = str(base) + ('.' * dots)
        if diff > 1e-2:
            print(f"[warning] approximate duration: requested ql={ql} approximated as {ql_candidate} (LilyPond: {dur_str}); diff={diff}")
        return dur_str

def _add_articulations_and_dynamics(token: str, event: dict) -> str:
    """
    Add articulations and dynamics to a LilyPond token.
    Helper for events_to_lilypond conversion.
    """
    from lily_converter import _add_articulations_and_dynamics as lily_add
    return lily_add(token, event)

def _events_to_absolute_lilypond(events: list, metadata: dict) -> str:
    """
    Convert event dictionaries to absolute LilyPond notation string.
    Returns clean music tokens (no \\relative wrapper, no directives).
    
    This is the core conversion logic extracted for reuse in both:
    1. engrave_with_abjad() - for .ly file generation
    2. build_score_from_blueprint() - for Station 2 editable snippets
    
    Args:
        events: List of event dictionaries (notes, rests, chords, barlines, etc.)
        metadata: Score metadata containing time_signature, key_signature, etc.
    
    Returns:
        str: LilyPond token string in absolute notation (octave 3 = no markers)
             Example: "c'4 d'4 e'4 f'4 | g'2 r2"
    """
    tokens = []
    
    for ev in events:
        # Skip structural markers
        if ev.get('type') == 'text_mark':
            continue
        
        # Skip raw_lilypond bypass events (already in LilyPond format)
        if ev.get('type') == 'raw_lilypond':
            tokens.append(ev.get('content', ''))
            continue
        
        # Handle barlines
        if ev.get('type') == 'barline':
            tokens.append('|')
            continue
        
        # Get duration
        ql = ev.get('ql', 1.0)
        dur_str = ql_to_lily_duration_string(ql)
        
        # Handle rests
        if ev.get('type') == 'rest':
            tokens.append(f"r{dur_str}")
        
        # Handle notes
        elif ev.get('type') == 'note':
            step = ev.get('step', 'c').lower()
            alter = ev.get('alter', 0)
            acc = ''
            if alter == 1: acc = 'is'
            elif alter == -1: acc = 'es'
            octave = ev.get('octave', 4)
            
            # Absolute notation: octave 3 is baseline (no markers)
            if octave == 3:
                pitch_text = f"{step}{acc}"
            elif octave > 3:
                marks = "'" * (octave - 3)
                pitch_text = f"{step}{acc}{marks}"
            else:
                marks = "," * (3 - octave)
                pitch_text = f"{step}{acc}{marks}"
            
            token = f"{pitch_text}{dur_str}"
            
            # Add tie if present
            if ev.get('tie') == 'start':
                token += '~'
            
            # Add articulations and dynamics (preserved from original)
            token = _add_articulations_and_dynamics(token, ev)
            tokens.append(token)
        
        # Handle chords
        elif ev.get('type') == 'chord':
            chord_pitches = []
            for pitch_data in ev.get('pitches', []):
                step = pitch_data.get('step', 'c').lower()
                alter = pitch_data.get('alter', 0)
                acc = ''
                if alter == 1: acc = 'is'
                elif alter == -1: acc = 'es'
                octave = pitch_data.get('octave', 4)
                
                if octave == 3:
                    pitch_text = f"{step}{acc}"
                elif octave > 3:
                    marks = "'" * (octave - 3)
                    pitch_text = f"{step}{acc}{marks}"
                else:
                    marks = "," * (3 - octave)
                    pitch_text = f"{step}{acc}{marks}"
                chord_pitches.append(pitch_text)
            
            chord_str = f"<{' '.join(chord_pitches)}>{dur_str}"
            chord_str = _add_articulations_and_dynamics(chord_str, ev)
            tokens.append(chord_str)
    
    return ' '.join(tokens)

def _parse_token(tok: str):
    if tok.lower().startswith('r'):
        m = re.match(r"r(\d+\.?)", tok, re.IGNORECASE)
        dur_token = m.group(1) if m else '4'
        ql = 4.0 / float(dur_token.replace('.', ''))
        if '.' in dur_token: ql *= 1.5
        return music21.note.Rest(quarterLength=ql)

    m = re.match(r"(?P<step>[a-g])(?P<acc>(?:is|es|s|b|#)?)(?P<oct>[,']*)(?P<dur>\d+\.?)?", tok, flags=re.IGNORECASE)
    if not m: return None
    
    data = m.groupdict()
    p = music21.pitch.Pitch(data['step'])
    acc_str = (data['acc'] or '').lower()
    if 'is' in acc_str or '#' in acc_str: p.accidental = '#'
    if 'es' in acc_str or 's' in acc_str: p.accidental = 'b'
    if 'b' in acc_str: p.accidental = 'b'
    
    p.octave = 4 + (data['oct'] or '').count("'") - (data['oct'] or '').count(",")
    dur_token = data['dur'] or '4'
    ql = 4.0 / float(dur_token.replace('.', ''))
    if '.' in dur_token: ql *= 1.5
    return music21.note.Note(p, quarterLength=ql)

def _resolve_relative(tok: str, last_pitch: music21.pitch.Pitch):
    element = _parse_token(tok)
    if not isinstance(element, music21.note.Note) or "'" in tok or "," in tok:
        return element
    element.pitch.octave = last_pitch.octave
    interval = music21.interval.Interval(last_pitch, element.pitch)
    if interval.direction == music21.interval.Direction.ASCENDING and interval.semitones > 6:
        element.pitch.octave -= 1
    elif interval.direction == music21.interval.Direction.DESCENDING and interval.semitones < -6:
        element.pitch.octave += 1
    return element
    
def parse_lilypond_snippet(snippet: str) -> music21.stream.Part:
    part = music21.stream.Part()
    relative_match = re.match(r"\\relative\s+([a-g][^ ]*)?\s*\{(.*)\}", snippet, re.DOTALL | re.IGNORECASE)
    if not relative_match: raise ValueError("Parser requires a \\relative block.")
    base_note_str, body = relative_match.groups()
    body = re.sub(r"\\(time|key|major|minor|tempo)\s+[^|\s}]+", "", body, re.IGNORECASE)
    body = body.replace("bmol", "b").replace("f#", "fis")
    tokens = [tok for tok in body.split() if tok != '|']
    last_note = _parse_token(base_note_str)
    if not isinstance(last_note, music21.note.Note): raise ValueError(f"Invalid base note: {base_note_str}")
    last_pitch = last_note.pitch
    for tok in tokens:
        element = _resolve_relative(tok, last_pitch)
        if element:
            part.append(element)
            if isinstance(element, music21.note.Note): last_pitch = element.pitch
    return part


def _build_documentation_block(metadata: dict, source_file: str = None) -> str:
    """
    Build comprehensive LilyPond comment block documenting all stations.
    
    Includes:
    - Original snippets (Station 1 & 2)
    - Shorthand structure (Station 3)
    - Programmatic voices (Station 4)
    - Usage instructions
    
    Args:
        metadata: Score metadata dictionary
        source_file: Optional path to source study file
        
    Returns:
        Formatted comment block string
    """
    lines = []
    has_content = False
    
    # Add source file attribution if provided
    if source_file:
        from pathlib import Path
        filename = Path(source_file).name
        lines.extend([
            "% ========================================",
            f"% GENERATED FROM: {filename}",
            "% ========================================",
            "%",
        ])
        has_content = True
    
    # ========================================
    # BLUEPRINT STRUCTURE (Station 3)
    # ========================================
    blueprint_structure = metadata.get('blueprint_structure', {})
    if blueprint_structure:
        has_content = True
        voice_stave_def = blueprint_structure.get('voice_stave_def', '')
        voice_stave_data = blueprint_structure.get('voice_stave_data', '')
        
        lines.extend([
            "% ========================================",
            "% BLUEPRINT STRUCTURE (Station 3)",
            "% ========================================",
            "%",
            "% VOICE_STAVE_DEF:",
            f"%   {voice_stave_def}",
            "%",
            "% VOICE_STAVE_DATA:",
        ])
        
        # Format the blueprint data with proper indentation
        for line in voice_stave_data.strip().split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                lines.append(f"%   {stripped}")
            elif stripped.startswith('#'):
                lines.append(f"%   {stripped}")
        
        lines.append("%")
    
    # ========================================
    # ORIGINAL SNIPPETS (Station 1 & 2)
    # ========================================
    original_snippets = metadata.get('original_snippets', {})
    tinynotation_snippets = metadata.get('tinynotation_snippets', {})
    
    if original_snippets or tinynotation_snippets:
        has_content = True
        lines.extend([
            "% ========================================",
            "% ORIGINAL SNIPPETS (Station 1 & 2)",
            "% ========================================",
            "%",
        ])
        
        # Show LilyPond snippets with duration metadata
        if original_snippets:
            lines.append("% LilyPond Format:")
            
            # Use barline-based duration calculation (simple, reliable, musical)
            from snippet_utils import calculate_snippet_duration_from_barlines
            
            for name, snippet in sorted(original_snippets.items()):
                # Calculate duration by counting barlines (bypasses parser complexity)
                duration_info = ""
                try:
                    result = calculate_snippet_duration_from_barlines(snippet)
                    total_ql = result['total_ql']
                    bars = result['bars']
                    time_sig = result['time_signature']
                    duration_info = f" ({total_ql:.1f} QL, {bars} bars, {time_sig})"
                except Exception as e:
                    # If calculation fails, just show snippet without duration
                    pass
                
                lines.append(f"%   {name}{duration_info}:")
                # Comment out each line of the snippet to prevent LilyPond from parsing it
                for snippet_line in snippet.strip().split('\n'):
                    lines.append(f"%     {snippet_line}")
                lines.append("%")
        
        # Show TinyNotation equivalents
        if tinynotation_snippets:
            lines.append("% TinyNotation Format:")
            for name, snippet in sorted(tinynotation_snippets.items()):
                lines.append(f"%   {name}:")
                lines.append(f"%     {snippet}")
                lines.append("%")
    
    # ========================================
    # TINYNOTATION INSPECTOR (Diagnostic Tool)
    # ========================================
    tiny_inspector = metadata.get('tinynotation_inspector', '')
    if tiny_inspector:
        has_content = True
        lines.extend([
            "% ========================================",
            "% TINYNOTATION INSPECTOR (Diagnostic)",
            "% ========================================",
            "% This TinyNotation string shows how the parser",
            "% resolved relative pitches. Use it to verify",
            "% octave resolution is working correctly.",
            "%",
            f"%   {tiny_inspector}",
            "%",
        ])
    
    # Legacy support: original_input field
    original_input = metadata.get('original_input', '')
    if original_input and not original_snippets:
        has_content = True
        lines.extend([
            "% ========================================",
            "% ORIGINAL LILYPOND INPUT",
            "% ========================================",
            "%",
        ])
        for line in original_input.split('\n'):
            lines.append(f"% {line}")
        lines.append("%")
    
    # ========================================
    # SHORTHAND STRUCTURE (Station 3)
    # ========================================
    voice_assignments = metadata.get('voice_assignments', {})
    if voice_assignments:
        has_content = True
        lines.extend([
            "% ========================================",
            "% SHORTHAND STRUCTURE (Station 3)",
            "% ========================================",
            "%",
        ])
        for part_name, assignments in sorted(voice_assignments.items()):
            if isinstance(assignments, dict):
                for voice_name, expression in sorted(assignments.items()):
                    lines.append(f"%   {part_name}.{voice_name}: {expression}")
            else:
                lines.append(f"%   {part_name}: {assignments}")
        lines.append("%")
    
    # ========================================
    # VOICE TRACKING (Station 4 - Detailed)
    # ========================================
    voice_tracking = metadata.get('voice_tracking', {})
    if voice_tracking:
        has_content = True
        lines.extend([
            "% ========================================",
            "% VOICE TRACKING (Station 4 - Detailed)",
            "% ========================================",
            "%",
        ])
        for voice_id, track_data in sorted(voice_tracking.items()):
            transformation = track_data.get('transformation', 'unknown')
            description = track_data.get('description', '')
            event_count = track_data.get('events', 0)
            source = track_data.get('source', '')
            lines.append(f"% {voice_id}:")
            lines.append(f"%   Transformation: {transformation}")
            lines.append(f"%   Description: {description}")
            lines.append(f"%   Events: {event_count}")
            if source:
                lines.append(f"%   Source: {source}")
            lines.append("%")
    
    # ========================================
    # PROGRAMMATIC VOICES (Station 4)
    # ========================================
    programmatic_voices = metadata.get('programmatic_voices', {})
    if programmatic_voices:
        has_content = True
        lines.extend([
            "% ========================================",
            "% PROGRAMMATIC VOICES (Station 4)",
            "% ========================================",
            "%",
        ])
        for voice_name, voice_data in sorted(programmatic_voices.items()):
            lily_notation = voice_data.get('lilypond', '')
            lines.append(f"% {voice_name}:")
            lines.append(f"%   {lily_notation}")
            lines.append("%")
    
    # ========================================
    # REFERENCE DOCUMENTATION
    # ========================================
    if has_content:
        lines.extend([
            "% ========================================",
            "% REFERENCE",
            "% ========================================",
            "% This header shows the original composition structure:",
            "% - Blueprint strings define the musical form",
            "% - Original LilyPond snippets show the source material",
            "% - TinyNotation provides an alternative notation view",
            "%",
            "% Use this as reference when modifying or extending the composition.",
            "% ========================================",
            "",
        ])
    
    return "\n".join(lines) if has_content else ""


def engrave_with_abjad(score_data: dict, output_basename: str, source_file: str = None):
    print(f"🎶 Engraving '{score_data.get('metadata', {}).get('title', '')}'...")
    out_dir = OUTPUTS_DIR; out_dir.mkdir(parents=True, exist_ok=True)
    ly_path = out_dir / f"{output_basename}.ly"
    title = score_data.get('metadata', {}).get('title', output_basename)
    metadata = score_data.get('metadata', {})
    
    # Copy source study file to outputs for inspection (always, for visual correlation)
    # Also inject Station 2 library (parsed events) and generated snippets if they exist
    if source_file:
        source_path = Path(source_file)
        if source_path.exists():
            dest_path = out_dir / source_path.name
            import shutil
            
            # Check if we have Station 2 library or generated snippets to inject
            station2_snippets = metadata.get('station2_snippets', {})
            generated_snippets = metadata.get('generated_snippets', {})
            
            if station2_snippets or generated_snippets:
                # Read source file
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                snippet_block = ""
                
                # Build Station 2 library section (editable LilyPond snippets!)
                if station2_snippets:
                    snippet_block += "\n# ============================================================================\n"
                    snippet_block += "# STATION 2: SNIPPET LIBRARY (Editable LilyPond - Absolute Notation)\n"
                    snippet_block += "# ============================================================================\n"
                    snippet_block += "# These are EDITABLE LilyPond snippets in absolute notation.\n"
                    snippet_block += "# You can copy and modify these snippets for reuse in other studies!\n"
                    snippet_block += "#\n"
                    snippet_block += "# ⭐ ALL snippets are included:\n"
                    snippet_block += "#    - Original snippets from Station 1 (your LilyPond input)\n"
                    snippet_block += "#    - Transformed snippets from Station 3 (transpose, retrograde, etc.)\n"
                    snippet_block += "#\n"
                    snippet_block += "# 📝 Notation format: Absolute (octave 3 = baseline)\n"
                    snippet_block += "#    c  = C3,  c' = C4,  c'' = C5\n"
                    snippet_block += "#    c, = C2,  c,, = C1\n"
                    snippet_block += "#\n"
                    snippet_block += "# Usage in other studies:\n"
                    snippet_block += "#   1. Copy any snippet below (e.g., THEME_A = r\\\"\\\"\\\"...\\\"\\\"\\\")\n"
                    snippet_block += "#   2. Paste into your new study's Station 1\n"
                    snippet_block += "#   3. Edit the LilyPond code as needed\n"
                    snippet_block += "#   4. Use the snippet name in VOICE_STAVE_DATA\n"
                    snippet_block += "# ============================================================================\n\n"
                    
                    for name, lily_code in sorted(station2_snippets.items()):
                        # Format snippet name to be valid Python identifier
                        safe_name = name.replace('(', '_').replace(')', '').replace(',', '').replace("'", '').replace(' ', '_')
                        snippet_block += f"{safe_name} = r\"\"\"\n{lily_code}\n\"\"\"\n\n"
                    
                    snippet_block += f"# Total snippets in Station 2 library: {len(station2_snippets)}\n"
                    snippet_block += "# ✨ These include both original AND transformed snippets!\n\n"
                
                # Build generated snippets section (LilyPond variations)
                if generated_snippets:
                    snippet_block += "\n# ============================================================================\n"
                    snippet_block += "# GENERATED VARIATIONS (Auto-generated LilyPond from transformations)\n"
                    snippet_block += "# ============================================================================\n"
                    snippet_block += "# These snippets show the LilyPond representation of transformations.\n"
                    snippet_block += "# They can be used as standalone LilyPond snippets if needed.\n"
                    snippet_block += "# ============================================================================\n\n"
                    
                    for name, lily_text in sorted(generated_snippets.items()):
                        # Format LilyPond text for readability: add line breaks after bar lines
                        formatted_lily = lily_text.replace(' | ', ' |\n    ')
                        # If no explicit bar lines, try to break after every ~8 tokens for readability
                        if '|' not in formatted_lily:
                            tokens = formatted_lily.split()
                            if len(tokens) > 10:
                                # Insert line breaks every 8 tokens to make it more readable
                                chunks = []
                                for i in range(0, len(tokens), 8):
                                    chunk = ' '.join(tokens[i:i+8])
                                    chunks.append('    ' + chunk if i > 0 else chunk)
                                formatted_lily = '\n'.join(chunks)
                        
                        snippet_block += f"{name}_LILY = r\"\"\"\n{formatted_lily}\n\"\"\"\n\n"
                
                # Insert after the original snippets section (before Station 2 comment)
                # Look for the Station 2 marker
                if '# STATION 2' in content or '# Station 2' in content:
                    marker = '# STATION 2' if '# STATION 2' in content else '# Station 2'
                    # Replace the Station 2 comment section with actual snippets
                    import re
                    # Find the Station 2 comment block and replace it entirely
                    pattern = r'(# =+\s*\n# STATION 2:.*?\n# =+\s*\n.*?(?=\n# =+|$))'
                    if re.search(pattern, content, re.DOTALL):
                        # Escape backslashes in snippet_block for regex replacement
                        safe_snippet_block = snippet_block.rstrip().replace('\\', r'\\')
                        content = re.sub(pattern, safe_snippet_block, content, count=1, flags=re.DOTALL)
                    else:
                        # Fallback: just insert before marker
                        content = content.replace(
                            f"# ============================================================================\n{marker}",
                            snippet_block + f"# ============================================================================\n{marker}"
                        )
                elif '# TINYNOTATION' in content.upper():
                    # Alternative: look for TinyNotation header
                    import re
                    pattern = r'(# =+\n# .*TINYNOTATION.*\n# =+)'
                    content = re.sub(pattern, snippet_block + r'\1', content, count=1)
                else:
                    # Fallback: insert after IMPORTS section
                    if '# IMPORTS' in content:
                        content = content.replace(
                            '# IMPORTS',
                            snippet_block + '# IMPORTS'
                        )
                
                # Write modified content
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                message_parts = []
                if station2_snippets:
                    message_parts.append(f"{len(station2_snippets)} Station 2 parsed events")
                if generated_snippets:
                    message_parts.append(f"{len(generated_snippets)} generated LilyPond snippets")
                print(f"📋 Copied {source_path.name} to outputs/ with {' and '.join(message_parts)}")
            else:
                # No snippets to inject, just copy as before
                shutil.copy2(source_path, dest_path)
                print(f"📋 Copied {source_path.name} to outputs/")

    # For multi-staff scores, synchronize break positions across all staves
    # Determine break positions based on barlines in a reference staff
    parts_items = sorted(score_data.get('parts', {}).items(), reverse=True)
    break_after_barline_numbers = set()  # Set of barline numbers (0, 1, 2, ...) where breaks should occur
    
    if len(parts_items) > 1:
        # Use first staff as reference for break positions
        first_part_name, first_part_events = parts_items[0]
        if isinstance(first_part_events, list):  # Only for single-voice staves
            barline_count = 0
            for ev in first_part_events:
                if ev.get('type') == 'barline':
                    # Only count SECTION barlines (||), not measure barlines (|)
                    if ev.get('style') == '||':
                        # Break after EVERY section barline to start each section on a new system
                        break_after_barline_numbers.add(barline_count)
                        barline_count += 1
            print(f"[DEBUG] Break positions: after section barlines {sorted(break_after_barline_numbers)}")

    staves = []
    # Note: reverse=True ensures correct staff order (Melody at top, Harmony at bottom)
    # LilyPond renders staves in reverse vertical order, so we reverse alphabetical sort
    for part_name, events_or_voices in parts_items:
        # Check if this is a multi-voice part (dict) or single-voice (list)
        is_multi_voice = isinstance(events_or_voices, dict)
        
        if is_multi_voice:
            # Multi-voice polyphonic structure: dict of voice names to event lists
            voice_bodies = []
            for voice_name, events in events_or_voices.items():
                voice_tokens = []
                for ev in events:
                    # Handle text marks (rehearsal marks for section labels)
                    if ev.get('type') == 'text_mark':
                        mark_text = ev.get('text', '')
                        voice_tokens.append(f"\\mark \"{mark_text}\"")
                        continue
                    
                    ql = ev.get('ql', 1.0)
                    dur_str = ql_to_lily_duration_string(ql)
                    if ev.get('type') == 'rest':
                        voice_tokens.append(f"r{dur_str}")
                    elif ev.get('type') == 'chord':
                        # Handle chord events - format as <pitch1 pitch2 pitch3>duration
                        chord_pitches = []
                        for pitch_data in ev.get('pitches', []):
                            step = pitch_data.get('step', 'c').lower()
                            alter = pitch_data.get('alter', 0)
                            acc = ''
                            if alter == 1: acc = 'is'
                            elif alter == -1: acc = 'es'
                            octave = pitch_data.get('octave', 4)
                            if octave == 4:
                                pitch_text = f"{step}{acc}"
                            elif octave > 4:
                                marks = "'" * (octave - 4)
                                pitch_text = f"{step}{acc}{marks}"
                            else:
                                marks = "," * (4 - octave)
                                pitch_text = f"{step}{acc}{marks}"
                            chord_pitches.append(pitch_text)
                        chord_str = f"<{' '.join(chord_pitches)}>{dur_str}"
                        # Add articulations and dynamics
                        chord_str = _add_articulations_and_dynamics(chord_str, ev)
                        voice_tokens.append(chord_str)
                    elif ev.get('type') == 'note':
                        step = ev.get('step', 'c').lower()
                        alter = ev.get('alter', 0)
                        acc = ''
                        if alter == 1: acc = 'is'
                        elif alter == -1: acc = 'es'
                        octave = ev.get('octave', 4)
                        if octave == 4:
                            pitch_text = f"{step}{acc}"
                        elif octave > 4:
                            marks = "'" * (octave - 4)
                            pitch_text = f"{step}{acc}{marks}"
                        else:
                            marks = "," * (4 - octave)
                            pitch_text = f"{step}{acc}{marks}"
                        token = f"{pitch_text}{dur_str}"
                        # Add articulations and dynamics
                        token = _add_articulations_and_dynamics(token, ev)
                        voice_tokens.append(token)
                voice_body = " ".join(voice_tokens)
                voice_bodies.append(f"{{ {voice_body} }}")
            
            # Combine voices with LilyPond polyphonic syntax: << {...} \\ {...} >>
            separator = ' \\\\ '
            body = f"<< {separator.join(voice_bodies)} >>"
        else:
            # Single-voice structure: list of events (backward compatible)
            events = events_or_voices
            part_tokens = []
            
            # Track quarter lengths for automatic bar line insertion
            # Parse time signature to get measure length in QL
            time_sig = metadata.get('time_signature', '4/4')
            try:
                time_num, time_den = map(int, time_sig.split('/'))
                measure_ql = (time_num / time_den) * 4.0  # Convert to quarter notes
            except:
                measure_ql = 4.0  # Default to 4/4
            
            current_measure_ql = 0.0  # Track QL accumulated in current measure
            
            for ev in events:
                # Handle text marks (rehearsal marks for section labels)
                if ev.get('type') == 'text_mark':
                    mark_text = ev.get('text', '')
                    part_tokens.append(f"\\mark \"{mark_text}\"")
                    continue
                
                # NEW: Handle raw_lilypond bypass events
                if ev.get('type') == 'raw_lilypond':
                    # Inject original LilyPond string directly (bypasses parser QL bugs)
                    content = ev.get('content', '')
                    snippet_name = ev.get('snippet_name', 'unknown')
                    part_tokens.append(content)
                    print(f"[BYPASS] Injected original LilyPond for {snippet_name}")
                    continue
                
                ql = ev.get('ql', 1.0)
                dur_str = ql_to_lily_duration_string(ql)
                if ev.get('type') == 'rest':
                    part_tokens.append(f"r{dur_str}")
                elif ev.get('type') == 'multi_voice_section':
                    # Handle multi-voice sections created by Blueprint Framework
                    # Extract voices dictionary and create LilyPond polyphonic syntax
                    voices_dict = ev.get('voices', {})
                    voice_bodies = []
                    
                    for voice_name, voice_events in voices_dict.items():
                        if voice_events is None:
                            # Rest placeholder - skip for now
                            continue
                        
                        voice_tokens = []
                        for v_ev in voice_events:
                            v_ql = v_ev.get('ql', 1.0)
                            v_dur_str = ql_to_lily_duration_string(v_ql)
                            
                            if v_ev.get('type') == 'rest':
                                voice_tokens.append(f"r{v_dur_str}")
                            elif v_ev.get('type') == 'note':
                                step = v_ev.get('step', 'c').lower()
                                alter = v_ev.get('alter', 0)
                                acc = ''
                                if alter == 1: acc = 'is'
                                elif alter == -1: acc = 'es'
                                octave = v_ev.get('octave', 4)
                                if octave == 3:
                                    pitch_text = f"{step}{acc}"
                                elif octave > 3:
                                    marks = "'" * (octave - 3)
                                    pitch_text = f"{step}{acc}{marks}"
                                else:
                                    marks = "," * (3 - octave)
                                    pitch_text = f"{step}{acc}{marks}"
                                token = f"{pitch_text}{v_dur_str}"
                                token = _add_articulations_and_dynamics(token, v_ev)
                                voice_tokens.append(token)
                            elif v_ev.get('type') == 'chord':
                                chord_pitches = []
                                for pitch_data in v_ev.get('pitches', []):
                                    step = pitch_data.get('step', 'c').lower()
                                    alter = pitch_data.get('alter', 0)
                                    acc = ''
                                    if alter == 1: acc = 'is'
                                    elif alter == -1: acc = 'es'
                                    octave = pitch_data.get('octave', 4)
                                    if octave == 3:
                                        pitch_text = f"{step}{acc}"
                                    elif octave > 3:
                                        marks = "'" * (octave - 3)
                                        pitch_text = f"{step}{acc}{marks}"
                                    else:
                                        marks = "," * (3 - octave)
                                        pitch_text = f"{step}{acc}{marks}"
                                    chord_pitches.append(pitch_text)
                                chord_str = f"<{' '.join(chord_pitches)}>{v_dur_str}"
                                chord_str = _add_articulations_and_dynamics(chord_str, v_ev)
                                voice_tokens.append(chord_str)
                        
                        voice_body = " ".join(voice_tokens)
                        voice_bodies.append(f"{{ {voice_body} }}")
                    
                    # Combine voices with LilyPond polyphonic syntax
                    if voice_bodies:
                        separator = ' \\\\ '
                        multi_voice_token = f"<< {separator.join(voice_bodies)} >>"
                        part_tokens.append(multi_voice_token)
                elif ev.get('type') == 'barline':
                    # Handle bar line markers
                    style = ev.get('style', '||')
                    part_tokens.append(f"\\bar \"{style}\"")
                elif ev.get('type') == 'tuplet':
                    # Handle tuplet events - format as \tuplet n/d { ... }
                    numerator = ev.get('numerator', 3)
                    denominator = ev.get('denominator', 2)
                    tuplet_notes_data = ev.get('notes', [])
                    tuplet_note_tokens = []
                    
                    for note_data in tuplet_notes_data:
                        note_ql = note_data.get('ql', 1.0)
                        note_dur_str = ql_to_lily_duration_string(note_ql)
                        if note_data.get('type') == 'rest':
                            tuplet_note_tokens.append(f"r{note_dur_str}")
                        elif note_data.get('type') == 'note':
                            step = note_data.get('step', 'c').lower()
                            alter = note_data.get('alter', 0)
                            acc = ''
                            if alter == 1: acc = 'is'
                            elif alter == -1: acc = 'es'
                            octave = note_data.get('octave', 4)
                            if octave == 3:
                                pitch_text = f"{step}{acc}"
                            elif octave > 3:
                                marks = "'" * (octave - 3)
                                pitch_text = f"{step}{acc}{marks}"
                            else:
                                marks = "," * (3 - octave)
                                pitch_text = f"{step}{acc}{marks}"
                            token = f"{pitch_text}{note_dur_str}"
                            # Add articulations and dynamics
                            token = _add_articulations_and_dynamics(token, note_data)
                            tuplet_note_tokens.append(token)
                    
                    tuplet_body = " ".join(tuplet_note_tokens)
                    part_tokens.append(f"\\tuplet {numerator}/{denominator} {{ {tuplet_body} }}")
                elif ev.get('type') == 'chord':
                    # Handle chord events - format as <pitch1 pitch2 pitch3>duration
                    chord_pitches = []
                    for pitch_data in ev.get('pitches', []):
                        step = pitch_data.get('step', 'c').lower()
                        alter = pitch_data.get('alter', 0)
                        acc = ''
                        if alter == 1: acc = 'is'
                        elif alter == -1: acc = 'es'
                        octave = pitch_data.get('octave', 4)
                        # LilyPond absolute: octave 3 is default (no markers)
                        if octave == 3:
                            pitch_text = f"{step}{acc}"
                        elif octave > 3:
                            marks = "'" * (octave - 3)
                            pitch_text = f"{step}{acc}{marks}"
                        else:
                            marks = "," * (3 - octave)
                            pitch_text = f"{step}{acc}{marks}"
                        chord_pitches.append(pitch_text)
                    chord_str = f"<{' '.join(chord_pitches)}>{dur_str}"
                    # Add articulations and dynamics
                    chord_str = _add_articulations_and_dynamics(chord_str, ev)
                    part_tokens.append(chord_str)
                elif ev.get('type') == 'note':
                    step = ev.get('step', 'c').lower()
                    alter = ev.get('alter', 0)
                    acc = ''
                    if alter == 1: acc = 'is'
                    elif alter == -1: acc = 'es'
                    octave = ev.get('octave', 4)
                    # LilyPond absolute: octave 3 is default (no markers)
                    # c = C3, c' = C4, c'' = C5, c, = C2, c,, = C1
                    if octave == 3:
                        pitch_text = f"{step}{acc}"
                    elif octave > 3:
                        marks = "'" * (octave - 3)
                        pitch_text = f"{step}{acc}{marks}"
                    else:
                        marks = "," * (3 - octave)
                        pitch_text = f"{step}{acc}{marks}"
                    token = f"{pitch_text}{dur_str}"
                    # Add articulations and dynamics
                    token = _add_articulations_and_dynamics(token, ev)
                    part_tokens.append(token)
                
                # AUTO-INSERT BAR LINES: Track QL and insert | at measure boundaries
                # Only for note/rest/chord events (not barline, text_mark, raw_lilypond, etc.)
                if ev.get('type') in ['note', 'rest', 'chord']:
                    ql = ev.get('ql', 0.0)
                    current_measure_ql += ql
                    
                    # Check if we've completed a measure (with small tolerance for floating point)
                    if abs(current_measure_ql - measure_ql) < 0.01:
                        # Exact match: insert bar line and reset
                        part_tokens.append("|")
                        current_measure_ql = 0.0
                    elif current_measure_ql > measure_ql:
                        # Overshoot: insert bar line and carry over excess
                        part_tokens.append("|")
                        current_measure_ql = current_measure_ql - measure_ql
            
            # Format body with line breaks for readability and system breaks
            # For multi-staff scores, use synchronized break positions
            formatted_lines = []
            current_line = []
            barline_number = -1  # Track which barline we're at (0-indexed)
            tokens_since_last_break = 0  # Prevent overly long lines
            MAX_TOKENS_PER_LINE = 20  # Limit line length to prevent staff separation
            
            for i, token in enumerate(part_tokens):
                current_line.append(token)
                tokens_since_last_break += 1
                
                # Check if this is a SECTION barline token (||), not measure barline (|)
                if '\\bar "||"' in token:
                    barline_number += 1
                    # Check if this barline position should have a break
                    if barline_number in break_after_barline_numbers:
                        # Add \break command to force a system break in LilyPond
                        current_line.append('\\break')
                        formatted_lines.append(" ".join(current_line))
                        current_line = []
                        tokens_since_last_break = 0
                    elif len(break_after_barline_numbers) == 0:
                        # Fallback: for single-staff scores, break every 2 section barlines
                        if barline_number % 2 == 1:  # 1, 3, 5, ... (0-indexed)
                            current_line.append('\\break')
                            formatted_lines.append(" ".join(current_line))
                            current_line = []
                            tokens_since_last_break = 0
                # If line is getting too long, insert a line break (no \break command)
                elif tokens_since_last_break >= MAX_TOKENS_PER_LINE and '\\mark' not in token:
                    formatted_lines.append(" ".join(current_line))
                    current_line = []
                    tokens_since_last_break = 0
            
            # Add any remaining tokens
            if current_line:
                formatted_lines.append(" ".join(current_line))
            
            body = "\n    ".join(formatted_lines)
        
        # Determine clef - check metadata first, then use heuristic
        clef = "treble"  # default
        if 'staff_info' in metadata and part_name in metadata['staff_info']:
            clef = metadata['staff_info'][part_name].get('clef', 'treble')
        elif "lower" in part_name.lower() or "bass" in part_name.lower() or "harmony" in part_name.lower():
            clef = "bass"
        
        # --- NEW: Add LilyPond directives from metadata ---
        staff_directives = []
        if 'time_signature' in metadata:
            staff_directives.append(f"\\time {metadata['time_signature']}")
        if 'key_signature' in metadata:
            key_sig = metadata['key_signature']
            if isinstance(key_sig, dict):
                tonic = key_sig.get('tonic', 'c')
                mode = key_sig.get('mode', 'major')
                staff_directives.append(f"\\key {tonic} \\{mode}")
        if 'tempo' in metadata:
            tempo_data = metadata['tempo']
            if isinstance(tempo_data, dict):
                beat_duration = tempo_data.get('beat_duration', 4)
                bpm = tempo_data.get('bpm', 120)
                staff_directives.append(f"\\tempo {beat_duration} = {bpm}")
            elif isinstance(tempo_data, int):
                staff_directives.append(f"\\tempo 4 = {tempo_data}")
        directives_str = " ".join(staff_directives)
        if directives_str:
            staff_content = f"  \\new Staff {{\n    \\clef {clef}\n    {directives_str}\n    {body}\n  }}\n"
        else:
            staff_content = f"  \\new Staff {{\n    \\clef {clef}\n    {body}\n  }}\n"
        staves.append(staff_content)
    
    # Build score block - use StaffGroup for multiple staves (piano-style)
    if len(staves) > 1:
        score_block = f"  \\new StaffGroup <<\n{''.join(staves)}  >>"
    else:
        score_block = f"  {staves[0]}"
    
    # Build comprehensive documentation block
    comment_section = _build_documentation_block(metadata, source_file)

    # Build comprehensive LilyPond header with all metadata
    header_fields = [f'title = "{title}"']
    
    if 'composer' in metadata:
        header_fields.append(f'composer = "{metadata["composer"]}"')
    
    if 'opus_number' in metadata:
        header_fields.append(f'opus = "{metadata["opus_number"]}"')
    
    # Add snippet references if available
    if 'original_snippets' in metadata:
        snippet_names = ', '.join(sorted(metadata['original_snippets'].keys()))
        header_fields.append(f'subtitle = "Based on: {snippet_names}"')
    
    header_block = '\\header {\n  ' + '\n  '.join(header_fields) + '\n}'

    # Add paper block for proper page formatting
    paper_block = r'''
\paper {
  indent = 0\mm
  line-width = 180\mm
  ragged-right = ##f
  ragged-last = ##f
  page-breaking = #ly:optimal-breaking
  system-system-spacing.basic-distance = #12
  system-system-spacing.minimum-distance = #8
  system-system-spacing.padding = #1
  score-system-spacing.basic-distance = #14
}
'''

    # Layout block to control staff visibility
    # Note: Removed \RemoveEmptyStaves override as it's not needed for most scores
    # LilyPond will show all staves by default in multi-staff scores
    layout_block = r'''  \layout {
    \context {
      \Staff
      % Keep empty staves visible (default behavior)
    }
  }'''

    ly_content = f'\\version "2.24.1"\n{comment_section}{header_block}\n{paper_block}\n\\score {{\n  {score_block}\n{layout_block}\n  \\midi {{ }}\n}}'
    ly_path.write_text(ly_content, encoding='utf-8')
    print(f"Wrote LilyPond file: {ly_path}")
    try:
        subprocess.run(["lilypond", str(ly_path.name)], cwd=str(out_dir), capture_output=True, text=True, check=True)
        print(f"✅ Successfully compiled {output_basename}.pdf and .midi")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️ Could not compile with LilyPond. Error:\n{getattr(e, 'stderr', e)}")


def export_to_musicxml(score_data: dict, output_basename: str):
    """
    Reconstructs a music21.Score from score_data and exports to MusicXML.
    
    This function enables MuseScore compatibility by:
    1. Converting score_data dict back to music21.Score
    2. Adding metadata (title, composer)
    3. Exporting to .musicxml format
    
    Multi-voice handling:
    - Currently, each voice in a multi-voice part exports to its own staff
    - This is a limitation of the music21 library's voice handling
    - Users can group/combine staves manually in MuseScore if desired
    - All musical content is preserved correctly
    
    Args:
        score_data: The score data dictionary
        output_basename: Base name for output file (e.g., 'ninth')
    """
    from music_data import data_to_part
    import music21
    
    title = score_data.get('metadata', {}).get('title', 'Untitled')
    print(f"🎵 Exporting '{title}' to MusicXML...")
    
    # Check if this study uses bypass mode (raw LilyPond snippets)
    has_bypass = False
    for part_name, part_content in score_data.get('parts', {}).items():
        events = part_content if isinstance(part_content, list) else []
        if isinstance(part_content, dict):
            # Check all voices in multi-voice parts
            for voice_events in part_content.values():
                if any(ev.get('type') == 'raw_lilypond' for ev in voice_events):
                    has_bypass = True
                    break
        elif any(ev.get('type') == 'raw_lilypond' for ev in events):
            has_bypass = True
            break
        if has_bypass:
            break
    
    if has_bypass:
        print("ℹ️  Note: This study uses BYPASS MODE (raw LilyPond snippets)")
        print("   Re-parsing bypass snippets for MusicXML export...")
        print("   💡 Articulations, dynamics, and complex expressions may be simplified")
    
    # Helper function to convert raw_lilypond events to parsed events
    def convert_raw_lilypond_to_events(events_list, part_metadata=None):
        """
        Convert raw_lilypond events to parsed note/rest/barline events.
        Uses the SAME pipeline as transformations (data_to_part).
        Also extracts clef from first snippet if present.
        """
        from lilypond_parser import parse_lilypond_to_data
        import re
        
        raw_count = sum(1 for ev in events_list if ev.get('type') == 'raw_lilypond')
        if raw_count > 0:
            print(f"   Converting {raw_count} raw_lilypond events to parsed events...")
        
        cleaned_events = []
        part_clef = None  # Extract from first snippet that has clef
        
        for idx, ev in enumerate(events_list):
            if ev.get('type') == 'raw_lilypond':
                # Re-parse using SAME pipeline as transformations
                content = ev.get('content', '')
                snippet_name = ev.get('snippet_name', 'unknown')
                
                # Extract clef from first snippet that has one
                if part_clef is None:
                    clef_match = re.search(r'\\clef\s+"?([a-z]+)"?', content)
                    if clef_match:
                        part_clef = clef_match.group(1)
                        if part_metadata is not None:
                            part_metadata['clef'] = part_clef
                            print(f"      Detected clef: {part_clef} (snippet: {snippet_name})")
                
                if content:
                    try:
                        # Wrap in minimal context ONLY if not already wrapped
                        # (Some snippets already have \relative, \time, etc.)
                        has_relative = '\\relative' in content
                        if not has_relative and '\\absolute' not in content:
                            wrapped = f"\\relative c' {{ {content} }}"
                        else:
                            wrapped = content
                        
                        # CRITICAL: Disable barline validation for MusicXML export
                        # Trust the original barlines from the composer
                        parsed = parse_lilypond_to_data(wrapped, part_name='temp', validate_barlines=False)
                        parsed_events = parsed.get('parts', {}).get('temp', [])
                        
                        # Count events for debugging
                        note_count = sum(1 for e in parsed_events if e.get('type') == 'note')
                        barline_count = sum(1 for e in parsed_events if e.get('type') == 'barline')
                        print(f"      '{snippet_name}': {note_count} notes, {barline_count} barlines")
                        
                        # Add all parsed events (notes, rests, barlines)
                        # Skip text_marks as they're LilyPond-specific
                        for parsed_ev in parsed_events:
                            if parsed_ev.get('type') in ['note', 'rest', 'chord', 'barline']:
                                cleaned_events.append(parsed_ev)
                        
                        # NOTE: Don't force-add closing barlines here
                        # The snippets already have barlines where the composer put them
                        # Adding extra barlines creates empty measures filled with padding rests
                    
                    except Exception as e:
                        # If re-parsing fails, add a rest as placeholder
                        print(f"⚠️  Warning: Could not re-parse snippet '{snippet_name}': {e}")
                        cleaned_events.append({
                            'type': 'rest',
                            'ql': 1.0
                        })
            else:
                # Keep non-raw_lilypond events as-is
                cleaned_events.append(ev)
        
        barline_total = sum(1 for ev in cleaned_events if ev.get('type') == 'barline')
        if raw_count > 0:
            print(f"   Result: {len(cleaned_events)} total events ({barline_total} barlines)")
        
        return cleaned_events
    
    # Create the main score object
    score = music21.stream.Score()
    
    # Add metadata to the score
    metadata = score_data.get('metadata', {})
    score.metadata = music21.metadata.Metadata()
    
    if 'title' in metadata:
        score.metadata.title = metadata['title']
    if 'composer' in metadata:
        score.metadata.composer = metadata.get('composer', '')
    if 'tagline' in metadata:
        # MusicXML doesn't have tagline, but we can add it as copyright
        score.metadata.copyright = metadata.get('tagline', '')
    
    # Reconstruct parts from the score_data dictionary
    # First pass: detect clefs from original snippets and pre-convert events
    parts_cleaned = {}
    parts_metadata = {}
    
    # Extract clefs from original snippets in metadata
    if 'original_snippets' in metadata:
        for snippet_name, lily_source in metadata['original_snippets'].items():
            clef_match = re.search(r'\\clef\s+"?([a-z]+)"?', lily_source)
            if clef_match:
                # Store temporarily, will be matched to parts later
                metadata[f'_snippet_clef_{snippet_name}'] = clef_match.group(1)
    
    for part_name, part_content in score_data.get('parts', {}).items():
        if isinstance(part_content, dict):
            # Multi-voice part
            parts_cleaned[part_name] = {}
            for voice_name, voice_events in sorted(part_content.items()):
                voice_key = f"{part_name}_{voice_name}"
                temp_meta = {}
                cleaned = convert_raw_lilypond_to_events(voice_events, temp_meta)
                parts_cleaned[part_name][voice_name] = cleaned
                
                # Check if any event has a snippet with a clef
                for ev in voice_events:
                    if ev.get('type') == 'raw_lilypond':
                        snippet_name = ev.get('snippet_name')
                        if snippet_name and f'_snippet_clef_{snippet_name}' in metadata:
                            parts_metadata[voice_key] = {'clef': metadata[f'_snippet_clef_{snippet_name}']}
                            break
        else:
            # Single-voice part
            temp_meta = {}
            cleaned = convert_raw_lilypond_to_events(part_content, temp_meta)
            parts_cleaned[part_name] = cleaned
            
            # Check if any event has a snippet with a clef
            for ev in part_content:
                if ev.get('type') == 'raw_lilypond':
                    snippet_name = ev.get('snippet_name')
                    if snippet_name and f'_snippet_clef_{snippet_name}' in metadata:
                        parts_metadata[part_name] = {'clef': metadata[f'_snippet_clef_{snippet_name}']}
                        break
    
    # Second pass: create music21 Parts with correct clefs
    for part_name, part_content in parts_cleaned.items():
        if isinstance(part_content, dict):
            # Multi-voice part
            for voice_name, cleaned_events in sorted(part_content.items()):
                part_meta = metadata.copy()
                
                # Apply detected clef
                voice_key = f"{part_name}_{voice_name}"
                if voice_key in parts_metadata and 'clef' in parts_metadata[voice_key]:
                    part_meta['clef'] = parts_metadata[voice_key]['clef']
                    print(f"   Using clef '{part_meta['clef']}' for part '{voice_key}'")
                
                voice_part = data_to_part(cleaned_events, part_meta)
                voice_part.id = voice_key
                voice_part.partName = f"{part_name} - {voice_name}"
                score.insert(0, voice_part)
            
        else:
            # Single-voice part
            part_meta = metadata.copy()
            
            # Apply detected clef
            if part_name in parts_metadata and 'clef' in parts_metadata[part_name]:
                part_meta['clef'] = parts_metadata[part_name]['clef']
                print(f"   Using clef '{part_meta['clef']}' for part '{part_name}'")
            
            part = data_to_part(part_content, part_meta)
            part.id = part_name
            part.partName = part_name
            score.insert(0, part)
    
    # Write the file
    out_dir = OUTPUTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    xml_path = out_dir / f"{output_basename}.musicxml"
    
    # Ensure all parts have the same number of measures before exporting
    # Some pipelines (bypass + parsed transformations) can produce
    # mismatched measure counts per part. Pad shorter parts with
    # full-measure rests so MusicXML parts align cleanly in MuseScore.
    try:
        # Determine desired measure length from metadata (default 4/4)
        measure_length = 4.0
        if 'time_signature' in metadata:
            try:
                num, denom = map(int, metadata['time_signature'].split('/'))
                measure_length = float(num) * (4.0 / float(denom))
            except Exception:
                pass

        part_measures = [len(p.getElementsByClass('Measure')) for p in score.parts]
        if part_measures:
            max_measures = max(part_measures)
            for p in score.parts:
                current = len(p.getElementsByClass('Measure'))
                while current < max_measures:
                    m = music21.stream.Measure()
                    # copy time/key/clef from first measure where possible
                    first_measure = p.getElementsByClass('Measure').first()
                    if first_measure is not None:
                        if hasattr(first_measure, 'timeSignature') and first_measure.timeSignature is not None:
                            m.timeSignature = first_measure.timeSignature
                        if hasattr(first_measure, 'keySignature') and first_measure.keySignature is not None:
                            m.keySignature = first_measure.keySignature
                        if hasattr(first_measure, 'clef') and first_measure.clef is not None:
                            m.clef = first_measure.clef
                    # add full-measure rest
                    r = music21.note.Rest(quarterLength=measure_length)
                    m.append(r)
                    p.append(m)
                    current += 1
    except Exception:
        # Non-fatal: if padding fails, continue and let export attempt anyway
        pass
    try:
        score.write('musicxml', fp=str(xml_path))
        
        # Add helpful comment to the XML file about the structure
        xml_content = xml_path.read_text()
        
        # Insert comment after XML declaration and DOCTYPE
        comment = """<!--
╔════════════════════════════════════════════════════════════════════════════╗
║ CODEMPOSE MUSICXML EXPORT - STRUCTURE EXPLANATION                          ║
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║ This MusicXML file contains all your musical data correctly.              ║
║                                                                            ║
║ STRUCTURE: Each voice is exported as a separate staff (Part).             ║
║ This is a reliable approach that preserves all musical content.           ║
║                                                                            ║
║ WHY SEPARATE STAVES?                                                      ║
║ - The music21 library has limitations with multi-voice staff grouping     ║
║ - This approach ensures 100% data integrity and reliability               ║
║ - All notes, rhythms, and articulations are preserved correctly           ║
║                                                                            ║
║ MUSESCORE WORKFLOW - COMBINING VOICES:                                    ║
║                                                                            ║
║ Use the "Implode" tool to merge staves into multi-voice staves:          ║
║                                                                            ║
║ 1. Select the measures from BOTH staves you want to combine               ║
║    (Example: Click first measure of Soprano, Shift+Click last of Alto)   ║
║                                                                            ║
║ 2. Go to: Tools → Implode                                                 ║
║                                                                            ║
║ 3. Result: Lower staff moves to Voice 2 on upper staff                    ║
║    (Stem directions adjust automatically)                                 ║
║                                                                            ║
║ 4. Delete the now-empty lower staff                                       ║
║                                                                            ║
║ Repeat for other voice pairs (Tenor + Bass, etc.)                         ║
║                                                                            ║
║ ALTERNATIVE: Use "Hide Empty Staves" (Format → Style → Score)             ║
║                                                                            ║
║ This workflow leverages Codempose's programmatic power while using        ║
║ MuseScore for final layout—the best of both worlds!                       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
-->
"""
        
        # Find where to insert (after DOCTYPE)
        doctype_end = xml_content.find('>', xml_content.find('<!DOCTYPE')) + 1
        if doctype_end > 0:
            xml_content = xml_content[:doctype_end] + '\n' + comment + xml_content[doctype_end:]
            xml_path.write_text(xml_content, encoding='utf-8')
        
        print(f"✅ Successfully exported {xml_path.name}")
        print(f"   📂 Open in MuseScore: {xml_path}")
        print(f"   📊 {len(score.parts)} staves exported (one per voice)")
        print(f"   💡 See XML comment for MuseScore 'Implode' workflow")
    except Exception as e:
        print(f"⚠️ Could not export to MusicXML. Error:\n{e}")
        import traceback
        traceback.print_exc()


def promote_shorthand_to_programmatic(file_path: Path, module) -> bool:
    """
    Convert VOICE_ASSIGNMENTS shorthand to programmatic Python code.
    
    Similar to promote_lilypond_to_tinynotation, this function:
    1. Parses VOICE_ASSIGNMENTS shorthand
    2. Generates equivalent programmatic Python code
    3. Saves it to the file as PROGRAMMATIC_VOICE_GENERATION
    4. Creates backup of original file
    
    Toggle: PROMOTE_TO_PROGRAMMATIC
    - False (default): Use VOICE_ASSIGNMENTS shorthand
    - True: Generate and save programmatic code
    
    Args:
        file_path: Path to the study file
        module: The loaded module
    
    Returns:
        True if promotion succeeded, False otherwise
    """
    import shutil
    from datetime import datetime
    
    print("\n" + "="*60)
    
    # Ensure outputs directory exists
    out_dir = OUTPUTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if programmatic version already exists
    has_programmatic = hasattr(module, 'PROGRAMMATIC_VOICE_GENERATION')
    
    if has_programmatic:
        # Scenario 1: Just toggle dominance
        print("🔄 PROMOTION: Toggling shorthand vs programmatic dominance")
        print("="*60)
        
        current_state = getattr(module, 'PROMOTE_TO_PROGRAMMATIC', False)
        new_state = not current_state
        
        print(f"Current state: PROMOTE_TO_PROGRAMMATIC = {current_state}")
        print(f"New state:     PROMOTE_TO_PROGRAMMATIC = {new_state}")
        print()
        
        if new_state:
            print("📝 Programmatic code will be PROCESSED (dominant)")
            print("📋 Shorthand will be PRESERVED (reference)")
        else:
            print("📋 Shorthand will be PROCESSED (dominant)")
            print("📝 Programmatic code will be PRESERVED (reference)")
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = out_dir / f"{file_path.stem}.{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        
        # Read and modify file
        content = file_path.read_text()
        pattern = r'PROMOTE_TO_PROGRAMMATIC\s*=\s*(True|False)'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, f'PROMOTE_TO_PROGRAMMATIC = {new_state}', content)
        else:
            # Add the toggle near the top (after imports)
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('import') and not line.strip().startswith('from'):
                    insert_pos = i
                    break
            lines.insert(insert_pos, f'\n# Toggle for programmatic dominance\nPROMOTE_TO_PROGRAMMATIC = {new_state}\n')
            new_content = '\n'.join(lines)
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        
        print(f"\n✅ Toggle updated")
        print(f"   Backup: {backup_path}")
        print("="*60 + "\n")
        
        return True
    
    else:
        # Scenario 2: Generate programmatic code from shorthand
        print("🎯 PROMOTION: Generating programmatic code from shorthand")
        print("="*60)
        
        if not hasattr(module, 'VOICE_ASSIGNMENTS'):
            print("❌ No VOICE_ASSIGNMENTS found - cannot promote")
            print("="*60 + "\n")
            return False
        
        voice_assignments = module.VOICE_ASSIGNMENTS
        
        # Generate programmatic code
        prog_code = generate_programmatic_from_shorthand(voice_assignments)
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = out_dir / f"{file_path.stem}.{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        
        # Read original content
        content = file_path.read_text()
        
        # Find insertion point (after VOICE_ASSIGNMENTS)
        lines = content.split('\n')
        insert_pos = len(lines)
        
        # Find end of VOICE_ASSIGNMENTS
        in_assignments = False
        brace_count = 0
        for i, line in enumerate(lines):
            if 'VOICE_ASSIGNMENTS' in line and '=' in line:
                in_assignments = True
                brace_count = line.count('{') - line.count('}')
            elif in_assignments:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    insert_pos = i + 1
                    break
        
        # Insert programmatic code
        prog_section = [
            "",
            "# ============================================================================",
            "# PROGRAMMATIC VOICE GENERATION (auto-generated from VOICE_ASSIGNMENTS)",
            "# ============================================================================",
            "# Toggle: PROMOTE_TO_PROGRAMMATIC = True to use this instead of shorthand",
            "",
            "PROGRAMMATIC_VOICE_GENERATION = '''",
            prog_code,
            "'''",
            ""
        ]
        
        for line in reversed(prog_section):
            lines.insert(insert_pos, line)
        
        # Add toggle at the top if not present
        if 'PROMOTE_TO_PROGRAMMATIC' not in content:
            toggle_lines = [
                "",
                "# Toggle for programmatic dominance (set True to use generated code)",
                "PROMOTE_TO_PROGRAMMATIC = False  # Set True after reviewing generated code",
                ""
            ]
            # Insert after imports
            import_end = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('import') and not line.strip().startswith('from'):
                    import_end = i
                    break
            for line in reversed(toggle_lines):
                lines.insert(import_end, line)
        
        # Write modified content
        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')
        
        # Also save to outputs for inspection
        output_copy = out_dir / file_path.name
        output_copy.write_text(new_content, encoding='utf-8')
        
        print(f"✅ Programmatic code generated and saved")
        print(f"   Backup: {backup_path}")
        print(f"   Modified: {file_path}")
        print(f"   Copy: {output_copy}")
        print()
        print("📋 Review the generated PROGRAMMATIC_VOICE_GENERATION code")
        print("   Then set PROMOTE_TO_PROGRAMMATIC = True to use it")
        print("="*60 + "\n")
        
        return True


def generate_programmatic_from_shorthand(voice_assignments: dict) -> str:
    """
    Generate programmatic Python code from VOICE_ASSIGNMENTS shorthand.
    
    This converts shorthand like:
        'Soprano': 'THEME + transpose(THEME, 7)'
    
    To programmatic code like:
        soprano_events = (
            voice_lookup['THEME'] +
            transpose_events(voice_lookup['THEME'], 7)
        )
    
    Args:
        voice_assignments: The VOICE_ASSIGNMENTS dictionary
    
    Returns:
        String of Python code
    """
    lines = []
    lines.append("def build_score_data_programmatic():")
    lines.append('    """')
    lines.append('    Auto-generated programmatic version of VOICE_ASSIGNMENTS.')
    lines.append('    ')
    lines.append('    This code was generated from the shorthand and can be modified.')
    lines.append('    Set PROMOTE_TO_PROGRAMMATIC = True to use this version.')
    lines.append('    """')
    lines.append('    from lilypond_parser import parse_lilypond_to_data')
    lines.append('    from composition_shorthand import transpose_events, invert_events, retrograde_events')
    lines.append('    ')
    lines.append('    # Parse all voice snippets (add your snippet parsing here)')
    lines.append('    # Example:')
    lines.append('    # theme_data = parse_lilypond_to_data(THEME_LILY, part_name="Theme")')
    lines.append('    # voice_lookup = {"THEME": theme_data["parts"]["Theme"]}')
    lines.append('    ')
    lines.append('    voice_lookup = {}  # TODO: Add your snippet parsing')
    lines.append('    ')
    
    # Generate code for each staff and voice
    for staff_name, voices in voice_assignments.items():
        lines.append(f'    # {staff_name} Staff')
        
        if isinstance(voices, dict):
            for voice_name, expression in voices.items():
                var_name = f"{voice_name.lower().replace(' ', '_')}_events"
                lines.append(f'    ')
                lines.append(f'    # {voice_name}: {expression}')
                
                # Parse the expression and generate code
                prog_expr = convert_expression_to_programmatic(expression)
                lines.append(f'    {var_name} = {prog_expr}')
        else:
            # Single voice (not a dict)
            var_name = f"{staff_name.lower().replace(' ', '_')}_events"
            lines.append(f'    ')
            lines.append(f'    # {staff_name}: {voices}')
            prog_expr = convert_expression_to_programmatic(voices)
            lines.append(f'    {var_name} = {prog_expr}')
        
        lines.append('    ')
    
    # Build final score_data
    lines.append('    # Assemble final score_data')
    lines.append('    score_data = {')
    lines.append('        "metadata": {')
    lines.append('            "title": "Your Title",  # TODO: Set your title')
    lines.append('            "composer": "Your Name",  # TODO: Set your composer')
    lines.append('        },')
    lines.append('        "parts": {')
    
    for staff_name, voices in voice_assignments.items():
        if isinstance(voices, dict):
            lines.append(f'            "{staff_name}": {{')
            for voice_name in voices.keys():
                var_name = f"{voice_name.lower().replace(' ', '_')}_events"
                lines.append(f'                "{voice_name}": {var_name},')
            lines.append('            },')
        else:
            var_name = f"{staff_name.lower().replace(' ', '_')}_events"
            lines.append(f'            "{staff_name}": {var_name},')
    
    lines.append('        }')
    lines.append('    }')
    lines.append('    ')
    lines.append('    return score_data')
    
    return '\n'.join(lines)


def convert_expression_to_programmatic(expression: str) -> str:
    """
    Convert shorthand expression to programmatic Python code.
    
    Examples:
        'THEME' -> 'voice_lookup["THEME"]'
        'THEME * 3' -> 'voice_lookup["THEME"] * 3'
        'THEME + VAR' -> 'voice_lookup["THEME"] + voice_lookup["VAR"]'
        'transpose(THEME, 7)' -> 'transpose_events(voice_lookup["THEME"], 7)'
        'invert(THEME)' -> 'invert_events(voice_lookup["THEME"])'
        'retrograde(THEME)' -> 'retrograde_events(voice_lookup["THEME"])'
    """
    # Split by + for chaining
    parts = [p.strip() for p in expression.split('+')]
    prog_parts = []
    
    for part in parts:
        # Check for transformation functions
        if '(' in part and ')' in part:
            func_match = re.match(r'(\w+)\((.*)\)', part)
            if func_match:
                func_name = func_match.group(1)
                args_str = func_match.group(2)
                args = [a.strip() for a in args_str.split(',')]
                
                # Convert function name
                if func_name in ['transpose', 'invert', 'retrograde']:
                    func_name_prog = f'{func_name}_events'
                else:
                    func_name_prog = func_name
                
                # Convert arguments
                prog_args = []
                for arg in args:
                    if arg.isdigit() or (arg.startswith('-') and arg[1:].isdigit()):
                        # Numeric argument
                        prog_args.append(arg)
                    elif arg.startswith("'") or arg.startswith('"'):
                        # String argument
                        prog_args.append(arg)
                    else:
                        # Voice name
                        prog_args.append(f'voice_lookup["{arg}"]')
                
                prog_parts.append(f'{func_name_prog}({", ".join(prog_args)})')
        
        # Check for repetition
        elif '*' in part:
            voice_name, count = [x.strip() for x in part.split('*')]
            prog_parts.append(f'voice_lookup["{voice_name}"] * {count}')
        
        # Simple voice reference
        else:
            prog_parts.append(f'voice_lookup["{part}"]')
    
    # Join with +
    if len(prog_parts) == 1:
        return prog_parts[0]
    else:
        return '(\n        ' + ' +\n        '.join(prog_parts) + '\n    )'


def promote_lilypond_to_tinynotation(file_path: Path, module) -> bool:
    """
    Toggle format dominance: switch which format (LILY or TINY) gets processed.
    
    This function handles two scenarios:
    
    1. If SOURCE_MELODY_TINY exists: Toggle PROMOTE_TO_TINYNOTATION
       - True = TinyNotation is dominant (gets processed)
       - False = LilyPond is dominant (gets processed)
    
    2. If SOURCE_MELODY_TINY missing: Generate it from LILY and enable toggle
       - Converts SOURCE_MELODY_LILY to TinyNotation
       - Adds SOURCE_MELODY_TINY to the file
       - Enables PROMOTE_TO_TINYNOTATION
    
    File management:
    - Original file → outputs/filename.TIMESTAMP.bak (before modification)
    - Modified file → root directory (replaces original)
    - Modified file → outputs/filename.py (for inspection)
    
    Args:
        file_path: Path to the study file
        module: The loaded module
    
    Returns:
        True if promotion succeeded, False otherwise
    """
    from lily_to_tiny import lily_to_tiny_notation
    import shutil
    from datetime import datetime
    
    print("\n" + "="*60)
    
    # Ensure outputs directory exists
    out_dir = OUTPUTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if TinyNotation already exists
    has_tiny = hasattr(module, 'SOURCE_MELODY_TINY')
    
    if has_tiny:
        # Scenario 1: Just toggle dominance
        print("🔄 PROMOTION: Toggling format dominance")
        print("="*60)
        
        current_state = getattr(module, 'PROMOTE_TO_TINYNOTATION', False)
        new_state = not current_state
        
        print(f"Current: {'TinyNotation' if current_state else 'LilyPond'} is dominant")
        print(f"New: {'TinyNotation' if new_state else 'LilyPond'} will be dominant")
        
        # Copy ORIGINAL file to outputs as backup BEFORE modification
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{file_path.stem}.{timestamp}.bak"
        backup_path = out_dir / backup_filename
        shutil.copy2(file_path, backup_path)
        print(f"💾 Original copied to: outputs/{backup_filename}")
        
        # Toggle the flag in the file
        original_content = file_path.read_text()
        new_content = original_content.replace(
            f'PROMOTE_TO_TINYNOTATION = {current_state}',
            f'PROMOTE_TO_TINYNOTATION = {new_state}'
        )
        
        # Write MODIFIED file to root (replaces original)
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Modified file written to: {file_path.name} (root)")
        
        # Copy MODIFIED file to outputs for inspection
        modified_output_path = out_dir / file_path.name
        shutil.copy2(file_path, modified_output_path)
        print(f"📋 Modified file copied to: outputs/{file_path.name}")
        
        print("="*60 + "\n")
        return True
    
    else:
        # Scenario 2: Generate TinyNotation from LilyPond
        print("🔄 PROMOTION: Generating TinyNotation from LilyPond")
        print("="*60)
        
        lily_source = getattr(module, 'SOURCE_MELODY_LILY', None)
        if not lily_source:
            print("❌ No SOURCE_MELODY_LILY found in module")
            return False
        
        print(f"📝 Converting: {lily_source[:60]}...")
        
        # Convert to TinyNotation
        result = lily_to_tiny_notation(lily_source)
        if not result.success:
            print(f"❌ Conversion failed: {result.error}")
            return False
        
        tiny_notation = result.tiny_notation
        print(f"✅ TinyNotation: {tiny_notation}")
        
        # Copy ORIGINAL file to outputs as backup BEFORE modification
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{file_path.stem}.{timestamp}.bak"
        backup_path = out_dir / backup_filename
        shutil.copy2(file_path, backup_path)
        print(f"💾 Original copied to: outputs/{backup_filename}")
        
        # Read the original file
        original_content = file_path.read_text()
        
        # Build the new content
        new_lines = []
        toggle_enabled = False
        tiny_added = False
        
        for line in original_content.split('\n'):
            # Enable the promotion toggle
            if 'PROMOTE_TO_TINYNOTATION' in line and '=' in line and 'False' in line and not toggle_enabled:
                new_lines.append('PROMOTE_TO_TINYNOTATION = True  # TinyNotation is now dominant')
                toggle_enabled = True
                continue
            
            # Add SOURCE_MELODY_TINY right after SOURCE_MELODY_LILY definition ends
            if '""".strip()' in line and 'SOURCE_MELODY_LILY' in '\n'.join(new_lines[-10:]) and not tiny_added:
                new_lines.append(line)
                new_lines.append('')
                new_lines.append('# TinyNotation equivalent (for visual comparison with LilyPond)')
                new_lines.append('# PROMOTE_TO_TINYNOTATION toggle controls which format is dominant (gets processed)')
                new_lines.append(f'SOURCE_MELODY_TINY = "{tiny_notation}"')
                tiny_added = True
                continue
            
            # Keep all other lines unchanged
            new_lines.append(line)
        
        # Write MODIFIED content to root (replaces original)
        new_content = '\n'.join(new_lines)
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Modified file written to: {file_path.name} (root)")
        
        # Copy MODIFIED file to outputs for inspection
        modified_output_path = out_dir / file_path.name
        with open(modified_output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"📋 Modified file copied to: outputs/{file_path.name}")
        
        print(f"   - PROMOTE_TO_TINYNOTATION enabled (TinyNotation is dominant)")
        print(f"   - SOURCE_MELODY_LILY preserved (for visual correlation)")
        print(f"   - SOURCE_MELODY_TINY added (will be processed)")
        print("="*60 + "\n")
        
        return True


def run_pipeline_from_file(file_path_str: str):
    """
    Central pipeline orchestrator - the "three stations" approach.
    
    This function implements flexible input handling with priority order:
    1. build_score_data() function - for programmatic composition
    2. SOURCE_MELODY_TINY variable - for TinyNotation strings (promoted)
    3. SOURCE_MELODY_LILY variable - for raw LilyPond strings
    4. build_part() function - for music21.Part generation
    
    The result is automatically engraved to PDF/MIDI in the outputs/ directory.
    
    Special feature: PROMOTE_TO_TINYNOTATION toggle
    If a study file sets PROMOTE_TO_TINYNOTATION = True, this function will:
    - Convert SOURCE_MELODY_LILY to TinyNotation
    - Create a backup of the original file
    - Rewrite the file with SOURCE_MELODY_TINY
    - Disable the promotion toggle
    
    Args:
        file_path_str: Path to the study file (usually __file__ from the caller)
    """
    import importlib.util
    import re
    from pathlib import Path
    
    # Resolve file path
    file_path = Path(file_path_str).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"Study file not found: {file_path}")
    
    # Derive output basename from filename (e.g., first.py → first)
    output_basename = file_path.stem
    
    print(f"\n{'='*60}")
    print(f"🎵 CODEMPOSE PIPELINE")
    print(f"{'='*60}")
    print(f"Study file: {file_path.name}")
    print(f"Output: outputs/{output_basename}.*")
    print(f"{'='*60}\n")
    
    # Load the study file as a Python module
    spec = importlib.util.spec_from_file_location(file_path.stem, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Check for SHORTHAND promotion toggle FIRST
    promote_shorthand_toggle = getattr(module, 'PROMOTE_TO_PROGRAMMATIC', False)
    if promote_shorthand_toggle:
        promotion_success = promote_shorthand_to_programmatic(file_path, module)
        if promotion_success:
            print("⚠️  File has been promoted. Please re-run to process the new programmatic code.")
            print("="*60 + "\n")
            return  # Exit early - user should re-run
        else:
            print("⚠️  Shorthand promotion failed. Continuing with normal processing...")
            print("="*60 + "\n")
    
    # Check for TINYNOTATION promotion toggle SECOND
    promote_toggle = getattr(module, 'PROMOTE_TO_TINYNOTATION', False)
    if promote_toggle:
        promotion_success = promote_lilypond_to_tinynotation(file_path, module)
        if promotion_success:
            print("⚠️  File has been promoted. Please re-run to process the new TinyNotation format.")
            print("="*60 + "\n")
            return  # Exit early - user should re-run
        else:
            print("⚠️  Promotion failed. Continuing with normal processing...")
            print("="*60 + "\n")
    
    score_data = None
    input_type = None
    
    # Station 1: Try build_score_data() - highest priority
    if hasattr(module, 'build_score_data'):
        print("📊 Found build_score_data() function")
        input_type = "build_score_data"
        try:
            result = module.build_score_data()
            # Handle case where build_score_data returns score_data dict
            if isinstance(result, dict) and 'parts' in result:
                score_data = result
                
                # Auto-extract LilyPond snippets from module for .ly header documentation
                # Look for variables ending with _LILY in the module namespace
                original_snippets = {}
                for attr_name in dir(module):
                    if attr_name.endswith('_LILY') and not attr_name.startswith('_'):
                        snippet_value = getattr(module, attr_name)
                        if isinstance(snippet_value, str):
                            # Remove the _LILY suffix for cleaner display
                            snippet_key = attr_name[:-5]  # Remove '_LILY'
                            original_snippets[snippet_key] = snippet_value
                
                # Add to metadata if snippets were found and not already present
                if original_snippets and 'original_snippets' not in score_data.get('metadata', {}):
                    if 'metadata' not in score_data:
                        score_data['metadata'] = {}
                    score_data['metadata']['original_snippets'] = original_snippets
                    print(f"   📝 Auto-extracted {len(original_snippets)} LilyPond snippets for .ly header")
                
            # Handle case where it returns a music21.Part
            elif hasattr(result, '__class__') and 'Part' in result.__class__.__name__:
                print("   Converting Part to score_data...")
                from music_data import extract_data_from_part
                events = extract_data_from_part(result)
                score_data = {
                    'metadata': {'title': output_basename},
                    'parts': {'Main': events}
                }
            else:
                raise ValueError(f"build_score_data() returned unexpected type: {type(result)}")
        except Exception as e:
            print(f"❌ Error executing build_score_data(): {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # Station 2: Try SOURCE_MELODY_TINY - second priority (promoted TinyNotation)
    elif hasattr(module, 'SOURCE_MELODY_TINY'):
        print("🎹 Found SOURCE_MELODY_TINY variable (promoted TinyNotation)")
        input_type = "SOURCE_MELODY_TINY"
        tiny_string = getattr(module, 'SOURCE_MELODY_TINY')
        print(f"   TinyNotation input: {tiny_string[:60]}...")
        
        # Parse metadata header from TinyNotation string
        # Format: "time=6/4 key=Cmajor tempo=90 c4 d4 e4 f4..."
        import music21
        import re
        from music_data import extract_data_from_part
        
        try:
            # Extract metadata header (key=value pairs at the start)
            metadata = {
                'title': output_basename,
                'source_format': 'TinyNotation (promoted)'
            }
            
            # Pattern to match key=value pairs at the beginning
            # Matches: time=6/4, key=Cmajor, tempo=90
            header_pattern = r'^((?:\w+=[\w/]+\s+)*)'
            header_match = re.match(header_pattern, tiny_string)
            
            notes_string = tiny_string  # Default: use whole string
            
            if header_match and header_match.group(1).strip():
                header_str = header_match.group(1).strip()
                print(f"   Detected metadata header: {header_str}")
                
                # Remove header from notes string
                notes_string = tiny_string[len(header_match.group(1)):].strip()
                
                # Parse key=value pairs
                for pair in header_str.split():
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        
                        if key == 'time':
                            # time=6/4
                            metadata['time_signature'] = value
                        
                        elif key == 'key':
                            # key=Cmajor or key=Dminor
                            # Parse to extract tonic and mode
                            # "Cmajor" -> tonic="C", mode="major"
                            match = re.match(r'([A-G][#b]?)(\w+)', value)
                            if match:
                                tonic = match.group(1).lower()  # "C" -> "c"
                                mode = match.group(2).lower()   # "major" -> "major"
                                metadata['key_signature'] = {
                                    'tonic': tonic,
                                    'mode': mode
                                }
                        
                        elif key == 'tempo':
                            # tempo=90
                            try:
                                bpm = int(value)
                                metadata['tempo'] = {
                                    'beat_duration': 4,  # Default to quarter note
                                    'bpm': bpm
                                }
                            except ValueError:
                                pass  # Ignore invalid tempo values
            
            # Add time signature to notes string for music21 if present
            if 'time_signature' in metadata:
                notes_string = f"{metadata['time_signature']} {notes_string}"
            
            print(f"   Notes string for music21: {notes_string[:60]}...")
            
            # Parse TinyNotation with music21
            tiny_obj = music21.converter.parse(f"tinynotation: {notes_string}")
            part = music21.stream.Part()
            
            # Extract notes and rests
            for element in tiny_obj.flatten().notesAndRests:
                part.append(element)
            
            # Extract time signature if present (music21 may have added it)
            for ts in tiny_obj.flatten().getElementsByClass(music21.meter.TimeSignature):
                if not part.getElementsByClass(music21.meter.TimeSignature):
                    part.insert(0, ts)
                break
            
            # Convert to score_data
            events = extract_data_from_part(part)
            score_data = {
                'metadata': metadata,
                'parts': {'Melody': events}
            }
            
        except Exception as e:
            print(f"❌ Error parsing SOURCE_MELODY_TINY: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # Station 3: Try SOURCE_MELODY_LILY - third priority
    elif hasattr(module, 'SOURCE_MELODY_LILY'):
        print("📝 Found SOURCE_MELODY_LILY variable")
        input_type = "SOURCE_MELODY_LILY"
        lily_string = getattr(module, 'SOURCE_MELODY_LILY')
        print(f"   LilyPond input: {lily_string[:60]}...")
        
        # Use the integrated parser
        from lilypond_parser import parse_lilypond_to_data
        try:
            score_data = parse_lilypond_to_data(lily_string, part_name='Melody')
            # Update title if not set
            if 'metadata' not in score_data:
                score_data['metadata'] = {}
            if 'title' not in score_data['metadata']:
                score_data['metadata']['title'] = output_basename
        except Exception as e:
            print(f"❌ Error parsing SOURCE_MELODY_LILY: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # Station 4: Try build_part() - fourth priority
    elif hasattr(module, 'build_part'):
        print("🎼 Found build_part() function")
        input_type = "build_part"
        try:
            part = module.build_part()
            print("   Converting Part to score_data...")
            from music_data import extract_data_from_part
            events = extract_data_from_part(part)
            score_data = {
                'metadata': {'title': output_basename},
                'parts': {'Main': events}
            }
        except Exception as e:
            print(f"❌ Error executing build_part(): {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # No valid entry point found
    else:
        raise AttributeError(
            f"Study file {file_path.name} must contain one of:\n"
            f"  1. build_score_data() function (highest priority)\n"
            f"  2. SOURCE_MELODY_TINY variable (promoted TinyNotation)\n"
            f"  3. SOURCE_MELODY_LILY variable (raw LilyPond)\n"
            f"  4. build_part() function\n\n"
            f"Tip: Set PROMOTE_TO_TINYNOTATION = True to auto-convert LilyPond to TinyNotation"
        )
    
    # Display what we found
    print(f"✅ Successfully loaded via: {input_type}")
    print(f"   Metadata: {score_data.get('metadata', {})}")
    print(f"   Parts: {list(score_data.get('parts', {}).keys())}")
    
    # Show warnings if any
    warnings = score_data.get('metadata', {}).get('warnings', [])
    if warnings:
        print(f"\n⚠️  Parser warnings:")
        for w in warnings:
            print(f"   - {w}")
    
    print()
    
    # Station 4: Engrave (pass source file for copying to outputs)
    engrave_with_abjad(score_data, output_basename, source_file=str(file_path))
    
    # Station 5: Export to MusicXML for MuseScore
    print()
    export_to_musicxml(score_data, output_basename)
    
    print(f"\n{'='*60}")
    print(f"✅ PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"Generated files:")
    print(f"  • outputs/{output_basename}.ly        (LilyPond source)")
    print(f"  • outputs/{output_basename}.pdf       (Musical score)")
    print(f"  • outputs/{output_basename}.midi      (Audio playback)")
    print(f"  • outputs/{output_basename}.musicxml  (MuseScore import)")
    print(f"{'='*60}\n")