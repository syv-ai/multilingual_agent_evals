# Multilingual Agent Evaluations

This syv.ai repository contains two separate multilingual evaluation resources:
MultiIFEval (verifiable instruction following) and MultiBFCL (BFCL-v2 tool calling).
Preserve the Alexandra Institute attribution in `LICENSE`.

## Stack and layout

- Python 3.12, `uv`, one `uv.lock`, and two installable packages under `src/`:
  `multi_ifeval/` and `multi_bfcl/`.
- `src/scripts/` contains separate translation CLIs and dataset utilities.
- `tests/` covers both packages. `paper/` contains the combined NoDaLiDa draft.
- `data/` holds ignored JSONL translation checkpoints. Never commit them or `.env`.

## Running and checking

```bash
uv sync --python 3.12 --locked --all-extras --dev
uv run --python 3.12 --locked pytest
uv run --python 3.12 --locked pre-commit run --all-files
```

Translation requires a model API key and may spend money. Do not run translation
as a test. Both scripts resume from `data/<benchmark>-<language>.jsonl`:

```bash
uv run --python 3.12 --locked src/scripts/translate_ifeval.py --help
uv run --python 3.12 --locked src/scripts/translate_bfcl.py --help
```

## Git workflow

Work directly on `main` and push commits to `origin/main`. Check for a clean,
up-to-date main checkout before editing. Do not overwrite other work, force-push,
or use worktrees for routine changes. Use Conventional Commit messages. If direct
pushes are blocked, report the blocker instead of bypassing branch protection.

## Gotchas

- Use Python 3.12 explicitly: newer defaults can fail on locked dependencies.
- MultiBFCL's BFCL-v2 category files are named `BFCL_v4_*` upstream. The loader
  currently follows upstream `main`; pin the source before claiming a reproducible
  release. Its translation does not translate tool metadata.
- The public datasets are separate: `danish-foundation-models/multi-ifeval`
  (CC BY-NC-SA 4.0) and `syvai/multi-bfcl` (CC BY-NC 4.0). Do not rename or
  republish either dataset as part of a code-repository change. Existing
  `alexandrainst/multi-wiki-qa` sources and the IFEval upload target
  `alexandrainst/multi-ifeval` are intentional legacy identifiers.
- MultiBFCL's ignored `data/bfcl-*.jsonl` files are resumable checkpoints;
  deleting one restarts that language. `load_bfcl()` downloads upstream on each
  call and may wait 60 seconds on a rate limit. Keep API keys and local caches
  out of Git.
- EuroEval's 31 translated BFCL registrations plus English constitute its
  32-language tool-calling support. Its derived `EuroEval/multi-bfcl-*-mini`
  repositories may be private; registration is not a published model result.
- In `paper/`, `run_euroeval.py` is named deliberately: a file named
  `evaluate.py` shadows EuroEval's `evaluate` dependency. The paper is still a
  draft without full model results or an anonymous reviewer-accessible release.
