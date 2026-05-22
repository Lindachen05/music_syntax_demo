from collections import Counter

from music21 import chord, converter, dynamics, expressions, note, tempo


technique_library = {
    "restrained tension": [
        "use narrow vibrato",
        "maintain steady bow pressure",
        "avoid early phrase release",
    ],
    "floating": [
        "use lighter bow contact",
        "maintain continuous bow flow",
        "avoid heavy articulation",
    ],
    "grounded stability": [
        "play with centered tone",
        "keep articulation stable",
        "avoid excessive rubato",
    ],
}


SCORE_FILE = "mozartk622mvt3.mxl"
PART_INDEX = 0
START_MEASURE = 1
END_MEASURE = 8


def normalize_part_name(part_name):
    if not part_name:
        return "Unknown part"

    return part_name.replace("Clarinette en Si♭", "Clarinet in B-flat")


def summarize_counter(items, empty_message="none found"):
    if not items:
        return empty_message

    counts = Counter(items)
    return ", ".join(f"{name} ({count})" for name, count in counts.most_common())


def format_location(item):
    context_measure = item.getContextByClass("Measure")
    measure_number = getattr(item, "measureNumber", None)

    if measure_number is None:
        measure_number = getattr(context_measure, "number", "?")

    try:
        measure_offset = float(item.getOffsetBySite(context_measure))
    except Exception:
        measure_offset = float(item.offset)

    return f"m{measure_number} offset {measure_offset:g}"


def summarize_locations(items, label_getter, empty_message="none found"):
    if not items:
        return empty_message

    return "; ".join(
        f"{format_location(item)}: {label_getter(item)}"
        for item in items
    )


def extract_notes_and_chords(excerpt):
    musical_events = excerpt.flatten().notes
    single_notes = []
    chords = []

    for event in musical_events:
        if isinstance(event, note.Note):
            single_notes.append(event)
        elif isinstance(event, chord.Chord):
            chords.append(event)
            single_notes.extend(event.notes)

    return musical_events, single_notes, chords


def analyze_pitch(single_notes):
    pitches = [n.pitch.midi for n in single_notes]

    if not pitches:
        return {
            "lowest_pitch_midi": None,
            "highest_pitch_midi": None,
            "average_pitch_midi": None,
            "pitch_range_semitones": 0,
            "note_count": 0,
            "register_summary": "no pitched notes found",
        }

    lowest_pitch = min(pitches)
    highest_pitch = max(pitches)
    avg_pitch = sum(pitches) / len(pitches)
    pitch_range = highest_pitch - lowest_pitch

    if avg_pitch < 60:
        register_summary = "low register"
    elif avg_pitch < 72:
        register_summary = "middle register"
    elif avg_pitch < 84:
        register_summary = "upper-middle / high register"
    else:
        register_summary = "very high register"

    return {
        "lowest_pitch_midi": lowest_pitch,
        "highest_pitch_midi": highest_pitch,
        "average_pitch_midi": round(avg_pitch, 2),
        "pitch_range_semitones": pitch_range,
        "note_count": len(pitches),
        "register_summary": register_summary,
    }


def analyze_melodic_contour(single_notes):
    intervals = []

    for current_note, next_note in zip(single_notes, single_notes[1:]):
        diff = next_note.pitch.midi - current_note.pitch.midi
        intervals.append(diff)

    ascending = sum(1 for x in intervals if x > 0)
    descending = sum(1 for x in intervals if x < 0)
    repeated = sum(1 for x in intervals if x == 0)
    leaps = sum(1 for x in intervals if abs(x) >= 5)
    steps = sum(1 for x in intervals if 0 < abs(x) <= 2)

    if ascending > descending:
        contour = "mostly ascending"
    elif descending > ascending:
        contour = "mostly descending"
    else:
        contour = "balanced / wave-like"

    return {
        "melodic_contour": contour,
        "ascending_intervals": ascending,
        "descending_intervals": descending,
        "repeated_notes": repeated,
        "stepwise_motion_count": steps,
        "leap_motion_count": leaps,
    }


def analyze_rhythm(excerpt, musical_events):
    durations = [float(n.duration.quarterLength) for n in musical_events]
    rests = list(excerpt.flatten().getElementsByClass(note.Rest))

    if not durations:
        return {
            "rhythmic_summary": "no rhythmic events found",
            "duration_profile": "none found",
            "rest_count": len(rests),
            "total_rest_quarter_length": round(
                sum(float(r.duration.quarterLength) for r in rests), 2
            ),
        }

    quarter_notes = durations.count(1.0)
    short_notes = sum(1 for d in durations if d < 1.0)
    long_notes = sum(1 for d in durations if d > 1.0)

    if quarter_notes > len(durations) * 0.6:
        rhythmic_summary = "mostly quarter-note motion"
    elif short_notes > len(durations) * 0.3:
        rhythmic_summary = "active / dense rhythmic motion"
    elif long_notes > len(durations) * 0.3:
        rhythmic_summary = "sustained / spacious rhythm"
    else:
        rhythmic_summary = "mixed rhythmic activity"

    duration_profile = summarize_counter(durations)

    return {
        "rhythmic_summary": rhythmic_summary,
        "duration_profile": duration_profile,
        "rest_count": len(rests),
        "total_rest_quarter_length": round(
            sum(float(r.duration.quarterLength) for r in rests), 2
        ),
    }


