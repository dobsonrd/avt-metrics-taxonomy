---
title: Assurance Planner
description: Build a tailored assurance sequence by filtering metrics by tier and responsible actor.
---

# Assurance Planner

Select tiers and a responsible actor to build a sequenced view of relevant metrics, grouped by when they should be applied.

<div id="assurance-planner-app" class="ap-app">

<div class="ap-filters">
<div class="ap-filter-row">

<div class="ap-filter-group">
<span class="ap-filter-label">Tier</span>
<div class="ap-tier-buttons">
<button type="button" class="ap-tier-btn ap-active" data-tier="1">🟢 Tier 1</button>
<button type="button" class="ap-tier-btn ap-active" data-tier="2">🟡 Tier 2</button>
<button type="button" class="ap-tier-btn ap-active" data-tier="3">🔵 Tier 3</button>
</div>
</div>

<div class="ap-filter-group">
<span class="ap-filter-label">Responsible Actor</span>
<select id="ap-actor-select" class="ap-select"><option value="">All actors</option></select>
</div>

</div>
<div id="ap-summary" class="ap-summary"></div>
</div>

<div id="ap-results" class="ap-results"><p class="ap-loading">Loading metrics…</p></div>

</div>
