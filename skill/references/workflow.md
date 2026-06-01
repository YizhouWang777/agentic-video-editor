# Workflow Reference

## Why The Loop Is Split

Video editing looks like one task, but an agent needs several distinct
interfaces:

- Intent entry: convert human taste into constraints.
- Asset understanding: make video readable through metadata, frames, and text.
- EDL: record creative decisions without rendering side effects.
- Tool layer: execute deterministic media operations.
- QA: detect failures after rendering.
- Evaluation: save reusable rules for the next edit.

This split keeps the model's autonomy where it helps and gives it rails where
video systems are brittle.

## Minimal Production Pass

1. Create or update `brief.md`.
2. Put media in `assets/source/`.
3. Run `ave inspect`.
4. Run `ave contact-sheet`.
5. Create transcripts with `ave transcribe` if speech matters.
6. Run `ave pack-transcripts`.
7. Draft the edit strategy with `ave log-decision`.
8. Write `plan/edl.json`.
9. Run `ave validate`.
10. Render preview and QA.
11. Iterate.
12. Render final and QA.

## Decision Log Format

Append one JSON object per decision:

```json
{"stage":"strategy","decision":"Open with the most concrete scene","reason":"The platform rewards fast context.","time":"2026-06-01T12:00:00Z"}
```

Keep it short. The log is for the next agent turn, not for marketing.
