"""
Composition Shorthand - Core Module

This module provides a declarative language for composing music by combining
and transforming snippet building blocks.

SYNTAX:
    'V1'                -> Single snippet
    'V1 + V2'          -> Chain two snippets
    'V1 * 3'           -> Repeat snippet 3 times
    'transpose(V1, 5)' -> Transpose snippet up 5 semitones
    'invert(V1)'       -> Invert snippet melodically
    'retrograde(V1)'   -> Reverse snippet
    
Example usage:
    VOICE_ASSIGNMENTS = {
        'Melody': {
            'Soprano': 'THEME + transpose(THEME, 5) + THEME',  # Transposed ABA
            'Alto': 'THEME * 2',                               # Repeat
        }
    }
    
    score_data = build_score_from_assignments(VOICE_ASSIGNMENTS, voice_data)
"""

import re
from typing import Dict, List, Any, Callable, Optional


# ============================================================================
# MUSICAL TRANSFORMATION FUNCTIONS
# ============================================================================

def transpose_events(events: list, semitones: int) -> list:
    """
    Transpose all notes in event list by given semitones.
    
    Args:
        events: List of event dictionaries
        semitones: Number of semitones to transpose (positive = up, negative = down)
    
    Returns:
        New list of transposed events
    """
    transposed = []
    
    for ev in events:
        new_ev = ev.copy()
        
        if ev.get('type') == 'note':
            # Calculate new pitch
            steps = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
            semitones_per_step = [0, 2, 4, 5, 7, 9, 11]  # C=0, D=2, E=4, etc.
            
            current_step_idx = steps.index(ev['step'].lower())
            current_semitone = semitones_per_step[current_step_idx] + ev.get('alter', 0)
            current_total = ev['octave'] * 12 + current_semitone
            
            # Add transposition
            new_total = current_total + semitones
            new_octave = new_total // 12
            new_semitone_in_octave = new_total % 12
            
            # Find closest step
            closest_idx = 0
            min_diff = 100
            for idx, sem in enumerate(semitones_per_step):
                diff = abs(sem - new_semitone_in_octave)
                if diff < min_diff:
                    min_diff = diff
                    closest_idx = idx
            
            new_step = steps[closest_idx]
            new_alter = new_semitone_in_octave - semitones_per_step[closest_idx]
            
            new_ev['step'] = new_step
            new_ev['octave'] = new_octave
            new_ev['alter'] = new_alter
            
        elif ev.get('type') == 'chord':
            # Transpose all pitches in chord
            new_pitches = []
            for pitch in ev.get('pitches', []):
                steps = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
                semitones_per_step = [0, 2, 4, 5, 7, 9, 11]
                
                current_step_idx = steps.index(pitch['step'].lower())
                current_semitone = semitones_per_step[current_step_idx] + pitch.get('alter', 0)
                current_total = pitch['octave'] * 12 + current_semitone
                
                new_total = current_total + semitones
                new_octave = new_total // 12
                new_semitone_in_octave = new_total % 12
                
                closest_idx = 0
                min_diff = 100
                for idx, sem in enumerate(semitones_per_step):
                    diff = abs(sem - new_semitone_in_octave)
                    if diff < min_diff:
                        min_diff = diff
                        closest_idx = idx
                
                new_pitch = pitch.copy()
                new_pitch['step'] = steps[closest_idx]
                new_pitch['octave'] = new_octave
                new_pitch['alter'] = new_semitone_in_octave - semitones_per_step[closest_idx]
                new_pitches.append(new_pitch)
            
            new_ev['pitches'] = new_pitches
        
        transposed.append(new_ev)
    
    return transposed


def invert_events(events: list, axis_pitch: str = 'c4') -> list:
    """
    Invert events melodically around an axis pitch.
    
    Args:
        events: List of event dictionaries
        axis_pitch: Pitch to invert around (e.g., 'c4', 'g4')
    
    Returns:
        New list of inverted events
    """
    # Parse axis pitch
    axis_step = axis_pitch[0].lower()
    axis_octave = int(axis_pitch[-1])
    
    steps = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    semitones_per_step = [0, 2, 4, 5, 7, 9, 11]
    axis_semitone = semitones_per_step[steps.index(axis_step)] + axis_octave * 12
    
    inverted = []
    
    for ev in events:
        new_ev = ev.copy()
        
        if ev.get('type') == 'note':
            current_step_idx = steps.index(ev['step'].lower())
            current_semitone = semitones_per_step[current_step_idx] + ev.get('alter', 0)
            current_total = ev['octave'] * 12 + current_semitone
            
            # Invert: new_pitch = axis - (current - axis)
            new_total = 2 * axis_semitone - current_total
            new_octave = new_total // 12
            new_semitone_in_octave = new_total % 12
            
            # Find closest step
            closest_idx = 0
            min_diff = 100
            for idx, sem in enumerate(semitones_per_step):
                diff = abs(sem - new_semitone_in_octave)
                if diff < min_diff:
                    min_diff = diff
                    closest_idx = idx
            
            new_ev['step'] = steps[closest_idx]
            new_ev['octave'] = new_octave
            new_ev['alter'] = new_semitone_in_octave - semitones_per_step[closest_idx]
        
        inverted.append(new_ev)
    
    return inverted


