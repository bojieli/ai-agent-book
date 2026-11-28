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
import html as html_lib
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
# Write the SVG namespace as the default one: `ns0:text` is valid XML but is not
# an SVG <text> to anything that parses the file as HTML, which matters when a
# reader or a measuring browser inlines the figure.
ET.register_namespace('', SVG_NS)
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


def measure_exactly(text: str, size: float, weight: int) -> float | None:
    """Width of a label in the Chinese source font, when that font is available.

    The 3.0 figures were typeset with Source Han Sans CN, so measuring the same
    string with the same font and the same code reproduces the original anchor
    exactly. Without fontTools installed this returns None and the caller falls
    back to a character-class estimate.
    """
    try:
        cache = measure_exactly.cache
    except AttributeError:
        cache = measure_exactly.cache = {}
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'book_figures'))
            from typography import measure as font_measure  # noqa: PLC0415

            cache['measure'] = font_measure
        except Exception:  # fontTools or the fonts are missing
            cache['measure'] = None
    font_measure = cache.get('measure')
    if font_measure is None:
        return None
    try:
        return font_measure(text, size, weight)
    except Exception:
        return None


def estimate_label_width(text: str, size: float, weight: int) -> float:
    measured = measure_exactly(text, size, weight)
    if measured is not None:
        return measured
    total = 0.0
    for char in text:
        if char == ' ':
            total += 0.5 * size
        elif ord(char) >= 0x2E80:
            total += size
        else:
            total += 0.6 * size
    return total


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
        # The anchor is the left origin plus half the whole label's width. The
        # steps between translate() origins are the *earlier* glyph's advances,
        # so they locate the left edge but never the right one: averaging the
        # origins lands about half a glyph left of centre. Measure the string.
        label = group.get('aria-label', '')
        fill = group.get('fill') or '#292929'
        weight = 700 if '700' in (group.get('data-font') or '') else 400
        label_width = estimate_label_width(label, size, weight)
        y = uses[0][1]
        centre = left + label_width / 2
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
            'original_width': round(label_width, 1),
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


def legacy_anchors(source: Path) -> dict[str, float]:
    """The anchors `extract` produced before it measured label widths.

    Averaging glyph origins put every label about half a glyph left of centre.
    Recognising that exact value lets `recentre` correct the labels nobody has
    touched while leaving a hand-adjusted one where its author put it.
    """
    root = ET.parse(source).getroot()
    anchors = {}
    for order, group in enumerate(el for el in root.iter(f'{NS}g') if el.get('aria-label')):
        origins = [
            float(match[1])
            for use in group.iter(f'{NS}use')
            if (match := re.search(r'translate\(([-\d.]+) ', use.get('transform', '')))
        ]
        if origins:
            anchors[f'L{order}'] = (min(origins) + max(origins)) / 2
    return anchors


def recentre(source: Path, built: Path, out: Path) -> tuple[int, int]:
    """Move unmodified labels in an already-built figure onto their true anchors."""
    labels = extract(source)['labels']
    legacy = legacy_anchors(source)
    root = ET.parse(built).getroot()

    # Match each text node to the Chinese label it came from: same legacy
    # anchor, and a baseline at or a few lines below that label's. Translators
    # sometimes merge or split labels, so nodes are matched one by one.
    moved = kept = 0
    for node in root.iter(f'{NS}text'):
        if not (node.text or '').strip():
            continue
        x = float(node.get('x', 0))
        y = float(node.get('y', 0))
        candidates = [
            label for label in labels
            if abs(legacy.get(label['id'], -1e9) - x) < 0.5
            and label['y'] - 2 <= y <= label['y'] + 4 * label['size']
        ]
        targets = {round(label['x'], 2) for label in candidates}
        if len(targets) == 1:
            node.set('x', f'{targets.pop():g}')
            moved += 1
        else:
            kept += 1

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ET.tostring(root, encoding='unicode') + '\n',
        encoding='utf-8',
    )
    return moved, kept


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


def estimated_problems(svg: Path, lang: str) -> list[dict]:
    """Fallback when no browser is available: widths from the advance table."""
    stack_name, _ = LANGUAGES.get(lang, ('latin', 'ltr'))
    family = script_family(stack_name)
    root = ET.parse(svg).getroot()
    _, _, view_w, view_h = (float(v) for v in root.get('viewBox', '0 0 0 0').split())
    rects = []
    for rect in root.iter(f'{NS}rect'):
        if 'x' not in rect.attrib or not rect.get('width'):
            continue
        x, y = float(rect.get('x', 0)), float(rect.get('y', 0))
        w, h = float(rect.get('width', 0)), float(rect.get('height', 0))
        if x <= 0 and y <= 0 and w >= view_w - 1:  # the canvas background
            continue
        rects.append((x, y, w, h))
    boxes = []
    for node in root.iter(f'{NS}text'):
        text = (node.text or '').strip()
        if not text:
            continue
        size = float(node.get('font-size', 26))
        x, y = float(node.get('x', 0)), float(node.get('y', 0))
        width = estimate_width(text, size, family)
        anchor = node.get('text-anchor', 'start')
        left = x if anchor == 'start' else x - width / 2 if anchor == 'middle' else x - width
        boxes.append((text, left, y - size * 0.8, width, size))

    problems = []
    for text, x, y, w, h in boxes:
        if x < -1 or y < -1 or x + w > view_w + 1 or y + h > view_h + 1:
            problems.append({'kind': 'canvas', 'text': text})
            continue
        for rx, ry, rw, rh in rects:
            if min(x + w, rx + rw) - max(x, rx) <= 1 or min(y + h, ry + rh) - max(y, ry) <= 1:
                continue
            over = max(rx - x, x + w - (rx + rw), ry - y, y + h - (ry + rh))
            if over > 4:
                problems.append({'kind': 'border', 'over': round(over), 'text': text})
                break
    for index, (text, x, y, w, h) in enumerate(boxes):
        for other, ox, oy, ow, oh in boxes[index + 1:]:
            same_baseline = abs((y + h) - (oy + oh)) < min(h, oh) * 0.35
            if min(x + w, ox + ow) - max(x, ox) > 6 and min(y + h, oy + oh) - max(y, oy) > min(h, oh) * 0.45 and same_baseline:
                problems.append({'kind': 'overlap', 'text': text, 'other': other})
    return problems


