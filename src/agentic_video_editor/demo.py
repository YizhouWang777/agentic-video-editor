from __future__ import annotations

import json
import math
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .ffmpeg import ffmpeg_bin
from .project import ensure_project, write_json


W, H, FPS = 1080, 1920, 24


def create_demo(root: Path) -> None:
    ensure_project(root)
    source_dir = root / "assets" / "source"
    specs = [
        ("brief.mp4", "BRIEF", "Intent becomes constraints", "#00A6A6", 4.0),
        ("assets.mp4", "ASSETS", "Raw media becomes readable", "#FF5A5F", 4.0),
        ("edl.mp4", "EDL", "Decisions before rendering", "#FFC857", 4.0),
        ("qa.mp4", "QA", "Checks before delivery", "#7B61FF", 4.0),
    ]
    for spec in specs:
        _make_clip(source_dir / spec[0], spec)
    write_json(
        root / "plan" / "edl.json",
        {
            "version": "0.1",
            "render": {"width": W, "height": H, "fps": FPS, "fit": "contain", "caption_style": "bold_safe"},
            "sources": {Path(name).stem: f"assets/source/{name}" for name, *_ in specs},
            "segments": [
                {"source": f"assets/source/{name}", "start": 0, "end": duration, "beat": title}
                for name, title, _subtitle, _accent, duration in specs
            ],
            "captions": [
                {"start": 0.4, "end": 2.6, "text": "Brief first. Tools second."},
                {"start": 4.4, "end": 6.7, "text": "Read assets through metadata and transcripts."},
                {"start": 8.4, "end": 10.8, "text": "EDL separates taste from execution."},
                {"start": 12.4, "end": 15.4, "text": "QA turns bugs into reusable rules."},
            ],
            "overlays": [],
        },
    )
    (root / "template" / "reusable_rules.md").write_text(
        "# Reusable Rules\n\n- Keep source media untouched.\n- Review EDL before rendering.\n- Run QA before delivery.\n",
        encoding="utf-8",
    )


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _make_clip(path: Path, spec: tuple[str, str, str, str, float]) -> None:
    _name, title, subtitle, accent, duration = spec
    path.parent.mkdir(parents=True, exist_ok=True)
    color = tuple(int(accent.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    title_font = _font(96, bold=True)
    subtitle_font = _font(44)
    small_font = _font(30)
    frames = int(duration * FPS)
    with imageio.get_writer(
        path,
        fps=FPS,
        codec="libx264",
        ffmpeg_log_level="error",
        macro_block_size=1,
        output_params=["-pix_fmt", "yuv420p"],
        ffmpeg_params=["-vcodec", "libx264"],
    ) as writer:
        for frame in range(frames):
            progress = frame / max(frames - 1, 1)
            img = Image.new("RGB", (W, H), (12, 16, 24))
            draw = ImageDraw.Draw(img)
            for y in range(0, H, 8):
                shade = int(20 + 24 * y / H)
                draw.rectangle((0, y, W, y + 8), fill=(12, 16 + shade // 3, 24 + shade // 2))
            cx = int(160 + progress * 760)
            cy = int(520 + math.sin(progress * math.tau) * 80)
            draw.ellipse((cx - 220, cy - 220, cx + 220, cy + 220), fill=tuple(int(c * 0.42) for c in color))
            for i in range(5):
                x = 150 + i * 170
                y = 950 + int(math.sin(progress * math.tau + i) * 50)
                draw.rounded_rectangle((x, y, x + 110, y + 110), radius=22, outline=color, width=4)
            _center(draw, title, 690, title_font, (246, 248, 252))
            _center(draw, subtitle, 815, subtitle_font, (210, 217, 228))
            draw.rounded_rectangle((92, 1450, 988, 1580), radius=28, outline=color, width=4)
            _center(draw, f"{title} -> agent-readable artifact", 1492, small_font, (238, 241, 247))
            writer.append_data(np.asarray(img))


def _center(draw: ImageDraw.ImageDraw, text: str, y: int, font: ImageFont.ImageFont, fill: tuple[int, int, int]) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    x = (W - (box[2] - box[0])) / 2
    draw.text((x, y), text, font=font, fill=fill)
