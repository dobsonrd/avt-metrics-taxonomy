"""Shared parser for the AVT Metrics Taxonomy source files.

Used by `build.py` (to emit CSV/JSON alongside the monolithic Markdown),
by `audit.py` (single invariant surface), and later by `build_site.py`
(to generate per-standard, per-principle, per-applicability pages).

Do not author structured data outside the source files - this parser
is the single route by which in-prose tables become structured data.
"""

from __future__ import annotations

import pathlib
import re
from collections import Counter
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).parent

# Canonical group file list: path -> {prefix, part, group name}.
# Matches the build.py order within each part.
# Single-source version stamp. Bumped manually at each release; consumed by
# build.py (JSON metadata), build_site.py (landing + downloads citation), and
# pyproject.toml. Keep these in sync at release time.
TAXONOMY_VERSION = "v5.5.14"
TAXONOMY_DATE = "2026-05-14"  # ISO date of TAXONOMY_VERSION release; bumped together


def ref_id_to_anchor(ref_id: str) -> str:
    """Canonical ref-ID-to-anchor slug: `TP.SN-5` → `tp-sn-5`. The MkDocs
    default slugifier produces `tpsn-5`, dropping the period; we use this
    form so reference IDs render as stable, human-readable anchors."""
    return ref_id.lower().replace(".", "-")


# Cluster naming. The two-letter prefix on every ref-ID is the canonical
# cluster identifier (TP / PI / HL / IO / GV / ES). Single source of truth —
# both build.py (for the CSV / JSON downloads) and build_site.py (for the
# rendered cluster eyebrow on group pages) consume this. v4.0 retired the
# v3.x Part-letter scheme (A–F).
CLUSTER_ORDER: list[str] = ["TP", "PI", "HL", "IO", "GV", "ES"]

CLUSTER_NAMES: dict[str, str] = {
    "TP": "The Technical Pipeline",
    "PI": "Pipeline Interactions",
    "HL": "The Human Layer",
    "IO": "Impact & Outcomes",
    "GV": "System Governance",
    "ES": "Evaluation Science",
}

GROUP_FILES: dict[str, dict[str, str]] = {
    "tp/audio-capture.md": {
        "prefix": "TP.AC",
        "cluster": "TP",
        "group": "Audio Capture & Environment",
    },
    "tp/asr-transcription.md": {
        "prefix": "TP.ASR",
        "cluster": "TP",
        "group": "ASR / Transcription",
    },
    "tp/diarisation.md": {"prefix": "TP.DI", "cluster": "TP", "group": "Diarisation"},
    "tp/summarisation-nlp.md": {
        "prefix": "TP.SN",
        "cluster": "TP",
        "group": "Summarisation / NLP",
    },
    "tp/clinical-coding.md": {
        "prefix": "TP.CC",
        "cluster": "TP",
        "group": "Clinical Coding",
    },
    "tp/downstream-write-back.md": {
        "prefix": "TP.WB",
        "cluster": "TP",
        "group": "Downstream Write-back",
    },
    "pi/partial-pipeline.md": {
        "prefix": "PI.PP",
        "cluster": "PI",
        "group": "Partial-Pipeline",
    },
    "pi/end-to-end-pipeline.md": {
        "prefix": "PI.E2E",
        "cluster": "PI",
        "group": "End-to-End Pipeline",
    },
    "hl/human-factors-workflow.md": {
        "prefix": "HL.HF",
        "cluster": "HL",
        "group": "Human Factors & Workflow",
    },
    "io/patient-experience.md": {
        "prefix": "IO.PX",
        "cluster": "IO",
        "group": "Patient Experience",
    },
    "io/fairness-equity.md": {
        "prefix": "IO.FE",
        "cluster": "IO",
        "group": "Fairness & Equity",
    },
    "gv/safety-governance.md": {
        "prefix": "GV.SG",
        "cluster": "GV",
        "group": "Safety & Governance",
    },
    "gv/nhs-compliance-regulatory.md": {
        "prefix": "GV.CR",
        "cluster": "GV",
        "group": "NHS Compliance & Regulatory",
    },
    "gv/security-adversarial-robustness.md": {
        "prefix": "GV.SC",
        "cluster": "GV",
        "group": "Security & Adversarial Robustness",
    },
    "gv/privacy-data-governance.md": {
        "prefix": "GV.PD",
        "cluster": "GV",
        "group": "Privacy & Data Governance",
    },
    "gv/operational.md": {"prefix": "GV.OP", "cluster": "GV", "group": "Operational"},
    "gv/environmental-sustainability.md": {
        "prefix": "GV.EN",
        "cluster": "GV",
        "group": "Environmental & Sustainability",
    },
    "gv/training-competency.md": {
        "prefix": "GV.TC",
        "cluster": "GV",
        "group": "Training & Competency",
    },
    "gv/vendor-transparency-contractual.md": {
        "prefix": "GV.VT",
        "cluster": "GV",
        "group": "Vendor Transparency & Contractual",
    },
    "es/meta-evaluation.md": {
        "prefix": "ES.ME",
        "cluster": "ES",
        "group": "Meta-Evaluation",
    },
}

TIER_ICON_TO_NUM = {"🟢": 1, "🟡": 2, "🔵": 3}
TIER_NUM_TO_LABEL = {1: "Minimum Viable", 2: "Recommended", 3: "Advanced / Research"}

