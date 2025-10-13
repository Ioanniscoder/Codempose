"""Voice documentation helper for programmatic composition."""

def register_and_document_voice(name, events, voice_lookup, metadata):
    """
    Register a programmatic voice and document it in metadata.
    
    Args:
        name: Voice name (string)
        events: List of event dictionaries
        voice_lookup: Dictionary to store the voice
        metadata: Metadata dictionary to store documentation
    """
    from lily_converter import events_to_lily
    
    # Register the voice
    voice_lookup[name] = events
    
    # Document it in metadata
    if 'programmatic_voices' not in metadata:
        metadata['programmatic_voices'] = {}
    
    # Convert events to LilyPond notation for documentation (with metadata context)
    lily_notation = events_to_lily(events, metadata)
    
    metadata['programmatic_voices'][name] = {
        'events': events,
        'lilypond': lily_notation
    }

