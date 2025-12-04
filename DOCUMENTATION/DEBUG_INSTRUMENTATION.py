#!/usr/bin/env python3
"""
Debug instrumentation for score_builder.py
Add this code temporarily to trace execution flow
"""

# Add at start of build_score_from_blueprint() function (around line 600):
print("\n" + "="*80)
print("DEBUG: Starting build_score_from_blueprint()")
print(f"DEBUG: Layout: {layout}")
print(f"DEBUG: Number of sections: {len(sections)}")
print("="*80)

# Add in section loop (around line 608):
print(f"\n{'='*80}")
print(f"DEBUG: SECTION {section_idx + 1} of {len(sections)}")
print(f"DEBUG: Section content: {section}")
print(f"{'='*80}")

# Add in staff loop (around line 614):
print(f"\n  DEBUG: Processing STAFF {staff_idx}: {staff_name}")
print(f"  DEBUG: is_top_staff: {is_top_staff}")
print(f"  DEBUG: staff_content: {staff_content}")
print(f"  DEBUG: staff_content type: {type(staff_content)}")
if staff_content:
    print(f"  DEBUG: staff_content[0] type: {type(staff_content[0]) if staff_content else 'N/A'}")

# Add at each execution path entry:

# Path 1 (Multi-voice):
print(f"  DEBUG: *** TAKING PATH 1: MULTI-VOICE STAFF ***")

# Path 2 (Single voice in parentheses):
print(f"  DEBUG: *** TAKING PATH 2: SINGLE VOICE IN PARENTHESES ***")

# Path 3 (Simple single-voice):
print(f"  DEBUG: *** TAKING PATH 3: SIMPLE SINGLE-VOICE STAFF ***")

# Add when collecting events (Path 3, around line 710):
print(f"    DEBUG: Before processing snippets, staff_events length: {len(staff_events)}")

# Add after processing each snippet (Path 3, around line 745):
print(f"    DEBUG: After {snippet_name}, staff_events length: {len(staff_events)}")

# Add after calculating duration (around line 748):
print(f"    DEBUG: Section duration for {staff_name}: {total_ql} QL")
print(f"    DEBUG: parts['{staff_name}'] length before extend: {len(parts[staff_name])}")

# Add after extending parts (Path 3, around line 750):
print(f"    DEBUG: parts['{staff_name}'] length after extend: {len(parts[staff_name])}")

# Add after adding barlines (around line 820):
print(f"\n  DEBUG: After section {section_idx + 1}, barline added")
for staff_name in parts.keys():
    last_event = parts[staff_name][-1] if parts[staff_name] else None
    print(f"    DEBUG: parts['{staff_name}'][-1] = {last_event}")
    print(f"    DEBUG: parts['{staff_name}'] total events: {len(parts[staff_name])}")

# Add at end of function (around line 830):
print("\n" + "="*80)
print("DEBUG: Blueprint assembly complete - FINAL STATE:")
for staff_name, events in parts.items():
    barline_count = sum(1 for e in events if e.get('type') == 'barline')
    total_ql = sum(e.get('ql', 0) for e in events if e.get('type') != 'barline')
    print(f"  {staff_name}:")
    print(f"    Total events: {len(events)}")
    print(f"    Barline events: {barline_count}")
    print(f"    Total QL (event sum): {total_ql}")
    print(f"    First 3 events: {events[:3]}")
    print(f"    Last 3 events: {events[-3:]}")
print("="*80)
