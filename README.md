# AntarikshPedia

A connected encyclopedia of humanity's journey into space. 209 missions,
1957 to today, explored as one story — with a page for every mission,
agency, and country, generated from a single canonical dataset.

## Architecture (Phase 2)

```
antarikshpedia/
├── data-sources/
│   └── missions_timeline.md     CANONICAL dataset — edit here, never elsewhere
├── scripts/build/               data pipeline (Python, stdlib only)
│   ├── gen-launch-dates.py      curated known launch dates → launch-dates.json
│   ├── generate-missions-json.py  md parser → src/_data/missions.json
│   ├── derive-catalogs.py       agencies/countries/relatedMissions derivation
│   ├── gen-stories.py           content/missions/*.md → stories.json
│   ├── enrich-missions.py       research pass: specs (Wikipedia infoboxes)
│   │                              + photos (NASA/Commons, license-gated)
│   ├── validate-data.py         guardrail — build fails on bad data
│   ├── media-overrides.json     per-image license records (survive rebuilds)
│   └── spec-overrides.json      researched mission specs (survive rebuilds)
├── content/missions/*.md        long-form stories (## Why it happened / ## The mission / ## Results)
├── src/
│   ├── _includes/base.njk       shared header/footer/nav/head + theme bootstrap
│   ├── _includes/partials/
│   ├── index.njk                homepage: journey + on-this-day
│   ├── catalog.njk              every mission grouped by era
│   ├── missions.njk             pagination → /missions/{slug}/
│   ├── agencies.njk + agency-pages.njk
│   ├── countries.njk + country-pages.njk
│   ├── vision.njk               project vision & roadmap
│   ├── admin.njk                contribution staging (CRUD, localStorage)
│   ├── styles/                  tokens.css is the master file; dark-only theme
│   ├── scripts/                 main.js (+theme toggle), home.js, search.js
│   │                              (Fuse.js)
│   └── assets/images/           licensed imagery; per-mission folders at
│                                  images/missions/<id>/photo.jpg
├── dist/                        BUILD OUTPUT — the only deployed directory
├── eleventy.config.js
└── package.json
```

## Commands

```bash
npm install          # once
npm run dev          # regenerate data + serve at localhost:8080 with watch
npm run build        # regenerate data + produce dist/
npm run validate     # data guardrail only
```

Deploy by pointing Netlify/Vercel/GitHub Pages at `dist/`. Build command:
`npm run build`, output directory: `dist`.

## The data pipeline (read before editing anything)

1. Edit `data-sources/missions_timeline.md` (one line per mission).
2. Run `npm run data`. The parser validates every entry (all fields
   non-empty, status from the allowed set, unique ids) and fails loudly on
   malformed input.
3. `src/_data/*.json` are generated outputs — never hand-edit them.
4. Image license records live in `scripts/build/media-overrides.json` and
   survive regeneration. Known precise launch dates live in
   `gen-launch-dates.py`.
5. Long-form mission stories go in `content/missions/<id>.md` with
   `## Why it happened`, `## The mission`, and/or `## Results` sections.
6. `npm run validate` runs automatically before every build.

## Contribution staging (/admin)

Create/edit/retire missions against a localStorage overlay. Export produces
a review JSON for a maintainer; nothing publishes automatically. This is
the Phase 3 groundwork described in the build prompt — swap localStorage
for Supabase when contributions open publicly.

## Media licensing

Every image carries a five-field record (`credit`, `license`, `source`,
`checked`) stored in `media-overrides.json` / rendered onto cards. Sourcing
rules per `copyright_guidelines.md`: NASA/ISRO/Commons-PD preferred;
CNSA/JAXA/Roscosmos avoided. See docs/image-credits.md.
