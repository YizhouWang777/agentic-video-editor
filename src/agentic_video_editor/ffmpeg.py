from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import imageio.v2 as imageio
import imageio_ffmpeg


def ffmpeg_bin() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def ffprobe_bin() -> str | None:
    path = Path(ffmpeg_bin())
    candidate = path.with_name(path.name.replace("ffmpeg", "ffprobe", 1))
    if candidate.exists():
        return str(candidate)
    return shutil.which("ffprobe")


def run(cmd: list[str], *, quiet: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        capture_output=quiet,
    )


def probe(path: Path) -> dict[str, Any]:
    ffprobe = ffprobe_bin()
    if ffprobe:
        try:
            return _probe_with_ffprobe(path, ffprobe)
        except (json.JSONDecodeError, subprocess.CalledProcessError):
            pass
    return _probe_with_ffmpeg(path)


def _probe_with_ffprobe(path: Path, ffprobe: str) -> dict[str, Any]:
    out = run(
        [
            ffprobe,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ]
    ).stdout
    data = json.loads(out)
    streams = data.get("streams", [])
    fmt = data.get("format", {})
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fps = _fps(video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/0")
    return {
        "path": str(path),
        "duration": float(fmt.get("duration") or video.get("duration") or 0.0),
        "width": int(video.get("width") or 0),
        "height": int(video.get("height") or 0),
        "fps": fps,
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name") if audio else None,
        "has_audio": audio is not None,
        "size_bytes": int(fmt.get("size") or path.stat().st_size),
    }


def _probe_with_ffmpeg(path: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-i", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    text = f"{proc.stdout}\n{proc.stderr}"
    video_line = next((line for line in text.splitlines() if " Video:" in line), "")
    audio_line = next((line for line in text.splitlines() if " Audio:" in line), "")
    width, height = _parse_size(video_line)
    duration = _parse_duration(text)
    fps = _parse_ffmpeg_fps(video_line)
    video_codec = _parse_codec(video_line, "Video")
    audio_codec = _parse_codec(audio_line, "Audio") if audio_line else None
    if not duration or not width or not height or not fps:
        metadata = _probe_with_imageio(path)
        duration = duration or metadata["duration"]
        width = width or metadata["width"]
        height = height or metadata["height"]
        fps = fps or metadata["fps"]
    return {
        "path": str(path),
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "video_codec": video_codec,
        "audio_codec": audio_codec,
        "has_audio": audio_codec is not None,
        "size_bytes": path.stat().st_size,
    }


def _probe_with_imageio(path: Path) -> dict[str, Any]:
    reader = imageio.get_reader(path)
    try:
        meta = reader.get_meta_data()
    finally:
        reader.close()
    size = meta.get("size") or (0, 0)
    return {
        "duration": float(meta.get("duration") or 0.0),
        "width": int(size[0] or 0),
        "height": int(size[1] or 0),
        "fps": float(meta.get("fps") or 0.0),
    }


def _parse_duration(text: str) -> float:
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if not match:
        return 0.0
    hours, minutes, seconds = match.groups()
    return round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3)


def _parse_size(line: str) -> tuple[int, int]:
    match = re.search(r"(?<![a-zA-Z])(\d{2,5})x(\d{2,5})(?![a-zA-Z])", line)
    if not match:
        return 0, 0
    return int(match.group(1)), int(match.group(2))


def _parse_ffmpeg_fps(line: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s+fps", line)
    return float(match.group(1)) if match else 0.0


def _parse_codec(line: str, stream_type: str) -> str | None:
    match = re.search(rf"{stream_type}:\s*([^,\s]+)", line)
    return match.group(1) if match else None


def _fps(rate: str) -> float:
    if not rate or rate == "0/0":
        return 0.0
    if "/" in rate:
        num, den = rate.split("/", 1)
        denominator = float(den)
        return round(float(num) / denominator, 3) if denominator else 0.0
    return float(rate)
