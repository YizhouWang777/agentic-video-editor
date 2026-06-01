# Contributing

Thanks for helping improve Agentic Video Editor.

This project is an alpha scaffold for agent-first video editing. Contributions
should keep the core loop inspectable:

```text
brief -> asset manifest -> contact sheet -> transcript pack -> EDL -> validate -> render -> QA -> reusable rules
```

## Development

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
```

Run the smoke workflow:

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

## Guidelines

- Keep source media immutable.
- Put deterministic media actions behind CLI commands.
- Add validation before adding rendering behavior.
- Add QA coverage for any new output risk.
- Keep generated media out of commits.
- Update `skill/` and `docs/` when changing the agent workflow.

## Pull Requests

Please include:

- What changed.
- Why it matters for agent reliability.
- How it was tested.
- Any remaining limitations.
