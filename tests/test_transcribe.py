import tempfile
import unittest
from pathlib import Path

from agentic_video_editor.project import ensure_project
from agentic_video_editor.transcribe import transcribe_project


class TranscribeTests(unittest.TestCase):
    def test_transcribe_without_optional_asr_is_skipped_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)

            report = transcribe_project(root)

        self.assertTrue(report["passed"])
        self.assertTrue(report["skipped"])
        self.assertIn("faster-whisper", report["reason"])


if __name__ == "__main__":
    unittest.main()
