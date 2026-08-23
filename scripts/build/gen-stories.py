#!/usr/bin/env python3
"""Compile content/missions/*.md into src/_data/stories.json.

One Markdown file per mission's long-form story. File name = mission id
(e.g. sputnik-1-1957.md). Sections are marked with simple headings:

    ## Why it happened
    ...paragraphs...

    ## The mission
    ...

    ## Results
    ...

Only missions with a file here get the full three-section treatment on
their page; everything else falls back to dataset text with an explicit
"write-up pending" note (never fabricated copy).
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / 'content' / 'missions'
OUT = ROOT / 'src' / '_data' / 'stories.json'


def md_paragraphs(text: str) -> str:
    """Minimal markdown: blank-line-separated paragraphs -> <p>."""
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return '\n'.join(f'<p>{p}</p>' for p in paragraphs)


def parse_story(path: Path) -> dict:
    sections = {}
    current = None
    buffer: list[str] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        heading = re.match(r'^##\s+(.+)$', line.strip())
        if heading:
            if current:
                sections[current] = md_paragraphs('\n'.join(buffer))
            current = heading.group(1).strip().lower()
            if current not in ('why it happened', 'the mission', 'results'):
                current = None  # ignore unknown sections rather than guess
            buffer = []
        elif current:
            buffer.append(line)
    if current:
        sections[current] = md_paragraphs('\n'.join(buffer))
    return sections


def main() -> None:
    stories: dict[str, dict] = {}
    if CONTENT.exists():
        for md_file in sorted(CONTENT.glob('*.md')):
            sections = parse_story(md_file)
            if sections:
                stories[md_file.stem] = {
                    'why': sections.get('why it happened', ''),
                    'story': sections.get('the mission', ''),
                    'results': sections.get('results', ''),
                }
    OUT.write_text(json.dumps(stories, ensure_ascii=False, indent=2) + '\n')
    print(f'wrote {len(stories)} mission stories')


if __name__ == '__main__':
    main()
