# NoDaLiDa 2027 submission

The [official call](https://eventsignup.ku.dk/nodalida-27/call-for-papers)
requires ACL style files; `acl_latex.tex` uses `acl.sty` in `review` mode.
The bundled `acl.sty` matches the latest official ACL style-files repo revision
checked on 3 October 2026 (`d5adc823ff0f80f98c80405ca0ab66c68e684409`).
The companion `acl_natbib.bst` is from that revision (with whitespace trimmed).
There is no separate NoDaLiDa LaTeX template. The current draft is aimed at a
**regular paper** (up to eight content pages; references, optional limitations and
ethical considerations sections excluded). A four-page short or demonstration paper
would require further cuts. Appendices are optional and reviewers need not read them.
Check the current call again before submitting; the direct-submission deadline is
**18 January 2027**, ARR commitment **22 February 2027**, and camera-ready
**5 April 2027**. Submit via OpenReview when the link becomes available.

Keep the review PDF anonymous: do not restore the author block, identify the team in
acknowledgements, or link directly to the released Hub repository, whose commit
history identifies the uploader. Arrange a reviewer-accessible anonymous copy or
other CFP-compliant access method before submission. For camera-ready, restore the
original public URL, accurate author affiliations and acknowledgements. The dataset
has already been released at
<https://huggingface.co/datasets/danish-foundation-models/multi-ifeval> under
CC BY-NC-SA 4.0. The live Hub split listing currently exposes 305 language
configurations; pin a Hub commit and check counts before making precise claims.

## Small evaluation (not yet run)

The companion `run_euroeval.py` creates **local** EuroEval `DatasetConfig` objects for
selected public language subsets. It uses the existing instruction-following task;
no upstream EuroEval registration or changes are needed. The Hub release is test-only,
so the config disables training and validation splits and explicitly enables test
split evaluation. EuroEval's default is *not* to evaluate the test split.

Before running: check available GPU memory, disk space for model weights and cache,
and the inference runtime. EuroEval's
[custom-dataset guide](https://euroeval.com/python-package#benchmarking-custom-datasets)
describes local configs. On this M5, the PyPI `euroeval[generative]` extra currently
tries to build an old CUDA-only vLLM and fails. Use a EuroEval source checkout with
its pinned macOS `vllm-metal` dependencies installed; **do not edit EuroEval**.
For example, from this repository, with an already-synced EuroEval checkout:

```bash
VLLM_METAL_MEMORY_FRACTION=0.18 uv run --project /path/to/EuroEval \
  --no-sync --python 3.12 paper/run_euroeval.py \
  --model Qwen/Qwen2.5-1.5B-Instruct
```

The `0.18` budget was necessary with the memory pressure on this particular laptop;
adjust it to available Metal memory, not total RAM. This full evaluation has not run.

Defaults: Danish and English, one iteration, zero-shot, no sample bootstrapping.
The local config maps `prompt` to EuroEval's input `text` column while retaining
instruction IDs and kwargs for scoring. It removes null padding from each kwargs
dictionary at retrieval time: the Hub's Parquet schema fills absent arguments with
nulls, whereas EuroEval's constraint checkers require only applicable arguments.
A full Danish dummy-model EuroEval run passed on 3 October 2026 (524 prompts,
EuroEval 18.1.0, 0% instruction accuracy as expected for meaningless responses).
Reproduce this integration check without model weights using:

```bash
uv run --no-project --python 3.12 --with euroeval \
  paper/run_euroeval.py --model dummy --language da
```

That checks dataset loading, preprocessing and scoring, **not** real model inference.
A separate one-example M5 smoke test also completed with EuroEval 18.2.0,
`Qwen/Qwen2.5-0.5B-Instruct`, and the Metal backend:

```bash
VLLM_METAL_MEMORY_FRACTION=0.18 uv run --project /path/to/EuroEval \
  --no-sync --python 3.12 paper/run_euroeval.py \
  --model Qwen/Qwen2.5-0.5B-Instruct --language da --max-examples 1
```

This returned 0% instruction accuracy on **one** prompt; that is a plumbing test,
not a reportable score. Without the reduced Metal budget, vLLM failed with GPU
out-of-memory while allocating its default KV cache. CUDA is **not** required.
The `--max-examples` option labels the dataset `-smoke` and caps generated tokens;
leave it out for real evaluations. Add `--language de --language fr` to cover more
European languages, and repeat `--model` for a second small non-reasoning model
(e.g. `Qwen/Qwen2.5-3B-Instruct`). EuroEval writes its results JSONL in the
current directory; generated results and model caches must not be committed
without review. These are examples, not completed measurements. Note
model IDs and revisions, inference settings, dataset revision and per-language sample
counts in the final paper. Check whether every translated constraint can be scored
reliably before reporting aggregate scores.

## Before submission

- Run the small evaluation and add **actual** scores, sample counts, scorer errors,
  and a few inspected failures to the paper. Otherwise remove result promises.
- Verify the released config inventory and per-language missing examples against a
  pinned Hub revision. State that 305 configs do not imply 305 validated translations.
- If using the manual Danish translation, document availability, alignment and
  validation protocol; otherwise omit the human-validation claim entirely.
- Replace the review manuscript's access-link note with an anonymous working
  resource link. The draft is not yet ready to submit without results and this link.
- Inspect the PDF for page limit, citation resolution, anonymity and layout. A TeX
  toolchain is not installed in this checkout, so PDF compilation is still pending.
- Check the current ACL style-file release before final submission. Only replace the
  bundled `acl.sty` if the NoDaLiDa organisers require a newer revision.
