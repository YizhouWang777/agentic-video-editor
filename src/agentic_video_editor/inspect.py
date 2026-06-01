from __future__ import annotations

from pathlib import Path

from .ffmpeg import probe
from .project import source_files, write_json


def inspect_project(root: Path) -> list[dict]:
    assets = []
    for path in source_files(root):
        metadata = probe(path)
        assets.append(
            {
                "id": path.stem,
                "file": str(path.relative_to(root)),
                "duration": round(metadata["duration"], 3),
                "width": metadata["width"],
                "height": metadata["height"],
                "fps": metadata["fps"],
                "has_audio": metadata["has_audio"],
                "video_codec": metadata["video_codec"],
                "audio_codec": metadata["audio_codec"],
                "size_bytes": metadata["size_bytes"],
            }
        )
    write_json(root / "analysis" / "asset_manifest.json", assets)
    write_frame_notes(root, assets)
    return assets


def write_frame_notes(root: Path, assets: list[dict]) -> None:
    lines = ["# Frame Notes", ""]
    if not assets:
        lines.append("No videos found in `assets/source/` or `assets/generated/`.")
    for item in assets:
        orientation = "portrait" if item["height"] > item["width"] else "landscape"
        lines.append(f"## {item['id']}")
        lines.append(f"- File: `{item['file']}`")
        lines.append(f"- Duration: {item['duration']}s")
        lines.append(f"- Size: {item['width']}x{item['height']} ({orientation})")
        lines.append(f"- Audio: {'yes' if item['has_audio'] else 'no'}")
        lines.append("- Agent note: inspect transcript and timeline views before making creative cuts.")
        lines.append("")
    (root / "analysis" / "frame_notes.md").write_text("\n".join(lines), encoding="utf-8")
