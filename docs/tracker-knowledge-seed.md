# Tracker Classic help knowledge seed

The production help stack runs on `nexusailive.com`: `digitz_ai_nexus` owns knowledge,
ingestion and retrieval; `digitz_ai_nexus_live` owns the public chat endpoint and
widget; experience, nexy and agentic provide the other Nexus surfaces. Prime's
App Documentation exporter originally supplied the committed multi-product JSON.
`hooks.after_migrate` calls `devtools.seed_digitz_docs_knowledge.run`.

## Replacement design

Refresh only entries whose app is exactly `DIGITZ Tracker`. Keep the eight original
source titles: these are Knowledge Source identities, so their bodies update in
place, disable obsolete chunks through the source controller, republish, and queue
reprocessing. Add functional chapters for Classic navigation, portal, mobile,
services, subscription and other current features. Other products, including
DIGITZ Service Tracker, remain byte-for-byte equivalent as parsed JSON entries.
No destructive cleanup or classification changes are needed.

The builder reads the current local Tracker Markdown, not legacy DocType labels.
It excludes architecture, port findings, API/reference material, historic destructive
migration instructions and demo tooling from public help. It strips relative Markdown
links (not served by Nexus), retaining their labels. Each source records the input
path, SHA-256 and documentation version. The source hashes identify working-tree
content too: a version banner alone does not prove a released snapshot.

Build from the nexus app repository:

```sh
python3 -m digitz_ai_nexus.devtools.build_tracker_docs_knowledge --tracker-root ../digitz_tracker
python3 -m unittest digitz_ai_nexus.tests.test_tracker_docs_knowledge
```

No new Frappe endpoint, dependency or hook is introduced. The production seed still
needs only its committed JSON; Tracker need not be installed on the Nexus server.
The existing source controller and ingestion processor own access and embedding
invalidation; the Public Docs policy and DIGITZ-TRACKER context stay unchanged.

## Verification and operations

Read-only production inspection on 10 November 2026 confirmed Nexus commit c8a5585,
a clean repository and the original eight Tracker seed titles. All eight database sources were
Published, embedding Completed, retrieval_ready=1, with one active chunk each.
This confirms the legacy help reached production; no replacement was deployed.

Deploy only through the repository PR/merge/pull process, then migrate
`nexusailive.com`. Verify all Tracker sources are Published, embedding Completed,
with active chunks and retrieval readiness, and try Classic navigation, renewal,
portal and company-role questions in the docs widget. A processing failure is logged
by the existing migration hook; rerun it to retry incomplete embeddings.

Rollback: restore the prior JSON through a reviewed commit and rerun the seed. Newly
added sources must be reviewed/retired explicitly if rolling back; removing a JSON
entry alone does not remove a live source. A future Prime full export overwrites this
JSON: rerun this builder after exporting until the upstream docs are refreshed too.

## Released input used for deployment

The initial draft included unreleased working-tree Multi-company guidance. Before
deployment, the seed was rebuilt from Tracker `origin/production` at `3fd96e3`,
documentation 5.29.0, isolated under `/tmp/tracker-help-release`. The unreleased
Multi-company chapter is excluded. There are 16 Tracker sections and 129
sections in total; all 113 other product sections are unchanged.

Run the exact-input test with `TRACKER_DOCS_ROOT=/path/to/pinned/tracker`.
The default test run does not assume an unrelated local checkout matches the pinned
production snapshot. Recorded source hashes identify the inputs shipped here.