# Reference IDs can carry a single lowercase letter suffix for sub-parts
# (e.g. TP.SN-7a, TP.SN-7b under parent TP.SN-7), introduced in v3.7
# Phase 2.1 to absorb the redundancy candidates from the v3.6 duplication
# review. Parents and sub-parts both match this regex; downstream code
# uses the suffix presence to distinguish them.
METRIC_HEADING = re.compile(
    r"^###\s+([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+[a-z]?)\s+([🟢🟡🔵])\s+(.+?)\s*$"
)
SUBPART_REF_ID_RE = re.compile(r"^([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+)([a-z])$")
DIM_ROW = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*$")


@dataclass
class Metric:
    ref_id: str
    name: str
    tier: int  # 1 / 2 / 3
    cluster: str  # cluster code: TP / PI / HL / IO / GV / ES
    group: str  # human-readable group name
    group_file: str  # relative path, e.g. "tp/audio-capture.md"
    heading_line: int  # 1-indexed line number of `### ...` heading in group file
    dimensions: dict[str, str] = field(default_factory=dict)
    applicability: str | None = None  # populated by annotate_applicability()

    @property
    def tier_icon(self) -> str:
        return {1: "🟢", 2: "🟡", 3: "🔵"}[self.tier]

    @property
    def cluster_name(self) -> str:
        return CLUSTER_NAMES.get(self.cluster, "")

    @property
    def tier_label(self) -> str:
        return TIER_NUM_TO_LABEL[self.tier]

    @property
    def cadence(self) -> str:
        return self.dimensions.get("Measurement Cadence", "")

    @property
    def pipeline_layer(self) -> str:
        return self.dimensions.get("Pipeline Layer", "")

    @property
    def assurance_question(self) -> str:
        return self.dimensions.get("Assurance Question", "")

    @property
    def measurement_method(self) -> str:
        return self.dimensions.get("Measurement Method", "")

    @property
    def lifecycle_phases(self) -> str:
        return self.dimensions.get("Lifecycle Phases") or self.dimensions.get(
            "Lifecycle Phase", ""
        )

    @property
    def responsible_actors(self) -> str:
        return self.dimensions.get("Responsible Actors") or self.dimensions.get(
            "Responsible Actor", ""
        )

    @property
    def maturity(self) -> str:
        return self.dimensions.get("Maturity", "")

    @property
    def source(self) -> str:
        return self.dimensions.get("Source", "")

    @property
    def family(self) -> str | None:
        """Named-metric-family membership (v5.4.0+); None if metric is unaffiliated.

        Family values are declared in `_families.md` and audit-checked for
        resolution; the dimensions table carries the value per metric.
        """
        return self.dimensions.get("Family") or None

    @property
    def ai_substrate(self) -> str | None:
        """AI-Substrate class (v5.5.3+, derived; plan-future #10 Option 2).

        One of: Pre-AI / AI-Substrate / Post-AI / AI-Mediated Workflow /
        AI-Agnostic Governance. Derived from cluster + per-metric
        overrides at read time — not a per-metric dimension. See
        `_ai-substrate.md` for the framing and `derive_ai_substrate`
        for the rules.
        """
        return derive_ai_substrate(self)

    @property
    def layer(self) -> str | None:
        """Layer of Defence — Prevention / Detection / Limitation (v5.5.0+).

        Optional per-metric field. v5.5.0 seeds 33 metrics from an
        early-draft slide-deck classification; remaining metrics leave
        the field absent and the by-layer-of-defence crosscut falls
        back to the cadence heuristic at `derive_layer_of_defence`.
        """
        return self.dimensions.get("Layer") or None

    @property
    def is_subpart(self) -> bool:
        """True iff this metric is a sub-part of a parent (ref_id ends in [a-z])."""
        return bool(SUBPART_REF_ID_RE.match(self.ref_id))

    @property
    def parent_ref_id(self) -> str | None:
        """For a sub-part, return the parent ref_id (e.g. TP.SN-7a → TP.SN-7).
        For a parent or single metric, return None."""
        m = SUBPART_REF_ID_RE.match(self.ref_id)
        return m.group(1) if m else None


def parse_group_file(rel_path: str) -> list[Metric]:
    info = GROUP_FILES[rel_path]
    lines = (ROOT / rel_path).read_text().splitlines()
    metrics: list[Metric] = []

    i = 0
    while i < len(lines):
        m = METRIC_HEADING.match(lines[i])
        if not m:
            i += 1
            continue
        ref_id, icon, name = m.group(1), m.group(2), m.group(3).strip()
        heading_line = i + 1
        tier = TIER_ICON_TO_NUM[icon]

        # Scan forward to the next metric heading, collecting dimension rows.
        dims: dict[str, str] = {}
        j = i + 1
        while j < len(lines) and not METRIC_HEADING.match(lines[j]):
            dm = DIM_ROW.match(lines[j])
            if dm:
                dims[dm.group(1).strip()] = dm.group(2).strip()
            j += 1

        metrics.append(
            Metric(
                ref_id=ref_id,
                name=name,
                tier=tier,
                cluster=info["cluster"],
                group=info["group"],
                group_file=rel_path,
                heading_line=heading_line,
                dimensions=dims,
                applicability=dims.get("Applicability"),
            )
        )
        i = j

    return metrics


def parse_all_metrics() -> list[Metric]:
    out: list[Metric] = []
    for rel_path in GROUP_FILES:
        out.extend(parse_group_file(rel_path))
    return out


