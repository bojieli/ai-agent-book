#!/usr/bin/env python3
"""Turn a Chinese revised figure into a translated, live-text figure.

Chinese 3.0 figures under ``book/images/revised`` draw their labels as outlined
Source Han Sans CN glyph paths inside ``<g aria-label="…">`` groups. That is
right for Chinese, but a translation cannot edit outlines, and outlining a
Latin/Cyrillic/Arabic/Tamil string would need a font per script and a shaper
for right-to-left text.

This tool recovers the labels from those groups and rebuilds the same figure
with ordinary ``<text>`` nodes: identical geometry, translated strings, and a
font stack the reader or the PDF renderer resolves. Arabic, Hebrew and Tamil
text is shaped by the renderer, so no manual shaping is involved.

Workflow, per figure::

    python3 scripts/i18n/svg_text.py extract book/images/revised/fig1-1.svg \\
        > /tmp/fig1-1.json                     # labels + width budget
    # …translate the "text" fields, keep "id"…
    python3 scripts/i18n/svg_text.py build book/images/revised/fig1-1.svg \\
        /tmp/fig1-1.json book-ja/images/revised/fig1-1.svg --lang ja
    python3 scripts/i18n/svg_text.py render book-ja/images/revised/fig1-1.svg \\
        /tmp/fig1-1.png                        # look at it, then iterate

``build`` shrinks a tight label to fit its box and warns when the translation
looks too long for it. ``check`` is the authority: it renders the figure in a
real browser, measures the glyphs, and reports any text that leaves the canvas,
spills out of its panel, or collides with another label. Fix what it reports.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = 'http://www.w3.org/2000/svg'
NS = f'{{{SVG_NS}}}'

# Font stacks per script. Each lists the fonts the CI PDF build installs (see
# .github/workflows/build-latest.yml), then common macOS fonts, then a generic
# family so a browser or a minimal TeX box still renders something.
FONT_STACKS = {
    'cjk-sc': '"Noto Sans CJK SC", "Source Han Sans CN", "PingFang SC", "Microsoft YaHei", sans-serif',
    'cjk-tc': '"Noto Sans CJK TC", "Source Han Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif',
    'cjk-jp': '"Noto Sans CJK JP", "Source Han Sans JP", "Hiragino Sans", "Yu Gothic", sans-serif',
    'cjk-kr': '"Noto Sans CJK KR", "Source Han Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
    'latin': '"DejaVu Sans", Arial, "Helvetica Neue", sans-serif',
    'arabic': '"Noto Naskh Arabic", "Noto Sans Arabic", Amiri, "Geeza Pro", sans-serif',
    'hebrew': '"Noto Sans Hebrew", "Noto Serif Hebrew", "Arial Hebrew", sans-serif',
    'tamil': '"Noto Sans Tamil", "Noto Serif Tamil", "Tamil Sangam MN", sans-serif',
}

# language → (font stack, text direction)
LANGUAGES = {
    'zh-CN': ('cjk-sc', 'ltr'),
    'zh-TW': ('cjk-tc', 'ltr'),
    'ja': ('cjk-jp', 'ltr'),
    'ko': ('cjk-kr', 'ltr'),
    'en': ('latin', 'ltr'),
    'es': ('latin', 'ltr'),
    'id': ('latin', 'ltr'),
    'vi': ('latin', 'ltr'),
    'tr': ('latin', 'ltr'),
    'hu': ('latin', 'ltr'),
    'pt-BR': ('latin', 'ltr'),
    'ru': ('latin', 'ltr'),
    'mn': ('latin', 'ltr'),
    'ar': ('arabic', 'rtl'),
    'he': ('hebrew', 'rtl'),
    'ta': ('tamil', 'ltr'),
}

# Average advance width as a fraction of font size, used only to estimate how
# wide a translated label will be. Deliberately generous: the point is to catch
# overflow before it reaches a reader, so over-estimating is the safe error.
ADVANCE = {
    'latin': 0.56,
    'cjk': 1.0,
    'arabic': 0.52,
    'hebrew': 0.52,
    'tamil': 0.62,
}

MIN_SCALE = 0.78  # never shrink a label below this fraction of its 3.0 size


def script_family(stack: str) -> str:
    if stack.startswith('cjk'):
        return 'cjk'
    return stack.split('-')[0] if stack in ADVANCE else 'latin'


def estimate_width(text: str, size: float, family: str) -> float:
    """Rough rendered width of one line, in SVG user units.

    Measured per character, because every language's figure labels mix scripts:
    Latin terms such as ``Model`` or ``Harness`` keep Latin widths even inside a
    Japanese label, and a CJK term inside an English label stays full width.
    """
    latin = ADVANCE['latin']
    total = 0.0
    for char in text:
        if char.isspace():
            total += latin * 0.55 * size
        elif char in '·:：、，,./()（）·—–-–':
            total += 0.4 * size
        elif ord(char) >= 0x2E80:
            total += size
        elif 0x0590 <= ord(char) <= 0x08FF:
            total += ADVANCE['arabic'] * size
        elif 0x0B80 <= ord(char) <= 0x0BFF:
            total += ADVANCE['tamil'] * size
        else:
            total += latin * size
    return total


def outer_texts(root: ET.Element) -> list[ET.Element]:
    return [el for el in root.iter(f'{NS}text') if el.text and el.text.strip()]


def panel_budget(rects: list[ET.Element], x: float, y: float) -> float | None:
    """Widest run that keeps a label inside its own panel, as typography.py does."""
    panels = []
    for rect in rects:
        rx, ry, rw, rh = (float(rect.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
        if rx + 2 < x < rx + rw - 2 and ry + 8 < y < ry + rh:
            panels.append((rw * rh, rx, rw))
    if not panels:
        return None
    _, rx, rw = min(panels)
    return 2 * min(x - rx - 10, rx + rw - x - 10)


def extract(source: Path) -> dict:
    root = ET.parse(source).getroot()
    rects = [el for el in root.iter(f'{NS}rect') if 'x' in el.attrib and el.get('width')]
    width = 900.0
    height = float(root.get('viewBox', '0 0 900 0').split()[3] or 0)
    fig_width = float(root.get('viewBox', '0 0 900 0').split()[2] or width)
    width = fig_width

    labels = []
    for order, group in enumerate([el for el in root.iter(f'{NS}g') if el.get('aria-label')]):
        uses = [
            (float(match[1]), float(match[2]))
            for use in group.iter(f'{NS}use')
            if (match := re.search(r'translate\(([-\d.]+) ([-\d.]+)\)', use.get('transform', '')))
        ]
        if not uses:
            continue
        size = float(group.get('data-size', 26))
        left = min(x for x, _ in uses)
        right = max(x for x, _ in uses)
        # The group is centred on its anchor and the last glyph occupies about
        # one advance past its own translate() origin.
        if group.get('fill'):
            fill = group.get('fill')
        else:
            fill = '#292929'
        weight = 700 if '700' in (group.get('data-font') or '') else 400
        y = uses[0][1]
        centre = (left + right) / 2
        budget = panel_budget(rects, centre, y)
        if budget is None:
            budget = 2 * min(centre - 10, width - 10 - centre)
        labels.append({
            'id': f'L{order}',
            'text': group.get('aria-label', ''),
            'x': round(centre, 2),
            'y': round(y, 2),
            'size': size,
            'weight': weight,
            'fill': fill,
            'budget': round(budget, 1),
            'original_width': round(right - left + size, 1),
        })

    meta = {}
    for tag in ('title', 'desc'):
        node = root.find(f'{NS}{tag}')
        if node is not None and node.text:
            meta[tag] = node.text
    return {
        'source': str(source),
        'viewBox': root.get('viewBox', ''),
        'title': meta.get('title', ''),
        'desc': meta.get('desc', ''),
        'labels': labels,
    }


def build(source: Path, translations: dict, out: Path, lang: str) -> None:
    if lang not in LANGUAGES:
        raise SystemExit(f'unknown language {lang!r}; known: {", ".join(sorted(LANGUAGES))}')
    stack_name, direction = LANGUAGES[lang]
    stack = FONT_STACKS[stack_name]
    family = script_family(stack_name)

    wanted = {label['id']: label for label in translations['labels']}
    parsed = ET.parse(source)
    root = parsed.getroot()

    # Replace the outlined groups with live text, keeping document order so the
    # figure paints the same way.
    groups = [el for el in root.iter(f'{NS}g') if el.get('aria-label')]
    surviving: list[tuple[ET.Element, list[ET.Element]]] = []
    parents = {child: parent for parent in root.iter() for child in parent}
    for order, group in enumerate(groups):
        label_id = f'L{order}'
        entry = wanted.get(label_id)
        if entry is None:
            raise SystemExit(f'{source.name}: translation JSON is missing {label_id}')
        text = (entry.get('text') or '').strip()
        if not text:
            raise SystemExit(f'{source.name}: {label_id} has an empty translation')
        size = float(entry.get('size', 26))
        budget = float(entry.get('budget', 400))
        weight = int(entry.get('weight', 400))
        lines = text.split('\n')

        width = max(estimate_width(line, size, family) for line in lines)
        scale = 1.0
        if width > budget:
            scale = budget / width
        if scale < MIN_SCALE:
            # The estimate is deliberately generous, so this is advice, not a
            # verdict: keep the label legible and let ``check`` — which measures
            # real rendered glyphs — decide whether it actually overflows.
            print(
                f'{source.name}: warning: {label_id} is tight: "{text}" needs '
                f'about {width:.0f}px at font-size {size:.0f}, box allows '
                f'{budget:.0f}px. Consider shortening it, then run check.',
                file=sys.stderr,
            )
        final_size = max(size * scale, size * MIN_SCALE)

        replacement = []
        for index, line in enumerate(lines):
            node = ET.Element(f'{NS}text')
            node.set('x', f'{float(entry["x"]):g}')
            node.set('y', f'{float(entry["y"]) + index * final_size * 1.22:g}')
            node.set('text-anchor', 'middle')
            node.set('font-family', stack)
            node.set('font-size', f'{final_size:.1f}')
            node.set('font-weight', str(weight))
            node.set('fill', entry.get('fill', '#292929'))
            if direction == 'rtl':
                node.set('direction', 'rtl')
            node.text = line
            replacement.append(node)
        surviving.append((group, replacement))

    for group, replacement in surviving:
        parent = parents[group]
        index = list(parent).index(group)
        parent.remove(group)
        for offset, node in enumerate(replacement):
            parent.insert(index + offset, node)

    # Drop the now-unused outlined glyph definitions, and keep the file honest
    # about its own metrics: width follows the viewBox, as in the 3.0 source.
    for defs in root.iter(f'{NS}defs'):
        for path in [el for el in defs if el.get('id', '').startswith('g') and re.fullmatch(r'g\d00-[0-9a-f]+', el.get('id', ''))]:
            defs.remove(path)

    title = root.find(f'{NS}title')
    if title is not None and translations.get('title'):
        title.text = translations['title']
    desc = root.find(f'{NS}desc')
    if desc is not None and translations.get('desc'):
        desc.text = translations['desc']

    _, _, vb_w, vb_h = root.get('viewBox', '0 0 900 0').split()
    root.set('width', f'{float(vb_w) * 106 / 900:.3f}mm')
    root.set('height', f'{float(vb_h) * 106 / 900:.3f}mm')

    out.parent.mkdir(parents=True, exist_ok=True)
    body = ET.tostring(root, encoding='unicode')
    out.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + body + '\n', encoding='utf-8')


def chromium() -> str | None:
    """Locate a headless Chromium for rasterising figures."""
    candidates = sorted(
        (Path.home() / 'Library/Caches/ms-playwright').glob(
            'chromium_headless_shell-*/chrome-headless-shell-mac-*/chrome-headless-shell'
        )
    ) + sorted(
        (Path.home() / 'Library/Caches/ms-playwright').glob(
            'chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium'
        )
    )
    for path in candidates:
        if path.exists():
            return str(path)
    for name in ('chromium', 'google-chrome', 'chrome-headed-shell', 'chrome'):
        found = shutil.which(name)
        if found:
            return found
    return None


def render(svg: Path, png: Path, scale: float = 1.0) -> None:
    view_box = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg.read_text(encoding='utf-8'))
    if not view_box:
        raise SystemExit(f'{svg}: no viewBox to size the render from')
    width = math.ceil(float(view_box[1]) * scale)
    height = math.ceil(float(view_box[2]) * scale)
    binary = chromium()
    if not binary:
        raise SystemExit('no headless Chromium found; install Playwright browsers or Chrome')
    png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as workspace:
        # A wrapper page gives a white background and no browser chrome margins.
        page = Path(workspace) / 'page.html'
        page.write_text(
            '<!doctype html><meta charset="utf-8">'
            '<style>html,body{margin:0;padding:0;background:#fff}'
            f'img{{display:block;width:{width}px;height:{height}px}}</style>'
            f'<img src="file://{svg.resolve()}">',
            encoding='utf-8',
        )
        subprocess.run(
            [
                binary, '--headless', '--disable-gpu', '--no-sandbox',
                '--hide-scrollbars', '--force-device-scale-factor=1',
                f'--window-size={width},{height}',
                f'--screenshot={png.resolve()}', f'file://{page}',
            ],
            check=True,
            capture_output=True,
        )
    if not png.exists():
        raise SystemExit(f'{svg}: rendering produced no PNG')


def text_boxes(svg: Path, lang: str) -> tuple[list[dict], float, float]:
    """Estimate every label's rendered box, and the figure's canvas size."""
    stack_name, _ = LANGUAGES.get(lang, ('latin', 'ltr'))
    family = script_family(stack_name)
    root = ET.parse(svg).getroot()
    _, _, view_w, view_h = root.get('viewBox', '0 0 0 0').split()
    boxes = []
    for node in root.iter(f'{NS}text'):
        text = (node.text or '').strip()
        if not text:
            continue
        size = float(node.get('font-size', 26))
        x = float(node.get('x', 0))
        y = float(node.get('y', 0))
        width = estimate_width(text, size, family)
        anchor = node.get('text-anchor', 'start')
        left = x if anchor == 'start' else x - width / 2 if anchor == 'middle' else x - width
        boxes.append({
            'text': text,
            'x': left,
            'y': y - size * 0.8,
            'width': width,
            'height': size * 1.0,
        })
    return boxes, float(view_w), float(view_h)


def check(svgs: list[Path], lang: str) -> int:
    """Report labels that leave the canvas, spill out of their panel, or collide.

    Widths are estimated rather than measured, so treat a hit as "look at this
    figure" — confirm with ``render`` before rewriting anything.
    """
    failures = 0
    for svg in svgs:
        root = ET.parse(svg).getroot()
        rects = []
        for rect in root.iter(f'{NS}rect'):
            if 'x' not in rect.attrib or not rect.get('width'):
                continue
            x, y = float(rect.get('x', 0)), float(rect.get('y', 0))
            w, h = float(rect.get('width', 0)), float(rect.get('height', 0))
            if x <= 0 and y <= 0 and w >= 890:  # the canvas background
                continue
            rects.append({'x': x, 'y': y, 'width': w, 'height': h})
        boxes, view_w, view_h = text_boxes(svg, lang)
        problems = []
        for box in boxes:
            if box['x'] < -1 or box['y'] < -1 or box['x'] + box['width'] > view_w + 1 or box['y'] + box['height'] > view_h + 1:
                problems.append(f'canvas: "{box["text"]}"')
                continue
            cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
            owners = sorted(
                (rect for rect in rects
                 if rect['x'] < cx < rect['x'] + rect['width'] and rect['y'] < cy < rect['y'] + rect['height']),
                key=lambda rect: rect['width'] * rect['height'],
            )
            if not owners:
                continue
            rect = owners[0]
            over = max(
                rect['x'] - box['x'],
                box['x'] + box['width'] - (rect['x'] + rect['width']),
                rect['y'] - box['y'],
                box['y'] + box['height'] - (rect['y'] + rect['height']),
            )
            if over > 4:
                problems.append(f'box +{over:.0f}px: "{box["text"]}"')
        for index, first in enumerate(boxes):
            for second in boxes[index + 1:]:
                overlap_w = min(first['x'] + first['width'], second['x'] + second['width']) - max(first['x'], second['x'])
                overlap_h = min(first['y'] + first['height'], second['y'] + second['height']) - max(first['y'], second['y'])
                if overlap_w > 6 and overlap_h > 4:
                    problems.append(f'overlap: "{first["text"]}" ↔ "{second["text"]}"')
        if problems:
            failures += 1
            for problem in problems:
                print(f'{svg}: {problem}')
    print(f'{len(svgs) - failures}/{len(svgs)} figure(s) clean')
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    extract_cmd = sub.add_parser('extract', help='dump a figure\'s labels and width budgets as JSON')
    extract_cmd.add_argument('svg', type=Path)

    build_cmd = sub.add_parser('build', help='write the translated figure')
    build_cmd.add_argument('svg', type=Path)
    build_cmd.add_argument('translations', type=Path)
    build_cmd.add_argument('out', type=Path)
    build_cmd.add_argument('--lang', required=True)

    render_cmd = sub.add_parser('render', help='rasterise a figure for visual inspection')
    render_cmd.add_argument('svg', type=Path)
    render_cmd.add_argument('png', type=Path)
    render_cmd.add_argument('--scale', type=float, default=1.0)

    check_cmd = sub.add_parser('check', help='measure rendered text for overflow and overlap')
    check_cmd.add_argument('svgs', type=Path, nargs='+')
    check_cmd.add_argument('--lang', default='en')

    args = parser.parse_args(argv)
    if args.command == 'check':
        return check(args.svgs, args.lang)
    if args.command == 'extract':
        json.dump(extract(args.svg), sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
    elif args.command == 'build':
        build(args.svg, json.loads(args.translations.read_text(encoding='utf-8')), args.out, args.lang)
    else:
        render(args.svg, args.png, args.scale)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
