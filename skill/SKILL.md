# Agentic Video Editor

Use this skill when the user asks a coding agent to edit, repurpose, assemble,
caption, or QA videos from local assets.

This is an agent workflow skill, not a one-shot prompt. The model should keep
creative authority, but all media execution must pass through inspectable
artifacts.

## First Response

For a new edit, collect or infer:

- Goal and platform.
- Target duration.
- Audience and style.
- Required source assets.
- Must-include and must-avoid constraints.
- Output spec.

If the user provided assets and the goal is clear enough, start the project
instead of asking for more detail.

## Required Loop

Run this loop unless the user explicitly asks for a narrower operation:

1. Read `brief.md`.
2. Run `ave inspect <project>`.
3. Run `ave contact-sheet <project>`.
4. Run `ave transcribe <project>` when ASR support is installed, or place transcript JSON manually.
5. Run `ave pack-transcripts <project>`.
6. Read `analysis/asset_manifest.json`, `analysis/timeline_view.md`, and `analysis/takes_packed.md`.
7. Write the edit strategy with `ave log-decision`.
8. Write `plan/edl.json`.
9. Run `ave validate <project>`.
10. Render a preview with `ave render <project> --preview`.
11. Run `ave qa <project> --video renders/preview.mp4`.
12. Patch the EDL or rules until preview QA passes.
13. Render final with `ave render <project>`.
14. Run `ave qa <project>` again.
15. Save reusable learnings to `template/reusable_rules.md`.

## Hard Rules

- Never mutate files under `assets/source/`.
- Do not render before there is an EDL.
- Do not skip validation before render.
- Do not cut inside transcript words when word-level timestamps exist.
- Apply subtitles after the base edit is assembled.
- Keep source timestamps and final-timeline timestamps separate.
- Prefer project commands over one-off shell commands.
- If QA fails, fix and rerun; do not present the render as done.

## Project Commands

```bash
ave init <project>
ave demo <project>
ave inspect <project>
ave contact-sheet <project>
ave transcribe <project>
ave pack-transcripts <project>
ave validate <project>
ave render <project> [--preview]
ave qa <project>
ave doctor [project]
ave log-decision <project> --stage ... --decision ... --reason ...
ave explain-failure <project>
```

## Artifact Map

- `brief.md`: human intent and constraints.
- `assets/source/`: untouched input media.
- `assets/generated/`: generated media that may be used as sources.
- `analysis/asset_manifest.json`: metadata for source videos.
- `analysis/frame_notes.md`: visual notes and orientation.
- `analysis/timeline_view.md`: keyframe-based visual index.
- `analysis/contact_sheets/`: generated contact sheets.
- `analysis/takes_packed.md`: readable transcript ranges.
- `plan/edl.json`: edit decisions.
- `plan/validation_report.json`: pre-render checks.
- `plan/decision_log.jsonl`: why decisions were made.
- `renders/preview.mp4`: timing-preserving preview.
- `renders/final.mp4`: final render.
- `renders/qa_report.json`: machine-readable QA.
- `renders/qa_report.md`: human-readable QA.
- `template/reusable_rules.md`: lessons for similar future videos.

## When To Use Other Runtimes

Use FFmpeg for the base edit. Add HyperFrames or Remotion only when needed:

- HyperFrames: HTML/CSS/GSAP motion graphics, kinetic text, social cards,
  data visualization, agent-authored visual effects.
- Remotion: reusable React templates, branded recurring formats, parameterized
  subtitles, complex component layout.

Read the reference docs only when relevant:

- `references/workflow.md`
- `references/hard-rules.md`
- `references/runtime-selection.md`
- `references/qa.md`
