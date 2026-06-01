from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from .ffmpeg import ffmpeg_bin, probe, run
from .project import source_files, write_json


def transcribe_project(
    root: Path,
    *,
    model_size: str = "base",
    language: str | None = None,
    device: str = "auto",
    compute_type: str = "auto",
) -> dict[str, Any]:
    transcript_dir = root / "analysis" / "transcripts"
    audio_dir = root / "work" / "audio"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    if importlib.util.find_spec("faster_whisper") is None:
        report = {
            "passed": True,
            "skipped": True,
            "reason": "faster-whisper is not installed.",
            "install": "pip install 'agentic-video-editor[asr]'",
            "outputs": [],
        }
        write_json(root / "analysis" / "transcribe_report.json", report)
        return report

    from faster_whisper import WhisperModel  # type: ignore

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    outputs = []
    for source in source_files(root):
        metadata = probe(source)
        if not metadata.get("has_audio"):
            outputs.append({"source": str(source.relative_to(root)), "skipped": True, "reason": "no audio stream"})
            continue
        audio_path = audio_dir / f"{source.stem}.wav"
        _extract_audio(source, audio_path)
        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,
            vad_filter=True,
        )
        words = []
        for segment in segments:
            for word in segment.words or []:
                text = str(word.word or "").strip()
                if not text:
                    continue
                words.append(
                    {
                        "text": text,
                        "start": round(float(word.start or 0.0), 3),
                        "end": round(float(word.end or word.start or 0.0), 3),
                        "probability": round(float(word.probability or 0.0), 4),
                    }
                )
        payload = {
            "source": str(source.relative_to(root)),
            "language": getattr(info, "language", language),
            "language_probability": round(float(getattr(info, "language_probability", 0.0) or 0.0), 4),
            "duration": metadata["duration"],
            "words": words,
        }
        out_path = transcript_dir / f"{source.stem}.json"
        write_json(out_path, payload)
        outputs.append(
            {
                "source": str(source.relative_to(root)),
                "transcript": str(out_path.relative_to(root)),
                "words": len(words),
                "skipped": False,
            }
        )
    report = {"passed": True, "skipped": False, "model": model_size, "outputs": outputs}
    write_json(root / "analysis" / "transcribe_report.json", report)
    return report


def _extract_audio(source: Path, output: Path) -> None:
    run(
        [
            ffmpeg_bin(),
            "-y",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(output),
        ]
    )
