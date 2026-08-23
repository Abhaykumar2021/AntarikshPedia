#!/usr/bin/env python3
"""Research enrichment pass for all missions.

For every mission in src/_data/missions.json this script:
  1. Finds the best-matching Wikipedia article and parses its spaceflight
     infobox for factual spec fields: launch date, launch vehicle, mass,
     orbit, duration. Only cleanly-parsed values are recorded — anything
     ambiguous stays absent (pages then say "unknown" rather than guess).
  2. Sources a photo when the mission has none: NASA Image Library first
     (public domain), else Wikimedia Commons with an explicit license-tag
     check (PD / CC0 / CC BY / CC BY-SA only). Files land in the per-mission
     folder assets/images/missions/<id>/photo.jpg.

Outputs (merged into builds via generate-missions-json.py):
  scripts/build/spec-overrides.json
  scripts/build/media-overrides.json   (extended in place)

Resumable: missions already present in both outputs are skipped.
Politeness: 0.15 s between network calls; descriptive User-Agent.
"""

import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'src' / '_data' / 'missions.json'
SPEC_OUT = ROOT / 'scripts' / 'build' / 'spec-overrides.json'
MEDIA_OUT = ROOT / 'scripts' / 'build' / 'media-overrides.json'
IMG_ROOT = ROOT / 'src' / 'assets' / 'images' / 'missions'
TMP = Path('/var/folders/52/rkhhtrb55q165ld8bkf618km0000gn/T/opencode')
if not TMP.exists():
    TMP = Path('/tmp')

UA = 'AntarikshPediaResearchBot/1.0 (educational encyclopedia; contact via repo)'
DELAY = 0.15

OK_LICENSES = re.compile(
    r'(public domain|cc0|cc by(-sa)? [1-4]|attribution)', re.I)


