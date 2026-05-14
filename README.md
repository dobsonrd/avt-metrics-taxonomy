# Prototype AVT Metrics Taxonomy

A healthcare metrics taxonomy for assuring Ambient Voice Technology (AVT) systems from an NHS perspective.

**236 metrics across 20 groups**, covering the full AVT pipeline from audio capture to downstream write-back, plus governance, human factors, equity, and meta-evaluation. **AI-coauthored prototype for discussion — v5.5.14, 2026-05-14.** Shared to provoke conversation; not a settled standard.

> ⚠️ This is an **AI-coauthored prototype for discussion**, not a finished taxonomy. Substantial portions were drafted with AI assistance and human-reviewed; **specific claims, citations, and threshold numbers may still contain confabulations or factual errors** despite review. Keep this front of mind, verify before use, and please flag anything that looks wrong — feedback on errors is genuinely welcome. It is shared openly to provoke conversation about what an AVT assurance frame should look like — *not* as an NHS-endorsed standard, regulatory document, or procurement gate. Tier assignments, threshold numbers, and metric framings will change in response to feedback. **You are invited to disagree, propose changes, point at gaps, flag errors, and share with colleagues. You should not paste threshold numbers into contracts, cite metrics as authoritative without flagging the prototype status, or treat any specific metric as policy.** See [docs site → Prototype status](https://danjscho.github.io/avt-metrics-taxonomy/prototype-status/) for the full framing.

## Quick links

- **Published site:** <https://danjscho.github.io/avt-metrics-taxonomy/> — readable navigation, search, per-standard cross-cut pages, and per-family / per-layer / per-AI-substrate views.
- **Monolithic markdown:** [avt-metrics-taxonomy.md](avt-metrics-taxonomy.md) — single-file assembled output.
- **Structured data:** [`dist/metrics.csv`](dist/metrics.csv) (236-row export with per-metric Family, Layer, and AI-Substrate columns), [`dist/metrics.json`](dist/metrics.json) (full structured catalogue), [`dist/gaps.json`](dist/gaps.json) (74 outstanding roadmap candidates).
- **Release history:** [CHANGELOG.md](CHANGELOG.md).
- **Reference implementation library** *(prototype, not yet on main)*: TP.ASR-cluster pilot of a runnable companion package on the `reference-library-pilot` branch ([`pkg/avt_metrics_ref/`](https://github.com/danjscho/avt-metrics-taxonomy/tree/reference-library-pilot/pkg/avt_metrics_ref)). Independently-versioned (`v0.1.0`); MIT-licensed; 51 unit tests.
- **What's in scope vs out of scope:** [Outcomes Boundary](taxonomy/_outcomes-boundary.md) — this taxonomy assures deployment safety; clinical-outcome validation is national-research-body work.
- **How to apply the metrics to your deployment:** [Calibration & Context principle](taxonomy/_calibration-and-context.md) — tier assignments and threshold numbers are calibration starting points; six deployment-setting axes (specialty mix, patient population, platform maturity, governance capacity, risk appetite, volume) drive local calibration.
- **Architecture of assurance:** [Layers of Defence](taxonomy/_layers-of-defence.md) — Prevention / Detection / Limitation framing applied per metric.
- **Worked failure pathways:** [Failure Pathways](taxonomy/_failure-pathways.md) — three concrete archetypes plus a day-by-day timeline of the closed governance loop.
- **Cuts at a glance:** [Dimensions Overview](taxonomy/_dimensions-overview.md) — what each per-metric dimension means and what it isn't.

## What this is for

The taxonomy organises measurable indicators that NHS deployers, vendors, and assurance teams can use to evaluate AVT systems. Metrics are tiered:

- **🟢 Tier 1 (58 metrics) — Minimum Viable Assurance.** What every deployer must measure to operate safely.
- **🟡 Tier 2 (99 metrics) — Recommended Assurance.** Add with reasonable governance capacity.
- **🔵 Tier 3 (79 metrics) — Advanced / Research.** Requires infrastructure that often doesn't yet exist.

Every metric carries thirteen structural dimensions (Reference, Priority Tier, Applicability, Family, Layer of Defence, Pipeline Layer, Assurance Question, Measurement Method, Lifecycle Phases, Measurement Cadence, Responsible Actors, Maturity, Outcome Type, Source) — see [Dimensions Overview](taxonomy/_dimensions-overview.md) for what each cut means and how it differs from neighbouring cuts.

The taxonomy commits to three parallel principles that govern how it should be applied:

- The [Outcomes Boundary](taxonomy/_outcomes-boundary.md) names what's *out of scope* (clinical-outcome validation belongs elsewhere).
- The [Calibration & Context principle](taxonomy/_calibration-and-context.md) names what's *in scope but context-dependent* (tier assignments and threshold numbers are deployer-calibrated starting points).
- The [Layers of Defence principle](taxonomy/_layers-of-defence.md) names how the metrics *compose* into prevention / detection / limitation infrastructure — no layer is sufficient on its own.

Read all three before applying any metric in procurement or operational governance.

## Per-audience entry points

### Procurement officer / Clinical Safety Officer

Start with the **Tier 1 Quick Reference** in the rendered site or [taxonomy/_tier-1-quick-reference.md](taxonomy/_tier-1-quick-reference.md). The 58 Tier 1 metrics are organised by responsible actor (Vendor, Deployer, Regional, National Body). **The Tier 1 list is a calibrated starting point, not a fixed checklist** — your specialty mix, patient population, platform maturity, governance capacity, risk appetite, and volume all shift which metrics belong in your Tier 1 set; see the [Calibration & Context principle](taxonomy/_calibration-and-context.md) for the structural commitment and the documentation expectation.

For tightened metrics, the **Operational Specification** sub-block tells you what your vendor must comply with at procurement; the **Trigger Conditions** sub-block names the qualitative escalation patterns post-deployment, and the [Threshold Reference page](https://danjscho.github.io/avt-metrics-taxonomy/thresholds/) holds the per-anchor starting-point thresholds with explicit ⚠️ Provenance lines distinguishing externally-cited thresholds (NAS Day Zero SPI, UK GDPR, NHSE IG guidance March 2026) from numbers proposed in this taxonomy as starting points that require local calibration before contractual use.

For the AVT Self-Certified Supplier Registry surface, see [`v5.2-registry-action-list.md`](archive/v5.4/v5.2-registry-action-list.md) — the action list anchored to FTS notice 069369-2025 that drove the Phase 5 minimum-set extension in v5.3.0 / v5.4.0 (now archived; the metric content lives in the catalogue itself).

For NHS T.E.S.T. assurance, see the NHS T.E.S.T. Framework section in [taxonomy/_standards-mapping.md](taxonomy/_standards-mapping.md) — the framework's 22 Section A platform-assurance requirements and 12 Section B benefit domains are mapped to specific metrics in this taxonomy.

### Vendor

The standards-mapping section ([taxonomy/_standards-mapping.md](taxonomy/_standards-mapping.md)) maps every metric against thirteen NHS / regulatory frameworks: DTAC, DSPT, DCB0129/0160, NHS England LLM Evaluation Framework, NHS T.E.S.T., MHRA SaMD/AIaMD, NICE ESF, FHIR UK Core, CQC, PSIRF, PRSB, Caldicott, and the NHS England AVT Self-Certified Supplier Registry. Use it to identify which metrics satisfy which compliance obligation.

The [Outcomes Boundary](taxonomy/_outcomes-boundary.md) is worth reading first — it sets the explicit limit of what this taxonomy assures (deployment safety) versus what national research bodies must validate (clinical outcomes). Vendors making outcome claims should also see ES.ME-8 Outcome Evidence Commitment Status and ES.ME-9 Causal Model Operationalisation in [taxonomy/es/meta-evaluation.md](taxonomy/es/meta-evaluation.md), which operationalise vendor-side commitment to outcome evaluation.

When pricing or scoping AVT contracts against this taxonomy, note that the [Calibration & Context principle](taxonomy/_calibration-and-context.md) means the contractual gate is the *deployer's local calibration*, not the taxonomy's published starting-point thresholds. Vendors should expect deployer calibration documents that name the local tier assignments and threshold values; once a deployer has calibrated, the calibrated number is the contract.

### Developer / contributor

[taxonomy/README.md](taxonomy/README.md) covers the full local-build recipe (uv-based) and the file layout. Quick version:

```
uv sync --extra dev                    # one-off: install deps + pytest from uv.lock
uv run python taxonomy/build.py        # → avt-metrics-taxonomy.md + dist/* CSV/JSON
uv run python taxonomy/build_site.py   # → populates docs/ and mirrors dist/* into docs/downloads/
uv run mkdocs serve                    # → http://127.0.0.1:8000/avt-metrics-taxonomy/
uv run python taxonomy/audit.py        # → structural + tier + family + layer + cadence audits
uv run pytest                          # → 99 unit tests (parse / build / build_site / audit / snapshot)
```

The project uses [uv](https://docs.astral.sh/uv/) for environment management; `uv.lock` is committed so local and CI builds match. `audit.py` is the source of truth for current structural correctness — fourteen audit checks cover tier totals, applicability, maturity values, family resolution, layer enum, cadence enum, within-cluster ordering, summary maturity drift, and more. Future work scope is derived from this output rather than from CHANGELOG prose.

[`taxonomy/parse.py`](taxonomy/parse.py) extracts every metric from its dimension table; [`taxonomy/build_site.py`](taxonomy/build_site.py) renders the MkDocs site; [`taxonomy/_gaps.md`](taxonomy/_gaps.md) is the consolidated roadmap of 74 outstanding candidates (with promoted candidates lifted to a §7 historical record for clean separation).

The [`archive/`](archive/) directory holds prior plans and research artefacts: the v3.4 Tier 1 LOOSE/TIGHT/SURROGATE classification, the v3.6 duplication review, per-release plans, and closed-but-preserved Phase 1a / 1b registry coverage research.

### Researcher

Several cross-cutting documents frame the policy, ethics, and application surface:

- [taxonomy/_responsible-ai-lens.md](taxonomy/_responsible-ai-lens.md) — DSIT AI Playbook (Feb 2025) ten principles and the six Responsible AI ethical themes (Safety/Security/Robustness; Transparency/Explainability; Fairness; Accountability/Governance; Contestability/Redress; Societal Wellbeing). Covers 38 cross-cutting policy gaps.
- [taxonomy/_outcomes-boundary.md](taxonomy/_outcomes-boundary.md) — explicit out-of-scope statement (this taxonomy does not assure clinical outcomes; that work belongs elsewhere) plus pointers to ES.ME-1, ES.ME-8, ES.ME-9 for the proximal/distal causal-logic framework.
- [taxonomy/_calibration-and-context.md](taxonomy/_calibration-and-context.md) — parallel principle to the Outcomes Boundary: tier assignments and threshold numbers are calibration starting points, not universal gates. Six deployment-setting axes drive local calibration. Research-side relevance: studies citing the taxonomy should specify both the version and the calibration applied to the deployment under study.
- [taxonomy/_layers-of-defence.md](taxonomy/_layers-of-defence.md) — Prevention / Detection / Limitation framing as a per-metric explicit dimension. The architectural shape that the catalogue exposes for assurance design.
- [taxonomy/_failure-pathways.md](taxonomy/_failure-pathways.md) — three worked failure pathways plus a day-by-day timeline of the closed governance loop. The "taxonomy in motion" companion to the architectural framing.
- [taxonomy/_ai-substrate.md](taxonomy/_ai-substrate.md) — five-class derived cut answering "which metrics test the AI itself, vs the infrastructure around it, vs the governance of it?"
- [taxonomy/_families.md](taxonomy/_families.md) — eight named metric families consolidating cross-cluster construct groupings (Clinical Content Fidelity, Demographic Equity Disaggregation, Medication Safety Thread, NHSE IG Attestation, PRSB Semantic Completeness & Write-back Fidelity, Post-Generation Correction, Reference-Based Text Similarity, Clinical Transcription Accuracy).
- [taxonomy/_gaps.md](taxonomy/_gaps.md) — 74 outstanding metric candidates with classification (proposed / accepted / deferred / rejected). Single source of truth across five origins.

## Citation grammar (v3.9 onwards)

External citations in metric files use a two-layer grammar settled at v3.9:

1. **Inline reference** in metric prose — a short stable handle in square brackets, e.g. `[DCB0129]`, `[NHSE-IG-Guidance-2026-03]`, `[UK-GDPR]`, `[Keyes-Stanford-Monitoring-2025]`.
2. **Catalogue entry** in [taxonomy/_references.md](taxonomy/_references.md) — full bibliographic record per handle (Title / Publisher / Source-Type / URL / Archive / Retrieved date / `Local-Mirror` / `Short` field used as the human-readable link label at site-build time).

Source rows in metric Dimensions tables, Reference Standard / Trigger Conditions prose blocks, and the `_standards-mapping.md` framework sections all follow this convention. The grammar separates *what* is cited from *where* the bibliographic detail lives, so a citation update touches one catalogue entry rather than every metric that references it.

`audit.py` enforces handle resolution: every `[Handle]` in a metric file must exist in `_references.md`, or the audit fails.

## Status / version

**Current prototype version:** v5.5.14, released 2026-05-14.

**Headline state at v5.5.14:**

- **236 metrics** across **20 groups**, organised in six clusters (TP / PI / HL / IO / GV / ES).
- **Tier counts:** 58 / 99 / 79 (Tier 1 / Tier 2 / Tier 3).
- **Maturity:** 69 Established / 64 Emerging / 4 Vendor-Proprietary / 99 Proposed/Novel.
- **8 named metric families** (cross-cluster construct groupings); ~50 metrics carry an explicit `Family` field.
- **All 236 countable metrics carry an explicit `Layer` field** (Prevention / Detection / Limitation): 77 Prevention, 134 Detection, 25 Limitation. Three additional parent-construct metrics (TP.SN-7, TP.SN-9, HL.HF-3) also carry a Layer for routing purposes; sub-parts inherit the parent's classification.
- **AI-substrate classification** derived per metric (countable view): 125 AI-Substrate, 64 AI-Agnostic Governance, 29 AI-Mediated Workflow, 9 Pre-AI, 9 Post-AI.
- **74 outstanding roadmap candidates** in `_gaps.md`; 17 candidates promoted across all releases to date (lifted to `_gaps.md §7` historical record).
- **13 NHS / regulatory frameworks** mapped in `_standards-mapping.md`.
- **~110 References-catalogue entries** in `_references.md`, all audit-enforced.
- **99 unit tests** in `taxonomy/tests/`; CI runs on every push.
- **14 audit checks** in `audit.py` cover structural, dimension-enum, count, ordering, and resolution properties.

### v5.x highlights

The v5.x line went from a mid-stage prototype (221 metrics, ~45 Tier 1) to a more substantively complete artefact:

- **v5.0.0** (MAJOR) — Threshold Reference structural split: threshold numbers moved out of metric bodies into a dedicated page; **Trigger Conditions** sub-block replaces **Threshold Guidance** with qualitative-only content; per-metric pointers link to per-anchor sections; "starting points" framing structurally repeated.
- **v5.1.0** — Cadence-dimension cleanup: multi-valued Cadence + new `Event-triggered` enum value; 32 metric edits.
- **v5.3.0** — Phase 5 lands: 7 promotions T2 → T1 + 13 new pull-through metrics from `_gaps.md` against the FTS-direct surface (anchored to FTS notice 069369-2025). Counts moved 221 → 234.
- **v5.4.0** — 5 workstreams: 2 parent + sub-part formalisations (PCCP and DPIA pairs); new `_families.md` with audit-enforced `Family` dimension; new `_layers-of-defence.md` first-class principle; new `_dimensions-overview.md` reader-orientation page; 2 v5.4 mints (GV.PD-18 Information Asset Register, GV.VT-11 Joint-Controller Status). Counts 234 → 236.
- **v5.5.0** — NHSE IG section refs cleanup; new `_ai-substrate.md` documentation page; inline family framings consolidated to `_families.md`; auto-generated by-family + by-layer-of-defence cross-cut site pages; `Layer` introduced as optional per-metric dimension seeded with 33 explicit values.
- **v5.5.1** — Failure Pathways page (3 archetypes + worked timeline).
- **v5.5.2** — Code-snippet + Formal Definition verification across the 23 code snippets and the 15 v5.3/v5.4 metrics; threshold-page regression fix.
- **v5.5.3** — AI-substrate Option 2: derived classification at build time; 5 new `by-ai-substrate/` cross-cut pages; `ai_substrate` column in CSV/JSON.
- **v5.5.4** — Explicit `Layer` extended from 33 to all 236 metrics (77/137/25 Prevention/Detection/Limitation); cadence heuristic retained as fallback.
- **v5.5.5** — Consistency sweep: refreshed `_tier-1-quick-reference.md` with the 15 missing v4.1/v5.3/v5.4 Tier 1 metrics; corrected Maturity totals in `_summary.md` (Established 62→69, Emerging 53→64, Proposed/Novel 110→99); cleaned up stale "(NHS framing; was X)" suffixes; closed plan-future #4 and #5 with status updates; new `check_summary_maturity_counts` audit check.
- **v5.5.7** — Catalogue licensed under CC BY 4.0; README refreshed with current counts and v5.x highlights.
- **v5.5.8** — Repo-wide documentation sweep: refreshed `_contents.md` per-group counts, `taxonomy/README.md`, `CLAUDE.md`, `_glossary.md`, `METHODOLOGY.md`; added CC-BY-4.0 to `pyproject.toml`; archived `v5.3-pre-mint-triage.md` (live items lifted into `plan-future.md`); split `CHANGELOG.md` (v5.0+ stays, v1.0–v4.5.1 moved to `CHANGELOG-archive.md`); new `archive/v4.6/README.md` documenting the working-name-vs-released-tag distinction.
- **v5.5.9** — Reader-experience polish: home-page release-summary block restructured from one wall-of-text paragraph into structural-patterns + recent-highlights bullets; Tier 1 Quick Reference reformatted as per-actor tables (Metric · Cadence · Why) with v4.1/v5.3/v5.4 promoted/minted entries merged into the main lists with `(new)` / `(promoted)` markers; `_applicability.md` By-Cluster table refreshed (was stuck at the v3.x 221-metric / Part-letter shape, now uses cluster codes and 236 totals); standards-mapping / applicability / RAI-lens table cells now linkify metric-name mentions to per-metric pages at build time (new `link_metric_names_in_tables` build pass); `plan-future.md` split — completed items 3/4/5/7/8 moved to `archive/plan-future-archive.md` with original numbering preserved.
- **v5.5.10** — Browse-by-applicability counts on the contents page were hard-coded at 48/77/89 (v3.x baseline); now live-derived from the parsed catalogue (50 / 79 / 107) so they stay in sync with `_applicability.md` automatically.
- **v5.5.11** — Reader-feedback wiring + Tier 1 quick-reference structural breaks. (1) Five GitHub issue-form templates land at `.github/ISSUE_TEMPLATE/` (factual error / tier disagreement / missing metric / broken link / framing feedback) so readers reporting an error get a structured form rather than a blank issue. (2) Each group page now ends with a "Spotted an error?" footer linking directly to the right template. (3) Prototype-status page lists what each template is for. (4) Tier 1 Quick Reference tables now subdivide by cluster/group at build time (e.g. *TP · ASR / Transcription*, *GV · Privacy & Data Governance*) so each per-actor block scans more cleanly. (5) Home-page "three priority tiers" block converted from soft-wrapped lines (which collapsed to one line in rendered Markdown) into a proper bulleted list.
- **v5.5.12** — Tier 2 home-page line trimmed from "recommended for any AVT deployment" to "recommended for AVT deployment" and the three-tier block re-rendered as paragraph-separated lines (blank line between each tier) so each line renders independently without the bullet-list shape.
- **v5.5.14** *(this release)* — Add interactive Assurance Planner site page: tier toggle buttons, responsible actor dropdown (5 canonical groups matching the How to Use actor taxonomy), metrics grouped by measurement cadence sequence (Pre-deployment / Continuous / Periodic audit / Event-triggered).
- **v5.5.13** — Renamed title to "Prototype AVT Metrics Taxonomy" across all reader-facing surfaces (site nav, browser tabs, headings, citations) ahead of making the repository public.

See [CHANGELOG.md](CHANGELOG.md) for full per-release notes including all earlier v3.x and v4.x releases.

## Citation

Until the prototype reaches a settled state, please cite as:

> Schofield, D. (2026). *Prototype AVT Metrics Taxonomy v5.5.14* [prototype-for-discussion]. Licensed under CC BY 4.0. Retrieved from https://dobsonrd.github.io/avt-metrics-taxonomy/

Note: prototype status means content / tier assignments / cross-references may change in response to feedback. Cite the specific version (e.g. v5.5.14) so subsequent readers can reproduce what you read, and please flag the prototype status when citing in academic work — pasting numbers into contracts or treating any specific metric as policy is out of scope until the artefact is settled.

## Contributing

The current contribution path is **GitHub issues** for proposed gaps, corrections, or framework alignments: <https://github.com/danjscho/avt-metrics-taxonomy/issues>.

Substantive proposals (new metrics, sub-cluster framings, cross-references) are tracked through [`taxonomy/_gaps.md`](taxonomy/_gaps.md). The roadmap convention is: `proposed` → reviewed → `accepted` (drafted) or `deferred` (with reasoning preserved) or `rejected` (with reasoning preserved). Promoted candidates move to the `_gaps.md §7` historical record so the rationale at promotion time is preserved alongside the active metric.

A formal CONTRIBUTING file does not yet exist. Issues are the right entry point until one does.

## Licence

The catalogue content (Markdown source under `taxonomy/`, the assembled `avt-metrics-taxonomy.md`, the rendered MkDocs site, and supporting documents at the repo root) is licensed under **[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)** — see [LICENSE](LICENSE) for full terms and the suggested attribution recipe.

You are free to share and adapt the catalogue, including for commercial purposes, provided you give appropriate credit (cite this repository and the specific version), link the licence, and indicate whether you made changes.

The reference implementation library at `pkg/avt_metrics_ref/` (currently on the `reference-library-pilot` branch only) is licensed separately under **MIT** — software licence for the software artefact, content licence for the content artefact.

The build / parse / audit / site-build Python source in `taxonomy/build.py`, `taxonomy/parse.py`, `taxonomy/audit.py`, `taxonomy/build_site.py`, `taxonomy/tools/`, and `taxonomy/tests/` is supplied to make the catalogue reproducible. If you re-use the tooling independently of the catalogue content, treat it as MIT licensed for that purpose.

Quoted framework material — DTAC, NHS England IG Guidance, MHRA SaMD documents, Caldicott Principles, NICE ESF, NHS T.E.S.T., DSPT, FHIR UK Core, PRSB, UK GDPR, FTS notices, and other external sources — remains under each publisher's own licence; the catalogue cites them under fair-dealing / fair-use conventions for review and commentary.

If your use case doesn't fit cleanly into these categories, open an issue and we'll figure it out.

---

*Last updated: v5.5.14 / 2026-05-14.*
