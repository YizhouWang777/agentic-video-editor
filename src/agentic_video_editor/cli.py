from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contact_sheet import create_contact_sheets
from .demo import create_demo
from .doctor import doctor
from .failure import explain_failure
from .inspect import inspect_project
from .log import log_decision
from .project import ensure_project
from .qa import qa_video
from .render import render_project
from .transcribe import transcribe_project
from .transcripts import pack_transcripts
from .validate import validate_project


def main() -> None:
    parser = argparse.ArgumentParser(prog="ave", description="Agentic video editing scaffold")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="Create a project workspace")
    init.add_argument("project", type=Path)

    demo = sub.add_parser("demo", help="Create synthetic demo sources and EDL")
    demo.add_argument("project", type=Path)

    inspect = sub.add_parser("inspect", help="Probe source assets")
    inspect.add_argument("project", type=Path)

    contact = sub.add_parser("contact-sheet", help="Create keyframes, contact sheets, and timeline view")
    contact.add_argument("project", type=Path)
    contact.add_argument("--frames", type=int, default=8)
    contact.add_argument("--thumb-width", type=int, default=320)

    transcribe = sub.add_parser("transcribe", help="Transcribe source assets; skips cleanly when ASR is not installed")
    transcribe.add_argument("project", type=Path)
    transcribe.add_argument("--model", default="base")
    transcribe.add_argument("--language", default=None)
    transcribe.add_argument("--device", default="auto")
    transcribe.add_argument("--compute-type", default="auto")

    pack = sub.add_parser("pack-transcripts", help="Pack transcript JSON files into takes_packed.md")
    pack.add_argument("project", type=Path)

    render = sub.add_parser("render", help="Render plan/edl.json")
    render.add_argument("project", type=Path)
    render.add_argument("--preview", action="store_true")

    validate = sub.add_parser("validate", help="Validate plan/edl.json before rendering")
    validate.add_argument("project", type=Path)

    qa = sub.add_parser("qa", help="Run technical QA")
    qa.add_argument("project", type=Path)
    qa.add_argument("--video", type=Path, default=None)

    explain = sub.add_parser("explain-failure", help="Summarize validation and QA failures")
    explain.add_argument("project", type=Path)

    decision = sub.add_parser("log-decision", help="Append an agent decision to plan/decision_log.jsonl")
    decision.add_argument("project", type=Path)
    decision.add_argument("--stage", required=True)
    decision.add_argument("--decision", required=True)
    decision.add_argument("--reason", required=True)

    health = sub.add_parser("doctor", help="Check local runtime dependencies and project structure")
    health.add_argument("project", type=Path, nargs="?")

    args = parser.parse_args()
    root = args.project.resolve() if getattr(args, "project", None) is not None else None

    if args.cmd == "init":
        assert root is not None
        ensure_project(root)
        print(root)
    elif args.cmd == "demo":
        assert root is not None
        create_demo(root)
        print(root)
    elif args.cmd == "inspect":
        assert root is not None
        print(json.dumps(inspect_project(root), indent=2))
    elif args.cmd == "contact-sheet":
        assert root is not None
        print(json.dumps(create_contact_sheets(root, frames_per_asset=args.frames, thumb_width=args.thumb_width), indent=2))
    elif args.cmd == "transcribe":
        assert root is not None
        print(
            json.dumps(
                transcribe_project(
                    root,
                    model_size=args.model,
                    language=args.language,
                    device=args.device,
                    compute_type=args.compute_type,
                ),
                indent=2,
            )
        )
    elif args.cmd == "pack-transcripts":
        assert root is not None
        print(pack_transcripts(root))
    elif args.cmd == "render":
        assert root is not None
        out = render_project(root, preview=args.preview)
        print(out)
    elif args.cmd == "validate":
        assert root is not None
        print(json.dumps(validate_project(root), indent=2))
    elif args.cmd == "qa":
        assert root is not None
        video = args.video
        if video is not None and not video.is_absolute():
            video = root / video
        print(json.dumps(qa_video(root, video), indent=2))
    elif args.cmd == "explain-failure":
        assert root is not None
        print(explain_failure(root))
    elif args.cmd == "log-decision":
        assert root is not None
        print(json.dumps(log_decision(root, stage=args.stage, decision=args.decision, reason=args.reason), indent=2))
    elif args.cmd == "doctor":
        print(json.dumps(doctor(root), indent=2))


if __name__ == "__main__":
    main()