def analyze_score_markings(excerpt):
    flat_excerpt = excerpt.flatten()

    dynamic_items = list(flat_excerpt.getElementsByClass(dynamics.Dynamic))
    dynamic_wedge_items = list(flat_excerpt.getElementsByClass(dynamics.DynamicWedge))
    tempo_items = list(flat_excerpt.getElementsByClass(tempo.MetronomeMark))
    text_expression_items = list(
        flat_excerpt.getElementsByClass(expressions.TextExpression)
    )

    dynamic_marks = [item.value for item in dynamic_items if item.value]
    dynamic_wedges = [item.type for item in dynamic_wedge_items if item.type]
    articulations_found = [
        articulation.classes[0]
        for n in flat_excerpt.notes
        for articulation in getattr(n, "articulations", [])
    ]
    expressions_found = [
        item.content
        for item in text_expression_items
        if item.content
    ]
    tempo_marks = [
        item.text or f"{item.number} BPM"
        for item in tempo_items
    ]
    time_signatures = [str(ts.ratioString) for ts in flat_excerpt.getTimeSignatures()]

    return {
        "dynamic_marks": summarize_counter(dynamic_marks),
        "dynamic_timeline": summarize_locations(
            dynamic_items,
            lambda item: item.value,
        ),
        "dynamic_mark_count": len(dynamic_marks),
        "dynamic_wedges": summarize_counter(dynamic_wedges),
        "dynamic_wedge_timeline": summarize_locations(
            dynamic_wedge_items,
            lambda item: item.type,
        ),
        "articulations": summarize_counter(articulations_found),
        "text_expressions": summarize_counter(expressions_found),
        "text_expression_timeline": summarize_locations(
            text_expression_items,
            lambda item: item.content,
        ),
        "tempo_marks": summarize_counter(tempo_marks),
        "tempo_timeline": summarize_locations(
            tempo_items,
            lambda item: item.text or f"{item.number} BPM",
        ),
        "time_signatures": summarize_counter(time_signatures),
    }


def analyze_harmony(chords):
    if not chords:
        return {
            "chord_count": 0,
            "chord_summary": "none found",
        }

    chord_names = [c.commonName for c in chords]
    return {
        "chord_count": len(chords),
        "chord_summary": summarize_counter(chord_names),
    }


def analyze_part(score, part_index, start_measure, end_measure):
    part = score.parts[part_index]
    part_name = normalize_part_name(part.partName)
    excerpt = part.measures(start_measure, end_measure)
    musical_events, single_notes, chords = extract_notes_and_chords(excerpt)

    key = excerpt.analyze("key")
    pitch_result = analyze_pitch(single_notes)
    contour_result = analyze_melodic_contour(single_notes)
    rhythm_result = analyze_rhythm(excerpt, musical_events)
    marking_result = analyze_score_markings(excerpt)
    harmony_result = analyze_harmony(chords)

    syntax_result = {
        "part": part_name,
        "measures": f"{start_measure}-{end_measure}",
        "key": str(key),
        **pitch_result,
        **contour_result,
        **rhythm_result,
        **marking_result,
        **harmony_result,
    }

    return part, excerpt, syntax_result


score = converter.parse(SCORE_FILE)

print("=== SCORE ===")
print(score)

print("\n=== PARTS ===")
for i, p in enumerate(score.parts):
    print(i, normalize_part_name(p.partName), p.id)

part, excerpt, syntax_result = analyze_part(
    score,
    PART_INDEX,
    START_MEASURE,
    END_MEASURE,
)

print("\n=== SELECTED EXCERPT ===")
print("Part:", syntax_result["part"])
print("Measures:", syntax_result["measures"])

print("\n=== SYNTAX RESULT ===")
for key, value in syntax_result.items():
    print(f"{key}: {value}")

syntax_summary = f"""
The selected part is {syntax_result["part"]}, measures {syntax_result["measures"]}.

The excerpt is analyzed in {syntax_result["key"]}.

The melodic range spans from MIDI {syntax_result["lowest_pitch_midi"]} to
{syntax_result["highest_pitch_midi"]}, with an average pitch around
{syntax_result["average_pitch_midi"]}, suggesting a
{syntax_result["register_summary"]}.

The melodic contour is {syntax_result["melodic_contour"]}.

The rhythm is characterized by {syntax_result["rhythmic_summary"]}.

Dynamics found: {syntax_result["dynamic_marks"]}.
Dynamic wedges found: {syntax_result["dynamic_wedges"]}.
Dynamic timeline: {syntax_result["dynamic_timeline"]}.
Articulations found: {syntax_result["articulations"]}.
Tempo marks found: {syntax_result["tempo_marks"]}.
Time signatures found: {syntax_result["time_signatures"]}.
Text expressions found: {syntax_result["text_expressions"]}.

The passage contains {syntax_result["note_count"]} pitched notes, 
{syntax_result["rest_count"]} rests, and {syntax_result["chord_count"]} chords.
"""

print("\n=== NATURAL LANGUAGE SUMMARY ===")
print(syntax_summary)
