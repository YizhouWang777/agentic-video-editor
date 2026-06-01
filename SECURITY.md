# Security

This project executes local media tooling such as FFmpeg. Treat untrusted media
and untrusted EDL files carefully.

## Reporting

Please do not file public issues for security-sensitive reports. Contact the
maintainers privately once a public security contact exists for the repository.

## Current Guardrails

- EDL sources are restricted to `assets/source/` and `assets/generated/`.
- Source media is not mutated.
- Rendering goes through validation before execution.

## Known Risk Areas

- FFmpeg processes untrusted media.
- Agent-generated EDL files can request expensive renders.
- Future runtime adapters may introduce browser or network surfaces.
