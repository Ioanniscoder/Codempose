# project_template.py

import music21
import abjad
from pathlib import Path
import subprocess
import re
from fractions import Fraction

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
        
        # Show LilyPond snippets
        if original_snippets:
            lines.append("% LilyPond Format:")
            for name, snippet in sorted(original_snippets.items()):
                lines.append(f"%   {name}:")
                lines.append(f"%     {snippet}")
                lines.append("%")
        
        # Show TinyNotation equivalents
        if tinynotation_snippets:
            lines.append("% TinyNotation Format:")
            for name, snippet in sorted(tinynotation_snippets.items()):
                lines.append(f"%   {name}:")
                lines.append(f"%     {snippet}")
                lines.append("%")
    
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
    # USAGE INSTRUCTIONS
    # ========================================
    if has_content:
        lines.extend([
            "% ========================================",
            "% HOW TO USE",
            "% ========================================",
            "% - Copy any snippet above into a new study file",
            "% - Use shorthand expressions as templates",
            "% - Programmatic voices can be edited or transformed",
            "% ========================================",
            "",
        ])
    
    return "\n".join(lines) if has_content else ""


def engrave_with_abjad(score_data: dict, output_basename: str, source_file: str = None):
    print(f"🎶 Engraving '{score_data.get('metadata', {}).get('title', '')}'...")
    out_dir = Path('outputs'); out_dir.mkdir(parents=True, exist_ok=True)
    ly_path = out_dir / f"{output_basename}.ly"
    title = score_data.get('metadata', {}).get('title', output_basename)
    metadata = score_data.get('metadata', {})
    
    # Copy source study file to outputs for inspection (always, for visual correlation)
    if source_file:
        source_path = Path(source_file)
        if source_path.exists():
            dest_path = out_dir / source_path.name
            import shutil
            shutil.copy2(source_path, dest_path)
            print(f"📋 Copied {source_path.name} to outputs/ (shows both LILY and TINY formats)")

    staves = []
    # Note: reverse=True ensures correct staff order (Melody at top, Harmony at bottom)
    # LilyPond renders staves in reverse vertical order, so we reverse alphabetical sort
    for part_name, events_or_voices in sorted(score_data.get('parts', {}).items(), reverse=True):
        # Check if this is a multi-voice part (dict) or single-voice (list)
        is_multi_voice = isinstance(events_or_voices, dict)
        
        if is_multi_voice:
            # Multi-voice polyphonic structure: dict of voice names to event lists
            voice_bodies = []
            for voice_name, events in events_or_voices.items():
                voice_tokens = []
                for ev in events:
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
                        voice_tokens.append(f"{pitch_text}{dur_str}")
                voice_body = " ".join(voice_tokens)
                voice_bodies.append(f"{{ {voice_body} }}")
            
            # Combine voices with LilyPond polyphonic syntax: << {...} \\ {...} >>
            separator = ' \\\\ '
            body = f"<< {separator.join(voice_bodies)} >>"
        else:
            # Single-voice structure: list of events (backward compatible)
            events = events_or_voices
            part_tokens = []
            for ev in events:
                ql = ev.get('ql', 1.0)
                dur_str = ql_to_lily_duration_string(ql)
                if ev.get('type') == 'rest':
                    part_tokens.append(f"r{dur_str}")
                elif ev.get('type') == 'barline':
                    # Handle bar line markers
                    style = ev.get('style', '||')
                    part_tokens.append(f"\\bar \"{style}\"")
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
                    part_tokens.append(f"{pitch_text}{dur_str}")
            body = " ".join(part_tokens)
        
        clef = "bass" if "harmony" in part_name.lower() else "treble"
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
            staff_content = f"\\new Staff {{\n  \\clef {clef}\n  {directives_str}\n  {body}\n}}"
        else:
            staff_content = f"\\new Staff {{\n  \\clef {clef}\n  {body}\n}}"
        staves.append(staff_content)
    score_block = f"<<\n{''.join(staves)}\n>>" if len(staves) > 1 else staves[0]

    # Build comprehensive documentation block
    comment_section = _build_documentation_block(metadata, source_file)

    ly_content = f'\\version "2.24.1"\n{comment_section}\\header {{ title = "{title}" }}\n\\score {{\n  {score_block}\n  \\layout {{ }}\n  \\midi {{ }}\n}}'
    ly_path.write_text(ly_content)
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
    for part_name, part_content in score_data.get('parts', {}).items():
        if isinstance(part_content, dict):
            # Multi-voice part (e.g., {'Soprano': [...], 'Alto': [...]})
            # Each voice becomes a separate staff in MusicXML
            for voice_name, voice_events in sorted(part_content.items()):
                voice_part = data_to_part(voice_events, metadata)
                voice_part.id = f"{part_name}_{voice_name}"
                voice_part.partName = f"{part_name} - {voice_name}"
                score.insert(0, voice_part)
            
        else:
            # Single-voice part (just a list of events)
            part = data_to_part(part_content, metadata)
            part.id = part_name
            part.partName = part_name
            score.insert(0, part)
    
    # Write the file
    out_dir = Path('outputs')
    out_dir.mkdir(parents=True, exist_ok=True)
    xml_path = out_dir / f"{output_basename}.musicxml"
    
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
            xml_path.write_text(xml_content)
        
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
    out_dir = Path('outputs')
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
        file_path.write_text(new_content)
        
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
        file_path.write_text(new_content)
        
        # Also save to outputs for inspection
        output_copy = out_dir / file_path.name
        output_copy.write_text(new_content)
        
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
    out_dir = Path('outputs')
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
        file_path.write_text(new_content)
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
        file_path.write_text(new_content)
        print(f"✅ Modified file written to: {file_path.name} (root)")
        
        # Copy MODIFIED file to outputs for inspection
        modified_output_path = out_dir / file_path.name
        with open(modified_output_path, 'w') as f:
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