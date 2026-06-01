from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def pack_transcripts(root: Path, silence_threshold: float = 0.5) -> str:
    transcript_dir = root / "analysis" / "transcripts"
    entries = []
    for path in sorted(transcript_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        words = data.get("words", [])
        if not isinstance(words, list):
            continue
        phrases = group_into_phrases(words, silence_threshold=silence_threshold)
        duration = phrases[-1]["end"] - phrases[0]["start"] if phrases else 0.0
        entries.append((path.stem, duration, phrases))
    packed = render_markdown(entries, silence_threshold)
    out = root / "analysis" / "takes_packed.md"
    out.write_text(packed, encoding="utf-8")
    return packed


def group_into_phrases(words: list[dict[str, Any]], silence_threshold: float = 0.5) -> list[dict[str, Any]]:
    phrases: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    current_start: float | None = None
    current_speaker: str | None = None
    previous_end: float | None = None

    def flush() -> None:
        nonlocal current, current_start, current_speaker
        if not current:
            return
        text = " ".join(str(w.get("text") or "").strip() for w in current).strip()
        text = text.replace(" ,", ",").replace(" .", ".").replace(" ?", "?").replace(" !", "!")
        if text:
            phrases.append(
                {
                    "start": float(current_start or current[0].get("start") or 0.0),
                    "end": float(current[-1].get("end") or current[-1].get("start") or 0.0),
                    "speaker": current_speaker,
                    "text": text,
                }
            )
        current = []
        current_start = None
        current_speaker = None

    for word in words:
        word_type = word.get("type", "word")
        if word_type == "spacing":
            start = word.get("start")
            end = word.get("end")
            if start is not None and end is not None and float(end) - float(start) >= silence_threshold:
                flush()
            continue
        start = word.get("start")
        end = word.get("end", start)
        if start is None:
            continue
        speaker = word.get("speaker_id") or word.get("speaker")
        if current_speaker is not None and speaker is not None and speaker != current_speaker:
            flush()
        if previous_end is not None and float(start) - previous_end >= silence_threshold:
            flush()
        if current_start is None:
            current_start = float(start)
            current_speaker = speaker
        current.append(word)
        previous_end = float(end)
    flush()
    return phrases


def render_markdown(entries: list[tuple[str, float, list[dict[str, Any]]]], silence_threshold: float) -> str:
    lines = [
        "# Packed Transcripts",
        "",
        f"Phrase-level, grouped on silences >= {silence_threshold:.1f}s or speaker change.",
        "Use `[start-end]` ranges to address cuts in the EDL.",
        "",
    ]
    if not entries:
        lines.append("_No transcript JSON files found in `analysis/transcripts/`._")
        return "\n".join(lines)
    for name, duration, phrases in entries:
        lines.append(f"## {name}  (duration: {duration:.1f}s, {len(phrases)} phrases)")
        if not phrases:
            lines.append("  _no speech detected_")
        for phrase in phrases:
            speaker = phrase.get("speaker")
            speaker_tag = f" S{speaker}" if speaker is not None else ""
            lines.append(
                f"  [{phrase['start']:06.2f}-{phrase['end']:06.2f}]{speaker_tag} {phrase['text']}"
            )
        lines.append("")
    return "\n".join(lines)
