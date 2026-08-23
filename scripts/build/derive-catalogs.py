#!/usr/bin/env python3
"""Derive agency, country, and related-mission catalogs from missions.json.

Outputs (all generated — never hand-edit):
  src/_data/agencies.json          one record per agency/program
  src/_data/countries.json         one record per country/entity
  src/_data/related-missions.json  { mission_id: [ {id, type}, ... ] }

Agency/country attribution is a mapping of the free-text `lead_partner`
values that actually occur in the dataset. A mission with multiple partners
("NASA / ESA") is listed on every partner's page. Where the source text
names a country rather than an agency ("United States", "Soviet Union"),
the mission is attributed to that country's national program record — the
overview text states this plainly instead of inventing an organizational
attribution the data does not contain.

Related missions are proposed by rule: same target, same category, or a
contemporary launch within ±2 years by a different lead (competitor).
Each mission keeps its top 4 candidates.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'src' / '_data'

# ---------------------------------------------------------------------------
# Agency registry: slug -> record. founded_year / overview are factual; where
# a country-level program stands in for several historical organizations, the
# overview says so explicitly.
# ---------------------------------------------------------------------------
AGENCIES = {
    'nasa': {
        'name': 'NASA',
        'country': 'united-states',
        'founded_year': 1958,
        'overview': (
            'The National Aeronautics and Space Administration, the United '
            'States\u2019 civilian space agency, opened on 1 October 1958. '
            'It absorbed the country\u2019s earlier military space teams '
            '\u2014 the Army Ballistic Missile Agency team that became '
            'Marshall, Caltech\u2019s Jet Propulsion Laboratory, and the '
            'Navy\u2019s Vanguard group \u2014 so missions credited simply '
            'to the United States (including pre-NASA flights like Explorer '
            '1 and Vanguard 1) are tracked here as part of that lineage.'
        ),
    },
    'soviet-program': {
        'name': 'Soviet space program',
        'country': 'soviet-union',
        'founded_year': 1957,
        'overview': (
            'The USSR ran its civil and military space work through design '
            'bureaus \u2014 Korolev\u2019s OKB-1 chief among them \u2014 under '
            'state ministries rather than a single public agency. Records '
            'attributed to "Soviet Union" reflect this program structure.'
        ),
    },
    'roscosmos': {
        'name': 'Roscosmos',
        'country': 'russia',
        'founded_year': 1992,
        'overview': (
            'The Russian state space corporation, formed in 1992 as the '
            'successor to the Soviet program within the new Russian Federation.'
        ),
    },
    'esa': {
        'name': 'ESA',
        'country': 'europe',
        'founded_year': 1975,
        'overview': (
            'The European Space Agency, an intergovernmental organization of '
            'European member states formed in 1975 from the merger of ESRO '
            'and ELDO.'
        ),
    },
    'cnsa': {
        'name': 'CNSA',
        'country': 'china',
        'founded_year': 1993,
        'overview': (
            'The China National Space Administration, the country\u2019s '
            'national space agency; earlier Chinese missions were conducted '
            'through state aerospace ministries and CAST.'
        ),
    },
    'jaxa': {
        'name': 'JAXA',
        'country': 'japan',
        'founded_year': 2003,
        'overview': (
            'The Japan Aerospace Exploration Agency, formed in 2003 by the '
            'merger of ISAS, NASDA, and NAL. Missions credited simply to '
            '"Japan" predate or predate-by-organization this merger and flew '
            'under ISAS or NASDA.'
        ),
    },
    'isro': {
        'name': 'ISRO',
        'country': 'india',
        'founded_year': 1969,
        'overview': (
            'The Indian Space Research Organisation, formed in 1969 from the '
            'Indian National Committee for Space Research (INCOSPAR, 1962).'
        ),
    },
    'cnes': {
        'name': 'CNES',
        'country': 'france',
        'founded_year': 1961,
        'overview': (
            'The French national space agency, founded in 1961 and a leading '
            'partner in later European cooperative projects.'
        ),
    },
    'asi': {
        'name': 'ASI',
        'country': 'italy',
        'founded_year': 1988,
        'overview': (
            'The Italian Space Agency, founded in 1988; Italian participation '
            'in earlier missions ran through CNR and industry.'
        ),
    },
    'csa': {
        'name': 'CSA',
        'country': 'canada',
        'founded_year': 1989,
        'overview': (
            'The Canadian Space Agency, established in 1989, continuing a '
            'space program that dates to the 1962 Alouette 1 satellite.'
        ),
    },
    'uk-program': {
        'name': 'United Kingdom space program',
        'country': 'united-kingdom',
        'founded_year': 1964,
        'overview': (
            'British missions were run through the Science Research Council '
            'and predecessors; the UK Space Agency itself was founded in 2010.'
        ),
    },
    'dlr': {
        'name': 'DLR',
        'country': 'germany',
        'founded_year': 1989,
        'overview': (
            'The German Aerospace Center, formed in its modern shape in 1989; '
            'German participation in earlier missions ran through DFVLR and '
            'predecessors.'
        ),
    },
    'netherlands-program': {
        'name': 'Netherlands space program',
        'country': 'netherlands',
        'founded_year': 1971,
        'overview': (
            'Dutch participation in early astronomy missions ran through the '
            'Netherlands Agency for Aerospace Programmes (NIVR) and university '
            'institutes such as SRON.'
        ),
    },
    'uae-space-agency': {
        'name': 'UAE Space Agency',
        'country': 'united-arab-emirates',
        'founded_year': 2014,
        'overview': (
            'The United Arab Emirates Space Agency, founded in 2014, with the '
            'Mohammed bin Rashid Space Centre in Dubai building and operating '
            'its Mars spacecraft.'
        ),
    },
    'scaled-composites': {
        'name': 'Scaled Composites',
        'country': 'united-states',
        'founded_year': 1982,
        'overview': (
            'Burt Rutan\u2019s Mojave-based aerospace firm, builder and operator '
            'of SpaceShipOne, the first crewed private suborbital spacecraft.'
        ),
    },
    'intuitive-machines': {
        'name': 'Intuitive Machines',
        'country': 'united-states',
        'founded_year': 2013,
        'overview': (
            'A Houston-based commercial lunar services company flying landers '
            'under NASA\u2019s Commercial Lunar Payload Services program.'
        ),
    },
    'firefly-aerospace': {
        'name': 'Firefly Aerospace',
        'country': 'united-states',
        'founded_year': 2014,
        'overview': (
            'A commercial launch and lunar-delivery company flying Blue Ghost '
            'landers under NASA\u2019s CLPS program.'
        ),
    },
    'international': {
        'name': 'International partnership',
        'country': 'international',
        'founded_year': None,
        'overview': (
            'Missions credited collectively to international partnerships, '
            'where no single lead organization dominates the record.'
        ),
    },
}

# lead_partner token -> agency slug
TOKEN_MAP = {
    'nasa': 'nasa',
    'esa': 'esa',
    'roscosmos': 'roscosmos',
    'cnsa': 'cnsa',
    'jaxa': 'jaxa',
    'isro': 'isro',
    'cnes': 'cnes',
    'asi': 'asi',
    'csa': 'csa',
    'dlr': 'dlr',
    'scaled composites': 'scaled-composites',
    'intuitive machines': 'intuitive-machines',
    'firefly aerospace': 'firefly-aerospace',
    'nasa clps': 'nasa',
    'soviet union': 'soviet-program',
    'united states': 'nasa',
    'china': 'cnsa',
    'japan': 'jaxa',
    'india': 'isro',
    'russia': 'roscosmos',
    'united arab emirates': 'uae-space-agency',
    'united kingdom': 'uk-program',
    'germany': 'dlr',
    'netherlands': 'netherlands-program',
    'france': 'cnes',
    'italy': 'asi',
    'international': 'international',
    'international partnership': 'international',
    'international partners': 'international',
    'france / esa partners'.split('/')[-1].strip(): None,  # placeholder guard
}

# countries.json content
COUNTRIES = {
    'united-states': {'name': 'United States', 'iso_code': 'US'},
    'soviet-union': {'name': 'Soviet Union', 'iso_code': 'SU'},
    'russia': {'name': 'Russia', 'iso_code': 'RU'},
    'europe': {
        'name': 'Europe (multi-national)',
        'iso_code': 'EU',
        'note': 'Stands for the European Space Agency and its member states.',
    },
    'china': {'name': 'China', 'iso_code': 'CN'},
    'japan': {'name': 'Japan', 'iso_code': 'JP'},
    'india': {'name': 'India', 'iso_code': 'IN'},
    'france': {'name': 'France', 'iso_code': 'FR'},
    'italy': {'name': 'Italy', 'iso_code': 'IT'},
    'canada': {'name': 'Canada', 'iso_code': 'CA'},
    'united-kingdom': {'name': 'United Kingdom', 'iso_code': 'GB'},
    'germany': {'name': 'Germany', 'iso_code': 'DE'},
    'netherlands': {'name': 'Netherlands', 'iso_code': 'NL'},
    'united-arab-emirates': {'name': 'United Arab Emirates', 'iso_code': 'AE'},
    'international': {
        'name': 'International',
        'iso_code': None,
        'note': 'Multi-country partnerships not attributable to one nation.',
    },
}


def resolve_agencies(lead_partner: str) -> list[str]:
    """Split a lead_partner string into canonical agency slugs."""
    tokens = [t.strip() for t in lead_partner.split('/') if t.strip()]
    slugs = []
    for token in tokens:
        # tolerate composite labels like "ESA partners"
        key = token.lower().replace(' partners', '').strip()
        slug = TOKEN_MAP.get(key) or TOKEN_MAP.get(token.lower())
        if slug is None:
            raise ValueError(f'unmapped lead_partner token: "{token}"')
        if slug not in slugs:
            slugs.append(slug)
    return slugs


def main() -> None:
    missions = json.loads((DATA / 'missions.json').read_text(encoding='utf-8'))

    # ---- agencies + countries ----
    agency_missions: dict[str, list[str]] = {}
    country_missions: dict[str, list[str]] = {}
    unmapped = set()

    for m in missions:
        try:
            slugs = resolve_agencies(m['lead_partner'])
        except ValueError as e:
            unmapped.add(str(e))
            continue
        for slug in slugs:
            agency_missions.setdefault(slug, []).append(m['id'])
            country = AGENCIES[slug]['country']
            country_missions.setdefault(country, []).append(m['id'])

    if unmapped:
        raise SystemExit(f'unmapped lead_partner values: {sorted(unmapped)}')

    agencies_out = []
    for slug, info in AGENCIES.items():
        agencies_out.append({
            'id': slug,
            'slug': slug,
            **info,
            'mission_ids': agency_missions.get(slug, []),
        })
    (DATA / 'agencies.json').write_text(
        json.dumps(agencies_out, ensure_ascii=False, indent=2) + '\n')

    countries_out = []
    for slug, info in COUNTRIES.items():
        entry = {
            'id': slug,
            'slug': slug,
            'name': info['name'],
            'iso_code': info.get('iso_code'),
            'agency_ids': [
                a['id'] for a in agencies_out if a['country'] == slug
            ],
            'mission_ids': sorted(set(country_missions.get(slug, []))),
        }
        if info.get('note'):
            entry['note'] = info['note']
        countries_out.append(entry)
    (DATA / 'countries.json').write_text(
        json.dumps(countries_out, ensure_ascii=False, indent=2) + '\n')

    # ---- related missions ----
    related: dict[str, list[dict]] = {}
    for m in missions:
        scored = []
        for other in missions:
            if other['id'] == m['id']:
                continue
            dy = abs(other['year'] - m['year'])
            if other['target'] == m['target'] and dy <= 12:
                rtype, score = ('same_target', 100 - dy)
            elif other['category'] == m['category'] and dy <= 8:
                rtype, score = ('same_program', 60 - dy)
            elif dy <= 2 and other['lead_partner'] != m['lead_partner']:
                rtype, score = ('competitor', 30 - dy)
            else:
                continue
            scored.append({'id': other['id'], 'type': rtype, '_score': score})
        scored.sort(key=lambda x: -x['_score'])
        related[m['id']] = [
            {'id': s['id'], 'type': s['type']} for s in scored[:4]
        ]

    (DATA / 'relatedMissions.json').write_text(
        json.dumps(related, ensure_ascii=False, indent=2) + '\n')

    linked = sum(1 for v in related.values() if v)
    print(f'agencies: {len(agencies_out)}, countries: {len(countries_out)}, '
          f'missions with related links: {linked}/{len(missions)}')


if __name__ == '__main__':
    main()
