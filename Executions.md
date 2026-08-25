# Executions Log

---

## Execution #1 — 2026-08-24 16:28 IST

### Requested Tasks
1. Go through the codebase.
2. Remove the future flip-book folder and future plans from the project.
3. Write everything about the codebase into `codebase_context.md` (context-restart reference doc).
4. Add the Carina Nebula image as the background of the landing page (home) hero; adjust text size and color for better look.
5. Stop and ask to continue for further plans.

### Execution Summary (plan)
1. **Executions.md** — this file, created first as required. Will be appended to after each task completes.
2. **Future flip-book removal** —
   - `future/` folder is already EMPTY on disk (flip-book code was previously moved out). It will be deleted outright.
   - `docs/future-plan.md` (the parked roadmap) will be deleted.
   - All references will be cleaned: README.md "Timeline flip-book (parked)" section, comment in `src/index.njk`, stale mention in `src/scripts/global-search.js`, flip tokens in `src/styles/tokens.css` (checked first for safe removal).
   - Expected output: no files or references to the flip-book / future plan remain anywhere in the project.
3. **Codebase exploration** — read all templates (`src/*.njk`), includes, styles, scripts, build pipeline (`scripts/build/`), data sources, content, config. Expected output: complete understanding of architecture, data flow, conventions.
4. **codebase_context.md** — comprehensive project context document written at repo root so a fresh model session can resume without re-reading the codebase. Expected output: single md file covering architecture, data pipeline, pages, styling system, scripts, conventions, commands, gotchas.
5. **Carina Nebula hero** — use existing `Carina Nebula.jpg` at repo root: copy into `src/assets/images/`, apply as fixed cover background on `.journey-hero` in `landing-journey.css`, add a dark gradient overlay for legibility, bump heading size and brighten text color.
   - Expected output: home page hero shows the Carina Nebula with readable white text.
6. **Verification** — run `npm run build:fast` (or `npm run validate`) to confirm nothing broke.

### Anti-loop rule
If any task gets stuck (repeated failures / no progress), it is terminated and either solved by an alternate method or skipped — any skip is noted below.

### Results

**Task 1 — Codebase exploration (16:29–16:34 IST): DONE.**
Full read of config, templates, includes, partials, scripts, styles, Python
pipeline, data formats, docs, assets. Findings distilled into
`codebase_context.md` (Task 3). No blockers.

**Task 2 — Future flip-book / future plans removal (16:28–16:31 IST): DONE.**
- `future/` folder was already empty on disk (code previously moved out) → deleted.
- `docs/future-plan.md` deleted.
- README.md: removed the "Timeline flip-book (parked)" section.
- `src/index.njk`: removed flip-book mention from header comment.
- `src/scripts/global-search.js`: removed stale flip-book comment line.
- `src/styles/tokens.css`: removed now-unused `--flip-duration-max` token.
- Verified: zero remaining references to flip-book / future-plan anywhere
  outside this log.

**Task 3 — codebase_context.md (16:35 IST): DONE.**
Written at repo root; covers architecture, Eleventy config + filters, every
page template, layout/partials, client scripts, styling/token system, the
Python data pipeline + override files, canonical dataset format, JSON shapes,
asset layout, content/licensing conventions, and 10 gotchas/rules for future sessions.

**Task 4 — Carina Nebula landing hero (16:36 IST): DONE.**
- Copied root `Carina Nebula.jpg` → `src/assets/images/carina-nebula.jpg`
  (passthrough-copied to dist by Eleventy).
- `src/styles/landing-journey.css`: `.journey-hero::before` renders the image
  full-bleed (`100vw`, cover) behind the hero, extending up under the
  translucent sticky header; `::after` adds a dark gradient scrim dissolving
  into the page background at the bottom edge for legibility.
- Text adjustments: h1 enlarged to `clamp(3rem, 8vw, 5.75rem)` in pure white
  with soft shadow; hook paragraph brightened from muted gray to near-white
  and sized up (`clamp(1.08rem, 2vw, 1.4rem)`); kicker set to amber accent;
  all with text-shadows over the nebula.
- Verified: `npm run validate` passes (209 missions OK); `npm run build:fast`
  succeeds (248 files); image present at `dist/assets/images/carina-nebula.jpg`.

**Anti-loop notes:** none — no task got stuck. (One trivial retry: first
`cp` ran before a directory listing confirmed it; re-ran successfully.)

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #2 — 2026-08-24 16:50 IST

