(function () {
  'use strict';

  var GROUPS = [
    {
      key: 'pre-deployment',
      label: 'Pre-deployment',
      subtitle: 'Apply before go-live or on day zero of deployment (includes Day Zero Baseline metrics).',
      match: function (cadences, lifecycle) {
        return cadences.indexOf('One-off gate') !== -1 ||
               lifecycle.indexOf('Pre-deployment') !== -1 ||
               lifecycle.indexOf('Day Zero Baseline') !== -1;
      }
    },
    {
      key: 'continuous',
      label: 'Continuous',
      subtitle: 'Monitor throughout live deployment.',
      match: function (cadences, lifecycle) {
        return lifecycle.indexOf('Continuous') !== -1 ||
               cadences.indexOf('Continuous') !== -1;
      }
    },
    {
      key: 'periodic',
      label: 'Periodic audit',
      subtitle: 'Apply on a scheduled review cycle.',
      match: function (cadences, lifecycle) {
        return lifecycle.indexOf('Periodic Audit') !== -1 ||
               cadences.indexOf('Periodic audit') !== -1;
      }
    },
    {
      key: 'event-triggered',
      label: 'Event-triggered',
      subtitle: 'Apply in response to specific incidents or changes.',
      match: function (cadences) {
        return cadences.indexOf('Event-triggered') !== -1;
      }
    }
  ];

  // Maps granular metric-level actor values to the 5 canonical groups
  // defined in the How to Use section. Clinician and Caldicott Guardian
  // are deployer-side roles and group under Deployer for filtering.
  var ACTOR_CANONICAL = {
    'Vendor':             'Vendor',
    'Deployer':           'Deployer',
    'Clinician':          'Deployer',
    'Caldicott Guardian': 'Deployer',
    'Regional (ICB)':     'Regional (ICB)',
    'National Body':      'National Body',
    'Academic':           'Academic'
  };

  var CANONICAL_ORDER = ['Vendor', 'Deployer', 'Regional (ICB)', 'National Body', 'Academic'];

  function canonicalActor(raw) {
    return ACTOR_CANONICAL[raw] || raw;
  }

  function splitSemicolon(value) {
    if (!value) return [];
    return value.split(';').map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function splitComma(value) {
    if (!value) return [];
    return value.split(',').map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function splitField(value) {
    if (!value) return [];
    return value.split(/[;,]/).map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function getCadences(metric) {
    return splitSemicolon((metric.dimensions || {})['Measurement Cadence']);
  }

  function getLifecycle(metric) {
    return splitComma((metric.dimensions || {})['Lifecycle Phases']);
  }

  function getActors(metric) {
    return splitField((metric.dimensions || {})['Responsible Actors']);
  }

  function groupUrl(metric) {
    var f = (metric.group_file || '').split('/').pop().replace(/\.md$/, '');
    return '../groups/' + f + '/';
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderCard(m) {
    var actors = getActors(m).join(', ') || '—';
    var aq = (m.dimensions || {})['Assurance Question'] || '—';
    return '<div class="ap-card">' +
      '<div class="ap-card-header">' +
        '<a class="ap-ref" href="' + groupUrl(m) + '">' + escapeHtml(m.ref_id) + '</a>' +
        '<span class="ap-tier-icon">' + escapeHtml(m.tier_icon || '') + ' Tier ' + escapeHtml(m.tier) + '</span>' +
      '</div>' +
      '<div class="ap-card-name">' + escapeHtml(m.name || '') + '</div>' +
      '<div class="ap-card-meta"><span class="ap-label">Actor:</span> ' + escapeHtml(actors) + '</div>' +
      '<div class="ap-card-meta"><span class="ap-label">Assurance question:</span> ' + escapeHtml(aq) + '</div>' +
    '</div>';
  }

  function renderGroup(group, metrics) {
    var countClass = metrics.length === 0 ? 'ap-count ap-count-empty' : 'ap-count';
    var body = metrics.length === 0
      ? '<p class="ap-empty">No metrics match the current filters.</p>'
      : '<div class="ap-cards">' + metrics.map(renderCard).join('') + '</div>';
    return '<section class="ap-group">' +
      '<h2 class="ap-group-title">' + escapeHtml(group.label) +
        ' <span class="' + countClass + '">' + metrics.length + '</span></h2>' +
      '<p class="ap-group-subtitle">' + escapeHtml(group.subtitle) + '</p>' +
      body +
    '</section>';
  }

  function render(allMetrics, tiers, actor) {
    var filtered = allMetrics.filter(function (m) {
      if (tiers.indexOf(String(m.tier)) === -1) return false;
      if (actor) {
        var matches = getActors(m).some(function (a) {
          return canonicalActor(a) === actor;
        });
        if (!matches) return false;
      }
      return true;
    });

    var summary = document.getElementById('ap-summary');
    if (summary) {
      summary.textContent = 'Showing ' + filtered.length + ' of ' + allMetrics.length + ' metrics';
    }

    var results = document.getElementById('ap-results');
    if (results) {
      results.innerHTML = GROUPS.map(function (group) {
        var groupMetrics = filtered.filter(function (m) {
          return group.match(getCadences(m), getLifecycle(m));
        });
        return renderGroup(group, groupMetrics);
      }).join('');
    }
  }

  function init(data) {
    var allMetrics = data.metrics || [];
    var actorSelect = document.getElementById('ap-actor-select');

    function getSelectedTiers() {
      var tiers = [];
      document.querySelectorAll('.ap-tier-btn.ap-active').forEach(function (el) {
        tiers.push(el.getAttribute('data-tier'));
      });
      return tiers;
    }

    function refreshActorDropdown(tiers) {
      var previous = actorSelect.value;
      var tierFiltered = allMetrics.filter(function (m) {
        return tiers.indexOf(String(m.tier)) !== -1;
      });
      var canonicalSet = {};
      tierFiltered.forEach(function (m) {
        getActors(m).forEach(function (a) { canonicalSet[canonicalActor(a)] = true; });
      });

      actorSelect.innerHTML = '<option value="">All actors</option>';
      CANONICAL_ORDER.forEach(function (group) {
        if (!canonicalSet[group]) return;
        var opt = document.createElement('option');
        opt.value = group;
        opt.textContent = group;
        actorSelect.appendChild(opt);
      });

      actorSelect.value = canonicalSet[previous] ? previous : '';
    }

    function update() {
      render(allMetrics, getSelectedTiers(), actorSelect.value);
    }

    document.querySelectorAll('.ap-tier-btn').forEach(function (el) {
      el.addEventListener('click', function () {
        el.classList.toggle('ap-active');
        refreshActorDropdown(getSelectedTiers());
        update();
      });
    });
    actorSelect.addEventListener('change', update);

    refreshActorDropdown(getSelectedTiers());
    update();
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!document.getElementById('assurance-planner-app')) return;

    fetch('../downloads/metrics.json')
      .then(function (r) { return r.json(); })
      .then(init)
      .catch(function (err) {
        var el = document.getElementById('ap-results');
        if (el) el.innerHTML = '<p class="ap-error">Failed to load metrics data. Please refresh the page.</p>';
        console.error('Assurance planner:', err);
      });
  });
})();
