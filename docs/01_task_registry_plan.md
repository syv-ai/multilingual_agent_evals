# NoDaLiDa 2027 paper: task registry plan

**Target:** Submit an anonymous, eight-page regular resource paper by
**18 January 2027**. NoDaLiDa also allows a four-page short or demonstration
paper if the regular-paper evidence cannot be completed in time. See the
[call for papers](https://www.aclweb.org/portal/content/cfp-26th-nordic-conference-computational-linguistics-copenhagen-may-25-28-2027).

**Scope:** Present MultiIFEval (instruction following) and MultiBFCL (tool
calling) as **two distinct datasets** in one paper. Explain the engineering
that made the BFCL-v2 translation pipeline scalable to many languages. Run a
bounded, reproducible comparison of `gpt-6-luna` and at least one open model on
English and Danish. Do not imply that a model run on two languages validates
all 305 dataset configurations.

**Current state (9 October 2026):** The public code is at
[`syv-ai/multilingual_agent_evals`](https://github.com/syv-ai/multilingual_agent_evals).
The two Hub releases remain at
[`danish-foundation-models/multi-ifeval`](https://huggingface.co/datasets/danish-foundation-models/multi-ifeval)
and [`syvai/multi-bfcl`](https://huggingface.co/datasets/syvai/multi-bfcl).
The paper draft and local EuroEval runners are in `paper/`. Dummy and
one-example runs test integration only; there are no reportable model results.
The old BFCL GitHub repository is archived, not deleted.

## Decisions and boundaries

- **Common BFCL scoring:** Use EuroEval's tool-calling task for its English
  BFCL-v2 and translated MultiBFCL evaluations. Do not make replacing its
  scorer or changing EuroEval a prerequisite. Use the same metric and disclose
  any differences in sample IDs, splits, or categories; never label an
  unmatched comparison as paired.
- **Different tasks, different metrics:** Report MultiIFEval instruction
  accuracy and MultiBFCL tool-calling accuracy in separate tables. A EuroEval
  registration is not a model result.
- **Primary models:** Evaluate `gpt-6-luna` through the local OpenAI-compatible
  proxy at `127.0.0.1:18080` and
  [`mistralai/Ministral-3-8B-Instruct-2512`](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512).
  The Ministral 3 family is dense, not MoE, and Apache-2.0. Its 3B variant is
  a fallback if the 8B cannot be run; the 14B is an optional extension after
  the primary matrix is complete. Do not substitute or add models after
  viewing scores without labelling the result exploratory.
- **Modest matrix:** Start with a *proposed*, not yet frozen, maximum of 200
  matched English–Danish MultiIFEval IDs and 100 BFCL IDs per language,
  stratified over eligible BFCL categories. This is about 600 generations per
  model. Finalize the IDs, category/constraint balance, and compute budget
  after a small throughput pilot but **before** running the scored matrix.
  Report sample-based findings, not full-release performance.
- **No paid or disruptive work by default:** The translation CLIs spend API
  money and are not tests. Do not rerun translation, send large proxy batches,
  stop Sparkie services, or alter either Hub dataset without a separate
  decision and cost/resource check. Do not commit checkpoints, model caches,
  API secrets, or raw results containing sensitive material.

## Registry

`P0` tasks block a defensible submission. `P1` tasks strengthen it if the
primary work is complete. All tasks start **To do**; dependencies refer to
IDs in this table. An acceptance check is required before marking a task done.

| ID | Priority | Task and output | Depends on | Acceptance check |
| --- | --- | --- | --- | --- |
| R01 | P0 | Freeze provenance and revisions | — | Record both Hub SHAs, BFCL-v2 upstream commit, EuroEval commit/version, paper code commit, and licences; document the BFCL source/answer join and source rights. |
| R02 | P0 | Inventory both releases | R01 | Produce reproducible per-language row/ID and missingness counts; for BFCL also count each of the ten categories and source-to-release coverage. Distinguish 305 configurations from validated translations. |
| R03 | P0 | Document BFCL scaling design | R01–R02 | Explain category selection, typed source/answers, language discovery, context selection, instruction-only translation, preserved tool metadata, per-language checkpoints, bounded concurrency, retries, recovery, and structural validation. State what each mechanism does and does not guarantee. |
| R04 | P0 | Quantify pipeline scale without new translation | R02–R03 | Tabulate source/release counts, completion or missingness by category and selected languages, and failure/retry or throughput numbers **only where existing records substantiate them**. Do not invent a cost or speedup. |
| R05 | P0 | Audit translated examples | R02 | Have a bilingual reader review about 40 ID-matched IFEval English–Danish prompts across constraint types, and about 50 BFCL pairs (target: five per category). Save rubric, sampled IDs, semantic/argument error counts, and resolution of disputed examples. |
| R06 | P0 | Check scoring and alignment | R01–R02, R05 | Verify IFEval constraints and BFCL possible answers on audited IDs; confirm public English/Danish subsets and EuroEval's English BFCL-v2 anchor use comparable task settings. Record unmatched IDs/categories, scorer failures, and exclusions. Retain EuroEval's common BFCL scorer. |
| R07 | P0 | Make paper runners traceable | R01–R02, R06 | Pin model/data/runtime inputs; preserve source IDs and category/constraint labels in an output manifest; record prompts, responses, tokens, errors, and effective generation settings. For BFCL bootstrap draws, report unique IDs and repeats rather than calling draws full coverage. |
| R08 | P0 | Pilot Luna via proxy | R06–R07 | Verify the proxy advertises `gpt-6-luna`, check its exact routing and permitted publication of results, and run a **small** English/Danish × both-task pilot. BFCL's earlier `json_schema` incompatibility may require EuroEval reasoning-mode generation; verify it before scaling. Measure token use, failures, and projected cost; agree a spending ceiling. |
| R09 | P0 | Pilot Ministral 8B | R06–R07 | Pin the Hugging Face revision; load only one weight format; verify Mistral tokenizer/config/load settings, prompt length, JSON/tool-call output, peak memory, and throughput on a small two-task pilot. Do not disturb running Sparkie services. |
| R10 | P0 | Freeze evaluation protocol | R05–R09 | Publish the ordered ID lists, BFCL category and IFEval constraint coverage, exclusion rules, decoding/output limits, seeds, scoring versions, compute/cost ceiling, and stop criteria **before** main scores are inspected. |
| R11 | P0 | Run the two-model matrix | R10 | Complete the same frozen English/Danish task samples with Luna and Ministral 8B, or disclose an approved fallback. Save resumable outputs and a run manifest. Reconcile requested, generated, unique, failed, and scored counts. |
| R12 | P0 | Analyse scores and failures | R11 | Produce **separate** per-model/per-language IFEval and BFCL tables with denominators, uncertainty suitable for small paired samples, category/constraint coverage, and inspected error cases. Do not claim an MoE advantage or a general 305-language ranking. |
| R13 | P0 | Write the final paper | R03–R05, R12 | Replace all planned-result placeholders. Integrate BFCL scaling as a substantive method contribution, two dataset descriptions, reproducible experiments, audit findings, limitations, ethics, and checked citations within the page limit. |
| R14 | P0 | Resolve reviewer access and anonymity | R01, R13 | Check CFP/OpenReview rules for already-public identifiable releases; provide reviewer-usable access to specified revisions without renaming or republishing datasets. Remove identifying text, self-references, metadata, and inappropriate links from the anonymous PDF. |
| R15 | P0 | Validate and submit | R13–R14 | Build and visually inspect the ACL-style PDF; check eight-page regular limit (references and optional limitations/ethics excluded), bibliography, links, tables, anonymity, and reproducibility instructions. Submit by 18 January 2027. |
| R16 | P1 | Compare manual Danish IFEval translation | R02, R05 | Include only if access, ID alignment, assessor protocol, and a meaningful matched comparison can be documented; otherwise omit manual-versus-machine validation claims. |
| R17 | P1 | Add a 14B or 3B model | R11 | Add 14B only with measured spare memory/time and the same frozen samples; use 3B as a clearly named fallback if 8B is infeasible. Report each as its own model condition. |
| R18 | P1 | Extend language coverage | R12 | Add German/French only after language-specific audit and compute capacity; otherwise explain why English/Danish were selected and avoid broader generalizations. |

## Hardware and spending gates

- **M5 Pro laptop:** 48 GiB unified memory and approximately 91 GiB free disk
  at the last check. Use it for audits, manifests, scoring, and writing. The
  Ministral 3B can be investigated as a fallback, but Metal/runtime
  compatibility must be tested rather than assumed. Do not download duplicate
  weight formats unnecessarily.
- **Sparkie:** NVIDIA GB10, 121 GiB host/unified memory, approximately 24 GiB
  available at the last read-only check. Existing image and vLLM processes
  occupy substantial GPU memory. Ministral 8B's **single** FP8 weight format
  is approximately 9.7 GiB; 3B is approximately 4.35 GiB and 14B is
  approximately 14.65 GiB. Their Hub repositories also contain an equivalent
  second format, so summing all `safetensors` files double-counts weights.
  These are weight sizes, **not** peak inference memory. Inspect active jobs,
  memory, disk, context/KV requirements, and ports before any launch. Schedule
  a quiet window; do not stop other workloads implicitly.
- **Inference compatibility:** The Ministral model card documents vLLM's
  `--tokenizer_mode mistral --config_format mistral --load_format mistral`
  settings. Select a context limit from the longest actual prompt rather than
  taking the 262k default. First test whether EuroEval can use the local
  server with the intended response format and same scoring protocol.
- **Luna proxy:** List models and check routing without inference first. A
  paid pilot precedes a cost estimate and explicit spending cap for the full
  run. Record returned model identifier, date, decoding options, errors, and
  token usage; an opaque alias cannot be described as a frozen weight revision.
- **Pilot stop rule:** If the 8B cannot load with safe headroom, either wait
  for an agreed Sparkie window or explicitly switch to 3B. If Luna cost,
  response-format errors, or failure rates make the proposed sample untenable,
  revise and freeze a smaller protocol *before* examining main scores.

## Milestones and submission gate

1. **October 2026:** R01–R06. Lock the release inventory, method contribution,
   rights, and bilingual audits before making performance claims.
2. **November 2026:** R07–R10. Validate both model paths with small pilots,
   settle resource/cost limits, and freeze the shared protocol.
3. **December 2026:** R11–R13. Run the primary matrix, inspect errors, and
   replace paper placeholders with reproducible numbers and limitations.
4. **Early January 2027:** R14–R15. Secure anonymous access, compile and review
   the PDF, and submit ahead of the 18 January deadline. If P0 evidence is too
   thin for eight pages, decide early whether the four-page demo format is
   more defensible; do not compress away methods or limitations at the end.

**Done means:** A reviewer can identify exactly which of the two releases,
examples, models, prompts, runtimes, and scorers produced each number; can
understand what was translated versus preserved in MultiBFCL; and can access
an anonymous, compliant PDF and the specified datasets. Smoke tests, model
cards, and EuroEval registrations alone do not satisfy this gate.
