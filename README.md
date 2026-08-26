# AntarikshPedia

A connected encyclopedia of humanity's journey into space. 209 missions,
1957 to today, each with its own page, linked to its agency, its country,
and the missions around it.

**Status: Phase 1.** The site is live, the full mission record is browsable,
and the foundation for deeper storytelling is in place.

## Built with agentic engineering

This project is an exercise in **vibe coding**: it is designed and curated
by a human, and built end to end by an AI agent working in long, supervised
sessions. Every template, style rule, data pipeline script, and research
pass you see here was produced by an agent, reviewed and directed by a
human, and committed in small, logged steps (see `Executions.md` for the
full work log and `codebase_context.md` for the project memory the agent
maintains).

The vision is to show how far agentic engineering can take a real,
content-heavy product: one person with a domain idea, an AI agent as the
engineering team, and a public record of how it was built. Phase 1 is the
encyclopedia itself. Later phases add depth (long-form stories for every
mission, more sourced media) and community (reviewed public contributions).

## Architecture

Static site, no frameworks, no database. One canonical dataset generates
every page.

```
data-sources/missions_timeline.md   CANONICAL DATASET — one line per mission
        │
        ▼  npm run data  (Python 3, stdlib only)
scripts/build/
├── gen-launch-dates.py            curated launch dates → launch-dates.json
├── generate-missions-json.py      parses the dataset → missions.json
├── derive-catalogs.py             derives agencies, countries, related missions
├── gen-stories.py                 compiles long-form stories → stories.json
└── validate-data.py               build fails loudly on bad data
        │
        ▼
src/_data/*.json                    GENERATED — never hand-edit
        │
        ▼  eleventy (npm run build)
src/                                templates, styles, scripts, assets
├── _includes/                      base layout, partials (cards, roster, marks)
├── index.njk                       home: hero, date section, evolution timeline
├── catalog.njk                     every mission grouped by era
├── missions.njk                    209 mission pages (paginated)
├── agencies.njk + agency-pages.njk 18 agency pages
├── countries.njk + country-pages.njk 15 country pages
├── vision.njk                      project vision
├── styles/                         tokens.css (design system), base, components
├── scripts/                        search (Fuse.js), theme, home, vision
└── assets/images/missions/         202 licensed mission photos
        │
        ▼
dist/                               BUILD OUTPUT — the only deployed directory
```

Key design decisions:

- **One source of truth.** Missions are edited only in
  `data-sources/missions_timeline.md`. Everything else is derived, so the
  209 records can never drift apart.
- **Validation as a guardrail.** `validate-data.py` checks required
  fields, allowed statuses, referential integrity, and image licenses on
  every build. Bad data fails the deploy instead of publishing.
- **Token-based theming.** `tokens.css` defines the entire look (dark
  telemetry console: amber accent, mono readouts). Components consume
  tokens only, so the site can be restyled from one file.
- **Build-time computation.** Date-based sections ("On this day", "Around
  this date") are computed when the site builds; a nightly scheduled
  rebuild keeps them current.

## The data

- **Missions (209).** Name, year, lead partner, target, category, outcome,
  status (Success, Partial success, Failure, In transit, Operational), and
  era (six eras from 1957 to present). Stored as one markdown line per
  mission in `data-sources/missions_timeline.md`.
- **Agencies (18) and countries (15).** Derived automatically from the
  mission records, with hand-written factual overviews.
- **Related missions.** Rule-based links between missions (same target,
  same program, competitors) with a scoring window in years.
- **Launch dates.** ~70 curated landmark dates, plus researched dates from
  Wikipedia infoboxes. Dates that are not confirmed stay unknown rather
  than guessed.
- **Specifications.** Launch vehicle, mass, orbit, and duration for ~150
  missions, researched from Wikipedia infoboxes into
  `scripts/build/spec-overrides.json`.
- **Images.** 202 of 209 missions have photos: NASA Image Library (public
  domain) and Wikimedia Commons (PD/CC licenses), each with a five-field
  license record (credit, license, source, check date). Two ISRO missions
  use GODL-India; one uses a rights-managed Getty photo by explicit
  decision (see `docs/image-credits.md`).
- **Stories.** Seven long-form mission histories so far
  (`content/missions/*.md`). Missions without one say so honestly instead
  of inventing copy.

## Local development

```bash
npm install          # once
npm run dev          # regenerate data + serve localhost:8080 with watch
npm run build        # regenerate data + produce dist/
npm run validate     # data guardrail only
```

Requires Node 18+ and Python 3 (stdlib only; nothing to pip install).

## Deployment

The site deploys automatically to **Cloudflare Pages** from this
repository:

- Every push to `main` triggers a build (`npm run build`) and goes live on
  [antarikshpedia.space](https://antarikshpedia.space) in a couple of
  minutes.
- A nightly GitHub Actions workflow (`.github/workflows/daily-rebuild.yml`)
  triggers a rebuild so the date-based sections stay current. It reads the
  Cloudflare build hook URL from the repository secret `CF_BUILD_HOOK`.

## Media licensing

Every image carries a five-field record (credit, license, source, check
date) stored in `scripts/build/media-overrides.json` and rendered on
mission pages. Sourcing rules per `copyright_guidelines.md`: NASA/ISRO and
Commons public-domain imagery preferred; agency logos never appear in the
interface. Full ledger in `docs/image-credits.md`.

## Roadmap

- **Phase 1 (now).** The complete mission record, browsable and
  cross-linked, with researched imagery and specifications.
- **Phase 2.** Depth: long-form sourced stories for every mission, more
  verified media, per-era landing pages.
- **Phase 3.** Community: public corrections and additions staged as
  pending until a reviewer approves them against a cited source.
