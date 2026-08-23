import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Well-documented launch dates for landmark missions only.
# These are unambiguous historical facts used for the homepage
# "On this day" feature and the quick-facts strip. Missions not listed
# here simply show no launch date rather than a guessed one.
LAUNCH_DATES = {
    'sputnik-1-1957': '1957-10-04',
    'sputnik-2-1957': '1957-11-03',
    'explorer-1-1958': '1958-01-31',
    'vanguard-1-1958': '1958-03-17',
    'luna-2-1959': '1959-09-12',
    'luna-3-1959': '1959-10-07',
    'vostok-1-1961': '1961-04-12',
    'mariner-2-1962': '1962-08-27',
    'syncom-2-1963': '1963-07-26',
    'ranger-7-1964': '1964-07-28',
    'gemini-4-1965': '1965-06-03',
    'mariner-4-1965': '1964-11-28',
    'voskhod-2-1965': '1965-03-18',
    'luna-9-1966': '1966-01-31',
    'surveyor-1-1966': '1966-05-30',
    'apollo-8-1968': '1968-12-21',
    'zond-5-1968': '1968-09-14',
    'apollo-11-1969': '1969-07-16',
    'luna-16-1970': '1970-09-12',
    'lunokhod-1-1970': '1970-11-10',
    'salyut-1-1971': '1971-04-19',
    'mars-3-1971': '1971-05-28',
    'apollo-17-1972': '1972-12-07',
    'pioneer-10-1972': '1972-03-02',
    'pioneer-11-1973': '1973-04-05',
    'skylab-1973': '1973-05-14',
    'mariner-10-1974': '1973-11-03',
    'apollo-soyuz-test-project-1975': '1975-07-15',
    'aryabhata-1975': '1975-04-19',
    'viking-1-1975': '1975-08-20',
    'voyager-1-2-1977': '1977-08-20',
    'sts-1-columbia-1981': '1981-04-12',
    'mir-1986': '1986-02-19',
    'galileo-1989': '1989-10-18',
    'magellan-1989': '1989-05-04',
    'hubble-space-telescope-1990': '1990-04-24',
    'cassini-huygens-1997': '1997-10-15',
    'mars-pathfinder-sojourner-1997': '1996-12-04',
    'soho-1996': '1995-12-02',
    'chandra-x-ray-observatory-1999': '1999-07-23',
    'zarya-international-space-station-assembly-begins-1998': '1998-11-20',
    'spirit-opportunity-2004': '2003-07-07',
    'rosetta-2004': '2004-03-02',
    'rosetta-philae-2014': '2004-03-02',
    'hayabusa-2003': '2003-05-09',
    'curiosity-msl-2012': '2011-11-26',
    'juno-2011': '2011-08-05',
    'new-horizons-2015': '2006-01-19',
    'mars-orbiter-mission-mangalyaan-2013': '2013-11-05',
    'chang-e-3-yutu-2013': '2013-12-01',
    'chandrayaan-1-2008': '2008-10-22',
    'kepler-2009': '2009-03-07',
    'perseverance-ingenuity-2020': '2020-07-30',
    'james-webb-space-telescope-2021': '2021-12-25',
    'artemis-i-2022': '2022-11-16',
    'dart-2022': '2022-11-24',
    'chandrayaan-3-2023': '2023-07-14',
    'luna-25-2023': '2023-08-10',
    'europa-clipper-2024': '2024-10-14',
    'im-1-odysseus-2024': '2024-02-15',
}

out_path = ROOT / 'src' / '_data' / 'launch-dates.json'
out_path.write_text(json.dumps(LAUNCH_DATES, indent=2) + '\n')
print(f'wrote {len(LAUNCH_DATES)} known launch dates')
