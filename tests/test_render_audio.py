import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from agentic_video_editor.ffmpeg import ffmpeg_bin, probe
from agentic_video_editor.project import ensure_project, write_json
from agentic_video_editor.qa import qa_video
from agentic_video_editor.render import render_project


class RenderAudioTests(unittest.TestCase):
    def test_silent_first_concat_preserves_later_audio_stream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)
            source_dir = root / "assets" / "source"
            ffmpeg = ffmpeg_bin()
            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=blue:s=320x240:d=0.8:r=24",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-an",
                    str(source_dir / "silent.mp4"),
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=red:s=320x240:d=0.8:r=24",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=0.8",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    str(source_dir / "audio.mp4"),
                ],
                check=True,
                capture_output=True,
            )
            write_json(
                root / "plan" / "edl.json",
                {
                    "version": "0.1",
                    "render": {"width": 320, "height": 240, "fps": 24},
                    "segments": [
                        {"source": "assets/source/silent.mp4", "start": 0, "end": 0.8},
                        {"source": "assets/source/audio.mp4", "start": 0, "end": 0.8},
                    ],
                    "captions": [],
                    "overlays": [],
                },
            )

            output = render_project(root, preview=True)
            metadata = probe(output)
            qa = qa_video(root, output)

        self.assertTrue(metadata["has_audio"], json.dumps(metadata, indent=2))
        self.assertTrue(qa["checks"]["audio_matches_expectation"])
        self.assertTrue(qa["checks"]["audio_not_silent"])


if __name__ == "__main__":
    unittest.main()
