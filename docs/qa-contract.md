# QA Contract

QA should produce machine-readable and human-readable reports:

- `renders/qa_report.json`
- `renders/qa_report.md`

## Current Checks

- Output exists and has non-zero size.
- Output duration is positive.
- Output dimensions are valid.
- Sampled frames are not black.
- Output file is not tiny.
- Output duration matches the EDL within tolerance.
- Expected source audio is preserved.
- Expected audio is not fully silent.

## Planned Checks

- Subtitle OCR spot checks.
- Safe-zone occupancy for captions.
- Motion delta for static-frame detection.
- Brand asset presence.
- Loudness normalization.

## Failure Handling

When QA fails, the agent should:

1. Read the failing check.
2. Inspect the relevant artifact.
3. Run `ave explain-failure <project>` for a concise repair summary.
4. Patch the EDL, renderer, or reusable rule.
5. Re-render the smallest possible preview.
6. Re-run QA.

Do not ignore QA failures in the final response.
