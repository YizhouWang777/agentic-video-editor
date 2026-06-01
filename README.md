# Agentic Video Editor

Agentic Video Editor is an alpha-stage local scaffold for coding agents that
edit video. It is not a one-click editor or a GUI replacement for traditional
editing tools. It gives Codex, Claude Code, Cursor, or another coding agent a
stable production protocol:

```text
brief -> asset manifest -> contact sheet -> transcript pack -> EDL -> validate -> render -> QA -> reusable rules
```

## Why This Exists

Text-first coding agents are good at writing code, calling tools, and revising
structured artifacts. Video editing becomes more reliable when the task is
split into artifacts the agent can inspect:

- `brief.md` for human intent and taste.
- `analysis/` for asset metadata, keyframes, contact sheets, and transcripts.
- `plan/edl.json` for edit decisions.
- `plan/validation_report.json` for pre-render guardrails.
- `renders/qa_report.json` for post-render checks.

The project is designed to be small enough to read, hack, and adapt.

## Influences

The design borrows from:

- `browser-use/video-use`: transcript-first editing, EDL, hard correctness rules
- `OpenMontage`: pipeline manifests, checkpoints, decision logs
- `mcp-video`: typed tool surfaces and media guardrails
- `Vex`: stateful projects, undo/rebuild thinking, deterministic fast paths
- `HyperFrames` and `Remotion`: separate render runtimes for HTML motion and React templates

## Quick Start

Requires Python 3.11 or newer.

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e .

ave init projects/my-edit
ave demo projects/my-edit
ave inspect projects/my-edit
ave contact-sheet projects/my-edit
ave transcribe projects/my-edit
ave pack-transcripts projects/my-edit
ave validate projects/my-edit
ave render projects/my-edit --preview
ave qa projects/my-edit --video renders/preview.mp4
ave render projects/my-edit
ave qa projects/my-edit
```

The demo creates synthetic source clips so the workflow can be tested without
external media. Real projects should put source files in `assets/source/`,
generated media in `assets/generated/`, and write an EDL at `plan/edl.json`.

## Project Layout

```text
project/
  brief.md
  assets/source/              # untouched user media
  assets/generated/           # generated media that may be used as sources
  analysis/asset_manifest.json
  analysis/frame_notes.md
  analysis/contact_sheet_report.json
  analysis/contact_sheets/
  analysis/keyframes/
  analysis/timeline_view.md
  analysis/transcripts/
  analysis/transcribe_report.json
  analysis/takes_packed.md
  plan/edl.json
  plan/validation_report.json
  plan/decision_log.jsonl
  renders/preview.mp4
  renders/final.mp4
  renders/preview_qa_report.json
  renders/final_qa_report.json
  renders/qa_report.json
  renders/qa_report.md
  template/reusable_rules.md
```

## Core Ideas

Hard rules belong in code and skill instructions: never mutate source media,
cache transcripts, keep subtitles last, keep an auditable EDL, verify before
showing output.

Taste belongs to the agent and the human: narrative shape, pacing, hook,
caption style, color mood, music, and visual packaging.

## CLI

```bash
ave init <project>
ave demo <project>
ave inspect <project>
ave contact-sheet <project> [--frames N] [--thumb-width PX]
ave transcribe <project> [--model base] [--language en]
ave pack-transcripts <project>
ave validate <project>
ave render <project> [--preview]
ave qa <project>
ave doctor [project]
ave log-decision <project> --stage ... --decision ... --reason ...
ave explain-failure <project>
```

Install ASR support only when needed:

```bash
.venv/bin/pip install -e '.[asr]'
```

Without ASR support, `ave transcribe` writes a skipped report and the rest of
the demo workflow still runs.

## Agent Skill

The `skill/` directory contains a Codex/Claude Code style skill that tells a
coding agent how to use the scaffold. The key rule is that the agent should
preserve creative autonomy in strategy and pacing, while letting deterministic
tools own media execution and QA.

## Docs

- `docs/research-findings.md`: what was borrowed from the researched projects.
- `docs/agent-loop.md`: the recommended loop for agents.
- `docs/edl-contract.md`: the edit decision list contract.
- `docs/runtime-selection.md`: when to use FFmpeg, HyperFrames, or Remotion.
- `docs/qa-contract.md`: current and planned checks.

## Status

This is alpha software. The FFmpeg base edit loop is implemented and tested.
ASR support is optional through `faster-whisper`. HyperFrames and Remotion are
represented in the skill and runtime-selection contract; full runtime adapters
belong behind the same EDL/QA boundary.

See [ROADMAP.md](ROADMAP.md) for planned work.
