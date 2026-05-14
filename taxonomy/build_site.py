"""Populate docs/ from the taxonomy source for MkDocs Material.

Pattern: each source file copied to the right docs path, with small
header tweaks so MkDocs page titles read well. The monolithic MD and
CSV/JSON downloads are still produced by build.py; this script only
lays out the site content.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
from collections import Counter, defaultdict

import parse as parse_src

ROOT = pathlib.Path(__file__).parent
REPO = ROOT.parent
DOCS = REPO / "docs"

# Single source of truth for the version stamp shown on landing + downloads.
# Bumped manually at each release as part of the release wrap; CI consumes
# the same string so site, monolith, and download citation stay aligned.
SITE_VERSION = parse_src.TAXONOMY_VERSION

# source file -> docs path
MAPPING: dict[str, str] = {
    "_header.md": "index.md",
    "_prototype-status.md": "prototype-status.md",
    "_how-to-use.md": "how-to-use.md",
    "_dimensions-overview.md": "dimensions-overview.md",
    "_tier-1-quick-reference.md": "tier-1-quick-reference.md",
    "_contents.md": "contents.md",
    "_applicability.md": "applicability.md",
    "_families.md": "families.md",
    "_standards-mapping.md": "standards-mapping.md",
    "_outcomes-boundary.md": "outcomes-boundary.md",
    "_calibration-and-context.md": "calibration-and-context.md",
    "_layers-of-defence.md": "layers-of-defence.md",
    "_failure-pathways.md": "failure-pathways.md",
    "_ai-substrate.md": "ai-substrate.md",
    "_responsible-ai-lens.md": "responsible-ai-lens.md",
    "_gaps.md": "gaps.md",
    "_glossary.md": "glossary.md",
    "_versioning.md": "versioning.md",
    "_thresholds.md": "thresholds.md",
    "_references.md": "references.md",
    "_assurance-planner.md": "assurance-planner.md",
    "tp/audio-capture.md": "groups/audio-capture.md",
    "tp/asr-transcription.md": "groups/asr-transcription.md",
    "tp/diarisation.md": "groups/diarisation.md",
    "tp/summarisation-nlp.md": "groups/summarisation-nlp.md",
    "tp/clinical-coding.md": "groups/clinical-coding.md",
    "tp/downstream-write-back.md": "groups/downstream-write-back.md",
    "pi/partial-pipeline.md": "groups/partial-pipeline.md",
    "pi/end-to-end-pipeline.md": "groups/end-to-end-pipeline.md",
    "hl/human-factors-workflow.md": "groups/human-factors-workflow.md",
    "io/patient-experience.md": "groups/patient-experience.md",
    "io/fairness-equity.md": "groups/fairness-equity.md",
    "gv/safety-governance.md": "groups/safety-governance.md",
    "gv/nhs-compliance-regulatory.md": "groups/nhs-compliance-regulatory.md",
    "gv/security-adversarial-robustness.md": "groups/security-adversarial-robustness.md",
    "gv/privacy-data-governance.md": "groups/privacy-data-governance.md",
    "gv/operational.md": "groups/operational.md",
    "gv/environmental-sustainability.md": "groups/environmental-sustainability.md",
    "gv/training-competency.md": "groups/training-competency.md",
    "gv/vendor-transparency-contractual.md": "groups/vendor-transparency-contractual.md",
    "es/meta-evaluation.md": "groups/meta-evaluation.md",
}


# Intra-monolith anchors that used to resolve inside the single file now
# need to redirect to the relevant page. Keys are the anchor slugs as they
# appear in the source; values are the target URL (relative to docs root).
ANCHOR_REWRITES: dict[str, str] = {
    # Group anchors - these were h2s inside the monolith; now they're pages.
    "audio-capture-environment": "groups/audio-capture.md",
    "asr-transcription": "groups/asr-transcription.md",
    "diarisation": "groups/diarisation.md",
    "summarisation-nlp": "groups/summarisation-nlp.md",
    "clinical-coding": "groups/clinical-coding.md",
    "epr-write-back": "groups/downstream-write-back.md",  # legacy alias from v3.x
    "downstream-write-back": "groups/downstream-write-back.md",
    "partial-pipeline": "groups/partial-pipeline.md",
    "end-to-end-pipeline": "groups/end-to-end-pipeline.md",
    "human-factors-workflow": "groups/human-factors-workflow.md",
    "patient-experience": "groups/patient-experience.md",
    "fairness-equity": "groups/fairness-equity.md",
    "safety-governance": "groups/safety-governance.md",
    "nhs-compliance-regulatory": "groups/nhs-compliance-regulatory.md",
    "security-adversarial-robustness": "groups/security-adversarial-robustness.md",
    "privacy-data-governance": "groups/privacy-data-governance.md",
    "operational": "groups/operational.md",
    "environmental-sustainability": "groups/environmental-sustainability.md",
    "training-competency": "groups/training-competency.md",
    "vendor-transparency-contractual": "groups/vendor-transparency-contractual.md",
    "meta-evaluation": "groups/meta-evaluation.md",
    # Cross-cutting sections - each now its own page.
    "applicability-classification": "applicability.md",
    "standards-mapping": "standards-mapping.md",
    "responsible-ai-lens": "responsible-ai-lens.md",
    "gaps-proposed-metrics-roadmap": "gaps.md",
    "outcomes-boundary": "outcomes-boundary.md",
    "calibration-context": "calibration-and-context.md",
    "references": "references.md",
    "prototype-status": "prototype-status.md",
    # Sections inside _standards-mapping.md that other pages link to.
    # Each is now an h2 on standards-mapping.md, so a fragment is preserved.
    "nhs-england-avt-self-certified-supplier-registry": "standards-mapping.md#nhs-england-avt-self-certified-supplier-registry",
    "nhs-test-framework-6-candidates": "gaps.md#3-nhs-test-framework-6-candidates",
    "nhs-test-framework-technology-evaluation-safety-test": "standards-mapping.md#nhs-test-framework-technology-evaluation-safety-test",
    "how-to-use-this-taxonomy": "how-to-use.md",
}

_MD_LINK = re.compile(r"(?<!!)\[([^\]]+?)\]\(#([a-z0-9][a-z0-9_-]*)\)")

# Metric headings look like:  ### TP.AC-1 🟡 Signal-to-Noise Ratio (SNR) Monitoring
# We want stable anchors like #tp-ac-1 so reference IDs can be cited forever.
# MkDocs' default slugifier drops the '.' and produces "tpac-1-...", which is
# unstable if the metric name changes. Inject an explicit {#tp-ac-1} via the
# attr_list extension (enabled in mkdocs.yml).
_METRIC_HEADING = re.compile(
    r"^(###\s+)([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+[a-z]?)(\s+[🟢🟡🔵]\s+.+?)\s*$",
    re.MULTILINE,
)


# Link every bolded metric name on the Tier-1 Quick Reference page to its
# source page. The source file (`_tier-1-quick-reference.md`) is authored
# prose - we don't edit it at source, we transform it on the way into the
# site. Each bullet is of the form:
#   - 🚪 **Metric Name** - rationale...
# We match `**Metric Name**` tokens (optionally followed by `⚠️`), look the
# name up in the parsed catalogue, and rewrite to a link.
_BOLD_METRIC_TOKEN = re.compile(r"\*\*([^*]+?)\*\*")


def _metric_name_index() -> dict[str, "parse_src.Metric"]:
    metrics = parse_src.parse_all_metrics()
    idx: dict[str, parse_src.Metric] = {}
    for m in metrics:
        idx[m.name] = m
        stripped = re.sub(r"\s*\([^)]*\)\s*", "", m.name).strip()
        if stripped and stripped not in idx:
            idx[stripped] = m
    return idx


def link_tier1_quickref(text: str) -> str:
    """Convert `**Name**` → `[REF-ID Name](../groups/<group>.md#ref-id)` when
    the bolded text matches a known Tier-1 metric. Non-metric bold phrases
    (e.g. **Deployer** actor subsection headings) are left untouched because
    they don't match the name index.

    The ref-ID prefix (e.g. `TP.SN-5`) is added inside the link to give
    readers cluster context (TP = Technical Pipeline, GV = Governance,
    etc.) and a stable shorthand for cross-referencing without losing the
    bolded human-readable name.
    """
    idx = _metric_name_index()

    def sub(m: re.Match) -> str:
        raw = m.group(1).strip()
        candidate = raw.rstrip(" ⚠️").strip()
        hit = idx.get(candidate)
        if hit is None:
            # Try base name (strip parenthetical)
            base = re.sub(r"\s*\([^)]*\)\s*", "", candidate).strip()
            hit = idx.get(base)
        if hit is None or hit.tier != 1:
            return m.group(0)  # not a Tier-1 metric, leave as-is
        slug = parse_src.ref_id_to_anchor(hit.ref_id)
        page = SRC_GROUP_FILE_TO_PAGE.get(hit.group_file, "")
        if not page:
            return m.group(0)
        # Keep the warning suffix outside the link if present.
        suffix = " ⚠️" if raw.endswith("⚠️") else ""
        return f"[`{hit.ref_id}` **{candidate}**]({page}#{slug}){suffix}"

    return _BOLD_METRIC_TOKEN.sub(sub, text)


# Map cluster code → friendly cluster name for the Tier-1 quick-reference
# sub-headers. Group names come from the parsed metric's group attribute.
_CLUSTER_FRIENDLY = {
    "TP": "Technical Pipeline",
    "PI": "Pipeline Interactions",
    "HL": "Human Layer",
    "IO": "Impact & Outcomes",
    "GV": "System Governance",
    "ES": "Evaluation Science",
}


def regroup_tier1_tables_by_cluster(text: str) -> str:
    """Split each per-actor Tier-1 table into per-cluster sub-tables. The
    source authors a single 3-column table per actor (Metric · Cadence ·
    Why); at build time we look each row's metric up, group by cluster +
    group, and emit one mini-table per (cluster, group) pair under a
    bolded subheader. Preserves the existing table column order; adds
    structural breaks so a long actor block is scannable.

    Runs *after* link_tier1_quickref so the rewritten Markdown links
    `[`REF-ID` **Name**](page.md#anchor)` are still visible to the row
    parser — we extract the ref-ID from the link target rather than from
    the metric-name index.
    """
    idx = _metric_name_index()
    name_to_metric = idx
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect a table header followed by a separator row
        is_header = (
            line.startswith("| Metric ")
            and i + 1 < len(lines)
            and re.match(r"^\|\s*-+", lines[i + 1])
        )
        if not is_header:
            out.append(line)
            i += 1
            continue
        header = line
        sep = lines[i + 1]
        # Collect data rows until a non-table line
        j = i + 2
        rows: list[str] = []
        while j < len(lines) and lines[j].startswith("|"):
            rows.append(lines[j])
            j += 1
        # Group rows by (cluster, group)
        groups: dict[tuple[str, str], list[str]] = {}
        ungrouped: list[str] = []
        for row in rows:
            # Try to extract a metric name from the first cell. After
            # link_tier1_quickref has run the cell looks like:
            #   | [`TP.AC-5` **Microphone & Hardware Validation**](...) | ... |
            # Pre-link form (if regroup runs before link) is just bolded.
            cells = [c.strip() for c in row.split("|")]
            cell0 = cells[1] if len(cells) > 1 else ""
            ref_id_match = re.search(r"`([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+[a-z]?)`", cell0)
            name_match = re.search(r"\*\*([^*]+?)\*\*", cell0)
            metric = None
            if ref_id_match:
                ref_id = ref_id_match.group(1)
                metric = next(
                    (m for m in name_to_metric.values() if m.ref_id == ref_id), None
                )
            if metric is None and name_match:
                raw = name_to_metric.get(name_match.group(1).strip().rstrip(" ⚠️"))
                if raw:
                    metric = raw
            if metric is None:
                ungrouped.append(row)
                continue
            cl = metric.ref_id.split(".")[0]
            grp = metric.group
            groups.setdefault((cl, grp), []).append(row)

        # Emit per-cluster subgroups in cluster order, preserving the
        # within-group order rows arrived in.
        cluster_order = ["TP", "PI", "HL", "IO", "GV", "ES"]
        emitted_any = False
        for cl in cluster_order:
            for (c, grp), grp_rows in list(groups.items()):
                if c != cl:
                    continue
                friendly = _CLUSTER_FRIENDLY.get(c, c)
                if emitted_any:
                    out.append("")
                out.append(f"**{c} · {grp}** *({friendly})*")
                out.append("")
                out.append(header)
                out.append(sep)
                out.extend(grp_rows)
                emitted_any = True
                del groups[(c, grp)]
        # Any remaining (unknown cluster) groups
        for (c, grp), grp_rows in groups.items():
            if emitted_any:
                out.append("")
            out.append(f"**{c} · {grp}**")
            out.append("")
            out.append(header)
            out.append(sep)
            out.extend(grp_rows)
            emitted_any = True
        if ungrouped:
            if emitted_any:
                out.append("")
            out.append("**Other**")
            out.append("")
            out.append(header)
            out.append(sep)
            out.extend(ungrouped)
        i = j
    return "\n".join(out)


def link_metric_names_in_tables(text: str) -> str:
    """Linkify bare metric-name occurrences inside markdown table cells on
    cross-cutting pages (standards-mapping, applicability summary tables,
    responsible-AI lens tables, etc.). The source authors write metric
    names as plain prose in the "Taxonomy Metrics" column — at build time
    we look each name up in the parsed catalogue and rewrite to a link to
    the per-metric anchor.

    Match strategy: walk lines that look like markdown table rows (`|`
    delimited), and within each cell, longest-match each catalogue metric
    name against the cell text. Skip cells that already contain a markdown
    link to avoid double-linking. Leave bolded names alone (they are
    handled by `link_tier1_quickref` on its dedicated page).
    """
    idx = _metric_name_index()
    # Sort names by length descending so longer matches (e.g. "Demographic-
    # Disaggregated WER") win over shorter prefixes ("WER").
    names_sorted = sorted(idx.keys(), key=len, reverse=True)
    # Build one big alternation regex; escape names for regex use. Require
    # word boundaries on both ends so partial-substring hits don't fire.
    if not names_sorted:
        return text
    pattern = re.compile(
        r"(?<![\w`\[])("
        + "|".join(re.escape(n) for n in names_sorted)
        + r")(?![\w`\]])"
    )

    def sub_in_cell(cell: str) -> str:
        # Skip cells that already contain a link
        if "](" in cell:
            return cell

        def repl(m: re.Match) -> str:
            name = m.group(1)
            hit = idx.get(name)
            if hit is None:
                return name
            slug = parse_src.ref_id_to_anchor(hit.ref_id)
            page = SRC_GROUP_FILE_TO_PAGE.get(hit.group_file, "")
            if not page:
                return name
            return f"[{name}]({page}#{slug})"

        return pattern.sub(repl, cell)

    out_lines: list[str] = []
    for line in text.splitlines():
        # Identify markdown table rows (start with |, contain at least one
        # other |). Skip separator rows (---|---).
        stripped = line.strip()
        if (
            stripped.startswith("|")
            and stripped.count("|") >= 2
            and "---" not in stripped
        ):
            cells = line.split("|")
            cells = [sub_in_cell(c) for c in cells]
            out_lines.append("|".join(cells))
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def add_metric_anchors(text: str) -> str:
    def sub(m: re.Match) -> str:
        prefix, ref_id, tail = m.group(1), m.group(2), m.group(3)
        slug = parse_src.ref_id_to_anchor(ref_id)
        # Keep the reference-ID visible in the heading; attach a stable id.
        return f"{prefix}{ref_id}{tail} {{ #{slug} }}"

    return _METRIC_HEADING.sub(sub, text)


# Repo-root files that source authors link to (for the monolithic build and
# GitHub README experience). These don't exist inside docs/, so MkDocs strict
# mode flags them. Rewrite to the docs equivalent (or to the GitHub raw URL
# for archive/* artefacts that are not part of the published site).
GITHUB_BLOB = "https://github.com/danjscho/avt-metrics-taxonomy/blob/main"
EXTERNAL_LINK_REWRITES: dict[str, str] = {
    "CHANGELOG.md": "changelog.md",
    "CHANGELOG-archive.md": f"{GITHUB_BLOB}/CHANGELOG-archive.md",
    "README.md": f"{GITHUB_BLOB}/README.md",
}

_EXTERNAL_LINK = re.compile(r"(?<!!)\[([^\]]+?)\]\(([^)#]+\.md)(#[^)]*)?\)")


def rewrite_external_links(text: str) -> str:
    """Rewrite source-side links that point outside docs/ to docs-internal
    paths or to GitHub blob URLs. Strict-mode mkdocs warns on these.

    Patterns handled:
    - `[X](CHANGELOG.md)` → `[X](changelog.md)`  (mapped into docs/)
    - `[X](README.md)` → GitHub blob URL  (lives at repo root only)
    - `[X](archive/<file>.md)` → GitHub blob URL  (research artefacts, not
       published)
    """

    def sub(m: re.Match) -> str:
        label, href, frag = m.group(1), m.group(2), m.group(3) or ""
        if href in EXTERNAL_LINK_REWRITES:
            return f"[{label}]({EXTERNAL_LINK_REWRITES[href]}{frag})"
        if href.startswith("archive/"):
            return f"[{label}]({GITHUB_BLOB}/{href}{frag})"
        return m.group(0)

    return _EXTERNAL_LINK.sub(sub, text)


_METRIC_SLUG_TO_PAGE_CACHE: dict[str, str] | None = None
_REFERENCE_HANDLES_CACHE: set[str] | None = None


def _reference_handles() -> set[str]:
    """Catalogue handle set, cached for the duration of a build run.

    Used to decide whether a given `[Handle]` token in a metric file should
    be rewritten as a hyperlink to references.md, or left as literal text
    (the latter shouldn't happen post-Phase 0; the audit catches unresolved
    handles in pilot files).
    """
    global _REFERENCE_HANDLES_CACHE
    if _REFERENCE_HANDLES_CACHE is None:
        _REFERENCE_HANDLES_CACHE = set(parse_src.parse_references().keys())
    return _REFERENCE_HANDLES_CACHE


_REFERENCE_SHORTS_CACHE: dict[str, str] | None = None


def _reference_shorts() -> dict[str, str]:
    """{handle: short-form text} — only for catalogue entries that declared
    a `**Short:**` field. Empty for entries that didn't, in which case the
    handle itself is used at render time (preserves prior behaviour).

    Introduced in v4.5 (citation grammar polish): rendering `[Handle]` as
    a slug reads poorly in prose; entries opt in by declaring a Short form
    and the build-time rewriter uses it as the link label.
    """
    global _REFERENCE_SHORTS_CACHE
    if _REFERENCE_SHORTS_CACHE is None:
        _REFERENCE_SHORTS_CACHE = {
            h: r.short for h, r in parse_src.parse_references().items() if r.short
        }
    return _REFERENCE_SHORTS_CACHE


_HANDLE_PATTERN = re.compile(r"(?<!!)\[([A-Za-z][A-Za-z0-9_-]*)\](?!\(|:|\[)")


def rewrite_reference_handles(text: str, current_page: str) -> str:
    """Rewrite reference-style `[Handle]` tokens to inline links pointing at
    the catalogue page (`references.md#<slug>`). Slugs are MkDocs's default
    lowercase-hyphenated slug from the catalogue h3 (handle).

    Skips:
    - tokens followed by `(` (already an inline link)
    - tokens followed by `:` (markdown reference-style link definition)
    - tokens followed by `[` (markdown reference-style link reference, rare)
    - inline code spans (handled by stripping `…` before scanning)
    - fenced code blocks
    - heading lines
    - the catalogue page itself (`references.md` is `current_page`); leaving
      catalogue cross-refs as plain `[Handle]` tokens that resolve via the
      h3 anchors on the same page would also work, but for now we just
      leave them untouched on the catalogue page.
    """
    if current_page == "references.md":
        return text
    handles = _reference_handles()
    if not handles:
        return text
    shorts = _reference_shorts()

    # Path from current_page to references.md (which lives at docs/ root).
    if "/" in current_page:
        target_prefix = "../references.md"
    else:
        target_prefix = "references.md"

    out_lines: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = "```" if stripped.startswith("```") else "~~~"
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            out_lines.append(line)
            continue
        if in_fence or line.startswith("#"):
            out_lines.append(line)
            continue

        # Inline-code-aware substitution: split the line on backtick spans,
        # only rewrite handles in the non-code segments.
        parts = re.split(r"(`[^`]*`)", line)
        for i, part in enumerate(parts):
            if i % 2 == 1:  # code span — leave untouched
                continue

            def sub(m: re.Match) -> str:
                handle = m.group(1)
                if handle not in handles:
                    return m.group(0)
                slug = handle.lower()
                label = shorts.get(handle, handle)
                return f"[{label}]({target_prefix}#{slug})"

            parts[i] = _HANDLE_PATTERN.sub(sub, part)
        out_lines.append("".join(parts))

    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")


def _metric_slug_to_page() -> dict[str, str]:
    """Build (and cache) a map from metric slug (e.g. "tp-ac-1", "hl-hf-3a")
    to the docs page that hosts that metric (e.g. "groups/audio-capture.md").
    Used to rewrite cross-page bare anchors during the per-page sweep.
    """
    global _METRIC_SLUG_TO_PAGE_CACHE
    if _METRIC_SLUG_TO_PAGE_CACHE is not None:
        return _METRIC_SLUG_TO_PAGE_CACHE
    idx: dict[str, str] = {}
    for m in parse_src.parse_all_metrics():
        slug = parse_src.ref_id_to_anchor(m.ref_id)
        page = SRC_GROUP_FILE_TO_PAGE.get(m.group_file)
        if page is not None:
            idx[slug] = page
    _METRIC_SLUG_TO_PAGE_CACHE = idx
    return idx


def rewrite_anchors(text: str, current_page: str) -> str:
    """Rewrite `[text](#slug)` links where `#slug` targets a section that
    has moved to another page in the site. Same-page anchors are left
    untouched.

    Two layered passes:
    1. ANCHOR_REWRITES — hand-curated section-level slugs (cross-cutting
       principles, group landings, standards-mapping sections).
    2. Metric ref-id slugs — `#tp-ac-1`, `#gv-vt-13`, `#hl-hf-3a` resolved
       against the parsed catalogue. If the metric lives on a different
       group page than the current one, rewrite to `<page>.md#slug`. If on
       the same page, leave bare.
    """

    metric_pages = _metric_slug_to_page()

    def sub(m: re.Match) -> str:
        label, slug = m.group(1), m.group(2)
        target = ANCHOR_REWRITES.get(slug)
        if target is None:
            metric_page = metric_pages.get(slug)
            if metric_page is None:
                return m.group(0)  # genuine same-page anchor
            # Same-page metric — leave bare.
            if metric_page == current_page:
                return m.group(0)
            # Cross-page metric — rewrite. Compute relative path from
            # current_page (e.g. "groups/operational.md") to the target
            # (e.g. "groups/safety-governance.md"). Both live in groups/,
            # so the relative path is just the basename.
            if "/" in current_page and metric_page.startswith("groups/"):
                rel = metric_page.split("/", 1)[1]
            else:
                rel = metric_page
            return f"[{label}]({rel}#{slug})"
        # Don't self-redirect if the current page is the target.
        if target.split("#", 1)[0] == current_page:
            return m.group(0)
        # If we're on a group page and the target lives at docs root,
        # prefix `../` so MkDocs can resolve.
        if "/" in current_page and "/" not in target:
            return f"[{label}](../{target})"
        return f"[{label}]({target})"

    return _MD_LINK.sub(sub, text)


# Bare ref-ID matcher used by link_bare_ref_ids. Catches both the standard
# form (TP.AC-1) and the sub-part form (HL.HF-3a). Cluster prefix is 2-3
# letters; group prefix is 2-3 alphanumeric chars; integer; optional
# single-letter sub-part suffix.
_BARE_REF_ID_RE = re.compile(r"\b([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+[a-z]?)\b")

# Markdown link / inline-code / fenced-code matchers used to mask out
# regions where bare ref-IDs must NOT be linkified.
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_EXISTING_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")


def link_bare_ref_ids(text: str, current_page: str) -> str:
    """Turn bare ref-IDs in prose into links to the metric's page.

    Standards-mapping, applicability, responsible-AI-lens and similar
    cross-cutting pages refer to metrics by ref-ID in plain text (e.g.
    "GV.CR-6 Clinical Safety Case Completeness"). Without this pass,
    those ref-IDs render as ordinary text — the reader can't click
    through to the metric definition. Group pages already inject anchors
    via add_metric_anchors and link cross-page anchors via
    rewrite_anchors, so the bare-ref-ID surface is concentrated on
    cross-cutting pages.

    Skips:
    - Already-formed markdown links `[…](…)` (so we don't double-wrap).
    - Inline code spans `` `TP.AC-1` `` (typed as code on purpose).
    - Fenced code blocks (Formal Definition pseudocode etc.).
    - Same-page ref-IDs (link target equals current page → leave bare).
    - Ref-IDs that don't resolve to a real metric (retired/reserved
      slots; let the audit flag those separately).

    The current_page argument is the rendered docs path (e.g.
    "standards-mapping.md") used to compute relative paths to group
    pages and to suppress self-redirects.
    """

    metric_pages = _metric_slug_to_page()

    def _link_ref_in_segment(segment: str) -> str:
        """Substitute bare ref-IDs in a segment with no fenced/inline code
        and no existing markdown links."""

        def sub(m: re.Match) -> str:
            ref_id = m.group(1)
            slug = parse_src.ref_id_to_anchor(ref_id)
            metric_page = metric_pages.get(slug)
            if metric_page is None:
                return m.group(0)  # retired/reserved or typo — leave bare
            if metric_page == current_page:
                return m.group(0)  # same-page — leave bare
            # Compute relative path. Cross-cutting pages live at docs
            # root; group pages live under groups/. Standards-mapping
            # and friends are at the root, so the rel path is just the
            # full metric_page (e.g. "groups/clinical-coding.md").
            if "/" in current_page and metric_page.startswith("groups/"):
                rel = metric_page.split("/", 1)[1]
            else:
                rel = metric_page
            return f"[{ref_id}]({rel}#{slug})"

        return _BARE_REF_ID_RE.sub(sub, segment)

    # Mask out regions where bare ref-IDs must not be touched, run the
    # substitution on the surviving prose, then restore the masked
    # regions verbatim. Order matters: fenced code first (greediest),
    # then existing links, then inline code.
    placeholders: list[str] = []

    def _mask(pattern: re.Pattern, raw: str) -> str:
        def sub(m: re.Match) -> str:
            placeholders.append(m.group(0))
            return f"\x00MASK{len(placeholders) - 1}\x00"

        return pattern.sub(sub, raw)

    masked = _mask(_FENCED_CODE_RE, text)
    masked = _mask(_EXISTING_LINK_RE, masked)
    masked = _mask(_INLINE_CODE_RE, masked)
    linked = _link_ref_in_segment(masked)

    # Restore.
    def _unmask_sub(m: re.Match) -> str:
        return placeholders[int(m.group(1))]

    return re.sub(r"\x00MASK(\d+)\x00", _unmask_sub, linked)


# Hand-written cluster titles keyed by cluster code, used as the eyebrow
# heading on each group page. v4.0 retired the v3.x "Part X - …" prefix
# in favour of the cluster-code form "TP — Technical Pipeline".
CLUSTER_TITLES = {
    code: f"{code} — {name}" for code, name in parse_src.CLUSTER_NAMES.items()
}


def _cluster_title_for_group_file(src_rel: str) -> str | None:
    """Look up the cluster title for a source group file, via the parser's
    canonical group list. Returns None for non-group files."""
    info = parse_src.GROUP_FILES.get(src_rel)
    if info is None:
        return None
    return CLUSTER_TITLES.get(info["cluster"])


def promote_h2_to_h1(text: str, src_rel: str | None = None) -> str:
    """Reshape a source file so MkDocs gets exactly one h1 at the top,
    with a consistent shape on every group page.

    Group files have two source shapes:
    - `# Part X - Name` then later `## Group` (the first file per part)
    - `## Group` only (every other file in that part)

    In both cases we want the rendered page to start identically:
        # Group Name
        *Part X - Name*     (italic kicker)
        *Original intro*    (the group's italic intro from source)

    Non-group files (underscore-prefixed cross-cutting pages) just have
    their `## Heading` promoted to `# Heading`.
    """
    lines = text.splitlines()
    # Find first non-empty line
    first_idx = None
    for i, line in enumerate(lines):
        if line.strip():
            first_idx = i
            break
    if first_idx is None:
        return text

    first = lines[first_idx].strip()

    # For every group file, emit header in eyebrow / title / dek order:
    #   *Part X - Name*    (kicker, styled as right-aligned eyebrow in CSS)
    #   # Group Name
    #   *Original intro*   (kept from source)
    # This lets the H1 and its description read as one unit, with the part
    # label as a small breadcrumb-style eyebrow above.

    # Case A: group file with explicit `# Part X - ...` heading.
    if first.startswith("# Part ") and " - " in first:
        part_title = first[2:].strip()
        for j in range(first_idx + 1, len(lines)):
            s = lines[j].strip()
            if s.startswith("## ") and not s.startswith("### "):
                group_title = s[3:].strip()
                kicker = f"*{part_title}*"
                new_head = [kicker, "", f"# {group_title}", ""]
                lines = lines[:first_idx] + new_head + lines[j + 1 :]
                break
        return "\n".join(lines) + ("\n" if not text.endswith("\n") else "")

    # Case B: group file without a Part heading - inject the kicker from
    # the canonical cluster title lookup so every group page starts the same.
    if first.startswith("## ") and src_rel is not None:
        part_title = _cluster_title_for_group_file(src_rel)
        if part_title is not None:
            group_title = first[3:].strip()
            kicker = f"*{part_title}*"
            new_head = [kicker, "", f"# {group_title}", ""]
            lines = lines[:first_idx] + new_head + lines[first_idx + 1 :]
            return "\n".join(lines) + ("\n" if not text.endswith("\n") else "")

    # Case C: cross-cutting file starting with `## Heading` - promote to `# Heading`.
    if first.startswith("## "):
        lines[first_idx] = "# " + first[3:]
    return "\n".join(lines) + ("\n" if not text.endswith("\n") else "")


_TEMPLATE_TOKENS = {
    "{{TAXONOMY_VERSION}}": parse_src.TAXONOMY_VERSION,
    "{{TAXONOMY_DATE}}": parse_src.TAXONOMY_DATE,
}


def _substitute_template_tokens(text: str) -> str:
    """Replace `{{TAXONOMY_VERSION}}` / `{{TAXONOMY_DATE}}` in source files
    so version stamps stay live across the monolith, the rendered site, and
    every per-page banner. Single source of truth = parse.TAXONOMY_VERSION.
    """
    for token, value in _TEMPLATE_TOKENS.items():
        text = text.replace(token, value)
    return text


def _build_metric_history_page() -> str:
    """Generate docs/metric-history.md from git tag history.

    For each tag (newest first), list the metric group files that changed
    between the previous tag and this one, with the metrics living in those
    files. Coarse but mechanical — knows that a file changed, not what
    changed semantically. Pairs with the optional **Change history:** stanza
    on individual metrics that flag substantive fixes worth reader attention.
    """
    try:
        tags_out = subprocess.check_output(
            ["git", "tag", "--list", "v*", "--sort=-v:refname"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return _metric_history_stub("git unavailable")
    tags = [t.strip() for t in tags_out.splitlines() if t.strip()]
    if not tags:
        return _metric_history_stub("no tags found")

    # Walk tag pairs from newest → oldest
    lines: list[str] = [
        "# Metric history",
        "",
        "Auto-generated from git tag history at build time. Each release lists "
        "the metric group files that changed between the previous tag and the "
        "release tag. Coarse — file-level only — but mechanical and exhaustive. "
        "Pair with each metric's optional **Change history:** stanza for "
        "reader-flagged substantive changes.",
        "",
        "See [Versioning](versioning.md) for what each release-version digit means.",
        "",
    ]
    metric_index = parse_src.parse_all_metrics()
    metrics_by_file: dict[str, list] = defaultdict(list)
    for m in metric_index:
        metrics_by_file[m.group_file].append(m)

    pairs = list(zip(tags, tags[1:] + [None]))
    for newer, older in pairs:
        if older is None:
            range_spec = newer  # initial release; show all metric files
            range_label = f"`{newer}` (initial release at this tag)"
        else:
            range_spec = f"{older}..{newer}"
            range_label = f"`{older}` → `{newer}`"
        try:
            diff_out = subprocess.check_output(
                ["git", "diff", "--name-only", range_spec, "--", "taxonomy/"],
                cwd=REPO,
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        changed = sorted(
            f
            for f in diff_out.splitlines()
            if f.startswith("taxonomy/") and f.endswith(".md")
        )
        # Filter to group files (those that contain metrics) — exclude
        # _-prefixed cross-cutting files and the catalogue
        group_changes = [f for f in changed if not pathlib.Path(f).name.startswith("_")]
        catalogue_changed = "taxonomy/_references.md" in changed
        crosscut_changes = [
            f
            for f in changed
            if pathlib.Path(f).name.startswith("_")
            and pathlib.Path(f).name != "_references.md"
        ]

        lines.append(f"## {range_label}")
        if not (group_changes or catalogue_changed or crosscut_changes):
            lines.append("")
            lines.append("_No taxonomy content changed (site / tooling release)._")
            lines.append("")
            continue
        if group_changes:
            lines.append("")
            lines.append("**Metric files changed:**")
            lines.append("")
            for f in group_changes:
                rel = f[len("taxonomy/") :]
                metrics = metrics_by_file.get(rel, [])
                names = ", ".join(m.ref_id for m in metrics) if metrics else "—"
                lines.append(f"- `{rel}` — {len(metrics)} metric(s): {names}")
            lines.append("")
        if catalogue_changed:
            lines.append("**Catalogue (`_references.md`) changed.**")
            lines.append("")
        if crosscut_changes:
            lines.append("**Cross-cutting / framework files changed:**")
            lines.append("")
            for f in crosscut_changes:
                lines.append(f"- `{f[len('taxonomy/') :]}`")
            lines.append("")
    return "\n".join(lines)


def _metric_history_stub(reason: str) -> str:
    return (
        "# Metric history\n\n"
        f"_Metric history page could not be generated: {reason}._\n\n"
        "Auto-generated from git tag history at site-build time. See "
        "[Versioning](versioning.md) for the release-version conventions.\n"
    )


def _git_dates_for(rel_path: str) -> tuple[str, str] | None:
    """Return (created, updated) ISO dates from git history for a repo file.
    Returns None if git is unavailable or the file has no git history.
    Used to populate front-matter on generated docs/ pages so the RSS
    plugin can produce valid feed entries from generated content.
    """
    try:
        created = (
            subprocess.check_output(
                ["git", "log", "--reverse", "--format=%aI", "--", rel_path],
                cwd=REPO,
                text=True,
                stderr=subprocess.DEVNULL,
            )
            .strip()
            .split("\n")[0]
        )
        updated = subprocess.check_output(
            ["git", "log", "-1", "--format=%aI", "--", rel_path],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not created or not updated:
        return None
    return (created, updated)


def _inject_changelog_dates_frontmatter(text: str) -> str:
    """Prepend YAML front-matter to the changelog page text with `date.created`
    and `date.updated` derived from the source `CHANGELOG.md`'s git history.
    The mkdocs-rss-plugin reads these fields to build feed entries — without
    them it warns 'Dates could not be retrieved' because docs/changelog.md
    is generated by build_site.py rather than git-tracked.
    """
    dates = _git_dates_for("CHANGELOG.md")
    if dates is None:
        return text
    created, updated = dates
    frontmatter = f"---\ndate:\n  created: {created}\n  updated: {updated}\n---\n\n"
    return frontmatter + text


def _refresh_announce_banner() -> None:
    """Rewrite the site-wide announce banner in overrides/main.html with the
    current version. The banner is pre-existing Jinja but mkdocs-material's
    template context doesn't expose our SITE_VERSION easily, so we treat the
    file as a build artefact: rebuilt every run with the live version baked
    in. Keeps the banner in sync with TAXONOMY_VERSION without a manual bump.
    """
    overrides = REPO / "overrides" / "main.html"
    if not overrides.exists():
        return
    content = (
        '{% extends "base.html" %}\n'
        "\n"
        "{% block announce %}\n"
        f"  <strong>AI-coauthored prototype for discussion — {SITE_VERSION}.</strong> "
        "Substantial portions of this taxonomy were drafted with AI assistance and "
        "human-reviewed; <strong>specific claims, citations, and threshold numbers may "
        "still contain confabulations or factual errors</strong> despite review. Keep "
        "this front of mind, verify before use, and please flag anything that looks "
        "wrong — feedback on errors is genuinely welcome. This is shared to provoke "
        "conversation, not as a settled standard or procurement gate. See the\n"
        "  <a href=\"{{ 'prototype-status/' | url }}\" style=\"color: inherit; text-decoration: underline;\">prototype status</a> page for what you're invited to do (and what you shouldn't), the\n"
        '  <a href="{{ \'changelog/\' | url }}" style="color: inherit; text-decoration: underline;">changelog</a> for recent changes, and the\n'
        '  <a href="{{ \'gaps/\' | url }}" style="color: inherit; text-decoration: underline;">roadmap</a> for what\'s pending.\n'
        "{% endblock %}\n"
    )
    overrides.write_text(content)


def main() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    (DOCS / "groups").mkdir()

    _refresh_announce_banner()

    for src_rel, dst_rel in MAPPING.items():
        src = ROOT / src_rel
        dst = DOCS / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = _substitute_template_tokens(src.read_text())
        if src_rel == "_references.md":
            text = parse_src.populate_cited_by(text)
        text = rewrite_anchors(text, dst_rel)
        text = rewrite_reference_handles(text, dst_rel)
        text = rewrite_external_links(text)
        text = add_metric_anchors(text)
        # Linkify bare ref-IDs in cross-cutting prose (standards-mapping,
        # applicability, responsible-AI-lens etc.). Group pages already
        # have anchors injected via add_metric_anchors and so don't need
        # the same pass — bare ref-IDs there typically belong to the
        # current page's metrics.
        # Skip link_bare_ref_ids on thresholds.md: that page uses ref-IDs
        # in headings as anchors (e.g. `#### GV.VT-15`) so the slugify-from-
        # heading mechanism produces clean per-metric anchors that the metric
        # bodies link back to. Linkifying the headings would slugify them as
        # `gv-vt-15-retirement-notification-compliance` instead, breaking
        # the round-trip.
        if not dst_rel.startswith("groups/") and dst_rel != "thresholds.md":
            text = link_bare_ref_ids(text, dst_rel)
            # Linkify metric names inside markdown table cells (standards
            # mapping, applicability, RAI lens etc.). Skip the Tier-1
            # quick reference because its bolded names are handled
            # separately by `link_tier1_quickref`.
            if dst_rel != "tier-1-quick-reference.md":
                text = link_metric_names_in_tables(text)
        if dst_rel == "tier-1-quick-reference.md":
            text = link_tier1_quickref(text)
            text = regroup_tier1_tables_by_cluster(text)
        if dst_rel == "gaps.md":
            text = _inject_roadmap_prelude(text)
        if dst_rel == "contents.md":
            text = _inject_contents_applicability_row(text)
        if dst_rel.startswith("groups/"):
            text = _add_applicability_badges(text, dst_rel)
            text = _add_related_metrics_footers(text, dst_rel)
            text = _add_feedback_footer(text)
        if dst_rel == "index.md":
            # Root index page - replace the source h1 and the repeated
            # summary prose with a concise landing block; keep the source's
            # "Acknowledgements / Sources / Structure" content below the
            # new jumping-off section.
            promoted = promote_h2_to_h1(text, src_rel)
            promoted_lines = promoted.splitlines()
            if promoted_lines and promoted_lines[0].startswith("# "):
                promoted_lines = promoted_lines[1:]
            while promoted_lines and not promoted_lines[0].strip():
                promoted_lines = promoted_lines[1:]
            promoted = "\n".join(promoted_lines)
            text = _landing_page(promoted)
        else:
            text = promote_h2_to_h1(text, src_rel)
            # Icon legend collapsible — lives on pages where tier + cadence
            # emoji appear densely; injected after promote_h2_to_h1 so the
            # h1 and Part kicker are already in place on group pages.
            text = inject_legend(text, dst_rel)
        dst.write_text(text)

    # Changelog at repo root is already Markdown - copy with link rewrites
    # so any `[X](README.md)` / `[X](archive/...)` references resolve in
    # the rendered site.
    cl_src = REPO / "CHANGELOG.md"
    if cl_src.exists():
        cl_text = cl_src.read_text()
        cl_text = rewrite_anchors(cl_text, "changelog.md")
        cl_text = rewrite_reference_handles(cl_text, "changelog.md")
        cl_text = rewrite_external_links(cl_text)
        cl_text = link_bare_ref_ids(cl_text, "changelog.md")
        cl_text = _inject_changelog_dates_frontmatter(cl_text)
        (DOCS / "changelog.md").write_text(cl_text)

    # Downloads landing page - links resolve in CI where dist/* is copied
    # into docs/downloads/ before mkdocs build (see .github/workflows/site.yml).
    # For local preview, also mirror dist/* into docs/downloads/ here so
    # `mkdocs serve` shows the downloads as working links.
    (DOCS / "downloads.md").write_text(_downloads_page())
    (DOCS / "metric-history.md").write_text(_build_metric_history_page())
    _mirror_downloads()
    _copy_stylesheets()
    _copy_javascripts()

    # Cross-cut auto-generated pages (applicability / principle / theme).
    crosscut_count = build_crosscuts()

    print(
        f"Populated {DOCS.relative_to(REPO)} with {len(MAPPING) + 2 + crosscut_count} pages."
    )


def _copy_stylesheets() -> None:
    """Copy taxonomy/stylesheets/*.css into docs/stylesheets/.
    docs/ is gitignored, so this has to run every build."""
    src = ROOT / "stylesheets"
    if not src.exists():
        return
    dest = DOCS / "stylesheets"
    dest.mkdir(exist_ok=True)
    for css in src.glob("*.css"):
        shutil.copy2(css, dest / css.name)


def _copy_javascripts() -> None:
    """Copy taxonomy/javascripts/*.js into docs/javascripts/."""
    src = ROOT / "javascripts"
    if not src.exists():
        return
    dest = DOCS / "javascripts"
    dest.mkdir(exist_ok=True)
    for js in src.glob("*.js"):
        shutil.copy2(js, dest / js.name)


def _mirror_downloads() -> None:
    dist = REPO / "dist"
    if not dist.exists():
        return  # build.py hasn't been run; skip
    target = DOCS / "downloads"
    target.mkdir(exist_ok=True)
    for name in ("metrics.csv", "metrics.json", "gaps.json", "summary.json"):
        src = dist / name
        if src.exists():
            shutil.copy2(src, target / name)
    # Copy the monolithic MD for local preview parity with CI - but with
    # a `.txt` extension so MkDocs doesn't treat it as a page source.
    # The Downloads page link carries `download="avt-metrics-taxonomy.md"`
    # so browsers save it with the expected filename.
    md_src = REPO / "avt-metrics-taxonomy.md"
    if md_src.exists():
        shutil.copy2(md_src, target / "avt-metrics-taxonomy.txt")


# ---------------------------------------------------------------------------
# Cross-cut auto-generated pages
#
# Generates pages under docs/crosscuts/ from parsed source:
#   - by-applicability/avt-specific.md, avt-contextualised.md, general.md
#   - by-principle/p1.md … p10.md
#   - by-theme/t1.md … t6.md
# Per-standard cross-cut pages are deferred - standards-mapping tables have
# heterogeneous shapes per standard; needs a dedicated extractor round.
# ---------------------------------------------------------------------------

CROSSCUT_DIR = "crosscuts"

# Short labels that match the left-nav hand-written names in mkdocs.yml,
# used wherever we link to a principle/theme page (index, landing, per-metric
# references). Kept in one place so a nav rename stays in sync.
PRINCIPLE_SHORT = {
    "P1": "P1 - Limitations",
    "P2": "P2 - Lawful/ethical",
    "P3": "P3 - Security",
    "P4": "P4 - Human control",
    "P5": "P5 - Lifecycle",
    "P6": "P6 - Right tool",
    "P7": "P7 - Openness",
    "P8": "P8 - Commercial",
    "P9": "P9 - Skills",
    "P10": "P10 - Org assurance",
}

THEME_SHORT = {
    "T1": "T1 - Safety, Security, Robustness",
    "T2": "T2 - Transparency & Explainability",
    "T3": "T3 - Fairness",
    "T4": "T4 - Accountability & Governance",
    "T5": "T5 - Contestability & Redress",
    "T6": "T6 - Societal Wellbeing",
}

SRC_GROUP_FILE_TO_PAGE = {
    "tp/audio-capture.md": "groups/audio-capture.md",
    "tp/asr-transcription.md": "groups/asr-transcription.md",
    "tp/diarisation.md": "groups/diarisation.md",
    "tp/summarisation-nlp.md": "groups/summarisation-nlp.md",
    "tp/clinical-coding.md": "groups/clinical-coding.md",
    "tp/downstream-write-back.md": "groups/downstream-write-back.md",
    "pi/partial-pipeline.md": "groups/partial-pipeline.md",
    "pi/end-to-end-pipeline.md": "groups/end-to-end-pipeline.md",
    "hl/human-factors-workflow.md": "groups/human-factors-workflow.md",
    "io/patient-experience.md": "groups/patient-experience.md",
    "io/fairness-equity.md": "groups/fairness-equity.md",
    "gv/safety-governance.md": "groups/safety-governance.md",
    "gv/nhs-compliance-regulatory.md": "groups/nhs-compliance-regulatory.md",
    "gv/security-adversarial-robustness.md": "groups/security-adversarial-robustness.md",
    "gv/privacy-data-governance.md": "groups/privacy-data-governance.md",
    "gv/operational.md": "groups/operational.md",
    "gv/environmental-sustainability.md": "groups/environmental-sustainability.md",
    "gv/training-competency.md": "groups/training-competency.md",
    "gv/vendor-transparency-contractual.md": "groups/vendor-transparency-contractual.md",
    "es/meta-evaluation.md": "groups/meta-evaluation.md",
}


def _metric_page_link(ref_id: str, name: str, group_file: str) -> str:
    """Return a Markdown link like [name](../groups/<group>.md#tp-ac-1)."""
    slug = parse_src.ref_id_to_anchor(ref_id)
    page = SRC_GROUP_FILE_TO_PAGE.get(group_file, "")
    if not page:
        return name
    # From crosscuts/by-X/page.md, the group pages are at ../../groups/*.md.
    # Use Markdown-style .md#slug path so MkDocs validates and rewrites it.
    return f"[{name}](../../{page}#{slug})"


def _tier_icon(t: int) -> str:
    return {1: "🟢", 2: "🟡", 3: "🔵"}[t]


def _crosscut_index_page(
    applicability_counts: dict[str, int],
    principle_counts: dict[str, int],
    theme_counts: dict[str, int],
    standards: dict[str, dict] | None = None,
) -> str:
    lines = [
        "# Catalogue views",
        "",
        f"Auto-generated views that slice the catalogue along three additional axes. "
        "Each view links back to individual metric pages - nothing here is authoritative, "
        "just a different way to read the same source.",
        "",
        "## By applicability",
        "",
        "Which metrics are AVT-specific vs transferable to any healthcare AI.",
        "",
    ]
    for label, path in (
        ("AVT-Specific", "by-applicability/avt-specific.md"),
        ("AVT-Contextualised", "by-applicability/avt-contextualised.md"),
        ("General Healthcare AI", "by-applicability/general.md"),
    ):
        count = applicability_counts.get(label, 0)
        lines.append(f"- [{label}]({path}) - {count} metrics")
    lines += [
        "",
        "## By DSIT AI Playbook principle",
        "",
        "The 10 Playbook principles that the taxonomy supports. Counts below include only "
        "metrics that genuinely operationalise the principle (not metrics that merely touch on it).",
        "",
    ]
    for code in sorted(principle_counts, key=lambda c: int(c[1:])):
        count = principle_counts[code]
        label = PRINCIPLE_SHORT.get(code, f"{code} - principle membership")
        lines.append(f"- [{label}](by-principle/{code.lower()}.md) - {count} metrics")
    lines += [
        "",
        "## By standard",
        "",
        "Auto-generated assertion-level pages for standards whose source "
        "tables map directly to metric IDs. Four additional standards "
        "(CQC, PSIRF, PRSB, Caldicott) use narrative prose rather than "
        "structured tables; they are summarised on the main "
        "[Standards Mapping](../standards-mapping.md) page.",
        "",
    ]
    if standards:
        for std, info in standards.items():
            total = sum(len(s.rows) for s in info["sections"])
            resolved = sum(len(r.metric_refs) for s in info["sections"] for r in s.rows)
            lines.append(
                f"- [{std}](by-standard/{info['code']}.md) - {total} assertions, {resolved} metric mappings"
            )
    lines += [
        "",
        "## By Responsible AI ethical theme",
        "",
        "Six cross-cutting themes from the Responsible AI literature, mapped to the metric catalogue.",
        "",
    ]
    for code in sorted(theme_counts, key=lambda c: int(c[1:])):
        count = theme_counts[code]
        label = THEME_SHORT.get(code, f"{code} - theme membership")
        lines.append(f"- [{label}](by-theme/{code.lower()}.md) - {count} metrics")
    lines.append("")
    return "\n".join(lines)


def _applicability_page(label: str, metrics: list) -> str:
    lines = [
        f"# Applicability: {label}",
        "",
        f"{len(metrics)} metrics classified as **{label}**.",
        "",
        "| Ref | Metric | Group | Tier |",
        "|-----|--------|-------|------|",
    ]
    for m in sorted(metrics, key=lambda x: (x.cluster, x.group, x.ref_id)):
        link = _metric_page_link(m.ref_id, m.name, m.group_file)
        lines.append(
            f"| {m.ref_id} | {link} | {m.group} | {_tier_icon(m.tier)} {m.tier} |"
        )
    lines.append("")
    return "\n".join(lines)


def _family_page(label: str, metrics: list) -> str:
    """Render the `crosscuts/by-family/<slug>.md` page listing family members."""
    lines = [
        f"# Family: {label}",
        "",
        f"{len(metrics)} metrics in this named family. Construct definition, "
        f"why-this-family rationale, and full framing prose live on the "
        f"canonical [Families page](../../families.md).",
        "",
        "| Ref | Metric | Group | Tier |",
        "|-----|--------|-------|------|",
    ]
    for m in sorted(metrics, key=lambda x: (x.cluster, x.group, x.ref_id)):
        link = _metric_page_link(m.ref_id, m.name, m.group_file)
        lines.append(
            f"| {m.ref_id} | {link} | {m.group} | {_tier_icon(m.tier)} {m.tier} |"
        )
    lines.append("")
    return "\n".join(lines)


def _ai_substrate_page(label: str, metrics: list) -> str:
    """Render the `crosscuts/by-ai-substrate/<slug>.md` page (v5.5.3+).

    AI-Substrate is a fully-derived classification (no per-metric
    field). The page is informational; `_ai-substrate.md` carries the
    construct definition and class-by-class rationale.
    """
    lines = [
        f"# AI-Substrate: {label}",
        "",
        f"{len(metrics)} metrics derived as **{label}** — see "
        f"[AI-Substrate](../../ai-substrate.md) for the five-class "
        f"framing and derivation rules. The classification is fully "
        f"derived from cluster + per-metric overrides at build time; "
        f"it is **not** a per-metric dimension on metric bodies.",
        "",
        "| Ref | Metric | Group | Tier |",
        "|-----|--------|-------|------|",
    ]
    for m in sorted(metrics, key=lambda x: (x.cluster, x.group, x.ref_id)):
        link = _metric_page_link(m.ref_id, m.name, m.group_file)
        lines.append(
            f"| {m.ref_id} | {link} | {m.group} | {_tier_icon(m.tier)} {m.tier} |"
        )
    lines.append("")
    return "\n".join(lines)


def _layer_page(label: str, metrics: list) -> str:
    """Render the `crosscuts/by-layer-of-defence/<slug>.md` page.

    As of v5.5.4, all 236 metrics carry an explicit per-metric `Layer`
    dimension (Prevention / Detection / Limitation). The cadence
    heuristic remains in `parse.derive_layer_of_defence` as a fallback
    for any future metric that lands without an explicit Layer, but
    the catalogue currently has 0 such cases.
    """
    lines = [
        f"# Layer of Defence: {label}",
        "",
        f"{len(metrics)} metrics serving the **{label}** layer — see "
        f"[Layers of Defence](../../layers-of-defence.md) for the framing "
        f"and the per-metric Layer dimension convention.",
        "",
        "| Ref | Metric | Group | Tier | Cadence |",
        "|-----|--------|-------|------|---------|",
    ]
    for m in sorted(metrics, key=lambda x: (x.cluster, x.group, x.ref_id)):
        link = _metric_page_link(m.ref_id, m.name, m.group_file)
        cadence = m.dimensions.get("Measurement Cadence", "")
        lines.append(
            f"| {m.ref_id} | {link} | {m.group} | {_tier_icon(m.tier)} {m.tier} | {cadence} |"
        )
    lines.append("")
    return "\n".join(lines)


def _principle_or_theme_page(kind: str, code: str, label: str, entries: list) -> str:
    header = "Playbook principle" if kind == "principle" else "Ethical theme"
    lines = [
        f"# {header} {code}: {label}",
        "",
        f"{len(entries)} metrics operationalise this {kind}. Each entry links to the metric's full definition on its group page.",
        "",
        "| Ref | Metric | Group | Tier | Aspect |",
        "|-----|--------|-------|------|--------|",
    ]
    # Resolve ref_id -> group_file via a quick lookup through parsed metrics.
    all_metrics = parse_src.parse_all_metrics()
    ref_to_group_file = {m.ref_id: m.group_file for m in all_metrics}
    for e in entries:
        gf = ref_to_group_file.get(e.ref_id, "")
        link = _metric_page_link(e.ref_id, e.name, gf) if gf else e.name
        lines.append(
            f"| {e.ref_id} | {link} | {e.group} | {e.tier_icon} | {e.aspect} |"
        )
    lines.append("")
    return "\n".join(lines)


def _standard_page(standard: str, sections: list) -> str:
    lines = [f"# Coverage: {standard}", ""]
    lines.append(
        f"Assertion-level mapping of this standard to the metric catalogue. "
        f"Each metric link jumps to the full definition on its group page. "
        f"See the full [Standards Mapping](../../standards-mapping.md) for "
        f"overview, publisher, and scope of this standard."
    )
    lines.append("")
    ref_to_group_file = {m.ref_id: m.group_file for m in parse_src.parse_all_metrics()}
    for section in sections:
        if section.subsection:
            lines.append(f"## {section.subsection}")
            lines.append("")
        lines.append("| Criterion | Description | Metrics | Tier |")
        lines.append("|-----------|-------------|---------|------|")
        for row in section.rows:
            metric_md = _render_metric_refs(
                row.metric_refs, row.metric_names, ref_to_group_file
            )
            lines.append(
                f"| {row.criterion} | {row.description} | {metric_md} | {row.tier_cell or '-'} |"
            )
        lines.append("")
    return "\n".join(lines)


def _render_metric_refs(
    ref_ids: list[str], names: list[str], ref_to_group_file: dict
) -> str:
    if not ref_ids and not names:
        return "*Process criterion - no metric equivalent*"
    parts: list[str] = []
    # Walk ref_ids in order, falling back to names that didn't resolve.
    seen = set()
    for rid in ref_ids:
        if rid in seen:
            continue
        seen.add(rid)
        gf = ref_to_group_file.get(rid, "")
        if gf:
            slug = rid.lower().replace(".", "-")
            page = SRC_GROUP_FILE_TO_PAGE.get(gf, "")
            # Find the metric's display name
            display = None
            for name, hit in parse_src._name_to_metric_idx().items():
                if hit.ref_id == rid and name == hit.name:
                    display = name
                    break
            display = display or rid
            if page:
                parts.append(f"[{rid} {display}](../../{page}#{slug})")
            else:
                parts.append(f"{rid} {display}")
        else:
            parts.append(rid)
    # Any unresolved textual names
    for name in names:
        if name in seen:
            continue
        # Skip names we already resolved by ref
        already = any(name in p for p in parts)
        if already:
            continue
        parts.append(f"*{name}*")
    return "<br>".join(parts)  # <br> keeps cells readable inside Markdown tables


def build_crosscuts() -> int:
    """Emit applicability / principle / theme cross-cut pages. Returns page count.

    Parents (with sub-parts; v3.7+) are excluded from these aggregations —
    they carry construct framing only, no applicability dimension, and
    would land in 'Unclassified' if included. Sub-parts and flat metrics
    are the unit of measurement and the unit of cross-cutting membership.
    """
    all_metrics = parse_src.annotate_applicability(parse_src.parse_all_metrics())
    parent_ids = {
        sp.parent_ref_id for sp in all_metrics if sp.parent_ref_id is not None
    }
    metrics = [m for m in all_metrics if m.ref_id not in parent_ids]
    apps = parse_src.group_metrics_by_applicability(metrics)
    families = parse_src.group_metrics_by_family(metrics)
    layers = parse_src.group_metrics_by_layer_of_defence(metrics)
    substrates = parse_src.group_metrics_by_ai_substrate(metrics)
    principles = parse_src.parse_rai_principle_membership()
    themes = parse_src.parse_rai_theme_membership()

    base = DOCS / CROSSCUT_DIR
    (base / "by-applicability").mkdir(parents=True, exist_ok=True)
    (base / "by-family").mkdir(parents=True, exist_ok=True)
    (base / "by-layer-of-defence").mkdir(parents=True, exist_ok=True)
    (base / "by-ai-substrate").mkdir(parents=True, exist_ok=True)
    (base / "by-principle").mkdir(parents=True, exist_ok=True)
    (base / "by-theme").mkdir(parents=True, exist_ok=True)
    (base / "by-standard").mkdir(parents=True, exist_ok=True)

    # Per-standard pages (only those with table-based assertion mappings).
    standards = parse_src.parse_standards_grouped()
    for standard, info in standards.items():
        (base / "by-standard" / f"{info['code']}.md").write_text(
            _standard_page(standard, info["sections"])
        )

    # Index page for the section
    (base / "index.md").write_text(
        _crosscut_index_page(
            applicability_counts={k: len(v) for k, v in apps.items()},
            principle_counts={k: len(v) for k, (_, v) in principles.items()},
            theme_counts={k: len(v) for k, (_, v) in themes.items()},
            standards=standards,
        )
    )

    # Applicability pages
    applicability_slugs = {
        "AVT-Specific": "avt-specific.md",
        "AVT-Contextualised": "avt-contextualised.md",
        "General Healthcare AI": "general.md",
    }
    for label, slug in applicability_slugs.items():
        if label in apps:
            (base / "by-applicability" / slug).write_text(
                _applicability_page(label, apps[label])
            )

    # Principle pages
    for code, (name, entries) in principles.items():
        (base / "by-principle" / f"{code.lower()}.md").write_text(
            _principle_or_theme_page("principle", code, name, entries)
        )

    # Theme pages
    for code, (name, entries) in themes.items():
        (base / "by-theme" / f"{code.lower()}.md").write_text(
            _principle_or_theme_page("theme", code, name, entries)
        )

    # Family pages (v5.5.0+)
    def _slugify(s: str) -> str:
        import re as _re

        return _re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

    for label, fam_metrics in families.items():
        (base / "by-family" / f"{_slugify(label)}.md").write_text(
            _family_page(label, fam_metrics)
        )

    # Layer-of-defence pages (v5.5.0+; explicit + heuristic)
    for label, layer_metrics in layers.items():
        (base / "by-layer-of-defence" / f"{label.lower()}.md").write_text(
            _layer_page(label, layer_metrics)
        )

    # AI-substrate pages (v5.5.3+; fully derived)
    for label, sub_metrics in substrates.items():
        (base / "by-ai-substrate" / f"{_slugify(label)}.md").write_text(
            _ai_substrate_page(label, sub_metrics)
        )

    total = (
        1
        + len(applicability_slugs)
        + len(families)
        + len(layers)
        + len(substrates)
        + len(principles)
        + len(themes)
        + len(standards)
    )
    print(f"Generated {total} crosscut pages under docs/{CROSSCUT_DIR}/.")
    return total


_APPLICABILITY_BADGES = {
    "AVT-Specific": ("🎯", "avt-specific.md"),
    "AVT-Contextualised": ("🔀", "avt-contextualised.md"),
    "General Healthcare AI": ("🌐", "general.md"),
}


def _legend_block(how_to_use_link: str) -> str:
    return (
        "\n"
        '??? note "Legend: tier and cadence icons"\n'
        "    **Priority tier** (leading dot in each metric heading):\n\n"
        "    - 🟢 **Tier 1** - Minimum viable assurance (measurable today with existing tools)\n"
        "    - 🟡 **Tier 2** - Recommended for any AVT deployment\n"
        "    - 🔵 **Tier 3** - Advanced / research-grade\n\n"
        "    **Measurement cadence** (used in the Tier 1 quick-reference bullets):\n\n"
        "    - 🚪 **One-off gate** - measured once pre-deployment as an acceptance criterion\n"
        "    - 📡 **Continuous** - automated, ongoing measurement during operational use\n"
        "    - 🔄 **Periodic audit** - scheduled assessment (quarterly / annual)\n\n"
        "    **Other flags:**\n\n"
        "    - ⚠️ Metric carries an underspecification warning - see the full entry for measurement-science caveats\n\n"
        f"    See [How to use]({how_to_use_link}) for the full definitions.\n"
        "\n"
    )


def _insert_after_h1(text: str, block: str) -> str:
    """Insert a block below the page's header region, which is:
        [optional italic eyebrow/kicker paragraph]
        # H1
        [optional italic intro paragraph]

    Positions the insertion after the final piece of that header so the
    inserted block (the legend) lands below the orientation content
    rather than interrupting it.
    """
    lines = text.splitlines()

    # Skip any leading eyebrow/kicker italic paragraph and its blanks
    # before we look for the h1.
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if (
        i < len(lines)
        and lines[i].startswith("*")
        and lines[i].rstrip().endswith("*")
        and not lines[i].startswith("# ")
    ):
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1

    # Find h1
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    if i == len(lines):
        return text  # no h1 found; leave alone
    # Skip the h1 line and any blank
    i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    # Skip any number of single-line italic paragraphs (e.g. intro) and
    # their trailing blank lines.
    while (
        i < len(lines) and lines[i].startswith("*") and lines[i].rstrip().endswith("*")
    ):
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
    return (
        "\n".join(lines[:i])
        + "\n"
        + block
        + "\n".join(lines[i:])
        + ("\n" if not text.endswith("\n") else "")
    )


def inject_legend(text: str, current_page: str) -> str:
    """Add a collapsible legend explaining tier and cadence icons to pages
    where those icons appear densely (group pages + the Tier-1 quickref).
    Uses a `???` collapsible admonition so it stays out of the way until a
    reader needs it."""
    if current_page.startswith("groups/"):
        return _insert_after_h1(text, _legend_block("../how-to-use.md"))
    if current_page == "tier-1-quick-reference.md":
        return _insert_after_h1(text, _legend_block("how-to-use.md"))
    return text


def _add_applicability_badges(text: str, current_page: str) -> str:
    """Inject a compact applicability badge after each metric's dimensions
    table on a group page. The badge is a single line:
        **Applicability:** 🎯 [AVT-Specific](../crosscuts/by-applicability/avt-specific.md)
    Inserted immediately after the closing row of the dimensions table (the
    line before the next blank-line-separated section).
    """
    if not current_page.startswith("groups/"):
        return text
    applicability_idx = parse_src.parse_applicability()

    # Split the doc into metric segments by ### Ref-ID heading (same regex
    # as add_metric_anchors, after anchor injection).
    heading_re = re.compile(
        r"^(###\s+([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+)\s+[🟢🟡🔵]\s+.+?)\s+\{\s*#[a-z0-9-]+\s*\}\s*$"
    )
    lines = text.splitlines()

    # Identify metric heading line numbers.
    metric_bounds: list[tuple[int, int, str]] = []
    indices = [i for i, line in enumerate(lines) if heading_re.match(line)]
    for k, start in enumerate(indices):
        end = indices[k + 1] if k + 1 < len(indices) else len(lines)
        ref_id = heading_re.match(lines[start]).group(2)
        metric_bounds.append((start, end, ref_id))

    if not metric_bounds:
        return text

    # For each metric, find the end of its dimensions table (last `|` row
    # before a non-`|` line), and insert the badge immediately below.
    inserts: dict[int, str] = {}
    for start, end, ref_id in metric_bounds:
        label = applicability_idx.get(ref_id)
        if label is None:
            continue
        badge = _APPLICABILITY_BADGES.get(label)
        if badge is None:
            continue
        emoji, target = badge
        # Walk from start+1 forward to find the dimensions table end.
        table_end = None
        in_table = False
        for i in range(start + 1, end):
            if lines[i].startswith("|"):
                in_table = True
                table_end = i
            elif in_table and not lines[i].startswith("|"):
                break
        if table_end is None:
            continue
        # Build the badge line. From groups/<this>.md, crosscuts/by-applicability/<target>
        # is reachable at ../crosscuts/by-applicability/<target>.
        badge_md = f"\n**Applicability:** {emoji} [{label}](../crosscuts/by-applicability/{target})\n"
        inserts[table_end + 1] = badge_md

    if not inserts:
        return text

    out: list[str] = []
    for i, line in enumerate(lines):
        if i in inserts:
            out.append(inserts[i])
        out.append(line)
    if len(lines) in inserts:
        out.append(inserts[len(lines)])
    return "\n".join(out)


_RAI_MEMBERSHIP_CACHE: dict[str, list[tuple[str, str]]] | None = None


def _rai_membership_by_ref_id() -> dict[str, list[tuple[str, str]]]:
    """Return {ref_id: [(axis, code), ...]} where axis is 'Principle' or 'Theme'."""
    global _RAI_MEMBERSHIP_CACHE
    if _RAI_MEMBERSHIP_CACHE is not None:
        return _RAI_MEMBERSHIP_CACHE
    out: dict[str, list[tuple[str, str]]] = {}
    for code, (_name, entries) in parse_src.parse_rai_principle_membership().items():
        for e in entries:
            out.setdefault(e.ref_id, []).append(("Principle", code))
    for code, (_name, entries) in parse_src.parse_rai_theme_membership().items():
        for e in entries:
            out.setdefault(e.ref_id, []).append(("Theme", code))
    _RAI_MEMBERSHIP_CACHE = out
    return out


_FEEDBACK_FOOTER = """
---

!!! tip "Spotted an error or disagree with a tier?"
    This catalogue is a [prototype-for-discussion](../prototype-status.md), and feedback on specific metrics is exactly what shapes the next version. Open an issue and pick the template that fits:

    - [Factual error](https://github.com/danjscho/avt-metrics-taxonomy/issues/new?template=01-factual-error.yml) — a claim, citation, threshold, or formula in a metric body looks wrong.
    - [Tier disagreement](https://github.com/danjscho/avt-metrics-taxonomy/issues/new?template=02-tier-disagreement.yml) — a metric is at the wrong priority tier for your context.
    - [Missing metric / gap](https://github.com/danjscho/avt-metrics-taxonomy/issues/new?template=03-missing-metric.yml) — an assurance question that should be in the catalogue but isn't.
    - [Broken link / site bug](https://github.com/danjscho/avt-metrics-taxonomy/issues/new?template=04-broken-link.yml) — internal link, dead citation, rendering issue.
    - [Framing feedback](https://github.com/danjscho/avt-metrics-taxonomy/issues/new?template=05-feedback.yml) — higher-level concern about principles, dimensions, or scope.
"""


def _add_feedback_footer(text: str) -> str:
    """Append a feedback / issue-templates footer to each group page so a
    reader who spots an error has a one-click path to the right issue
    template. Lives at the page bottom rather than per-metric to keep the
    metric bodies clean."""
    return text.rstrip() + "\n" + _FEEDBACK_FOOTER


def _add_related_metrics_footers(text: str, current_page: str) -> str:
    """Append a compact "Related metrics" list after each metric entry on a
    group page. Related = other metrics sharing at least one Playbook
    principle or ethical theme from the Responsible AI lens.

    Works by matching each `### REF ICON Name` heading, computing the set
    of co-memberships, and injecting the block before the next metric
    heading or before the final `---` / EOF.
    """
    if not current_page.startswith("groups/"):
        return text
    membership = _rai_membership_by_ref_id()
    ref_to_metric = {m.ref_id: m for m in parse_src.parse_all_metrics()}

    # Build a reverse lookup: axis-code -> list of ref_ids
    by_axis: dict[tuple[str, str], list[str]] = {}
    for rid, axes in membership.items():
        for ax in axes:
            by_axis.setdefault(ax, []).append(rid)

    # Walk the page: find metric heading lines, collect their co-members.
    lines = text.splitlines()
    out_lines: list[str] = []
    i = 0
    # Pattern: our headings include the explicit {#slug} suffix added earlier.
    heading_re = re.compile(
        r"^###\s+([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+)\s+[🟢🟡🔵]\s+.+?\s+\{\s*#[a-z0-9-]+\s*\}\s*$"
    )
    # For each metric, find the range ending before the next `###` or `---` at col 1.
    metric_heading_line_nums: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            metric_heading_line_nums.append((idx, m.group(1)))

    if not metric_heading_line_nums:
        return text

    # Compute bounds for each metric: ends at next metric heading or a standalone '---'.
    bounds: list[tuple[int, int, str]] = []
    for i, (line_num, rid) in enumerate(metric_heading_line_nums):
        end = (
            metric_heading_line_nums[i + 1][0]
            if i + 1 < len(metric_heading_line_nums)
            else len(lines)
        )
        bounds.append((line_num, end, rid))

    # Build an insert map: index -> block text
    inserts: dict[int, str] = {}
    for start, end, rid in bounds:
        axes = membership.get(rid, [])
        if not axes:
            continue
        related_ids: set[str] = set()
        for ax in axes:
            related_ids.update(by_axis.get(ax, []))
        related_ids.discard(rid)
        if not related_ids:
            continue

        # Cap at 6 most-shared first (sort by co-axis count).
        def co_count(r: str) -> int:
            other = set(membership.get(r, []))
            return len(set(axes) & other)

        ranked = sorted(related_ids, key=lambda r: (-co_count(r), r))[:6]
        items = []
        for r in ranked:
            target = ref_to_metric.get(r)
            if target is None:
                continue
            page = SRC_GROUP_FILE_TO_PAGE.get(target.group_file, "")
            same_page = page == current_page
            slug = r.lower().replace(".", "-")
            # Markdown-style link so mkdocs validates and rewrites.
            # From groups/<this>.md, sibling group pages are at ./<name>.md.
            href = f"#{slug}" if same_page else f"{pathlib.Path(page).name}#{slug}"
            items.append(f"[{r} {target.name}]({href})")
        if not items:
            continue
        # Find the last content line before the next metric heading - place
        # before any trailing `---` separator.
        insert_at = end
        while insert_at > start and lines[insert_at - 1].strip() in ("", "---"):
            insert_at -= 1
        block = (
            "\n\n**Related metrics** *(shared Playbook principles / ethical themes):* "
            + " · ".join(items)
            + "\n"
        )
        inserts[insert_at] = block

    # Assemble output with inserts.
    for idx, line in enumerate(lines):
        if idx in inserts:
            out_lines.append(inserts[idx])
        out_lines.append(line)
    # Any inserts at EOF
    if len(lines) in inserts:
        out_lines.append(inserts[len(lines)])
    return "\n".join(out_lines)


def _inject_contents_applicability_row(text: str) -> str:
    """Inject a prominent applicability-filter row near the top of the
    contents page so a reader can jump to AVT-Specific / AVT-Contextualised
    / General Healthcare AI in one click. Counts are live-derived from the
    parsed catalogue (countable metrics only — sub-parts excluded) so this
    row stays in sync with `_applicability.md` without manual edits."""
    metrics = parse_src.parse_all_metrics()
    parents = {m.parent_ref_id for m in metrics if m.parent_ref_id}
    countable = [m for m in metrics if m.ref_id not in parents]
    counts = Counter(m.dimensions.get("Applicability", "") for m in countable)
    avt = counts.get("AVT-Specific", 0)
    ctx = counts.get("AVT-Contextualised", 0)
    gen = counts.get("General Healthcare AI", 0)
    block = (
        "\n"
        '!!! tip "Browse by applicability"\n'
        "    Jump straight to the metrics that match your scope:\n\n"
        f"    [:material-target: {avt} AVT-Specific](crosscuts/by-applicability/avt-specific.md){{ .md-button }}\n"
        f"    [:material-shuffle-variant: {ctx} AVT-Contextualised](crosscuts/by-applicability/avt-contextualised.md){{ .md-button }}\n"
        f"    [:material-earth: {gen} General Healthcare AI](crosscuts/by-applicability/general.md){{ .md-button }}\n"
        "\n"
    )
    # Insert after the h1 (first `# ` line) and any immediately following blank lines.
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_at = i + 1
            while insert_at < len(lines) and not lines[insert_at].strip():
                insert_at += 1
            break
    return (
        "\n".join(lines[:insert_at])
        + "\n"
        + block
        + "\n".join(lines[insert_at:])
        + ("\n" if not text.endswith("\n") else "")
    )


def _inject_roadmap_prelude(text: str) -> str:
    """Insert a 'Near-term priorities' panel at the top of the gaps page,
    driven by parsed gap data (Tier 1 candidates + High-severity RAI gaps).
    The source file stays editorial; this is a derived view.
    """
    gaps = parse_src.parse_gaps()
    tier_1 = [g for g in gaps if g.tier == 1]
    rai_high = [g for g in gaps if g.severity == "High"]

    # Build a compact table of the Tier 1 candidates - the accepted/proposed
    # set a deployer or standards body would want to tackle first.
    lines = [
        '!!! tip "Near-term priorities"',
        "    These candidates combine **Tier 1 classification** (where assigned) "
        "and **High severity** (Responsible AI lens). They are the highest-leverage "
        "adds for any future metric round.",
        "",
        "### Tier 1 candidates",
        "",
    ]
    if tier_1:
        lines.append("| ID | Title | Origin |")
        lines.append("|----|-------|--------|")
        for g in sorted(tier_1, key=lambda x: (x.origin, x.gap_id or "")):
            gid = g.gap_id or "-"
            lines.append(f"| {gid} | {g.title} | {g.origin} |")
    else:
        lines.append(
            "_(no Tier 1 candidates currently - earlier rounds promoted all available.)_"
        )
    lines.append("")

    lines += [
        "### High-severity policy gaps (RAI lens)",
        "",
    ]
    if rai_high:
        lines.append("| Origin | Title | Cross-reference |")
        lines.append("|--------|-------|-----------------|")
        for g in rai_high:
            lines.append(f"| {g.origin} | {g.title} | {g.notes} |")
    else:
        lines.append("_(no High-severity gaps recorded.)_")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Insert the prelude immediately after the first "## Gaps..." heading + intro
    # paragraph, which ends at the "---" separator on line 13 in the source.
    # The post-promotion text starts with "# Gaps & Proposed Metrics (Roadmap)".
    # Place the prelude right after the first "---" line.
    pieces = text.split("\n---\n", 1)
    if len(pieces) == 2:
        return pieces[0] + "\n\n" + "\n".join(lines) + "\n" + pieces[1]
    return text + "\n\n" + "\n".join(lines) + "\n"


def _landing_page(header_body: str) -> str:
    """Generate the site landing page with live counts and jump links."""
    summary = parse_src.summary()
    metric_count = summary["metric_count"]
    group_count = summary["group_count"]
    t1 = summary["tier_counts"].get("1", 0)
    t2 = summary["tier_counts"].get("2", 0)
    t3 = summary["tier_counts"].get("3", 0)
    gap_count = summary["gap_count"]
    # Live applicability counts (parents excluded — countable units only)
    all_metrics = parse_src.annotate_applicability(parse_src.parse_all_metrics())
    parent_ids = {sp.parent_ref_id for sp in all_metrics if sp.parent_ref_id}
    countable = [m for m in all_metrics if m.ref_id not in parent_ids]
    from collections import Counter

    app_counts = Counter(m.applicability for m in countable)
    avt_specific = app_counts.get("AVT-Specific", 0)
    avt_contextualised = app_counts.get("AVT-Contextualised", 0)
    general = app_counts.get("General Healthcare AI", 0)
    return f"""# Prototype AVT Metrics Taxonomy

!!! warning "Draft - not yet stakeholder-approved"
    Shared openly for early feedback. Tier assignments, gap analysis, and
    cross-references may change before public release. Treat as a working
    document, not a settled standard.

!!! info "{SITE_VERSION} - {metric_count} metrics across {group_count} groups"
    A healthcare-AI assurance metrics taxonomy for Ambient Voice Technology
    in NHS and comparable settings. Each metric carries a formal definition,
    priority tier, responsible actors, and mappings to 13 healthcare,
    AI, and procurement standards.

## At a glance

<div class="grid cards" markdown>

-   :material-scale:{{ .lg .middle }} **Three priority tiers**

    ---

    🟢 **{t1}** Tier 1 — minimum viable assurance, measurable today  

    🟡 **{t2}** Tier 2 — recommended for AVT deployment  
    
    🔵 **{t3}** Tier 3 — advanced / research-grade

    [Jump to Tier 1 quick reference](tier-1-quick-reference.md)

-   :material-clipboard-check-outline:{{ .lg .middle }} **Standards coverage**

    ---

    Mapped to DTAC, DSPT, DCB0129/0160, NHS LLM Framework, NHS T.E.S.T.,
    NHSE AVT Self-Certified Supplier Registry, MHRA SaMD, NICE ESF,
    FHIR UK Core, CQC, PSIRF, PRSB, and Caldicott Principles.

    [Full standards mapping](standards-mapping.md)

-   :material-eye-outline:{{ .lg .middle }} **Policy lens**

    ---

    Mapped to the DSIT AI Playbook's 10 principles and the six
    Responsible AI ethical themes. Includes a coverage matrix of
    high-leverage "policy-lever" metrics.

    [Responsible AI lens](responsible-ai-lens.md)

-   :material-map-marker-path:{{ .lg .middle }} **Roadmap**

    ---

    {gap_count} gap candidates pending review, drawn from external
    coverage audits (RSET, NHSE IG), standards mapping, and the
    policy lens.

    [Browse roadmap](gaps.md)

-   :material-filter-variant:{{ .lg .middle }} **Browse by applicability**

    ---

    Quickly filter the catalogue by whether the metric is specific to
    ambient voice, applies to any healthcare AI, or sits in between.

    🎯 [{avt_specific} AVT-Specific](crosscuts/by-applicability/avt-specific.md) ·
    🔀 [{avt_contextualised} AVT-Contextualised](crosscuts/by-applicability/avt-contextualised.md) ·
    🌐 [{general} General Healthcare AI](crosscuts/by-applicability/general.md)

</div>

## Ways in

- **First time here?** Read [How to use the taxonomy](how-to-use.md) to understand tiers, cadence, and responsible actors.
- **Deploying AVT?** Start with the [Tier 1 Quick Reference](tier-1-quick-reference.md) - the Day Zero set.
- **Evaluating products?** Jump to the [Applicability classification](applicability.md) and the [AVT-Specific cross-cut](crosscuts/by-applicability/avt-specific.md).
- **Setting procurement criteria?** Work through [Standards Mapping](standards-mapping.md) and the [per-principle cross-cuts](crosscuts/index.md).
- **Building a metric?** Every metric has a stable reference ID. Cite as `TP.AC-1` → `/groups/audio-capture/#tp-ac-1`.
- **Want raw data?** See [Downloads](downloads.md) for CSV, JSON, and the monolithic Markdown archival copy.

---

{header_body}
"""


def _downloads_page() -> str:
    summary = parse_src.summary()
    metric_count = summary["metric_count"]
    gap_count = summary["gap_count"]
    version = SITE_VERSION
    return f"""# Downloads

Machine-readable and archival exports of the taxonomy, regenerated on every release.

## Structured data

- [metrics.csv](downloads/metrics.csv) - all {metric_count} metrics as a flat spreadsheet (17 columns: reference ID, name, tier, part, group, applicability, 8 dimension fields, source, pointer to source file).
- [metrics.json](downloads/metrics.json) - same metrics with full dimension dictionary preserved per entry. Stable for programmatic consumption.
- [gaps.json](downloads/gaps.json) - {gap_count} roadmap candidates (accepted + deferred), partitioned by origin (RSET, NHSE IG, standards mapping, Responsible AI lens).
- [summary.json](downloads/summary.json) - headline counts (metric count, tier distribution, group count, gap count).

## Archival Markdown

- <a href="downloads/avt-metrics-taxonomy.txt" download="avt-metrics-taxonomy.md">avt-metrics-taxonomy.md</a> - the full monolithic document. Same content as the site, assembled into a single file for offline reading, PDF printing, or citation. Served with a `.txt` extension so MkDocs treats it as a static download; the link triggers a `.md` save filename in the browser.

## Citing

Cite the taxonomy as:

> Prototype AVT Metrics Taxonomy {version} (2026). Schofield, D. Healthcare metrics taxonomy for assuring Ambient Voice Technology. https://danjscho.github.io/avt-metrics-taxonomy/

For a specific metric, use its reference ID (e.g. `TP.AC-1`) - these are stable across versions. Individual metric pages carry anchor links of the form `/groups/<group>/#tp-ac-1` suitable for deep citation.

## Earlier versions

Versioned historical builds will appear here once the `mike` plugin is wired up. For now, this page shows the current tagged release.
"""


if __name__ == "__main__":
    main()
