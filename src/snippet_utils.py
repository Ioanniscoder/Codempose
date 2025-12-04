"""
Snippet utility functions for LilyPond code analysis.

Provides simple, parser-independent duration calculation based on musical structure
(barlines and time signatures) rather than complex event summing.
"""

import re
from typing import Dict


def calculate_snippet_duration_from_barlines(lily_string: str) -> Dict[str, float]:
    """
    Calculate snippet duration by counting barlines and using time signature.
    
    This approach is:
    - Simple: Just count | characters
    - Reliable: Independent of parser internals
    - Musical: Matches how composers think in measures
    
    Args:
        lily_string: LilyPond notation string
        
    Returns:
        dict with keys:
            - 'bars': int (number of measures)
            - 'time_signature': str (e.g., "3/4")
            - 'ql_per_bar': float (quarter lengths per bar)
            - 'total_ql': float (total duration in quarter lengths)
    
    Example:
        >>> snippet = r'''
        ... \\time 3/4
        ... d4 e4 f4 |
        ... g4 a4 b4 |
        ... '''
        >>> result = calculate_snippet_duration_from_barlines(snippet)
        >>> result['total_ql']
        6.0  # 2 bars × 3 QL/bar
    """
    # Extract time signature (default 4/4)
    time_match = re.search(r'\\time\s+(\d+)/(\d+)', lily_string)
    if time_match:
        numerator = int(time_match.group(1))
        denominator = int(time_match.group(2))
        time_sig = f"{numerator}/{denominator}"
        # Convert to quarter lengths: numerator / (denominator/4)
        ql_per_bar = numerator * (4.0 / denominator)
    else:
        time_sig = "4/4"
        ql_per_bar = 4.0
    
    # Count explicit barlines (|)
    # Strategy: Count single | but not || (double barline)
    single_bar_count = lily_string.count('|') - (2 * lily_string.count('||'))
    
    # Add 1 for implied final barline (unless snippet ends with ||)
    if '||' in lily_string and lily_string.rstrip().endswith('||'):
        bars = single_bar_count + 1  # || counts as one bar boundary
    else:
        bars = single_bar_count + 1  # Add implied final barline
    
    total_ql = bars * ql_per_bar
    
    return {
        'bars': bars,
        'time_signature': time_sig,
        'ql_per_bar': ql_per_bar,
        'total_ql': total_ql
    }
