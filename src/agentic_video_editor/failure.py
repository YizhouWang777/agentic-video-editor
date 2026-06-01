from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def explain_failure(root: Path) -> str:
    validation = _read_json(root / "plan" / "validation_report.json")
    qa = _read_json(root / "renders" / "qa_report.json")
    lines = ["# Failure Explanation", ""]

    _append_report(lines, "Validation", validation)
    _append_report(lines, "QA", qa)
    if len(lines) == 2:
        lines.append("No validation or QA reports found.")
    text = "\n".join(lines)
    out = root / "renders" / "failure_explanation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return text


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"passed": False, "read_error": f"Invalid JSON: {path}"}
    return data if isinstance(data, dict) else {"passed": False, "read_error": f"Expected object: {path}"}


def _append_report(lines: list[str], title: str, report: dict[str, Any] | None) -> None:
    if report is None:
        return
    lines.append(f"## {title}")
    lines.append(f"- Passed: {report.get('passed')}")
    if report.get("read_error"):
        lines.append(f"- Read error: {report['read_error']}")
    checks = report.get("checks")
    if isinstance(checks, list):
        failed = [item for item in checks if isinstance(item, dict) and not item.get("passed")]
        if failed:
            lines.append("- Failed checks:")
            for item in failed:
                lines.append(f"  - `{item.get('id')}`: {item.get('detail')}")
        else:
            lines.append("- Failed checks: none")
    elif isinstance(checks, dict):
        failed = [key for key, value in checks.items() if not value]
        if failed:
            lines.append("- Failed checks:")
            for key in failed:
                lines.append(f"  - `{key}`")
        else:
            lines.append("- Failed checks: none")
    if report.get("probe_error"):
        lines.append(f"- Probe error: `{report['probe_error']}`")
    if report.get("sample_errors"):
        lines.append("- Sample errors:")
        for item in report["sample_errors"]:
            lines.append(f"  - {item}")
    lines.append("")