### Laws acknowledged (from user)
1. Always follow the law.
2. Always ask before making any commits.
3. Update `codebase_context.md` after every task execution; keep these laws recorded in the context file.

### Requested Tasks
1. Fix the "Our Vision" page — it renders completely unstyled/messy (screenshot in `Bugs/`). Redesign it to convey the vision with rich visual effects and visionary text.
2. Remove the light theme from the website (dark-only).

### Execution Summary (plan)
1. **Vision page root cause** — `src/vision.njk` has no `extraStyles`, so
   `landing-journey.css` (which holds `.page-head/.chain/.principle-card/...`)
   never loads → raw HTML. Fix by full redesign with a dedicated stylesheet.
2. **Vision page redesign** —
   - New `src/styles/vision.css` + `src/scripts/vision.js`, loaded via
     `extraStyles` front-matter.
   - Effects planned: animated canvas starfield (twinkle + slow drift,
     reduced-motion aware), hero with staggered reveal + gradient-glow
     display type, knowledge chain rebuilt as an animated "constellation"
     (glowing nodes, pulse traveling along connectors, sequential
     scroll-triggered lighting), count-up stats strip, glassy phase cards
     with hover lift/glow and a pulsing "live" dot on Phase 1, a large
     visionary manifesto/quote section (real Tsiolkovsky quote, attributed),
     editorial-standard card, CTA.
   - Expected output: a cinematic, dark, on-brand vision page.
3. **Remove light theme** — delete `:root[data-theme="light"]` block from
   `tokens.css`; remove theme bootstrap script + `#theme-toggle` button from
   `base.njk`; remove toggle code from `main.js`; remove `.theme-toggle`
   styles from `components.css`. Expected output: site is dark-only, no
   theme toggle UI, no dead code.
4. **Verify** — `npm run build:fast` + grep for leftover theme refs.
5. **Update `codebase_context.md`** after each task (per Law 3) — add Laws
   section, vision-page notes, dark-only notes.

### Anti-loop rule
Any task that gets stuck is terminated and either solved another way or
skipped with a note here.

### Results

**Task 1 — Vision page redesign (16:50–17:02 IST): DONE.**
- Root cause found: `src/vision.njk` had no `extraStyles`, so the stylesheet
  holding `.page-head/.chain/.principle-card` (`landing-journey.css`) never
  loaded → raw unstyled HTML (matches the Bugs/ screenshot).
