"""
Score Builder: Blueprint String Framework
==========================================

Composer-centric shorthand for assembling multi-stave scores using
blueprint strings with intuitive delimiters.

NEW: Supports on-the-fly transformations in blueprint strings!

TRANSFORMATION SYNTAX (HYBRID MODEL):
-------------------------------------

1. NO SUFFIX (for single-part transformations):
   transpose_part(THEME, 'P5')
   → Returns single part, auto-caches with .id = 'melody'
   → Backward compatible with existing studies

2. SUFFIX (for multi-part transformations):
   harmonize_part(MELODY, 'I-IV-V-I'):melody
   harmonize_part(MELODY, 'I-IV-V-I'):harmony
   → Runs once, caches all named parts
   → Second call is a simple lookup

3. ERROR HANDLING:
   harmonize_part(MELODY, 'I-IV-V-I')  [no suffix]
   → ERROR: "Multi-part transformation requires suffix"
   → Prevents ambiguity

Example:
    VOICE_STAVE_DEF = "Melody & Bass"
    
    VOICE_STAVE_DATA = '''
        transpose_part(THEME, 'P5') & BASS;
        harmonize_part(MELODY, 'I-V-I'):melody & harmonize_part(MELODY, 'I-V-I'):harmony
    '''

SNIPPET MARKS (Structural Labels):
-----------------------------------
Uppercase snippet names (e.g., THEME_A, INTRO, CODA) automatically appear
as text marks in the PDF output for navigation and structural clarity.
Lowercase names (e.g., bass_figure) are internal and don't generate marks.
"""

from typing import Dict, List, Any, Optional
import re
import music21

# Import transformation functions and data conversion utilities
from src import transformations
from src.music_data import data_to_part, extract_data_from_part, part_to_data


# ============================================================================
# SNIPPET MARK VISIBILITY
# ============================================================================

def _extract_clean_music_content(lily_source: str, strip_marks: bool = True) -> str:
    """
    Extract music content from LilyPond snippet with SMART directive stripping.
    
    STRATEGY:
    - Strips ONLY initial directives (\\key, \\time, \\tempo, \\clef, \\mark)
      that appear BEFORE any musical content
    - Preserves mid-snippet changes (intentional key/time/tempo changes)
    - Always strips \\mark if strip_marks=True (handled by auto-injection logic)
    
    Example:
        \\relative c' {
            \\key c \\major    # <- STRIPPED (initial)
            \\time 4/4        # <- STRIPPED (initial)
            c4 d e f |        # <- KEPT
            \\time 3/4        # <- KEPT (mid-snippet change!)
            g4 a b |          # <- KEPT
        }
    
    Args:
        lily_source: Original LilyPond snippet string
        strip_marks: If True, remove ALL \\mark directives (default True)
    
    Returns:
        Cleaned music content string
    """
    import re
    
    # Extract content from \\relative { ... }
    match = re.search(r'\\relative\s+[^\{]*\{(.*)\}', lily_source, re.DOTALL)
    if not match:
        return ""
    
    content = match.group(1).strip()
    lines = content.split('\n')
    
    cleaned_lines = []
    found_music = False  # Track when we've seen actual music content
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this line is a directive
        is_directive = (
            stripped.startswith('\\key ') or
            stripped.startswith('\\time ') or
            stripped.startswith('\\tempo ') or
            stripped.startswith('\\clef ')
        )
        
        is_mark = stripped.startswith('\\mark ')
        
        # Check if line has musical content (notes/rests)
        # Pattern: note letter followed by duration number (e.g., "c4", "fis8", "r2")
        # Must have a digit after the note name to avoid matching directive keywords
        has_music = bool(re.search(r'[a-gr][is]*\d+', stripped))
        
        if has_music:
            found_music = True
        
        # Decision logic:
        if is_mark and strip_marks:
            # Always strip marks (handled by auto-injection)
            continue
        elif is_directive and not found_music:
            # Strip INITIAL directives (before any music)
            continue
        else:
            # Keep everything else (including mid-snippet directives)
            cleaned_lines.append(line)
    
    # Clean up excessive blank lines
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n\s*\n+', '\n', result)
    result = result.strip()
    
    return result


def __get_snippet_mark_text(snippet_name: str) -> str:
    """
    Determines the text for a snippet mark based on the underscore convention.
    Returns everything after the first underscore, or None if no underscore exists
    or if it's a repeat (*) or transformation (contains parentheses).

    Convention:
    - Snippet name MUST contain at least one underscore (_) to be visible
    - Must NOT contain parentheses (transformations are hidden)
    - Must NOT contain asterisk (repeats are hidden)
    - Text displayed is everything AFTER the first underscore
    - Characters like - and : are allowed in the displayed text
    
    Examples:
        "m1_intro"              → "intro"
        "m1_m1"                 → "m1"
        "m2_transform-m1"       → "transform-m1"
        "m2_m2:transform-m1"    → "m2:transform-m1"
        "THEME_A"               → "A"
        "m1"                    → None (no underscore)
        "transpose_part(m1)"    → None (contains parentheses)
        "_internal_use"         → "internal_use"
        "m3_repeat * 2"         → None (contains *)
        "prefix_"               → None (empty suffix)
    """
    # Must contain underscore, and not be a repeat or transformation
    if '_' not in snippet_name or '*' in snippet_name or '(' in snippet_name or ')' in snippet_name:
        return None
    
    # Split only on the *first* underscore
    parts = snippet_name.split('_', 1)
    if len(parts) < 2:
        return None  # Should not happen if '_' is present
    
    # Return everything after the first underscore
    suffix = parts[1]
    
    # Avoid returning empty string if name is like "prefix_"
    return suffix if suffix else None


def snippet_contains_explicit_mark(lily_string: str) -> bool:
    """
    Check if snippet already contains a \\mark directive.
    
    This allows composers to override automatic mark injection by
    placing explicit marks in their LilyPond snippets.
    
    Examples:
        r'\\mark "Intro" c2 d2'              → True
        r'\\mark \\default c2'                → True
        r'\\mark \\markup { ... } c2'        → True
        r'd4 e4 f4 g4'                       → False
        r'% \\mark "commented" d4'           → False (comment)
    """
    # Remove comments first (% to end of line)
    cleaned = re.sub(r'%.*$', '', lily_string, flags=re.MULTILINE)
    
    # Match \mark followed by:
    # - quoted string: \mark "text"
    # - \default: \mark \default
    # - \markup: \mark \markup { ... }
    pattern = r'\\mark\s+(".*?"|\\\w+)'
    return bool(re.search(pattern, cleaned))


