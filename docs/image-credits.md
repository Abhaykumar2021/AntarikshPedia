# Image & video credits

All media used on AntarikshPedia pages, with sources and license terms.
Per-image records live in the data sidecars (`scripts/build/media-overrides.json`,
merged into each mission's `media` field: `thumb`, `credit`, `license`,
`source`, `checked`). See `copyright_guidelines.md` for the agency-by-agency
policy reference.

## Automated sourcing pipeline (August 2026)

`scripts/build/enrich-missions.py` sources photos for missions lacking one:

- NASA Image Library first (public domain), with a relevance gate — the
  hit's title must match the mission's name tokens, or its asset ID must
  carry a year within ±1 of the launch year.
- Wikimedia Commons otherwise, gated twice: the license tag must be
  PD / CC0 / CC BY / CC BY-SA **and** the file page must carry space-related
  categories.
- Every automated pick was then title-reviewed by hand; ~30 false positives
  were removed (wrong spacecraft, people, landscapes, stamps). Remaining
  gaps render honest placeholder tiles rather than wrong images.

Coverage after the pass: **145 of 209** missions carry photos, each stored
in its per-mission folder `src/assets/images/missions/<id>/photo.jpg`.
The remaining 64 are queued for manual curation; nothing is guessed.

The same pass parsed Wikipedia spaceflight infoboxes for specification
fields (`launch_vehicle`, `mass_kg`, `orbit_type`, `duration`) — recorded
only when cleanly extracted, in `scripts/build/spec-overrides.json`
(88 missions covered as of this pass).

## Landing page — journey milestones (`assets/images/milestones/`)

| File | Subject | Source | Terms |
|------|---------|--------|-------|
| `sputnik.jpg` | Sputnik 1 with whip antennas | Wikimedia Commons, `File:Sputnik asm.jpg` (NSSDC/NASA) | Public domain |
| `laika.jpg` | Laika in an experimental space suit | Wikimedia Commons, `File:Laika experimental space dog space suit.jpg` by James Duncan | CC BY-SA 2.0 |
| `gagarin.jpg` | Yuri Gagarin, 1961 (restored) | Wikimedia Commons, `File:Yuri Gagarin (1961) - Restoration.jpg` | Public domain |
| `apollo11.jpg` | Buzz Aldrin on the lunar surface (AS11-40-5903) | Wikimedia Commons, `File:Aldrin Apollo 11 original.jpg` (NASA) | Public domain |
| `iss.jpg` | ISS photographed from Space Shuttle Endeavour (STS-130) | Wikimedia Commons, `File:STS-130 Endeavour flyaround 5.jpg` (NASA) | Public domain |

## Other landing assets

| File | Subject | Source | Terms |
|------|---------|--------|-------|
| `assets/images/hero-deep-field.jpg` | Webb's First Deep Field (SMACS 0723), 1960×2000 | NASA Image Library, id `webb_first_deep_field` (STScI), original PNG re-encoded JPEG q85 | NASA usage guidelines, free with credit |

Also kept, available for future pages: `cosmic-cliffs.jpg`
(Carina Nebula, NASA/STScI), `pillars.jpg` (Pillars of Creation,
ESA/Webb weic2216a, CC BY 4.0).

## Vision page videos

| Video | Channel | Source | Terms |
|-------|---------|--------|-------|
| JWST Launch — Official NASA Broadcast (`7nT7JGZMbtM`) | NASA | youtube.com/watch?v=7nT7JGZMbtM | NASA media, public domain; embedded via official channel |
| Perseverance EDL camera footage (`GUqsH5y1j1M`) | NASA | youtube.com/watch?v=GUqsH5y1j1M | NASA media, public domain |

Embeds use the privacy-enhanced `youtube-nocookie.com` host with
`loading="lazy"`; credit lines appear beneath each player.

## Standing practices

1. Never use agency logos/insignia in site UI.
2. Record license + source + check date per image at download time.
3. Re-verify any SpaceX or third-party-credited imagery before reuse.
4. Credit lines render adjacent to media (mission cards) or directly
   beneath embeds (vision page).
5. Rerun `python3 scripts/build/enrich-missions.py` to backfill gaps —
   it is resumable and skips already-sourced missions.