def retrograde_events(events: list) -> list:
    """
    Reverse the order of events (retrograde).
    
    Args:
        events: List of event dictionaries
    
    Returns:
        New list with reversed event order
    """
    return list(reversed(events))


# ============================================================================
# VALIDATION
# ============================================================================

def validate_voice_assignments(voice_assignments: dict, available_voices: list) -> List[str]:
    """
    Validate VOICE_ASSIGNMENTS against available voice names.
    
    Returns list of errors (empty if valid).
    
    Args:
        voice_assignments: The VOICE_ASSIGNMENTS structure
        available_voices: List of available voice names (e.g., ['INTRO', 'THEME'])
    
    Returns:
        List of error messages (empty if valid)
    
    Example:
        >>> assignments = {'Melody': {'Soprano': 'INTRO + THEM'}}  # Typo: THEM
        >>> errors = validate_voice_assignments(assignments, ['INTRO', 'THEME'])
        >>> print(errors)
        ["Voice 'THEM' not found in Melody.Soprano expression 'INTRO + THEM'"]
    """
    errors = []
    
    for staff_name, voices in voice_assignments.items():
        for voice_name, expression in voices.items():
            # Extract all voice references from expression
            # Remove transformations to get voice names
            expr_clean = re.sub(r'\w+\([^)]+\)', '', expression)  # Remove func(...)
            expr_clean = re.sub(r'\*\s*\d+', '', expr_clean)  # Remove * N
            
            # Split by + and get voice names
            parts = [p.strip() for p in expr_clean.split('+') if p.strip()]
            
            # Also check inside transformations
            func_matches = re.findall(r'\w+\(([^)]+)\)', expression)
            for match in func_matches:
                args = [a.strip() for a in match.split(',')]
                if args:
                    parts.append(args[0])  # First arg is usually voice name
            
            # Validate each referenced voice
            for part in parts:
                if part and part not in available_voices:
                    errors.append(
                        f"Voice '{part}' not found in {staff_name}.{voice_name} "
                        f"expression '{expression}'. Available: {available_voices}"
                    )
    
    return errors


# ============================================================================
# SHORTHAND PARSER
# ============================================================================

