"""
Relative Octave Logic (Phase 4)
================================

Handles LilyPond's \relative mode octave calculations.

In \relative mode, pitches are calculated relative to the previous pitch,
choosing the closest pitch (within a perfect fourth).

Rules:
1. Start with the base pitch from \relative c' (or whatever is specified)
2. For each subsequent note, choose the octave that places it closest to the previous note
3. Explicit octave markers (' and ,) modify the calculated octave
4. Large leaps (> 13 semitones) are flagged as warnings

References:
- LilyPond documentation: https://lilypond.org/doc/v2.24/Documentation/notation/writing-pitches#relative-octave-entry
"""

from lily_token_parser import ParsedToken, pitch_to_midi
from typing import Tuple, List


def parse_base_pitch(base_str: str) -> Tuple[str, int]:
    """
    Parse a \relative base pitch string into pitch letter and octave.
    
    Args:
        base_str: Base pitch string (e.g., "c'", "c''", "e,,")
    
    Returns:
        Tuple of (pitch_letter, octave)
        Octave numbering: c' = C4 (middle C), c'' = C5, c = C4, c,, = C2
        
        IMPORTANT: In LilyPond, \relative c means "relative to C4" (middle C octave),
        not C3. This matches LilyPond's convention where the default octave for 
        \relative (without markers) is octave 4.
    
    Examples:
        >>> parse_base_pitch("c'")
        ('c', 5)
        >>> parse_base_pitch("c''")
        ('c', 6)
        >>> parse_base_pitch("e")
        ('e', 4)
        >>> parse_base_pitch("e,,")
        ('e', 2)
    """
    # Extract pitch letter
    pitch = base_str[0]
    
    # Count octave markers
    up_markers = base_str.count("'")
    down_markers = base_str.count(",")
    
    # Base octave: c (no markers) = C4 (middle C octave), c' = C5, c'' = C6
    # This matches LilyPond's convention where \relative c defaults to C4
    base_octave = 4
    octave = base_octave + up_markers - down_markers
    
    return (pitch, octave)


