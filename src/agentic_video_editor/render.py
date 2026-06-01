from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from .ffmpeg import ffmpeg_bin, probe, run
from .project import read_json, write_json
from .validate import validate_project


CAPTION_STYLE = (
    "FontName=Helvetica,FontSize=18,Bold=1,"
    "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,"
    "BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=90"
)


def render_project(root: Path, *, preview: bool = False) -> Path:
    validation = validate_project(root)
    if not validation["passed"]:
        failed = [item["id"] for item in validation["checks"] if not item["passed"]]
        raise ValueError(f"EDL validation failed before render: {', '.join(failed)}")
    edl_path = root / "plan" / "edl.json"
    edl = read_json(edl_path)
    render_cfg = edl.get("render", {})
    width = int(render_cfg.get("width") or 1080)
    height = int(render_cfg.get("height") or 1920)
    fps = int(render_cfg.get("fps") or 24)
    out_path = root / "renders" / ("preview.mp4" if preview else "final.mp4")
    work_dir = root / "work" / ("preview_clips" if preview else "clips")
    work_dir.mkdir(parents=True, exist_ok=True)

    segment_paths = []
    for index, segment in enumerate(edl.get("segments", [])):
        segment_paths.append(_extract_segment(root, segment, index, work_dir, width, height, fps, preview=preview))
    if not segment_paths:
        raise ValueError("EDL has no segments. Add segments to plan/edl.json before rendering.")

    base = root / "work" / ("preview_base.mp4" if preview else "base.mp4")
    _concat(segment_paths, base)
    caption_path = _write_srt(root, edl.get("captions", []))
    if caption_path and not preview:
        _burn_subtitles(base, caption_path, out_path)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        base.replace(out_path)
    write_json(
        root / "renders" / ("preview_render_report.json" if preview else "render_report.json"),
        {
            "output": str(out_path.relative_to(root)),
            "segments": [str(p.relative_to(root)) for p in segment_paths],
            "preview": preview,
            "render": {"width": width, "height": height, "fps": fps},
        },
    )
    return out_path


def _extract_segment(
    root: Path,
    segment: dict[str, Any],
    index: int,
    work_dir: Path,
    width: int,
    height: int,
    fps: int,
    *,
    preview: bool,
) -> Path:
    source_rel = segment["source"]
    source = (root / source_rel).resolve()
    start = float(segment.get("start", 0.0))
    end = float(segment["end"])
    duration = max(0.0, end - start)
    if duration <= 0:
        raise ValueError(f"Segment {index} has invalid duration: {segment}")
    out = work_dir / f"seg_{index:03d}.mp4"
    metadata = probe(source)
    volume = float(segment.get("volume", 1.0))
    vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    preset = "ultrafast" if preview else "fast"
    crf = "28" if preview else "20"
    cmd = [
        ffmpeg_bin(),
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(source),
    ]
    if not metadata.get("has_audio"):
        cmd += [
            "-f",
            "lavfi",
            "-t",
            f"{duration:.3f}",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
        ]
    cmd += [
        "-map",
        "0:v:0",
        "-map",
        "0:a:0" if metadata.get("has_audio") else "1:a:0",
        "-t",
        f"{duration:.3f}",
        "-vf",
        vf,
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        crf,
        "-pix_fmt",
        "yuv420p",
    ]
    fade_start = max(0.0, duration - 0.03)
    cmd += [
        "-af",
        f"volume={volume:.3f},afade=t=in:st=0:d=0.03,afade=t=out:st={fade_start:.3f}:d=0.03",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
    ]
    cmd += ["-movflags", "+faststart", str(out)]
    run(cmd)
    return out


def _concat(paths: list[Path], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        list_path = Path(f.name)
        for path in paths:
            escaped = str(path.resolve()).replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")
    try:
        run([ffmpeg_bin(), "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(output)])
    finally:
        list_path.unlink(missing_ok=True)


def _write_srt(root: Path, captions: list[dict[str, Any]]) -> Path | None:
    if not captions:
        return None
    path = root / "work" / "master.srt"
    lines = []
    for index, caption in enumerate(captions, start=1):
        start = float(caption["start"])
        end = float(caption["end"])
        text = str(caption.get("text") or "").strip()
        if not text:
            continue
        lines.extend([str(index), f"{_srt_time(start)} --> {_srt_time(end)}", text, ""])
    if not lines:
        return None
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _burn_subtitles(input_path: Path, srt_path: Path, output_path: Path) -> None:
    escaped = str(srt_path).replace("\\", "\\\\").replace(":", "\\:")
    vf = f"subtitles='{escaped}':force_style='{CAPTION_STYLE}'"
    run(
        [
            ffmpeg_bin(),
            "-y",
            "-i",
            str(input_path),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "copy",
            str(output_path),
        ]
    )


def _srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    h, rem = divmod(millis, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
