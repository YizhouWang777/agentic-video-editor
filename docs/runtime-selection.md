# Runtime Selection

The agent should choose the smallest runtime that can do the job.

## FFmpeg

Use FFmpeg for:

- Trimming source footage.
- Concat and transcode.
- Format conversion.
- Letterboxing/pillarboxing.
- Subtitle burn.
- Simple fades.

FFmpeg is the default for the base edit.

## HyperFrames

Use HyperFrames when the video needs agent-authored motion graphics:

- Social cards.
- Data visualization.
- Kinetic text.
- GLSL transitions.
- HTML/CSS/GSAP scenes.

Rules:

- Keep timelines deterministic.
- Do not rely on wall-clock animation.
- Do not fetch network assets at render time.
- Validate scenes before final render.

## Remotion

Use Remotion when the video needs reusable React templates:

- Branded recurring formats.
- Componentized layouts.
- Programmatic subtitles.
- Template libraries for many videos.

Rules:

- Use `useCurrentFrame()` and interpolation for animation state.
- Preview in Studio when possible.
- Keep templates parameterized by JSON timing and content.

## External APIs

Use commercial APIs only behind a clear artifact boundary:

- TTS output becomes audio in `assets/generated/`.
- Image generation output becomes images in `assets/generated/`.
- Video generation output becomes clips in `assets/generated/`.

Never make final rendering depend on a remote API call.
