# Data model notes

Working notes on how AntarikshPedia's data is structured, and how it needs
to grow. Keep this updated as decisions get made — this is the place to look
before re-deciding something already settled.

## v1 (current): flat mission list, enhanced schema

As of August 2026, `data/missions.json` was rebuilt from a more selective,
better-sourced dataset (`AntarikshPedia_1957-Present_Enhanced_Mission_List.docx`),
replacing an earlier, less curated seed list. 89 entries.

Each mission is a flat record:

| Field         | Type   | Notes                                                        |
|---------------|--------|---------------------------------------------------------------|
| id            | string | slug incl. year, unique identifier                            |
| name          | string | mission/spacecraft/programme name                             |
| year          | string | launch or start year                                          |
| lead_partner  | string | national or international programme (not always a single agency) |
| target        | string | e.g. "Moon", "Mars", "Earth orbit", "Sun–Earth L2"             |
| category      | string | free-text category, e.g. "Lunar orbiter", "Space observatory" |
| status        | string | Success / Partial success / Failure / In transit / Operational |
| outcome       | string | one-line "why it matters" summary                             |
| era           | string | which timeline section it belongs to                          |
| intro         | string | 2-4 sentence write-up, empty until written                    |

This is intentionally flat — no separate Agency/Program entities yet. Good
enough for a single filterable timeline page. The filter bar currently
groups by `lead_partner`.

## Known gaps

Per-mission fields not yet captured, needed for a fuller mission page later:
- launch vehicle
- mass
- orbit/trajectory type
- precise launch date (currently year-only)
- mission duration / end date
- instrument list
- sources / citations
- images
- related missions (cross-links)

These are the fields flagged as "recommended future database fields" in the
source document — worth tackling before Phase 2 individual mission pages.

## Where this needs to go for Phase 2 (per the project concept doc)

The concept doc's information architecture is: **Agency → Program → Mission →
Spacecraft → Components/Instruments → Events/Discoveries/Publications**, with
cross-cutting hubs for people, places, technologies, and historical context.

That means eventually splitting the flat `missions.json` into separate,
linked collections — something like:

- `agencies.json` — one record per agency/programme (NASA, ESA, ISRO, Roscosmos, etc.)
- `missions.json` — mission records, each referencing an agency `id`
- `spacecraft.json` — spacecraft records, each referencing a mission `id`

This is a real restructuring, not just adding fields — it's the point where
a flat JSON file starts to strain and a proper database (or at least linked
JSON files with an id-referencing convention) becomes worth the setup cost.
Not needed for v1. Revisit when Phase 2 planning starts.

## Editorial conventions carried over from the source dataset

- **Outcome labeling**: "Success" describes the main milestone claimed in a
  row, not every objective of the mission. "Partial success" is used
  deliberately to keep real achievements visible without hiding a failed
  landing or lost component.
- **Russia after Mir**: the list includes Phobos-Grunt (2011, failure),
  ExoMars 2016 (ESA–Russia partnership), Nauka/Prichal (2021, ISS
  infrastructure), and Luna 25 (2023, failure) — chosen to avoid overstating
  routine ISS logistics as independent deep-space exploration, while still
  representing Russia's post-Soviet program honestly.
- **Planned missions are excluded** from this core timeline by design. If
  planned/upcoming missions are wanted later, they belong in a separate,
  date-stamped collection so schedule slips don't blur completed history.
