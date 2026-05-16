"""
LilyPond ↔ music21 Hybrid with theory-guided cost optimization
==============================================================
- Parses LilyPond snippets (including \relative mode and chords).
- Builds a shared feature representation from music21 parts.
- Evaluates measurable musical-theory rules.
- Applies configurable cost-based optimization.
- Exports optimized output with Abjad/LilyPond.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import subprocess
from typing import Dict, List, Optional, Tuple

import abjad
import music21


# ==============================
# LilyPond → music21 parser
# ==============================
def parse_lilypond_snippet(snippet: str) -> music21.stream.Part:
    """Parses a LilyPond snippet, including \relative mode and chords."""
    snippet = snippet.strip()
    m = re.match(r"\\relative\s+([a-g][eis]*[,']*)\s*\{(.+)\}", snippet, re.DOTALL)
    if m:
        base = m.group(1).strip()
        body = m.group(2).strip()
        return _parse_relative_block(base, body)
    return _parse_absolute_block(snippet)


def _get_tokens(body: str) -> List[str]:
    token_regex = r"<[^>]+>\d*\.?|[a-gr][eis]*[,']*\d*\.?|\|"
    return re.findall(token_regex, body)


def _parse_relative_block(base_pitch: str, body: str) -> music21.stream.Part:
    part = music21.stream.Part()
    ref_note = _parse_note_token(base_pitch)
    if not isinstance(ref_note, music21.note.Note):
        raise ValueError(f"Invalid base pitch for relative: {base_pitch}")

    last_pitch = ref_note.pitch
    tokens = _get_tokens(body)

    for tok in tokens:
        if tok.startswith("<"):
            element = _parse_chord_token(tok, last_pitch)
            if element:
                last_pitch = element.pitches[-1]
                part.append(element)
        else:
            element = _resolve_relative(tok, last_pitch)
            if element:
                if isinstance(element, music21.note.Note):
                    last_pitch = element.pitch
                part.append(element)
    return part


def _parse_absolute_block(snippet: str) -> music21.stream.Part:
    part = music21.stream.Part()
    tokens = _get_tokens(snippet)
    for tok in tokens:
        if tok.startswith("<"):
            element = _parse_chord_token(tok)
            if element:
                part.append(element)
        else:
            element = _parse_note_token(tok)
            if element:
                part.append(element)
    return part


def _resolve_relative(tok: str, last_pitch: music21.pitch.Pitch, ql: float = None):
    n = _parse_note_token(tok, ql)
    if isinstance(n, music21.note.Note):
        cand = n.pitch
        cand.octave = last_pitch.octave
        while cand.ps - last_pitch.ps > 6:
            cand.octave -= 1
        while last_pitch.ps - cand.ps > 6:
            cand.octave += 1
        n.pitch = cand
    return n


def _parse_duration(dur_token: str) -> float:
    if not dur_token:
        return 1.0
    base = int(re.sub(r"\D", "", dur_token))
    ql = 4 / base
    if "." in dur_token:
        ql *= 1.5
    return ql


def _parse_note_token(tok: str, ql: float = None):
    m = re.match(r"([a-gr][eis]*[,']*)(\d+\.?)?", tok)
    if not m:
        return None
    pitch_token, dur_token = m.groups()
    if ql is None:
        ql = _parse_duration(dur_token)
    if pitch_token.startswith("r"):
        return music21.note.Rest(quarterLength=ql)
    step = pitch_token[0].upper()
    acc = ""
    if "is" in pitch_token:
        acc = "#"
    elif "es" in pitch_token:
        acc = "-"
    octave_shift = pitch_token.count("'") - pitch_token.count(",")
    octave = 4 + octave_shift
    return music21.note.Note(f"{step}{acc}{octave}", quarterLength=ql)


def _parse_chord_token(tok: str, last_pitch: music21.pitch.Pitch = None):
    m = re.fullmatch(r"<([^>]*)>(\d+\.?)?", tok)
    if not m:
        return None
    chord_body, dur_token = m.groups()
    ql = _parse_duration(dur_token)
    chord_pitches = []

    temp_last_pitch = last_pitch
    for t in chord_body.split():
        if last_pitch:
            n = _resolve_relative(t, temp_last_pitch, ql)
            if isinstance(n, music21.note.Note):
                temp_last_pitch = n.pitch
                chord_pitches.append(n.pitch)
        else:
            n = _parse_note_token(t, ql)
            if isinstance(n, music21.note.Note):
                chord_pitches.append(n.pitch)
    if chord_pitches:
        return music21.chord.Chord(chord_pitches, quarterLength=ql)
    return None


# ==============================
# Shared representation layer
# ==============================
@dataclass
class Event:
    offset: float
    ql: float
    event_type: str
    midi: Optional[int] = None
    midi_list: Optional[List[int]] = None


def build_event_representation(part: music21.stream.Part) -> List[Event]:
    events: List[Event] = []
    for el in part.flatten().notesAndRests:
        if isinstance(el, music21.note.Note):
            events.append(
                Event(
                    offset=float(el.offset),
                    ql=float(el.quarterLength),
                    event_type="note",
                    midi=int(el.pitch.midi),
                )
            )
        elif isinstance(el, music21.chord.Chord):
            events.append(
                Event(
                    offset=float(el.offset),
                    ql=float(el.quarterLength),
                    event_type="chord",
                    midi_list=[int(p.midi) for p in el.pitches],
                )
            )
        elif isinstance(el, music21.note.Rest):
            events.append(
                Event(
                    offset=float(el.offset),
                    ql=float(el.quarterLength),
                    event_type="rest",
                )
            )
    return events


def _nearest_harmony_pitches_at_offset(harmony_events: List[Event], offset: float) -> List[int]:
    for ev in harmony_events:
        start, end = ev.offset, ev.offset + ev.ql
        if start <= offset < end:
            if ev.event_type == "chord" and ev.midi_list:
                return ev.midi_list
            if ev.event_type == "note" and ev.midi is not None:
                return [ev.midi]
    return []


def _melody_notes(events: List[Event]) -> List[Event]:
    return [e for e in events if e.event_type == "note" and e.midi is not None]


def _max_consecutive_leaps(note_midis: List[int], leap_threshold: int = 6) -> int:
    max_run = 0
    run = 0
    for i in range(1, len(note_midis)):
        if abs(note_midis[i] - note_midis[i - 1]) > leap_threshold:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    return max_run


def extract_theory_features(melody: music21.stream.Part, harmony: music21.stream.Part) -> Dict[str, float]:
    melody_events = build_event_representation(melody)
    harmony_events = build_event_representation(harmony)

    melody_notes = _melody_notes(melody_events)
    note_midis = [n.midi for n in melody_notes if n.midi is not None]

    if len(note_midis) < 2:
        return {
            "stepwise_motion_ratio": 0.0,
            "leap_ratio": 0.0,
            "contour_coherence": 0.0,
            "consonance_ratio": 0.0,
            "cadence_strength": 0.0,
            "rhythmic_variety": 0.0,
            "rhythmic_stability": 0.0,
            "tonal_center_fit": 0.0,
            "max_consecutive_leaps": 0.0,
        }

    intervals = [abs(note_midis[i] - note_midis[i - 1]) for i in range(1, len(note_midis))]
    stepwise_motion_ratio = sum(1 for i in intervals if i <= 2) / len(intervals)
    leap_ratio = sum(1 for i in intervals if i > 5) / len(intervals)

    directions = []
    for i in range(1, len(note_midis)):
        delta = note_midis[i] - note_midis[i - 1]
        if delta > 0:
            directions.append(1)
        elif delta < 0:
            directions.append(-1)
        else:
            directions.append(0)
    if len(directions) <= 1:
        contour_coherence = 1.0
    else:
        direction_changes = sum(1 for i in range(1, len(directions)) if directions[i] != directions[i - 1])
        contour_coherence = 1.0 - (direction_changes / (len(directions) - 1))

    consonant_classes = {0, 3, 4, 7, 8, 9}
    consonant_hits = 0
    vertical_checks = 0
    for n in melody_notes:
        harmony_pitches = _nearest_harmony_pitches_at_offset(harmony_events, n.offset)
        if not harmony_pitches:
            continue
        min_class = min(abs((n.midi - hp) % 12) for hp in harmony_pitches)
        vertical_checks += 1
        if min_class in consonant_classes:
            consonant_hits += 1
    consonance_ratio = consonant_hits / vertical_checks if vertical_checks else 0.0

    final_harmony = [e for e in harmony_events if e.event_type in {"note", "chord"}]
    if melody_notes and final_harmony:
        final_note_pc = melody_notes[-1].midi % 12
        last_harmony = final_harmony[-1]
        last_harmony_pcs = (
            [m % 12 for m in last_harmony.midi_list]
            if last_harmony.midi_list
            else [last_harmony.midi % 12] if last_harmony.midi is not None else []
        )
        cadence_strength = 1.0 if final_note_pc in last_harmony_pcs else 0.0
    else:
        cadence_strength = 0.0

    durations = [e.ql for e in melody_events if e.event_type in {"note", "rest"}]
    rhythmic_variety = len(set(durations)) / max(1, len(durations))
    rhythmic_stability = sum(1 for n in melody_notes if math.isclose(n.offset % 1, 0.0, abs_tol=1e-9)) / max(1, len(melody_notes))

    major_scale_pcs = {0, 2, 4, 5, 7, 9, 11}
    tonal_center_fit = sum(1 for m in note_midis if (m % 12) in major_scale_pcs) / len(note_midis)

    max_consecutive_leaps = float(_max_consecutive_leaps(note_midis))

    return {
        "stepwise_motion_ratio": stepwise_motion_ratio,
        "leap_ratio": leap_ratio,
        "contour_coherence": contour_coherence,
        "consonance_ratio": consonance_ratio,
        "cadence_strength": cadence_strength,
        "rhythmic_variety": rhythmic_variety,
        "rhythmic_stability": rhythmic_stability,
        "tonal_center_fit": tonal_center_fit,
        "max_consecutive_leaps": max_consecutive_leaps,
    }


THEORY_RULE_CATALOG: Dict[str, Dict[str, str]] = {
    "balanced_melodic_motion": {
        "feature": "stepwise_motion_ratio + leap_ratio",
        "description": "Prefer mostly stepwise melodic motion while limiting excessive leaps.",
        "target": "stepwise_motion_ratio >= 0.45 and leap_ratio <= 0.25",
    },
    "vertical_consonance": {
        "feature": "consonance_ratio",
        "description": "Prefer consonant melody-harmony vertical intervals.",
        "target": "consonance_ratio >= 0.60",
    },
    "cadential_closure": {
        "feature": "cadence_strength",
        "description": "Prefer final melody pitch to resolve into final harmony sonority.",
        "target": "cadence_strength = 1.0",
    },
    "rhythmic_shape": {
        "feature": "rhythmic_variety + rhythmic_stability",
        "description": "Balance rhythmic variety with stable metric anchoring.",
        "target": "rhythmic_variety >= 0.25 and rhythmic_stability >= 0.50",
    },
    "tonal_fit": {
        "feature": "tonal_center_fit",
        "description": "Prefer pitch content consistent with tonic collection.",
        "target": "tonal_center_fit >= 0.75",
    },
}


def evaluate_theory_penalties(features: Dict[str, float]) -> Dict[str, float]:
    penalties = {
        "excessive_leaps": max(0.0, features["leap_ratio"] - 0.25),
        "insufficient_stepwise_motion": max(0.0, 0.45 - features["stepwise_motion_ratio"]),
        "weak_vertical_consonance": max(0.0, 0.60 - features["consonance_ratio"]),
        "weak_cadence": max(0.0, 1.0 - features["cadence_strength"]),
        "low_rhythmic_variety": max(0.0, 0.25 - features["rhythmic_variety"]),
        "low_rhythmic_stability": max(0.0, 0.50 - features["rhythmic_stability"]),
        "poor_tonal_fit": max(0.0, 0.75 - features["tonal_center_fit"]),
        "low_contour_coherence": max(0.0, 0.35 - features["contour_coherence"]),
    }
    return {k: min(1.0, v) for k, v in penalties.items()}


# ==============================
# Cost-based model
# ==============================
DEFAULT_COST_MODEL = {
    "weights": {
        "excessive_leaps": 1.1,
        "insufficient_stepwise_motion": 0.8,
        "weak_vertical_consonance": 1.4,
        "weak_cadence": 1.2,
        "low_rhythmic_variety": 0.7,
        "low_rhythmic_stability": 0.6,
        "poor_tonal_fit": 1.3,
        "low_contour_coherence": 0.7,
        "complexity_penalty": 0.9,
        "novelty_penalty": 0.4,
    },
    "hard_constraints": {
        "max_consecutive_leaps": 2.0,
        "min_consonance_ratio": 0.40,
    },
    "hard_violation_cost": 100.0,
}


def _complexity_penalty(melody: music21.stream.Part) -> float:
    notes = [n for n in melody.flatten().notes if isinstance(n, music21.note.Note)]
    if len(notes) <= 1:
        return 0.0
    intervals = [abs(notes[i].pitch.midi - notes[i - 1].pitch.midi) for i in range(1, len(notes))]
    avg_interval = sum(intervals) / len(intervals)
    return min(1.0, max(0.0, (avg_interval - 4.0) / 12.0))


def _novelty_penalty(candidate: music21.stream.Part, source: music21.stream.Part) -> float:
    c_notes = [n.pitch.midi for n in candidate.flatten().notes if isinstance(n, music21.note.Note)]
    s_notes = [n.pitch.midi for n in source.flatten().notes if isinstance(n, music21.note.Note)]
    if not c_notes or not s_notes or len(c_notes) != len(s_notes):
        return 0.5
    diff = sum(abs(c_notes[i] - s_notes[i]) for i in range(len(c_notes)))
    normalized = diff / (len(c_notes) * 12.0)
    return min(1.0, normalized)


def score_candidate(
    candidate_melody: music21.stream.Part,
    source_melody: music21.stream.Part,
    harmony: music21.stream.Part,
    model: Dict,
) -> Dict:
    features = extract_theory_features(candidate_melody, harmony)
    penalties = evaluate_theory_penalties(features)
    penalties["complexity_penalty"] = _complexity_penalty(candidate_melody)
    penalties["novelty_penalty"] = _novelty_penalty(candidate_melody, source_melody)

    hard_violations = []
    if features["max_consecutive_leaps"] > model["hard_constraints"]["max_consecutive_leaps"]:
        hard_violations.append("max_consecutive_leaps")
    if features["consonance_ratio"] < model["hard_constraints"]["min_consonance_ratio"]:
        hard_violations.append("min_consonance_ratio")

    weighted_cost = 0.0
    for k, v in penalties.items():
        weighted_cost += model["weights"].get(k, 1.0) * min(1.0, max(0.0, v))

    if hard_violations:
        weighted_cost += model["hard_violation_cost"]

    return {
        "total_cost": weighted_cost,
        "features": features,
        "penalties": penalties,
        "hard_violations": hard_violations,
    }


# ==============================
# Optimization strategies
# ==============================
TRANSFORMATION_INTERVALS = ["P1", "m2", "M2", "m3", "M3", "P4", "P5", "-m2", "-M2", "-m3"]


def _safe_transpose(part: music21.stream.Part, interval_name: str) -> music21.stream.Part:
    return part.transpose(interval_name, inPlace=False)


def optimize_greedy(
    source_melody: music21.stream.Part,
    harmony: music21.stream.Part,
    model: Dict,
) -> Dict:
    candidates: List[Tuple[str, music21.stream.Part]] = [("identity", source_melody)]
    for interval_name in TRANSFORMATION_INTERVALS:
        try:
            candidates.append((f"transpose_{interval_name}", _safe_transpose(source_melody, interval_name)))
        except Exception:
            continue

    scored = []
    for label, candidate in candidates:
        result = score_candidate(candidate, source_melody, harmony, model)
        scored.append((label, candidate, result))

    best = min(scored, key=lambda x: x[2]["total_cost"])
    return {
        "strategy": "greedy",
        "label": best[0],
        "melody": best[1],
        "score": best[2],
    }


def optimize_beam(
    source_melody: music21.stream.Part,
    harmony: music21.stream.Part,
    model: Dict,
    beam_width: int = 4,
    depth: int = 2,
) -> Dict:
    beam = [
        {
            "label": "identity",
            "history": ["P1"],
            "melody": source_melody,
            "score": score_candidate(source_melody, source_melody, harmony, model),
        }
    ]

    for _ in range(depth):
        expanded = []
        for state in beam:
            for interval_name in TRANSFORMATION_INTERVALS:
                try:
                    cand = _safe_transpose(state["melody"], interval_name)
                except Exception:
                    continue
                scored = score_candidate(cand, source_melody, harmony, model)
                expanded.append(
                    {
                        "label": f"{'/'.join(state['history'])}->{interval_name}",
                        "history": state["history"] + [interval_name],
                        "melody": cand,
                        "score": scored,
                    }
                )
        if not expanded:
            break
        expanded.sort(key=lambda s: s["score"]["total_cost"])
        beam = expanded[:beam_width]

    best = min(beam, key=lambda s: s["score"]["total_cost"])
    return {
        "strategy": "beam",
        "label": best["label"],
        "melody": best["melody"],
        "score": best["score"],
    }


def optimize_fallback(
    source_melody: music21.stream.Part,
    harmony: music21.stream.Part,
    model: Dict,
) -> Dict:
    candidates = [
        ("identity", source_melody),
        ("transpose_P5", _safe_transpose(source_melody, "P5")),
    ]
    scored = [(label, cand, score_candidate(cand, source_melody, harmony, model)) for label, cand in candidates]
    best = min(scored, key=lambda x: x[2]["total_cost"])
    return {
        "strategy": "fallback_simple",
        "label": best[0],
        "melody": best[1],
        "score": best[2],
    }


def optimize_melody_for_harmony(
    source_melody: music21.stream.Part,
    harmony: music21.stream.Part,
    model: Optional[Dict] = None,
    primary_strategy: str = "beam",
) -> Dict:
    model = model or DEFAULT_COST_MODEL

    if primary_strategy == "greedy":
        primary = optimize_greedy(source_melody, harmony, model)
    else:
        try:
            primary = optimize_beam(source_melody, harmony, model)
        except Exception:
            primary = optimize_greedy(source_melody, harmony, model)

    if primary["score"]["hard_violations"]:
        fallback = optimize_fallback(source_melody, harmony, model)
        if fallback["score"]["total_cost"] < primary["score"]["total_cost"]:
            return fallback
    return primary


# ==============================
# Benchmark and evaluation
# ==============================
BENCHMARK_SNIPPETS = [
    {
        "name": "baseline_stepwise",
        "melody": r"\relative c' { c4 d e f g2 g4 a }",
        "harmony": "<c e g>2 <f a c>2 <g b d>2 <c e g>2",
    },
    {
        "name": "leap_heavy",
        "melody": r"\relative c' { c4 g' e c' a f d b }",
        "harmony": "<c e g>1 <a c e>1",
    },
    {
        "name": "cadence_test",
        "melody": r"\relative c' { e4 f g a g f e d }",
        "harmony": "<c e g>2 <g b d>2 <c e g>1",
    },
]


def run_benchmark(model: Optional[Dict] = None) -> List[Dict]:
    model = model or DEFAULT_COST_MODEL
    rows: List[Dict] = []

    for case in BENCHMARK_SNIPPETS:
        melody = parse_lilypond_snippet(case["melody"])
        harmony = parse_lilypond_snippet(case["harmony"])

        baseline = score_candidate(melody, melody, harmony, model)
        optimized = optimize_melody_for_harmony(melody, harmony, model, primary_strategy="beam")

        rows.append(
            {
                "name": case["name"],
                "baseline_cost": round(baseline["total_cost"], 4),
                "optimized_cost": round(optimized["score"]["total_cost"], 4),
                "improvement": round(baseline["total_cost"] - optimized["score"]["total_cost"], 4),
                "strategy": optimized["strategy"],
                "label": optimized["label"],
                "hard_violations": optimized["score"]["hard_violations"],
            }
        )

    return rows


def print_evaluation_report(rows: List[Dict]):
    print("\n=== Theory Rule Catalog (Deliverable) ===")
    for rule_name, meta in THEORY_RULE_CATALOG.items():
        print(f"- {rule_name}: feature={meta['feature']}; target={meta['target']}")

    print("\n=== Benchmark Evaluation Report (Deliverable) ===")
    for row in rows:
        print(
            f"- {row['name']}: baseline={row['baseline_cost']}, "
            f"optimized={row['optimized_cost']}, improvement={row['improvement']}, "
            f"strategy={row['strategy']}, label={row['label']}, "
            f"hard_violations={row['hard_violations']}"
        )


# ==============================
# music21 → Abjad/LilyPond export
# ==============================
def ql_to_lily_duration_string(ql: float) -> str:
    dur = abjad.Duration(Fraction(ql / 4))
    return dur.lilypond_duration_string()


def m21_pitch_to_lily(p: music21.pitch.Pitch) -> str:
    return abjad.lilypond(abjad.NamedPitch(p.nameWithOctave))


def engrave_with_abjad(parts: Dict[str, music21.stream.Part], output_file: str):
    voices = {}
    for name, part in parts.items():
        tokens = []
        for el in part.flatten().notesAndRests:
            if isinstance(el, music21.chord.Chord):
                dur_str = ql_to_lily_duration_string(el.quarterLength)
                chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                tokens.append(f"<{chord_pitches}>{dur_str}")
            elif isinstance(el, music21.note.Note):
                dur_str = ql_to_lily_duration_string(el.quarterLength)
                tokens.append(f"{m21_pitch_to_lily(el.pitch)}{dur_str}")
            elif isinstance(el, music21.note.Rest):
                dur_str = ql_to_lily_duration_string(el.quarterLength)
                tokens.append(f"r{dur_str}")

        voices[name] = abjad.Voice(" ".join(tokens), name=name)

    melody_staff = abjad.Staff([voices.get("Melody")], name="Melody")
    harmony_staff = abjad.Staff([voices.get("Harmony")], name="Harmony")

    if melody_staff and abjad.select.leaf(melody_staff, 0):
        leaf0 = abjad.select.leaf(melody_staff, 0)
        abjad.attach(abjad.Clef("treble"), leaf0)
        abjad.attach(abjad.TimeSignature((4, 4)), leaf0)
        abjad.attach(abjad.KeySignature(abjad.NamedPitchClass("c"), abjad.Mode("major")), leaf0)
        abjad.attach(abjad.MetronomeMark(abjad.Duration(1, 4), 100), leaf0)

    if harmony_staff and abjad.select.leaf(harmony_staff, 0):
        leaf0h = abjad.select.leaf(harmony_staff, 0)
        abjad.attach(abjad.Clef("bass"), leaf0h)
        abjad.attach(abjad.TimeSignature((4, 4)), leaf0h)

    score = abjad.Score([abjad.StaffGroup([melody_staff, harmony_staff], lilypond_type="PianoStaff")])
    header = abjad.Block(
        name="header",
        items=[
            'title = "Theory + Cost Optimization Demo"',
            'composer = "Python + music21 + Abjad"',
        ],
    )
    lyfile = abjad.LilyPondFile(items=[header, score])

    ly_path = Path(output_file).with_suffix(".ly")
    abjad.persist.as_ly(lyfile, ly_path)
    print(f"Compiling {ly_path} with LilyPond...")
    subprocess.run(["lilypond", str(ly_path)], check=False)


# ==============================
# Demo / main
# ==============================
if __name__ == "__main__":
    melody_snippet = r"\relative c' { e4 f g a <c e g>2. r4 }"
    harmony_snippet = "c,2 g,2 <c e g>1"

    print("--- Parsing music from LilyPond strings ---")
    source_melody = parse_lilypond_snippet(melody_snippet)
    harmony = parse_lilypond_snippet(harmony_snippet)

    print("\n--- Running cost-based optimization ---")
    optimized = optimize_melody_for_harmony(source_melody, harmony, DEFAULT_COST_MODEL, primary_strategy="beam")
    optimized_melody = optimized["melody"]
    print(f"Selected strategy: {optimized['strategy']}")
    print(f"Selected candidate: {optimized['label']}")
    print(f"Total cost: {optimized['score']['total_cost']:.4f}")
    print(f"Hard violations: {optimized['score']['hard_violations']}")

    print("\n--- Running benchmark evaluation ---")
    report_rows = run_benchmark(DEFAULT_COST_MODEL)
    print_evaluation_report(report_rows)

    print("\n--- Engraving with Abjad ---")
    engrave_with_abjad({"Melody": optimized_melody, "Harmony": harmony}, "relative_score_optimized")
    print("\n✅ Done.")
