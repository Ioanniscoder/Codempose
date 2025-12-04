"""
Score Builder: Flexible declarative score assembly from SCORE_STRUCTURE.

This module provides utilities to build multi-stave scores from declarative
structure definitions, supporting:
- 1-stave to N-stave systems
- Single-voice and multi-voice (polyphonic) staves
- Auto-generation of matching rests
- Clean separation of musical content (snippets) from structure

Design Philosophy:
- Snippet-first: All musical content defined as named snippets
- Declarative: Structure describes composition, not implementation  
- Flexible: Scales from solo to orchestral without code changes
- Safe: Pure data structures (no eval, no dynamic code execution)

Usage Example:
    snippets = {
        'MELODY': melody_events,
        'HARMONY': harmony_events,
    }
    
    structure = [
        {
            'name': 'Introduction',
            'staves': {
                'UpperStaff': 'MELODY',
                'LowerStaff': 'r',  # Auto-generate rests
            }
        },
    ]
    
    score_data = build_score_from_structure(structure, snippets, metadata)
"""

from typing import Dict, List, Union, Any
import copy


def calculate_snippet_duration(events: List[Dict]) -> float:
    """
    Calculate total quarter-length duration of event list.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        Total duration in quarter lengths (excluding barlines)
    """
    return sum(e.get('ql', 0) for e in events if e.get('type') != 'barline')


def parse_time_signature(time_sig: str) -> float:
    """
    Parse time signature string to quarter-length duration per measure.
    
    Args:
        time_sig: Time signature string (e.g., '4/4', '3/4', '6/8')
        
    Returns:
        Bar duration in quarter lengths
        
    Examples:
        '4/4' → 4.0 (4 quarter notes)
        '3/4' → 3.0 (3 quarter notes)
        '6/8' → 3.0 (6 eighth notes = 3 quarter notes)
    """
    numerator, denominator = map(int, time_sig.split('/'))
    
    # Calculate quarter-note equivalents
    if denominator == 4:
        return float(numerator)
    elif denominator == 8:
        return float(numerator) / 2.0
    elif denominator == 2:
        return float(numerator) * 2.0
    elif denominator == 16:
        return float(numerator) / 4.0
    else:
        # Default fallback
        return 4.0


def create_bar_rests(duration_ql: float, time_sig: str = '4/4') -> List[Dict]:
    """
    Generate whole-bar rests matching total duration.
    
    Uses r1 (whole rest) for each measure, regardless of time signature.
    This follows LilyPond convention where r1 means "rest for one full measure".
    
    Args:
        duration_ql: Total duration in quarter lengths to fill with rests
        time_sig: Time signature (default '4/4')
        
    Returns:
        List of rest events, one per measure
        
    Examples:
        create_bar_rests(8.0, '4/4') → 2 measures of r1
        create_bar_rests(6.0, '3/4') → 2 measures of r1
    """
    bar_duration = parse_time_signature(time_sig)
    num_measures = int(duration_ql / bar_duration)
    
    # Generate one r1 (whole rest) per measure
    return [{'type': 'rest', 'ql': bar_duration} for _ in range(num_measures)]


def find_reference_snippet(
    staves: Dict[str, Union[str, Dict]],
    snippets: Dict[str, List[Dict]]
) -> List[Dict]:
    """
    Find first non-'r' snippet to use as duration reference.
    
    When auto-generating rests, we need to know how long they should be.
    This function finds the first actual snippet (not 'r') in the staves
    dict to use as the reference duration.
    
    Args:
        staves: Dict of staff assignments from SCORE_STRUCTURE section
        snippets: Dict of all available snippets
        
    Returns:
        Event list from first non-rest snippet found, or empty list
    """
    for staff_content in staves.values():
        if isinstance(staff_content, str) and staff_content != 'r':
            return snippets.get(staff_content, [])
        elif isinstance(staff_content, dict):
            # Multi-voice staff: check each voice
            for voice_snippet in staff_content.values():
                if voice_snippet != 'r':
                    return snippets.get(voice_snippet, [])
    
    return []  # No reference found


