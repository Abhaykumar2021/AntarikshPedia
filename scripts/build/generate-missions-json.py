#!/usr/bin/env python3
"""Generate src/_data/missions.json from data-sources/missions_timeline.md.

This is the ONLY sanctioned way to produce missions.json — the file is
generated output and must never be hand-edited. If the markdown source
changes, rerun this script (or `npm run data`).

Line format per mission:
    - **Name** (Year) — Lead/partner · Target · Category — Outcome text. [Status]

Entries are grouped under six `## <era>` headings. Validation is strict:
every entry needs all nine fields non-empty and a status from the allowed
set; the script exits non-zero on any parse failure instead of skipping.

Optional: scripts/build/media-overrides.json maps mission id → media block
(thumb/credit/license/source/checked). It is merged in after parsing so
image-license records survive regeneration.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'data-sources' / 'missions_timeline.md'
OUT = ROOT / 'src' / '_data' / 'missions.json'
OVERRIDES = ROOT / 'scripts' / 'build' / 'media-overrides.json'
LAUNCH_DATES = ROOT / 'src' / '_data' / 'launch-dates.json'

ALLOWED_STATUSES = {
    'Success', 'Partial success', 'Failure', 'In transit', 'Operational',
}

# - **Name** (Year) — Lead · Target · Category — Outcome. [Status]
LINE_RE = re.compile(
    r'^- \*\*(?P<name>.+?)\*\* \((?P<year>\d{4})\) — '
    r'(?P<lead>.+?) · (?P<target>.+?) · (?P<category>.+?) — '
    r'(?P<outcome>.+?) \[(?P<status>[^\]]+)\]$'
)

HEADING_RE = re.compile(r'^## (?P<era>\d{4}–(?:\d{4}|Present): .+)$')


def slugify(name: str, year: str) -> str:
    """Lowercase, alphanumeric + hyphens only.

    Apostrophes become hyphens so "Chang’e" slugs to "chang-e" — this
    matches the id convention already used by existing media assets.
    """
    s = name.replace('\u2019', '-').replace("'", '-')
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return f'{s}-{year}'


def parse(path: Path) -> list[dict]:
    missions: list[dict] = []
    era = None
    errors: list[str] = []

    for lineno, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('# ') or line.startswith('`') \
                or line.startswith('Ground-truth') or line.startswith('`- **'):
            continue
        heading = HEADING_RE.match(line)
        if heading:
            era = heading.group('era')
            continue

        m = LINE_RE.match(line)
        if not m:
            if line.startswith('- **'):
                errors.append(f'line {lineno}: malformed entry: {line[:90]}')
            continue

        year = m.group('year')
        status = m.group('status').strip()
        record = {
            'id': slugify(m.group('name'), year),
            'name': m.group('name').strip(),
            'year': int(year),
            'lead_partner': m.group('lead').strip(),
            'target': m.group('target').strip(),
            'category': m.group('category').strip(),
            'status': status,
            'outcome': m.group('outcome').strip(),
            'era': era,
        }

        # strict validation — fail loudly
        for field, value in record.items():
            if value in (None, '', []):
                errors.append(f"line {lineno}: empty field '{field}'")
        if status not in ALLOWED_STATUSES:
            errors.append(f'line {lineno}: invalid status "{status}"')

        missions.append(record)

    ids = [r['id'] for r in missions]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f'duplicate ids: {sorted(dupes)}')
    if errors:
        print('PARSE FAILED:', file=sys.stderr)
        for e in errors:
            print(f'  - {e}', file=sys.stderr)
        sys.exit(1)

    return missions


def merge_overrides(missions: list[dict]) -> None:
    if not OVERRIDES.exists():
        return
    overrides = json.loads(OVERRIDES.read_text(encoding='utf-8'))
    applied = 0
    for record in missions:
        if record['id'] in overrides:
            media = dict(overrides[record['id']])
            # per-mission asset folder layout; an explicit thumb in the
            # override always wins
            media.setdefault('thumb',
                             f"assets/images/missions/{record['id']}/photo.jpg")
            items = list(record.items())
            items.append(('media', media))
            record.clear()
            record.update(dict(items))
            applied += 1
    print(f'media overrides applied: {applied}')


SPEC_FIELDS = ['launch_date', 'launch_vehicle', 'mass_kg', 'orbit_type',
               'duration']


def merge_specs(missions: list[dict]) -> None:
    """Attach researched specification fields from spec-overrides.json.

    Values here come from the enrichment pipeline (scripts/build/
    enrich-missions.py), which only records facts parsed from cited public
    sources. Missing fields stay absent — pages render them as unknown.
    """
    path = ROOT / 'scripts' / 'build' / 'spec-overrides.json'
    if not path.exists():
        return
    specs = json.loads(path.read_text(encoding='utf-8'))
    applied = 0
    for record in missions:
        extra = {k: v for k, v in specs.get(record['id'], {}).items()
                 if k in SPEC_FIELDS and v and k not in record}
        if not extra:
            continue
        items = list(record.items())
        items.extend(extra.items())
        record.clear()
        record.update(dict(items))
        applied += 1
    print(f'spec fields merged for {applied} missions')


def merge_launch_dates(missions: list[dict]) -> None:
    """Attach known precise launch dates (see gen-launch-dates.py)."""
    if not LAUNCH_DATES.exists():
        return
    dates = json.loads(LAUNCH_DATES.read_text(encoding='utf-8'))
    applied = 0
    for record in missions:
        if record['id'] in dates:
            items = list(record.items())
            items.append(('launch_date', dates[record['id']]))
            record.clear()
            record.update(dict(items))
            applied += 1
    print(f'launch dates merged: {applied}')


def main() -> None:
    if not SRC.exists():
        print(f'FATAL: source file missing: {SRC}', file=sys.stderr)
        sys.exit(1)
    missions = parse(SRC)
    merge_overrides(missions)
    merge_launch_dates(missions)
    merge_specs(missions)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(missions, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    print(f'wrote {len(missions)} missions -> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
