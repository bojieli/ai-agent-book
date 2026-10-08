"""Book-size figure typography with pinned Source Han Sans outlines.

Input coordinates remain editable in chapter scripts. Text is wrapped within its
existing panel; added lines insert vertical space across the diagram, including
connector endpoints. Glyph outlines make the SVG independent of viewer fonts.
"""
from pathlib import Path
import copy
import unicodedata
import re
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[2]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
FONTS = {}
for weight in (400, 700):
    font = TTFont(ROOT / 'book/fonts' / f'SourceHanSansCN-{"Bold" if weight == 700 else "Regular"}.otf')
    FONTS[weight] = (font, font.getBestCmap(), font.getGlyphSet(), font['head'].unitsPerEm)


def glyph_info(char, cmap):
    if ord(char) in cmap:
        return cmap[ord(char)], 1, 0
    base = unicodedata.normalize('NFKD', char)
    if len(base) == 1 and ord(base) in cmap:
        return cmap[ord(base)], .65, .2 if 'SUBSCRIPT' in unicodedata.name(char) else -.4
    raise ValueError(f'Missing Source Han Sans glyph: {char!r}')


def measure(text, size, weight):
    font, cmap, _, upm = FONTS[weight]
    return sum(font['hmtx'][glyph_info(c, cmap)[0]][0] * glyph_info(c, cmap)[1] for c in text) * size / upm


def wrap(text, width, size, weight):
    if measure(text, size, weight) <= width:
        return [text]
    # Prefer word/punctuation boundaries; a long code token may continue on the
    # next line. Its characters and order remain unchanged.
    tokens = re.findall(r'（[A-Za-z0-9_]+）|\([A-Za-z0-9_]+\)|[A-Za-z0-9_]+|\s+|.', text)
    lines, current = [], ''
    for token in tokens:
        if current and measure(current + token, size, weight) > width:
            lines.append(current)
            current = ''
        for char in token:
            if current and measure(current + char, size, weight) > width:
                lines.append(current)
                current = ''
            current += char
    if current:
        lines.append(current)
    # Avoid a lone final CJK character or closing delimiter. Keep the exact
    # character sequence while balancing the last two lines.
    if len(lines) > 1 and len(lines[-1].strip()) < 3:
        previous, last = lines[-2:]
        candidates = [(abs(measure(previous[:i], size, weight)-measure(previous[i:]+last, size, weight)), i)
                      for i in range(1, len(previous))
                      if measure(previous[i:]+last, size, weight) <= width
                      and not previous[i:].startswith(('）', ')', '，', '。'))
                      and not (previous[i-1].isascii() and previous[i-1].isalnum()
                               and previous[i].isascii() and previous[i].isalnum())]
        if candidates:
            _, i = min(candidates)
            lines[-2:] = [previous[:i], previous[i:]+last]
    return lines


def compact_vertical_space(root):
    """Shorten empty horizontal bands without changing text or graph topology.

    Protect text, horizontal edges and diagonal segments. Vertical connectors
    and enclosing panels shrink together under the same coordinate mapping.
    This removes spare panel height while retaining room around arrowheads.
    """
    height = float(root.get('viewBox').split()[3])
    occupied = [(0, 0), (height, height)]
    for el in root:
        tag = el.tag.rsplit('}', 1)[-1]
        if tag == 'text':
            y, size = float(el.get('y')), float(el.get('font-size'))
            occupied.append((y-size, y+8))
        elif tag == 'rect' and 'x' in el.attrib:
            y, h = float(el.get('y')), float(el.get('height'))
            occupied.extend([(y-8, y+8), (y+h-8, y+h+8)])
        elif tag == 'circle':
            y, r = float(el.get('cy')), float(el.get('r'))
            occupied.append((y-r-8, y+r+8))
        elif tag == 'path':
            points = [(float(x), float(y)) for x, y in
                      re.findall(r'[ML]\s*(-?[\d.]+)[ ,]+(-?[\d.]+)', el.get('d'))]
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                if x1 != x2:
                    occupied.append((min(y1, y2)-8, max(y1, y2)+8))
            for _, y in points:
                occupied.append((y-8, y+8))
    merged = []
    for lo, hi in sorted(occupied):
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    cuts = [(a[1]+10, b[0]-10) for a, b in zip(merged, merged[1:])
            if b[0]-a[1] > 40]

    def move(y):
        return y-sum(max(0, min(y, end)-start) for start, end in cuts)

    for el in root:
        tag = el.tag.rsplit('}', 1)[-1]
        if tag == 'rect':
            y, h = float(el.get('y', 0)), float(el.get('height'))
            el.set('y', f'{move(y):g}')
            el.set('height', f'{move(y+h)-move(y):g}')
        elif tag == 'text':
            el.set('y', f'{move(float(el.get("y"))):g}')
        elif tag == 'circle':
            el.set('cy', f'{move(float(el.get("cy"))):g}')
        elif tag == 'path':
            el.set('d', re.sub(r'([ML])\s*(-?[\d.]+)[ ,]+(-?[\d.]+)',
                              lambda m: f'{m[1]}{m[2]} {move(float(m[3])):g}', el.get('d')))
    root.set('viewBox', f'0 0 900 {move(height):g}')
    return move(height)


