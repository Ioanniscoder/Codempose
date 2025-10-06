"""Convert event dictionaries to LilyPond notation."""

def events_to_lily(events):
    """
    Convert a list of event dictionaries to LilyPond notation.
    
    Args:
        events: List of event dictionaries with 'pitch' and 'duration' keys
        
    Returns:
        String of LilyPond notation
    """
    lily_parts = []
    
    for event in events:
        pitch = event.get('pitch', 'c')
        duration = event.get('duration', 4)
        
        # Convert duration to LilyPond format
        lily_parts.append(f"{pitch}{duration}")
    
    return ' '.join(lily_parts)