- Instead of patching, fully redesigned per user intent ("visual effects +
  text of a visionary"):
  - New `src/styles/vision.css` (loaded via `extraStyles`) and
    `src/scripts/vision.js` (module).
  - Hero: full-viewport canvas **starfield** (twinkling + slow drift,
    paused off-screen, reduced-motion → static), CSS nebula glows, staggered
    rise-in, gradient-glow headline "Not a catalog. A connected story.",
    rewritten visionary hook paragraph.
  - **Count-up stats strip**: 209 missions / 18 agencies / 15 countries /
    70 years, animating on scroll (reduced-motion → instant).
  - Knowledge chain rebuilt as an animated **constellation**: 8 glowing
    nodes on an amber line with a traveling signal pulse; staggered
    scroll-triggered lighting; collapses to a vertical timeline ≤760px.
  - Phase cards: glassy gradient surfaces, hover lift + amber glow, ghost
    phase numbers, pulsing "live" dot on Phase 1 — now.
  - **Manifesto section**: real attributed quote — "Earth is the cradle of
    humanity, but one cannot live in a cradle forever." — Konstantin
    Tsiolkovsky, 1911 (verified historical quote, no fabricated attribution).
  - Editorial-standard card + CTA retained, restyled.
  - All effects have `prefers-reduced-motion` fallbacks.
- Two self-review fixes before build: pulse animation made
  container-relative (was viewport-based, would overshoot), and `dt` placed
  before `dd` in the stats `<dl>` (valid HTML) with `column-reverse` for
  the number-on-top visual.

**Task 2 — Light theme removal (16:55–17:04 IST): DONE.**
- `tokens.css`: deleted entire `:root[data-theme="light"]` block + comment.
- `base.njk`: removed theme bootstrap script and the `#theme-toggle` header button.
- `main.js`: removed all toggle code (file now does reveals only; noted dark-only).
- `components.css`: removed `.theme-toggle` styles.
- README.md: updated architecture note to "dark-only theme".
- Stale artifact `dist/timeline/` (old flip-book page with theme-toggle)
  found during verification and deleted.
- Verified: zero `data-theme|ap-theme|theme-toggle` refs in `src/` and dist
  pages; `npm run build:fast` passes (248 files); vision.css + vision.js
  present in dist.

**codebase_context.md updated per Law 3**: Laws section added (§0), vision
page + vision.js/vision.css documented, dark-only theme noted, two new
gotchas (extraStyles wiring, stale dist artifacts).

**Anti-loop notes:** none — no task got stuck.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #3 — 2026-08-24 17:22 IST

### Requested Task
Implement the site logo from `Logos/` (`Title Logo.png` = Earth + JWST
artwork; `logo.jpeg` = full lockup with "AntarikshPedia — A connected space
encyclopedia" wordmark).

### Execution Summary (plan)
1. Derive optimized brand assets into `src/assets/brand/` (using `sips`):
   - `logo-mark.png` (~256px, center-cropped to the Earth) — header brand.
   - `favicon.png` (64px) + `apple-touch-icon.png` (180px).
   - `og-image.jpg` (full `logo.jpeg` lockup) for social sharing.
2. `base.njk`: favicon + apple-touch-icon + og:image links; logo mark image
   in the header brand next to the wordmark.
3. `components.css`: `.brand` flex layout + `.brand-mark` circular style
   with subtle amber glow.
4. Verify build; update `codebase_context.md` (Law 3).

### Anti-loop rule
Stuck tasks are terminated and solved another way or skipped with a note.

### Results

**Logo implementation (17:22–17:36 IST): DONE.**
- Derived optimized assets into `src/assets/brand/` with `sips` (center-crop
  560² around the Earth — also removes the sparkle watermark in the corner):
  `logo-mark.png` 256² (header), `favicon.png` 64², `apple-touch-icon.png`
  180², `og-image.jpg` (full `logo.jpeg` lockup for social sharing).
- `base.njk`: favicon + apple-touch-icon + `og:image` links added; header
  brand now shows the circular Earth mark beside the "Antariksh**Pedia**"
  wordmark.
- `components.css`: `.brand` converted to flex with gap; new `.brand-mark`
  circular style with subtle amber glow + hover scale.
- Verified: `npm run build:fast` passes (248 files, 205 copied); brand files
  present in `dist/assets/brand/`; `brand-mark`/favicon present in output HTML.
- One trivial retry: a flawed `cp ||` chain produced sips warnings; re-ran
  with clean commands. No task stuck.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #4 — 2026-08-24 17:45 IST

### Requested Tasks
1. Apply the vision-page fix (missing stylesheet wiring) across every page.
2. Humanize all text content per Wikipedia:Signs of AI writing
   (remove puffery, "not just X but Y", rule-of-three, em-dash overuse,
   "-ing" trailing analysis, AI vocabulary).

### Execution Summary (plan)
1. **Style audit** — only index/vision/admin set `extraStyles`; catalog,
   missions, agencies, agency-pages, countries, country-pages rely on
   shared classes (.page-head, .mp-section, .context-note) that live in
   landing-journey.css, which they never load. Fix: move shared layout
   classes into components.css (loaded everywhere); delete dead vision-era
   styles from landing-journey.css; add page-specific extraStyles only
   where genuinely needed.
2. **Humanize copy** — rewrite visitor-facing text in all templates
   (hero hooks, section intros, empty-state notes, meta descriptions,
   footer) and the 7 long-form stories in content/missions/ to remove
   AI tells. Keep factual dataset lines (209 outcome strings) intact
   except obvious tells; note any mass-data edits.
3. Verify with build; update codebase_context.md (Law 3).

### Anti-loop rule
Stuck tasks are terminated and solved another way or skipped with a note.

### Results
_(appended as work completes)_

---

### Results (Execution #4)

**Task 1 — Style wiring fixed on every page (17:45–17:55 IST): DONE.**
Audit found the vision-page bug replicated site-wide:
- Classes used but defined NOWHERE: `.era-block` (catalog), `.mission-body`
  and `.sources` (mission pages).
- Classes defined only in landing-journey.css (loaded by homepage only) but
  used by catalog, missions, agencies, agency-pages, countries,
  country-pages, admin: `.page-head`, `.mp-section`, `.context-note`,
  `.facts-wrap`.
Fix (the vision-page method — ensure every page loads the styles its
classes depend on):
- Moved shared layout primitives into components.css (loaded by every page
  via base.njk): `.page-head`, `.mp-section`(+h2), `.context-note`,
  `.facts-wrap`.
- Added the three never-defined classes to components.css: `.era-block`
  (era section spacing + era-accent border on h2 + scroll-margin),
  `.mission-body` (reading column), `.sources`/`.source-list` (credits).
- Deleted dead vision-era styles from landing-journey.css
  (`.chain*`, `.principle-card*`, `.phase-tag`, `.standard*`).
- No extraStyles changes needed elsewhere; homepage keeps
  landing-journey.css, vision keeps vision.css.
Verified: build passes (248 files); all classes now resolve in components.css.

**Task 2 — Copy humanized per WP:AISIGNS (17:55–18:10 IST): DONE.**
- index.njk: hero hook rewritten (removed "first light of the universe"
  flourish and "every launch is a doorway" metaphor); "Sixty-eight years.
  One long journey." → dynamic "{{ span }} years. One journey." (also fixes
  stale count — dataset now spans 70 years); CTA "Begin the journey — 1957"
  → "Begin in 1957"; on-this-day empty note simplified.
- vision.njk: hero hook rewritten (removed rule-of-three "of agencies and
  machines, of rivalries and handshakes, of ideas igniting ideas" and
  em-dash chain); constellation caption de-anaphorized; Phase-1 card em dash
  removed; meta description em dash removed. Kept "Not a catalog. A
  connected story." tagline (brand voice, predates this pass) and the real
  attributed Tsiolkovsky quote.
- missions.njk: misleading "Mission #209 tracked" hero tag → "Era X of 6 ·
  full record in the catalog"; pending-writeup note rewritten without em
  dash / editorializing.
- base.njk: meta description + og:description fallbacks made dynamic and
  de-dashed (Nunjucks `~` concatenation via `{% set %}`); footer-note
  rewritten as plain factual sentence (was a 7-item list + em dash).
- catalog.njk / agencies.njk: hooks simplified (em-dash elaborations
  removed).
- Stories: vostok-1 title fixed from slug `# vostok-1-1961` to `# Vostok 1`;
  luna-3 "for the first time in human history" → "for the first time".
  Other stories audited — already factual, specific, and clean (kept).
- Swept all src/content for AI vocabulary (testament/pivotal/crucial/
  vibrant/showcase/underscore/not just/stands as/...): zero hits. Remaining
  em dashes are legitimate (attribution lines, title separators, factual
  appositives).
- Scope note: 209 canonical dataset outcome lines and README/docs left
  as-is — dataset lines are short factual records guarded by the validator;
  README/docs are developer-facing, not site copy. Noted here per anti-loop
  rule rather than mass-rewriting data.

**Verified:** `npm run validate` passes (209 missions); `npm run build:fast`
passes (248 files); dist sweep confirms removed phrases are gone.

**codebase_context.md updated per Law 3** (shared-layout note, copy-style
rules for future sessions, timestamp).

**Anti-loop notes:** none — no task got stuck. One self-caught fix: replaced
`+` string concatenation with Nunjucks `~` in base.njk meta description to
avoid filter-precedence bugs.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #5 — 2026-08-24 18:40 IST

### Requested Tasks
1. Remove the Contributions page (/admin) for now.
2. Home upper half: fix the too-small gap between the hero CTAs and the
   facts strip (Bugs/Upper Half.jpg).
3. Home lower half: verify "On this day" works (needs launch dates); fix
   anything faulty (Bugs/Lower half.jpg).
4. Redesign the milestones under "70 years. One journey." as a visually
   astonishing connected story (evolution-of-life metaphor), adding more
   landmark missions incl. Voyager 1 & 2.
5. Replace the bad Sputnik 2 image with the provided `Laika_dog.webp`
   (credit: Heritage Images—Hulton Archive/Getty Images).

### Execution Summary (plan)
1. **/admin removal** — delete `src/admin.njk` + `src/admin/` (git history
   preserves them), remove footer "Contributions" link in base.njk, remove
   the "Propose this write-up" chip in missions.njk, drop the
   `src/admin → admin` passthrough in eleventy.config.js, update README.
2. **Hero gap** — add top margin between `.hero-actions` and the
   `.facts-strip` inside `.journey-hero` (landing-journey.css).
3. **On this day** — filter logic verified correct; today (24 Aug) has no
   exact match among the 60 curated dates. Fix: add `onThisWeek` filter
   (±3 days, any year) as a fallback with its own heading ("This week in
   space history"), so the section always shows something relevant (today:
   Voyager 1–2, Viking 1, Mariner 2).
4. **Milestones → evolution timeline** — vertical "lineage" spine that
   grows as you scroll (JS progress var, reduced-motion → static), era-
   colored nodes branching alternately left/right, 9 milestones:
   Sputnik 1 → Sputnik 2 (Laika) → Vostok 1 → Apollo 11 → Pioneer 10 →
   Voyager 1–2 → Hubble → Zarya/ISS → JWST. Deep-space gradient backdrop,
   glow dots, connector lines. Mobile: single column.
5. **Sputnik 2 image** — convert `Laika_dog.webp` →
   `src/assets/images/missions/sputnik-2-1957/photo.jpg`; update
   media-overrides.json record (credit: Heritage Images—Hulton Archive/
   Getty Images; license: rights-managed; source: gettyimages.com root
   until a direct item URL is provided; checked: today).
6. Build + verify + update codebase_context.md (Law 3).

### Anti-loop rule
Stuck tasks are terminated and solved another way or skipped with a note.

### Results
_(appended as work completes)_

---

### Results (Execution #5)

**1. Contributions page removed (18:40–18:47 IST): DONE.**
Deleted `src/admin.njk` + `src/admin/` (recoverable from git history),
removed the footer "Contributions" link, the "Propose this write-up" chip
on mission pages, and the `src/admin → admin` passthrough. README updated.
`dist/admin` cleaned; build confirms no admin refs remain.

**2. Hero gap fixed (18:48 IST): DONE.**
`.journey-hero .facts-strip { margin-top: var(--space-8) }` — clear
breathing room between the CTAs and the telemetry strip (Bugs/Upper Half.jpg).

**3. On this day verified + fixed (18:48–19:05 IST): DONE.**
- Diagnosis: the `onThisDay` filter logic was correct; today (24 Aug)
  genuinely has no exact-date launch among the 60 curated dates, so the
  section always showed the empty state for most dates. Root limitation:
  only ~60/209 missions have known launch dates (by design — no guessed
  dates).
- Fix: new `nearestAnniversaries` filter (day-of-year distance via
  Date.UTC, sorted, top 4). When no exact match exists, the section now
  renders "Around this date in space history" with the 4 closest launch
  anniversaries and an honest note. Today it shows Mariner 2 (Δ3d),
  Viking 1 (Δ4d), Voyager 1–2 (Δ4d), ISEE-3 (Δ12d).
- Self-caught fixes during implementation: Nunjucks `set` rejects ternaries
  (restructured with if/elif); first ±3-day window missed Voyager's Aug 20
  anniversary from Aug 24 (Δ4) — replaced with the closest-N approach.
- Exact-date matches still render "On this day" as before (e.g. Oct 4 →
  Sputnik 1).

**4. Milestones → evolution timeline (18:50–19:00 IST): DONE.**
Replaced the flat 6-card grid with a connected "lineage" timeline
(`.evo-strip`/`.evolution` in landing-journey.css + `home.js`):
- Central spine: dim track with a bright era-gradient line that GROWS down
  the section as you scroll (rAF-throttled scroll handler sets `--growth`
  0→1; `prefers-reduced-motion` → always full).
- 9 milestones (added Pioneer 10, Voyager 1–2, Hubble): Sputnik 1 →
  Sputnik 2 (Laika) → Vostok 1 → Apollo 11 → Pioneer 10 → Voyager 1–2 →
  Hubble → Zarya/ISS → JWST. Dataset has a combined `voyager-1-2-1977`
  record, used as-is.
- Each milestone branches off the spine with an era-colored node dot +
  connector, alternating left/right (single column ≤760px), image cards
  with hover zoom, new lede paragraph telling the evolution story
  (humanized copy per Execution #4 rules).

**5. Sputnik 2 / Laika image replaced (18:52 IST): DONE.**
Converted root `Laika_dog.webp` → `src/assets/images/missions/sputnik-2-1957/photo.jpg`
(1200px JPEG via sips; historic Hulton Archive photo of Laika in her
capsule — far better than the old suit image). media-overrides.json updated:
credit "Heritage Images—Hulton Archive/Getty Images", license
"rights-managed", source gettyimages.com root (replace with the direct
item URL when available), checked 2026-08-24. Validator passes with the
rights-managed license value. Note: this intentionally overrides the
project's usual PD-preference rule at the user's explicit direction.

**Verified:** `npm run data` + `npm run validate` (209 missions OK) +
`npm run build:fast` (247 files, one fewer with /admin gone); dist checks
confirm the fallback section, new milestones, and no admin remnants.

**codebase_context.md updated per Law 3** (homepage entry, home.js,
landing-journey.css, admin removal, launch-dates behavior).

**Anti-loop notes:** none stuck; two self-caught issues fixed above.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #6 — 2026-08-24 20:05 IST

### New Laws from user (recorded in codebase_context.md §0)
4. All generated visitor-facing text must be humanized (WP:AISIGNS) before
   a task is done — no AI tells, no em dashes in prose.
5. AI builds this project, but the result must never feel AI-made.
6. All images belong under src/assets/ (never loose in repo root); moves
   must never break site integration.

### Requested Tasks
1. Add the laws above to the context.
2. Capitalize stray lowercase labels ("editorial standard" etc.); fix
   agency names on Countries pages showing lowercase slugs.
3. Remove em dashes from all visitor-facing pages (clear AI tell).
4. Bugs/On this day.jpg: heading/note text overlapping — fix.
5. Content span must line up with the facts table; remove the grid
   pattern from all pages; remove the gray shade from the table.
6. Bugs/Info2.jpg: status badge clipped by card edge — fix.
7. Agencies/Countries catalog: clicking an agency chip must open that
   agency's mission page (currently the stretched link swallows clicks).
8. Credit NASA/ESA/CSA/STScI (JWST) for the Carina Nebula background.
9. Move root-level images (Carina Nebula.jpg, Laika_dog.webp) into
   src/assets/ without breaking the site.

### Anti-loop rule
Stuck tasks are terminated and solved another way or skipped with a note.

### Results
_(appended as work completes)_

---

### Results (Execution #6)

**1. Laws recorded (Law 3): DONE.** Three new laws (humanize-always,
never-feel-AI-made, images-belong-in-assets) added to codebase_context.md §0.

**2. Labels + agency names: DONE.**
- Vision mono-tags capitalized: "The model", "Roadmap", "Editorial
  standard"; phase tags now "Phase 1 · Now" etc.
- New `agencyBySlug` filter; agency chips on countries.njk,
  country-pages.njk, agency-pages.njk now render proper registered names
  ("Firefly Aerospace", "ISRO"...) instead of raw slugs.

**3. Em-dash purge: DONE.** Removed every visitor-facing em dash:
- base.njk titles now use "·"; footer/mission descriptions, "year known
  only:", sources credit separator all converted.
- vision.njk: phase tags + Tsiolkovsky cite.
- index.njk: evolution lede rewritten (also humanized — Law 4/5).
- Stories: sputnik-1 (2), explorer-1 (sentence split), luna-3, jwst,
  apollo-11 (2) — all rewritten with commas/periods.
- media-overrides.json: 42 credit strings " — " → " · ".
- Verified in dist: zero em dashes except the owner-supplied official
  Getty credit format ("Heritage Images—Hulton Archive/Getty Images") and
  en dashes in year ranges — both intentional.

**4. On-this-day overlap: DONE.** Root cause: `.section-title` was another
never-defined class (h2 default margins collapsed with the note's negative
margin). Defined `.section-title` in components.css and gave `.otd-note` a
positive top margin.

**5. Span alignment + grid + gray shade: DONE.**
- `.facts-wrap` is now a centered 860px column (matches `.mp-section`);
  `container` class removed from the three facts-wrap sections so the
  table lines up with the article text.
- Grid pattern: `body::before` deleted from base.css; unused `--grid-line`
  token removed from tokens.css.
- Gray shade: `.facts-strip div` background removed (transparent cells,
  hairline dividers remain).

**6. Status badge clipping: DONE.** `.card-title-row` now wraps
(`flex-wrap: wrap`) and badges are `flex-shrink: 0` — long badges like
"PARTIAL SUCCESS" drop to their own line instead of overflowing the card
(Bugs/Info2.jpg).

**7. Agency chip click-through: DONE.** Root cause: `.stretched-link`
(z-index 1) covered the plain chips in country cards, so clicks opened the
country page instead of the agency page. Agency chips now carry
`chip-link` (z-index 2) and open the agency's mission timeline.

**8. Carina Nebula credit: DONE.** Footer now reads "...Carina Nebula hero:
NASA, ESA, CSA, STScI (James Webb Space Telescope)"; full entries added to
docs/image-credits.md (hero background + Laika rights-managed exception).

**9. Images moved into assets (Law 6): DONE.** `Carina Nebula.jpg` and
`Laika_dog.webp` moved from repo root to `src/assets/images/source/` via
git mv (provenance originals). Site references use the derived copies
(`assets/images/carina-nebula.jpg`, `assets/images/missions/sputnik-2-1957/photo.jpg`)
— unchanged and verified in dist. Repo root now has no loose images.

**Verified:** `npm run data` + `npm run validate` (209 OK) +
`npm run build:fast` (247 files); dist checks for chips, credit line,
badge wrap, and em-dash sweep all pass.

**Anti-loop notes:** none stuck. One self-caught issue: first ±3-day
anniversary window would have missed Voyager (Δ4d) — replaced with
closest-4 approach (noted in #5 results).

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #7 — 2026-08-24 20:35 IST

### Requested Tasks
1. The table dimension change was not wanted: revert the facts table to its
   full span and instead WIDEN the body text to run parallel with the
   table (Bugs/info.jpg).
2. Hyperlink every mission on the agency and country individual pages to
   its mission page.

### Results

**1. Span fix: DONE.**
- Reverted `.facts-wrap` to full container width (the `container` class is
  back on the facts sections in missions/agency-pages/country-pages).
- `.mp-section` no longer caps at 860px: body text now spans the same
  width as the facts table, exactly parallel, as requested.
- Note recorded in codebase_context.md so future sessions do not
  re-narrow the column.

**2. Roster hyperlinks: DONE.**
Mission names in the roster were already links, but only the name. Each
`.rt-card` on agency/country pages is now fully clickable
(`has-stretched-link` + stretched link to `/missions/{id}/`,
`.rt-card` made position:relative). Verified in dist: NASA page 117
clickable cards, India page 11, all pointing at their mission pages.

**Verified:** `npm run build:fast` passes (247 files). codebase_context.md
updated per Law 3.

**Anti-loop notes:** none.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #8 — 2026-08-24 20:50 IST

### Requested Task
Fix the "PARTIAL SUCCESS" status badge overlapping the VEHICLE column in
the mission-page facts table (user screenshot, Pioneer 1 page).

### Result: DONE (20:52 IST)
Root cause: `.status-badge` is `white-space: nowrap`; inside the facts
strip's ~150px grid cells a 15-character pill cannot fit and paints over
the neighboring cell.
Fix: scoped override `.facts-strip .status-badge { white-space: normal;
line-height: 1.5; max-width: 100%; }` — the pill now wraps to two tidy
lines inside its own cell. Card badges (title rows) are unaffected; they
already wrap via `.card-title-row`.
Verified: `npm run build:fast` passes.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #9 — 2026-08-24 20:58 IST

### Requested Task
Remove the box (border frame / divider lines) from the facts table.

### Result: DONE (20:59 IST)
`.facts-strip` no longer draws `border-block` or the 1px divider grid
(gap + background trick removed); cells are plain text columns with a row
gap for wrapped rows. Verified: `npm run build:fast` passes.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #10 — 2026-08-24 21:05 IST

### Requested Task
Restore the facts-table boundaries (previous task over-removed) and instead
remove the ellipse (pill outline) that highlights the mission status.

### Result: DONE (21:06 IST)
- `.facts-strip` box restored: border-block + 1px divider grid back exactly
  as before Execution #9.
- `.facts-strip .status-badge` is now plain status-colored text: pill
  border, padding, and border-radius removed (still wraps to fit its cell).
  Badges on cards elsewhere keep their pill look.
Verified: `npm run build:fast` passes.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #11 — 2026-08-24 21:12 IST

### Requested Task
Move the Carina Nebula credit off the site footer and onto the hero image
itself, in a corner.

### Result: DONE (21:13 IST)
- Footer copy restored to its original form (no Carina credit).
- New `.hero-credit` line "Carina Nebula · NASA, ESA, CSA, STScI" sits in
  the hero's bottom-right corner (small mono text, 55% white, subtle
  shadow, brightens on hover).
- docs/image-credits.md ledger unchanged (still records full provenance).
Verified: `npm run build:fast` passes; credit renders in dist/index.html.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #12 — 2026-08-24 21:20 IST

### Requested Tasks
1. Research + collect images for ALL missions still missing thumbnails
   (84 of 209), starting from Artemis II (2026) back through the 2000s,
   then the rest.
2. Better Voyager image; replace Ariel 1, IM-1 Odysseus, Vostok 1 images.
3. Prioritize real satellite/spacecraft imagery; avoid human faces.
4. Fix thumbnail cropping that cuts identifying parts (e.g. Apollo 11
   astronaut's helmet) in catalog cards.

### Plan
1. Patch enrich-missions.py: newest-first ordering flag, credit separator
   "·" (no em dashes per Execution #6), checked date updated.
2. Clear the 4 named missions' media entries so the pipeline re-sources
   them; hand-verify each result and replace with hand-picked NASA/Commons
   images if the auto-pick is poor.
3. Run the pipeline newest-first (resumable, saves every 10).
4. CSS: bias thumbnail crop toward the top of photos (object-position) so
   faces/helmets/upper structure survive the cover crop.
5. npm run data + validate + build; review a sample of new images; update
   codebase_context.md (Law 3).

### Anti-loop rule
Network research can fail per-mission; failures are logged and skipped
(the script is resumable). No retry loops.

### Results
_(appended as work completes)_

---

### Results (Execution #12)

**Image research pass: DONE (21:20–22:05 IST). 202/209 missions now have
thumbnails (was 145; +57 this pass).**

- Pipeline: ran `enrich-missions.py` newest-first (new `newest` ordering
  flag added; credits now " · ", checked date 2026-08-24) in resumable
  chunks, then a targeted pass with 37 curated per-mission queries, then
  direct Commons file fetches for hand-picked images.
- Priority order honored: Artemis II (2026) backward through the 2000s
  first, then older eras.
- Named replacements verified visually:
  - **Artemis II**: crew portrait (human faces — rejected per rule) →
    NASA SLS/Orion rollout photo (real hardware).
  - **Voyager 1–2**: now the classic JPL Voyager spacecraft image.
  - **Vostok 1**: Gagarin portrait → Vostok cockpit instrument panel
    (Globus navigation globe), no faces.
  - **Ariel 1**: real flight-model satellite photo.
  - **IM-1 Odysseus**: real lunar-surface mission imagery.
- Spot-checked new picks (Chandrayaan-3 lander on the Moon, Lunokhod-1
  LRO site image, Helios, SMART-1, IKAROS, Planck, Gaia, BepiColombo,
  LIGO Hanford aerial...): all real imagery, no faces found.
- License discipline kept: NASA PD + Commons PD/CC only, plus GODL-India
  accepted deliberately for two ISRO missions (astrosat, xposat) — ISRO
  imagery is preferred by the project guidelines and GODL-India is ISRO's
  standard free license. Logged here as the licensing decision.
- **7 missions remain without images** (luna-19-1971, bhaskara-1-1979,
  tenma-1983, sakigake-1985, suisei-1985, ginga-1987, sross-c2-1993):
  only sub-500px GIFs or wrong-subject hits exist on NASA/Commons. They
  render letter placeholders; skipped honestly per the anti-loop rule.

**Thumbnail crop fix: DONE.** `object-position: 50% 18%` on catalog card
and evolution-timeline thumbnails (25% on mission-page heroes) — the crop
now keeps the top of portrait photos, so identifying parts (Apollo 11
astronaut's helmet, rocket upper stages, spacecraft tops) are no longer
cut by the cover crop.

**Verified:** `npm run data` + `npm run validate` pass (209 missions, all
media licenses OK); `npm run build:fast` passes (283 files copied, 247
written); zero em-dash credits.

**codebase_context.md updated per Law 3** (coverage numbers, script
flags, GODL decision, crop bias).

**Anti-loop notes:** none stuck; automated gates' rejections were handled
by curated queries and hand-picked files instead of retry loops.

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---

## Execution #13 — 2026-08-25 10:25 IST

### Requested Task
Thumbnails not visible in the related-missions rail on mission pages
(user screenshot: Zarya page shows letter placeholders for TRACE,
Chandra, FUSE, Terra).

### Result: DONE (10:26 IST)
Root cause: `missions.njk` builds the related-missions rail from trimmed
records that omitted the `media` (and `era`) fields, so `mission-card.njk`
always fell back to letter placeholders there — even for missions with
photos. The pushed records now include `media` and `era`.
Verified in dist: the Zarya page's four related cards all reference real
`/assets/images/missions/<id>/photo.jpg` thumbnails. Build passes.
(Note: a running `npm run dev` server picks this up on rebuild.)

---
## NEXT: awaiting user approval for further plans (stopped as requested).

---
