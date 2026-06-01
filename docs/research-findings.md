# Research Findings

This scaffold was designed after reading and testing patterns from several
open-source agentic video projects. The goal is not to copy one project. The
goal is to extract the parts that make a general coding agent reliable at video
work.

Repository snapshot, collected on 2026-06-01:

| Project | Stars | Main Lesson |
| --- | ---: | --- |
| [`browser-use/video-use`](https://github.com/browser-use/video-use) | 8723 | Transcript-first editing, timeline views, EDL before render, hard cut rules. |
| [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) | 22924 | HTML-first motion graphics designed for agents, deterministic timeline rendering. |
| [`calesthio/OpenMontage`](https://github.com/calesthio/OpenMontage) | 4184 | Pipeline manifests, checkpoints, stage skills, provider/runtime decisions. |
| [`remotion-dev/skills`](https://github.com/remotion-dev/skills) | 3390 | Progressive skill disclosure for Remotion authoring and preview loops. |
| [`Agents365-ai/video-podcast-maker`](https://github.com/Agents365-ai/video-podcast-maker) | 1110 | Production workflow with review gates and output verification scripts. |
| [`AKMessi/vex`](https://github.com/AKMessi/vex) | 48 | Terminal-first editing state, intent compiler, artifacts, undo/rebuild thinking. |
| [`KyaniteLabs/mcp-video`](https://github.com/KyaniteLabs/mcp-video) | 29 | Typed tool surfaces, guardrails, structured results around FFmpeg/HyperFrames. |
| [`remotion-dev/remotion`](https://github.com/remotion-dev/remotion) | 48604 | Mature React video runtime and renderer primitives. |

## What Good Projects Have In Common

The strong projects do not ask the model to "just edit a video." They narrow
the problem into inspectable artifacts:

1. A brief that captures human intent and taste.
2. An asset manifest that makes raw media addressable.
3. Transcript and timeline packs that make footage readable to a text model.
4. An EDL that separates creative decisions from rendering.
5. A deterministic tool layer for cutting, compositing, subtitles, and motion.
6. QA reports that turn failure into a reusable rule.

This is the reason this project uses:

```text
brief -> asset manifest -> transcript pack -> EDL -> validate -> render -> QA -> reusable rules
```

## Project Notes

### browser-use/video-use

The most important idea is transcript-first editing. The agent should work from
word-level timestamps, timeline views, and packed transcripts before it writes
an EDL. Its strict rules are practical: do not cut inside a word, cache
transcripts, keep subtitles as the last step, extract segments before concat,
and add small fade/padding around cuts. This scaffold adopts the EDL boundary
and includes optional word-boundary validation when transcript JSON exists.

### OpenMontage

OpenMontage treats video generation as a production pipeline, not a single
prompt. It makes the agent read a manifest, choose a runtime, write checkpoints,
and log decisions. This scaffold adopts the project layout, `decision_log.jsonl`,
validation report, and reviewable intermediate artifacts.

### mcp-video

mcp-video is valuable because it does not expose raw FFmpeg as a loose string
interface. It wraps media actions in typed tools, search, guards, and structured
results. This scaffold keeps the same spirit: the CLI commands are stable
surfaces (`inspect`, `pack-transcripts`, `validate`, `render`, `qa`) that an
agent can call repeatedly.

### HyperFrames

HyperFrames is compelling for agent-authored motion graphics because HTML, CSS,
and GSAP are easier for coding agents to write and inspect than many video
timeline formats. Its strongest rule is deterministic rendering: no wall-clock
animation, no unseeded randomness, no render-time network fetches. This scaffold
does not yet ship the HyperFrames adapter, but the runtime-selection contract
keeps a clean place for it.

### Remotion

Remotion is the mature choice for React-based video templates, especially when
the output needs reusable components, type safety, Studio preview, and renderer
APIs. Its skills emphasize progressive disclosure: load only the rules needed
for subtitles, audio, transitions, or FFmpeg. This scaffold mirrors that in the
`skill/references` folder.

### video-podcast-maker

The strongest pattern here is mandatory production review before final render.
It also keeps scripts, templates, timing data, and verification separate. This
scaffold adopts the same idea with preview/final render modes and QA reports.

### Vex

Vex is small but useful because it treats terminal editing as a stateful
conversation. A project should have session logs, artifacts, and a way to
rebuild. This scaffold keeps source media immutable and writes render/validation
reports so the next agent turn can understand what happened.

## Design Decisions

### Why Use EDL As The Center

An EDL is the right central artifact because it lets the agent be creative
without hiding the edit. Humans can inspect it. Validators can reject it. Render
engines can evolve behind it.

### Why Validate Before Render

Video rendering is expensive and failure-prone. Validating the EDL first catches
missing files, invalid ranges, captions outside the timeline, invalid render
dimensions, and transcript word-boundary cuts.

### Why QA After Render

Rendered video can fail even when the EDL is valid: black frames, bad dimensions,
wrong duration, tiny corrupt files, subtitle burn failures, and audio loss. QA is
where these failures become facts the agent can fix.

## Not Implemented Yet

This first version intentionally focuses on the core loop. The next adapters
should be added behind the same EDL/QA boundary:

- Whisper or faster-whisper transcript generation.
- Contact sheets and keyframe extraction for visual understanding.
- HyperFrames adapter for HTML/GSAP motion scenes.
- Remotion adapter for reusable React templates.
- Music beat detection and beat-aligned cuts.
- Richer perceptual QA: OCR subtitle checks, audio silence detection, motion
  delta, and safe-zone occupancy.
