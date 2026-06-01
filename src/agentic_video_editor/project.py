from __future__ import annotations

import json
from pathlib import Path
from typing import Any


VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
MEDIA_DIRS = ["assets/source", "assets/generated"]


def ensure_project(root: Path) -> None:
    for rel in [
        "assets/source",
        "assets/generated",
        "analysis/transcripts",
        "plan",
        "renders/verify",
        "template",
        "work/clips",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    brief = root / "brief.md"
    if not brief.exists():
        brief.write_text(default_brief(), encoding="utf-8")
    edl = root / "plan" / "edl.json"
    if not edl.exists():
        edl.write_text(json.dumps(default_edl(), indent=2), encoding="utf-8")
    decision_log = root / "plan" / "decision_log.jsonl"
    if not decision_log.exists():
        decision_log.write_text("", encoding="utf-8")


def source_files(root: Path) -> list[Path]:
    files = []
    for rel in MEDIA_DIRS:
        media_dir = root / rel
        if not media_dir.exists():
            continue
        files.extend(p for p in media_dir.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
    return sorted(files)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def default_brief() -> str:
    return """# Video Brief

## Goal
Describe what this video should achieve.

## Platform
Shorts / Reels / TikTok / Xiaohongshu / Bilibili / YouTube / Internal.

## Audience
Who is watching and what do they already know?

## Duration
Target duration and acceptable range.

## Style
Pacing, mood, references, subtitle style, music direction.

## Source Assets
List source clips, audio, images, brand files, or scripts.

## Narrative
What story should the final video tell?

## Must Include
Required clips, phrases, logos, scenes, CTA.

## Must Avoid
Things to remove or avoid.

## Output Spec
Aspect ratio, resolution, fps, format, subtitle language.

## Success Criteria
How should the first cut be judged?
"""


def default_edl() -> dict[str, Any]:
    return {
        "version": "0.1",
        "render": {
            "width": 1080,
            "height": 1920,
            "fps": 24,
            "caption_style": "bold_safe",
        },
        "sources": {},
        "segments": [],
        "captions": [],
        "overlays": [],
    }
