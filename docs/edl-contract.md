# EDL Contract

The EDL is stored at `plan/edl.json`.

## Minimal Example

```json
{
  "version": "0.1",
  "render": {
    "width": 1080,
    "height": 1920,
    "fps": 24,
    "caption_style": "bold_safe"
  },
  "sources": {
    "intro": "assets/source/intro.mp4"
  },
  "segments": [
    {
      "source": "assets/source/intro.mp4",
      "start": 0.2,
      "end": 3.8,
      "beat": "hook",
      "volume": 1.0
    }
  ],
  "captions": [
    {
      "start": 0.4,
      "end": 2.4,
      "text": "Brief first. Tools second."
    }
  ],
  "overlays": []
}
```

## Rules

- Source media paths are relative to the project root.
- Source media must stay under `assets/source/` or `assets/generated/`.
- Source media under `assets/source/` must stay untouched.
- Segment `start` and `end` are source-local seconds.
- Segment `volume` is optional and must be between 0.0 and 4.0.
- Caption `start` and `end` are final-timeline seconds.
- Subtitles are applied after the base edit is rendered.
- If word-level transcripts exist, cuts must not land inside a word.
- Every rendered segment is normalized to h264 video plus AAC audio. Silent
  sources receive generated silent audio so concat does not drop later audio.
- Preview renders may use lower quality settings, but must preserve timing.
- Final renders must run QA after completion.
