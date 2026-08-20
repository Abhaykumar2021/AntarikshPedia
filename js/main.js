// main.js
// Job of this file: load data/missions.json, then render it as a
// grouped, filterable timeline inside #timeline-container.
//
// Nothing about styling lives here (that's style.css) and nothing
// about content lives here (that's missions.json). This file only
// contains behavior: fetch data -> build HTML -> handle filter clicks.

const container = document.getElementById('timeline-container');
const filterBar = document.getElementById('filter-bar');

let allMissions = [];   // holds the full dataset once loaded
let activeFilter = 'all';

// Step 1: fetch the data file
fetch('data/missions.json')
  .then(response => response.json())
  .then(missions => {
    allMissions = missions;
    buildFilterButtons(allMissions);
    renderTimeline(allMissions);
  })
  .catch(error => {
    container.innerHTML = `<p>Could not load mission data. Check that data/missions.json exists.</p>`;
    console.error(error);
  });

// Step 2: build one filter button per unique lead/partner organization
// (e.g. "Soviet Union", "United States", "ESA", "India")
function buildFilterButtons(missions) {
  const leads = [...new Set(missions.map(m => m.lead_partner))].sort();

  leads.forEach(lead => {
    const btn = document.createElement('button');
    btn.className = 'filter-btn';
    btn.textContent = lead;
    btn.dataset.filter = lead;
    btn.addEventListener('click', () => handleFilterClick(lead));
    filterBar.appendChild(btn);
  });

  // The "All" button already exists in index.html — wire it up too
  document.querySelector('[data-filter="all"]')
    .addEventListener('click', () => handleFilterClick('all'));
}

function handleFilterClick(filterValue) {
  activeFilter = filterValue;

  // Update which button looks "active"
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === filterValue);
  });

  const filtered = filterValue === 'all'
    ? allMissions
    : allMissions.filter(m => m.lead_partner === filterValue);

  renderTimeline(filtered);
}

// Step 3: render missions, grouped by era, in chronological order
function renderTimeline(missions) {
  container.innerHTML = '';

  if (missions.length === 0) {
    container.innerHTML = '<p>No missions match this filter.</p>';
    return;
  }

  // Group missions by era while preserving the order eras first appear in
  const eraOrder = [];
  const grouped = {};

  missions.forEach(mission => {
    if (!grouped[mission.era]) {
      grouped[mission.era] = [];
      eraOrder.push(mission.era);
    }
    grouped[mission.era].push(mission);
  });

  eraOrder.forEach(era => {
    const heading = document.createElement('h2');
    heading.className = 'era-heading';
    heading.textContent = era;
    container.appendChild(heading);

    grouped[era].forEach(mission => {
      container.appendChild(buildMissionCard(mission));
    });
  });
}

// Maps a status string to a CSS class suffix, so each outcome type
// (Success / Partial success / Failure / In transit / Operational)
// gets its own badge color in style.css
function statusClass(status) {
  return 'status-' + status.toLowerCase().replace(/\s+/g, '-');
}

// Builds a single mission's HTML card
function buildMissionCard(mission) {
  const card = document.createElement('div');
  card.className = 'mission-card';

  const hasIntro = mission.intro && mission.intro.trim().length > 0;

  card.innerHTML = `
    <div class="mission-card-header">
      <span class="mission-name">${mission.name}</span>
      <span class="mission-meta">${mission.lead_partner} · ${mission.year}</span>
    </div>
    <div class="mission-subline">
      <span class="mission-target">${mission.target}</span>
      <span class="mission-category">${mission.category}</span>
      <span class="status-badge ${statusClass(mission.status)}">${mission.status}</span>
    </div>
    <div class="mission-outcome">${mission.outcome}</div>
    <div class="mission-intro ${hasIntro ? '' : 'empty'}">
      ${hasIntro ? mission.intro : 'Full write-up coming soon.'}
    </div>
  `;

  return card;
}
