# Runtime Selection Reference

## FFmpeg First

Use FFmpeg for the base edit because it is deterministic, fast, local, and easy
to validate.

## HyperFrames

Use HyperFrames for agent-authored HTML motion scenes. Keep animation
deterministic and render-time assets local.

## Remotion

Use Remotion for reusable React video templates. Keep templates parameterized by
JSON timing/content artifacts so the agent can update many videos safely.

## External APIs

Commercial APIs may create assets, but final assembly should stay local and
reproducible.
