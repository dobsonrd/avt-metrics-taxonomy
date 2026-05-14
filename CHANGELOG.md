# Changelog

## v5.5.14 (2026-05-14)

**Patch release: Assurance Planner interactive site page. No metric content edits.**

- New **Assurance Planner** page (`/assurance-planner/`) — tier toggle buttons (Tier 1 / 2 / 3), responsible actor dropdown filtered to the 5 canonical groups from the How to Use section (Vendor, Deployer, Regional ICB, National Body, Academic), with Clinician and Caldicott Guardian mapped under Deployer. Metrics grouped by cadence sequence: Pre-deployment / Continuous / Periodic audit / Event-triggered. Each card shows ref-ID, tier, actor, and assurance question.
- New `taxonomy/javascripts/` source directory; `build_site.py` gains `_copy_javascripts()` mirroring the existing `_copy_stylesheets()` pattern.
- GitHub Actions workflow opts into Node.js 24 (`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`) and sets `dev` as default alias on main-branch deploys.

**Counts unchanged**: 236 metrics / 58-99-79 tiers.

## v5.5.13 (2026-05-11)

**Patch release: title renamed to "Prototype AVT Metrics Taxonomy" ahead of public launch. No metric content edits.**

- All reader-facing titles (site nav/browser tab via `mkdocs.yml`, markdown headings, citation block) now lead with "Prototype" to make the artefact's status immediately visible.

**Counts unchanged**: 236 metrics / 58-99-79 tiers.

## v5.5.12 (2026-05-09)

**Patch release: small home-page tier-block tweak. No metric content edits.**

- "Three priority tiers" block on the home page: Tier 2 line trimmed from "recommended for any AVT deployment" to "recommended for AVT deployment"; the three lines now render as separate paragraphs (blank line between each) rather than as a bulleted list.

**Counts unchanged**: 236 metrics / 58-99-79 tiers.

## v5.5.11 (2026-05-09)

**Patch release: reader-feedback wiring + Tier 1 quick-reference structural breaks. No metric content edits.**

Three reader-experience fixes surfaced after live testing:

1. **GitHub issue templates** — five issue-form templates at `.github/ISSUE_TEMPLATE/` so reporting a problem produces a structured submission rather than a blank issue: factual error / confabulation, tier disagreement, missing metric / gap, broken link / dead citation / site bug, framing / structural feedback. Each template captures the metadata reviewers actually need (ref-ID, what the catalogue says, what the source says, suggested fix). The factual-error template also asks the reader to tick a prototype-status acknowledgement so error reports are framed as "improving the artefact" rather than "this is broken policy."
2. **"Spotted an error?" footer on every group page** — each rendered group page now ends with a links block pointing directly at the five issue templates. Source side: a single `_FEEDBACK_FOOTER` string appended at build time via the new `_add_feedback_footer` pass; no per-metric edits needed. Closes the loop between the prototype-status framing and the actual one-click reporting flow.
3. **Prototype-status page** — replaced the bare `/issues` URL with a `/issues/new/choose` link plus a five-bullet list of what each template is for. Same wiring as the per-page footer; reduces friction for readers who land on the prototype-status page first.

Plus a Tier 1 Quick Reference structural break:

- **Per-actor tables now subdivide by cluster/group at build time** — new `regroup_tier1_tables_by_cluster` pass walks each per-actor table on the rendered Tier 1 quick reference, groups rows by their metric's `cluster · group`, and emits one mini-table per group under a bolded sub-header (e.g. *TP · ASR / Transcription* / *GV · Privacy & Data Governance*). Long actor blocks (Deployer has 43 entries) now scan in cluster-sized chunks instead of as one wall-of-rows. The source `_tier-1-quick-reference.md` is unchanged — the regrouping happens in `taxonomy/build_site.py` after `link_tier1_quickref` has injected the per-row ref-IDs.

And a small home-page rendering fix:

- **"Three priority tiers" block on the home page** — the three tier lines used soft line-breaks, which Markdown collapses to one paragraph. Converted to a proper bulleted list so each tier renders on its own line.

**Counts unchanged**: 236 metrics / 58-99-79 tiers.

## v5.5.10 (2026-05-09)

**Patch release: live-derived applicability counts on the contents page.**

The contents page's "Browse by applicability" tip block had hard-coded counts (48 AVT-Specific / 77 AVT-Contextualised / 89 General Healthcare AI) baked into `_inject_contents_applicability_row` in `taxonomy/build_site.py`. Those numbers were the v3.x baseline and had drifted with every metric mint since. Live counts at v5.5.x are 50 / 79 / 107 — the count surface elsewhere on the site (`_applicability.md` summary table, `crosscuts/by-applicability/*.md` page intros) was already correct, but this one inject-helper was stale.

**Fix:** reworked the inject-helper to parse the catalogue and derive counts from the live `Applicability` dimension at build time (countable metrics only — sub-parts excluded), matching the same derivation used elsewhere. The block can no longer drift.

**Counts unchanged**: 236 metrics / 58-99-79 tiers.

## v5.5.9 (2026-05-09)

**Patch release: reader-experience polish — no metric content edits.**

A focused tidy-up surfaced after an end-user readability pass: the home-page release-summary was a single ~4 KB paragraph; the Tier 1 Quick Reference duplicated v4.1/v5.3/v5.4 promotions in a separate trailing section; the Standards Mapping tables referenced metric names as plain prose; the Applicability by-cluster table was stale at the v3.x shape.

**What changed:**

- **Home page (`taxonomy/_header.md`)** — replaced the wall-of-text release summary with a structural-patterns block (Tier 1 tightening, citation grammar, per-metric dimensions, honest-prototype framing, test/audit safety net) plus a recent-highlights bullet list (v5.5.x → v4.0.0). Full per-release notes still in CHANGELOG.
- **Tier 1 Quick Reference (`taxonomy/_tier-1-quick-reference.md`)** — rewritten as per-actor markdown tables (Metric · Cadence · Why this tier). v4.1 / v5.3 / v5.4 promoted/minted entries merged into the main per-actor lists with `(new in vX.Y)` / `(promoted vX.Y)` markers; the standalone trailing additions section removed. Cadence icons (🚪 / 📡 / 🔄) explained once at the top.
- **Applicability by-cluster table (`taxonomy/_applicability.md`)** — refreshed from the v3.x baseline (221 total, Part-letter A–F naming, 0 GHA in TP) to v5.5.x state (236 total, TP/PI/HL/IO/GV/ES cluster codes, current per-cluster splits 75/21/19/18/94/9). Headline summary block was already current; only the by-cluster cut was stale.
- **Metric-name linkification in cross-cutting tables** — new `link_metric_names_in_tables` pass in `taxonomy/build_site.py` rewrites bare metric-name occurrences inside markdown table cells on cross-cutting pages (standards-mapping, applicability, responsible-AI lens, etc.) into links to the per-metric anchor. Skips cells that already contain a markdown link; longest-match precedence so "Demographic-Disaggregated WER" wins over "WER". Closes the gap between the "ref-IDs in cross-cutting prose linkify" v4.2.1 feature and the standards-mapping tables that use metric *names* not ref-IDs.
- **`plan-future.md` split** — completed items 3 / 4 / 5 / 7 / 8 (versioning conventions; Tier 1 minimum-set construction; snippet + Formal Definition verification; citation grammar `Short:` field; threshold-numbers structural split) lifted into `archive/plan-future-archive.md` as a historical record. Active backlog (1, 9, 10, 11, 12) stays at root. Original per-item numbering preserved across both files so cross-references in CHANGELOG / commits continue to resolve.

**Counts unchanged**: 236 metrics / 58-99-79 tiers.

## v5.5.8 (2026-05-08)

**Patch release: repo-wide documentation sweep — no metric content edits.**

A tidy-up pass aligning long-stale top-level documentation with the v5.5.x catalogue state. Surfaced after the v5.5.7 number-and-link sweep when several reader-facing docs were found to be five major releases out of date.

**What changed:**

