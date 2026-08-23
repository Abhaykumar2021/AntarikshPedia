#!/usr/bin/env python3
"""Validate generated data before a build. Exits non-zero on any failure.

Checks:
  1. missions.json — every record has all required fields non-empty,
     year is an int, status is an allowed value, ids are unique.
  2. related-missions.json — every referenced mission id exists.
  3. agencies.json / countries.json — every agency's country exists;
     every mission id they reference exists; every mission appears on at
     least one agency page.
  4. media blocks — every thumb path exists on disk and carries all five
     license fields (per copyright_guidelines.md).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'src' / '_data'

REQUIRED = ['id', 'name', 'year', 'lead_partner', 'target', 'category',
            'status', 'outcome', 'era']
ALLOWED_STATUSES = {'Success', 'Partial success', 'Failure',
                    'In transit', 'Operational'}
MEDIA_FIELDS = ['thumb', 'credit', 'license', 'source', 'checked']


def main() -> None:
    errors: list[str] = []

    def load(name: str):
        path = DATA / name
        if not path.exists():
            errors.append(f'missing data file: {path.name}')
            return []
        return json.loads(path.read_text(encoding='utf-8'))

    missions = load('missions.json')
    if not missions:
        print('FATAL: no missions parsed', file=sys.stderr)
        sys.exit(1)

    ids = set()
    for m in missions:
        mid = m.get('id', '<no-id>')
        for field in REQUIRED:
            value = m.get(field)
            if value is None or value == '':
                errors.append(f'{mid}: missing/empty field "{field}"')
        if not isinstance(m.get('year'), int):
            errors.append(f'{mid}: year must be an integer')
        if m.get('status') not in ALLOWED_STATUSES:
            errors.append(f'{mid}: invalid status "{m.get("status")}"')
        ids.add(mid)

    dupes = len(missions) - len(ids)
    if dupes:
        errors.append(f'{dupes} duplicate mission ids')

    # related-missions referential integrity
    for mid, rels in load('relatedMissions.json').items():
        if mid not in ids:
            errors.append(f'related-missions: unknown source {mid}')
        for rel in rels:
            if rel['id'] not in ids:
                errors.append(f'{mid}: relates to unknown mission {rel["id"]}')
            if rel['type'] not in {'same_target', 'same_program', 'competitor'}:
                errors.append(f'{mid}: bad relation type "{rel["type"]}"')

    # agencies + countries
    covered: set[str] = set()
    for agency in load('agencies.json'):
        if agency['country'] not in {c['id'] for c in load('countries.json')}:
            errors.append(f'agency {agency["id"]}: unknown country '
                          f'{agency["country"]}')
        for mid in agency['mission_ids']:
            if mid not in ids:
                errors.append(f'agency {agency["id"]}: unknown mission {mid}')
            covered.add(mid)

    for country in load('countries.json'):
        for mid in country['mission_ids']:
            if mid not in ids:
                errors.append(
                    f'country {country["id"]}: unknown mission {mid}')

    uncovered = ids - covered
    if uncovered:
        errors.append(f'{len(uncovered)} missions belong to no agency: '
                      f'{sorted(uncovered)[:5]}...')

    # media license records
    for m in missions:
        media = m.get('media')
        if not media:
            continue
        for field in MEDIA_FIELDS:
            if not media.get(field):
                errors.append(f'{m["id"]}: media missing "{field}"')
        if not (ROOT / 'src' / media['thumb']).exists():
            errors.append(f'{m["id"]}: media thumb not found '
                          f'{media["thumb"]}')

    # spec fields (when present) must be sane
    for m in missions:
        if 'launch_date' in m and not re.match(
                r'^\d{4}-\d{2}-\d{2}$', str(m['launch_date'])):
            errors.append(f'{m["id"]}: launch_date must be ISO YYYY-MM-DD')
        for numeric in ('mass_kg',):
            if numeric in m and not isinstance(m[numeric], (int, float)):
                errors.append(f'{m["id"]}: {numeric} must be a number')

    if errors:
        print(f'VALIDATION FAILED ({len(errors)} problems):', file=sys.stderr)
        for e in errors[:40]:
            print(f'  - {e}', file=sys.stderr)
        sys.exit(1)

    print(f'validation OK: {len(missions)} missions, '
          f'related links, agencies/countries, and media licenses all pass')


if __name__ == '__main__':
    main()
