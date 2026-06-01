# Publishing

The repository is prepared for a public alpha release.

## Create A GitHub Repository

With GitHub CLI:

```bash
gh repo create agentic-video-editor --public --source=. --remote=origin --push
```

With an existing remote:

```bash
git remote add origin git@github.com:<owner>/agentic-video-editor.git
git push -u origin main
git push origin v0.1.0
```

## Release Checklist

```bash
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests
ave demo /tmp/ave-smoke
ave inspect /tmp/ave-smoke
ave contact-sheet /tmp/ave-smoke --frames 2 --thumb-width 160
ave transcribe /tmp/ave-smoke
ave pack-transcripts /tmp/ave-smoke
ave validate /tmp/ave-smoke
ave render /tmp/ave-smoke --preview
ave qa /tmp/ave-smoke --video renders/preview.mp4
ave render /tmp/ave-smoke
ave qa /tmp/ave-smoke
.venv/bin/python -m pip wheel --no-deps -w /tmp/ave-wheel .
```

## Notes

- Generated videos and analysis artifacts are intentionally ignored.
- ASR support is optional and installed with `pip install -e '.[asr]'`.
- `ffprobe` is optional; the project falls back to FFmpeg/imageio probing.