- **`taxonomy/_contents.md`** — refreshed per-group metric counts (sum to 236) and added cross-cutting bullets for Families, Layers of Defence, Failure Pathways, AI-Substrate, Dimensions Overview. Framework count → 13. Gap count → 74 outstanding. Fixed `#epr-write-back` anchor → `#downstream-write-back`.
- **`CLAUDE.md`** — complete rewrite. Was describing the v2 migration as active work; now reflects v5.5.x state (236 metrics; 58/99/79; full v5.x cross-cutting page set; 13 dimensions; locked conventions including deprecate-don't-renumber, gap-allocation, within-cluster ordering, topic-cited NHSE IG, per-artefact licensing; release-wrap order).
- **`taxonomy/README.md`** — complete rewrite. Was stuck at v2.0; now documents 236-row × 21-column CSV, explicit `build.FILES` ordering (was claiming alphabetical), versioning section through v5.5.7.
- **`taxonomy/_glossary.md`** — added FTS, NHSE IG Guidance March 2026, AVT Self-Certified Supplier Registry to Standards section. Added Cluster, Layer of Defence, AI-Substrate, Failure Pathway, Outcomes Boundary, Calibration & Context principle, Maturity, Outcome Type, Tightening pattern, Provenance prelude entries to Taxonomy-specific section. Updated Cadence to multi-valued enum. Updated Reference ID with v3.7+ deprecate-don't-renumber. Metric family count 6 → 8.
- **`METHODOLOGY.md`** — refreshed closing-line counts (214 → 236; 11 → 13 standards; v3.1 → full v1→v5.x arc) plus a paragraph on primitives accumulated since the methodology was written (Family dimension, Layers of Defence, AI-Substrate, Failure Pathways, Threshold Reference structural split).
- **`pyproject.toml`** — added `license = { text = "CC-BY-4.0" }` field for catalogue-licensing visibility at the package-metadata level.
- **`archive/v4.6/README.md`** — new file documenting the directory's naming-vs-release distinction (work was named "v4.6" during planning; structural split actually shipped as v4.5.1 + v5.0.0; rationale previously buried in `archive/v5.0.3/v5.0.3-cadence-plan.md`).
- **`v5.3-pre-mint-triage.md`** — relocated to `archive/v5.4/` after lifting the two genuinely-live follow-ups (Gap-IG-A rubric piloting, GV.VT-10 WP-2 source verification) into `plan-future.md` as new item #12.
- **`CHANGELOG.md` split** — pre-v5.0 entries (v1.0 – v4.5.1) moved to `CHANGELOG-archive.md` (~1044 lines). The active CHANGELOG now covers v5.0+ only and ends with a pointer to the archive.

**Counts unchanged**: 236 metrics / 58-99-79 tiers. Catalogue size unchanged. The change is documentation-only.

## v5.5.7 (2026-05-08)

**Patch release: number + link sweep across the v5.x catalogue.**

Systematic sweep for misaligned numbers and broken links. Five real issues found and fixed; one false-positive class (assembled-output static link checks) confirmed harmless.

### Number alignment fixes

1. **Layer-of-defence distribution** — README and CHANGELOG cited 77 / 137 / 25 (Prevention / Detection / Limitation), which was the with-parents view. The countable view (parents excluded, consistent with the 236-metric headline) is **77 / 134 / 25**. Three parents (TP.SN-7, TP.SN-9, HL.HF-3, all Detection) account for the difference. Both views are now documented; countable view is the canonical headline.
2. **AI-substrate distribution** — same pattern. With-parents view was 127 / 64 / 30 / 9 / 9; countable view is **125 / 64 / 29 / 9 / 9**. Both views now documented; countable view is canonical.

### Broken link fixes

3. **`plan-future.md`** — three references to private `.claude/projects/.../memory/...` paths (leftovers from an early draft) replaced with public CHANGELOG cross-references.
4. **`CHANGELOG.md`** — three broken `archive/v3.6-duplication-review.md` and `archive/v3.3-tier1-classification.md` paths corrected to their actual locations under `archive/audits/`.

### New audit guard

5. **`check_readme_headline_counts`** added — verifies README's "X metrics across 20 groups" and "Tier N (X metrics)" claims against live count. WARN-level. Catches future drift on the most-cited claims automatically.

### Sweep results saved

The sweep tooling at `/tmp/full_sweep.py` (not committed) found 153 link-issue candidates across all repo Markdown files. After filtering known false-positive classes (the assembled `avt-metrics-taxonomy.md` output reuses path patterns from many source files; site-context filenames like `families.md` resolve via the linkifier at site time), only the four issues above remained.

mkdocs strict pass (the rendered links work fine — the static-source check was over-flagging). 99/99 pytest. Audit zero ERROR/WARN. No metric content edits.

## v5.5.6 (2026-05-08)

**Patch release: catalogue licence + README refresh.**

### Catalogue licensed under CC BY 4.0

The catalogue content (Markdown source under `taxonomy/`, the assembled `avt-metrics-taxonomy.md`, the rendered MkDocs site, and supporting documents at the repo root) is now licensed under **[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**. New `LICENSE` file at the repo root carries the full terms, suggested attribution recipe, and explicit scope notes for the per-artefact licence split:

- **Catalogue content** — CC BY 4.0 (this release).
- **Reference implementation library** at `pkg/avt_metrics_ref/` (on `reference-library-pilot` branch only) — MIT, separately.
- **Build / parse / audit / site-build Python tooling** at `taxonomy/build.py`, `taxonomy/parse.py`, `taxonomy/audit.py`, `taxonomy/build_site.py`, `taxonomy/tools/`, `taxonomy/tests/` — supplied to make the catalogue reproducible; treated as MIT for independent re-use.
- **Quoted framework material** (DTAC, NHSE IG, MHRA SaMD, Caldicott, NICE ESF, etc.) remains under each publisher's own licence; the catalogue cites under fair-dealing conventions.

CC BY 4.0 was chosen over alternatives because (a) it's the convention for documentation-as-knowledge-artefact (Wikipedia, OpenAPI spec, NHSE OGL-equivalent content); (b) attribution requirement keeps the prototype-status framing legally enforceable when the catalogue is cited; (c) no share-alike requirement, so vendor / deployer / regulator re-use isn't blocked; (d) compatible with academic and procurement citation.

### README refresh

The README on main was carrying counts from earlier in the v5.x line. Refreshed across:

- Headline counts: 236 metrics; 58 / 99 / 79 tier distribution; 69 / 64 / 4 / 99 maturity distribution.
- Tier 1 Quick Reference description: 45 → 58 metrics.
- Standards mapping: "twelve frameworks" → "thirteen" (since v3.8 added the AVT Self-Certified Supplier Registry).
- Roadmap candidate count: 89 → 74 outstanding (reflects v5.3.0 lift of promoted candidates to `_gaps.md §7` historical record).
- Pytest count: 88 → 99.
- Stale `taxonomy/part-f/` paths (pre-v4.0 naming scheme) → `taxonomy/es/`.
- Quick links section gains entries for the new v5.4 / v5.5 cross-cutting pages: Layers of Defence, Failure Pathways, AI Substrate, Dimensions Overview.
- New "Headline state at v5.5.6" section in *Status / version* summarising current state at a glance.
- New "v5.x highlights" section condensing the v5.0.0 → v5.5.6 release arc into one place.
- Reference implementation library cross-reference added to Quick links (with explicit note that it lives on a branch and isn't merged to main).
- Licence section: replaced "TBD" with the full CC BY 4.0 framing + per-artefact split.

### Build effects

- No metric content edits.
- No site-build changes.
- Audit and pytest unaffected.

## v5.5.5 (2026-05-08)

**Patch release: v5.x consistency sweep + closure of plan-future #4 and #5.**

### Plan-future #4 closure (Tier 1 minimum-set)

Plan-future #4 ("Full Tier 1 gap review and minimum-set construction (post-agreement)") closes. Substantively actioned through the v5.0.1 → v5.5.0 Phase 5 work — the FTS notice 069369-2025 provided the external trigger for "what counts as minimum viable", v5.1.4 framed the criteria, and v5.3.0 / v5.4.0 actioned the gap-fill. The catalogue moved 218 / 43 Tier 1 → 236 / 58 across that arc.

### Plan-future #5 reconfirmation

Plan-future #5 ("Verify code snippets and Formal Definitions against sources") was already marked complete in v4.5+ but v5.5.5 audits the verification chain end-to-end:

- v4.2 covered TP / IO.FE / ES.ME (92 metrics)
- v4.3 covered GV / HL / PI / IO.PX (131 metrics)
- v4.4 ran Pass B externally over the 138-metric ✓ set (137/138 verified clean, 1 fix on GV.SG-5)
- v5.5.2 verified the 23 code snippets + 15 v5.3/v5.4 Formal Definitions added since v4.4
- **v5.5.5 confirms no FD edits between v4.4 and v5.5.2 bypassed verification** — the v4.5 / v5.0 / v5.1 / v5.2 commits did not modify Formal Definitions (they ran citation-grammar polish, threshold-block structural split, cadence-dimension cleanup, and research-output additions respectively). Verification arc is end-to-end across all 236 metrics.

### Consistency sweep — issues found and fixed

A systematic sweep across the v5.x catalogue surfaced 8 real consistency issues:

1. **`_tier-1-quick-reference.md` missing 15 of 58 Tier 1 metrics.** Refreshed: section header counts corrected (Deployer 36 → 47, Vendor 20 → 33, Regional 2 → 5, National 1 → 5 — multi-actor responsibilities counted per-actor, totals exceed 58 by design); new "v4.1 / v5.3 / v5.4 additions to Tier 1" supplement section added with all missing metrics grouped by Responsible Actor.

2. **`_summary.md` Maturity counts drifted.** Established 62 → 69; Emerging 53 → 64; Vendor-Proprietary 4 (unchanged); Proposed/Novel 110 → 99. Drift accumulated from v5.3.0 / v5.4.0 promotions and pull-throughs that updated tier counts but not maturity counts.

3. **`_summary.md` Family count for Clinical Content Fidelity.** Changed 5 → "4 + 1 parent construct (TP.SN-7 Factual Verification)" — consistent with the parent-vs-countable distinction the build uses.

4. **`_summary.md` Unaffiliated count.** 196 → 197.

5. **`_outcomes-boundary.md` count.** "215 metrics" → "236 metrics".

6. **`_standards-mapping.md` count.** "215 metrics" → "236 metrics".

7. **TP.CC-7 / TP.CC-10 stale renaming suffixes.** "(NHS framing; was Coding Inflation Detection)" / "(NHS framing; was wRVU / Tariff Impact)" removed from the canonical metric headings — the v3.7 reframing context lives in body prose where it belongs.

8. **plan-future #4 stale counts.** Updated from v3.x-era 218 / 43 baseline to current 236 / 58.

### New audit check

`check_summary_maturity_counts` enforces that `_summary.md`'s declared Maturity bucket totals match the live countable-metric distribution. Catches future drift automatically. WARN-level (non-blocking).

### Build effects

- 87 site pages (unchanged from v5.5.4).
- Build clean. Audit zero ERROR/WARN. 99/99 pytest. mkdocs strict pass.
- No metric content edits; all changes are headline-text or audit-tooling.

## v5.5.4 (2026-05-08)

**Patch release: explicit `Layer` dimension extended from 33 → 236 metrics.**

v5.5.0 seeded explicit `Layer` (Prevention / Detection / Limitation) on 33 metrics from an early-draft slide-deck classification, leaving ~200 unclassified and falling back to a cadence-based heuristic that was wrong about a third of the time. v5.5.4 extends explicit classification to all 206 remaining metrics through a per-cluster pattern-based pass:

- **TP.AC (8)** — One-off gates → Prevention; Continuous monitoring → Detection
- **TP.ASR (12)** — Mostly Prevention (one-off corpus evaluation); Detection where continuous (CK-ER, RTF, OOV)
- **TP.DI (9)** — All Prevention (one-off pre-deployment gates)
- **TP.SN (22)** — Mostly Detection (in-service summarisation quality); Prevention for benchmarks (ROUGE, BERTScore, MedHELM)
- **TP.CC (11)** — All Detection (continuous coding quality monitoring)
- **TP.WB (4)** — Detection for conformance metrics; Limitation for rollback capability
- **PI.PP (9)** — Mostly Prevention (one-off gates); Detection where continuous
- **PI.E2E (12)** — Mostly Detection (post-deployment pipeline evaluation); Prevention for one-off cascade/reproducibility/recovery tests
- **HL.HF (17)** — All Detection (workflow signals)
- **IO.FE (8)** — All Detection except IO.FE-2 Accent Taxonomy (one-off Prevention gate)
- **IO.PX (9)** — All Detection (post-deployment outcome / patient-experience signals)
- **ES.ME (9)** — Mostly Detection; Prevention for ES.ME-2/-8/-9 (one-off gates)
- **GV.CR (14)** — Mostly Prevention (compliance gates); Detection for continuous compliance metrics; Limitation for board oversight + EU AI Act event logging
- **GV.SC (12)** — Mostly Prevention (one-off resistance tests) + Detection (continuous monitoring)
- **GV.SG (12 of remainder)** — Mostly Detection; Limitation for incident response (Time-to-Correct, SPI Escalation, Model Update Impact)
- **GV.PD (13)** — Mostly Prevention (compliance gates); Detection for continuous monitoring; Limitation for decommissioning
- **GV.OP (7)** — Mostly Detection (operational signals); Limitation for governance burden + historical output continuity
- **GV.VT (11)** — Mostly Limitation (vendor-side infrastructure for bounded response); Prevention for one-off procurement gates
- **GV.TC (4)** — Mix of Prevention (training gates), Detection (impact assessment), Limitation (CPD currency)
- **GV.EN (3)** — All Detection (operational sustainability monitoring)

### Distribution

After v5.5.4, all 236 countable metrics carry explicit `Layer`:

- **Prevention: 77 (33%)**
- **Detection: 134 (57%)**
- **Limitation: 25 (11%)**

Three parent-construct metrics (TP.SN-7, TP.SN-9, HL.HF-3) also carry a Layer (all Detection) for routing purposes — sub-parts inherit the parent classification. Counting parents would give 77 / 137 / 25; the countable view (parents excluded) is the canonical headline.

The 11% Limitation share is honestly thin — it surfaces the architectural gap that `_layers-of-defence.md` already names: limitation infrastructure (incident response, vendor disclosure, board oversight, rollback capability) is the layer most often under-instrumented in deployer plans.

### Build effects

- `_layers-of-defence.md` updated: removed two-stage classification framing; documents the unified per-metric explicit dimension. Cadence heuristic remains as a fallback in `parse.derive_layer_of_defence` for any future metric that lands without explicit `Layer` (catalogue currently has 0 such cases).
- `_layer_page` site builder simplified: no longer renders separate "Explicit" / "Heuristic" sections since all metrics are now explicit.
- Audit `check_layer_resolves` continues enforcing the enum.

Build clean. Audit zero ERROR/WARN. 99/99 pytest. mkdocs strict pass. No metric content edits beyond the new dimension row.

## v5.5.3 (2026-05-08)

**Patch release: AI-substrate Option 2 (derived classification at build time).**

Plan-future #10 promotes from documentation-only Option 3 (landed in v5.5.0) to derived-at-build-time Option 2.

### What changed

- `parse._AI_SUBSTRATE_GROUP_DEFAULTS` defines per-cluster defaults for the five-class cut (Pre-AI / AI-Substrate / Post-AI / AI-Mediated Workflow / AI-Agnostic Governance).
- `parse._AI_SUBSTRATE_OVERRIDES` carries 10 per-metric exceptions where the cluster default is wrong (training-data metrics → AI-Substrate; downstream IO.PX outcome metrics → AI-Substrate; system availability → Post-AI; some GV.SG metrics → AI-Agnostic Governance or AI-Mediated Workflow).
- `parse.derive_ai_substrate(m)` and `parse.group_metrics_by_ai_substrate(metrics)` provide the build-time derivation.
- `Metric.ai_substrate` property exposes the classification.
- New `by-ai-substrate/` cross-cut directory at `docs/crosscuts/by-ai-substrate/`, one page per class (5 pages).
- `ai_substrate` column added to CSV / JSON downloads.
- mkdocs.yml gains "By AI substrate" sub-nav under Catalogue views.

### Distribution

Across the 236 countable metrics:

- AI-Substrate — 125 (53%)
- AI-Agnostic Governance — 64 (27%)
- AI-Mediated Workflow — 29 (12%)
- Pre-AI — 9 (4%)
- Post-AI — 9 (4%)
- **Disputed — 0 (0%)** — well under the >20% promotion threshold from plan-future #10.

Counting parents (TP.SN-7 / TP.SN-9 / HL.HF-3, which inherit AI-Substrate / AI-Substrate / AI-Mediated Workflow respectively) gives the with-parents view 127 / 64 / 30 / 9 / 9; the countable view is the canonical headline.

### `_ai-substrate.md` updated

The page is no longer "documentation-only" framing; it now explains the build-time derivation, names the override list, and documents the promotion criteria that were met. Future structural promotion (Option 1: per-metric `AI Substrate` field on bodies) remains open if the cut becomes contractually load-bearing.

### Build effects

- 82 → 87 site pages.
- 40 → 45 crosscut pages.
- Build clean. Audit zero ERROR/WARN. 99/99 pytest. mkdocs strict pass.
- No metric content edits.

## v5.5.2 (2026-05-08)

**Patch release: code-snippet + Formal Definition verification + threshold-page regression fix.**

### Code-snippet verification (plan-future #5)

23 code snippets across 23 metrics enumerated and verified against current public APIs of their cited libraries:

- **jiwer** (TP.ASR-1, TP.ASR-4, TP.ASR-8) — `wer()`, `cer()`, `process_words()` all current
- **librosa** (TP.AC-1) — `librosa.load`, `librosa.feature.rms` current
- **pyannote.metrics** (TP.DI-1) — `DiarizationErrorRate(collar=0.25)` current
- **rouge_score** (TP.SN-1) — `RougeScorer` current
- **bert_score** (TP.SN-2) — `score()` returning P, R, F1 current
- **transformers** (TP.SN-5) — `microsoft/deberta-v3-large-mnli` model exists on HF
- **sentence-transformers** (PI.E2E-6) — `all-MiniLM-L6-v2` model exists
- **medcat** (TP.ASR-3, PI.PP-7) — `CAT.load_model_pack` API current
- **scipy.stats** (HL.HF-1) — `linregress` returns 5-tuple (slope, intercept, r, p, stderr); code unpacks correctly
- **Levenshtein** (TP.ASR-3) — `ratio` import current
- Pseudocode-flagged (TP.ASR-2, TP.SN-7b, PI.E2E-3, PI.E2E-4, PI.E2E-7) — explicitly named as illustrative

**One verification flag added:** GV.CR-3's claimed SNOMED concept ID `24771000000105` ("Audio Dictation") cannot be re-verified at a stable URL (parent NHSE IG hub doesn't expose stable section anchors). Limitations section gains a flag pointing deployers at the [SNOMED CT UK Edition browser](https://termbrowser.nhs.uk/) to verify before relying on it. Change history stanza added.

### Formal Definition verification

Sampled the 15 metrics added in v5.3.0 / v5.4.0:
- All 15 Formal Definitions are internally consistent rubrics, scenario walk-throughs, or formulae
- UK GDPR Article references (13/14, 18, 26) correct
- No fabricable claims embedded in the definitions

### Threshold-page regression fix (v5.3.0)

The v5.3.0 commit `0fcb19e` added GV.CR-13 / GV.VT-9 / GV.PD-13 threshold rows to `docs/thresholds.md` directly — but `docs/` is regenerated from `taxonomy/_thresholds.md` on every build, so those additions were silently overwritten on subsequent builds.

This release ports those entries into `taxonomy/_thresholds.md` so they survive build:
- **GV.CR-13** Refusal Impact-Explanation Quality — ≥4-of-5 rubric pass per refusal (rubric not nationally piloted)
- **GV.VT-9** PMSR/PSUR Currency — ≤10 working days PMSR; ≤12 months PSUR
- **GV.PD-13** Privacy Notice Currency — 12-month version-dating; 5-of-5 content elements

No metric content edits beyond the GV.CR-3 verification flag and Change history. Counts unchanged at 236.

Build clean. Audit zero ERROR/WARN. 99/99 pytest. mkdocs strict pass.

## v5.5.1 (2026-05-08)

**Patch release: Failure Pathways page.**

New cross-cutting page `_failure-pathways.md` (rendered as `failure-pathways.md` in Principles & Frameworks nav). Sourced from prior slide-deck work and provides **scenario framing** to complement the architectural framing in `_layers-of-defence.md` and the construct framing in `_families.md`.

Two complementary views on one page:

### Three failure pathways (archetypes)

Three parallel failure shapes traced step by step through the pipeline. Each pathway names the pipeline stages traversed and the Tier 1 metrics that are the catches at each stage:

- **Pathway I — The hallucination cascade.** ASR fabrication → patient safety incident. ASR → Summarisation → Human Review → EPR → Detection → Escalation. Concrete instance: a Whisper-style hallucination from a 4-second silence becomes a drug prescribed on a symptom the patient never reported.
- **Pathway II — The silent write-back failure.** Content correct, field wrong → interaction warning bypass. ASR → Summarisation → Write-back → EPR → Prescribing. Concrete instance: an allergy correctly transcribed but routed to the free-text field instead of the structured allergy list.
- **Pathway III — The undisclosed model update.** Silent vendor change → population accuracy drift. Vendor → Telemetry → Workflow → Audit → Governance Action. Concrete instance: a vendor deploys a new model without notification; accuracy drops 14% on EAL patients.

The framing carries the load-bearing claim: **no single metric covers a whole pathway. The taxonomy is a net, not a filter.**

### One worked timeline (taxonomy in motion)

Pathway III traced day by day from silent change to bounded response, showing the closed-loop escalation in concrete time terms:

- **Day 0** Silent update (GV.VT-1 Notification breached)
- **Day 1** Version detected (GV.SG-1 Model Version Tracking)
- **Day 3–7** Edit rate climbs (HL.HF-1 Edit Rate)
- **Day 14** SPI breach (GV.SG-9 DSCMS thresholds)
- **Day 16** Audit confirms (TP.SN-5 Hallucination Rate)
- **Day 17** Pause & file (GV.SG-11 LFPSE Reporting)

Five of the six catches in this timeline are Limitation-layer — the timeline demonstrates what a *fully wired* Limitation layer looks like in practice, complementing the architectural-gap finding in `_layers-of-defence.md` that Limitation is the thinnest layer when not actively wired.

The page also enumerates "what's not in this timeline" honestly — patient harm, inter-deployer correlation, non-AI failure modes — so the worked example doesn't overclaim coverage.

### How to use

The page closes with a four-step "how to use" stub for deployers reviewing their own assurance plans:
1. Walk a pathway end-to-end against your own deployment.
2. Test the closed loop (would Day 0 reach Day 17 in your setup?).
3. Stratify before aggregating (demographic-disaggregated detection is faster).
4. The metrics are the catches; the wiring is the work.

### Build effects

- 81 → 82 site pages.
- Build clean. Audit zero ERROR/WARN. 99/99 pytest. mkdocs strict pass.

No metric content edits.

## v5.5.0 (2026-05-08)

**Minor release: NHSE IG section refs cleanup, AI-substrate framing, family-page consolidation, by-family + by-layer-of-defence cross-cuts, and explicit `Layer` dimension on 33 metrics.**

Five workstreams.

### 1) NHSE IG section refs cleanup

Six v5.3.0/v5.4.0 metrics carrying `(section ref to be added on next pass)` markers in their Source rows tightened to **topic-cited convention**. The parent NHSE IG guidance hub does not currently expose a stable per-section URL anchor (already noted in the catalogue entry itself), so rather than fabricate section numbers I can't verify, the convention shifts to topic-cited references — naming the substantive obligation the metric tests rather than guessing a section number.

Metrics touched:
- **GV.CR-13** Refusal Impact-Explanation Quality → topic: transparency / dissent-handling
- **GV.PD-13** Privacy Notice Currency & Completeness → topic: privacy notice / AVT-processing transparency
- **GV.PD-14** SAR Deletion-Pause Interaction → topic: data subject rights / SAR-handling
- **GV.PD-15** Right-to-Restrict Tooling Support → topic: data subject rights / restriction tooling
- **GV.PD-18** Information Asset Register Completeness → topic: information asset register / IAO-naming (drops the unverified "section 8" placeholder from v5.4.0)
- **GV.VT-11** Joint-Controller Status Assessment → topic: controller-status determination (drops the unverified "section 5" placeholder)

Body-prose duplicates of the deferred markers also removed; each affected metric gains a v5.5.0 Change history stanza.

### 2) AI-substrate classification (documentation-only)

New cross-cutting page **`_ai-substrate.md`** (rendered as `ai-substrate.md` in Principles & Frameworks nav). Names the five-class derived cut answering "which metrics test the AI itself, vs the infrastructure around the AI, vs the governance of the AI?":

- **Pre-AI** — microphone hardware, signal capture
- **AI-Substrate** — the model itself (hallucination, calibration, drift)
- **Post-AI** — write-back, EPR integration, downstream consumption
- **AI-Mediated Workflow** — clinician edits, automation bias, time-to-sign
- **AI-Agnostic Governance** — DPIA, board oversight, sub-processor disclosure

Documentation-only Option 3 chosen (per plan-future #10): the cut is real but fuzzy at the edges. Page covers derivation rules from Pipeline Layer + Cluster + Responsible Actors, worked examples covering each class, and four reader-archetype views. Plan-future #10 status note added; structural Option 2 upgrade remains queued.

### 3) Inline family framings lifted to `_families.md`

Three inline family framings in cluster files migrated to `_families.md` as canonical home:

- Demographic Equity Disaggregation framing in `tp/asr-transcription.md` → one-line italic pointer.
- Clinical Content Fidelity framing in `tp/summarisation-nlp.md` → one-line pointer; substantive content (CREOLA citation, Asgari subtype mapping, faithfulness-vs-factuality framing) lifted into `_families.md` where the family already had a compact section.
- Medication Safety Thread framing in `tp/summarisation-nlp.md` → one-line pointer.

Per-metric `*See also: ... family*` italics on individual metric bodies left in place — those work as cross-references back to the family page from each member.

### 4) Site-side cross-cut pages for Family + Layer of Defence

Two new auto-generated cross-cut surfaces under `docs/crosscuts/`:

- **`by-family/`** — one page per declared family in `EXPECTED_FAMILIES`. 8 pages: clinical-content-fidelity, reference-based-text-similarity, clinical-transcription-accuracy, post-generation-correction, medication-safety-thread, demographic-equity-disaggregation, nhse-ig-attestation, prsb-semantic-completeness-write-back-fidelity.
- **`by-layer-of-defence/`** — three pages (Prevention / Detection / Limitation). Each page renders two cohorts: explicit (per-metric `Layer` field) and heuristic (cadence-derived) — the distinction is visible on the page so readers know what's authoritative.

`parse.py` gains `group_metrics_by_family()`, `derive_layer_of_defence(m)` (heuristic with explicit-Layer override), and `group_metrics_by_layer_of_defence()`. `build_site.py` gains `_family_page()` and `_layer_page()` helpers.

mkdocs.yml gains nav entries for the 8 family pages and 3 layer pages under "Catalogue views".

Site grows **70 → 81 pages**; 29 → 40 crosscut pages.

### 5) `Layer` as an optional per-metric dimension

`Layer` (Prevention / Detection / Limitation) is now an **optional** per-metric dimension. Seeded in v5.5.0 with **33 metrics** classified from an early-draft slide-deck "minimum viable assurance" presentation:

- **Prevention (11)**: TP.AC-5, TP.ASR-12, TP.ASR-13, TP.WB-1, TP.WB-3, TP.WB-4, GV.PD-9, GV.PD-10, GV.PD-11, GV.TC-1, GV.SG-17
- **Detection (14)**: HL.HF-1, HL.HF-3a, HL.HF-3b, TP.SN-5, TP.SN-6, TP.SN-15, TP.SN-20, TP.WB-2, GV.OP-5, IO.PX-1, GV.SG-14, GV.OP-6, GV.PD-1, GV.PD-8
- **Limitation (8)**: GV.SG-9, GV.SG-1, GV.VT-1, GV.SG-11, GV.SG-13, GV.OP-1, GV.VT-5, GV.VT-7

Reconciliation against the cadence-only heuristic showed **63% agreement**: the heuristic conflates always-on limitation infrastructure (LFPSE incident reporting, sub-processor transparency) with detection (8 cases), and miscategorises pre-deployment gates with continuous nominal cadence as detection (3 cases). The explicit field is authoritative where present.

`parse.Metric.layer` property; `EXPECTED_LAYERS` enum + `check_layer_resolves` audit check; `layer` column added to CSV/JSON.

`_dimensions-overview.md` updated: 12 → 13 fields; new Layer section; Cadence "what it's NOT" tightened to acknowledge the heuristic-vs-explicit split. `_layers-of-defence.md` updated: section heading shifted from "How the layers map onto existing dimensions" to "How metrics are classified into layers" with honest two-tier-classification disclaimer.

Future work: extend explicit `Layer` classification to the remaining ~200 metrics. Queued for v5.5.x or v5.6.x; see plan-future when promoted.

### Counts

- Metrics: unchanged at **236**
- Tier counts: unchanged at **58 / 99 / 79**
- Maturity: unchanged at 62 / 53 / 4 / 110

### Reviewer artefact still at repo root

`v5.3-pre-mint-triage.md` remains at root — the rubric-piloting follow-up for GV.CR-13 and the WP-2 re-source for GV.VT-10 are still load-bearing for future minor releases.

## v5.4.1 (2026-05-08)

**Patch release: housekeeping.**

No metric / catalogue content changes. Two changes:

1. `_versioning.md` gains a "Within-cluster metric ordering (v5.4.0 convention)" section explicitly documenting the ascending-numeric ref-ID convention applied in v5.4.0 (audit-enforced via `check_within_cluster_order`). Notes compatibility with retired IDs, sub-cluster intros, and named-family framings.

2. Two completed working files moved from repo root to `archive/v5.4/`:
   - `v5.2-registry-action-list.md` — its mint section C actioned in v5.4.0
   - `v5.3-merge-and-family-sweep.md` — its 2 merge candidates + 2 family mints all actioned in v5.4.0

`v5.3-pre-mint-triage.md` stays at repo root because its Outstanding follow-ups (NHSE IG section refs, Gap-IG-A rubric pilot, MHRA WP-2 re-source) are still load-bearing for v5.5+.

## v5.4.0 (2026-05-08)

**Minor release: merges, families, layers-of-defence, dimensions-overview + 2 NHSE IG mints.**

Five workstreams landed together — the v5.3.0 merge & family sweep (held for reviewer sign-off) executes here, plus the 2 NHSE IG mints flagged in `v5.2-registry-action-list.md §C`, plus two new first-class cross-cutting pages.

### 1) Parent + sub-part formalisations (2 pairs)

- **PCCP pair:** **GV.CR-9** (parent — substantive quality of acceptance criteria) + **GV.SG-18** (sub-part — structural completeness of the documented PCCP). Cross-cluster placement preserved (CR for compliance-attestation; SG for safety-governance) per the assurance-question split. Both bodies updated with explicit parent + sub-part language and Change history stanzas.
- **DPIA pair:** **GV.CR-7** (parent — structural completion of NHSE March 2026 DPIA template) + **GV.PD-17** (sub-part — substantive Caldicott Principle 1 review). Same cross-cluster pattern.

### 2) Named Metric Families consolidated

Named-metric family framings consolidated to a new top-level `_families.md` page (rendered as `families.md` on the site, in the Principles & Frameworks nav). Eight families:

- 6 existing: Clinical Content Fidelity (5 members), Reference-Based Text Similarity (2), Clinical Transcription Accuracy (3), Post-Generation Correction (4), Medication Safety Thread (4 — cross-cutting), Demographic Equity Disaggregation (7 — cross-cutting)
- **2 new in v5.4.0:**
  - **NHSE IG Attestation** (11 members; cross-cutting GV.CR + GV.PD) — documentation and operational verification that AVT deployments comply with NHSE IG March 2026 Guidance. Members: GV.CR-1, GV.CR-2, GV.CR-3, GV.CR-7, GV.CR-13, GV.PD-8, GV.PD-9, GV.PD-13, GV.PD-14, GV.PD-15, GV.PD-18 (the new mint).
  - **PRSB Semantic Completeness & Write-back Fidelity** (4 members; Downstream Write-back) — end-to-end write-back assurance from output capture through structural FHIR validation to clinical mandatory-element completeness. Members: TP.WB-1, TP.WB-3, TP.WB-6, TP.WB-8.

Family field added to dimensions table on all 51 family-member metrics, audit-enforced via new `check_family_resolves` check + `EXPECTED_FAMILIES` enum. `parse.Metric.family` property; CSV/JSON gain `family` column.

Existing inline family framings in cluster files left in place for v5.4.0 (the inline `*See also: ... family*` italics on per-metric bodies still work as before); a v5.4.1 cleanup can lift them into `_families.md` later if useful. The `_families.md` page is the canonical home; cluster-file inlines are now informally redundant.

### 3) Layers of Defence first-class principle

New `_layers-of-defence.md` page (rendered as `layers-of-defence.md` in Principles & Frameworks nav). Names the **prevention / detection / limitation** framing from prior slide-deck work — *no layer is sufficient alone*. Maps onto existing dimensions (Cadence + Lifecycle Phase + Cluster correlate but don't equal layer-of-defence — it's a derived cut). Three worked examples (hallucination — chain complete; bias drift — limitation thin; medication error — fully instrumented) showing how the three layers compose for each failure mode. Surfaces actionable architectural gaps where coverage is uneven across layers.

### 4) Dimensions overview reader-orientation page

New `_dimensions-overview.md` (rendered as `dimensions-overview.md`, top-level nav next to How-to-use). Disambiguates the 12 structural cuts the taxonomy makes — Tier vs Layer of Defence, Family vs Cluster, Cadence vs Lifecycle Phase, Maturity vs Tier, etc. Per-dimension detail with "what it's NOT" pattern for the most-commonly-conflated cuts. Comparison table at the top giving the 12 cuts at a glance.

### 5) Two new NHSE IG mints

- **GV.PD-18** 🟢 **Information Asset Register Completeness** — NHSE IG section 8 IAR registration with named owner, lawful basis, retention period, sub-processor list, risk classification. Tier 1 because the IAR is the structural index that ties the rest of the IG-attestation surface together.
- **GV.VT-11** 🟡 **Joint-Controller Status Assessment** — UK GDPR Article 26 binary determination distinct from sub-processor disclosure (GV.VT-7). Tier 2 because most NHS deployments will land at vendor-as-processor, but the determination must be made and documented, not assumed.

Both join the NHSE IG Attestation family.

### 6) Within-cluster numerical sort

`gv/privacy-data-governance.md` and `gv/vendor-transparency-contractual.md` re-sorted by ref-ID (was chronological-append since v3.x). New audit check `check_within_cluster_order` enforces ascending numeric ref-ID order within each cluster file. Other cluster files were already in order.

### Counts

- Metrics: **234 → 236** (+2 net)
- Tier 1: **57 → 58** (+1; GV.PD-18)
- Tier 2: **98 → 99** (+1; GV.VT-11)
- Tier 3: unchanged at 79
- Maturity: Established 60 → 62; others unchanged
- Applicability: General Healthcare AI 105 → 107
- Outstanding gaps: unchanged at 74; promoted-historical-record §7 grows from 15 → 17

### Reconcile

- `_gaps.md` §7g new section recording the 2 v5.4.0 mints; preamble + roll-up updated to 17 promoted across all releases
- `_summary.md`, `_applicability.md`, `_header.md` count refreshes
- `audit.py`: `EXPECTED_TIER_TOTALS`, `EXPECTED_APPLICABILITY`, `EXPECTED_TOTAL` updated; `EXPECTED_FAMILIES` enum added; new `check_family_resolves` and `check_within_cluster_order` checks
- `test_audit.py`: `TestCheckTierTotals.test_pass` shape updated to 58/99/79
- `parse.Metric.family` property; `build.py` CSV/JSON `family` column; site nav additions for Families / Layers of Defence / Dimensions overview

### Reviewer artefacts at repo root

- `v5.3-pre-mint-triage.md` — kept (Outstanding follow-ups still load-bearing)
- `v5.3-merge-and-family-sweep.md` — its 2 merge candidates and 2 family mints have all been actioned; can be archived in v5.4.1 housekeeping
- `v5.2-registry-action-list.md` — its mint section C now actioned; can be archived in v5.4.1 housekeeping

### Plan-future updates

- Plan-future #10 (AI-substrate classification) — still open for v5.5+; complementary to but distinct from Layers of Defence
- New plan-future candidate: cluster-file-internal ordering convention review — chronological append was not intentional but ref-ID sort breaks v3.x batch grouping logic; documentation needed

## v5.3.0 (2026-05-07)

**Minor release: Phase 5 lands — promotions + pull-throughs against the FTS-direct surface.**

The largest content-change release since the early v2.x consolidation. Reviewer-gated through three commits on the `v5-3-phase-5-promotions-and-pull-throughs` branch: promotions first, triage before bodies land, then bodies + reconcile + threshold-page additions.

### 7 promotions Tier 2 → Tier 1

Against the FTS notice 069369-2025 surface and its transitively-named frameworks (DTAC, MHRA Class I, "the guidance issued by NHS England"):

- **GV.VT-2** Telemetry Provision Completeness — FTS Performance & Monitoring Response substrate
- **GV.VT-13** Evidence Pack Freshness — FTS "all collateral must be kept up to date"
- **GV.VT-14** Indicative Pricing Transparency — FTS Step 1.a direct submission
- **ES.ME-8** Outcome Evidence Commitment Status — FTS Step 1.f
- **IO.FE-1** Deployment Equity Index — NHSE IG + CIO/CCIO equity guidance (transitive)
- **TP.ASR-4** Demographic-Disaggregated WER — MHRA GMLP-3 + Performance & Monitoring "boundaries and bias"
- **GV.SG-3** Performance Degradation Detection Latency — MHRA post-market surveillance (FTS Step 1.i)

Cybersecurity cluster (GV.SC-1 / -2 / -6) deliberately held at Tier 2 pending industry-standard adversarial-testing maturity — MHRA WP5 names cybersecurity as gate-level but AVT-specific adversarial-prompt-injection testing isn't yet industry-standard, and the FTS notice is silent on cybersecurity testing cadence specifically. Defensible to revisit when industry capability matures.

### 13 new pull-through metrics from `_gaps.md`

**MHRA-driven (`_gaps.md §2a`, all 5 promoted):**
- **GV.CR-11** 🟢 Medical Device Classification Documentation
- **GV.SG-18** 🟡 PCCP Documentation Completeness
- **GV.VT-9** 🟡 Post-Market Surveillance Report Currency
- **GV.VT-10** 🟡 MHRA Transparency Content Completeness *(Maturity: Proposed/Novel — pending MHRA Roadmap WP-2 final outputs)*
- **GV.PD-12** 🟡 Training Data Representativeness Documentation

**CQC well-led (`_gaps.md §2d`, 1 of 4 promoted):**
- **GV.CR-12** 🟢 Board-Level AI Governance Mechanism

**NHSE IG-driven (`_gaps.md §1c`, all 4 promoted):**
- **GV.CR-13** 🟡 Refusal Impact-Explanation Quality *(Maturity: Proposed/Novel — placeholder rubric pending national pilot)*
- **GV.PD-13** 🟢 Privacy Notice Currency & Completeness
- **GV.PD-14** 🟡 SAR Deletion-Pause Interaction
- **GV.PD-15** 🟡 Right-to-Restrict Tooling Support

**Caldicott (`_gaps.md §2g`, 2 of 3 promoted):**
- **GV.CR-14** 🟢 Consultation-Type Appropriateness Assessment
- **GV.PD-17** 🟡 DPIA Justification Quality

**PRSB (`_gaps.md §2f`, 1 of 4 promoted):**
- **TP.WB-8** 🟢 PRSB Semantic Completeness — cross-framework heavyweight (DTAC C4 + FHIR UK Core + CQC Reg 17 + PRSB)

### FHIR UK Core deferred from v5.3.0

`TP.WB-8 Per-Resource UK Core Conformance`, `TP.WB-9 UK Core Extension Conformance`, and `TP.WB-10 STU Version Targeting Declaration` were originally in v5.3.0 scope but held back by reviewer pending UK Core STU landscape stabilisation. Entries remain in `_gaps.md §2c` with annotations pointing to the pickup-ready outline at `reference-docs/v5.3-deferred-fhir-uk-core.md` (gitignored — same convention as `v5.2-fts/`). The slot freed by FHIR hold-back was claimed by PRSB Semantic Completeness, which moved from proposed `TP.WB-11` → `TP.WB-8`.

### Slot reallocations recorded in `_gaps.md`

- Gap-IG-A → **GV.CR-13** (slot was originally proposed for "CSO AI Oversight Capacity"; that metric remains deferred and the slot will be reallocated when picked up)
- Gap-IG-B → **GV.PD-13** (was originally proposed for Caldicott DPIA Justification Quality, which moved to GV.PD-17)
- Gap-IG-C → **GV.PD-14** (was originally proposed for Per-Data-Item Necessity Documentation, which remains deferred at Tier 3)
- Gap-IG-D → **GV.PD-15** (was originally proposed for NHS T.E.S.T. Training Data Anonymisation Provenance, which remains deferred)

### Counts

- Metrics: **221 → 234** (+13 net)
- Tier 1: **45 → 57** (+12 net Tier 1, of which 7 are promotions and 5 are new at Tier 1)
- Tier 2: **97 → 98** (+1 net — new T2 metrics in, promotions out)
- Tier 3: unchanged at 79
- Maturity: Established 54 → 60; Emerging 48 → 53; Vendor-Proprietary unchanged at 4; Proposed/Novel 108 → 110
- Applicability: General Healthcare AI 92 → 105 (all 13 new metrics)

### Reconcile

- `_gaps.md` rows for the 13 promoted metrics annotated with v5.3.0-status column; FHIR UK Core §2c annotated as deferred
- `_standards-mapping.md` per-framework references updated for MHRA, CQC, PRSB, Caldicott — gaps lists crossed-through for resolved items
- `docs/thresholds.md` gains rows for the 3 new metrics with quantitative thresholds (GV.CR-13 rubric, GV.VT-9 PMSR/PSUR cadence, GV.PD-13 currency)
- `audit.py`: `EXPECTED_TIER_TOTALS`, `EXPECTED_APPLICABILITY`, `EXPECTED_TOTAL` updated; `test_audit.py` shape updated
- `_summary.md`, `_applicability.md` aggregate counts updated

### Outstanding follow-ups (carried forward from triage)

- **Gap-IG-A rubric piloting** — placeholder rubric should be replaced with a piloted national rubric in a future minor; metric Maturity then moves Proposed/Novel → Emerging
- **NHSE IG section refs** for the four IG-derived metrics (GV.CR-13, GV.PD-13/-14/-15) — body prose currently says "section ref to be added on next pass"
- **MHRA Roadmap WP-2 transparency outputs** — GV.VT-10 to be re-sourced once WP-2 outputs are published in final form
- **FHIR UK Core pickup** — three deferred metrics, outline at `reference-docs/v5.3-deferred-fhir-uk-core.md`

### Reviewer artefacts at repo root (deferred archive until the work they support closes)

- `v5.3-pre-mint-triage.md` — Pass A/B verdicts on the 16 pull-through candidates; reviewer decisions recorded inline
- `v5.3-merge-and-family-sweep.md` — research-only sweep flagging 2 parent + sub-part merge candidates (GV.SG-18 / GV.CR-9 PCCP pair; GV.PD-17 / GV.CR-7 DPIA pair) and 2 emergent named-metric families (NHSE IG Attestation; PRSB Semantic Completeness & Write-back Fidelity). Reviewer to sign off before any merges or family framings land — deferred to v5.3.1 or v5.4.0
- `v5.2-registry-action-list.md` — already shipped in v5.1.4; remains until v5.4.0 wraps the action list

### Plan-future updates

- v5.4.0 will mint the 2 new attestation metrics flagged in v5.1.4 (Information Asset Register Completeness, Joint-Controller Status Assessment) at the next available slots — GV.PD-17 was originally reserved but is now taken by Caldicott DPIA Justification Quality, so Information Asset Register will land at GV.PD-18.

## v5.1.4 (2026-05-06)

**Patch release: v5.2.0-prep Registry-driven action list (Phase 5 reviewable triage).**

No metric / catalogue content changes. One research-output file at repo root: `v5.2-registry-action-list.md`.

The user provided the full text of the FTS notice 069369-2025 (NHS England's AVT Self-Certified Supplier Registry tender) — preserved verbatim in `reference-docs/v5.2-fts/find-tender-069369-2025-notice.md` (gitignored). The FTS notice is the public ceiling on what the Registry actually requires; the granular Atamis application pack remains inaccessible without supplier credentials.

**Frameworks the FTS notice explicitly names**: DTAC + everything DTAC transitively names (DSPT, Cyber Essentials, FHIR R4, WCAG, AIS, NHS Number / PDS, ICO registration, DCB0129); MHRA Class 1 medical device + post-market surveillance; "the guidance issued by NHS England" (NHSE IG Guidance March 2026 transitively).

**Frameworks audited in Phase 1b but NOT Registry-direct**: NHS LLM Framework, NICE ESF, NHS T.E.S.T., PSIRF, PRSB. These map to the Registry-deferrable tier.

**Action list compiled in `v5.2-registry-action-list.md`**:

- **10 promotions** Tier 2 → Tier 1 (GV.VT-2/-13/-14, ES.ME-8, IO.FE-1, TP.ASR-4, GV.SG-3, GV.SC-1/-2/-6) — each with FTS-direct rationale
- **16 pull-throughs** from `_gaps.md` (5 §2a MHRA + 3 §2c FHIR UK Core + 4 §1c NHSE IG + 1 §2d CQC + 2 §2g Caldicott + 1 §2f PRSB borderline-but-recommended)
- **2 new mints**: `GV.PD-17 Information Asset Register Completeness` (T1) and `GV.VT-16 Joint-Controller Status Assessment` (T2)

**Net effect on counts** (when Phase 5 lands as v5.3.0): 221 → 239 metrics; 45 → 63 Tier 1.

**Three reviewer decision points flagged** in the file:
1. Whether `GV.SC-1/-2/-6` cybersecurity cluster is genuinely T1-shape vs T2-shape (FTS silent on cadence)
2. Whether the 2 new mints (`GV.PD-17`, `GV.VT-16`) belong as metrics or as a separate process-attestation kind
3. Big-bang vs staged release shape for v5.3.0

**Honest scope ceiling preserved**: the Atamis application pack remains the unaccessed ground truth. Phase 5 verdicts may shift if/when that pack becomes accessible.

**~73 gap items would remain in `_gaps.md` after Phase 5** — concentrated in product-capability gaps (RSET §1a, ~9), RAI Playbook + Theme governance gaps (§4, ~38), and framework-deferrable gaps (NICE ESF, T.E.S.T., PSIRF, remaining CQC + PRSB, ~21).

## v5.1.3 (2026-05-05)

**Patch release: archive housekeeping.**

No metric / catalogue content changes. Two files moved from repo root to `archive/v5.0.3/`:

- `v5.0.3-cadence-plan.md`
- `v5.0.3-cadence-audit.md`

Both shipped as part of the v5.0.3 cadence audit + v5.1.0 cadence-dimension cleanup. The audit scope is now closed (TP.ASR-13 + TP.ASR-12 directly fixed, multi-cadence-deferred set addressed in v5.1.0). Per the CLAUDE.md "archive/ is for finished work only" convention, these belong in `archive/` now.

## v5.1.2 (2026-05-05)

**Patch release: Phase 1b framework coverage audits — batches 2 + 3 (NHS LLM, DSPT, NICE ESF, T.E.S.T., UK GDPR, CQC, FHIR UK Core, ICO).**

No metric / catalogue content changes. One research-output file at repo root: `v5.1.2-phase-1b-batches-2-3.md`.

Continues from v5.1.1 batch 1 (DTAC + NHSE IG + DCB + MHRA). v5.1.2 ships the remaining 8 frameworks the Registry transitively requires, completing Phase 1b.

**Headline result for batches 2 + 3**: ~140 sub-criteria audited, **0 NEW gaps** beyond what batch 1 surfaced. Combined with batch 1 (128 sub-criteria, 2 NEW gaps), Phase 1b totals **268 sub-criteria across 12 frameworks, only 2 NEW gaps** (information asset register; joint-controller status assessment).

**Per-batch summary:**
- Batch 2 (NHS LLM + DSPT + NICE ESF + T.E.S.T.): 0 NEW gaps; ~14 already-roadmapped candidates surfaced (GV.OP-13 TCO, ES.ME-9/10, GV.OP-10/11 economic eval, TP.WB-8/9/10 FHIR, GV.VT-11/12, IO.FE-9, etc.)
- Batch 3 (UK GDPR + CQC + FHIR + ICO): 0 NEW gaps; ~10 already-roadmapped candidates surfaced (GV.CR-12 board governance, GV.SG-19 PSIRF, IO.PX-11/12 complaint handling + engagement, TP.WB-11 PRSB, GV.PD-15 anonymisation provenance, etc.)

**Cross-framework synergies confirmed**: many gap candidates appear across 3-4 frameworks (e.g. `GV.CR-12 Board-Level AI Governance` covers CQC + RAI Principle 10 + Theme 4 + DTAC C3.1). These multi-framework candidates are the highest-confidence Phase 5 priorities.

**Promotion-to-Tier-1 candidates**: stable at 8 (4 from v5.0.1 + 4 from v5.1.1 batch 1). Batches 2 + 3 surfaced no additional promotion candidates.

**Phase 5 surface estimate (post all of Phase 1b)**: ~25-35 metric content changes. Post-Phase-5 counts would land **221 → 245-255 metrics**, **45 → 65-75 Tier 1**.

**Phase 1b is now complete.** All 12 Registry-transitively-named frameworks audited. Phase 5 is ready to commence pending user review and the Registry attestation form.

## v5.1.1 (2026-05-05)

**Patch release: Phase 1b framework coverage audits — batch 1 (DTAC, NHSE IG, DCB, MHRA).**

No metric / catalogue content changes. One research-output file at repo root: `v5.1.1-phase-1b-framework-audits.md`.

Continues from v5.0.1 Phase 1a (Registry transitive coverage map). v5.1.1 is the first batch of per-framework deep coverage audits across the 4 highest-yield Registry-mandatory frameworks: DTAC v2.0, NHSE IG Guidance (March 2026), DCB0129/DCB0160, MHRA SaMD/AIaMD.

**Headline result**: 128 substantive sub-criteria audited across 4 frameworks. The taxonomy achieves very strong coverage — most sub-criteria map cleanly to existing metrics. **Only 2 NEW gaps** (verified absent from `_gaps.md`):

1. Information asset register / storage-location documentation (NHSE IG)
2. Joint-controller status assessment (NHSE IG / UK GDPR Art 26)

15 already-roadmapped gaps cross-confirmed (including GV.CR-11 SaMD classification, GV.SG-18 PCCP, GV.PD-12 training data representativeness, GV.VT-9/-10 MHRA PMSR/Transparency, GV.SG-19 PSIRF systems-based incident analysis, GV.CR-14 Caldicott consultation-type, TP.WB-11 PRSB semantic completeness, IG-A through IG-D from §1c).

Promotion-to-Tier-1 candidates surfaced by the audits: GV.SG-3, GV.SC-1, GV.SC-2, GV.SC-6 (cybersecurity + performance monitoring) — added to the 4 from v5.0.1 (GV.VT-2, GV.VT-14, IO.FE-1, TP.ASR-4). 8 total candidates awaiting user discussion before Phase 5.

**Phase 5 surface estimate**: ~25 metric content changes (15 pull-throughs + 2 mints + 8 promotions). Post-Phase-5 counts would land ~235-240 metrics, ~55-60 Tier 1.

**Phase 1b batches 2 + 3** (NHS LLM Framework + DSPT + NICE ESF + T.E.S.T.; UK GDPR + CQC + FHIR UK Core + ICO) planned for v5.1.2 and v5.1.3.

**Honest scope note**: audits worked from the transitively-named frameworks, not the Registry's specific attestation form (still not publicly accessible). Phase 5 prioritisation needs the actual Registry form to land.

## v5.1.0 (2026-05-05)

**Minor release: cadence-dimension cleanup — multi-valued Cadence; new `Event-triggered` enum value; ~32 metric edits.**

User noticed (during the v5.0.3 cadence audit) that DPIAs and similar regulatory artefacts are "updated to reflect material changes to their coverage" — a cadence pattern distinct from `One-off gate`, `Periodic audit`, and `Continuous`. The single-value Cadence dimension also can't express that some metrics are genuinely *both* a pre-deployment gate AND continuously / periodically / event-triggered re-measured. v5.1 addresses both.

**What changed.**

- **`Measurement Cadence` dimension is now multi-valued.** Semicolon-separated, e.g. `One-off gate; Continuous` or `Periodic audit; Event-triggered`. A metric carrying multiple cadences is operational at each — both apply.
- **New `Event-triggered` enum value.** Distinct from `Periodic audit` (calendar-driven) and `Continuous` (always-on). Re-measurement is triggered by a material change event: model version update, contract renewal, new sub-processor disclosed, new failure mode discovered, retirement event, scope expansion, etc.
- **The four-element enum is now formally enforced.** Previously the catalogue had crept in 6 distinct cadence strings (e.g. `One-off gate; reviewed annually`, `One-off gate + per-event`); these are normalised to the enum form.

**Metric edits.** 32 metric content changes:

- **18 Cadence updates** to multi-value or new value, including TP.WB-1 / TP.WB-3 (`One-off gate; Continuous`), GV.SG-1 / GV.SG-17 / GV.TC-5 (`Continuous; Event-triggered`), GV.SG-2 (`Event-triggered` — pure event-triggered), GV.CR-6 / GV.CR-7 / GV.CR-8 (`Periodic audit; Event-triggered` — DPIA-style), GV.PD-7 (`One-off gate; Periodic audit; Event-triggered`), and TP.ASR-8 (`One-off gate; Event-triggered`).
- **14 Lifecycle Phases trims** on metrics where Lifecycle Phases listed Periodic Audit / Continuous but body content is genuinely pre-deployment-only — covers the v5.0.3 multi-cadence-deferred set (TP.AC-3, TP.AC-6, TP.ASR-1, TP.ASR-2, TP.DI-1, TP.DI-2, TP.DI-5, TP.DI-8, TP.SN-13, PI.PP-1, PI.E2E-3, IO.FE-2, GV.SG-4, GV.CR-9). Cadence stays `One-off gate`; Lifecycle Phases tightens to `Pre-deployment`.

**`Change history:` stanzas added** on TP.WB-1, TP.WB-3, GV.SG-1, GV.CR-7 — the four metrics where the cadence rewrite is most semantically meaningful.

**Audit-side enforcement.** New `check_cadence_values` in `audit.py` validates every Cadence string as a semicolon-separated list of known enum values. Catches free-text deviations and prevents future drift. Existing pre-v5.1 deviations were normalised to the enum form as part of the metric edits above.

**Documentation.** `_how-to-use.md:Measurement Cadence` rewritten to describe the multi-value semantics, name `Event-triggered` as the fourth value, and explain when a metric pairs multiple cadences.

**Counts unchanged**: 221 / 45-97-79.

## v5.0.3 (2026-05-05)

**Patch release: cadence audit + 2 metric label fixes.**

User noticed TP.ASR-13 Numeric Accuracy was labelled `Measurement Cadence: One-off gate` but its body explicitly described monthly review of production-traffic numeric accuracy + a sustained-drift alert + a pause-on-confirmed-dosage-error trigger in production traffic. The label contradicted the body.

A scan found 51 metrics labelled `One-off gate` in the catalogue; 21 of them also listed `Periodic Audit` or `Continuous` in their `Lifecycle Phases` dimension — a widespread under-claiming pattern.

**Phase (a) — direct fix.** TP.ASR-13 cadence corrected to `Periodic audit`. Body is unchanged; pre-deployment retains via Lifecycle Phases. Change history stanza added.

**Phase (b) — full audit triage.** All 51 one-off-gate metrics audited against body content. Outcome:

- **1 additional Change** — TP.ASR-12 Hallucination-Under-Noise Rate. Operational Specification explicitly says "periodic audit re-runs the test corpus on every component change" — same shape as TP.ASR-13. Cadence corrected to `Periodic audit` in v5.0.3.
- **19 Multi-cadence (defer)** — Lifecycle Phases lists Periodic / Continuous but the body content is pre-deployment-focused; Lifecycle Phases is the outlier, not Cadence. The fix is either tightening Lifecycle Phases per-metric or splitting the Cadence dimension structurally — both v5.1+ work.
- **30 Keep** — body and label and Lifecycle Phases all genuinely agree on one-off-gate semantics.

The triage file at `v5.0.3-cadence-audit.md` (repo root) has the per-metric verdicts with rationales.

**Structural finding for v5.1+.** `Measurement Cadence` is a single-value dimension, but at least 3 metrics (TP.WB-1, TP.WB-3, GV.PD-10) have body content that genuinely combines a hard pre-deployment gate AND ongoing periodic / continuous measurement. The single-value dimension can't express that cleanly. v5.1+ should either (a) allow Cadence to be multi-valued, or (b) split into `Pre-deployment Gate` + `Ongoing Cadence` columns. Deferred.

**Counts unchanged**: 221 / 45-97-79.

**Other housekeeping (carried in this release).** Three `v4.6-threshold-*.md` research-output files moved from repo root → `archive/v4.6/` (they fed the v5.0 structural threshold split which has shipped, so per the CLAUDE.md "archive/ is for finished work only" convention they belong there now). `.gitignore` updated to ignore `.cache/`, `.playwright-mcp/`, `.pytest_cache/`, `.venv/`.

## v5.0.2 (2026-05-04)

**Patch release: standalone summary of Registry-needed metrics.**

No metric / catalogue content changes. One additional research-output file at repo root: `v5.1-registry-needed-metrics.md` — a small, scannable list pulled out of v5.0.1's longer Phase 1a audit, answering the direct question "what metrics does the AVT Registry transitively need?". 38 Tier 1 metrics confirmed Registry-relevant, organised by attestation type (clinical safety, IG, NHS-specific compliance, vendor transparency, AVT-specific accuracy, clinical accountability, operational/interop). Carries the same honest scoping note as v5.0.1: mapped against the *transitive surface* (CIO/CCIO + IG guidance), not the actual Registry attestation form (which is not publicly accessible).

This file is intended as a quick reference while waiting for the actual Registry attestation form. When the form is available, re-running Phase 1a against this list produces a sharp diff (confirmed / surplus / net gap).

## v5.0.1 (2026-05-04)

**Patch release: Phase 1a Registry coverage audit (research output for v5.1+ minimum-set work).**

No metric / catalogue content changes. One research-output file added at repo root: `v5.1-registry-coverage-audit.md`.

**What this is.** Plan-future #4 (Tier 1 minimum-set construction) starts with a coverage audit against the NHS England AVT Self-Certified Supplier Registry. Per the user-direction framing, the minimum set extends Tier 1 (no demotions; promotions only; replacements discussed explicitly), and the Registry pulls in transitive coverage of every framework it references.

**Honest scope note.** The public Registry page at `digital.nhs.uk/services/ambient-scribing/...` does not publicly enumerate the attestation criteria themselves — they live behind the National Commercial and Procurement Hub. The audit therefore maps against the *transitive surface*: the CIO/CCIO guidance + IG guidance (March 2026) + Mills & Reeve legal summary + HTN article on the registry launch. The actual attestation form would refine this if accessible.

**Headline findings.**

- **14 frameworks** transitively required by the Registry; **all 14 already in catalogue** (1 — Caldicott / NDG — already on the gap roadmap as `_gaps.md §2g`). No new framework handles needed.
- **~70 substantive requirements** mapped across 7 areas (clinical safety, IG, vendor transparency, AVT-specific accuracy, clinical accountability, operational/interop, training/governance).
- **Most requirements already covered** at Tier 1 today.
- **4 candidate promotions Tier 2 → Tier 1**: GV.VT-2 Telemetry Provision Completeness, GV.VT-14 Indicative Pricing Transparency, IO.FE-1 Deployment Equity Index, TP.ASR-4 Demographic-Disaggregated WER. Discussion required before Phase 5.
- **4 already-roadmapped gaps to pull through**: GV.SG-19 (PSIRF), GV.CR-12 (CQC), GV.CR-14 (Caldicott), TP.WB-11 (PRSB).
- **~8 new gap candidates** surfaced: lawful-basis-documentation, Right to Restrict Processing, information-asset-register, joint-controller-status, organisational opt-out mechanism, training-data-provenance disclosure, encryption-specific attestation, AVT-specific organisational policy.

**Phase 1b plan.** Per-framework coverage audit across 11 frameworks (DTAC, DSPT, DCB0129, DCB0160, MHRA SaMD, NHS LLM Framework, NHSE IG Guidance, NICE ESF, NHS T.E.S.T., CQC, UK GDPR, FHIR UK Core, ICO). Sequenced highest-yield-first (DTAC → IG → DCB → MHRA → LLM → DSPT → ESF → T.E.S.T. → GDPR → CQC → FHIR → ICO). Likely ships across 2-3 PATCH releases.

Plan-future #4 progresses; closes when Phase 5 promotions and `minimum-set.md` page land.

## v5.0.0 (2026-05-04)

**Major release: structural split — threshold numbers move out of metric bodies into a dedicated Threshold Reference page.**

The user-direction concern that started this work: numbers leaked from metric bodies into procurement contracts and academic citations without their context. The "proposed in vX.Y as starting points" Provenance preludes did honest work locally but couldn't travel with the number once it was copy-pasted out. v5.0 addresses this structurally rather than rhetorically.

**The split.**

- New top-level page **[Threshold Reference](thresholds.md)** at `docs/thresholds.md` (source: `taxonomy/_thresholds.md`). Contains every taxonomy-proposed threshold across the tightened-pattern metrics, with a "why this number" provenance column per row, four named cross-metric conventions (severity-weighting, test-corpus floor, severity-band notification ladders, aggregate-rate gates vs zero-tolerance category boundaries), and a prominent compound-errors caveat repeated structurally throughout.
- **Metric bodies**: the **Threshold Guidance** sub-block is renamed **Trigger Conditions**. Each Trigger Conditions block now carries a one-line pointer to the per-metric anchor on the Threshold Reference page. Cited numbers (NAS Day Zero SPI, UK GDPR statutory, NHSE guidance) stay in metric bodies — they are sourced, not proposed. Severity-weighting formulas stay in metric bodies (definitional to the metric) and are restated on the Threshold Reference page so the page is self-contained.

**The "starting points" framing is structurally repeated** at the page top, at every per-metric section, and inside every Trigger Conditions pointer. The compound-errors caveat is named explicitly: each threshold was authored independently, has not been jointly calibrated against deployment data, and a deployment that adopts every threshold as written may sit on overlapping triggers that no single trigger predicted.

**Phase 2a tightenings applied.**

- **TP.ASR-12** drift threshold tightened: > 50 % drift → > 25 % drift sustained two audit cycles (was too loose; matches v3.4 GV.PD drift conventions).
- **TP.WB-2** IER < 0.001 provenance reframed: was "standard SLA target" (vague); now flagged as "standard healthcare integration SLA convention" with the Three-nines-reliability lineage made explicit.
- **GV.TC-1** module-minute floors loosened: the specific 30 / 15 / 20-minute floors added false precision and have been replaced with "engagement floor per module — deployer-set based on module length, audited via session-time telemetry".

**Phase 2b cross-metric conventions named.** Four patterns that previously recurred across multiple metric bodies now have single named definitions on the Threshold Reference page:

1. **Severity-weighting convention** — symmetric `(0.1·benign + 0.5·moderate + 1.0·critical) / N` referenced by TP.ASR-12, TP.SN-5, TP.SN-6, TP.SN-15. Asymmetric variant for TP.SN-20 explicitly distinguished.
2. **Test-corpus floor convention** (≥ 200 cases + ICC ≥ 0.85) — referenced by 6+ metrics. Adds an explicit **rare-event-rate caveat** that the prior taxonomy did not make: 200 is a floor, not a target — for sub-1 % rates, push the floor above 1000 expected events.
3. **Severity-band notification-ladder convention** — meta-pattern (3-4 bands, 3-7× ratios, immediate-most-severe) referenced by GV.SG-1, GV.VT-1, GV.VT-5, GV.VT-15. Per-metric ladders kept because the underlying decisions genuinely differ.
4. **Aggregate-rate gates vs zero-tolerance category boundaries** — the most important reframe. Many "100 %" thresholds in the catalogue are zero-tolerance category boundaries, not stringent percentage gates. Same numbers, fundamentally different communication. Body prose now says "definitional category boundary" or "pre-deployment gate" depending on which.

**Build / audit changes.**

- `audit.py:TIGHTENING_SUB_BLOCKS` updated: `Threshold Guidance` → `Trigger Conditions`.
- `check_threshold_provenance` repurposed: previously checked for the in-body Provenance prelude; now checks that every tightened metric's Trigger Conditions block contains a pointer to `thresholds.md` with the metric's own anchor.
- `build_site.MAPPING` adds `_thresholds.md` → `thresholds.md`.
- `link_bare_ref_ids` skips `thresholds.md` (the page uses ref-IDs in `####` headings as anchors via attr_list — linkifying them would break the round-trip).
- `mkdocs.yml` nav adds Threshold Reference under About.

**Why MAJOR not MINOR.** The Threshold Guidance heading rename is a breaking change for any tooling that grepped or parsed metric bodies for `**Threshold Guidance**`. The `_thresholds.md` source file is new. The audit-check rename (`missing-threshold-provenance` → `missing-thresholds-pointer`) is a breaking change for anyone consuming the audit JSON. v3.x → v4.0 was MAJOR for the same reason (Part-letter retirement); v4.x → v5.0 is MAJOR for the structural threshold split.

**Plan-future #8 closes** with this release.

**Counts unchanged**: 221 metrics / 45-97-79 tiers. Catalogue size unchanged. The shape change is structural, not content.

---

Earlier releases (v1.0 – v4.5.1) are in [CHANGELOG-archive.md](CHANGELOG-archive.md).

