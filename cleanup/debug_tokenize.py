#!/usr/bin/env python3
from lily_tokenizer import tokenize_body
from lily_token_parser import parse_token

# Test simple tokenization
print("Test 1: Simple note with container")
tokens = tokenize_body(r"{ c4(.) }")
print(f"Tokens: {tokens}")
for token in tokens:
    parsed = parse_token(token)
    print(f"Parsed: {parsed}")
print()

# Test grace note
print("Test 2: Grace note")
tokens = tokenize_body(r"{ ~g16 a2(f) }")
print(f"Tokens: {tokens}")
for token in tokens:
    parsed = parse_token(token)
    print(f"Token: {token}")
    print(f"Parsed: step={parsed.pitch_letter}, is_grace={parsed.is_grace}, dynamics={parsed.dynamics}")
