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

## Public cutover status (9 October 2026)

- Locked Python 3.12 tests (21 passed), pre-commit, both CLI help commands,
  `git diff --check`, and the source/wheel build passed. The wheel contains
  both packages. Only `data/.gitkeep`, not JSONL or secrets, entered Git.
- Published the combined `main` as commit `5be9fdc` without force, then
  renamed the repository to `syv-ai/multilingual_agent_evals`. Verified
  `origin/main` at the new URL points to that commit and the BFCL source SHA
  remains an ancestor. The Hugging Face dataset IDs did not change.
- Manual CI run `37917702180` passed code checks and pytest on Linux, macOS,
  and Windows. The old `syv-ai/multi_bfcl` repository was archived by the
  owner, not deleted; it remains a read-only historical pointer. The local
  checkout and Git bundle are retained. No CLI deletion permission was added.
- The paper also has a local public-Hub MultiBFCL EuroEval conversion script;
  a one-example Danish dummy-model run reached tool-calling scoring. This is
  only an integration smoke test, not a reportable model result.

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
