from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ffmpeg import probe
from .project import read_json, write_json


WORD_BOUNDARY_TOLERANCE = 0.03
ALLOWED_SOURCE_DIRS = ("assets/source", "assets/generated")


def validate_project(root: Path) -> dict[str, Any]:
    try:
        edl = read_json(root / "plan" / "edl.json")
    except Exception as exc:
        return _write_report(
            root,
            [
                {
                    "id": "edl_readable",
                    "passed": False,
                    "detail": f"Could not read plan/edl.json: {exc}",
                }
            ],
            total_duration=0.0,
        )
    checks: list[dict[str, Any]] = []
    source_cache: dict[str, dict[str, Any] | None] = {}

    def add(check_id: str, passed: bool, detail: str, **extra: Any) -> None:
        payload = {"id": check_id, "passed": bool(passed), "detail": detail}
        payload.update(extra)
        checks.append(payload)

    if not isinstance(edl, dict):
        add("edl_object", False, "EDL must be a JSON object.")
        return _write_report(root, checks, total_duration=0.0)

    segments = edl.get("segments", [])
    if not isinstance(segments, list):
        add("segments_list", False, "EDL `segments` must be a list.")
        segments = []
    add("segments_present", bool(segments), "EDL must contain at least one segment.")

    total_duration = 0.0
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            add(f"segment_{index:03d}_object", False, f"Segment {index} must be a JSON object.")
            continue
        source_rel = str(segment.get("source") or "")
        source = _resolve_allowed_source(root, source_rel)
        source_key = source_rel
        source_allowed = source is not None
        add(
            f"segment_{index:03d}_source_allowed",
            source_allowed,
            f"Segment {index} source must be relative and inside one of: {', '.join(ALLOWED_SOURCE_DIRS)}.",
            source=source_rel,
        )
        source_exists = bool(source_allowed and source and source.exists() and source.is_file())
        add(
            f"segment_{index:03d}_source_exists",
            source_exists,
            f"Segment {index} source must exist: {source_rel}",
            source=source_rel,
        )
        start = _float(segment.get("start"))
        end = _float(segment.get("end"))
        valid_range = start is not None and end is not None and start >= 0 and end > start
        add(
            f"segment_{index:03d}_range_valid",
            bool(valid_range),
            f"Segment {index} must have start >= 0 and end > start.",
            start=start,
            end=end,
        )
        if not source_exists or not valid_range or source is None:
            continue
        volume = _float(segment.get("volume", 1.0))
        add(
            f"segment_{index:03d}_volume_valid",
            volume is not None and 0.0 <= volume <= 4.0,
            f"Segment {index} volume must be between 0.0 and 4.0.",
            volume=volume,
        )
        if source_key not in source_cache:
            source_cache[source_key] = _safe_probe(source)
        metadata = source_cache[source_key]
        if metadata is None:
            add(
                f"segment_{index:03d}_probe_ok",
                False,
                f"Could not inspect source media: {source_rel}",
                source=source_rel,
            )
            continue
        duration = float(metadata["duration"])
        within_media = end <= duration + 0.05
        add(
            f"segment_{index:03d}_within_source",
            within_media,
            f"Segment {index} must not extend beyond source duration.",
            source_duration=duration,
            end=end,
        )
        word_boundary = _check_word_boundaries(root, source, start, end)
        if word_boundary is not None:
            add(
                f"segment_{index:03d}_word_boundary",
                word_boundary["passed"],
                word_boundary["detail"],
                boundary_hits=word_boundary["boundary_hits"],
            )
        total_duration += end - start

    captions = edl.get("captions", [])
    if captions is None:
        captions = []
    if not isinstance(captions, list):
        add("captions_list", False, "EDL `captions` must be a list when present.")
        captions = []
    previous_end = 0.0
    for index, caption in enumerate(captions):
        if not isinstance(caption, dict):
            add(f"caption_{index:03d}_object", False, f"Caption {index} must be a JSON object.")
            continue
        start = _float(caption.get("start"))
        end = _float(caption.get("end"))
        text = str(caption.get("text") or "").strip()
        valid = start is not None and end is not None and start >= 0 and end > start and bool(text)
        ordered = start is None or start + 1e-6 >= previous_end
        in_timeline = end is not None and end <= total_duration + 0.2
        add(
            f"caption_{index:03d}_valid",
            bool(valid and ordered and in_timeline),
            "Captions need non-empty text, ordered time ranges, and must fit the final timeline.",
            start=start,
            end=end,
            text_present=bool(text),
            ordered=ordered,
            in_timeline=in_timeline,
        )
        if end is not None:
            previous_end = end

    render = edl.get("render", {})
    if not isinstance(render, dict):
        add("render_object", False, "EDL `render` must be a JSON object.")
        render = {}
    width = _int(render.get("width"))
    height = _int(render.get("height"))
    fps = _int(render.get("fps"))
    add("render_dimensions", width > 0 and height > 0, "Render width and height must be positive.", width=width, height=height)
    add("render_fps", fps > 0, "Render fps must be positive.", fps=fps)

    return _write_report(root, checks, total_duration=total_duration)


def _write_report(root: Path, checks: list[dict[str, Any]], *, total_duration: float) -> dict[str, Any]:
    report = {
        "passed": all(item["passed"] for item in checks),
        "total_duration": round(total_duration, 3),
        "checks": checks,
    }
    write_json(root / "plan" / "validation_report.json", report)
    return report


def _safe_probe(path: Path) -> dict[str, Any] | None:
    try:
        return probe(path)
    except Exception:
        return None


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int:
    numeric = _float(value)
    return int(numeric) if numeric is not None else 0


def _resolve_allowed_source(root: Path, source_rel: str) -> Path | None:
    if not source_rel:
        return None
    raw = Path(source_rel)
    if raw.is_absolute():
        return None
    candidate = (root / raw).resolve()
    allowed_roots = [(root / rel).resolve() for rel in ALLOWED_SOURCE_DIRS]
    if any(_is_relative_to(candidate, allowed_root) for allowed_root in allowed_roots):
        return candidate
    return None


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _check_word_boundaries(root: Path, source: Path, start: float, end: float) -> dict[str, Any] | None:
    transcript = root / "analysis" / "transcripts" / f"{source.stem}.json"
    if not transcript.exists():
        return None
    try:
        words = json.loads(transcript.read_text(encoding="utf-8")).get("words", [])
    except json.JSONDecodeError:
        return {"passed": False, "detail": f"Transcript JSON is invalid: {transcript.name}", "boundary_hits": []}
    boundary_hits = []
    for boundary_name, boundary in [("start", start), ("end", end)]:
        for word in words:
            if word.get("type", "word") == "spacing":
                continue
            word_start = _float(word.get("start"))
            word_end = _float(word.get("end"))
            if word_start is None or word_end is None:
                continue
            if word_start + WORD_BOUNDARY_TOLERANCE < boundary < word_end - WORD_BOUNDARY_TOLERANCE:
                boundary_hits.append(
                    {
                        "boundary": boundary_name,
                        "time": boundary,
                        "word": str(word.get("text") or ""),
                        "word_start": word_start,
                        "word_end": word_end,
                    }
                )
    return {
        "passed": not boundary_hits,
        "detail": "Segment cuts must not land inside transcript words.",
        "boundary_hits": boundary_hits,
    }
