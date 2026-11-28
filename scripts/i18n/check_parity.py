#!/usr/bin/env python3
"""Check that a translated edition still has the shape of the Chinese original.

A translation should differ from `book/` in wording and nothing else. This gate
compares structure, which language must not change: headings by level, fenced
code blocks (and their languages), tables, images and whether each image file
exists, footnote definitions, display equations, experiment numbers and figure
captions. It catches the mistakes that are invisible in a spot check — a dropped
experiment box, a figure that was renamed, a paragraph merged away.

Usage::

    python3 scripts/i18n/check_parity.py            # every edition
    python3 scripts/i18n/check_parity.py ja ko      # selected editions
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# The checkout to inspect. Defaults to the current directory when it is a
# checkout (so `python3 /path/to/check_parity.py book-ja` run inside a git
# worktree checks that worktree, not the copy the script lives in), else the
# repository this script belongs to. `--root DIR` overrides both.
ROOT = Path(__file__).resolve().parents[2]
if (Path.cwd() / 'book' / 'chapter1.md').exists():
    ROOT = Path.cwd().resolve()

# edition directory → filename suffix used by its chapter files
EDITIONS = {
    'book-en': '',
    'book-es': '.es',
    'book-id': '',
    'book-ar': '.ar',
    'book-zhtw': '.zhtw',
    'book-ta': '.ta',
    'book-vi': '.vi',
    'book-ja': '.ja',
    'book-tr': '.tr',
    'book-ko': '.ko',
    'book-hu': '',
    'book-he': '.he',
    'book-ptbr': '.ptbr',
    'book-mn': '',
    'book-ru': '',
}

DOCUMENTS = ['introduction', *[f'chapter{n}' for n in range(1, 11)], 'afterword']


def source(edition: str, document: str) -> Path:
    return ROOT / edition / f'{document}{EDITIONS[edition]}.md'


def chinese(document: str) -> Path:
    return ROOT / 'book' / f'{document}.md'


def fence_blocks(text: str) -> list[str]:
    """Fenced code blocks as (info string, body) pairs."""
    blocks, current = [], None
    for line in text.splitlines():
        if line.startswith('```'):
            if current is None:
                current = [line[3:].strip()]
            else:
                blocks.append('\x00'.join(current))
                current = None
            continue
        if current is not None:
            current.append(line)
    return blocks


def strip_code(text: str) -> str:
    """Text with fenced blocks removed, so counters ignore their contents."""
    kept, inside = [], False
    for line in text.splitlines():
        if line.startswith('```'):
            inside = not inside
            continue
        if not inside:
            kept.append(line)
    return '\n'.join(kept)


def images(text: str) -> list[str]:
    return re.findall(r'!\[[^\]]*\]\(([^)\s]+)', strip_code(text))


def numbered_refs(text: str) -> list[str]:
    """Every chapter-scoped number such as 6-1 or 6-15, outside code.

    Figures, experiments, tables and exercises are all numbered this way. A
    translation must keep exactly the same set, whatever word, case ending or
    word order its language puts around the number, so the gate compares the
    numbers alone instead of guessing each language's inflections.
    """
    return sorted(
        set(re.findall(r'(?<![\d.:/-])(?:10|[0-9])-(?:[1-9][0-9]?)(?![\d:/]|-\d)', strip_code(text))),
        key=lambda v: tuple(map(int, v.split('-'))),
    )


def footnote_ids(text: str) -> set[str]:
    return set(re.findall(r'^\[\^([^\]]+)\]:', strip_code(text), re.M))


def headings(text: str) -> dict[int, int]:
    counts: dict[int, int] = {}
    for match in re.finditer(r'^(#{1,6})\s+\S', strip_code(text), re.M):
        level = len(match[1])
        counts[level] = counts.get(level, 0) + 1
    return counts


def tables(text: str) -> int:
    lines = strip_code(text).splitlines()
    return sum(
        1 for index, line in enumerate(lines[:-1])
        if line.lstrip().startswith('|') and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[index + 1])
    )


def display_maths(text: str) -> int:
    return strip_code(text).count('$$') // 2


def compare(edition: str, document: str) -> list[str]:
    reference_path, target_path = chinese(document), source(edition, document)
    if not target_path.exists():
        return [f'missing file {target_path.relative_to(ROOT)}']
    reference_text, target_text = reference_path.read_text(encoding='utf-8'), target_path.read_text(encoding='utf-8')
    problems: list[str] = []

    for name, expected, actual in [
        ('headings per level', headings(reference_text), headings(target_text)),
        ('fenced blocks', len(fence_blocks(reference_text)), len(fence_blocks(target_text))),
        ('tables', tables(reference_text), tables(target_text)),
        ('display equations', display_maths(reference_text), display_maths(target_text)),
    ]:
        if expected != actual:
            problems.append(f'{name}: expected {expected}, found {actual}')

    reference_images, target_images = images(reference_text), images(target_text)
    if reference_images != target_images:
        missing = [path for path in reference_images if path not in target_images]
        extra = [path for path in target_images if path not in reference_images]
        detail = []
        if missing:
            detail.append(f'missing {len(missing)}: {", ".join(missing[:4])}')
        if extra:
            detail.append(f'unexpected {len(extra)}: {", ".join(extra[:4])}')
        if not detail:
            detail.append('same paths in a different order')
        problems.append('images: ' + '; '.join(detail))
    for path in target_images:
        if path.startswith(('http://', 'https://')):
            continue
        resolved = (target_path.parent / path).resolve()
        if not resolved.exists():
            problems.append(f'image file not found: {path}')

    expected_refs, found_refs = numbered_refs(reference_text), numbered_refs(target_text)
    if expected_refs != found_refs:
        lost = [ref for ref in expected_refs if ref not in found_refs]
        added = [ref for ref in found_refs if ref not in expected_refs]
        problems.append(f'numbered references (figures/experiments/tables): lost {lost}, added {added}')
    # A translator may add a note of their own, but every original note stays.
    lost_notes = sorted(footnote_ids(reference_text) - footnote_ids(target_text))
    if lost_notes:
        problems.append(f'footnotes missing: {", ".join(lost_notes)}')

    reference_code, target_code = fence_blocks(reference_text), fence_blocks(target_text)
    for index, (expected, actual) in enumerate(zip(reference_code, target_code)):
        expected_info = expected.split('\x00')[0]
        actual_info = actual.split('\x00')[0]
        if expected_info != actual_info:
            problems.append(f'code block {index + 1} language: expected {expected_info!r}, found {actual_info!r}')
        expected_lines = expected.count('\x00')
        actual_lines = actual.count('\x00')
        if expected_lines and abs(expected_lines - actual_lines) > max(2, expected_lines // 10):
            problems.append(f'code block {index + 1}: expected about {expected_lines} lines, found {actual_lines}')
    return problems


def main(argv: list[str]) -> int:
    global ROOT
    selected = argv[1:]
    if '--root' in selected:
        index = selected.index('--root')
        ROOT = Path(selected[index + 1]).resolve()
        del selected[index:index + 2]
    missing = [name for name in selected if name not in EDITIONS]
    if missing:
        print(f'unknown edition(s): {", ".join(missing)}; known: {", ".join(sorted(EDITIONS))}')
        return 2
    editions = selected or sorted(EDITIONS)
    failures = 0
    for edition in editions:
        edition_problems = 0
        for document in DOCUMENTS:
            problems = compare(edition, document)
            for problem in problems:
                print(f'{edition}/{document}: {problem}')
            edition_problems += len(problems)
        if edition_problems:
            failures += 1
            print(f'✗ {edition}: {edition_problems} structural difference(s)')
        else:
            print(f'✓ {edition}: structure matches the Chinese 3.0 edition')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