def parse_voice_assignment(expression: str, voice_lookup: dict, transformations: Optional[Dict[str, Callable]] = None) -> list:
    """
    Convert shorthand expression to event list with transformation support.
    
    Supported syntax:
        'V1'                    -> voice1_events
        'V1 + V2'               -> voice1_events + voice2_events
        'V1 * 3'                -> voice1_events * 3
        'transpose(V1, 5)'      -> Transpose V1 up 5 semitones
        'invert(V1)'            -> Melodic inversion of V1
        'retrograde(V1)'        -> Reverse V1
        'V1 + transpose(V2, 7)' -> Mixed operations
    
    Args:
        expression: Shorthand string (e.g., 'V1 + transpose(V2, 5)')
        voice_lookup: Dict mapping 'V1' -> voice1_events
        transformations: Optional dict of custom transformation functions
    
    Returns:
        Combined event list
    
    Examples:
        >>> voices = {'V1': [{'type': 'note', 'step': 'c', 'octave': 4, 'ql': 1.0}]}
        >>> result = parse_voice_assignment('V1 + V1', voices)
        >>> len(result)
        2
    """
    if transformations is None:
        transformations = {
            'transpose': transpose_events,
            'invert': invert_events,
            'retrograde': retrograde_events,
        }
    
    # Split by + operator (chain)
    parts = [p.strip() for p in expression.split('+')]
    result = []
    
    for part in parts:
        # Check for transformation functions: func(voice, args...)
        func_match = re.match(r'(\w+)\((.*)\)', part)
        
        if func_match:
            # Parse transformation: transpose(V1, 5)
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            
            if func_name not in transformations:
                raise ValueError(f"Unknown transformation '{func_name}'. Available: {list(transformations.keys())}")
            
            # Parse arguments
            args = [a.strip() for a in args_str.split(',')]
            voice_name = args[0]
            
            if voice_name not in voice_lookup:
                raise ValueError(f"Voice '{voice_name}' not found in voice_lookup. Available: {list(voice_lookup.keys())}")
            
            events = voice_lookup[voice_name].copy() if isinstance(voice_lookup[voice_name], list) else list(voice_lookup[voice_name])
            
            # Apply transformation
            if func_name == 'transpose':
                if len(args) < 2:
                    raise ValueError(f"transpose() requires 2 arguments: voice, semitones")
                semitones = int(args[1])
                events = transformations['transpose'](events, semitones)
            elif func_name == 'invert':
                axis = args[1] if len(args) > 1 else 'c4'
                events = transformations['invert'](events, axis)
            elif func_name == 'retrograde':
                events = transformations['retrograde'](events)
            else:
                # Custom transformation
                events = transformations[func_name](events, *args[1:])
            
            result.extend(events)
            
        elif '*' in part:
            # Repetition: V1 * 3
            voice_name, count = [x.strip() for x in part.split('*')]
            count = int(count)
            if voice_name not in voice_lookup:
                raise ValueError(f"Voice '{voice_name}' not found in voice_lookup. Available: {list(voice_lookup.keys())}")
            result.extend(voice_lookup[voice_name] * count)
        else:
            # Simple voice reference
            if part not in voice_lookup:
                raise ValueError(f"Voice '{part}' not found in voice_lookup. Available: {list(voice_lookup.keys())}")
            result.extend(voice_lookup[part])
    
    return result


def build_score_from_assignments(voice_assignments: dict, voice_data: dict, metadata: dict = None) -> dict:
    """
    Auto-generate score_data from VOICE_ASSIGNMENTS shorthand.
    
    Args:
        voice_assignments: Structure definition
            Example: {
                'Melody': {
                    'Soprano': 'V1 + transpose(V2, 5)',
                    'Alto': 'V2 * 2',
                }
            }
        voice_data: Parsed voice data
            Example: {
                'V1': voice1_events,
                'V2': voice2_events,
            }
        metadata: Optional metadata dict (title, tempo, etc.)
    
    Returns:
        Complete score_data structure ready for engraving
    
    Example:
        >>> voice_assignments = {'Melody': {'Soprano': 'V1 + V2'}}
        >>> voice_data = {'V1': [{'type': 'note'}], 'V2': [{'type': 'rest'}]}
        >>> result = build_score_from_assignments(voice_assignments, voice_data)
        >>> len(result['parts']['Melody']['Soprano'])
        2
    """
    parts = {}
    
    for staff_name, voices in voice_assignments.items():
        parts[staff_name] = {}
        for voice_name, expression in voices.items():
            parts[staff_name][voice_name] = parse_voice_assignment(expression, voice_data)
    
    score_data = {'parts': parts}
    
    if metadata:
        score_data['metadata'] = metadata
    
    return score_data


# Example usage demonstration
if __name__ == '__main__':
    # Test transformations
    test_event = [{'type': 'note', 'step': 'c', 'octave': 4, 'alter': 0, 'ql': 1.0}]
    
    # Test transpose
    transposed = transpose_events(test_event, 5)
    print(f"Original: C4")
    print(f"Transposed +5: {transposed[0]['step'].upper()}{transposed[0]['octave']}")
    
    # Test invert
    inverted = invert_events(test_event, 'c4')
    print(f"Inverted around C4: {inverted[0]['step'].upper()}{inverted[0]['octave']}")
    
    # Test retrograde
    multi_events = test_event * 3
    retro = retrograde_events(multi_events)
    print(f"Retrograde: {len(retro)} events reversed")
    
    # Test parser
    voice_data = {'V1': test_event, 'V2': test_event}
    result = parse_voice_assignment('V1 + transpose(V2, 7)', voice_data)
    print(f"\nParsed 'V1 + transpose(V2, 7)': {len(result)} events")
    
    # Test validation
    assignments = {'Melody': {'Soprano': 'INTRO + THEME'}}
    errors = validate_voice_assignments(assignments, ['INTRO', 'THEME'])
    print(f"\nValidation (should be empty): {errors}")
    
    errors = validate_voice_assignments(assignments, ['INTRO'])  # Missing THEME
    print(f"Validation (should have error): {len(errors)} error(s)")
    
    print("\n✅ All tests passed!")
