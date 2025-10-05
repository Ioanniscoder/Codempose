"""
Data structures for LilyPond shorthand → TinyNotation conversion.

This module defines the result types returned by the parser, allowing
rich metadata to be preserved alongside the musical output.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class TokenInfo:
    """Metadata about a single parsed token from LilyPond shorthand.
    
    Attributes:
        original: The original LilyPond token string (e.g., "bmol4", "f#8")
        converted: The TinyNotation output (e.g., "Bb4", "F#8")
        position: Zero-based position in the token sequence
        warnings: List of human-readable warning messages for this token
        pitch_leap: Semitone interval from previous note (None for rests/first note)
    """
    original: str
    converted: str
    position: int
    warnings: List[str] = field(default_factory=list)
    pitch_leap: Optional[int] = None
    
    def has_warning(self) -> bool:
        """Returns True if this token has any warnings."""
        return bool(self.warnings)
    
    def is_flagged(self) -> bool:
        """Returns True if this token should be reviewed (has warnings or large leap)."""
        return self.has_warning() or (self.pitch_leap is not None and abs(self.pitch_leap) > 6)


@dataclass
class ParseResult:
    """Complete result of LilyPond shorthand → TinyNotation conversion.
    
    This object contains both the clean TinyNotation string for music21
    and rich diagnostic metadata for review and debugging.
    
    Attributes:
        tiny_notation: The complete TinyNotation string (e.g., "6/4 E2 Bb4 C2 r4")
        tokens: Detailed metadata for each parsed token
        directives: Extracted directives like time signature, key, tempo
        warnings: Global warnings not tied to a specific token
        success: Whether the conversion completed successfully
    """
    tiny_notation: str = ""
    tokens: List[TokenInfo] = field(default_factory=list)
    directives: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    success: bool = True
    
    def has_warnings(self) -> bool:
        """Check if any tokens have warnings or if there are global warnings."""
        return bool(self.warnings) or any(t.has_warning() for t in self.tokens)
    
    def flagged_tokens(self) -> List[TokenInfo]:
        """Return list of tokens that need review (warnings or large leaps)."""
        return [t for t in self.tokens if t.is_flagged()]
    
    def format_review(self) -> str:
        """Generate a human-readable review report.
        
        Returns:
            Multi-line string with conversion details and warnings
        """
        lines = ["=" * 60]
        lines.append("LILYPOND → TINYNOTATION CONVERSION REVIEW")
        lines.append("=" * 60)
        lines.append(f"\n✓ TinyNotation Output:\n  {self.tiny_notation}\n")
        
        # Directives
        if self.directives:
            lines.append("📋 Directives:")
            for key, value in self.directives.items():
                lines.append(f"  • {key}: {value}")
            lines.append("")
        
        # Token details
        lines.append("🎵 Token Conversion Details:")
        for token in self.tokens:
            marker = "  "
            if token.has_warning():
                marker = "⚠️ "
            elif token.pitch_leap and abs(token.pitch_leap) > 6:
                marker = "📊"
            
            line = f"{marker}{token.position + 1:2d}. {token.original:12s} → {token.converted:8s}"
            
            # Add leap info
            if token.pitch_leap is not None:
                direction = "↑" if token.pitch_leap > 0 else "↓"
                line += f"  [{direction}{abs(token.pitch_leap):2d} semitones]"
            
            lines.append(line)
            
            # Add warnings indented
            for warning in token.warnings:
                lines.append(f"      └─ ⚠️  {warning}")
        
        # Global warnings
        if self.warnings:
            lines.append("\n⚠️  Global Warnings:")
            for warning in self.warnings:
                lines.append(f"  • {warning}")
        
        # Summary
        lines.append("\n" + "=" * 60)
        flagged = self.flagged_tokens()
        if flagged:
            lines.append(f"⚠️  {len(flagged)} token(s) flagged for review")
        else:
            lines.append("✓ No tokens flagged for review")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_inline_annotated(self) -> str:
        """Format TinyNotation with inline warning markers.
        
        Returns:
            TinyNotation string with [⚠️] or [↗️] markers after flagged tokens
        """
        parts = []
        for token in self.tokens:
            token_str = token.converted
            if token.has_warning():
                token_str += "[⚠️]"
            elif token.pitch_leap and abs(token.pitch_leap) > 6:
                token_str += "[↗️]"
            parts.append(token_str)
        
        time_sig = self.directives.get('time', '4/4')
        return f"{time_sig} {' '.join(parts)}"
    
    def to_dict(self) -> dict:
        """Export as a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for json.dump()
        """
        return {
            "tiny_notation": self.tiny_notation,
            "success": self.success,
            "tokens": [
                {
                    "position": t.position,
                    "original": t.original,
                    "converted": t.converted,
                    "warnings": t.warnings,
                    "pitch_leap": t.pitch_leap
                }
                for t in self.tokens
            ],
            "directives": self.directives,
            "warnings": self.warnings,
            "flagged_count": len(self.flagged_tokens())
        }
