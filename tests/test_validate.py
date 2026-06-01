from pathlib import Path
import subprocess
import tempfile
import unittest

from agentic_video_editor.ffmpeg import ffmpeg_bin
from agentic_video_editor.project import ensure_project, write_json
from agentic_video_editor.validate import validate_project


class ValidateTests(unittest.TestCase):
    def test_validate_rejects_empty_edl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)

            report = validate_project(root)

        self.assertFalse(report["passed"])
        self.assertTrue(any(check["id"] == "segments_present" and not check["passed"] for check in report["checks"]))

    def test_validate_rejects_bad_caption_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            source = root / "assets" / "source" / "missing.mp4"
            write_json(
                root / "plan" / "edl.json",
                {
                    "version": "0.1",
                    "render": {"width": 1080, "height": 1920, "fps": 24},
                    "segments": [{"source": str(source.relative_to(root)), "start": 0, "end": 2}],
                    "captions": [
                        {"start": 1.0, "end": 1.5, "text": "first"},
                        {"start": 0.5, "end": 0.9, "text": "second"},
                    ],
                    "overlays": [],
                },
            )

            report = validate_project(root)

        self.assertFalse(report["passed"])
        self.assertTrue(any(check["id"] == "caption_001_valid" and not check["passed"] for check in report["checks"]))

    def test_validate_rejects_sources_outside_asset_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            write_json(
                root / "plan" / "edl.json",
                {
                    "version": "0.1",
                    "render": {"width": 1080, "height": 1920, "fps": 24},
                    "segments": [{"source": "../outside.mp4", "start": 0, "end": 1}],
                    "captions": [],
                    "overlays": [],
                },
            )

            report = validate_project(root)

        self.assertFalse(report["passed"])
        self.assertTrue(
            any(check["id"] == "segment_000_source_allowed" and not check["passed"] for check in report["checks"])
        )

    def test_validate_reports_malformed_render_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            write_json(
                root / "plan" / "edl.json",
                {
                    "version": "0.1",
                    "render": {"width": "1080px", "height": 1920, "fps": "24.0"},
                    "segments": [],
                    "captions": [],
                    "overlays": [],
                },
            )

            report = validate_project(root)

        self.assertFalse(report["passed"])
        self.assertTrue(any(check["id"] == "render_dimensions" and not check["passed"] for check in report["checks"]))

    def test_validate_rejects_invalid_segment_volume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            source = root / "assets" / "source" / "clip.mp4"
            subprocess.run(
                [
                    ffmpeg_bin(),
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=black:s=160x90:d=0.5:r=12",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-an",
                    str(source),
                ],
                check=True,
                capture_output=True,
            )
            write_json(
                root / "plan" / "edl.json",
                {
                    "version": "0.1",
                    "render": {"width": 1080, "height": 1920, "fps": 24},
                    "segments": [{"source": "assets/source/clip.mp4", "start": 0, "end": 1, "volume": 9}],
                    "captions": [],
                    "overlays": [],
                },
            )

            report = validate_project(root)

        self.assertFalse(report["passed"])
        self.assertTrue(any(check["id"] == "segment_000_volume_valid" and not check["passed"] for check in report["checks"]))


if __name__ == "__main__":
    unittest.main()