def build_score_from_structure(
    score_structure: List[Dict[str, Any]],
    snippets: Dict[str, List[Dict]],
    metadata: Dict[str, Any],
    time_signature: str = '4/4'
) -> Dict[str, Any]:
    """
    Build score_data from declarative SCORE_STRUCTURE.
    
    This is the main entry point for flexible score assembly. It supports:
    
    1. Single-snippet format (one-stave score):
       {'snippet': 'MELODY'}
       
    2. Named section with single snippet:
       {'name': 'Introduction', 'snippet': 'INTRO'}
       
    3. Multi-stave with explicit staff assignment:
       {
           'name': 'Theme A',
           'staves': {
               'UpperStaff': 'THEME_A',
               'LowerStaff': 'r',  # Auto-generate rests
           }
       }
       
    4. Multi-voice per staff (polyphonic):
       {
           'name': 'Fugue',
           'staves': {
               'UpperStaff': {
                   'Voice1': 'SOPRANO',
                   'Voice2': 'ALTO',
               },
               'LowerStaff': {
                   'Voice3': 'TENOR',
                   'Voice4': 'BASS',
               }
           }
       }
    
    Args:
        score_structure: List of section definitions (see formats above)
        snippets: Dict mapping snippet names to event lists
        metadata: Score metadata (title, key, tempo, etc.)
        time_signature: Default time signature for rest generation
        
    Returns:
        Standard score_data dict: {'metadata': {...}, 'parts': {...}}
        
    Examples:
        # Single-stave score
        structure = [{'snippet': 'MELODY'}]
        
        # Two-stave score with auto-rests
        structure = [{
            'staves': {
                'Melody': 'THEME',
                'Harmony': 'r',
            }
        }]
        
        # Multi-section with alternating staves
        structure = [
            {'name': 'Intro', 'staves': {'Upper': 'INTRO', 'Lower': 'r'}},
            {'name': 'Harmony', 'staves': {'Upper': 'r', 'Lower': 'CHORDS'}},
        ]
    """
    # Initialize parts dictionary
    # Parts can be:
    # - Single-voice: part_name → list of events
    # - Multi-voice: part_name → dict of voice_name → list of events
    parts: Dict[str, Union[List[Dict], Dict[str, List[Dict]]]] = {}
    
    # Process each section in the structure
    for section in score_structure:
        section_name = section.get('name', 'Untitled Section')
        
        # Format 1/2: Simple snippet (single-stave score)
        if 'snippet' in section:
            snippet_name = section['snippet']
            if snippet_name not in snippets:
                print(f"⚠️  WARNING: Snippet '{snippet_name}' not found, skipping")
                continue
            
            # Add to default part
            default_part = 'MainStaff'
            if default_part not in parts:
                parts[default_part] = []
            
            parts[default_part].extend(copy.deepcopy(snippets[snippet_name]))
            parts[default_part].append({'type': 'barline', 'style': '||', 'ql': 0.0})
        
        # Format 3/4/5: Multi-stave with explicit staff assignment
        elif 'staves' in section:
            staves = section['staves']
            
            # Find reference snippet for rest duration calculation
            reference_events = find_reference_snippet(staves, snippets)
            reference_duration = calculate_snippet_duration(reference_events)
            
            # Process each staff
            for staff_name, staff_content in staves.items():
                # Initialize staff if needed
                if staff_name not in parts:
                    # Determine if this will be multi-voice based on first content
                    if isinstance(staff_content, dict):
                        parts[staff_name] = {}
                    else:
                        parts[staff_name] = []
                
                # Handle different content types
                if staff_content == 'r':
                    # Auto-generate rests
                    rest_events = create_bar_rests(reference_duration, time_signature)
                    
                    if isinstance(parts[staff_name], dict):
                        # Multi-voice staff: add to first voice
                        first_voice = list(parts[staff_name].keys())[0] if parts[staff_name] else 'Voice1'
                        if first_voice not in parts[staff_name]:
                            parts[staff_name][first_voice] = []
                        parts[staff_name][first_voice].extend(rest_events)
                    else:
                        # Single-voice staff
                        parts[staff_name].extend(rest_events)
                
                elif isinstance(staff_content, str):
                    # Single-voice: snippet name
                    snippet_name = staff_content
                    if snippet_name not in snippets:
                        print(f"⚠️  WARNING: Snippet '{snippet_name}' not found, skipping")
                        continue
                    
                    if isinstance(parts[staff_name], list):
                        parts[staff_name].extend(copy.deepcopy(snippets[snippet_name]))
                    else:
                        print(f"⚠️  WARNING: Staff '{staff_name}' mixing single/multi-voice, skipping")
                
                elif isinstance(staff_content, dict):
                    # Multi-voice: dict of voice names → snippet names
                    if not isinstance(parts[staff_name], dict):
                        print(f"⚠️  WARNING: Staff '{staff_name}' mixing single/multi-voice, skipping")
                        continue
                    
                    for voice_name, voice_snippet in staff_content.items():
                        if voice_name not in parts[staff_name]:
                            parts[staff_name][voice_name] = []
                        
                        if voice_snippet == 'r':
                            # Auto-generate rests for this voice
                            rest_events = create_bar_rests(reference_duration, time_signature)
                            parts[staff_name][voice_name].extend(rest_events)
                        else:
                            # Add snippet content
                            if voice_snippet not in snippets:
                                print(f"⚠️  WARNING: Snippet '{voice_snippet}' not found, skipping")
                                continue
                            parts[staff_name][voice_name].extend(copy.deepcopy(snippets[voice_snippet]))
            
            # Add barlines to all staves after section
            for staff_name in staves.keys():
                if staff_name in parts:
                    if isinstance(parts[staff_name], list):
                        parts[staff_name].append({'type': 'barline', 'style': '||', 'ql': 0.0})
                    elif isinstance(parts[staff_name], dict):
                        # Add barline to each voice
                        for voice_events in parts[staff_name].values():
                            voice_events.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Return standard score_data structure
    return {
        'metadata': metadata,
        'parts': parts,
    }


# Public API
__all__ = [
    'build_score_from_structure',
    'calculate_snippet_duration',
    'create_bar_rests',
    'parse_time_signature',
]
