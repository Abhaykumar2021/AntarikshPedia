# AntarikshPedia

A connected encyclopedia of humanity's journey into space. This repo is the v1
"timeline" build: a chronological, filterable list of landmark space missions
and spacecraft from 1957 to today.

## What's in this repo

```
antarikshpedia/
├── index.html          The single page — structure only, no styling or logic
├── css/style.css        All visual styling
├── js/main.js            All behavior: loads data, builds the timeline, handles filters
├── data/missions.json     The content — every mission as a structured record
├── assets/images/          Mission photos/graphics (empty for now)
└── docs/                    Working notes on the data model and decisions
```

## How to run this locally

No build step, no install required for v1. Two options:

1. **Simplest**: double-click `index.html` to open it in a browser.
   Note: some browsers block `fetch()` from loading local files this way,
   so if the timeline doesn't appear, use option 2.

2. **Recommended**: run a tiny local server so `fetch('data/missions.json')`
   works properly.
   - If you have VS Code's **Live Server** extension installed, right-click
     `index.html` and choose "Open with Live Server."
   - Or, from a terminal in this folder, run: `python3 -m http.server 8000`
     then open `http://localhost:8000` in your browser.

## How to add or edit a mission

Open `data/missions.json`. Each mission is one object:

```json
{
  "id": "sputnik-1-1957",
  "name": "Sputnik 1",
  "year": "1957",
  "lead_partner": "Soviet Union",
  "target": "Earth orbit",
  "category": "Technology / Earth orbit",
  "status": "Success",
  "outcome": "First artificial satellite; began the space age.",
  "era": "1957–1969: Opening the Space Age",
  "intro": "Launched by the Soviet Union on 4 October 1957..."
}
```

Add a new object to the list, or edit an existing one's `intro` field.
You do not need to touch `index.html`, `style.css`, or `main.js` to add content —
that's the point of keeping data separate from code.

## Deploying

This is a static site — no server-side code. It can be deployed for free on
Vercel, Netlify, or GitHub Pages by pointing them at this folder. No build
command is needed since there's no framework/bundler involved yet.

## Status

- v1 scope: timeline listing with filters, no individual mission pages yet.
- 89 missions loaded from the curated dataset (replaced an earlier, less
  selective seed list in August 2026); each entry now includes lead/partner
  org, target, category, and a Success/Partial/Failure/In transit/Operational
  status badge.
- Intro write-ups in progress — a handful carried over from the earlier
  dataset, most entries still show "Full write-up coming soon."
- Data model will need to expand for Phase 2 (Programs, Spacecraft detail
  pages, cross-links) — see `docs/data-model-notes.md`.
