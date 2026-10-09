<!-- markdownlint-disable MD041 -->
<a href="https://github.com/syv-ai/multilingual_agent_evals">
<img
 src="assets/syv-ai-logo.svg"
 width="120"
 height="172"
 align="right"
 alt="syv.ai logo"
/>
</a>

# Multilingual Agent Evaluations

Two separate multilingual datasets for agent-relevant capabilities:

| Dataset | Capability | Public release |
| --- | --- | --- |
| **MultiIFEval** | Verifiable instruction following, 305 language configurations | [Hugging Face](https://huggingface.co/datasets/danish-foundation-models/multi-ifeval) (CC BY-NC-SA 4.0) |
| **MultiBFCL** | Tool calling on BFCL-v2 subsets, 305 language configurations | [Hugging Face](https://huggingface.co/datasets/syvai/multi-bfcl) (CC BY-NC 4.0) |

The source packages remain independent under `src/multi_ifeval/` and
`src/multi_bfcl/`. This repository is not a third dataset, and neither dataset's
Hugging Face identifier has changed. MultiBFCL uses BFCL-v2 categories from the
upstream `BFCL_v4_*` file layout. For more details on the paper and its remaining
work, see [`paper/README.md`](paper/README.md).

## Install and check

Python 3.12 and [uv](https://docs.astral.sh/uv/) are required.

```bash
uv sync --python 3.12 --locked --all-extras --dev
uv run --python 3.12 --locked pytest
uv run --python 3.12 --locked pre-commit run --all-files
```

## Translate

Translation requires model API credentials and may incur API costs. The two CLIs
are separate and save per-language, resumable JSONL checkpoints in `data/`:

```bash
uv run --python 3.12 --locked src/scripts/translate_ifeval.py --help
uv run --python 3.12 --locked src/scripts/translate_bfcl.py --help
```

Keep `.env`, generated datasets, and translation checkpoints out of Git. The
MultiBFCL loader currently fetches its upstream source from a moving branch;
pin that source revision for reproducible runs. The code is MIT-licensed with
historical Alexandra Institute attribution in `LICENSE`; dataset licences are
listed separately above.

## Evaluation and paper

Both resources can use local EuroEval configurations: see
[`paper/run_euroeval.py`](paper/run_euroeval.py) for MultiIFEval and
[`paper/run_multibfcl.py`](paper/run_multibfcl.py) for the public MultiBFCL
release. EuroEval has BFCL-v2 English and 31 translated MultiBFCL language
registrations for its separate `tool-calling` metric. Its derived mini datasets
may require access, so the public MultiBFCL Hub release is the data source.
Neither task's registration is a model score. The
[combined NoDaLiDa draft](paper/acl_latex.tex) keeps both tasks, methods,
metrics, and limitations distinct; reported model results still need to be
collected and checked.
