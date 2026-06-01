from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from .ffmpeg import ffmpeg_bin, ffprobe_bin


def doctor(project: Path | None = None) -> dict[str, Any]:
    checks = []

    def add(check_id: str, passed: bool, detail: str, *, required: bool = True, **extra: Any) -> None:
        payload = {"id": check_id, "passed": bool(passed), "required": required, "detail": detail}
        payload.update(extra)
        checks.append(payload)

    ffmpeg = Path(ffmpeg_bin())
    add("ffmpeg", ffmpeg.exists(), "FFmpeg binary is available.", path=str(ffmpeg))
    ffprobe = ffprobe_bin()
    add("ffprobe", bool(ffprobe), "FFprobe is optional; imageio/ffmpeg fallback is used when absent.", required=False, path=ffprobe)
    for package in ["imageio", "imageio_ffmpeg", "numpy", "PIL"]:
        add(f"python_package_{package}", importlib.util.find_spec(package) is not None, f"Python package `{package}` is importable.")
    add(
        "python_package_faster_whisper",
        importlib.util.find_spec("faster_whisper") is not None,
        "`faster_whisper` is optional and needed only for `ave transcribe`.",
        required=False,
    )

    if project is not None:
        add("project_exists", project.exists(), "Project directory exists.", path=str(project))
        for rel in ["brief.md", "assets/source", "analysis", "plan/edl.json", "renders", "template"]:
            path = project / rel
            add(f"project_{rel.replace('/', '_')}", path.exists(), f"Project path exists: {rel}", path=str(path))

    return {"passed": all(item["passed"] or not item["required"] for item in checks), "checks": checks}
