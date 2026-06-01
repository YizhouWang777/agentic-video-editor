# Hard Rules

## Source Safety

- Never overwrite `assets/source/*`.
- Write generated files under `assets/generated/`, `work/`, `analysis/`,
  `plan/`, or `renders/`.
- EDL sources must stay inside `assets/source/` or `assets/generated/`.

## Timing

- EDL segment times are source-local.
- Captions are final-timeline local.
- Do not cut inside a word when word timestamps exist.
- Add micro fades around speech cuts when possible.

## Rendering

- Render base edit first.
- Apply captions after base edit assembly.
- Keep preview timing identical to final timing.
- Do not silently substitute a runtime. Log the choice.
- Normalize rendered segments to a consistent video/audio stream layout before concat.

## Failure

- If validation fails, patch the EDL before rendering.
- If QA fails, patch the smallest artifact that explains the failure.
- Do not call a failed render complete.