def extract_snippet_names_from_blueprint(voice_stave_data: str) -> List[str]:
    """
    Automatically extract all snippet names referenced in blueprint strings.
    
    This allows Station 1 to only define snippets and blueprint,
    without needing the redundant snippets_to_parse dictionary.
    
    Extracts:
    - Direct snippet references: THEME_A, BASS_FIGURE
    - Snippet names in transformations: transpose_part(THEME_A, 'P5')
    - Ignores: 'r' (rest placeholder), repetitions (THEME * 2)
    
    Args:
        voice_stave_data: Blueprint string with sections/staves/snippets
        
    Returns:
        List of unique snippet names in order of first appearance
        
    Examples:
        >>> extract_snippet_names_from_blueprint('''
        ...     THEME_A & BASS;
        ...     transpose_part(THEME_A, 'P5') & BASS
        ... ''')
        ['THEME_A', 'BASS']
        
        >>> extract_snippet_names_from_blueprint('''
        ...     INTRO;
        ...     harmonize_part(MELODY, 'I-V'):melody & harmonize_part(MELODY, 'I-V'):harmony
        ... ''')
        ['INTRO', 'MELODY']
    """
    snippet_names = []
    seen = set()
    
    # Remove comments (# to end of line)
    cleaned = re.sub(r'#.*$', '', voice_stave_data, flags=re.MULTILINE)
    
    # Pattern 1: Transformation function calls - extract first argument
    # Matches: transpose_part(SNIPPET_NAME, ...), harmonize_part(SNIPPET_NAME, ...)
    transformation_pattern = r'\w+_part\s*\(\s*([A-Z_][A-Z0-9_]*)'
    for match in re.finditer(transformation_pattern, cleaned):
        name = match.group(1)
        if name not in seen and name != 'R':  # Exclude 'R' (rest)
            snippet_names.append(name)
            seen.add(name)
    
    # Pattern 2: Direct snippet references (uppercase identifiers)
    # Matches: THEME_A, BASS_FIGURE, etc.
    # Excludes: lowercase, already in transformations, inside parentheses
    # Split by delimiters: ;, &, |, ,
    for line in cleaned.split('\n'):
        # Remove everything inside parentheses (transformations already handled)
        no_parens = re.sub(r'\([^)]*\)', '', line)
        
        # Split by blueprint delimiters
        tokens = re.split(r'[;&|,]', no_parens)
        
        for token in tokens:
            token = token.strip()
            
            # Skip empty, rest placeholder, repetitions
            if not token or token == 'r' or '*' in token:
                continue
            
            # Skip transformation suffixes (:melody, :harmony)
            if ':' in token:
                continue
                
            # Match uppercase identifier (snippet name convention)
            if re.match(r'^[A-Z_][A-Z0-9_]*$', token):
                if token not in seen:
                    snippet_names.append(token)
                    seen.add(token)
    
    return snippet_names


def _calculate_accurate_duration(events: List[Dict], snippet_names: List[str], metadata: Dict) -> float:
    """
    Calculate accurate duration using barline-based method for original snippets.
    Falls back to event summing for complex cases.
    
    Args:
        events: List of event dictionaries
        snippet_names: List of snippet names that comprise these events
        metadata: Metadata dict containing 'original_snippets' with LilyPond source
    
    Returns:
        Total duration in quarter lengths
    """
    from snippet_utils import calculate_snippet_duration_from_barlines
    
    # If we have a single snippet (original, transformed, or repeated), try barline counting
    if len(snippet_names) == 1:
        snippet_name = snippet_names[0]
        
        # Case 1: Original snippet (no transformation or repeat)
        if '(' not in snippet_name and '*' not in snippet_name:
            original_snippets = metadata.get('original_snippets', {})
            lily_source = original_snippets.get(snippet_name, '')
            
            if lily_source:
                duration_info = calculate_snippet_duration_from_barlines(lily_source)
                if duration_info and 'total_ql' in duration_info:
                    print(f"         (Using barline-based: {duration_info['total_ql']} QL from {duration_info['bars']} bars)")
                    return duration_info['total_ql']
        
        # Case 2: Repetition like "THEME_A * 2"
        elif '*' in snippet_name and '(' not in snippet_name:
            parts = snippet_name.split('*')
            if len(parts) == 2:
                base_name = parts[0].strip()
                try:
                    repeat_count = int(parts[1].strip())
                    original_snippets = metadata.get('original_snippets', {})
                    lily_source = original_snippets.get(base_name, '')
                    
                    if lily_source:
                        duration_info = calculate_snippet_duration_from_barlines(lily_source)
                        if duration_info and 'total_ql' in duration_info:
                            total = duration_info['total_ql'] * repeat_count
                            print(f"         (Using barline-based: {total} QL = {duration_info['total_ql']} × {repeat_count})")
                            return total
                except (ValueError, IndexError):
                    pass
        
        # Case 3: Transformation like "transpose_part(THEME_A, 'P4')"
        elif '(' in snippet_name:
            # Extract base snippet name from transformation
            # Pattern: transform_name(base_snippet, args...)
            import re
            match = re.search(r'\(([^,)]+)', snippet_name)
            if match:
                base_name = match.group(1).strip()
                original_snippets = metadata.get('original_snippets', {})
                lily_source = original_snippets.get(base_name, '')
                
                if lily_source:
                    duration_info = calculate_snippet_duration_from_barlines(lily_source)
                    if duration_info and 'total_ql' in duration_info:
                        print(f"         (Using barline-based: {duration_info['total_ql']} QL from base '{base_name}')")
                        return duration_info['total_ql']
    
    # Fall back to event summing for complex cases or when barline method fails
    return sum(e.get('ql', 0) for e in events if e.get('type') != 'barline')


# ============================================================================
# TRANSFORMATION CACHE (Cleared at start of each build)
# ============================================================================

