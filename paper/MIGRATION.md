# Proposed `multilingual_agent_evals` consolidation

**Decision:** One NoDaLiDa 2027 paper about **MultiIFEval and MultiBFCL as two
separate datasets**; one code repository with `src/multi_ifeval/` and
`src/multi_bfcl/`. Draft the paper now. Do **not** move or rename repositories,
interrupt translations, change publishing destinations, or publish BFCL outputs
until the current MultiBFCL translation jobs have finished and the cutover has
been approved.

## Current boundaries

- The current code repositories are `syv-ai/multi_ifeval` and
  `syv-ai/multi_bfcl`, each with its own upstream Alexandra Institute remote.
  Both software repositories have MIT notices naming syv.ai and the Alexandra
  Institute; preserve those notices. The public MultiIFEval dataset remains at
  `danish-foundation-models/multi-ifeval` with its own CC BY-NC-SA 4.0 licence.
- MultiBFCL is still generating per-language `data/bfcl-*.jsonl` checkpoints
  outside Git. On 3 October 2026, generation-related Python processes were
  active and the ignored `data/` directory occupied approximately 578 MB.
  No migration should touch those files or their writers while active.
- MultiBFCL selects ten BFCL-v2 categories from files currently named
  `BFCL_v4_*` upstream: BFCL-v2 is a subset of the v4 distribution, not a
  different intended task. The upstream URL follows a moving `main` branch;
  pin its commit and subset inventory before any resumed translation,
  publication, or paper counts.
- MultiBFCL derives candidate languages from `alexandrainst/multi-wiki-qa`
  and intersects them with its own language definitions. Do not assume its
  complete translated language inventory equals MultiIFEval's 305 configs.
  Its current code translates selected messages, not tool descriptions; it
  does not include a model evaluation pipeline or published dataset card.

## Cutover gates

1. **Before touching either repository:** confirm writers have finished; record
   process state, the two clean and up-to-date `main` commit IDs, ignored file
   counts and checksums, and an independently stored, immutable backup of BFCL
   JSONL checkpoints. Freeze the BFCL source revision and compare each resumed
   checkpoint's example IDs and source-aligned fields against that revision;
   stop on mismatch instead of mixing source versions. Review upstream BFCL
   and MultiWikiQA terms for redistribution.
   Do not copy `.env`, API tokens, model caches, or generated data into Git.
2. **Choose a canonical public repository:** propose preserving the
   `multi_ifeval` history as the base and renaming it to
   `syv-ai/multilingual_agent_evals`, then importing MultiBFCL's Git history
   without rewriting either old history. This rename and the treatment of the
   old BFCL repository require an explicit cutover decision: retain it as a
   read-only pointer/archive if appropriate. Keep both old URLs usable via
   redirects or documentation; do not repoint Hugging Face IDs by default.
3. **Integrate code after the writer stops:** import BFCL under a temporary
   prefix with history preserved, then move its Python package to
   `src/multi_bfcl/`, rename colliding scripts/tests, and retain
   `src/multi_ifeval/` separately. Reconcile `pyproject.toml`, `uv.lock`,
   packaging, Python 3.12 tools, CI, docs, `AGENTS.md`, and ignored output
   paths. Preserve both translation commands and BFCL resume-by-ID semantics;
   make the source loader read the frozen BFCL revision before any resumption.
4. **Verify before switching production:** install from the locked environment;
   import and test both packages; run all offline tests, pre-commit, and CLI
   help checks without generation or network writes. Compare checkpoint hashes
   and perform one controlled BFCL resume from a disposable copy of the
   checkpoints against the frozen BFCL revision before retiring the original
   writer. Never append to the rollback backup. CI should check the direct-main workflow.
5. **Paper and release:** the draft can be written in parallel. Keep the two
   methods, dataset versions, quality limitations and metrics distinct. Add
   actual small-model results for each only after a working evaluator and
   checked translated samples exist. Document BFCL rights and publication
   status; arrange anonymous review access and check NoDaLiDa page limits.
   MultiIFEval's existing public Hub URL stays stable.

**Rollback:** do not delete or force-push either original repository. Keep the
original BFCL checkout and immutable checkpoint backup until the merged code
has passed CI and resumed a translation safely. On any mismatch, stop the new
writer and restore to a new working directory from the verified backup; keep
the backup unchanged.
