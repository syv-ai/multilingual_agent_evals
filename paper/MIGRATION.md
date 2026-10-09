# Combined repository cutover

**Decision:** One NoDaLiDa 2027 paper on **MultiIFEval and MultiBFCL as two
separate datasets**; one code repository, `syv-ai/multilingual_agent_evals`,
with `src/multi_ifeval/` and `src/multi_bfcl/`. Keep their Hugging Face dataset
IDs unchanged. The owner approved merging the paper branch into `main`,
renaming the IFEval code repository, and deleting the old BFCL code repository
only after the combined repository is verified.

## Completed locally (9 October 2026)

- Confirmed both source Git checkouts clean and their `main` branches at their
  respective origin tips. The earlier BFCL translation processes had stopped.
- Saved verified Git bundles of both repositories and a separate copy of 305
  ignored BFCL JSONL checkpoints, with a SHA-256 manifest, at
  `~/gitsky/_migration_backups/multilingual_agent_evals_2026-10-09/`.
  No `.env`, API credentials or model caches were copied into Git.
- Fast-forwarded the paper branch onto the IFEval checkout's `main`; imported
  MultiBFCL's Git history as a second parent and moved its package, CLI and
  tests into separate root paths. Kept the two original package import names.
- Reconciled a single Python 3.12 project and lockfile. The offline combined
  pytest suite passed (21 tests), as did pre-commit after the integration fixes.
  Copied the 305 ignored BFCL checkpoints from the backup into the combined
  checkout and verified the copy byte-for-byte with `rsync --checksum`.
- Verified the published datasets: `danish-foundation-models/multi-ifeval`
  (CC BY-NC-SA 4.0) and `syvai/multi-bfcl` (CC BY-NC 4.0), each advertising
  305 language configurations. EuroEval registers tool calling for 31
  translated BFCL languages plus English, but its derived mini repositories
  may be private. No model scores were created as part of this migration.

## Public cutover checklist

1. Re-run locked tests, pre-commit, both CLI help commands and `git diff --check`.
   Ensure neither secrets nor checkpoint JSONL files are staged. Verify both
   source Git SHAs are ancestors of the integration commit.
2. Push the tested combined `main` without force to the existing
   `syv-ai/multi_ifeval` remote. Confirm the remote commit and CI. Rename that
   repository to `syv-ai/multilingual_agent_evals`, update the local `origin`,
   and verify a fresh fetch and links at the new URL.
3. Verify the old BFCL history is reachable in the new repo and retain its
   local checkout and backup. Only then retire `syv-ai/multi_bfcl`. Git history
   can be recreated from the bundle, but deletion loses issues, stars, settings,
   and the old URL. Do not delete on a failed check.

## Independent data and paper work still required

- BFCL-v2 is intentionally the subset of files named `BFCL_v4_*` upstream.
  The loader follows a mutable `main` URL. Before resuming translation, pin
  the BFCL source commit and compare checkpointed IDs and source-aligned
  fields with it. On mismatch, stop rather than mixing revisions; test resume
  from a disposable checkpoint copy, never from the immutable backup.
- The public BFCL release has its own licence. Review the upstream BFCL and
  MultiWikiQA source terms, translation quality, per-language sample counts,
  and tool metadata left in English. Do not treat 305 configs as human
  validation or EuroEval registration as a model evaluation result.
- The paper needs separate real model results, an anonymous reviewer access
  route, a verified PDF/page count, and pinned dataset revisions. Neither
  dataset ID or publication destination should be silently redirected.

**Rollback:** retain the old BFCL checkout, both Git bundles and the immutable
checkpoint backup. If the new writer ever fails, restore to a *new* working
copy from the backup and check source alignment before resuming. Do not
force-push published `main`; use a revert if the integrated code must be undone.
