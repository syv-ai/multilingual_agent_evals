# MultiBFCL

Machine-translated version of the BFCL-v2 (Berkeley Function Call Leaderboard)
benchmark. The package downloads BFCL-v2 tool-calling examples and translates
them into many languages using an LLM, producing per-language JSONL datasets in
`data/`.

## Stack

- Python 3.12, managed with `uv` (lockfile: `uv.lock`); hatchling build backend.
- Runtime deps: `datasets`, `litellm`. Dev deps: `pytest`, `ruff`, `pyrefly`,
  `pre-commit`, `mkdocs-material`, `readme-coverage-badger`.
- Type checking is done with **pyrefly**, not mypy/pyright.

## Layout

- `src/multi_bfcl/` — the package. Modules use **relative imports**
  (`from .data_models import Example`).
- `src/scripts/` — executable CLIs (click-based). Scripts use **absolute
  imports** (`from multi_bfcl import ...`) and are the only code called from
  the terminal.
- `tests/` — pytest tests (also import via absolute imports).
- `data/` — translated output, one `bfcl-<lang-code>.jsonl` per language.
- `docs/` — mkdocs site; API reference is generated from docstrings (mkapi).

## Running it

```bash
make install-non-interactive   # agent/CI-safe setup (uv, deps, pre-commit)
source .venv/bin/activate      # or prefix commands with `uv run`

uv run src/scripts/translate_bfcl.py --model <model> [--api-base <url>]
```

- `make check` — lint, format, type-check (pre-commit: ruff, pyrefly,
  markdownlint).
- `make test` — `pytest` + `readme-cov` (see gotchas).
- `make docs` / `make publish-docs` — local mkdocs serve / GitHub Pages deploy.

## Conventions

- Google-style docstrings and full type annotations are enforced (ruff `D`,
  `ANN`, `DOC` rules + pygrep `python-use-type-annotations`).
- ruff: line length 88, double quotes, `skip-magic-trailing-comma`.
- Commits follow Conventional Commits (`feat:`, `fix:`, `docs:`, ...).
- CI runs pre-commit plus a pytest matrix (Windows/macOS/Linux, Python 3.12)
  on PRs to `main`.

## Gotchas

- **`make install` is interactive** (prompts for git name/email). Use
  `make install-non-interactive` in agents, CI, or scripts.
- **`make test` rewrites `README.md`** to update the coverage badge. Commit
  that README change alongside test changes.
- **`load_bfcl()` downloads data from the network on every call**
  (BFCL-v4 JSON from the gorilla repo on raw.githubusercontent.com). It
  retries on HTTP 429 with a 60 s sleep. No offline mode.
- **`load_languages()` derives the language list from the Hugging Face
  dataset `alexandrainst/multi-wiki-qa`** (its config names). A language is
  only translatable if it appears both there and as a module-level `Language`
  constant in `src/multi_bfcl/languages.py` — `get_all_languages()` discovers
  languages by scanning module `globals()`, so new languages must be
  top-level constants, not local variables.
- **`translate_bfcl.py` currently has a TEMP guard that only translates
  DANISH** (`if language != DANISH: continue`). This is a deliberate
  temporary restriction, not a bug.
- **Translation requires an LLM API** (litellm). Default model is
  `gemini/gemini-3.1-flash-lite-preview`; `--api-base` points at a custom
  OpenAI-compatible endpoint.
- **Output files are resumable checkpoints**: `data/bfcl-<lang>.jsonl` is
  loaded at startup and already-translated example IDs are skipped. Deleting
  a file restarts that language.
- **pytest treats warnings as errors** (`filterwarnings = ["error", ...]` in
  `pyproject.toml`), runs `--doctest-modules` over `src/multi_bfcl`, and
  collects coverage for `src/multi_bfcl` — new warnings or broken docstring
  examples break `make test`.
- `.env` and `.name_and_email` are gitignored and created by
  `src/scripts/fix_dot_env_file.py` (holds `GIT_NAME`/`GIT_EMAIL`).
- `data/raw/`, `data/processed/`, `data/final/`, and `models/` are gitignored
  placeholder dirs from the template; actual output goes to `data/` directly.
