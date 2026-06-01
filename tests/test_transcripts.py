import unittest

from agentic_video_editor.transcripts import group_into_phrases


class TranscriptTests(unittest.TestCase):
    def test_group_into_phrases_splits_on_silence(self) -> None:
        words = [
            {"text": "Hello", "start": 0.0, "end": 0.2},
            {"text": "world", "start": 0.25, "end": 0.5},
            {"type": "spacing", "start": 0.5, "end": 1.2},
            {"text": "again", "start": 1.2, "end": 1.5},
        ]

        phrases = group_into_phrases(words, silence_threshold=0.5)

        self.assertEqual(
            phrases,
            [
                {"start": 0.0, "end": 0.5, "speaker": None, "text": "Hello world"},
                {"start": 1.2, "end": 1.5, "speaker": None, "text": "again"},
            ],
        )

    def test_group_into_phrases_splits_on_speaker_change(self) -> None:
        words = [
            {"text": "A", "start": 0.0, "end": 0.2, "speaker": "1"},
            {"text": "B", "start": 0.25, "end": 0.5, "speaker": "2"},
        ]

        phrases = group_into_phrases(words, silence_threshold=0.5)

        self.assertEqual(len(phrases), 2)
        self.assertEqual(phrases[0]["speaker"], "1")
        self.assertEqual(phrases[1]["speaker"], "2")


if __name__ == "__main__":
    unittest.main()
