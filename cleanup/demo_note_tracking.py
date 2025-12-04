"""
Note Tracking System - Explanation and Demo
=============================================

The Codempose system includes a sophisticated note tracking feature that 
preserves the connection between:
1. Original input tokens (LilyPond or TinyNotation)
2. Parsed/converted representations
3. Final music21 events
4. Generated LilyPond output

This creates a complete audit trail for debugging and analysis.
"""

# Test with a LilyPond snippet that includes warnings
SOURCE_MELODY_LILY = r"\relative e { e2 bmol4 c2 r4 | fis2 e'4 }"

if __name__ == '__main__':
    import sys
    import json
    sys.path.insert(0, '/workspaces/Codempose')
    
    from lilypond_parser import parse_lilypond_to_data
    
    print("="*70)
    print("NOTE TRACKING DEMONSTRATION")
    print("="*70)
    print()
    print("Input:", SOURCE_MELODY_LILY)
    print()
    
    # Parse the snippet
    score_data = parse_lilypond_to_data(SOURCE_MELODY_LILY, 'Test Part')
    
    # Show metadata with parser tokens
    print("METADATA:")
    print("-" * 70)
    metadata = score_data['metadata']
    print(f"Original Input: {metadata.get('original_input', 'N/A')}")
    print(f"Time Signature: {metadata.get('time_signature', 'N/A')}")
    print(f"Warnings: {metadata.get('warnings', [])}")
    print()
    
    # Show parser tokens (tracking data)
    if 'parser_tokens' in metadata:
        print("PARSER TOKENS (conversion tracking):")
        print("-" * 70)
        print(f"{'#':<4} {'Original':<15} {'Converted':<20} {'Warnings':<30}")
        print("-" * 70)
        for i, token in enumerate(metadata['parser_tokens']):
            warnings_str = ', '.join(token['warnings']) if token['warnings'] else '—'
            print(f"{i:<4} {token['original']:<15} {token['converted']:<20} {warnings_str:<30}")
        print()
    
    # Show final events (what music21 sees)
    print("FINAL EVENTS (music21 representation):")
    print("-" * 70)
    print(f"{'#':<4} {'Type':<8} {'Pitch':<10} {'Octave':<7} {'Alter':<6} {'QL':<5} {'Original':<15}")
    print("-" * 70)
    events = score_data['parts']['Test Part']
    for i, event in enumerate(events):
        event_type = event.get('type', '?')
        if event_type == 'note':
            pitch = event.get('step', '?')
            octave = event.get('octave', '?')
            alter = event.get('alter', 0)
            alter_str = {1.0: '#', -1.0: 'b', 0: '♮'}.get(alter, str(alter))
        else:
            pitch = '—'
            octave = '—'
            alter_str = '—'
        
        ql = event.get('ql', '?')
        original = event.get('original_token', '?')
        
        print(f"{i:<4} {event_type:<8} {pitch:<10} {octave:<7} {alter_str:<6} {ql:<5} {original:<15}")
    
    print()
    print("="*70)
    print("KEY INSIGHTS:")
    print("="*70)
    print()
    print("1. TRACKING FLOW:")
    print("   Original → Parser → Converter → music21 → Events")
    print()
    print("2. EACH EVENT KNOWS:")
    print("   - Its original input token (e.g., 'bmol4')")
    print("   - Its position in the sequence")
    print("   - Any warnings during parsing")
    print("   - The final pitch, octave, and duration")
    print()
    print("3. BENEFITS:")
    print("   - Debug parser issues")
    print("   - Trace conversion problems")
    print("   - Validate transformations")
    print("   - Understand relative octave logic")
    print()
    print("4. METADATA STRUCTURE:")
    print("   score_data = {")
    print("       'metadata': {")
    print("           'original_input': '...',")
    print("           'parser_tokens': [...]  # <-- TRACKING DATA")
    print("           'warnings': [...]")
    print("       },")
    print("       'parts': {")
    print("           'Part Name': [")
    print("               {")
    print("                   'original_token': '...',  # <-- TRACK BACK")
    print("                   'position': 0,")
    print("                   'type': 'note',")
    print("                   'step': 'E',")
    print("                   'octave': 4,")
    print("                   ...") 
    print("               }")
    print("           ]")
    print("       }")
    print("   }")
    print()
    print("="*70)