# ---------------------------------------------------------------------------
# Applicability - now sourced from each metric's dimension table (v3.6+).
# Legacy parse_applicability() reads _applicability.md and is kept only for
# audit cross-validation during the transition. annotate_applicability() is
# a no-op since parse_group_file() already populates metric.applicability
# from the dimension table - retained as an idempotent safety net for any
# call site that has not yet been updated.
# ---------------------------------------------------------------------------

_APPLICABILITY_ROW = re.compile(
    r"^\|\s*([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+)\s*\|\s*[^|]+\|\s*[^|]+\|\s*([^|]+?)\s*\|"
)


def parse_applicability_legacy() -> dict[str, str]:
    """Read the per-metric applicability map from _applicability.md.

    Used only by audit.py for cross-validation against the per-metric
    dimension-table values during the v3.6 transition. The dimension
    table is the source of truth from v3.6 onward.
    """
    text = (ROOT / "_applicability.md").read_text()
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = _APPLICABILITY_ROW.match(line)
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


# Backwards-compatible alias — some callers still import parse_applicability.
parse_applicability = parse_applicability_legacy


def annotate_applicability(metrics: list[Metric]) -> list[Metric]:
    """Idempotent: parse_group_file already populates metric.applicability
    from the dimension table. This function is retained as a safety net
    for older callers and fills any None values from the legacy file."""
    needs_fill = [m for m in metrics if not m.applicability]
    if not needs_fill:
        return metrics
    idx = parse_applicability_legacy()
    for metric in needs_fill:
        metric.applicability = idx.get(metric.ref_id)
    return metrics


# ---------------------------------------------------------------------------
# Gaps - parsed from _gaps.md by origin section
# ---------------------------------------------------------------------------


@dataclass
class Gap:
    gap_id: str | None  # e.g. "Gap-RSET-A", "GV.CR-11", or None for RAI severity rows
    title: str
    origin: str  # "rset-accepted" / "rset-deferred" / "ig" / "standards-*" / "rai-principle" / "rai-theme"
    tier: int | None  # 1 / 2 / 3 or None (RAI severity rows don't have a tier)
    severity: str | None  # "High" / "Medium" / "Low" or None
    source: str  # source standard / audit reference
    notes: str  # free-text rationale or cross-reference


_GAP_SECTIONS: list[tuple[str, str, str]] = [
    # (section anchor start, origin tag, source label)
    ("### 1a. Accepted - RSET", "rset-accepted", "RSET external review"),
    ("### 1b. Deferred - RSET", "rset-deferred", "RSET external review"),
    ("### 1c. Accepted - NHSE IG", "ig", "NHSE IG Mar-2026"),
    ("### 2a. MHRA SaMD", "standards-mhra", "MHRA SaMD / AIaMD"),
    ("### 2b. NICE Evidence Standards", "standards-nice-esf", "NICE ESF"),
    ("### 2c. FHIR UK Core", "standards-fhir-uk-core", "FHIR UK Core"),
    ("### 2d. CQC Assessment", "standards-cqc", "CQC Assessment"),
    ("### 2e. PSIRF", "standards-psirf", "PSIRF"),
    ("### 2f. PRSB", "standards-prsb", "PRSB"),
    ("### 2g. Caldicott", "standards-caldicott", "Caldicott Principles"),
    ("## 3. NHS T.E.S.T.", "standards-test", "NHS T.E.S.T."),
    ("### 4a. By Playbook principle", "rai-principle", "DSIT AI Playbook"),
    ("### 4b. By ethical theme", "rai-theme", "Responsible AI ethical themes"),
]


def _section_slices(text: str) -> list[tuple[str, str, str, str]]:
    """Return [(origin, source, section_header, section_body)] for each tracked section."""
    out = []
    for header, origin, source in _GAP_SECTIONS:
        idx = text.find(header)
        if idx == -1:
            continue
        # Body runs until the next section marker or a higher-level heading.
        rest = text[idx + len(header) :]
        # Next `### ` or `## ` heading ends the section.
        m = re.search(r"\n(#{2,3})\s", rest)
        body = rest[: m.start()] if m else rest
        out.append((origin, source, header, body))
    return out


_TIER_RE = re.compile(r"🟢\s*1|🟡\s*2|🔵\s*3")


def _parse_gap_row(cells: list[str], origin: str, source: str) -> Gap | None:
    """Interpret a gap table row. Column layout varies by section."""
    # Strip markdown-table artefacts.
    cells = [c.strip() for c in cells]
    if not cells or not any(cells):
        return None

    # Detect tier icon anywhere in the row.
    tier = None
    for c in cells:
        if "🟢" in c:
            tier = 1
            break
        if "🟡" in c:
            tier = 2
            break
        if "🔵" in c:
            tier = 3
            break

    # Severity (RAI rows use High/Medium/Low).
    severity = None
    for c in cells:
        lc = c.lower()
        if lc in {"high", "medium", "low"}:
            severity = c
            break

    # Column-1 disposition (v5.3.0+):
    # - External-review rows: cells[0] is `Gap-RSET-*` / `Gap-IG-*` (gap_id), cells[1] is title
    # - Standards rows (post-v5.3.0): cells[0] is title (slot-less per the convention shift)
    # - Standards rows (pre-v5.3.0 promoted entries with a v5.3.0-status column): cells[0] is title
    # - RAI rows: cells[0] is the principle/theme label (no separate title column)
    gap_id = None
    if cells and re.match(
        r"^(Gap-[A-Z]+-[A-Z0-9]+|[A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+)$", cells[0]
    ):
        gap_id = cells[0]
        title_cell = cells[1] if len(cells) >= 2 else cells[0]
    else:
        title_cell = cells[0]

    # Notes: last cell is usually "cross-reference" or rationale.
    notes = cells[-1] if len(cells) >= 3 else ""

    # Filter out header rows masquerading as data (e.g. "Gap ID | Title | ...").
    if title_cell.lower() in {"title", "gap", "description"}:
        return None
    if (
        gap_id is None
        and title_cell.lower().startswith("principle")
        or title_cell.lower().startswith("theme")
    ):
        return None

    return Gap(
        gap_id=gap_id,
        title=title_cell,
        origin=origin,
        tier=tier,
        severity=severity,
        source=source,
        notes=notes,
    )


