/**
 * admin.js — contribution staging (Phase 3 groundwork).
 *
 * CRUD operations run entirely client-side against a localStorage
 * overlay ("staging area") on top of the canonical dataset. Nothing is
 * published automatically: the maintainer workflow is
 *   stage changes here → export JSON → maintainer reviews against cited
 *   sources → applies to data-sources/missions_timeline.md → rebuild.
 */

const BASE = window.__AP_MISSIONS__ || [];
const STORE_KEY = 'ap-staged-changes';

const form = document.getElementById('mission-form');
const tbody = document.getElementById('crud-tbody');
const stagedCount = document.getElementById('staged-count');
const formStatus = document.getElementById('form-status');
const formTitle = document.getElementById('form-title');
const cancelEdit = document.getElementById('btn-cancel-edit');
const btnExport = document.getElementById('btn-export');
const btnImport = document.getElementById('btn-import');
const btnDiscard = document.getElementById('btn-discard');

/** @type {{creates:Object[], updates:Object.<string,Object>, deletes:string[]}} */
let staged = loadStaged();

function loadStaged() {
  try {
    return (
      JSON.parse(localStorage.getItem(STORE_KEY)) || {
        creates: [],
        updates: {},
        deletes: [],
      }
    );
  } catch {
    return { creates: [], updates: {}, deletes: [] };
  }
}

function saveStaged() {
  localStorage.setItem(STORE_KEY, JSON.stringify(staged));
  render();
}

function slugify(name, year) {
  const s = String(name)
    .replace(/['’]/g, '-')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return `${s}-${year}`;
}

function allMissions() {
  const updated = new Map(BASE.map(m => [m.id, { ...m }]));
  Object.entries(staged.updates).forEach(([id, patch]) => {
    if (updated.has(id)) Object.assign(updated.get(id), patch);
  });
  staged.creates.forEach(c => updated.set(c.id, c));
  staged.deletes.forEach(id => updated.delete(id));
  return [...updated.values()].sort((a, b) => a.year - b.year);
}

/* ---------- table ---------- */

function rowFor(m) {
  let change = 'base';
  let cls = 'base-row';
  if (staged.deletes.includes(m.id)) {
    change = 'delete staged';
    cls = 'row-delete';
  } else if (staged.updates[m.id]) {
    change = 'update staged';
    cls = 'row-update';
  }
  if (staged.creates.some(c => c.id === m.id)) {
    change = 'create staged';
    cls = 'row-create';
  }

  return `
    <tr class="${cls}">
      <td class="mono">${m.id}</td>
      <td>${escHtml(m.name)}</td>
      <td class="mono">${m.year}</td>
      <td>${escHtml(m.status)}</td>
      <td>${change}</td>
      <td class="ops">
        <button type="button" data-act="edit" data-id="${m.id}">edit</button>
        ${change !== 'delete staged'
          ? `<button type="button" data-act="delete" data-id="${m.id}">retire</button>`
          : `<button type="button" data-act="undelete" data-id="${m.id}">restore</button>`}
      </td>
    </tr>`;
}

function escHtml(v) {
  const d = document.createElement('div');
  d.textContent = v ?? '';
  return d.innerHTML;
}

function render() {
  tbody.innerHTML = allMissions().map(rowFor).join('');
  const n =
    staged.creates.length +
    Object.keys(staged.updates).length +
    staged.deletes.length;
  stagedCount.textContent = `${n} staged`;
}

tbody.addEventListener('click', event => {
  const button = event.target.closest('button[data-act]');
  if (!button) return;
  const id = button.dataset.id;

  switch (button.dataset.act) {
    case 'edit': {
      const m = allMissions().find(x => x.id === id);
      if (!m) return;
      form._mode.value = 'edit';
      form.dataset.originalId = id;
      formTitle.textContent = `Editing ${id}`;
      cancelEdit.hidden = false;
      ['name', 'year', 'lead_partner', 'target', 'category',
        'status', 'outcome', 'era', 'intro'].forEach(k => {
        if (form.elements[k]) form.elements[k].value = m[k] || '';
      });
      break;
    }
    case 'delete':
      staged.deletes.push(id);
      saveStaged();
      break;
    case 'undelete':
      staged.deletes = staged.deletes.filter(x => x !== id);
      saveStaged();
      break;
    default:
      break;
  }
});

/* ---------- create / update ---------- */

form.addEventListener('submit', event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));

  const record = {
    name: data.name.trim(),
    year: parseInt(data.year, 10),
    lead_partner: data.lead_partner.trim(),
    target: data.target.trim(),
    category: data.category.trim(),
    status: data.status,
    outcome: data.outcome.trim(),
    era: data.era,
  };

  if (!record.name || !record.year || Number.isNaN(record.year)) {
    formStatus.textContent = 'name and year are required';
    return;
  }

  if (form._mode.value === 'edit') {
    const id = form.dataset.originalId;
    staged.updates[id] = record;
    formStatus.textContent = `staged update to ${id}`;
  } else {
    const id = slugify(record.name, record.year);
    if (allMissions().some(m => m.id === id)) {
      formStatus.textContent = `id collision: ${id} already exists`;
      return;
    }
    record.id = id;
    record.intro = data.intro?.trim() || '';
    staged.creates.push(record);
    formStatus.textContent = `staged creation of ${id}`;
  }

  form.reset();
  setCreateMode();
  saveStaged();
});

cancelEdit.addEventListener('click', () => {
  form.reset();
  setCreateMode();
});

function setCreateMode() {
  form._mode.value = 'create';
  delete form.dataset.originalId;
  formTitle.textContent = 'New mission record';
  cancelEdit.hidden = true;
}

/* ---------- export / import / discard ---------- */

btnExport.addEventListener('click', () => {
  const payload = {
    exportedAt: new Date().toISOString(),
    note: 'Staged contributions for AntarikshPedia — pending review.',
    creates: staged.creates,
    updates: staged.updates,
    deletes: staged.deletes,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `antarikshpedia-contributions-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
});

btnImport.addEventListener('click', () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'application/json';
  input.onchange = async () => {
    try {
      const parsed = JSON.parse(await input.files[0].text());
      staged = {
        creates: parsed.creates || [],
        updates: parsed.updates || {},
        deletes: parsed.deletes || [],
      };
      saveStaged();
      formStatus.textContent = 'imported staged changes';
    } catch (error) {
      formStatus.textContent = `import failed: ${error.message}`;
    }
  };
  input.click();
});

btnDiscard.addEventListener('click', () => {
  if (!confirm('Discard ALL staged changes? This cannot be undone.')) return;
  staged = { creates: [], updates: {}, deletes: [] };
  saveStaged();
  formStatus.textContent = 'staging cleared';
});

/* ---------- boot ---------- */

// base dataset injected at build time for the staging view
render();
