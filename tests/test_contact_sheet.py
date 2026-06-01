import subprocess
import tempfile
import unittest
from pathlib import Path

from agentic_video_editor.contact_sheet import create_contact_sheets
from agentic_video_editor.ffmpeg import ffmpeg_bin
from agentic_video_editor.project import ensure_project


class ContactSheetTests(unittest.TestCase):
    def test_contact_sheet_generates_keyframes_and_timeline_view(self) -> None:
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
                    "color=c=green:s=160x90:d=0.6:r=12",
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

            report = create_contact_sheets(root, frames_per_asset=2, thumb_width=120)

            self.assertEqual(len(report), 1)
            self.assertTrue((root / report[0]["contact_sheet"]).exists())
            self.assertTrue((root / "analysis" / "timeline_view.md").exists())


if __name__ == "__main__":
    unittest.main()