def calculate_relative_octave(prev_midi: int, current_pitch: str, current_accidental: str,
                               explicit_markers: str, prev_pitch: str = 'c') -> Tuple[int, int, bool]:
    """
    Calculate the octave for a note in \relative mode.
    
    LilyPond rule: Choose the octave that results in an interval of a fourth or less.
    When the interval is a fourth in both directions (e.g., C to G is a 4th up or 5th down),
    the tie is broken by moving in the same direction as the note names in the scale.
    
    The algorithm:
    1. Consider the current pitch in three octaves: prev_octave-1, prev_octave, prev_octave+1
    2. Choose the octave that minimizes chromatic interval (≤ 5 semitones = perfect 4th)
    3. When tied at a 4th in both directions, use diatonic direction as tiebreaker
    4. If still tied, prefer upward motion
    
    Args:
        prev_midi: MIDI note number of the previous note
        current_pitch: Pitch letter of the current note
        current_accidental: Normalized accidental ('sharp', 'flat', '', etc.)
        explicit_markers: Explicit octave markers from the token (e.g., "'", ",,")
        prev_pitch: Pitch letter of the previous note (for diatonic direction)
    
    Returns:
        Tuple of (absolute_octave, new_midi, large_leap_warning)
    """
    # Get the previous note's octave
    prev_octave = (prev_midi // 12) - 1  # Convert MIDI to octave number
    
    # Determine diatonic (scale) direction for tie-breaking
    # The "direction of the note names in the scale" means the direction of motion
    # through the natural C major scale: C-D-E-F-G-A-B-C
    # This refers to ALPHABETICAL ORDER, not the shortest diatonic path.
    # 
    # If the current pitch comes "after" the previous pitch in the alphabet
    # (moving forward in c-d-e-f-g-a-b), the scale direction is UPWARD.
    # If it comes "before" (wrapping backward), the scale direction is DOWNWARD.
    #
    # Examples:
    #   C→D: D after C, forward=1 < backward=6 → UPWARD
    #   C→G: G after C, forward=4 < backward=3? No... but G is after C!
    #
    # Wait, the issue is that C→G wrapping backward (c-b-a-g) is shorter (3 steps)
    # than going forward (c-d-e-f-g, 4 steps). But alphabetically, G comes AFTER C.
    #
    # The key insight: "alphabetical order" means we consider the sequence
    # c-d-e-f-g-a-b-c-d-e-f-g-a-b... as an infinite ascending sequence.
    # If curr_index > prev_index, we're moving forward (upward).
    # If curr_index < prev_index, we've wrapped, so check if forward wrapping
    # is more natural than backward wrapping.
    #
    # Actually, let me use a simpler rule: scale direction is upward if
    # moving forward (without considering wrapping) takes us from prev to curr.
    # That is: if (curr_index >= prev_index) OR (forward distance < backward distance)
    #
    # No wait, that's still confusing. Let me think differently:
    # For C→G: forward=4, backward=3. Even though backward is shorter,
    # G comes AFTER C in the alphabet, so scale direction is UP.
    #
    # The rule must be: scale direction is upward if curr_index > prev_index,
    # UNLESS we're wrapping so far backward that it's more natural to go backward.
    # The threshold is: if forward <= 3 (within half octave), definitely upward.
    # If forward > 3, check if we wrapped (curr_index < prev_index). If so, downward.
    #
    # Let me implement this:
    pitch_order = 'cdefgab'
    prev_index = pitch_order.index(prev_pitch.lower())
    curr_index = pitch_order.index(current_pitch.lower())
    
    # Calculate diatonic distances
    diatonic_up = (curr_index - prev_index) % 7
    diatonic_down = (prev_index - curr_index) % 7
    
    # Scale direction: upward if moving forward in the alphabet is more natural
    # Rule: if curr comes after prev without wrapping (curr > prev), it's upward
    #       if curr comes before prev (wrapped), check if forward < backward
    if curr_index > prev_index:
        # No wrapping: curr comes directly after prev in alphabet → UPWARD
        scale_direction_upward = True
    elif curr_index < prev_index:
        # Wrapped: check if forward wrapping is shorter than backward
        scale_direction_upward = diatonic_up < diatonic_down
    else:
        # Same note (unison): treat as upward
        scale_direction_upward = True
    
    # Try the current pitch in three octaves: one below, same, and one above
    candidates = []
    for test_octave in range(prev_octave - 1, prev_octave + 2):
        test_midi = pitch_to_midi(current_pitch, current_accidental, test_octave)
        
        # Calculate the signed interval (positive = up, negative = down)
        signed_interval = test_midi - prev_midi
        abs_interval = abs(signed_interval)
        
        is_downward = signed_interval < 0
        is_upward = signed_interval > 0
        
        # Check if motion matches the scale direction
        matches_scale_direction = (scale_direction_upward and is_upward) or \
                                   (not scale_direction_upward and is_downward) or \
                                   (signed_interval == 0)  # Unison always matches
        
        # Store: (abs_interval, matches_scale_direction (negated), is_downward, test_octave, test_midi)
        # Negate matches so True (matches) sorts before False (doesn't match)
        candidates.append((abs_interval, not matches_scale_direction, is_downward, test_octave, test_midi))
    
    # LilyPond rule (CORRECTED after testing):
    # 1. Choose smallest chromatic interval (≤ perfect 4th = 5 semitones)
    # 2. When intervals are equal AND one of them is a tritone (6 semitones),
    #    PREFER UPWARD MOTION (not scale direction!)
    # 3. For non-tritone ties, use scale direction as tiebreaker
    # 4. Final tiebreaker: prefer upward motion
    #
    # Key insight: The tritone (augmented 4th / diminished 5th) is a special case
    # because it's exactly halfway between octaves. LilyPond appears to resolve
    # tritone ambiguity by preferring upward motion, which is more natural for
    # melodic continuation.
    
    # Filter to options ≤ 5 semitones (perfect 4th)
    # Note: We use ≤5 as the primary filter, but will consider ≤7 as fallback
    within_fourth = [c for c in candidates if c[0] <= 5]
    within_fifth = [c for c in candidates if c[0] <= 7]
    
    if within_fourth:
        # Prefer options within a perfect 4th
        valid_candidates = within_fourth
    elif within_fifth:
        # Fallback: use options within a perfect 5th
        valid_candidates = within_fifth
    else:
        # Last resort: use all candidates
        valid_candidates = candidates
    
    # Check if we have a tritone (6 semitones) - special case
    intervals = sorted(set(c[0] for c in valid_candidates))
    has_tritone = 6 in intervals
    
    if has_tritone and len([c for c in valid_candidates if c[0] == 6]) >= 2:
        # Tritone ambiguity: multiple options at 6 semitones
        # LilyPond resolves this by preferring UPWARD motion
        # Tuple: (abs_interval, not matches_scale_direction, is_downward, test_octave, test_midi)
        # Sort by: smallest interval (x[0]), then upward motion (x[2])
        # This makes upward preferred over scale direction for tritones
        valid_candidates.sort(key=lambda x: (x[0], x[2]))
        best_abs_interval, _, _, best_octave, best_midi = valid_candidates[0]
    else:
        # Normal case: smallest interval, then scale direction, then upward
        valid_candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        best_abs_interval, _, _, best_octave, best_midi = valid_candidates[0]
    
    # Apply explicit octave markers AFTER relative calculation
    up_markers = explicit_markers.count("'")
    down_markers = explicit_markers.count(",")
    final_octave = best_octave + up_markers - down_markers
    final_midi = pitch_to_midi(current_pitch, current_accidental, final_octave)
    
    # Check for large leap (> 13 semitones)
    # BUT: if explicit markers were used, don't warn (user intended it)
    if explicit_markers:
        large_leap_warning = False  # Explicit markers mean intentional leap
    else:
        leap = abs(best_midi - prev_midi)
        large_leap_warning = leap > 13
    
    return (final_octave, final_midi, large_leap_warning)


def apply_absolute_octave_markers(base_octave: int, explicit_markers: str) -> int:
    """
    Apply explicit octave markers to a base octave (for absolute mode).
    
    Args:
        base_octave: The default octave (typically 3 for middle range)
        explicit_markers: Explicit octave markers (e.g., "'", ",,")
    
    Returns:
        Final octave number
    
    Examples:
        >>> apply_absolute_octave_markers(3, "'")
        4
        >>> apply_absolute_octave_markers(3, ",,")
        1
    """
    up_markers = explicit_markers.count("'")
    down_markers = explicit_markers.count(",")
    return base_octave + up_markers - down_markers


def process_relative_sequence(base_pitch: str, base_octave: int, 
                               tokens: List[ParsedToken]) -> List[Tuple[ParsedToken, int, bool]]:
    """
    Process a sequence of tokens in \relative mode.
    
    Args:
        base_pitch: The base pitch letter
        base_octave: The base octave number
        tokens: List of ParsedToken objects
    
    Returns:
        List of tuples: (token, absolute_octave, large_leap_warning)
    
    Examples:
        >>> from lily_token_parser import parse_token
        >>> tokens = [parse_token("c4"), parse_token("d"), parse_token("e")]
        >>> result = process_relative_sequence('c', 4, tokens)
        >>> [(t.original, oct) for t, oct, _ in result]
        [('c4', 4), ('d', 4), ('e', 4)]
    """
    results = []
    
    # Start with the base MIDI note and pitch
    current_midi = pitch_to_midi(base_pitch, '', base_octave)
    current_pitch = base_pitch
    
    for token in tokens:
        if token.is_rest:
            # Rests don't change the reference pitch
            results.append((token, 0, False))  # Octave 0 for rests (ignored)
        elif token.pitch_letter and token.pitch_letter.startswith('<'):
            # CHORD: Chords don't participate in relative octave calculation
            # They already have explicit octaves for each pitch
            # Use octave 0 as placeholder (will be ignored during conversion)
            results.append((token, 0, False))
            # Don't update reference pitch/MIDI - chords don't affect next note's octave
        else:
            # Regular note: Calculate relative octave
            octave, new_midi, large_leap = calculate_relative_octave(
                current_midi,
                token.pitch_letter,
                token.accidental,
                token.octave_markers,
                current_pitch  # Pass previous pitch for alphabetical comparison
            )
            
            results.append((token, octave, large_leap))
            
            # Update reference pitch for next note
            current_midi = new_midi
            current_pitch = token.pitch_letter
    
    return results


def process_absolute_sequence(base_octave: int, tokens: List[ParsedToken]) -> List[Tuple[ParsedToken, int, bool]]:
    """
    Process a sequence of tokens in absolute mode (no \relative).
    
    Args:
        base_octave: The default octave (typically 3)
        tokens: List of ParsedToken objects
    
    Returns:
        List of tuples: (token, absolute_octave, large_leap_warning)
    """
    results = []
    prev_midi = None
    
    for token in tokens:
        if token.is_rest:
            results.append((token, 0, False))
        else:
            octave = apply_absolute_octave_markers(base_octave, token.octave_markers)
            current_midi = pitch_to_midi(token.pitch_letter, token.accidental, octave)
            
            # Check for large leap
            large_leap = False
            if prev_midi is not None:
                leap = abs(current_midi - prev_midi)
                large_leap = leap > 13
            
            results.append((token, octave, large_leap))
            prev_midi = current_midi
    
    return results


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    from lily_token_parser import parse_token
    
    print("=== Relative Octave Logic Test ===\n")
    
    # Test 1: Simple C major scale in relative mode
    print("Test 1: C Major Scale (\\relative c')")
    tokens = [parse_token(t) for t in ["c4", "d", "e", "f", "g", "a", "b", "c"]]
    results = process_relative_sequence('c', 4, tokens)
    
    for token, octave, large_leap in results:
        pitch = token.pitch_letter.upper() if token.pitch_letter else "R"
        print(f"  {token.original:6} -> {pitch}{octave}  {'⚠️ LARGE LEAP' if large_leap else ''}")
    
    print()
    
    # Test 2: With localized accidentals and rests
    print("Test 2: Real-world example (\\relative e)")
    tokens = [parse_token(t) for t in ["e2", "bmol4", "c2", "r4"]]
    results = process_relative_sequence('e', 3, tokens)
    
    for token, octave, large_leap in results:
        if token.is_rest:
            print(f"  {token.original:6} -> rest")
        else:
            pitch = token.pitch_letter.upper()
            acc = token.accidental
            acc_str = {'sharp': '#', 'flat': '-', '': ''}. get(acc, acc)
            print(f"  {token.original:6} -> {pitch}{acc_str}{octave}  {'⚠️ LARGE LEAP' if large_leap else ''}")
            if token.warnings:
                print(f"           Warnings: {token.warnings}")
    
    print()
    
    # Test 3: Large leap detection
    print("Test 3: Large leap (\\relative c)")
    tokens = [parse_token(t) for t in ["c4", "c'''4"]]  # C3 to C6 = 36 semitones!
    results = process_relative_sequence('c', 3, tokens)
    
    for token, octave, large_leap in results:
        pitch = token.pitch_letter.upper()
        print(f"  {token.original:6} -> {pitch}{octave}  {'⚠️ LARGE LEAP' if large_leap else ''}")
