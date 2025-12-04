#!/usr/bin/env python3
import re

# Test different suffix patterns
test = "~g16"

# Current (broken)
pattern_broken = r"~?[a-gr](?:isis|ises|eses|is|es|bmol|mol|\#|b)?[',]*\d*\.?\([^)]*\)?~?"
# Should be: optional group for the entire container
pattern_fixed = r"~?[a-gr](?:isis|ises|eses|is|es|bmol|mol|\#|b)?[',]*\d*\.?(?:\([^)]*\))?~?"

m_broken = re.match(pattern_broken, test)
m_fixed = re.match(pattern_fixed, test)

print(f"Broken pattern match: {m_broken}")
print(f"Fixed pattern match: {m_fixed}")
if m_fixed:
    print(f"  Matched: '{m_fixed.group()}'")

# Test with container
test2 = "c4(.)"
m2 = re.match(pattern_fixed, test2)
print(f"\nTest with container: {test2}")
print(f"Fixed pattern match: {m2}")
if m2:
    print(f"  Matched: '{m2.group()}'")

# Test with container and tie
test3 = "a2(p, >)~"
m3 = re.match(pattern_fixed, test3)
print(f"\nTest with container and tie: {test3}")
print(f"Fixed pattern match: {m3}")
if m3:
    print(f"  Matched: '{m3.group()}'")
