#!/usr/bin/env python3
from lily_tokenizer import tokenize_body
from lily_token_parser import parse_token

# Parse tokens
body = r"{ a2(p, themeA, >) a2~ a2(f) r4 }"
tokens = tokenize_body(body)

print("Tokens:")
for i, token in enumerate(tokens):
    print(f"  {i}: '{token}'")
    parsed = parse_token(token)
    print(f"     pitch={parsed.pitch_letter}, has_tie={parsed.has_tie}, dynamics={parsed.dynamics}, articulations={parsed.articulations}")
