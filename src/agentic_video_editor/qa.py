from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .ffmpeg import ffmpeg_bin, probe, run
from .project import read_json


def qa_video(root: Path, video: Path | None = None) -> dict:
    target = video or _default_video(root)
    frame_dir = root / "renders" / "verify"
    frame_dir.mkdir(parents=True, exist_ok=True)
    expected_audio = _expected_audio(root)
    expected_duration = _expected_duration(root)
    if not target.exists():
        report = _build_report(
            root,
            target,
            _empty_metadata(target),
            [],
            [],
            [],
            expected_audio=expected_audio,
            expected_duration=expected_duration,
            audio_stats=None,
            probe_error=None,
            sample_errors=["Target video does not exist."],
        )
        _write_reports(root, target, report)
        return report
    try:
        metadata = probe(target)
        probe_error = None
    except Exception as exc:
        metadata = _empty_metadata(target)
        probe_error = str(exc)
    samples = []
    sample_errors = []
    if metadata["duration"] > 0 and metadata["width"] > 0 and metadata["height"] > 0:
        try:
            samples = _extract_samples(target, metadata["duration"], frame_dir)
        except Exception as exc:
            sample_errors.append(f"Could not extract sample frames: {exc}")
    audio_stats = _audio_stats(target) if metadata.get("has_audio") else None
    frame_means = []
    black_frames = []
    for sample in samples:
        image = Image.open(sample).convert("RGB")
        mean = float(np.asarray(image).mean())
        frame_means.append(round(mean, 2))
        if mean < 8:
            black_frames.append(sample.name)
    report = _build_report(
        root,
        target,
        metadata,
        samples,
        frame_means,
        black_frames,
        expected_audio=expected_audio,
        expected_duration=expected_duration,
        audio_stats=audio_stats,
        probe_error=probe_error,
        sample_errors=sample_errors,
    )
    _write_reports(root, target, report)
    return report


