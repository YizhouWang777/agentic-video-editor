# Agent Loop

This document describes how an agent should use the project.

## Loop Overview

```text
1. Read brief.md
2. Inspect assets with `ave inspect`
3. Generate contact sheets with `ave contact-sheet`
4. Generate transcripts with `ave transcribe` or place transcript JSON manually
5. Pack transcripts with `ave pack-transcripts`
6. Read analysis/asset_manifest.json, analysis/timeline_view.md, and analysis/takes_packed.md
7. Propose an edit strategy with `ave log-decision`
8. Write plan/edl.json
9. Run `ave validate`
10. Render preview with `ave render --preview`
11. Run `ave qa --video renders/preview.mp4`
12. Adjust the EDL or template rules
13. Render final with `ave render`
14. Run `ave qa` again
15. Add reusable learnings to template/reusable_rules.md
```

## Intent Entry

The user should not need to specify FFmpeg commands. The user should specify:

- Goal: what the video should achieve.
- Audience: who is watching.
- Platform: where it will be published.
- Duration: target and tolerance.
- Style: pacing, tone, references, subtitle feel, music.
- Must include: required scenes, phrases, brand elements, CTA.
- Must avoid: scenes, claims, moods, or formats that should not appear.
- Success criteria: how to judge the first cut.

The agent converts this into constraints and then writes the EDL.

## Asset Understanding

The asset layer exists because text models need a readable representation of
video. Use:

- `analysis/asset_manifest.json` for metadata.
- `analysis/frame_notes.md` for visual summaries.
- `analysis/timeline_view.md` and `analysis/contact_sheets/` for keyframe-based visual review.
- `analysis/takes_packed.md` for transcript ranges.

Do not make creative cuts before the assets are inspectable.

## EDL

The EDL is the contract between taste and execution. It should be small enough
for a human to read and strict enough for a machine to validate.

Required segment fields:

- `source`: path under the project root.
- `start`: source timestamp in seconds.
- `end`: source timestamp in seconds.

Optional segment fields:

- `beat`: narrative purpose.
- `notes`: reasoning for the cut.
- `volume`: per-segment audio gain from 0.0 to 4.0.

Captions use final-timeline timestamps, not source timestamps.

## Tool Layer

Use deterministic tools for deterministic jobs:

- FFmpeg for cutting, padding, concat, encoding, and subtitle burn.
- Whisper/faster-whisper for transcripts.
- HyperFrames for HTML/GSAP motion graphics.
- Remotion for React-based reusable video templates.
- Python utilities for validation, QA, and state.

The agent should not hand-write one-off shell commands when a project command
exists.

## QA And Evaluation

QA is part of the loop, not an afterthought. Always check:

- File exists and is not tiny.
- Duration is positive and roughly matches the EDL.
- Dimensions and fps match the render spec.
- Sampled frames are not black.
- Captions fit the final timeline.
- Sources were not mutated.

Failures should update either `plan/edl.json` or `template/reusable_rules.md`.
