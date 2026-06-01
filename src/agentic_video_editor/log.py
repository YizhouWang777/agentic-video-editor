from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def log_decision(root: Path, *, stage: str, decision: str, reason: str) -> dict[str, Any]:
    payload = {
        "time": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "decision": decision,
        "reason": reason,
    }
    path = root / "plan" / "decision_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")
    return payload
