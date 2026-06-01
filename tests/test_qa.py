import tempfile
import unittest
from pathlib import Path

from agentic_video_editor.project import ensure_project
from agentic_video_editor.qa import qa_video


class QATests(unittest.TestCase):
    def test_qa_missing_video_returns_structured_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ensure_project(root)

            report = qa_video(root, root / "renders" / "missing.mp4")

        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["file_exists"])
        self.assertIn("Target video does not exist.", report["sample_errors"])


if __name__ == "__main__":
    unittest.main()
