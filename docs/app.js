(function () {
  var CONFIG_ENDPOINT = 'https://tjcryyjrjxbcjzybzdow.supabase.co/functions/v1/hivemind-config';
  var TRIGGERS = ['cron', 'manual', 'reactive', 'event'];
  var EFFORTS = ['low', 'medium', 'high'];
  var VALUES = ['low', 'medium', 'high'];

  var state = {
    config: null,
    plays: [],
    allSkills: [],
    commentsByPlay: new Map(),
    totalComments: 0,
    graphData: null,
    graphInstance: null,
    filters: {
      search: '',
      trigger: new Set(),
      effort: new Set(),
      value: new Set(),
      skill: ''
    },
    sort: 'title'
  };

  var els = {
    loadingState: document.getElementById('loadingState'),
    errorState: document.getElementById('errorState'),
    menuToggle: document.getElementById('menuToggle'),
    topNav: document.getElementById('topNav'),
    searchInput: document.getElementById('searchInput'),
    sortSelect: document.getElementById('sortSelect'),
    triggerChips: document.getElementById('triggerChips'),
    effortChips: document.getElementById('effortChips'),
    valueChips: document.getElementById('valueChips'),
    skillSelect: document.getElementById('skillSelect'),
    clearFilters: document.getElementById('clearFilters'),
    countLabel: document.getElementById('countLabel'),
    playsGrid: document.getElementById('playsGrid'),
    browseEmpty: document.getElementById('browseEmpty'),
    backButton: document.getElementById('backButton'),
    permalink: document.getElementById('permalink'),
    playDetailCard: document.getElementById('playDetailCard'),
    commentsList: document.getElementById('commentsList'),
    commentsEmpty: document.getElementById('commentsEmpty'),
    graphMount: document.getElementById('graphMount'),
    statPlays: document.getElementById('statPlays'),
    statSkills: document.getElementById('statSkills'),
    statComments: document.getElementById('statComments'),
    topSkills: document.getElementById('topSkills'),
    views: {
      browse: document.getElementById('view-browse'),
      play: document.getElementById('view-play'),
      graph: document.getElementById('view-graph'),
      about: document.getElementById('view-about')
    }
  };

  init();

  async function init() {
    bindEvents();
    renderFilterChips();

    try {
      await loadInitialData();
      hideLoading();
      route();
    } catch (error) {
      showError(error instanceof Error ? error.message : String(error));
    }
  }

  function bindEvents() {
    window.addEventListener('hashchange', route);

    els.menuToggle.addEventListener('click', function () {
      var isOpen = els.topNav.classList.toggle('open');
      els.menuToggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', function (event) {
      if (!els.topNav.contains(event.target) && event.target !== els.menuToggle) {
        els.topNav.classList.remove('open');
        els.menuToggle.setAttribute('aria-expanded', 'false');
      }
    });

    els.searchInput.addEventListener('input', onFilterControlChange);
    els.sortSelect.addEventListener('change', onFilterControlChange);
    els.skillSelect.addEventListener('change', onFilterControlChange);

    els.clearFilters.addEventListener('click', function () {
      state.filters = {
        search: '',
        trigger: new Set(),
        effort: new Set(),
        value: new Set(),
        skill: ''
      };
      state.sort = 'title';
      location.hash = '#browse';
    });

    els.playsGrid.addEventListener('click', function (event) {
      var skillBtn = event.target.closest('[data-skill]');
      if (skillBtn) {
        event.preventDefault();
        goToBrowseWithSkill(skillBtn.getAttribute('data-skill'));
      }
    });

    els.playDetailCard.addEventListener('click', function (event) {
      var skillBtn = event.target.closest('[data-skill]');
      if (skillBtn) {
        event.preventDefault();
        goToBrowseWithSkill(skillBtn.getAttribute('data-skill'));
      }
    });

    els.backButton.addEventListener('click', function () {
      var detailRoute = parseRoute();
      var from = detailRoute.params.get('from');
      if (from) {
        var decoded = decodeURIComponent(from);
        location.hash = decoded.startsWith('#') ? decoded : '#browse';
        return;
      }

      if (window.history.length > 1) {
        window.history.back();
      } else {
        location.hash = '#browse';
      }
    });
  }

  async function loadInitialData() {
    var configResponse = await fetch(CONFIG_ENDPOINT);
    if (!configResponse.ok) {
      throw new Error('Failed to load hivemind config endpoint.');
    }
    state.config = await configResponse.json();

    var requests = [fetchPlays(), fetchGraphData(), fetchCommentsCount()];
    var results = await Promise.allSettled(requests);

    if (results[0].status !== 'fulfilled') {
      throw new Error('Failed to load plays from Supabase.');
    }

    state.plays = results[0].value;
    state.graphData = results[1].status === 'fulfilled' ? results[1].value : { nodes: [], links: [] };
    state.totalComments = results[2].status === 'fulfilled' ? results[2].value : 0;

    state.allSkills = buildAllSkills(state.plays);
    populateSkillSelect();
  }

  async function fetchPlays() {
    var url = new URL('/rest/v1/plays', state.config.supabase_url);
    url.searchParams.set('select', 'id,title,description,skills,trigger,effort,value,gotcha,source,replication_count,created_at');
    url.searchParams.set('order', 'title');

    var response = await fetch(url.toString(), {
      headers: {
        apikey: state.config.supabase_anon_key,
        Authorization: 'Bearer ' + state.config.supabase_anon_key
      }
    });

    if (!response.ok) {
      throw new Error('Supabase plays request failed with status ' + response.status);
    }

    var rows = await response.json();
    return rows.map(normalizePlay);
  }

  async function fetchCommentsCount() {
    var url = new URL('/rest/v1/comments', state.config.supabase_url);
    url.searchParams.set('select', 'id');
    url.searchParams.set('limit', '1');

    var response = await fetch(url.toString(), {
      headers: {
        apikey: state.config.supabase_anon_key,
        Authorization: 'Bearer ' + state.config.supabase_anon_key,
        Prefer: 'count=exact'
      }
    });

    if (!response.ok) {
      return 0;
    }

    var contentRange = response.headers.get('content-range') || '';
    var totalStr = contentRange.split('/')[1] || '0';
    var total = Number(totalStr);
    return Number.isFinite(total) ? total : 0;
  }

  async function fetchGraphData() {
    var response = await fetch('./graph-data.json');
    if (!response.ok) {
      throw new Error('Could not load graph-data.json');
    }
    return response.json();
  }

  async function fetchCommentsForPlay(playId) {
    if (state.commentsByPlay.has(playId)) {
      return state.commentsByPlay.get(playId);
    }

    var url = new URL('/rest/v1/comments', state.config.supabase_url);
    url.searchParams.set('play_id', 'eq.' + playId);
    url.searchParams.set('select', '*');
    url.searchParams.set('order', 'created_at');

    var response = await fetch(url.toString(), {
      headers: {
        apikey: state.config.supabase_anon_key,
        Authorization: 'Bearer ' + state.config.supabase_anon_key
      }
    });

    if (!response.ok) {
      throw new Error('Failed loading comments for play.');
    }

    var comments = await response.json();
    state.commentsByPlay.set(playId, comments);
    return comments;
  }

  function route() {
    var routeState = parseRoute();
    closeMobileMenu();
    setActiveNav(routeState.view);

    Object.keys(els.views).forEach(function (name) {
      els.views[name].classList.toggle('active', name === routeState.view);
    });

    if (routeState.view === 'browse') {
      applyBrowseParams(routeState.params);
      renderBrowse();
    } else if (routeState.view === 'play') {
      renderPlayDetail(routeState.id, routeState.params);
    } else if (routeState.view === 'graph') {
      renderGraph();
    } else if (routeState.view === 'about') {
      renderAbout();
    }
  }

  function parseRoute() {
    var raw = window.location.hash.replace(/^#/, '');
    if (!raw || raw === 'browse') {
      return { view: 'browse', params: new URLSearchParams() };
    }

    if (raw[0] === '?') {
      return { view: 'browse', params: new URLSearchParams(raw.slice(1)) };
    }

    var parts = raw.split('?');
    var path = parts[0] || '';
    var params = new URLSearchParams(parts[1] || '');

    if (path.indexOf('play/') === 0) {
      return { view: 'play', id: decodeURIComponent(path.slice(5)), params: params };
    }

    if (path === 'graph') {
      return { view: 'graph', params: params };
    }

    if (path === 'about') {
      return { view: 'about', params: params };
    }

    if (path === 'browse') {
      return { view: 'browse', params: params };
    }

    return { view: 'browse', params: new URLSearchParams() };
  }

  function applyBrowseParams(params) {
    state.filters.search = params.get('q') || '';
    state.filters.trigger = readSetParam(params.get('trigger'), TRIGGERS);
    state.filters.effort = readSetParam(params.get('effort'), EFFORTS);
    state.filters.value = readSetParam(params.get('value'), VALUES);

    var skill = params.get('skill') || '';
    state.filters.skill = state.allSkills.includes(skill) ? skill : '';

    var sort = params.get('sort') || 'title';
    state.sort = ['title', 'value', 'effort'].includes(sort) ? sort : 'title';

    syncControlsWithState();
  }

  function syncControlsWithState() {
    els.searchInput.value = state.filters.search;
    els.sortSelect.value = state.sort;
    els.skillSelect.value = state.filters.skill;

    syncChipGroup(els.triggerChips, state.filters.trigger);
    syncChipGroup(els.effortChips, state.filters.effort);
    syncChipGroup(els.valueChips, state.filters.value);
  }

  function syncChipGroup(container, selectedSet) {
    var chips = container.querySelectorAll('.chip');
    chips.forEach(function (chip) {
      var value = chip.getAttribute('data-value');
      chip.classList.toggle('active', selectedSet.has(value));
    });
  }

  function onFilterControlChange() {
    state.filters.search = els.searchInput.value.trim();
    state.filters.skill = els.skillSelect.value;
    state.sort = els.sortSelect.value;
    updateBrowseHashFromState();
  }

  function onChipClick(type, value) {
    var targetSet = state.filters[type];
    if (targetSet.has(value)) {
      targetSet.delete(value);
    } else {
      targetSet.add(value);
    }
    updateBrowseHashFromState();
  }

  function updateBrowseHashFromState() {
    var hash = buildBrowseHash(state.filters, state.sort);
    if (window.location.hash !== hash) {
      window.location.hash = hash;
      return;
    }
    renderBrowse();
  }

  function renderBrowse() {
    var filtered = state.plays.filter(function (play) {
      return matchesFilters(play, state.filters);
    });

    sortPlays(filtered, state.sort);

    var isFiltered = filtered.length !== state.plays.length;
    els.countLabel.innerHTML = 'Showing ' + (isFiltered ? '<span class="count-highlight">' + filtered.length + '</span>' : filtered.length) + ' of ' + state.plays.length + ' plays';
    els.browseEmpty.classList.toggle('hidden', filtered.length > 0);

    els.playsGrid.innerHTML = filtered
      .map(function (play) {
        return renderPlayCard(play);
      })
      .join('');
  }

  async function renderPlayDetail(playId, params) {
    var play = state.plays.find(function (p) {
      return String(p.id) === String(playId);
    });

    els.permalink.setAttribute('href', '#play/' + encodeURIComponent(playId));

    if (!play) {
      els.playDetailCard.innerHTML = '<h2 class="detail-title">Play not found</h2><p class="detail-text">This play id is not in the current dataset.</p>';
      els.commentsList.innerHTML = '';
      els.commentsEmpty.classList.remove('hidden');
      return;
    }

    var from = params.get('from');
    els.backButton.classList.remove('hidden');
    if (!from) {
      els.backButton.textContent = '← Back to browse';
    }

    els.playDetailCard.innerHTML =
      '<div class="detail-header">' +
      '<h1 class="detail-title">' +
      escapeHtml(play.title) +
      '</h1>' +
      '<div class="badges detail-meta">' +
      renderBadge('trigger', play.trigger) +
      renderBadge('effort', play.effort) +
      renderBadge('value', play.value) +
      '</div>' +
      '</div>' +
      '<p class="detail-text">' +
      escapeHtml(play.description || '') +
      '</p>' +
      (play.gotcha
        ? '<div class="detail-gotcha"><strong>Gotcha:</strong> ' + escapeHtml(play.gotcha) + '</div>'
        : '') +
      '<div class="pills">' +
      (play.skills || [])
        .map(function (skill) {
          return '<button class="skill-pill" data-skill="' + escapeAttribute(skill) + '">' + escapeHtml(skill) + '</button>';
        })
        .join('') +
      '</div>' +
      (play.replication_count > 0 ? '<p class="detail-text replication-count">' + play.replication_count + ' replication' + (play.replication_count !== 1 ? 's' : '') + '</p>' : '') +
      (playSourceUrl(play) ? '<p><a href="' + escapeAttribute(playSourceUrl(play)) + '" target="_blank" rel="noopener noreferrer">View source →</a></p>' : '');

    els.commentsList.innerHTML = '<p class="detail-text">Loading comments...</p>';
    els.commentsEmpty.classList.add('hidden');

    // Update the comment command with the actual play ID
    var cmdEl = document.getElementById('commentCmd');
    if (cmdEl) {
      cmdEl.textContent = 'hivemind comment ' + play.id.substring(0, 8) + ' "your comment"';
    }

    try {
      var comments = await fetchCommentsForPlay(play.id);
      renderCommentsThread(comments);
    } catch (_error) {
      els.commentsList.innerHTML = '<p class="detail-text">Could not load comments right now.</p>';
    }
  }

  function renderGraph() {
    if (state.graphInstance) {
      return;
    }

    state.graphInstance = window.HivemindGraph.mount(els.graphMount, state.graphData || { nodes: [], links: [] }, function (skill) {
      goToBrowseWithSkill(skill);
    });
  }

  function renderAbout() {
    els.statPlays.textContent = String(state.plays.length);
    els.statSkills.textContent = String(state.allSkills.length);
    els.statComments.textContent = String(state.totalComments);

    var skillCounts = countSkills(state.plays);
    var top = Object.entries(skillCounts)
      .sort(function (a, b) {
        if (b[1] !== a[1]) return b[1] - a[1];
        return a[0].localeCompare(b[0]);
      })
      .slice(0, 10);

    var max = top[0] ? top[0][1] : 1;
    els.topSkills.innerHTML = top
      .map(function (entry) {
        var pct = Math.max(4, Math.round((entry[1] / max) * 100));
        return (
          '<div class="skill-bar">' +
          '<span class="skill-bar-name">' +
          escapeHtml(entry[0]) +
          '</span>' +
          '<div class="skill-bar-track"><div class="skill-bar-fill" style="width:' +
          pct +
          '%"></div></div>' +
          '<span class="skill-bar-count">' +
          entry[1] +
          '</span>' +
          '</div>'
        );
      })
      .join('');
  }

  function renderCommentsThread(comments) {
    if (!comments.length) {
      els.commentsList.innerHTML = '';
      els.commentsEmpty.classList.remove('hidden');
      return;
    }

    els.commentsEmpty.classList.add('hidden');

    var byParent = new Map();
    comments.forEach(function (comment) {
      var key = comment.parent_id || '__root__';
      var list = byParent.get(key) || [];
      list.push(comment);
      byParent.set(key, list);
    });

    byParent.forEach(function (list) {
      list.sort(function (a, b) {
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      });
    });

    function renderNode(comment) {
      var kids = byParent.get(comment.id) || [];
      return (
        '<article class="comment-item">' +
        '<div class="comment-meta">' +
        '<span class="comment-author">' +
        escapeHtml(shortHash(comment.agent_hash)) +
        '</span>' +
        '<span class="comment-time">' +
        escapeHtml(formatDate(comment.created_at)) +
        '</span>' +
        '</div>' +
        '<p class="comment-body">' +
        escapeHtml(comment.body || '') +
        '</p>' +
        (kids.length
          ? '<div class="comment-children">' +
            kids
              .map(function (child) {
                return renderNode(child);
              })
              .join('') +
            '</div>'
          : '') +
        '</article>'
      );
    }

    var roots = byParent.get('__root__') || [];
    els.commentsList.innerHTML = roots
      .map(function (root) {
        return renderNode(root);
      })
      .join('');
  }

  function renderPlayCard(play) {
    var fromHash = encodeURIComponent(buildBrowseHash(state.filters, state.sort));
    var detailHash = '#play/' + encodeURIComponent(play.id) + '?from=' + fromHash;

    return (
      '<article class="play-card">' +
      '<div class="play-title-row">' +
      '<h3 class="play-title"><a href="' +
      detailHash +
      '">' +
      escapeHtml(play.title) +
      '</a></h3>' +
      (playSourceUrl(play) ? '<a class="source-link" href="' + escapeAttribute(playSourceUrl(play)) + '" target="_blank" rel="noopener noreferrer" aria-label="Source link">↗</a>' : '') +
      '</div>' +
      '<p class="play-desc">' +
      escapeHtml(play.description || '') +
      '</p>' +
      '<div class="pills">' +
      (play.skills || [])
        .map(function (skill) {
          return '<button class="skill-pill" data-skill="' + escapeAttribute(skill) + '">' + escapeHtml(skill) + '</button>';
        })
        .join('') +
      '</div>' +
      '<div class="badges">' +
      renderBadge('effort', play.effort) +
      renderBadge('value', play.value) +
      '</div>' +
      '</article>'
    );
  }

  function renderBadge(kind, rawValue) {
    var val = normalizeLevel(rawValue);
    if (!val) {
      return '';
    }
    var label = val === 'medium' ? 'med' : val;
    return '<span class="badge ' + kind + '-' + val + '">' + kind + ': ' + label + '</span>';
  }

  function matchesFilters(play, filters) {
    var searchNeedle = filters.search.toLowerCase();
    if (searchNeedle) {
      var hay = (play.title + ' ' + (play.description || '')).toLowerCase();
      if (hay.indexOf(searchNeedle) === -1) {
        return false;
      }
    }

    if (filters.trigger.size && !filters.trigger.has((play.trigger || '').toLowerCase())) {
      return false;
    }

    var effort = normalizeLevel(play.effort);
    if (filters.effort.size && !filters.effort.has(effort)) {
      return false;
    }

    var value = normalizeLevel(play.value);
    if (filters.value.size && !filters.value.has(value)) {
      return false;
    }

    if (filters.skill && !(play.skills || []).includes(filters.skill)) {
      return false;
    }

    return true;
  }

  function sortPlays(list, sortMode) {
    var valueRank = { high: 3, medium: 2, low: 1, '': 0 };
    var effortRank = { low: 1, medium: 2, high: 3, '': 4 };

    list.sort(function (a, b) {
      if (sortMode === 'value') {
        var av = valueRank[normalizeLevel(a.value) || ''] || 0;
        var bv = valueRank[normalizeLevel(b.value) || ''] || 0;
        if (bv !== av) return bv - av;
      } else if (sortMode === 'effort') {
        var ae = effortRank[normalizeLevel(a.effort) || ''] || 4;
        var be = effortRank[normalizeLevel(b.effort) || ''] || 4;
        if (ae !== be) return ae - be;
      }
      return a.title.localeCompare(b.title);
    });
  }

  function renderFilterChips() {
    buildChipGroup(els.triggerChips, TRIGGERS, 'trigger');
    buildChipGroup(els.effortChips, ['low', 'med', 'high'], 'effort');
    buildChipGroup(els.valueChips, ['low', 'med', 'high'], 'value');
  }

  function buildChipGroup(container, values, key) {
    container.innerHTML = values
      .map(function (value) {
        var normalized = value === 'med' ? 'medium' : value;
        return '<button class="chip" type="button" data-kind="' + key + '" data-value="' + normalized + '">' + value + '</button>';
      })
      .join('');

    container.addEventListener('click', function (event) {
      var chip = event.target.closest('.chip');
      if (!chip) {
        return;
      }
      var type = chip.getAttribute('data-kind');
      var value = chip.getAttribute('data-value');
      onChipClick(type, value);
    });
  }

  function populateSkillSelect() {
    var options = ['<option value="">All skills</option>']
      .concat(
        state.allSkills.map(function (skill) {
          return '<option value="' + escapeAttribute(skill) + '">' + escapeHtml(skill) + '</option>';
        })
      )
      .join('');

    els.skillSelect.innerHTML = options;
  }

  function readSetParam(raw, allowed) {
    var set = new Set();
    if (!raw) {
      return set;
    }

    raw
      .split(',')
      .map(function (part) {
        return part.trim().toLowerCase();
      })
      .forEach(function (val) {
        if (val === 'med') {
          val = 'medium';
        }
        if (allowed.indexOf(val) > -1) {
          set.add(val);
        }
      });

    return set;
  }

  function buildBrowseHash(filters, sort) {
    var params = new URLSearchParams();

    if (filters.search) params.set('q', filters.search);
    if (filters.trigger.size) params.set('trigger', Array.from(filters.trigger).sort().join(','));
    if (filters.effort.size) params.set('effort', Array.from(filters.effort).sort().join(','));
    if (filters.value.size) params.set('value', Array.from(filters.value).sort().join(','));
    if (filters.skill) params.set('skill', filters.skill);
    if (sort && sort !== 'title') params.set('sort', sort);

    var q = params.toString();
    return q ? '#browse?' + q : '#browse';
  }

  function goToBrowseWithSkill(skill) {
    var nextFilters = {
      search: '',
      trigger: new Set(),
      effort: new Set(),
      value: new Set(),
      skill: skill
    };
    var nextHash = buildBrowseHash(nextFilters, 'title');
    location.hash = nextHash;
  }

  function normalizePlay(row) {
    var skills = Array.isArray(row.skills)
      ? row.skills.filter(Boolean)
      : typeof row.skills === 'string'
      ? row.skills
          .replace(/[{}]/g, '')
          .split(',')
          .map(function (s) {
            return s.trim();
          })
          .filter(Boolean)
      : [];

    return {
      id: row.id,
      title: row.title || '(Untitled)',
      description: row.description || '',
      skills: skills,
      trigger: row.trigger || '',
      effort: normalizeLevel(row.effort),
      value: normalizeLevel(row.value),
      gotcha: row.gotcha || '',
      source: row.source || '',
      replication_count: row.replication_count || 0,
      created_at: row.created_at || ''
    };
  }

  function normalizeLevel(level) {
    if (!level) return '';
    var raw = String(level).toLowerCase();
    return raw === 'med' ? 'medium' : raw;
  }

  function countSkills(plays) {
    var map = {};
    plays.forEach(function (play) {
      (play.skills || []).forEach(function (skill) {
        map[skill] = (map[skill] || 0) + 1;
      });
    });
    return map;
  }

  function buildAllSkills(plays) {
    return Object.keys(countSkills(plays)).sort(function (a, b) {
      return a.localeCompare(b);
    });
  }

  function playSourceUrl(play) {
    if (play.source && play.source.startsWith('http')) {
      return play.source;
    }
    return null;
  }

  function shortHash(value) {
    var str = value || 'anonymous';
    if (str.length <= 12) return str;
    return str.slice(0, 8) + '...' + str.slice(-4);
  }

  function formatDate(value) {
    if (!value) return 'Unknown time';
    var date = new Date(value);
    if (Number.isNaN(date.getTime())) return 'Unknown time';
    return date.toLocaleString();
  }

  function setActiveNav(viewName) {
    var navMap = {
      browse: 'browse',
      play: 'browse',
      graph: 'graph',
      about: 'about'
    };
    var active = navMap[viewName] || 'browse';

    els.topNav.querySelectorAll('a[data-nav]').forEach(function (link) {
      link.classList.toggle('active', link.getAttribute('data-nav') === active);
    });
  }

  function closeMobileMenu() {
    els.topNav.classList.remove('open');
    els.menuToggle.setAttribute('aria-expanded', 'false');
  }

  function hideLoading() {
    els.loadingState.classList.add('hidden');
    els.errorState.classList.add('hidden');
  }

  function showError(message) {
    els.loadingState.classList.add('hidden');
    els.errorState.classList.remove('hidden');
    els.errorState.textContent = 'Unable to load app: ' + message;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replace(/`/g, '&#96;');
  }
})();