def parse_gaps() -> list[Gap]:
    path = ROOT / "_gaps.md"
    if not path.exists():
        return []
    text = path.read_text()

    gaps: list[Gap] = []
    for origin, source, _header, body in _section_slices(text):
        # Walk rows of any Markdown table inside this section body.
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            # Skip header separator rows (|---|---|).
            if re.match(r"^\|\s*[:\-]+\s*(\|\s*[:\-]+\s*)+\|\s*$", line):
                continue
            # Split cells; drop empty leading/trailing cell from |..|..|..
            parts = [c for c in line.split("|")]
            # Trim first and last if empty
            if parts and parts[0].strip() == "":
                parts = parts[1:]
            if parts and parts[-1].strip() == "":
                parts = parts[:-1]
            parts = [c.strip() for c in parts]
            # Header row detection: contains "Gap ID" / "Proposed Ref" / "Principle" / "Theme"
            lower = [c.lower() for c in parts]
            if any(
                h in lower for h in ("gap id", "proposed ref", "principle", "theme")
            ):
                continue
            gap = _parse_gap_row(parts, origin, source)
            if gap is not None:
                gaps.append(gap)

    return gaps


# ---------------------------------------------------------------------------
# Responsible AI lens - per-principle and per-theme membership tables
# ---------------------------------------------------------------------------

# The source file has one table per principle (P1..P10) and per theme (T1..T6).
# Each is preceded by a heading that names the principle/theme. We extract the
# table body (Ref | Metric | Group | Tier | Aspect) and return a map from
# principle/theme code to a list of entries.

_RAI_SECTION = re.compile(
    r"^###\s+(?:Principle\s+(?P<pnum>\d+):\s*(?P<pname>.+?)|"
    r"Theme\s+(?P<tnum>\d+)\s*[:\-–—]\s*(?P<tname>.+?))\s*$",
    re.MULTILINE,
)
_TABLE_ROW = re.compile(
    r"^\|\s*([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|"
)


@dataclass
class RaiEntry:
    ref_id: str
    name: str
    group: str
    tier_icon: str
    aspect: str


def _parse_rai_section(body: str) -> list[RaiEntry]:
    entries: list[RaiEntry] = []
    for line in body.splitlines():
        m = _TABLE_ROW.match(line)
        if not m:
            continue
        ref_id, name, grp, tier, aspect = (g.strip() for g in m.groups())
        # Header row may fall through if "Ref" wasn't exactly matched; skip if
        # this doesn't look like a real ref.
        if not re.match(r"^[A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+$", ref_id):
            continue
        entries.append(
            RaiEntry(
                ref_id=ref_id,
                name=name,
                group=grp,
                tier_icon=tier,
                aspect=aspect,
            )
        )
    return entries


def parse_rai_principle_membership() -> dict[str, tuple[str, list[RaiEntry]]]:
    """Returns {'P1': ('principle title', [RaiEntry...]), ...}."""
    text = (ROOT / "_responsible-ai-lens.md").read_text()
    sections: dict[str, tuple[str, list[RaiEntry]]] = {}
    matches = list(_RAI_SECTION.finditer(text))
    for i, m in enumerate(matches):
        if m.group("pnum") is None:
            continue
        code = f"P{m.group('pnum')}"
        name = m.group("pname").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[code] = (name, _parse_rai_section(text[start:end]))
    return sections


def parse_rai_theme_membership() -> dict[str, tuple[str, list[RaiEntry]]]:
    text = (ROOT / "_responsible-ai-lens.md").read_text()
    sections: dict[str, tuple[str, list[RaiEntry]]] = {}
    matches = list(_RAI_SECTION.finditer(text))
    for i, m in enumerate(matches):
        if m.group("tnum") is None:
            continue
        code = f"T{m.group('tnum')}"
        name = m.group("tname").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[code] = (name, _parse_rai_section(text[start:end]))
    return sections


# ---------------------------------------------------------------------------
# Standards mapping - per-standard assertion → metric rows
# ---------------------------------------------------------------------------

# Standards each live under an `### Standard Name` heading in
# _standards-mapping.md. Within that, subsections are `#### Section Name`.
# Tables have a consistent 4-column shape:
#   | Criterion | Description | Taxonomy Metrics | Tier |
# Some rows list metrics by name only (comma-separated); some prefix the
# reference ID. We extract both shapes and resolve names against the
# parsed metric catalogue.


@dataclass
class StandardRow:
    criterion: str  # e.g. "C1.2.2" or "WP3-05"
    description: str
    metric_refs: list[str]  # resolved reference IDs (may be empty)
    metric_names: list[str]  # original names, useful for fallback display
    tier_cell: str  # raw tier cell (e.g. "🟢 1" or "🟢 1 / 🟡 2" or "-")