# Global cache to track which transformations have been run and what parts they produced.
# This enables the "run once, cache all parts" behavior for multi-part transformations.
# Cleared at the start of build_score_from_blueprint() to prevent pollution between builds.
_TRANSFORMATION_CACHE_STATUS = {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def normalize_blueprint_string(data_string: str) -> str:
    """Clean blueprint string by removing comments and whitespace."""
    lines = []
    for line in data_string.split('\n'):
        line = re.sub(r'#.*$', '', line)
        line = line.strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


def _get_or_create_snippet_events(snippet_name: str, snippets: Dict[str, List[Dict]]) -> List[Dict]:
    """
    Get events from snippets dict, applying transformations on-the-fly if needed.
    
    HYBRID MODEL LOGIC:
    -------------------
    
    1. NO SUFFIX (e.g., 'transpose_part(THEME, 'P5')'):
       - Runs transformation
       - If returns single Part: auto-caches and returns events (backward compatible)
       - If returns Score: ERROR (composer must specify which part with suffix)
    
    2. WITH SUFFIX (e.g., 'harmonize_part(THEME):harmony'):
       - Runs base transformation ONCE
       - Caches ALL named parts (e.g., :melody, :harmony)
       - Returns only the requested part's events
       - Subsequent calls with same base are lookups (no re-execution)
    
    3. AUTO-ID ASSIGNMENT:
       - Single Parts without .id get auto-assigned .id = 'melody'
       - Removes developer burden for simple transformations
    
    Args:
        snippet_name: Either simple name, transformation call, or suffixed transformation
        snippets: Dictionary of snippet_name -> event_list
    
    Returns:
        List of event dictionaries
    
    Examples:
        # Simple snippet lookup
        >>> _get_or_create_snippet_events('THEME', snippets)
        
        # Single-part transformation (no suffix needed)
        >>> _get_or_create_snippet_events("transpose_part(THEME, 'P5')", snippets)
        
        # Multi-part transformation (suffix required)
        >>> _get_or_create_snippet_events("harmonize_part(THEME, 'I-V-I'):melody", snippets)
        >>> _get_or_create_snippet_events("harmonize_part(THEME, 'I-V-I'):harmony", snippets)
    """
    # 1. Check if snippet (or its result) is already in the dictionary
    if snippet_name in snippets:
        return snippets[snippet_name]
    
    # 2. Check for SUFFIXED transformation syntax: base_instruction:part_id
    #    e.g., "harmonize_part(THEME, 'I-V-I'):harmony"
    suffix_match = re.match(r'^(.*\)):(\w+)$', snippet_name)
    
    if suffix_match:
        # This is a SUFFIXED transformation
        base_instruction = suffix_match.group(1)  # e.g., "harmonize_part(THEME, 'I-V-I')"
        requested_part_id = suffix_match.group(2)  # e.g., "harmony"
        
        # Check if this base transformation has already been run
        if base_instruction in _TRANSFORMATION_CACHE_STATUS:
            # Already ran - this is a lookup
            if snippet_name not in snippets:
                available_parts = _TRANSFORMATION_CACHE_STATUS[base_instruction]
                raise KeyError(
                    f"❌ Transformation '{base_instruction}' was executed, but did not provide "
                    f"a part named '{requested_part_id}'.\n"
                    f"   Available parts: {available_parts}\n"
                    f"   Did you mean: {', '.join(f':{p}' for p in available_parts)}?"
                )
            return snippets[snippet_name]
        
        # First call with this base - run the transformation
        return _run_and_cache_transformation(base_instruction, requested_part_id, snippet_name, snippets)
    
    # 3. Check for REPEAT syntax: SNIPPET * N
    import copy
    repeat_match = re.match(r'^\s*(.+?)\s*\*\s*(\d+)\s*$', snippet_name)
    if repeat_match:
        base_snippet = repeat_match.group(1).strip()
        repeat_count = int(repeat_match.group(2))
        
        # Recursively get base events (handles nested transformations)
        base_events = _get_or_create_snippet_events(base_snippet, snippets)
        
        # Repeat the events
        repeated_events = []
        for _ in range(repeat_count):
            repeated_events.extend(copy.deepcopy(base_events))
        
        # Cache the result
        snippets[snippet_name] = repeated_events
        print(f"      ✓ Repeated {base_snippet} × {repeat_count} = {len(repeated_events)} events")
        
        return repeated_events
    
    # 4. Check for UNSUFFIXED transformation syntax: func_name(base_snippet, arg1, ...)
    transform_match = re.match(r'^\s*(\w+)\s*\((.*)\)\s*$', snippet_name)
    if transform_match:
        # This is an UNSUFFIXED transformation
        # It will work for single-part returns, error for multi-part returns
        return _run_and_cache_transformation(snippet_name, None, snippet_name, snippets)
    
    # 5. Not found and not a transformation
    raise KeyError(
        f"❌ Snippet '{snippet_name}' not found and is not a valid transformation.\n"
        f"   Available snippets: {list(snippets.keys())}\n"
        f"   Transformation syntax: function_name(snippet, 'arg') or function_name(snippet, 'arg'):part_id"
    )


def _run_and_cache_transformation(
    base_instruction: str,
    requested_part_id: Optional[str],
    cache_key: str,
    snippets: Dict[str, List[Dict]]
) -> List[Dict]:
    """
    Execute a transformation function and cache its results.
    
    HYBRID BEHAVIOR:
    ----------------
    - If requested_part_id is None (unsuffixed call):
      * Single Part return: auto-cache with .id='melody', return events
      * Score return: ERROR (composer must use suffix)
    
    - If requested_part_id is provided (suffixed call):
      * Cache all parts with their IDs as suffixes
      * Return only the requested part
    
    Args:
        base_instruction: The transformation call (e.g., "harmonize_part(THEME, 'I-V-I')")
        requested_part_id: The part ID from suffix (e.g., "harmony"), or None if unsuffixed
        cache_key: The full key to use for caching (includes suffix if present)
        snippets: The snippets dictionary to update
    
    Returns:
        List of event dictionaries for the requested/primary part
    """
    print(f"      🔄 Applying transformation: {base_instruction}")
    
    # Parse the transformation call
    match = re.match(r'^\s*(\w+)\s*\((.*)\)\s*$', base_instruction)
    if not match:
        raise ValueError(f"❌ Invalid transformation syntax: {base_instruction}")
    
    func_name = match.group(1)
    args_str = match.group(2)
    
    # Parse arguments
    parsed_args = []
    if args_str:
        for arg in args_str.split(','):
            arg = arg.strip()
            # String literal (quoted)
            if (arg.startswith("'") and arg.endswith("'")) or \
               (arg.startswith('"') and arg.endswith('"')):
                parsed_args.append(arg[1:-1])  # Remove quotes
            # Float (has decimal point)
            elif '.' in arg:
                try:
                    parsed_args.append(float(arg))
                except ValueError:
                    parsed_args.append(arg)  # Treat as snippet name
            # Integer
            else:
                try:
                    parsed_args.append(int(arg))
                except ValueError:
                    parsed_args.append(arg)  # Treat as snippet name
    
    if not parsed_args:
        raise ValueError(f"❌ Transformation '{func_name}' has no arguments.")
    
    # Get base snippet events (first argument) - recursively handle transformations
    base_snippet_name = parsed_args.pop(0)
    base_events = _get_or_create_snippet_events(base_snippet_name, snippets)
    base_part = data_to_part(base_events, {})
    
    # Get and call the transformation function
    try:
        transform_func = getattr(transformations, func_name)
    except AttributeError:
        raise ValueError(
            f"❌ Transformation function '{func_name}' not found in transformations.py.\n"
            f"   Available: identity, transpose_part, invert_part, retrograde_part, "
            f"augment_part, diminish_part, chordify_part, retrograde_inversion, "
            f"transpose_and_augment, harmonize_part, analyze_structural_tones"
        )
    
    transformed_result = transform_func(base_part, *parsed_args)
    
    # HYBRID LOGIC: Handle based on return type and suffix presence
    
    if isinstance(transformed_result, music21.stream.Part):
        # SINGLE PART RETURN
        
        # Auto-assign .id if missing
        if not transformed_result.id:
            transformed_result.id = 'melody'
            print(f"      ℹ️  Auto-assigned .id = 'melody' to single-part result")
        
        part_events = part_to_data(transformed_result)
        
        if requested_part_id is None:
            # UNSUFFIXED CALL - This is the backward-compatible case
            snippets[cache_key] = part_events
            _TRANSFORMATION_CACHE_STATUS[base_instruction] = [transformed_result.id]
            print(f"      ✓ Single Part returned, cached as '{cache_key}'")
            return part_events
        else:
            # SUFFIXED CALL - Verify requested ID matches
            if requested_part_id != transformed_result.id:
                raise KeyError(
                    f"❌ Transformation '{base_instruction}' returned a single part with "
                    f".id = '{transformed_result.id}', but you requested ':{ requested_part_id}'.\n"
                    f"   Use ':{transformed_result.id}' instead, or call without suffix."
                )
            
            # Cache with suffix
            full_key = f"{base_instruction}:{transformed_result.id}"
            snippets[full_key] = part_events
            _TRANSFORMATION_CACHE_STATUS[base_instruction] = [transformed_result.id]
            print(f"      ✓ Single Part returned, cached as '{full_key}'")
            return part_events
    
    elif isinstance(transformed_result, music21.stream.Score):
        # MULTI-PART RETURN (Score)
        
        if requested_part_id is None:
            # UNSUFFIXED CALL - This is an ERROR for multi-part returns
            raise ValueError(
                f"❌ Transformation '{base_instruction}' returns multiple parts.\n"
                f"   You MUST specify which part you want using a suffix.\n"
                f"   Example: {base_instruction}:melody  or  {base_instruction}:harmony\n"
                f"   \n"
                f"   This transformation returned {len(transformed_result.parts)} parts.\n"
                f"   Run it once to see what part IDs are available."
            )
        
        # SUFFIXED CALL - Cache all parts and return requested one
        print(f"      → Detected Score with {len(transformed_result.parts)} parts. Caching all:")
        
        cached_part_ids = []
        for part in transformed_result.parts:
            if not part.id:
                raise ValueError(
                    f"❌ Transformation '{func_name}' returned a Score, but one of its "
                    f"parts is missing a .id attribute.\n"
                    f"   The transformation function must set .id on all returned parts.\n"
                    f"   Example: melody_part.id = 'melody'; bass_part.id = 'harmony'"
                )
            
            part_events = part_to_data(part)
            full_key = f"{base_instruction}:{part.id}"
            snippets[full_key] = part_events
            cached_part_ids.append(part.id)
            print(f"         ... Cached as '{full_key}'")
        
        _TRANSFORMATION_CACHE_STATUS[base_instruction] = cached_part_ids
        
        # Return the requested part
        requested_key = f"{base_instruction}:{requested_part_id}"
        if requested_key not in snippets:
            raise KeyError(
                f"❌ Transformation '{base_instruction}' ran successfully, but did not "
                f"provide a part named '{requested_part_id}'.\n"
                f"   Available parts: {cached_part_ids}\n"
                f"   Did you mean: {', '.join(f':{p}' for p in cached_part_ids)}?"
            )
        
        return snippets[requested_key]
    
    else:
        raise TypeError(
            f"❌ Transformation '{func_name}' returned unexpected type: {type(transformed_result)}.\n"
            f"   Must return music21.stream.Part or music21.stream.Score."
        )


# ============================================================================
# BLUEPRINT STRING PARSING
# ============================================================================

def parse_voice_stave_def(def_string: str) -> List[List[str]]:
    """
    Parse VOICE_STAVE_DEF header into layout structure.
    
    Examples:
        "UpperStaff & LowerStaff" -> [['UpperStaff'], ['LowerStaff']]
        "(Soprano, Alto) & (Tenor, Bass)" -> [['Soprano', 'Alto'], ['Tenor, Bass']]
    """
    def_string = def_string.strip()
    staff_defs = [s.strip() for s in def_string.split('&')]
    
    layout = []
    for staff_def in staff_defs:
        if staff_def.startswith('(') and staff_def.endswith(')'):
            voices_str = staff_def[1:-1]
            voices = [v.strip() for v in voices_str.split(',')]
            layout.append(voices)
        else:
            layout.append([staff_def])
    
    return layout


def parse_voice_stave_data(data_string: str, layout: List[List[str]]) -> List[List[List[str]]]:
    """
    Parse VOICE_STAVE_DATA body into section/staff/snippet structure.
    
    Delimiter hierarchy:
      1. ; splits sections (rows)
      2. & splits staves (columns)
      3. | concatenates snippets (cells)
      4. , separates voices in multi-voice staves
    """
    cleaned = normalize_blueprint_string(data_string)
    section_strings = [s.strip() for s in cleaned.split(';') if s.strip()]
    
    sections = []
    for section_idx, section_str in enumerate(section_strings):
        staff_strings = [s.strip() for s in section_str.split('&')]
        
        if len(staff_strings) != len(layout):
            raise ValueError(
                f"Section {section_idx + 1} has {len(staff_strings)} staves "
                f"but layout defines {len(layout)} staves"
            )
        
        section = []
        for staff_idx, staff_str in enumerate(staff_strings):
            voice_names = layout[staff_idx]
            
            if len(voice_names) > 1:
                voice_strings = [v.strip() for v in staff_str.split(',')]
                
                if len(voice_strings) != len(voice_names):
                    raise ValueError(
                        f"Section {section_idx + 1}, Staff {staff_idx + 1} "
                        f"has {len(voice_names)} voices but provides {len(voice_strings)}"
                    )
                
                staff_content = []
                for voice_str in voice_strings:
                    snippets_list = [s.strip() for s in voice_str.split('|') if s.strip()]
                    staff_content.append(snippets_list)
                section.append(staff_content)
            else:
                snippets_list = [s.strip() for s in staff_str.split('|') if s.strip()]
                section.append(snippets_list)
        
        sections.append(section)
    
    return sections


def build_score_from_blueprint(
    voice_stave_def: str,
    voice_stave_data: str,
    snippets: Dict[str, List[Dict]],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build complete score data from blueprint strings.
    
    This function clears the transformation cache at the start to ensure
    each build is isolated and prevent state pollution between runs.
    """
    # Clear transformation cache (prevents pollution between builds)
    global _TRANSFORMATION_CACHE_STATUS
    _TRANSFORMATION_CACHE_STATUS.clear()
    
    print("\n" + "="*70)
    print("BLUEPRINT STRING FRAMEWORK")
    print("="*70)
    
    print("\n[Parsing layout definition...]")
    layout = parse_voice_stave_def(voice_stave_def)
    
    print(f"✓ Layout structure: {len(layout)} staves")
    for idx, voices in enumerate(layout):
        if len(voices) == 1:
            print(f"   Staff {idx + 1}: {voices[0]} (single voice)")
        else:
            print(f"   Staff {idx + 1}: {', '.join(voices)} ({len(voices)} voices)")
    
    print("\n[Parsing content definition...]")
    sections = parse_voice_stave_data(voice_stave_data, layout)
    
    print(f"✓ Content structure: {len(sections)} sections")
    for section_idx, section in enumerate(sections):
        print(f"   Section {section_idx + 1}:")
        for staff_idx, staff_content in enumerate(section):
            staff_name = layout[staff_idx][0] if len(layout[staff_idx]) == 1 else f"({', '.join(layout[staff_idx])})"
            
            if isinstance(staff_content[0], list):
                for voice_idx, voice_snippets in enumerate(staff_content):
                    voice_name = layout[staff_idx][voice_idx]
                    snippet_str = ' | '.join(voice_snippets)
                    print(f"      {voice_name}: {snippet_str}")
            else:
                snippet_str = ' | '.join(staff_content)
                print(f"      {staff_name}: {snippet_str}")
    
    print("\n[Assembling events from snippets...]")
    
    print("\n" + "="*80)
    print("DEBUG: Starting event assembly")
    print(f"DEBUG: Layout: {layout}")
    print(f"DEBUG: Number of sections: {len(sections)}")
    print("="*80)
    
    parts = {}
    for staff_idx, voices in enumerate(layout):
        staff_name = voices[0] if len(voices) == 1 else f"Staff{staff_idx + 1}"
        parts[staff_name] = []
    
    for section_idx, section in enumerate(sections):
        print(f"\n{'='*80}")
        print(f"DEBUG: SECTION {section_idx + 1} of {len(sections)}")
        print(f"DEBUG: Section content: {section}")
        print(f"{'='*80}")
        print(f"\n   Section {section_idx + 1}:")
        
        section_durations = {}
        section_marks_added = set()  # Track which snippet marks we've added this section
        
        for staff_idx, staff_content in enumerate(section):
            staff_name = list(parts.keys())[staff_idx]
            is_top_staff = (staff_idx == 0)  # Marks should only appear on top staff
            
            print(f"\n  DEBUG: Processing STAFF {staff_idx}: {staff_name}")
            print(f"  DEBUG: is_top_staff: {is_top_staff}")
            print(f"  DEBUG: staff_content: {staff_content}")
            print(f"  DEBUG: staff_content type: {type(staff_content)}")
            if staff_content:
                print(f"  DEBUG: staff_content[0] type: {type(staff_content[0]) if staff_content else 'N/A'}")
            
            # Check if this is a multi-voice staff
            if staff_content and isinstance(staff_content[0], list):
                # Multi-voice staff: staff_content is list of voice snippet lists
                voice_names = layout[staff_idx]
                
                if len(voice_names) > 1:
                    print(f"  DEBUG: *** TAKING PATH 1: MULTI-VOICE STAFF ***")
                    # Process ALL voices in multi-voice staff
                    voice_events_dict = {}
                    total_ql = 0
                    
                    for voice_idx, voice_snippets in enumerate(staff_content):
                        voice_name = voice_names[voice_idx]
                        
                        # Handle rest placeholder
                        if voice_snippets == ['r']:
                            voice_events_dict[voice_name] = None  # Will fill with rests later
                            print(f"      {voice_name}: (rest - duration TBD)")
                            continue
                        
                        # Collect events for this voice
                        voice_events = []
                        for snippet_name in voice_snippets:
                            # Check if snippet has explicit \mark directive
                            original_snippets = metadata.get('original_snippets', {})
                            snippet_lily = original_snippets.get(snippet_name, '')
                            has_explicit_mark = snippet_contains_explicit_mark(snippet_lily) if snippet_lily else False
                            
                            # Inject text mark if snippet follows naming convention (has underscore)
                            # Only on top staff, and only once per section
                            # UNLESS snippet already has explicit mark (override)
                            mark_text = __get_snippet_mark_text(snippet_name)
                            if (is_top_staff and 
                                mark_text and 
                                not has_explicit_mark and
                                snippet_name not in section_marks_added):
                                mark_event = {
                                    'type': 'text_mark',
                                    'text': mark_text,  # Use suffix after underscore
                                    'ql': 0.0  # Zero duration (annotation)
                                }
                                voice_events.append(mark_event)
                                section_marks_added.add(snippet_name)
                            
                            # Use helper function to support on-the-fly transformations
                            snippet_events = _get_or_create_snippet_events(snippet_name, snippets)
                            
                            voice_events.extend(snippet_events)
                            print(f"      {voice_name}: +{snippet_name} ({len(snippet_events)} events)")
                        
                        voice_events_dict[voice_name] = voice_events
                        
                        # Calculate duration for this voice
                        voice_ql = sum(e.get('ql', 0) for e in voice_events if e.get('type') != 'barline')
                        if voice_ql > total_ql:
                            total_ql = voice_ql
                    
                    # Create multi-voice section event
                    parts[staff_name].append({
                        'type': 'multi_voice_section',
                        'voices': voice_events_dict
                    })
                    
                    section_durations[staff_name] = total_ql
                else:
                    print(f"  DEBUG: *** TAKING PATH 2: SINGLE VOICE IN PARENTHESES ***")
                    # Single voice in parentheses (treat as simple single-voice)
                    snippet_names = staff_content[0]
                    
                    if snippet_names == ['r']:
                        section_durations[staff_name] = None
                        print(f"      {staff_name}: (rest - duration TBD)")
                        continue
                    
                    staff_events = []
                    for snippet_name in snippet_names:
                        # Check if snippet has explicit \mark directive
                        original_snippets = metadata.get('original_snippets', {})
                        snippet_lily = original_snippets.get(snippet_name, '')
                        has_explicit_mark = snippet_contains_explicit_mark(snippet_lily) if snippet_lily else False
                        
                        # Inject text mark if snippet follows naming convention
                        # UNLESS snippet already has explicit mark (override)
                        mark_text = __get_snippet_mark_text(snippet_name)
                        if (is_top_staff and 
                            mark_text and 
                            not has_explicit_mark and
                            snippet_name not in section_marks_added):
                            mark_event = {
                                'type': 'text_mark',
                                'text': mark_text,  # Use suffix after underscore
                                'ql': 0.0
                            }
                            staff_events.append(mark_event)
                            section_marks_added.add(snippet_name)
                        
                        # ALWAYS USE PARSED EVENTS (parser handles both LilyShorthand and LilyPond)
                        # Bypass is ONLY used as error handler fallback
                        
                        try:
                            # Get parsed events (handles transformations, repetitions, etc.)
                            snippet_events = _get_or_create_snippet_events(snippet_name, snippets)
                            
                            if snippet_events and len(snippet_events) > 0:
                                # SUCCESS: Use parsed events
                                staff_events.extend(snippet_events)
                                print(f"      {staff_name}: +{snippet_name} ({len(snippet_events)} events)")
                            else:
                                # EMPTY RESULT: Try bypass as fallback
                                raise ValueError(f"Parser returned 0 events for {snippet_name}")
                        
                        except Exception as parse_error:
                            # PARSER FAILED: Generate comprehensive debug output, then try bypass
                            import traceback
                            import re
                            
                            # Extract base name for repetitions (e.g., "THEME_A * 2" -> "THEME_A")
                            base_name = snippet_name
                            repeat_count = 1
                            repeat_match = re.match(r'^\s*(.+?)\s*\*\s*(\d+)\s*$', snippet_name)
                            if repeat_match:
                                base_name = repeat_match.group(1).strip()
                                repeat_count = int(repeat_match.group(2))
                            
                            # Check if base snippet is original (not a transformation)
                            is_original = base_name in original_snippets and '(' not in base_name
                            
                            # ============================================================
                            # GENERATE COMPREHENSIVE DEBUG OUTPUT FOR PARSER UPDATES
                            # ============================================================
                            print(f"\n{'='*70}")
                            print(f"⚠️  PARSER FAILURE DETECTED")
                            print(f"{'='*70}")
                            print(f"Snippet name: {snippet_name}")
                            print(f"Base name: {base_name}")
                            print(f"Is original: {is_original}")
                            print(f"Is transformation: {'(' in snippet_name}")
                            print(f"\nError type: {type(parse_error).__name__}")
                            print(f"Error message: {str(parse_error)}")
                            
                            # Show the original LilyPond input (if available)
                            if is_original and base_name in original_snippets:
                                lily_input = original_snippets[base_name]
                                print(f"\n--- Original LilyPond Input ---")
                                print(lily_input)
                                print(f"--- End Input (length: {len(lily_input)} chars) ---")
                            
                            # Try to run tokenization to show where it fails
                            print(f"\n--- Attempting Manual Tokenization Debug ---")
                            try:
                                from lily_tokenizer import preprocess_snippet
                                if is_original and base_name in original_snippets:
                                    directives, relative_base, raw_tokens = preprocess_snippet(original_snippets[base_name])
                                    print(f"✓ Tokenization succeeded:")
                                    print(f"  Directives: {directives}")
                                    print(f"  Relative base: {relative_base}")
                                    print(f"  Tokens ({len(raw_tokens)}): {raw_tokens}")
                                else:
                                    print(f"  (Not applicable - transformation, not raw snippet)")
                            except Exception as token_error:
                                print(f"✗ Tokenization failed: {type(token_error).__name__}: {token_error}")
                            
                            # Show traceback for detailed diagnosis
                            print(f"\n--- Full Traceback ---")
                            traceback.print_exc()
                            print(f"{'='*70}\n")
                            
                            # ============================================================
                            # CRITICAL: CHECK IF TRANSFORMATION WAS REQUESTED
                            # ============================================================
                            # Transformations MUST be parsed successfully - bypass is NOT allowed
                            # Bypass is ONLY for display-only snippets (no transformation)
                            is_transformation_requested = '(' in snippet_name
                            
                            if is_transformation_requested:
                                # TRANSFORMATION FAILED: DO NOT BYPASS
                                print(f"      ❌ CRITICAL ERROR: Parser failed for transformation '{snippet_name}'")
                                print(f"      ℹ️  Transformations require successful parsing to extract structured data.")
                                print(f"      ℹ️  Bypass is NOT allowed for transformations (would produce incorrect results).")
                                print(f"      💡 Solution: Fix the snippet syntax or update the parser to handle this syntax.")
                                raise ValueError(
                                    f"Cannot apply transformation '{snippet_name}' because parsing failed.\n"
                                    f"   The parser must succeed to extract structured data for transformations.\n"
                                    f"   Fix the snippet syntax or update the parser to handle this syntax."
                                ) from parse_error
                            
                            # ============================================================
                            # ATTEMPT BYPASS FALLBACK (DISPLAY-ONLY SNIPPETS)
                            # ============================================================
                            elif is_original:
                                # No transformation requested - try bypass for display-only
                                print(f"      ℹ️  Parser failed, but no transformation requested. Attempting bypass...")
                                
                                # Try to extract raw LilyPond for bypass
                                music_content = _extract_clean_music_content(original_snippets[base_name])
                                
                                if music_content:
                                    # BYPASS: Inject original LilyPond directly
                                    for rep_idx in range(repeat_count):
                                        raw_event = {
                                            'type': 'raw_lilypond',
                                            'content': music_content,
                                            'snippet_name': base_name,
                                            'ql': 0.0  # Duration handled by renderer
                                        }
                                        staff_events.append(raw_event)
                                        
                                        # Insert bar line between repetitions
                                        if rep_idx < repeat_count - 1:
                                            barline_event = {
                                                'type': 'barline',
                                                'style': '||',
                                                'ql': 0.0
                                            }
                                            staff_events.append(barline_event)
                                    
                                    if repeat_count > 1:
                                        print(f"      ✓ {staff_name}: +{snippet_name} (BYPASS successful: display-only, using original LilyPond × {repeat_count})")
                                    else:
                                        print(f"      ✓ {staff_name}: +{snippet_name} (BYPASS successful: display-only, using original LilyPond)")
                                else:
                                    # COMPLETE FAILURE: Can't parse and can't bypass
                                    print(f"      ❌ {staff_name}: +{snippet_name} (COMPLETE FAILURE: cannot parse or bypass)")
                                    raise parse_error
                            else:
                                # Not original, not transformation - shouldn't happen
                                print(f"      ❌ {staff_name}: +{snippet_name} (PARSER FAILED: unexpected case)")
                                raise parse_error
                    
                    # Use barline-based duration if available, otherwise fall back to event sum
                    total_ql = _calculate_accurate_duration(staff_events, snippet_names, metadata)
                    section_durations[staff_name] = total_ql
                    
                    parts[staff_name].extend(staff_events)
            else:
                print(f"  DEBUG: *** TAKING PATH 3: SIMPLE SINGLE-VOICE STAFF ***")
                # Single-voice staff (simple list)
                snippet_names = staff_content
                
                if snippet_names == ['r']:
                    section_durations[staff_name] = None
                    print(f"      {staff_name}: (rest - duration TBD)")
                    continue
                
                print(f"    DEBUG: snippet_names = {snippet_names}")
                print(f"    DEBUG: parts['{staff_name}'] length before: {len(parts[staff_name])}")
                
                staff_events = []
                print(f"    DEBUG: Created new staff_events list, id={id(staff_events)}")
                
                for snippet_name in snippet_names:
                    # Check if snippet has explicit \mark directive
                    original_snippets = metadata.get('original_snippets', {})
                    snippet_lily = original_snippets.get(snippet_name, '')
                    has_explicit_mark = snippet_contains_explicit_mark(snippet_lily) if snippet_lily else False
                    
                    if has_explicit_mark:
                        print(f"      🔒 Snippet '{snippet_name}' has explicit \\mark - skipping auto-inject")
                    
                    # Inject text mark if snippet follows naming convention
                    # UNLESS snippet already has explicit mark (override)
                    mark_text = __get_snippet_mark_text(snippet_name)
                    if (is_top_staff and 
                        mark_text and 
                        not has_explicit_mark and
                        snippet_name not in section_marks_added):
                        mark_event = {
                            'type': 'text_mark',
                            'text': mark_text,  # Use suffix after underscore
                            'ql': 0.0
                        }
                        staff_events.append(mark_event)
                        section_marks_added.add(snippet_name)
                    
                    # PARSER BYPASS: Check if this is an original snippet or simple repetition
                    # Extract base name for repetitions (e.g., "THEME_A * 2" -> "THEME_A")
                    import re
                    base_name = snippet_name
                    repeat_count = 1
                    repeat_match = re.match(r'^\s*(.+?)\s*\*\s*(\d+)\s*$', snippet_name)
                    if repeat_match:
                        base_name = repeat_match.group(1).strip()
                        repeat_count = int(repeat_match.group(2))
                    
                    # Check if base snippet is original (not a transformation)
                    is_original = base_name in original_snippets and '(' not in base_name
                    
                    if is_original:
                        # This is an original snippet or repetition of original
                        # Extract clean music content (remove metadata directives)
                        music_content = _extract_clean_music_content(original_snippets[base_name])
                        
                        if music_content:
                            # Create raw_lilypond events (repeat if necessary)
                            for rep_idx in range(repeat_count):
                                raw_event = {
                                    'type': 'raw_lilypond',
                                    'content': music_content,
                                    'snippet_name': base_name,
                                    'ql': 0.0  # Duration handled by renderer
                                }
                                staff_events.append(raw_event)
                                
                                # Insert bar line between repetitions (but not after the last one)
                                if rep_idx < repeat_count - 1:
                                    barline_event = {
                                        'type': 'barline',
                                        'style': '||',
                                        'ql': 0.0
                                    }
                                    staff_events.append(barline_event)
                            
                            if repeat_count > 1:
                                print(f"      {staff_name}: +{snippet_name} (BYPASS: display-only, using original LilyPond × {repeat_count})")
                            else:
                                print(f"      {staff_name}: +{snippet_name} (BYPASS: display-only, using original LilyPond)")
                        else:
                            # Fallback: use parsed events if extraction fails
                            snippet_events = _get_or_create_snippet_events(snippet_name, snippets)
                            staff_events.extend(snippet_events)
                            print(f"      {staff_name}: +{snippet_name} ({len(snippet_events)} events, extraction failed)")
                    else:
                        # Transformation: MUST parse successfully (no bypass allowed)
                        try:
                            snippet_events = _get_or_create_snippet_events(snippet_name, snippets)
                            
                            # Hybrid model always returns List[Dict] (events), never dict of parts
                            staff_events.extend(snippet_events)
                            print(f"      {staff_name}: +{snippet_name} ({len(snippet_events)} events)")
                        except Exception as transform_error:
                            # TRANSFORMATION FAILED: DO NOT BYPASS
                            print(f"\n{'='*70}")
                            print(f"❌ CRITICAL ERROR: Transformation '{snippet_name}' failed")
                            print(f"{'='*70}")
                            print(f"ℹ️  Transformations require successful parsing to extract structured data.")
                            print(f"ℹ️  Bypass is NOT allowed for transformations (would produce incorrect results).")
                            print(f"💡 Solution: Fix the snippet syntax or update the parser to handle this syntax.")
                            print(f"{'='*70}\n")
                            raise ValueError(
                                f"Cannot apply transformation '{snippet_name}' because it failed.\n"
                                f"   The parser must succeed to extract structured data for transformations.\n"
                                f"   Fix the snippet syntax or update the parser to handle this syntax."
                            ) from transform_error
                    print(f"    DEBUG: After {snippet_name}, staff_events length: {len(staff_events)}")
                
                # Use barline-based duration if available, otherwise fall back to event sum
                total_ql = _calculate_accurate_duration(staff_events, snippet_names, metadata)
                section_durations[staff_name] = total_ql
                
                print(f"    DEBUG: Section duration for {staff_name}: {total_ql} QL")
                print(f"    DEBUG: staff_events final length: {len(staff_events)}")
                print(f"    DEBUG: About to extend parts['{staff_name}']...")
                
                parts[staff_name].extend(staff_events)
                
                print(f"    DEBUG: parts['{staff_name}'] length after extend: {len(parts[staff_name])}")
        
        active_durations = [d for d in section_durations.values() if d is not None]
        if active_durations:
            max_duration = max(active_durations)
            
            if len(set(active_durations)) > 1:
                print(f"\n   ⚠️  WARNING: Section {section_idx + 1} has mismatched durations")
                for staff_name, duration in section_durations.items():
                    if duration is not None:
                        print(f"      {staff_name}: {duration} QL")
            
            for staff_name, duration in section_durations.items():
                if duration is None:
                    # Get bar duration from time signature (don't hardcode 4.0!)
                    time_sig = metadata.get('time_signature', '4/4')
                    if '/' in time_sig:
                        numerator, denominator = time_sig.split('/')
                        bar_duration = int(numerator) * (4.0 / int(denominator))
                    else:
                        bar_duration = 4.0
                    
                    num_bars = int(max_duration / bar_duration)
                    
                    rest_events = []
                    for i in range(num_bars):
                        rest_events.append({'type': 'rest', 'ql': bar_duration})
                        # Add measure bar line after each rest (except the last one)
                        # The section barline will be added after the loop
                        if i < num_bars - 1:
                            rest_events.append({'type': 'barline', 'style': '|', 'ql': 0.0})
                    
                    parts[staff_name].extend(rest_events)
                    print(f"      {staff_name}: Generated {num_bars} bar rests with measure bars ({max_duration} QL)")
        
        print(f"\n  DEBUG: After section {section_idx + 1}, adding barlines")
        for staff_name in parts.keys():
            # Avoid appending duplicate barline events which create empty measures
            # in MusicXML export (consecutive barlines result in empty measures).
            if not parts[staff_name] or parts[staff_name][-1].get('type') != 'barline':
                parts[staff_name].append({'type': 'barline', 'style': '||', 'ql': 0.0})
            else:
                # If last event already a barline, don't append another; keep as-is
                pass
            last_event = parts[staff_name][-1] if parts[staff_name] else None
            print(f"    DEBUG: parts['{staff_name}'][-1] = {last_event}")
            print(f"    DEBUG: parts['{staff_name}'] total events: {len(parts[staff_name])}")
    
    print("\n" + "="*70)
    print("BLUEPRINT ASSEMBLY COMPLETE")
    print("="*70)
    
    print("\nDEBUG: FINAL STATE:")
    for staff_name, events in parts.items():
        barline_count = sum(1 for e in events if e.get('type') == 'barline')
        total_ql = sum(e.get('ql', 0) for e in events if e.get('type') != 'barline')
        print(f"  {staff_name}:")
        print(f"    Total events: {len(events)}")
        print(f"    Barline events: {barline_count}")
        print(f"    Total QL (event sum): {total_ql}")
        print(f"    First 3 events: {events[:3]}")
        print(f"    Last 3 events: {events[-3:]}")
    
    print("\n" + "="*70)
    for staff_name, events in parts.items():
        total_ql = sum(e.get('ql', 0) for e in events if e.get('type') != 'barline')
        print(f"✓ {staff_name}: {len(events)} events ({total_ql} QL)")
    
    # Store blueprint structure in metadata for .ly header documentation
    metadata['blueprint_structure'] = {
        'voice_stave_def': voice_stave_def,
        'voice_stave_data': voice_stave_data,
    }
    
    # Convert ALL snippets (original + transformations) to editable LilyPond
    from src.project_template import _events_to_absolute_lilypond
    
    lilypond_snippets = {}
    for name, events in snippets.items():
        if events:  # Only convert non-empty snippets
            try:
                lily_code = _events_to_absolute_lilypond(events, metadata)
                lilypond_snippets[name] = lily_code
            except Exception as e:
                print(f"⚠️  Failed to convert '{name}' to LilyPond: {e}")
                # Store events as fallback (for debugging)
                lilypond_snippets[name] = f"# ERROR: Could not convert to LilyPond\n# {str(e)}"
    
    # Store as LilyPond snippets (editable format!) for Station 2 display
    metadata['station2_snippets'] = lilypond_snippets
    
    return {
        'metadata': metadata,
        'parts': parts
    }


# ============================================================================
# STATION 2 DISPLAY HELPER
# ============================================================================

def display_station2_library(snippets: Dict[str, List[Dict]], title: str = "STATION 2: PARSED SNIPPET LIBRARY"):
    """
    Display Station 2 snippet library with copy-paste ready format.
    
    Args:
        snippets: Dictionary of snippet_name -> event_list
        title: Title to display (default: "STATION 2: PARSED SNIPPET LIBRARY")
    """
    print("\n" + "="*70)
    print(title)
    print("="*70)
    print("\n# You can copy these parsed events to reuse in other studies:")
    print("# (bypasses LilyPond parsing - direct event lists)\n")
    
    for name, events in snippets.items():
        if events:  # Only show non-empty snippets
            print(f"{name} = [")
            for i, event in enumerate(events):
                # Format event dict with proper indentation
                event_items = []
                for key, value in event.items():
                    # Format value appropriately
                    if isinstance(value, str):
                        event_items.append(f"'{key}': '{value}'")
                    elif isinstance(value, list):
                        # Format lists of strings (like articulations)
                        formatted_list = "[" + ", ".join(f"'{v}'" for v in value) + "]"
                        event_items.append(f"'{key}': {formatted_list}")
                    else:
                        event_items.append(f"'{key}': {value}")
                
                # Join with proper wrapping
                event_str = "{" + ", ".join(event_items) + "}"
                
                # Add trailing comma except for last item
                if i < len(events) - 1:
                    print(f"    {event_str},")
                else:
                    print(f"    {event_str}")
            print("]\n")
    
    print("="*70)
    print(f"💡 TIP: Total snippets in library: {len(snippets)}")
    print(f"💡 Copy snippet lists above to reuse without LilyPond parsing")
    print("="*70 + "\n")


# ============================================================================
# AUTO-PARSING WRAPPER (Station 1 Clean Interface)
# ============================================================================

def build_score_from_blueprint_auto(
    voice_stave_def: str,
    voice_stave_data: str,
    metadata: Dict[str, Any],
    caller_globals: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build score from blueprint with AUTOMATIC snippet detection and parsing.
    
    This is the CLEAN STATION 1 interface that eliminates the redundant
    snippets_to_parse dictionary.
    
    Workflow:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. Analyze VOICE_STAVE_DATA to extract all referenced snippet names
    2. Look up snippet variables in caller's namespace (globals())
    3. Auto-parse LilyPond snippets into Station 2 library
    4. Call build_score_from_blueprint() with populated SNIPPETS
    
    Args:
        voice_stave_def: Layout definition ("Melody & Bass")
        voice_stave_data: Content blueprint with sections/snippets
        metadata: Score metadata dictionary
        caller_globals: globals() from calling module (to find snippet variables)
        
    Returns:
        dict: Complete score_data {'metadata': {}, 'parts': {}}
        
    Example (in study file):
        # STATION 1: Only define snippets and blueprint
        THEME_A = r'''\\relative c'' { c4 d e f }'''
        BASS = r'''\\relative c { c4 g c2 }'''
        
        VOICE_STAVE_DEF = "Melody & Bass"
        VOICE_STAVE_DATA = '''
            THEME_A & BASS;
            transpose_part(THEME_A, 'P5') & BASS
        '''
        
        def build_score_data():
            metadata = {'title': 'My Study'}
            return build_score_from_blueprint_auto(
                VOICE_STAVE_DEF,
                VOICE_STAVE_DATA,
                metadata,
                globals()  # Pass module namespace
            )
    """
    from src.lilypond_parser import parse_lilypond_to_data
    
    print("\n" + "="*70)
    print("AUTO-PARSING STATION 1 SNIPPETS")
    print("="*70)
    
    # Extract all snippet names from blueprint
    print("\n[Analyzing blueprint for snippet references...]")
    snippet_names = extract_snippet_names_from_blueprint(voice_stave_data)
    print(f"✓ Found {len(snippet_names)} unique snippets: {', '.join(snippet_names)}")
    
    # Auto-build snippets_to_parse dictionary from caller's globals
    print("\n[Looking up snippet variables in caller namespace...]")
    snippets_to_parse = {}
    missing_snippets = []
    
    for name in snippet_names:
        if name in caller_globals:
            snippet_value = caller_globals[name]
            # Verify it's a string (LilyPond code)
            if isinstance(snippet_value, str):
                snippets_to_parse[name] = snippet_value
                print(f"  ✓ {name}: Found ({len(snippet_value)} chars)")
            else:
                print(f"  ⚠️  {name}: Found but not a string (type: {type(snippet_value).__name__})")
                missing_snippets.append(name)
        else:
            print(f"  ❌ {name}: Not found in caller namespace")
            missing_snippets.append(name)
    
    if missing_snippets:
        raise ValueError(
            f"Missing snippet definitions in Station 1: {', '.join(missing_snippets)}\n"
            f"Ensure these variables are defined before VOICE_STAVE_DATA."
        )
    
    # Parse LilyPond snippets into Station 2 library
    print("\n[Station 1 → Station 2: Parsing LilyPond snippets...]")
    SNIPPETS: Dict[str, list] = {}
    
    for name, lily_code in snippets_to_parse.items():
        try:
            parsed = parse_lilypond_to_data(lily_code, part_name=name)
            
            if parsed and 'parts' in parsed and name in parsed['parts']:
                SNIPPETS[name] = parsed['parts'][name]
                event_count = len(SNIPPETS[name])
                print(f"  ✓ {name}: {event_count} events")
            else:
                print(f"  ⚠️  {name}: Parse failed or no events found")
                SNIPPETS[name] = []
                
        except Exception as e:
            print(f"  ❌ {name}: Parse error: {e}")
            SNIPPETS[name] = []
    
    print(f"\n  → Station 2 Library: {len(SNIPPETS)} snippets ready")
    
    # Remember initial snippet count
    initial_snippet_count = len(SNIPPETS)
    initial_snippet_names = set(SNIPPETS.keys())
    
    # Display initial Station 2 contents (from Station 1 parsing)
    display_station2_library(SNIPPETS, "STATION 2 (Initial): PARSED LILYPOND SNIPPETS")
    
    # Store original snippets in metadata (for clef detection, mark injection, etc.)
    metadata['original_snippets'] = snippets_to_parse
    
    # Call main blueprint builder with populated SNIPPETS
    # Note: SNIPPETS dictionary is modified in-place during blueprint processing
    score_data = build_score_from_blueprint(
        voice_stave_def,
        voice_stave_data,
        SNIPPETS,  # This gets modified in-place!
        metadata
    )
    
    # Check if new snippets were added during Station 3 processing
    final_snippet_names = set(SNIPPETS.keys())
    new_snippet_names = final_snippet_names - initial_snippet_names
    
    if new_snippet_names:
        print("\n" + "="*70)
        print("🔄 STATION 3 ADDED NEW SNIPPETS TO STATION 2")
        print("="*70)
        print(f"Initial: {initial_snippet_count} snippets → Final: {len(SNIPPETS)} snippets")
        print(f"New snippets: {', '.join(sorted(new_snippet_names))}\n")
        
        display_station2_library(SNIPPETS, "STATION 2 (Final): ALL SNIPPETS (Original + Transformations)")
    
    return score_data