def _build_report(
    root: Path,
    target: Path,
    metadata: dict[str, Any],
    samples: list[Path],
    frame_means: list[float],
    black_frames: list[str],
    *,
    expected_audio: bool | None,
    expected_duration: float | None,
    audio_stats: dict[str, float] | None,
    probe_error: str | None,
    sample_errors: list[str] | None = None,
) -> dict[str, Any]:
    sample_errors = sample_errors or []
    exists = target.exists()
    checks = {
        "file_exists": exists and target.stat().st_size > 0,
        "probe_succeeded": probe_error is None,
        "duration_positive": metadata["duration"] > 0.5,
        "valid_dimensions": metadata["width"] > 0 and metadata["height"] > 0,
        "sample_frames_extracted": bool(samples) and not sample_errors,
        "no_sampled_black_frames": bool(samples) and not black_frames,
        "file_not_tiny": exists and target.stat().st_size > 50_000,
    }
    if expected_audio is not None:
        checks["audio_matches_expectation"] = metadata["has_audio"] if expected_audio else True
    if expected_duration is not None:
        tolerance = max(0.25, expected_duration * 0.03)
        checks["duration_matches_edl"] = abs(metadata["duration"] - expected_duration) <= tolerance
    if expected_audio and metadata.get("has_audio"):
        checks["audio_not_silent"] = audio_stats is not None and audio_stats.get("mean_volume_db", -100.0) > -55.0
    report = {
        "file": _display_path(root, target),
        "metadata": metadata,
        "sampled_frames": [str(p.relative_to(root)) for p in samples],
        "sampled_frame_means": frame_means,
        "black_frames": black_frames,
        "expected_audio": expected_audio,
        "expected_duration": expected_duration,
        "audio_stats": audio_stats,
        "probe_error": probe_error,
        "sample_errors": sample_errors,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return report


def _write_reports(root: Path, target: Path, report: dict[str, Any]) -> None:
    root.joinpath("renders").mkdir(parents=True, exist_ok=True)
    stem = _qa_report_stem(target)
    for json_name in ["qa_report.json", f"{stem}.json"]:
        (root / "renders" / json_name).write_text(json.dumps(report, indent=2), encoding="utf-8")
    for md_name in ["qa_report.md", f"{stem}.md"]:
        _write_markdown(root / "renders" / md_name, report)


def _qa_report_stem(target: Path) -> str:
    if target.name == "final.mp4":
        return "final_qa_report"
    if target.name == "preview.mp4":
        return "preview_qa_report"
    return f"{target.stem}_qa_report"


def _empty_metadata(target: Path) -> dict[str, Any]:
    return {
        "path": str(target),
        "duration": 0.0,
        "width": 0,
        "height": 0,
        "fps": 0.0,
        "video_codec": None,
        "audio_codec": None,
        "has_audio": False,
        "size_bytes": target.stat().st_size if target.exists() else 0,
    }


def _expected_audio(root: Path) -> bool | None:
    try:
        edl = read_json(root / "plan" / "edl.json")
    except Exception:
        return None
    if not isinstance(edl, dict):
        return None
    segments = edl.get("segments")
    if not isinstance(segments, list):
        return None
    saw_existing_source = False
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        source_rel = str(segment.get("source") or "")
        source = _safe_project_path(root, source_rel)
        if source is None:
            continue
        if not source.exists():
            continue
        saw_existing_source = True
        try:
            if probe(source).get("has_audio"):
                return True
        except Exception:
            continue
    return False if saw_existing_source else None


def _expected_duration(root: Path) -> float | None:
    try:
        edl = read_json(root / "plan" / "edl.json")
    except Exception:
        return None
    if not isinstance(edl, dict) or not isinstance(edl.get("segments"), list):
        return None
    total = 0.0
    for segment in edl["segments"]:
        if not isinstance(segment, dict):
            return None
        try:
            start = float(segment["start"])
            end = float(segment["end"])
        except (KeyError, TypeError, ValueError):
            return None
        if end <= start:
            return None
        total += end - start
    return round(total, 3)


def _audio_stats(video: Path) -> dict[str, float] | None:
    try:
        proc = run(
            [
                ffmpeg_bin(),
                "-i",
                str(video),
                "-af",
                "volumedetect",
                "-f",
                "null",
                "-",
            ]
        )
    except Exception:
        return None
    text = f"{proc.stdout}\n{proc.stderr}"
    mean = _parse_volume(text, "mean_volume")
    max_volume = _parse_volume(text, "max_volume")
    if mean is None and max_volume is None:
        return None
    result = {}
    if mean is not None:
        result["mean_volume_db"] = mean
    if max_volume is not None:
        result["max_volume_db"] = max_volume
    return result


def _parse_volume(text: str, label: str) -> float | None:
    match = re.search(rf"{label}:\s*(-?\d+(?:\.\d+)?)\s*dB", text)
    return float(match.group(1)) if match else None


def _safe_project_path(root: Path, rel_path: str) -> Path | None:
    raw = Path(rel_path)
    if raw.is_absolute():
        return None
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root.resolve())
        return candidate
    except ValueError:
        return None


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _default_video(root: Path) -> Path:
    final = root / "renders" / "final.mp4"
    if final.exists():
        return final
    preview = root / "renders" / "preview.mp4"
    if preview.exists():
        return preview
    raise FileNotFoundError("No renders/final.mp4 or renders/preview.mp4 found.")


def _extract_samples(video: Path, duration: float, out_dir: Path) -> list[Path]:
    fractions = [0.02, 0.25, 0.5, 0.75, 0.96]
    paths = []
    for index, fraction in enumerate(fractions, start=1):
        timestamp = max(0.0, min(duration * fraction, max(duration - 0.05, 0.0)))
        out = out_dir / f"sample_{index:02d}.jpg"
        run(
            [
                ffmpeg_bin(),
                "-y",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-q:v",
                "3",
                str(out),
            ]
        )
        paths.append(out)
    return paths


def _write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# QA Report",
        "",
        f"- File: `{report['file']}`",
        f"- Duration: {report['metadata']['duration']:.2f}s",
        f"- Size: {report['metadata']['width']}x{report['metadata']['height']}",
        f"- Passed: {report['passed']}",
        "",
        "## Checks",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- {'PASS' if value else 'FAIL'}: {key}")
    lines.extend(["", "## Frame Means", ", ".join(str(v) for v in report["sampled_frame_means"])])
    if report["black_frames"]:
        lines.extend(["", f"Black frame samples: {', '.join(report['black_frames'])}"])
    if report.get("expected_audio") is not None:
        lines.extend(["", f"- Expected audio: {report['expected_audio']}"])
    if report.get("expected_duration") is not None:
        lines.append(f"- Expected duration: {report['expected_duration']:.2f}s")
    if report.get("audio_stats"):
        lines.append(f"- Audio stats: `{report['audio_stats']}`")
    if report.get("probe_error"):
        lines.extend(["", f"Probe error: `{report['probe_error']}`"])
    if report.get("sample_errors"):
        lines.extend(["", "## Sample Errors", *[f"- {item}" for item in report["sample_errors"]]])
    path.write_text("\n".join(lines), encoding="utf-8")