@dataclass
class StandardSection:
    code: str  # unique code e.g. "dtac-c1"
    standard: str  # top-level standard heading text
    subsection: str  # `#### ...` heading text (may be empty)
    rows: list[StandardRow]


# Heading patterns
_STD_H3 = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
_STD_H4 = re.compile(r"^####\s+(.+?)\s*$", re.MULTILINE)

_PIPE_ROW = re.compile(r"^\|(.+)\|\s*$")


def _split_cells(line: str) -> list[str]:
    # Strip leading and trailing pipe, then split.
    inner = line.strip().strip("|")
    return [c.strip() for c in inner.split("|")]


def _is_separator(cells: list[str]) -> bool:
    return all(re.match(r"^[:\-]+$", c or "-") for c in cells)


def _tables_in(body: str) -> list[list[list[str]]]:
    """Return a list of tables (each a list of rows, each a list of cells)
    found in the given markdown body. Tables are detected as runs of lines
    starting with `|` separated by non-pipe gaps."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in body.splitlines():
        if line.startswith("|"):
            m = _PIPE_ROW.match(line)
            if m:
                current.append(_split_cells(line))
                continue
        if current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


_NAME_TO_METRIC_CACHE: dict[str, Metric] | None = None


def _name_to_metric_idx() -> dict[str, Metric]:
    global _NAME_TO_METRIC_CACHE
    if _NAME_TO_METRIC_CACHE is None:
        idx: dict[str, Metric] = {}
        for m in parse_all_metrics():
            idx[m.name] = m
            # Base name without parenthesised suffix
            stripped = re.sub(r"\s*\([^)]*\)\s*", "", m.name).strip()
            if stripped and stripped not in idx:
                idx[stripped] = m
            # Abbreviations inside parens (e.g. "WER" from "Word Error Rate (WER)")
            for abbr in re.findall(r"\(([^)]+)\)", m.name):
                abbr = abbr.strip()
                if abbr and abbr not in idx:
                    idx[abbr] = m
        _NAME_TO_METRIC_CACHE = idx
    return _NAME_TO_METRIC_CACHE


def _extract_metric_refs(cell: str) -> tuple[list[str], list[str]]:
    """Given a standards-table 'Taxonomy Metrics' cell, return (ref_ids,
    display_names). The cell may be:
      - italic process note: `*Process criterion - no metric equivalent*`
      - a comma-separated list of names, optionally prefixed with ref IDs
      - empty or "-"
    """
    if not cell or cell.strip() in {"-", "-"}:
        return [], []
    # Strip italic wrapper if present; if the whole cell is italic process
    # text we return nothing.
    stripped = cell.strip()
    if stripped.startswith("*") and stripped.endswith("*"):
        return [], []
    # Remove bold/italic markers so regex and name matching work
    cleaned = re.sub(r"\*+", "", stripped)
    # Split on commas at top level (metric names don't contain commas by
    # current convention).
    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    idx = _name_to_metric_idx()
    ref_ids: list[str] = []
    names: list[str] = []
    for part in parts:
        # Try "TP.SN-3 Metric Name" prefix form first.
        m = re.match(r"^([A-Z]{2,3}\.[A-Z0-9]{2,3}-\d+)\s+(.+)$", part)
        if m:
            ref_ids.append(m.group(1))
            names.append(m.group(2).strip())
            continue
        # Otherwise look up by full / base / abbreviation.
        hit = idx.get(part)
        if hit is None:
            base = re.sub(r"\s*\([^)]*\)\s*", "", part).strip()
            hit = idx.get(base)
        if hit is not None:
            ref_ids.append(hit.ref_id)
            names.append(hit.name)
        else:
            names.append(part)  # unresolved - preserve for display
    return ref_ids, names


def _standard_code(heading: str) -> str:
    """Shortest stable slug for a standard heading."""
    # Keep only alnum and hyphens from the first word or two.
    text = heading.lower()
    # Clip to just before the em dash / colon
    for sep in (" - ", " – ", ": "):
        if sep in text:
            text = text.split(sep, 1)[0]
            break
    # Squash non-alnum → hyphen
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def parse_standards_mapping() -> list[StandardSection]:
    path = ROOT / "_standards-mapping.md"
    if not path.exists():
        return []
    text = path.read_text()

    # Find every ### block.
    h3s = [(m.start(), m.group(1).strip()) for m in _STD_H3.finditer(text)]
    # Add terminator
    h3s_bounds = [
        (h3s[i][0], h3s[i][1], h3s[i + 1][0] if i + 1 < len(h3s) else len(text))
        for i in range(len(h3s))
    ]

    sections: list[StandardSection] = []
    for start, heading, end in h3s_bounds:
        block = text[start:end]
        # Identify subsections
        h4_matches = list(_STD_H4.finditer(block))
        segments: list[tuple[str, str]] = []
        if h4_matches:
            # Segment before first h4 (rare - usually intro only, skip)
            intro_end = h4_matches[0].start()
            for i, h4 in enumerate(h4_matches):
                seg_start = h4.end()
                seg_end = (
                    h4_matches[i + 1].start() if i + 1 < len(h4_matches) else len(block)
                )
                segments.append((h4.group(1).strip(), block[seg_start:seg_end]))
        else:
            segments.append(("", block[len(heading) + 4 :]))  # after `### <heading>\n`

        for sub_heading, body in segments:
            all_rows: list[StandardRow] = []
            for table in _tables_in(body):
                if len(table) < 2:
                    continue
                # Rows beyond the header and separator.
                data_rows = [r for r in table if not _is_separator(r)]
                if not data_rows:
                    continue
                header_cells = [c.lower() for c in data_rows[0]]
                # Require "taxonomy metrics" column presence
                try:
                    metric_col = next(
                        i
                        for i, c in enumerate(header_cells)
                        if "taxonomy metric" in c or "metrics" == c
                    )
                except StopIteration:
                    continue
                # Locate other columns heuristically
                desc_col = next(
                    (
                        i
                        for i, c in enumerate(header_cells)
                        if c
                        in {"description", "item", "principle", "assertion", "clause"}
                        or "description" in c
                    ),
                    1 if len(header_cells) > 1 else None,
                )
                tier_col = next(
                    (i for i, c in enumerate(header_cells) if c == "tier"), None
                )
                # Treat the first column as criterion regardless.
                crit_col = 0
                for row in data_rows[1:]:
                    if len(row) <= metric_col:
                        continue
                    criterion = row[crit_col] if crit_col < len(row) else ""
                    description = (
                        row[desc_col]
                        if (desc_col is not None and desc_col < len(row))
                        else ""
                    )
                    metric_cell = row[metric_col]
                    tier_cell = (
                        row[tier_col]
                        if (tier_col is not None and tier_col < len(row))
                        else ""
                    )
                    ref_ids, names = _extract_metric_refs(metric_cell)
                    all_rows.append(
                        StandardRow(
                            criterion=criterion,
                            description=description,
                            metric_refs=ref_ids,
                            metric_names=names,
                            tier_cell=tier_cell,
                        )
                    )
            if all_rows:
                sections.append(
                    StandardSection(
                        code=_standard_code(heading)
                        + (("-" + _standard_code(sub_heading)) if sub_heading else ""),
                        standard=heading,
                        subsection=sub_heading,
                        rows=all_rows,
                    )
                )
    return sections


def parse_standards_grouped() -> dict[str, dict]:
    """Return {standard_heading: {'code': slug, 'sections': [StandardSection...]}}.
    Groups sub-sections of the same standard together, so each standard
    gets one page."""
    out: dict[str, dict] = {}
    for section in parse_standards_mapping():
        out.setdefault(
            section.standard,
            {
                "code": _standard_code(section.standard),
                "sections": [],
            },
        )["sections"].append(section)
    return out


# ---------------------------------------------------------------------------
# Applicability membership (derived from already-parsed metrics)
# ---------------------------------------------------------------------------


def group_metrics_by_applicability(metrics: list[Metric]) -> dict[str, list[Metric]]:
    out: dict[str, list[Metric]] = {}
    for m in metrics:
        key = m.applicability or "Unclassified"
        out.setdefault(key, []).append(m)
    return out


def group_metrics_by_family(metrics: list[Metric]) -> dict[str, list[Metric]]:
    """Group metrics by Family dimension value (v5.4.0+). Metrics without a
    Family value are excluded entirely (no `Unaffiliated` bucket — the
    families page already names "Unaffiliated" in prose; here we surface
    only the named families)."""
    out: dict[str, list[Metric]] = {}
    for m in metrics:
        fam = m.family
        if not fam:
            continue
        out.setdefault(fam, []).append(m)
    return out


# v5.5.3: AI-Substrate derived classification (plan-future #10 Option 2).
# Cluster-default + per-metric overrides; documented at `_ai-substrate.md`.
_AI_SUBSTRATE_GROUP_DEFAULTS: dict[str, str] = {
    "TP.AC": "Pre-AI",
    "TP.ASR": "AI-Substrate",
    "TP.DI": "AI-Substrate",
    "TP.SN": "AI-Substrate",
    "TP.CC": "AI-Substrate",
    "TP.WB": "Post-AI",
    "PI.PP": "AI-Substrate",
    "PI.E2E": "AI-Substrate",
    "HL.HF": "AI-Mediated Workflow",
    "IO.PX": "AI-Mediated Workflow",
    "IO.FE": "AI-Substrate",
    "ES.ME": "AI-Substrate",
    "GV.SG": "AI-Substrate",
    "GV.SC": "AI-Substrate",
    "GV.CR": "AI-Agnostic Governance",
    "GV.VT": "AI-Agnostic Governance",
    "GV.PD": "AI-Agnostic Governance",
    "GV.OP": "AI-Agnostic Governance",
    "GV.TC": "AI-Agnostic Governance",
    "GV.EN": "AI-Agnostic Governance",
}
_AI_SUBSTRATE_OVERRIDES: dict[str, str] = {
    # Training data metrics live in privacy-data-governance for cluster
    # placement but test the model's data substrate.
    "GV.PD-7": "AI-Substrate",
    "GV.PD-12": "AI-Substrate",
    # IO.PX outcome metrics that test downstream AI-output quality, not
    # the patient-clinician interaction.
    "IO.PX-9": "AI-Substrate",
    "IO.PX-10": "AI-Substrate",
    # System availability is the infrastructure consumed by the AI; the
    # metric tests deployer-side uptime, not AI behaviour.
    "GV.OP-5": "Post-AI",
    # Some GV.SG metrics test deployer governance posture (versioning,
    # change tracking, assurance debt) rather than model behaviour.
    "GV.SG-1": "AI-Agnostic Governance",
    "GV.SG-2": "AI-Agnostic Governance",
    "GV.SG-13": "AI-Agnostic Governance",
    # Some GV.SG metrics route AI-failure through human/organisational
    # channels (LFPSE incident reporting, near-miss reporting).
    "GV.SG-14": "AI-Mediated Workflow",
    "GV.SG-11": "AI-Mediated Workflow",
}


def derive_ai_substrate(m: Metric) -> str | None:
    """Heuristic AI-substrate classifier (v5.5.3+; plan-future #10 Option 2).

    Five-class derived cut: Pre-AI / AI-Substrate / Post-AI /
    AI-Mediated Workflow / AI-Agnostic Governance. Documented at
    `_ai-substrate.md`. Per-group defaults + per-metric overrides
    yield 0% disputed coverage on the catalogue at v5.5.3 time of
    introduction. Promotion criterion (>80% non-disputed) is met.

    The classifier is documentation-derived, not per-metric structural
    — there is no `AI Substrate` field on metric bodies. Future
    releases may add the field if the cut becomes load-bearing.
    """
    ref_id = m.ref_id
    if ref_id in _AI_SUBSTRATE_OVERRIDES:
        return _AI_SUBSTRATE_OVERRIDES[ref_id]
    cluster = m.cluster
    parts = ref_id.split(".", 1)
    if len(parts) != 2:
        return None
    group = parts[1].split("-")[0]
    group_key = f"{cluster}.{group}"
    return _AI_SUBSTRATE_GROUP_DEFAULTS.get(group_key)


def group_metrics_by_ai_substrate(metrics: list[Metric]) -> dict[str, list[Metric]]:
    """Group metrics by derived AI-substrate classification (v5.5.3+).
    Metrics without a derivable class are excluded."""
    out: dict[str, list[Metric]] = {}
    for m in metrics:
        cls = derive_ai_substrate(m)
        if cls is None:
            continue
        out.setdefault(cls, []).append(m)
    return out


def derive_layer_of_defence(m: Metric) -> str | None:
    """Layer-of-Defence classifier (v5.5.0+).

    Prefers the explicit per-metric `Layer` field. Falls back to a
    Cadence-based heuristic for metrics that don't carry the field:

    - `One-off gate` → Prevention
    - `Continuous` / `Periodic audit` → Detection
    - `Event-triggered` → Limitation

    The cadence heuristic is **wrong about a third of the time** (it
    conflates always-on limitation infrastructure with detection, and
    misses pre-deployment gates that have continuous nominal cadence).
    The explicit `Layer` field — seeded for 33 Tier 1 metrics in
    v5.5.0 from an early-draft slide-deck classification — is the
    authoritative answer where present. Remaining metrics use the
    heuristic with a known-imperfect-but-honest disclaimer on the
    crosscut page.
    """
    explicit = m.layer
    if explicit:
        return explicit
    cadence = m.dimensions.get("Measurement Cadence", "").strip()
    if not cadence:
        return None
    elements = [e.strip() for e in cadence.split(";") if e.strip()]
    layer_for = {
        "One-off gate": "Prevention",
        "Periodic audit": "Detection",
        "Continuous": "Detection",
        "Event-triggered": "Limitation",
    }
    classified = [layer_for[e] for e in elements if e in layer_for]
    if not classified:
        return None
    # Tie-break: prefer Prevention > Detection > Limitation when multi-valued
    for preferred in ("Prevention", "Detection", "Limitation"):
        if preferred in classified:
            return preferred
    return classified[0]


def group_metrics_by_layer_of_defence(metrics: list[Metric]) -> dict[str, list[Metric]]:
    """Group metrics by derived layer-of-defence classification (v5.5.0+).
    Metrics without a derivable layer are excluded."""
    out: dict[str, list[Metric]] = {}
    for m in metrics:
        layer = derive_layer_of_defence(m)
        if layer is None:
            continue
        out.setdefault(layer, []).append(m)
    return out


# ---------------------------------------------------------------------------
# References catalogue (v3.9)
#
# `_references.md` is the single source of truth for every external citation
# the taxonomy makes. This section parses it into structured records for use
# by audit.py (handle-resolution check) and build_site.py (cited-by back-
# reference rendering, populated at build time).
# ---------------------------------------------------------------------------


REFERENCES_FILE = "_references.md"
REFERENCE_HEADING = re.compile(r"^###\s+([A-Za-z0-9][A-Za-z0-9_-]*)\s*$")
REFERENCE_FIELD = re.compile(r"^-\s+\*\*([^*]+?):\*\*\s*(.*?)\s*$")
# Inline `[Handle]` reference-style links in metric files. Matches `[Foo]`
# only when not followed by `(...)` (which would be an inline link) and not
# preceded by `!` (image link). The Handle character set matches the catalogue
# heading regex.
INLINE_HANDLE = re.compile(r"(?<!!)\[([A-Za-z][A-Za-z0-9_-]*)\](?!\()")


@dataclass
class Reference:
    handle: str
    title: str = ""
    publisher: str = ""
    source_type: str = ""
    url: str = ""
    archive: str = ""
    retrieved: str = ""
    local_mirror: str = ""
    short: str = ""  # human-readable short form for inline-link rendering (v4.5)
    description: str = ""

    @property
    def is_archived(self) -> bool:
        # An entry counts as archived only if Archive is a real URL —
        # the placeholder "(Phase 1 — pending snapshot.py)" does not count.
        return self.archive.startswith("http")


def parse_references() -> dict[str, Reference]:
    """Parse `_references.md` into {handle: Reference}.

    The grammar is: each entry is an h3 (`### Handle`) followed by a bullet
    list of fields (`- **Field:** value`). Free-form prose between or after
    the bullet list is captured as `description`. Field names are canonical
    (Title, Publisher, Source-Type, URL, Archive, Retrieved, Local-Mirror);
    Cited-by is auto-generated and is not stored.
    """
    path = ROOT / REFERENCES_FILE
    if not path.exists():
        return {}
    refs: dict[str, Reference] = {}
    current: Reference | None = None
    description_lines: list[str] = []
    for line in path.read_text().splitlines():
        m = REFERENCE_HEADING.match(line)
        if m:
            if current is not None:
                current.description = "\n".join(description_lines).strip()
                refs[current.handle] = current
            current = Reference(handle=m.group(1))
            description_lines = []
            continue
        if current is None:
            continue  # skip preamble before first entry
        f = REFERENCE_FIELD.match(line)
        if f:
            field_name = f.group(1).strip().lower().replace("-", "_")
            value = f.group(2).strip()
            if field_name == "title":
                current.title = value
            elif field_name == "publisher":
                current.publisher = value
            elif field_name == "source_type":
                current.source_type = value.split()[0] if value else ""
            elif field_name == "url":
                current.url = value
            elif field_name == "archive":
                current.archive = value
            elif field_name == "retrieved":
                current.retrieved = value
            elif field_name == "local_mirror":
                current.local_mirror = value
            elif field_name == "short":
                current.short = value
            # `cited_by` is auto-generated; ignore any hand-written value.
        else:
            stripped = line.strip()
            if stripped and not stripped.startswith("---"):
                description_lines.append(line)
    if current is not None:
        current.description = "\n".join(description_lines).strip()
        refs[current.handle] = current
    return refs


def find_inline_handles(text: str) -> list[str]:
    """Return every `[Handle]` reference-style link in `text`.

    Excludes:
    - headings (any `#`-prefixed line)
    - fenced code blocks (toggled on triple-backtick or triple-tilde fences)
    - image links (filtered by the regex via the `!` lookbehind)
    - inline links of the form `[label](url)` (filtered by the regex via the
      lookahead for `(`)

    The result is a list (not a set) so the same handle cited twice on a
    page counts twice — useful for cited-by frequency in a future iteration.
    """
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        # Toggle fence state on triple-backtick or triple-tilde lines.
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = "```" if stripped.startswith("```") else "~~~"
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        if line.startswith("#"):
            continue
        # Strip inline code spans (`...`) before matching, so a literal
        # `[Handle]` appearing in prose-as-code-example doesn't register.
        scrubbed = re.sub(r"`[^`]*`", "", line)
        for m in INLINE_HANDLE.finditer(scrubbed):
            out.append(m.group(1))
    return out


def populate_cited_by(text: str) -> str:
    """Substitute every `Cited-by: _(auto-generated)_` line in the
    references-catalogue source with an actual list of citing files. Used
    by both build.py (monolith) and build_site.py (MkDocs page) so the
    rendered output everywhere shows the back-references.
    """
    cited = build_cited_by()
    out: list[str] = []
    current_handle: str | None = None
    for line in text.splitlines():
        m = re.match(r"^### (\S+)", line)
        if m:
            current_handle = m.group(1)
        if line.startswith("- **Cited-by:** _(auto-generated)_"):
            files = cited.get(current_handle or "", [])
            if files:
                names = ", ".join(f"`{f}`" for f in files)
                line = f"- **Cited-by:** {names}"
            else:
                line = "- **Cited-by:** _(no citations found in source)_"
        out.append(line)
    return "\n".join(out)


def build_cited_by() -> dict[str, list[str]]:
    """Walk every source markdown file under `taxonomy/` and return a map
    `{handle: [list of files citing it]}`. Used by build.py to substitute
    the `Cited-by: _(auto-generated)_` placeholder with the actual list at
    monolith-build time.

    Files included:
    - every entry in GROUP_FILES (the per-metric files)
    - the underscore-prefixed cross-cutting files at the catalogue root
      (`_standards-mapping.md`, `_outcomes-boundary.md`, etc.)

    Files excluded:
    - `_references.md` itself (intra-catalogue cross-references aren't
      cited-by relationships in the bibliographic sense)
    - the `_glossary.md` (no handle references expected)
    """
    cited: dict[str, set[str]] = {}
    files_to_walk: list[str] = list(GROUP_FILES.keys()) + [
        "_header.md",
        "_how-to-use.md",
        "_summary.md",
        "_tier-1-quick-reference.md",
        "_contents.md",
        "_applicability.md",
        "_standards-mapping.md",
        "_responsible-ai-lens.md",
        "_outcomes-boundary.md",
        "_calibration-and-context.md",
        "_gaps.md",
    ]
    for rel in files_to_walk:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text()
        for handle in find_inline_handles(text):
            cited.setdefault(handle, set()).add(rel)
    return {h: sorted(files) for h, files in cited.items()}


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def summary() -> dict:
    all_metrics = annotate_applicability(parse_all_metrics())
    # Parents (with sub-parts) are excluded from headline counts; the
    # countable units are flat metrics + sub-parts.
    parent_ids = {
        sp.parent_ref_id for sp in all_metrics if sp.parent_ref_id is not None
    }
    metrics = [m for m in all_metrics if m.ref_id not in parent_ids]
    gaps = parse_gaps()
    tiers = Counter(m.tier for m in metrics)
    return {
        "metric_count": len(metrics),
        "tier_counts": {str(k): v for k, v in sorted(tiers.items())},
        "group_count": len(GROUP_FILES),
        "gap_count": len(gaps),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summary(), indent=2))
