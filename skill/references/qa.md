# QA Reference

QA is mandatory after preview and final render.

The minimum acceptable report must answer:

- Did the file render?
- Is it the expected format and dimensions?
- Is the duration plausible?
- Are sampled frames visible?
- Does the duration match the EDL?
- Was expected audio preserved?
- Did captions fit the timeline?

When a check fails:

1. Read `renders/qa_report.json`.
2. Inspect sample frames under `renders/verify/`.
3. Patch `plan/edl.json` or the renderer.
4. Re-run preview render and QA.
