# Agent Instructions

This repository is an agent-first video editing scaffold.

## Language

Use English for code, comments, schemas, and repository documentation.

## Workflow

Do not treat video editing as a single prompt. Use the project loop:

```text
brief -> asset manifest -> transcript pack -> EDL -> validate -> render -> QA -> reusable rules
```

## Safety

- Never overwrite `assets/source/*` in a user project.
- Prefer the `ave` CLI over ad hoc FFmpeg commands.
- Run validation before rendering.
- Run QA after preview and final renders.
- Keep generated artifacts under the project workspace.

## Development

Install locally:

```bash
python -m venv .venv
.venv/bin/pip install -e .
```

Run tests:

```bash
python -m unittest discover -s tests
```

Run the smoke demo:

```bash
ave demo examples/demo-project
ave inspect examples/demo-project
ave contact-sheet examples/demo-project
ave transcribe examples/demo-project
ave pack-transcripts examples/demo-project
ave validate examples/demo-project
ave render examples/demo-project --preview
ave qa examples/demo-project --video renders/preview.mp4
ave render examples/demo-project
ave qa examples/demo-project
```
