# codebase_context.md

> **Purpose:** Complete context for the AntarikshPedia codebase so a fresh
> model session can resume work without re-reading the whole repo.
> Last updated: 2026-08-26 (Execution #16).

## 0. Laws (from the user — always in force)

1. Always follow the law.
2. **Always ask before making any commits.**
3. **Update `codebase_context.md` after every task execution**, and keep
   these laws recorded in this file.
4. **All generated visitor-facing text must be humanized per
   Wikipedia:Signs of AI writing (WP:AISIGNS) before a task is considered
   done** — no puffery, no "not just X but Y", no rule-of-three rhetoric,
   **no em dashes in prose**, plain factual sentences.
5. **AI builds this project, but the result must never feel AI-made.**
6. **All images belong under `src/assets/`** — never loose in the repo
   root. Moving images must never break site integration: verify every
   reference after a move.

Also standing: before executing any task, write a summary + expected output
in `Executions.md` with a timestamp; never get stuck in a loop — terminate a
stuck task and find another method or skip it with a note in `Executions.md`.

Commit history of note:
- `4447995` (2026-08-26) — README rewrite, absolute og:image, nightly
  rebuild workflow, wrangler.toml pinning dist (fixes first Cloudflare
  deploy error from the Workers-style flow).
- `3f48b6e` (2026-08-25) — Executions #4–#13: site-wide style fixes,
  humanized copy, /admin removal, home redesign (evolution timeline,
  on-this-day fallback), brand assets, 57 new mission thumbnails
  (202/209), related-rail thumbnail fix.
- `6ae5c32` (2026-08-24) — flip-book removal, dark-only theme, vision
  page redesign, Carina Nebula hero, context/log docs.
The root `Carina Nebula.jpg` original is intentionally untracked; the
site uses `src/assets/images/carina-nebula.jpg`.

## 14. Brand assets (added 2026-08-24, Execution #3)

- Source: `Logos/Title Logo.png` (Earth + JWST artwork, 1024², untracked)
  and `Logos/logo.jpeg` (full lockup with wordmark, untracked).
- Derived (committed) into `src/assets/brand/` via `sips` center-crop
  (560² around the Earth, watermark excluded):
  - `logo-mark.png` (256²) — header brand image (`.brand-mark`, 28px circle,
    amber glow on hover) in `base.njk`.
  - `favicon.png` (64²) + `apple-touch-icon.png` (180²) — linked in `base.njk` head.
  - `og-image.jpg` — copy of `logo.jpeg` for `og:image` (relative URL; make
    absolute if a canonical domain is ever configured).
- To regenerate: re-run the sips crop/resize chain documented in
  `Executions.md` Execution #3.

## 15. Deployment (set up 2026-08-26, Execution #14)

- **Target:** Cloudflare Pages, free tier (chosen over Netlify: Netlify's
  2026 credit pricing allows only ~20 production deploys/month free, which
  daily rebuilds would exceed; Cloudflare gives 500 builds + unlimited
  bandwidth, no credit card). Repo stays PRIVATE.
- **Auto-deploy:** every push to `main` → Cloudflare builds
  `npm run build` (Python 3 available in its build image) → live on
  `https://antarikshpedia.space`.
- **Deploy command gotcha (Execution #16):** the project's deploy step
  MUST be `npx wrangler pages deploy dist --project-name=antarikshpedia`
  (set in the Cloudflare dashboard, Settings > Build). A plain
  `npx wrangler deploy` fails with "Missing entry-point" — it expects a
  Worker script or `[assets]` config, and `pages_build_output_dir` in
  wrangler.toml does not apply to it.
- **Nightly rebuild:** `.github/workflows/daily-rebuild.yml` cron
  (`30 19 * * *` = 01:00 IST) POSTs to the Cloudflare build hook stored in
  the GitHub repo secret `CF_BUILD_HOOK` (workflow skips gracefully if
  unset). Keeps "Around this date in space history" current.
- **DNS:** `antarikshpedia.space` must be a Cloudflare zone (registrar
  nameservers pointed at Cloudflare) for the apex domain; SSL auto-issued.
- **og:image is an absolute URL** (`https://antarikshpedia.space/...`) —
  keep it absolute; relative URLs break social scrapers.
- Fallback if Cloudflare's build image ever lacks Python 3: build in
  GitHub Actions and deploy with `wrangler pages deploy` (still $0).

---

## 1. What this project is

**AntarikshPedia v2.0.0** — "A connected encyclopedia of humanity's journey
into space." A static site covering **209 missions (1957 → present)**, with a
page for every mission, agency, and country, all generated from **one
canonical dataset**. MIT license. Author credit: Abhay Kumar.

- Stack: **Eleventy 3.1** (`"type": "module"`), Python 3 stdlib data pipeline,
  **Fuse.js 7.5** (vendored ESM at `src/scripts/vendor/fuse.mjs`).
- No frameworks, no bundler. Plain NJK templates + CSS + ES modules.
- Deploy target: `dist/` only (Netlify/Vercel/GH Pages; build cmd `npm run build`, output `dist`).

## 2. Commands

```bash
npm install          # once
npm run dev          # regen data + serve localhost:8080 with watch
npm run build        # regen data + produce dist/
npm run build:fast   # eleventy only (skip data regen)
npm run validate     # data guardrail only
npm run data         # full python pipeline (see §6)
```

## 3. Repo layout (top level)

```
data-sources/missions_timeline.md   CANONICAL dataset — edit here ONLY
scripts/build/                      Python pipeline + override JSONs
content/missions/*.md               long-form stories (7 of 209 written)
src/                                Eleventy input (templates/styles/scripts/assets)
src/_data/*.json                    GENERATED outputs — never hand-edit
dist/                               BUILD OUTPUT (gitignored) — deployed
docs/                               data-model-notes.md, image-credits.md
Bugs/                               screenshots (gitignored)
Logos/                              project's own Title Logo.png, logo.jpeg
Carina Nebula.jpg                   hero background source image (repo root)
copyright_guidelines.md             media policy reference (gitignored)
eleventy.config.js                  Eleventy config
Executions.md                       running task-execution log
codebase_context.md                 THIS FILE
```

## 4. Eleventy config (`eleventy.config.js`)

- Input `src/` → output `dist/`; includes `_includes`, data `_data`.
- `templateFormats: ['njk','md']`, `htmlTemplateEngine: 'njk'`.
- Passthrough copies: `src/assets→assets`, `src/styles→styles`,
  `src/scripts→scripts`, `src/admin→admin`.
- **Filters** (all via `addFilter`, no collections):
  - `missionById(missions, id)` — find by id
  - `push(arr, item)` — mutating push returning arr (Nunjucks `set` scoping workaround)
  - `relGraph(mission, related)` — radial SVG relationship graph (640×300), links to `/missions/{id}/`
  - `humanDate(iso)` — `1957-10-04` → `4 Oct 1957`
  - `numberFormat(n)` — thousands separators
  - `initials(name)` — strips the/of/and/for, max 3 letters (wordmark badges)
  - `findCountry(countries, id)`
  - `onThisDay(missions)` — missions whose launch_date MM-DD == today (build time!)
  - `eraAccent(era)` / `eraIndex(era)` — era string prefix → CSS var index 1–6
    (prefixes `1957–1969:`, `1970–1985:`, `1986–2000:`, `2001–2012:`,
    `2013–2020:`, `2021–Present:`)
  - `sortByYear(missions)`

## 5. Pages & templates (`src/*.njk`, all extend `base.njk`)

| Template | URL | Notes |
|---|---|---|
| `index.njk` | `/` | Homepage. `.journey-hero` hero (Carina Nebula bg) + facts-strip (top margin `--space-8` below CTAs), history section via `missions \| onThisDay` with fallback `missions \| nearestAnniversaries` ("Around this date in space history", 4 closest launch anniversaries to today — build-time), `.evo-strip` evolution timeline: 9 milestones (sputnik-1, sputnik-2, vostok-1, apollo-11, pioneer-10, voyager-1-2, hubble, zarya-iss, jwst) on a central spine that grows as you scroll (`home.js` sets `--growth`; reduced-motion → full), era-colored nodes branching alternately, single-column ≤760px. Loads `/scripts/home.js`. Uses `extraStyles: ['landing-journey.css']`. |
| `catalog.njk` | `/catalog/` | All missions grouped by era; derives unique eras via `push` filter; mission cards per era block. |
| `missions.njk` | `/missions/{id}/` ×209 | Pagination over `missions` (size 1, alias `mission`). Hero (media or `hero-deep-field.jpg` fallback), facts strip, story sections (why/story/results or honest "pending" note), related-missions SVG graph + rail (relatedFull records carry `media` + `era` — added Execution #13; without them rail cards rendered letter placeholders), sources & credits. JSON-LD schema via `schema` var. |
| `agencies.njk` | `/agencies/` | Card grid of 18 agencies (photo/mark, overview truncated 140 chars, country chip). |
| `agency-pages.njk` | `/agencies/{slug}/` ×18 | Facts strip + chronological `roster-timeline.njk` roster + sibling agencies. |
| `countries.njk` | `/countries/` | Card grid of 15 countries using `flag()` macro. |
| `country-pages.njk` | `/countries/{slug}/` ×15 | Flag head + facts strip + roster timeline. |
| `vision.njk` | `/vision/` | Vision page (redesigned 2026-08-24, `extraStyles: ['vision.css']` + `/scripts/vision.js`): full-screen starfield-canvas hero with nebula glows, gradient-glow display headline, count-up stats strip (missions/agencies/countries/years), knowledge-chain rendered as an animated "constellation" (glowing nodes on a line with a traveling signal pulse, staggered scroll reveal, vertical variant ≤760px), phase cards with ghost numbers + pulsing "live" dot on Phase 1, Tsiolkovsky manifesto quote, editorial-standard card + CTA. |
| `admin.njk` | REMOVED 2026-08-24 (Execution #5) | Contribution staging UI deleted from build at user request ("for now"); code recoverable from git history (`src/admin.njk`, `src/admin/admin.js`, passthrough `src/admin→admin`). Footer link and the "Propose this write-up" chip on mission pages removed too. |

### `src/_includes/base.njk` (shared layout)
- Head: conditional title (`{{ title }} — AntarikshPedia`), meta description,
  OG tags, Google Fonts (**Space Grotesk** display / **Inter** body /
  **JetBrains Mono** mono).
- **Theme bootstrap inline script before first paint**: reads
  `localStorage['ap-theme']`, falls back to `prefers-color-scheme`, sets
  `<html data-theme>`.
- Stylesheets always loaded: `/styles/tokens.css`, `base.css`, `components.css`;
  then `{% for sheet in extraStyles %}` loop for page-specific CSS.
- Optional JSON-LD via `{% if schema %}`.
- Body: skip-link → sticky header (brand, global search form
  `#global-search-form`/`#global-search-input`/results `#global-results`,
  nav Home/Catalog/Agencies/Countries/Vision with `aria-current` driven by
  `section` variable, `#theme-toggle`) → `<main>{{ content }}</main>` → footer
  (links incl. /admin/, credits).
- Injects search dataset snapshot: `<script type="application/json"
  id="all-missions">{{ missions | sortByYear | dump | safe }}</script>`.
- Loads `/scripts/main.js` (defer) + `/scripts/global-search.js` (module).

### Partials (`src/_includes/partials/`)
- `mission-card.njk` — one card for an `m` in caller scope: media img or
  letter placeholder (`--ph-accent`), title row + status badge, meta
  (lead_partner · year), outcome, chips (target/category).
- `roster-timeline.njk` — vertical chronological list for agency/country
  pages; each item gets `--era-accent`; the whole `.rt-card` is clickable
  via a stretched link to `/missions/{id}/` (Execution #7).
- `marks.njk` — macros: `flag(iso,name,size=40)` (from
  `/assets/images/flags/<iso>.png`, 🌐 fallback), `agency_mark(name,size)`
  (text initials — deliberate: agency logos are trademarked, never used),
  `agency_photo(agency,missions)` (first mission photo path).

## 6. Data pipeline (`npm run data` = scripts/build/*.py, stdlib only)

Order: `gen-launch-dates.py && generate-missions-json.py && derive-catalogs.py && gen-stories.py && validate-data.py`

1. **gen-launch-dates.py** — hard-coded dict of ~60 curated landmark launch
   dates → `launch-dates.json`. Philosophy: only unambiguous historical facts.
2. **generate-missions-json.py** — sole producer of `missions.json`. Parses
   canonical md lines:
   `- **Name** (Year) — Lead/partner · Target · Category — Outcome. [Status]`
   under era headings `## YYYY–YYYY: Title`. `slugify(name,year)` lowercases,
   apostrophes→hyphens, appends year. Strict validation (9 fields non-empty,
   status whitelist, unique ids) exits non-zero on errors. Then merges:
   `media-overrides.json` (media block; default thumb
   `assets/images/missions/<id>/photo.jpg`), `launch-dates.json`,
   `spec-overrides.json`.
3. **derive-catalogs.py** — from missions.json derives `agencies.json`
   (18 records, built-in registry), `countries.json` (15, computed
   agency/mission ids), `relatedMissions.json` (rule-based scoring:
   same_target 100−Δy ≤12 yrs, same_program 60−Δy ≤8, competitor 30−Δy ≤2;
   top 4 each). Unmapped lead_partner token ⇒ hard failure.
4. **gen-stories.py** — `content/missions/<id>.md` → `stories.json`
   (`## Why it happened`→why, `## The mission`→story, `## Results`→results,
   paragraphs wrapped in `<p>`).
5. **validate-data.py** — guardrail: required fields, allowed statuses, dup
   ids, referential integrity (relatedMissions ids, agency↔country, every
   mission must belong to ≥1 agency), media blocks need all five fields
   (thumb/credit/license/source/checked) and thumb file exists on disk, ISO
   date regex, numeric mass_kg. Exits non-zero w/ up to 40 errors.
6. **enrich-missions.py** — MANUAL/offline research pass (resumable,
   0.15s politeness delay; `python3 scripts/build/enrich-missions.py
   [limit] [chronological|newest]`): Wikipedia infobox specs →
   spec-overrides.json; NASA Image Library then Wikimedia Commons
   (license-gated PD/CC0/CC BY(-SA) + space-category gate, width ≥500) →
   photo into `src/assets/images/missions/<id>/` + record appended to
   media-overrides.json. Credits use " · " (never em dashes). Coverage
   after Execution #12: **202/209 missions have photos**; the 7 without
   (luna-19, bhaskara-1, tenma, sakigake, suisei, ginga, sross-c2) have no
   usable free-licensed image ≥500px on NASA/Commons — they render letter
   placeholders. Two ISRO missions (astrosat, xposat) use GODL-India
   (ISRO's standard free license; accepted deliberately for ISRO imagery,
   which the project guidelines prefer).

**Override files** (`scripts/build/`): `media-overrides.json` (~125 entries —
five-field license records that survive rebuilds), `spec-overrides.json`
(88 entries: launch_vehicle/mass_kg/orbit_type/duration).

## 7. Canonical dataset format (`data-sources/missions_timeline.md`)

Six era headings; 209 lines like:

```
- **Sputnik 1** (1957) — Soviet Union · Earth orbit · Technology / Earth orbit — First artificial satellite; began the space age. [Success]
```

Statuses allowed: `Success`, `Partial success`, `Failure`, `In transit`,
`Operational`. **Edit here, run `npm run data`; never hand-edit `src/_data/*.json`.**

## 8. Mission record shape (`src/_data/missions.json`)

Required: `id, name, year(int), lead_partner, target, category, status,
outcome, era`. Optional: `launch_date` (ISO), `launch_vehicle`, `mass_kg`,
`orbit_type`, `duration`, `intro`, `media{thumb,credit,license,source,checked}`.

Other generated data: `agencies.json` {id,slug,name,country,founded_year,overview,mission_ids[]},
`countries.json` {id,slug,name,iso_code,agency_ids[],mission_ids[],note?},
`relatedMissions.json` keyed by id → [{id,type}], `stories.json` keyed by id →
{why,story,results}, `launch-dates.json` flat id→ISO date (60 curated
landmark dates; drives the homepage history section — exact-date matches
show "On this day", otherwise the 4 closest anniversaries show under
"Around this date"). Note: some launch dates also come via
spec-overrides.json (e.g. isee-3-1978).

## 9. Client scripts (`src/scripts/`)

- `main.js` (all pages, defer): IntersectionObserver scroll-reveals
  (`.reveal` → `.visible`; reduced-motion aware). The theme toggle was
  removed with the light theme (2026-08-24).
- `vision.js` (vision page module): canvas starfield (twinkle + slow drift,
  paused off-screen via IO, reduced-motion → static frame) + count-up
  animation for `.stat-num[data-count]` (ease-out, reduced-motion → instant).
- `home.js` (homepage module): clicking `#otd-link` adds `.visible` to
  `#on-this-day`; scroll-driven growth for the evolution timeline
  (`#evolution` → sets `--growth` 0→1 from viewport position,
  rAF-throttled, passive listeners; reduced-motion → spine always full).
- `search.js`: exports `createSearchIndex(missions)` (Fuse weights name:3,
  lead_partner:1, target:1, category:.5, outcome:.5; threshold .34,
  ignoreLocation) + `fuzzySearch(index,q,limit=8)`.
- `global-search.js` (all pages, module): wires header search to `#all-missions`
  JSON; up to 7 results, ↓/↑ keyboard nav, Enter opens `/missions/{id}/`.
- `vendor/fuse.mjs`: vendored Fuse.js 7.5.0 ESM.
- `src/admin/admin.js` (admin page): localStorage CRUD overlay key
  `'ap-staged-changes'` shape `{creates:[],updates:{},deletes:[]}`;
  import/export/discard; export downloads review JSON. Future plan: swap for Supabase.

## 10. Styling system (`src/styles/`)

- **tokens.css = master.** DARK-ONLY (light theme removed 2026-08-24 —
  no `[data-theme="light"]` block, no toggle UI, no `ap-theme` storage).
  `:root`: bg `#08090c`, surface `#15171e`, text `#f2f2f0`, muted `#9ba1ab`,
  single amber accent `#e8a33d` (+ oklch variant, glow, soft), status
  palette, six era accents `--era-1..6`, type scale
  (`--text-hero: clamp(2.6rem,7vw,5rem)`), font stacks, spacing scale,
  radii/pill, `--max-width:1160px`, `--header-h:64px`, motion tokens,
  z-layers. Convention: **no raw hex/px in component CSS for anything
  tunable — use tokens.**
- `base.css`: reset, smooth scroll, display-font headings, accent links,
  `.skip-link`, `.container` (max-width var), `.reveal` primitive,
  reduced-motion overrides. (The faint grid background `body::before` was
  removed in Execution #6 — user wants no grid texture.)
- `components.css` (~880 lines): header/nav/search dropdown, buttons
  (`.btn/.btn-solid/.btn-ghost`), `.status-badge.status-{success,partial-success,failure,in-transit,operational}`,
  `.chip`, `.hero` family (mission pages; ken-burns `hero-drift`), `.facts-strip`,
  `.mission-card` family, `.card-grid` (auto-fill minmax 280px), `.rail`,
  `.rel-graph`, admin table styles, flags/marks, `.roster-timeline`, footer.
  **Also hosts the shared page-layout primitives** (moved here in
  Execution #4 so EVERY page gets them): `.page-head`, `.section-title`,
  `.mp-section` (full container span — the user wants body text as wide as
  the facts table, NOT a narrow reading column; Execution #7),
  `.context-note`, `.facts-wrap` (full container span, Execution #7),
  `.era-block` (catalog era sections with `--era-accent` left border on
  h2), `.mission-body` (mission reading column), `.sources`/`.source-list`
  (credits block).
  `.facts-strip` keeps its box (border-block + 1px divider grid — restored
  in #10 after #9 over-removed it) with transparent cells (gray shade
  removed, #6); status inside the strip is plain status-colored text, no
  pill ellipse (`.facts-strip .status-badge`, Execution #10 — it also
  wraps to fit its cell; nowrap pills once painted over neighboring
  cells, #8);
  `.card-title-row` wraps so status badges never clip (#6);
  `.chip-link`/`.has-stretched-link .card-title-row a` sit at z-index 2
  above `.stretched-link` — any link inside a stretched-link card NEEDS
  one of these or the card link swallows the click (#6).
- `landing-journey.css`: homepage-only (via front-matter
  `extraStyles`). `.journey-hero` (78vh, Carina Nebula full-bleed
  background via `::before` + dark scrim `::after`, see §11), `.otd` +
  `.otd-note`, `.evo-strip`/`.evolution` timeline (dim track `::before`,
  era-gradient grown line `::after` scaled by `--growth`, `.evo-item`
  alternating sides with `.evo-node` dots + connectors, mobile ≤760px
  single column), `.center-cta`.
  (The generic bits that used to live here were moved to components.css;
  the dead vision-era `.chain/.principle-card/.standard` styles deleted.)
- `vision.css`: vision-page-only (via `extraStyles`). Hero starfield
  layout + nebula glows, gradient headline (`.vision-hero h1 em`),
  `.vision-stats` count-up strip, `.constellation` network (nodes with
  `--i` stagger, traveling `::after` pulse; vertical variant ≤760px),
  `.phase-card` grid (ghost `.phase-num`, pulsing `.live-dot`),
  `.manifesto` quote, `.standard-card`. All animations have
  `prefers-reduced-motion` fallbacks.

**How extraStyles works:** front-matter array looped in base.njk head.

## 11. Assets (`src/assets/` — passthrough-copied)

- `images/missions/<mission-id>/photo.jpg` — **202 of 209** missions have
  photos (Execution #12 pass), referenced by `media.thumb` as
  `/{{ m.media.thumb }}`. Thumbnail crops bias toward the photo top
  (`object-position: 50% 18%` on `.card-media img`/`.evo-media img`,
  25% on `.hero-media img`) so helmets/upper structure survive the
  cover crop.
- `images/flags/<iso>.png` — ae ca cn de eu fr gb in it jp nl ru su us.
- `images/milestones/` — homepage journey images (apollo11, gagarin, iss, laika, sputnik).
- `timeline/<mission-id>.jpg` — 33 legacy/alternate timeline images.
- `hero-deep-field.jpg` — mission-page hero fallback.
- Duplicates exist (cleanup candidates): `assets/milestones/*` vs
  `assets/images/milestones/*`; `cosmic-cliffs.jpg`/`pillars.jpg` at two levels.
- `images/source/` — original source scans kept for provenance
  (`Carina Nebula.jpg`, `Laika_dog.webp`, moved from repo root in
  Execution #6 per Law 6). Derivatives used by the site:
  `images/carina-nebula.jpg` (hero) and
  `images/missions/sputnik-2-1957/photo.jpg` (Laika, 1200px JPEG).
- `carina-nebula.jpg` — landing-page hero background (copied from root
  `Carina Nebula.jpg`, 2026-08-24). Credit rendered as `.hero-credit` in
  the hero's bottom-right corner (moved off the footer in Execution #11);
  full provenance in docs/image-credits.md: NASA, ESA, CSA, STScI (JWST).

## 12. Content & docs conventions

- Stories: `content/missions/<id>.md` with optional `# Title` and any/all of
  `## Why it happened` / `## The mission` / `## Results`. Missions without a
  story render an honest "write-up pending" note (never fabricated copy).
- **Copy style (Execution #4):** all visitor-facing text was humanized per
  Wikipedia:Signs of AI writing (WP:AISIGNS). Rules for new copy: no
  puffery/legacy emphasis ("testament", "pivotal", "stands as"), no
  "not just X but Y" parallelisms, no rhetorical rule-of-three (factual
  enumerations are fine), no "-ing" trailing analysis phrases, no vague
  attributions, minimal em dashes (factual appositives/attribution lines
  OK), plain factual sentences preferred. Keep this voice when writing new
  UI copy or stories.
- Media licensing (per `copyright_guidelines.md` + `docs/image-credits.md`):
  every image carries a five-field record rendered onto pages; prefer
  NASA/ISRO/Commons-PD; avoid CNSA/JAXA/Roscosmos imagery; NEVER use agency
  logos/insignia in UI (text initials marks instead).
- `docs/data-model-notes.md`: v1 field tables, editorial semantics (Success
  labeling, planned missions deliberately excluded).

## 13. Gotchas & rules

1. Never hand-edit anything in `src/_data/` — regenerated on every
   `npm run dev/build` (NOT on `build:fast`).
2. Canonical edits go in `data-sources/missions_timeline.md`, then `npm run data`.
3. Validation fails the build loudly (non-zero exit) on bad data.
4. `onThisDay` is computed at BUILD TIME — exact-date matches show "On this
   day"; otherwise the 4 nearest launch anniversaries render under "Around
   this date in space history" (filter `nearestAnniversaries`).
5. Era strings are prefixed keys used by `eraAccent`/`eraIndex` — keep the
   exact prefixes when adding eras.
6. Agency logos never appear in UI; use `marks.njk` initials macro.
7. Fuse.js is vendored — don't add it to package imports; import from
   `./search.js` which wraps vendor/fuse.mjs.
8. Theme: **dark-only** — never reintroduce `[data-theme]`, theme toggles,
   or `localStorage['ap-theme']`; new components just use the dark tokens.
9. The flip-book/timeline experiment was fully removed (2026-08-24):
   `future/` folder and `docs/future-plan.md` deleted; README/index/global-search/
   tokens cleaned. A stale `dist/timeline/` artifact was also deleted. Do not
   reintroduce references to it.
10. `Bugs/`, `PLAN.docx`, `copyright_guidelines.md` are gitignored working files.
11. Page-specific CSS must be wired via `extraStyles` front-matter — a
    template using classes from a non-default stylesheet without it renders
    unstyled (this is what broke the vision page before Execution #2).
12. `dist/` can hold stale artifacts after deletions; check for leftovers
    when something is removed from `src/`.
13. **No em dashes in visitor-facing prose or labels** (Execution #6).
    Use commas, periods, colons, or `·`. Exception: official credit formats
    supplied by the owner (e.g. "Heritage Images—Hulton Archive/Getty
    Images") and en dashes in year ranges (1957–1969).
14. Agency/country chips that link out must carry `chip-link` (or sit in a
    `.has-stretched-link .card-title-row a`) or the card's stretched link
    swallows the click.