def typeset(source, name):
    root = ET.fromstring(source)
    rects = [e for e in root if e.tag == f'{{{NS}}}rect' and 'x' in e.attrib]
    text_nodes = [e for e in root if e.tag == f'{{{NS}}}text']
    layouts, additions = [], {}
    for el in text_nodes:
        x, y = float(el.get('x')), float(el.get('y'))
        weight = 700 if el.get('font-weight') in ('700', 'bold') else 400
        size = max(float(el.get('font-size', 22)), 28 if weight == 700 else 26)
        panels = []
        for r in rects:
            rx, ry, rw, rh = (float(r.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
            if rx + 2 < x < rx + rw - 2 and ry + 8 < y < ry + rh:
                panels.append((rw * rh, rx, rw))
        width = 2 * min(x - 10, 890 - x)
        if panels:
            _, rx, rw = min(panels)
            width = min(width, 2 * min(x - rx - 10, rx + rw - x - 10))
        # Narrow marginal labels (e.g. the vertical context-window bracket)
        # keep their existing character-per-line arrangement.
        width = max(size, width)
        lines = wrap(el.text or '', width, size, weight)
        threshold = y + 4
        additions[threshold] = max(additions.get(threshold, 0), (len(lines) - 1) * 32)
        layouts.append((el, x, y, size, weight, lines))

    def move(y):
        return y + sum(extra for threshold, extra in additions.items() if threshold <= y)

    for el in root:
        tag = el.tag.rsplit('}', 1)[-1]
        if tag == 'rect':
            y = float(el.get('y', 0)); h = float(el.get('height'))
            el.set('y', f'{move(y):g}'); el.set('height', f'{move(y+h)-move(y):g}')
        elif tag == 'circle':
            el.set('cy', f'{move(float(el.get("cy"))):g}')
        elif tag == 'path':
            # Chapter drawings use absolute M/L polyline coordinates.
            el.set('d', re.sub(r'([ML])\s*(-?[\d.]+)[ ,]+(-?[\d.]+)',
                              lambda m: f'{m[1]}{m[2]} {move(float(m[3])):g}', el.get('d')))
    for el, x, y, size, weight, lines in layouts:
        index = list(root).index(el)
        root.remove(el)
        for i, line in enumerate(lines):
            node = copy.deepcopy(el)
            node.text = line
            node.set('y', f'{move(y)+32*i:g}')
            node.set('font-size', f'{size:g}')
            node.set('font-family', 'Source Han Sans CN')
            root.insert(index+i, node)
    old_height = float(root.get('viewBox').split()[3])
    height = move(old_height)
    root.set('viewBox', f'0 0 900 {height:g}')
    # Quantitative plots and spatial grids retain their coordinate scale.
    if name not in {'fig6-7.svg', 'fig6-8.svg', 'fig8-3.svg'}:
        height = compact_vertical_space(root)
    root.set('width', '106mm'); root.set('height', f'{height*106/900:.3f}mm')
    proof = ROOT / 'book/build/figure-text'
    proof.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(proof / name, encoding='unicode')
    outline(root)
    return ET.tostring(root, encoding='unicode') + '\n'


def outline(root):
    defs = ET.SubElement(root, f'{{{NS}}}defs')
    used = set()
    for el in list(root):
        if el.tag != f'{{{NS}}}text':
            continue
        weight = 700 if el.get('font-weight') in ('700', 'bold') else 400
        font, cmap, glyphs, upm = FONTS[weight]
        size = float(el.get('font-size')); scale = size/upm
        text = el.text or ''
        x = float(el.get('x')) - measure(text, size, weight)/2
        y = float(el.get('y'))
        group = ET.Element(f'{{{NS}}}g', {'aria-label': text, 'fill': el.get('fill', '#292929'), 'data-font': f'Source Han Sans CN {weight}', 'data-size': str(size)})
        for c in text:
            glyph, factor, offset = glyph_info(c, cmap)
            ident = f'g{weight}-{ord(c):x}'
            if ident not in used:
                pen = SVGPathPen(glyphs); glyphs[glyph].draw(pen)
                ET.SubElement(defs, f'{{{NS}}}path', {'id': ident, 'd': pen.getCommands()})
                used.add(ident)
            ET.SubElement(group, f'{{{NS}}}use', {'href': '#'+ident, 'transform': f'translate({x:.3f} {y+offset*size:g}) scale({scale*factor:g} {-scale*factor:g})'})
            x += font['hmtx'][glyph][0]*scale*factor
        index = list(root).index(el); root.remove(el); root.insert(index, group)