MEASURE_JS = r"""
const svg = document.querySelector('svg');
if (!svg) { document.body.setAttribute('data-result', 'NOSVG'); }
else {
const vb = svg.viewBox.baseVal;
const rects = [...svg.querySelectorAll('rect')]
  .filter(r => r.getAttribute('x') !== null && r.getAttribute('width') !== null)
  .map(r => r.getBBox())
  .filter(b => !(b.x <= 0 && b.y <= 0 && b.width >= vb.width - 1));
const texts = [...svg.querySelectorAll('text')]
  .filter(t => t.textContent.trim()).map(t => ({t: t.textContent.trim(), b: t.getBBox()}));
const problems = [];
for (const {t, b} of texts) {
  if (b.x < -0.5 || b.y < -0.5 || b.x + b.width > vb.width + 0.5 || b.y + b.height > vb.height + 0.5)
    problems.push({kind: 'canvas', text: t});
  // A label must sit wholly inside or wholly outside every panel; partly
  // inside means it crosses that panel's border.
  for (const r of rects) {
    const ix = Math.min(b.x + b.width, r.x + r.width) - Math.max(b.x, r.x);
    const iy = Math.min(b.y + b.height, r.y + r.height) - Math.max(b.y, r.y);
    if (ix <= 1 || iy <= 1) continue;
    const over = Math.max(r.x - b.x, b.x + b.width - (r.x + r.width),
                          r.y - b.y, b.y + b.height - (r.y + r.height));
    if (over > 6) { problems.push({kind: 'border', over: Math.round(over), text: t}); break; }
  }
}
for (let i = 0; i < texts.length; i++)
  for (let j = i + 1; j < texts.length; j++) {
    const a = texts[i].b, c = texts[j].b;
    const w = Math.min(a.x + a.width, c.x + c.width) - Math.max(a.x, c.x);
    const h = Math.min(a.y + a.height, c.y + c.height) - Math.max(a.y, c.y);
    // Font boxes carry ascent and descent padding, so two labels a line apart
    // overlap in bounding-box terms while their glyphs do not. Only flag a
    // collision that eats into both boxes by a visible margin.
    const sameBaseline = Math.abs((a.y + a.height) - (c.y + c.height)) < Math.min(a.height, c.height) * 0.35;
    if (w > 2 && h > Math.min(a.height, c.height) * 0.45 && sameBaseline)
      problems.push({kind: 'overlap', text: texts[i].t, other: texts[j].t});
  }
document.body.setAttribute('data-result', JSON.stringify(problems));
}
"""


def measured_problems(svg: Path, binary: str) -> list[dict] | None:
    """Real glyph boxes from a browser; None when it cannot be measured."""
    markup = re.sub(r'^<\?xml[^>]*>\s*', '', svg.read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory() as workspace:
        page = Path(workspace) / 'measure.html'
        page.write_text(
            '<!doctype html><meta charset="utf-8"><body>' + markup
            + '<script>' + MEASURE_JS + '</script></body>',
            encoding='utf-8',
        )
        try:
            result = subprocess.run(
                [binary, '--headless', '--disable-gpu', '--no-sandbox',
                 '--virtual-time-budget=3000', '--dump-dom', f'file://{page}'],
                check=True, capture_output=True, text=True, timeout=120,
            )
        except (subprocess.SubprocessError, OSError):
            return None
    match = re.search(r'data-result="([^"]*)"', result.stdout)
    if not match:
        return None
    value = html_lib.unescape(match.group(1))
    if value == 'NOSVG':
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def check(svgs: list[Path], lang: str) -> int:
    """Report labels that leave the canvas, spill out of their panel, or collide.

    Geometry comes from a headless browser laying out the real glyphs, in the
    fonts this machine has. Without a browser it falls back to an estimate,
    which is coarser: confirm anything it reports with ``render``.
    """
    binary = chromium()
    failures = 0
    for svg in svgs:
        problems = measured_problems(svg, binary) if binary else None
        if problems is None:
            problems = estimated_problems(svg, lang)
        if problems:
            failures += 1
            for problem in problems:
                detail = f' +{problem["over"]}px' if 'over' in problem else ''
                other = f' with "{problem["other"]}"' if 'other' in problem else ''
                print(f'{svg}: {problem["kind"]}{detail}: "{problem["text"]}"{other}')
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

    recentre_cmd = sub.add_parser('recentre', help='fix label anchors in an already-built figure')
    recentre_cmd.add_argument('svg', type=Path, help='Chinese source figure')
    recentre_cmd.add_argument('built', type=Path, help='translated figure to correct in place')
    recentre_cmd.add_argument('--out', type=Path)

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
    if args.command == 'recentre':
        moved, kept = recentre(args.svg, args.built, args.out or args.built)
        print(f'{args.built.name}: {moved} label(s) recentred, {kept} left as adjusted')
        return 0
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
