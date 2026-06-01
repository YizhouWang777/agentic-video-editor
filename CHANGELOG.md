# Changelog

## Unreleased

- Added render `fit` mode with `contain` and `cover` options.
- Validates render fit mode and documents crop-to-fill behavior.
- Dogfooded with a real local HEVC/MOV source and vertical crop render.

## 0.1.0 - 2026-06-01

Initial alpha release.

- Project scaffold for agent-first video editing.
- CLI commands for init, demo, inspect, contact sheets, transcript packing,
  validation, rendering, QA, doctor checks, decision logging, and failure
  explanation.
- FFmpeg base renderer with source sandboxing and audio stream normalization.
- EDL, validation report, and QA report schemas.
- Codex/Claude Code style skill instructions.
- Unit tests and GitHub Actions CI.
