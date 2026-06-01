from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .ffmpeg import ffmpeg_bin, probe, run
from .project import source_files, write_json


def create_contact_sheets(root: Path, *, frames_per_asset: int = 8, thumb_width: int = 320) -> list[dict[str, Any]]:
    frames_per_asset = max(1, frames_per_asset)
    keyframe_dir = root / "analysis" / "keyframes"
    sheet_dir = root / "analysis" / "contact_sheets"
    keyframe_dir.mkdir(parents=True, exist_ok=True)
    sheet_dir.mkdir(parents=True, exist_ok=True)

    reports = []
    for source in source_files(root):
        metadata = probe(source)
        timestamps = _timestamps(float(metadata["duration"]), frames_per_asset)
        frame_paths = []
        for index, timestamp in enumerate(timestamps, start=1):
            frame_path = keyframe_dir / f"{source.stem}_{index:02d}_{timestamp:.2f}s.jpg"
            _extract_frame(source, timestamp, frame_path)
            frame_paths.append(frame_path)
        sheet_path = sheet_dir / f"{source.stem}.jpg"
        _compose_sheet(sheet_path, source.stem, frame_paths, timestamps, thumb_width=thumb_width)
        reports.append(
            {
                "id": source.stem,
                "file": str(source.relative_to(root)),
                "duration": metadata["duration"],
                "width": metadata["width"],
                "height": metadata["height"],
                "fps": metadata["fps"],
                "frames": [str(path.relative_to(root)) for path in frame_paths],
                "contact_sheet": str(sheet_path.relative_to(root)),
            }
        )
    write_json(root / "analysis" / "contact_sheet_report.json", reports)
    _write_timeline_view(root, reports)
    return reports


def _timestamps(duration: float, count: int) -> list[float]:
    if duration <= 0:
        return [0.0]
    if count == 1:
        return [min(duration * 0.5, max(duration - 0.05, 0.0))]
    return [round(min(duration * (i + 0.5) / count, max(duration - 0.05, 0.0)), 3) for i in range(count)]


def _extract_frame(source: Path, timestamp: float, output: Path) -> None:
    run(
        [
            ffmpeg_bin(),
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-q:v",
            "3",
            str(output),
        ]
    )


def _compose_sheet(output: Path, title: str, frames: list[Path], timestamps: list[float], *, thumb_width: int) -> None:
    thumbs = []
    for frame in frames:
        image = Image.open(frame).convert("RGB")
        ratio = thumb_width / image.width
        thumb_height = max(1, int(image.height * ratio))
        thumbs.append(image.resize((thumb_width, thumb_height)))
    if not thumbs:
        return
    cols = min(4, len(thumbs))
    rows = math.ceil(len(thumbs) / cols)
    label_h = 34
    title_h = 48
    gap = 10
    cell_w = thumb_width
    cell_h = max(img.height for img in thumbs) + label_h
    width = cols * cell_w + (cols + 1) * gap
    height = title_h + rows * cell_h + (rows + 1) * gap
    sheet = Image.new("RGB", (width, height), (18, 22, 30))
    draw = ImageDraw.Draw(sheet)
    font = _font(18)
    title_font = _font(24)
    draw.text((gap, 12), title, fill=(244, 247, 252), font=title_font)
    for index, image in enumerate(thumbs):
        row, col = divmod(index, cols)
        x = gap + col * (cell_w + gap)
        y = title_h + gap + row * (cell_h + gap)
        sheet.paste(image, (x, y))
        draw.text((x, y + image.height + 6), f"{timestamps[index]:.2f}s", fill=(220, 226, 235), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=88)


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _write_timeline_view(root: Path, reports: list[dict[str, Any]]) -> None:
    lines = [
        "# Timeline View",
        "",
        "Visual index generated from source media. Use these contact sheets before drafting an EDL.",
        "",
    ]
    if not reports:
        lines.append("_No source videos found._")
    for item in reports:
        lines.append(f"## {item['id']}")
        lines.append(f"- Source: `{item['file']}`")
        lines.append(f"- Duration: {float(item['duration']):.2f}s")
        lines.append(f"- Size: {item['width']}x{item['height']} at {item['fps']}fps")
        lines.append(f"- Contact sheet: `{item['contact_sheet']}`")
        lines.append("- Frames:")
        for frame in item["frames"]:
            lines.append(f"  - `{frame}`")
        lines.append("")
    (root / "analysis" / "timeline_view.md").write_text("\n".join(lines), encoding="utf-8")
