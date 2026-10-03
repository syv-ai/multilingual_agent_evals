# Multi Ifeval

This repository generates a multilingual IFEval dataset for 300+ languages. It belongs
to syv.ai; preserve the historical Alexandra Institute attribution in `LICENSE`.

## Stack and layout

- Python 3.12 with `uv` and `uv.lock`; use `uv run` for Python commands.
- `src/multi_ifeval/` contains dataset loading, translation, models and languages.
- `src/scripts/` contains the translation and Hugging Face upload scripts.
- `tests/` contains the pytest suite; `assets/` holds the README logo.

## Running and checking

```bash
uv sync --python 3.12 --locked --all-extras --dev
uv run --python 3.12 --locked pytest
uv run --python 3.12 --locked pre-commit run --all-files
```

See `README.md` for translation usage. Translation requires a model API key; do not
commit keys, `.env` files or generated datasets. Run checks before pushing.

## Git workflow

**Always work directly on `main` in this repository and push commits to `origin/main`.**
Do not create feature branches or PRs for routine agent changes. Check that the main
checkout is clean and up to date with `origin/main` before editing; do not overwrite
uncommitted work or force-push. Use Conventional Commit messages. If direct pushes are
blocked, stop and report the blocker rather than bypassing branch protection.

## Gotchas

- Use Python 3.12 explicitly: newer default interpreters may fail when importing the
  locked dataset dependencies during test collection.
- The `alexandrainst/multi-wiki-qa` IDs are intentional Hugging Face dataset sources.
  The upload script also points at an existing `alexandrainst/multi-ifeval` ID; do not
  redirect dataset publishing as part of a branding change.
- The README logo is tracked at `assets/syv-ai-logo.svg`; do not reference a private
  filesystem path or an externally hosted Alexandra logo.
