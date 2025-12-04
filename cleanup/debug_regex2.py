#!/usr/bin/env python3
import re

# Simplified test
pattern1 = r"~?[a-gr](?:isis|ises|eses|is|es|bmol|mol|\#|b)?[',]*\d*\.?\([^)]*\)?~?"
pattern2 = r'~?[a-gr](?:isis|ises|eses|is|es|bmol|mol|\#|b)?[' + r"',]*" + r'\d*\.?\([^)]*\)?~?'

test = "~g16"
m1 = re.match(pattern1, test)
m2 = re.match(pattern2, test)

print(f"Pattern1 match: {m1}")
if m1:
    print(f"  Matched: '{m1.group()}'")
print(f"Pattern2 match: {m2}")
if m2:
    print(f"  Matched: '{m2.group()}'")

# Try even simpler
pattern3 = r"~?[a-gr][',]*\d*"
m3 = re.match(pattern3, test)
print(f"Pattern3 match: {m3}")
if m3:
    print(f"  Matched: '{m3.group()}'")
