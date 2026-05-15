technique_library = {

    "restrained tension": [
        "use narrow vibrato",
        "maintain steady bow pressure",
        "avoid early phrase release"
    ],

    "floating": [
        "use lighter bow contact",
        "maintain continuous bow flow",
        "avoid heavy articulation"
    ],

    "grounded stability": [
        "play with centered tone",
        "keep articulation stable",
        "avoid excessive rubato"
    ]
}
from music21 import corpus, note

# =========================
# LOAD SCORE
# =========================

# 使用 music21 自带曲库（先确保能跑通）
score = corpus.parse('bach/bwv66.6')

print(score)

# =========================
# LIST PARTS
# =========================

print("\n=== PARTS ===")

for p in score.parts:
    print(p.partName)

# =========================
# SELECT PART
# =========================

# 选择 Soprano 声部
part = score.parts[0]

# 取前 8 小节
excerpt = part.measures(1, 8)

# =========================
# KEY ANALYSIS
# =========================

key = excerpt.analyze("key")

print("\n=== KEY ANALYSIS ===")
print("Detected key:", key)

# =========================
# NOTE EXTRACTION
# =========================

notes = excerpt.flatten().notes

# MIDI pitch list
pitches = [n.pitch.midi for n in notes if isinstance(n, note.Note)]

# =========================
# BASIC PITCH STATS
# =========================

lowest_pitch = min(pitches)
highest_pitch = max(pitches)

avg_pitch = sum(pitches) / len(pitches)

pitch_range = highest_pitch - lowest_pitch

# =========================
# MELODIC CONTOUR
# =========================

intervals = []

for i in range(len(notes)-1):

    current_note = notes[i]
    next_note = notes[i+1]

    if isinstance(current_note, note.Note) and isinstance(next_note, note.Note):

        diff = next_note.pitch.midi - current_note.pitch.midi
        intervals.append(diff)

ascending = sum(1 for x in intervals if x > 0)
descending = sum(1 for x in intervals if x < 0)

if ascending > descending:
    contour = "mostly ascending"

elif descending > ascending:
    contour = "mostly descending"

else:
    contour = "balanced / wave-like"

# =========================
# RHYTHMIC PROFILE
# =========================

durations = [n.duration.quarterLength for n in notes]

# Rhythm summary
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

# =========================
# REGISTER SUMMARY
# =========================

if avg_pitch < 60:
    register_summary = "low register"

elif avg_pitch < 72:
    register_summary = "middle register"

elif avg_pitch < 84:
    register_summary = "upper-middle / high register"

else:
    register_summary = "very high register"

# =========================
# BUILD SYNTAX RESULT
# =========================

syntax_result = {
    "part": part.partName,
    "key": str(key),
    "lowest_pitch_midi": lowest_pitch,
    "highest_pitch_midi": highest_pitch,
    "average_pitch_midi": round(avg_pitch, 2),
    "pitch_range_semitones": pitch_range,
    "note_count": len(pitches),
    "melodic_contour": contour,
    "rhythmic_summary": rhythmic_summary,
    "register_summary": register_summary,
}

# =========================
# PRINT STRUCTURED RESULT
# =========================

print("\n=== SYNTAX RESULT ===")

for k, v in syntax_result.items():
    print(f"{k}: {v}")

# =========================
# NATURAL LANGUAGE SUMMARY
# =========================

syntax_summary = f"""
The selected part is {part.partName}.

The excerpt is analyzed in {key}.

The melodic range spans from MIDI {lowest_pitch} to {highest_pitch},
with an average pitch around {avg_pitch:.1f},
suggesting a {register_summary}.

The melodic contour is {contour}.

The rhythm is characterized by {rhythmic_summary}.

The passage contains {len(pitches)} notes
with a pitch range of {pitch_range} semitones.
"""

print("\n=== NATURAL LANGUAGE SUMMARY ===")
print(syntax_summary)