def curl_json(url: str):
    out = subprocess.run(
        ['curl', '-sL', '--max-time', '20', '-A', UA, url],
        capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def curl_file(url: str, dest: Path) -> bool:
    r = subprocess.run(['curl', '-sL', '--max-time', '40', '-A', UA,
                        '-o', str(dest), url])
    return r.returncode == 0 and dest.exists() and dest.stat().st_size > 15000


# ---------------------------------------------------------------- wikipedia

WIKI_API = 'https://en.wikipedia.org/w/api.php'


def wiki_title(name: str, year: int) -> str | None:
    q = urllib.parse.urlencode({
        'action': 'query', 'list': 'search', 'srsearch':
            f'{name} spacecraft {year}', 'srlimit': 1, 'format': 'json'})
    data = curl_json(f'{WIKI_API}?{q}')
    hits = (data or {}).get('query', {}).get('search', [])
    if not hits:
        q = urllib.parse.urlencode({
            'action': 'query', 'list': 'search', 'srsearch':
                name, 'srlimit': 1, 'format': 'json'})
        data = curl_json(f'{WIKI_API}?{q}')
        hits = (data or {}).get('query', {}).get('search', [])
    return hits[0]['title'] if hits else None


def wiki_wikitext(title: str) -> str:
    q = urllib.parse.urlencode({
        'action': 'query', 'prop': 'revisions', 'rvprop': 'content',
        'rvslots': 'main', 'titles': title, 'format': 'json',
        'rvlimit': 1})
    data = curl_json(f'{WIKI_API}?{q}')
    pages = (data or {}).get('query', {}).get('pages', {})
    for page in pages.values():
        revs = page.get('revisions', [])
        if revs:
            return revs[0]['slots']['main']['*'] or ''
    return ''


MONTHS = {m.lower(): i for i, m in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}

TEMPLATE_WORDS = re.compile(r'\{\{|\}\}|\[\[|\]\}|<[^>]+>')


def clean(value: str) -> str:
    value = re.sub(r'\{\{[^{}]*\}\}', '', value)
    value = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', value)
    value = re.sub(r'<ref[^>]*>.*?</ref>', '', value, flags=re.S)
    value = re.sub(r'<[^>]+>', '', value)
    value = re.sub(r'\)\s*(?=\S)', ') ', value)   # keep parentheticals spaced
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def parse_date(value: str) -> str | None:
    """ISO YYYY-MM-DD from wikitext dates like '4 October 1957'."""
    v = clean(value)
    m = re.search(r'(\d{1,2})\s+([A-Za-z]{3,9}),?\s+(\d{4})', v)
    if m:
        day, mon, year = m.groups()
        if mon[:3].lower() in MONTHS:
            return f'{year}-{MONTHS[mon[:3].lower()]:02d}-{int(day):02d}'
    m = re.search(r'([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})', v)
    if m:
        mon, day, year = m.groups()
        if mon[:3].lower() in MONTHS:
            return f'{year}-{MONTHS[mon[:3].lower()]:02d}-{int(day):02d}'
    return None


def parse_mass_kg(value: str) -> int | None:
    v = clean(value)
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*(kg|kilograms?|t\b|tonnes?)', v, re.I)
    if not m:
        # bare number field (infobox mass is usually kg already)
        m2 = re.search(r'^\s*([\d,]+)\s*$', v)
        if m2:
            return int(m2.group(1).replace(',', ''))
        return None
    num = float(m.group(1).replace(',', ''))
    unit = m.group(2).lower()
    if unit.startswith('t'):
        num *= 1000
    return round(num)


def infobox(text: str) -> str:
    """Extract the first {{Infobox ...}} block with brace balancing."""
    m = re.search(r'\{\{\s*[Ii]nfobox[_ ]space[a-z ]*', text)
    if not m:
        m = re.search(r'\{\{\s*[Ii]nfobox', text)
    if not m:
        return ''
    start = m.start() + 2
    depth = 2
    i = start
    while i < len(text) - 1 and depth > 0:
        if text[i:i + 2] == '{{':
            depth += 1
            i += 2
        elif text[i:i + 2] == '}}':
            depth -= 1
            i += 2
        else:
            i += 1
    return text[start:i - 2]


FIELD_ALIASES = {
    'launch_date': ['launch_date', 'launch'],
    'launch_vehicle': ['launch_rocket', 'launch_vehicle', 'rocket'],
    'mass_kg': ['mass', 'launch_mass', 'spacecraft_mass', 'landing_mass'],
    'orbit_type': ['orbit_reference', 'orbit_regime', 'orbit_parameters'],
    'duration': ['mission_duration', 'duration', 'mission_end', 'end_date',
                 'landing_date'],
}


def extract_specs(wikitext: str) -> dict:
    box = infobox(wikitext)
    if not box:
        return {}
    fields = {}
    for line in box.split('\n'):
        m = re.match(r'\s*\|\s*([a-z_0-9 ]+?)\s*=\s*(.+)', line, re.I)
        if m:
            key = m.group(1).strip().lower().replace(' ', '_')
            fields[key] = m.group(2).strip()

    specs = {}

    def first(*names):
        for n in names:
            v = fields.get(n, '').strip()
            if v:
                return v
        return None

    raw_date = first(*FIELD_ALIASES['launch_date'])
    if raw_date:
        iso = parse_date(raw_date)
        if iso:
            specs['launch_date'] = iso

    raw_vehicle = first(*FIELD_ALIASES['launch_vehicle'])
    if raw_vehicle:
        vehicle = clean(raw_vehicle).split('(')[0].split('/')[0].strip()
        if 2 < len(vehicle) < 60 and 'rocket' in vehicle.lower() or \
           re.match(r'^[A-Z][\w\- ]+$', vehicle):
            specs['launch_vehicle'] = vehicle

    raw_mass = first(*FIELD_ALIASES['mass_kg'])
    if raw_mass:
        kg = parse_mass_kg(raw_mass)
        if kg and 1 < kg < 1_000_000:
            specs['mass_kg'] = kg

    raw_orbit = first(*FIELD_ALIASES['orbit_type'])
    if raw_orbit:
        orbit = clean(raw_orbit).split(',')[0].strip()
        if 0 < len(orbit) < 50 and TEMPLATE_WORDS.pattern:
            specs['orbit_type'] = orbit

    raw_duration = first(*FIELD_ALIASES['duration'])
    if raw_duration:
        dur = clean(raw_duration)
        if re.search(r'\d', dur) and len(dur) < 80 and \
                not parse_date(dur):  # skip if it was really a date field
            specs['duration'] = dur

    return {k: v for k, v in specs.items() if v}


# ---------------------------------------------------------------- images

def nasa_relevant(title: str, name: str, nasa_id: str, year: int) -> bool:
    """Gate NASA search hits: token overlap wins outright; otherwise an ID
    carrying a plausibly matching year (KSC-2013, s65-, 81PC, ARC-1991...)
    passes; anything else is rejected rather than risk a wrong photo."""
    tokens = name_tokens(name)
    title_l = title.lower()
    if any(t in title_l for t in tokens):
        return True
    m = re.search(r'(19|20)\d{2}', nasa_id)
    if m:
        return abs(int(m.group(0)) - year) <= 1
    m = re.search(r'-(\d{2})[a-z]', nasa_id.lower()) or \
        re.match(r'^[a-z]{0,3}(\d{2})', nasa_id.lower())
    if m:
        yy = int(m.group(1))
        full = 1900 + yy if yy > 25 else 2000 + yy
        return abs(full - year) <= 1
    return False


def nasa_image(query: str, dest: Path, name: str = '', year: int = 0) -> dict | None:
    q = urllib.parse.urlencode({'q': query, 'media_type': 'image'})
    data = curl_json(f'https://images-api.nasa.gov/search?{q}')
    items = (data or {}).get('collection', {}).get('items', [])
    # scan several hits until one passes the relevance gate
    for item in items[:6]:
        nasa_id = item['data'][0]['nasa_id']
        title = item['data'][0].get('title', '')
        if not nasa_relevant(title, name, nasa_id, year):
            continue
        assets = curl_json(f'https://images-api.nasa.gov/asset/{nasa_id}')
        hrefs = [a['href'].replace('http://', 'https://')
                 for a in (assets or {}).get('collection', {}).get('items', [])]
        pick = next((h for h in hrefs if '~medium.jpg' in h), None) or \
            next((h for h in hrefs if '~large.jpg' in h), None) or \
            next((h for h in hrefs if '~small.jpg' in h), None)
        if not pick or not curl_file(pick, dest):
            continue
        return {
            'credit': 'Image credit: NASA',
            'license': 'public-domain',
            'source': f'https://images.nasa.gov/details/{nasa_id}',
            'checked': '2026-08-23',
        }
    return None


STOP_TOKENS = {'the', 'of', 'and', 'first', 'space', 'mission', 'satellite',
               'lander', 'rover', 'probe', 'observatory', 'station'}


def name_tokens(name: str) -> set[str]:
    """Distinctive words from the mission name, incl. parenthetical aliases."""
    raw = re.findall(r"[A-Za-z0-9']+", name.lower())
    return {t for t in raw if len(t) > 2 and t not in STOP_TOKENS}


SPACE_HINT = re.compile(
    r'spacecraft|satellite|space|rocket|launch|orbit|lunar|moon|mars|venus'
    r'|comet|asteroid|planetary|cosmonaut|astronaut|nasa|esa|isro|jaxa'
    r'|sonde|probe', re.I)


def commons_relevant(page_title: str, categories: str,
                     mission_name: str) -> bool:
    """Commons picks MUST carry space-related categories on the file page.
    Title-token overlap alone rejected false positives like a person named
    Uhuru or a hashtag sign matching SMART-1."""
    _ = page_title, mission_name
    return bool(categories and SPACE_HINT.search(categories))


def commons_image(name: str, dest: Path) -> dict | None:
    q = urllib.parse.urlencode({
        'action': 'query', 'format': 'json', 'generator': 'search',
        'gsrsearch': f'filetype:bitmap {name}', 'gsrnamespace': '6',
        'gsrlimit': '8', 'prop': 'imageinfo',
        'iiprop': 'url|size|extmetadata'})
    data = curl_json(f'https://commons.wikimedia.org/w/api.php?{q}')
    pages = sorted((data or {}).get('query', {}).get('pages', {}).values(),
                   key=lambda p: p.get('index', 99))
    for page in pages:
        ii = (page.get('imageinfo') or [None])[0]
        if not ii:
            continue
        emeta = ii.get('extmetadata', {})
        lic = emeta.get('LicenseShortName', {}).get('value', '')
        if not lic or not OK_LICENSES.search(lic):
            continue
        if ii.get('width', 0) < 500:
            continue
        categories = emeta.get('Categories', {}).get('value', '')
        if not commons_relevant(page['title'], categories, name):
            continue
        title_enc = urllib.parse.quote(page['title'].replace(' ', '_'))
        url = ('https://commons.wikimedia.org/w/index.php'
               f'?title=Special:Redirect/file/{title_enc}&width=1000')
        if curl_file(url, dest):
            lic_l = lic.lower()
            license_key = ('public-domain' if 'public domain' in lic_l
                           else 'cc0' if 'cc0' in lic_l
                           else lic.lower().replace(' ', '-'))
            artist = emeta.get('Artist', {}).get('value', 'Wikimedia Commons')
            artist_clean = clean(artist)[:60]
            return {
                'credit': f'{artist_clean}, via Wikimedia Commons — {lic}',
                'license': license_key,
                'source': ('https://commons.wikimedia.org/wiki/'
                           + page['title'].replace(' ', '_')),
                'checked': '2026-08-23',
            }
    return None


# ---------------------------------------------------------------- main

def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    missions = json.loads(DATA.read_text(encoding='utf-8'))
    specs = load_json(SPEC_OUT, {})
    media = load_json(MEDIA_OUT, {})

    done = stats = img_added = 0
    for idx, m in enumerate(missions):
        mid = m['id']
        has_specs = any(k in m for k in
                        ('launch_vehicle', 'mass_kg', 'orbit_type')) \
            or mid in specs
        has_media = mid in media

        if has_specs and has_media:
            continue
        if limit and done >= limit:
            break

        note = []
        # ---- specs ----
        if not has_specs:
            title = wiki_title(m['name'], m['year'])
            time.sleep(DELAY)
            if title:
                text = wiki_wikitext(title)
                time.sleep(DELAY)
                found = extract_specs(text)
                if found:
                    specs[mid] = found
                    note.append(f"{len(found)} specs")
            else:
                time.sleep(DELAY)

        # ---- image ----
        if not has_media:
            folder = IMG_ROOT / mid
            folder.mkdir(parents=True, exist_ok=True)
            dest = folder / 'photo.jpg'
            rec = nasa_image(f"{m['name']} {m['target']}", dest,
                             m['name'], m['year'])
            if rec:
                media[mid] = rec
                img_added += 1
                note.append('NASA img')
            else:
                time.sleep(DELAY)
                rec = commons_image(m['name'], dest)
                if rec:
                    media[mid] = rec
                    img_added += 1
                    note.append('Commons img')
                elif dest.exists():
                    dest.unlink()
                time.sleep(DELAY)

        done += 1
        if note:
            print(f"[{idx+1}/{len(missions)}] {mid}: {', '.join(note)}",
                  flush=True)

        # periodic saves so the run is resumable
        if done % 10 == 0:
            save_json(SPEC_OUT, specs)
            save_json(MEDIA_OUT, media)

    save_json(SPEC_OUT, specs)
    save_json(MEDIA_OUT, media)
    print(f'DONE: processed {done} missions this run; '
          f'{img_added} new images; '
          f'{len(specs)} missions have specs; '
          f'{len(media)} missions have media', flush=True)


if __name__ == '__main__':
    main()
