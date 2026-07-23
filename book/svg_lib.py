"""SVG diagram generation library for book illustrations.

Style: black/white/grayscale for B&W printing.
- White (#fff) backgrounds
- Light gray (#f0f0f0) box fills
- Medium gray (#d0d0d0) secondary fills
- Dark gray (#999) emphasis fills
- Black (#333) borders and text
- 2px stroke, 6px rounded corners
- Sans-serif fonts (20px body, 16px small, 24px title)
- Designed for print: readable at 50-60% scaling
"""

import math
import os

COLORS = {
    'white': '#ffffff',
    'light': '#f0f0f0',
    'medium': '#d0d0d0',
    'dark': '#999999',
    'darker': '#666666',
    'border': '#333333',
    'text': '#333333',
    'text_light': '#666666',
    'bg': '#ffffff',
    'code_bg': '#f5f5f5',
}

FONT = "Arial, 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', sans-serif"
MONO = "'Courier New', Courier, monospace"
STROKE_W = 2
CORNER_R = 6

FS_TITLE = 24
FS_BODY = 20
FS_SMALL = 16
FS_TINY = 14
FS_LABEL = 16

# 按学术规范：图本身不包含标题，标题写在正文里。
# 当 OMIT_TITLE=True 时，任何 font_size==FS_TITLE 的“标题型”文本（短符号如
# VS/→/+ 除外）都视为图标题，不予渲染——无论它位于图的顶部还是中部（多面板
# 图的分节标题同样剔除）。短符号通过 TITLE_MIN_LEN 长度阈值保留。
OMIT_TITLE = True
TITLE_Y_THRESHOLD = 60   # 兼容旧逻辑保留，当前不再单独依赖
TITLE_MIN_LEN = 4        # 长度 >= 此值的 FS_TITLE 文本才视为标题并剔除
TITLE_CROP_PX = 40


def _escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def _marker_def():
    return (
        '<defs>'
        '<marker id="ah" markerWidth="12" markerHeight="8" refX="12" refY="4" orient="auto">'
        f'<polygon points="0 0, 12 4, 0 8" fill="{COLORS["border"]}"/>'
        '</marker>'
        '<marker id="ah-light" markerWidth="12" markerHeight="8" refX="12" refY="4" orient="auto">'
        f'<polygon points="0 0, 12 4, 0 8" fill="{COLORS["dark"]}"/>'
        '</marker>'
        '</defs>'
    )


class SVG:
    """SVG diagram builder."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.elems = []

    def rect(self, x, y, w, h, fill='light', stroke='border', rx=CORNER_R, dash=False):
        c_fill = COLORS.get(fill, fill)
        c_stroke = COLORS.get(stroke, stroke)
        d = ' stroke-dasharray="8,4"' if dash else ''
        self.elems.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{c_fill}" stroke="{c_stroke}" stroke-width="{STROKE_W}"{d}/>'
        )

    def box(self, x, y, w, h, label, fill='light', sublabel=None, bold=False, font_size=FS_BODY,
            first_line_font_size=None):
        self.rect(x, y, w, h, fill=fill)
        fw = 'bold' if bold else 'normal'
        lines = label.split('\n')
        if sublabel:
            lines.append(sublabel)
        total = len(lines)
        start_y = y + h / 2 - (total - 1) * (font_size * 0.6)
        for i, line in enumerate(lines):
            ly = start_y + i * font_size * 1.3
            fs = font_size - 2 if (sublabel and i == total - 1) else font_size
            if first_line_font_size and i == 0:
                fs = first_line_font_size
            fc = COLORS['text_light'] if (sublabel and i == total - 1) else COLORS['text']
            w2 = 'bold' if (bold and i == 0 and not sublabel) else ('bold' if bold else 'normal')
            self.elems.append(
                f'<text x="{x + w / 2}" y="{ly}" font-family="{FONT}" font-size="{fs}" '
                f'fill="{fc}" text-anchor="middle" dominant-baseline="central" font-weight="{w2}">'
                f'{_escape(line)}</text>'
            )

    def text(self, x, y, content, size=FS_BODY, bold=False, anchor='middle', fill='text', baseline='central'):
        # Skip in-figure titles per academic convention (titles belong in body text).
        # Drop any FS_TITLE-sized phrase anywhere in the figure; keep short symbols
        # (VS / → / + 等) which also happen to use the title size as diagram content.
        if OMIT_TITLE and size == FS_TITLE and len(str(content).strip()) >= TITLE_MIN_LEN:
            return
        c = COLORS.get(fill, fill)
        fw = 'bold' if bold else 'normal'
        self.elems.append(
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{c}" '
            f'text-anchor="{anchor}" dominant-baseline="{baseline}" font-weight="{fw}">'
            f'{_escape(content)}</text>'
        )

    def mono(self, x, y, content, size=FS_SMALL, anchor='start', fill='text'):
        """Monospace text for code snippets."""
        c = COLORS.get(fill, fill)
        self.elems.append(
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{c}" '
            f'text-anchor="{anchor}" dominant-baseline="central">'
            f'{_escape(content)}</text>'
        )

    def code_block(self, x, y, w, lines, font_size=FS_SMALL, line_h=None):
        """Render a block of monospace code lines with background."""
        if line_h is None:
            line_h = font_size * 1.5
        h = len(lines) * line_h + 12
        self.rect(x, y, w, h, fill='code_bg', stroke='dark', rx=4)
        for i, line in enumerate(lines):
            ly = y + 10 + i * line_h + line_h / 2
            self.mono(x + 10, ly, line, size=font_size)
        return h

    def multiline_text(self, x, y, lines, size=FS_BODY, anchor='middle', fill='text', line_h=None, bold=False):
        """Render multiple lines of text."""
        if line_h is None:
            line_h = size * 1.4
        for i, line in enumerate(lines):
            ly = y + i * line_h
            self.text(x, ly, line, size=size, anchor=anchor, fill=fill, bold=bold)

    def arrow(self, x1, y1, x2, y2, label=None, dash=False, color='border'):
        c = COLORS.get(color, color)
        d = ' stroke-dasharray="8,4"' if dash else ''
        mk = 'ah-light' if color in ('dark', COLORS['dark']) else 'ah'
        self.elems.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{c}" stroke-width="{STROKE_W}"{d} marker-end="url(#{mk})"/>'
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.elems.append(
                f'<text x="{mx}" y="{my - 10}" font-family="{FONT}" font-size="{FS_LABEL}" '
                f'fill="{COLORS["text_light"]}" text-anchor="middle">{_escape(label)}</text>'
            )

    def arrow_curved(self, x1, y1, x2, y2, curve=30, label=None, dash=False, color='border'):
        """Draw a curved arrow using a quadratic bezier."""
        c = COLORS.get(color, color)
        d = ' stroke-dasharray="8,4"' if dash else ''
        mk = 'ah-light' if color in ('dark', COLORS['dark']) else 'ah'
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            nx, ny = -dy / dist * curve, dx / dist * curve
        else:
            nx, ny = 0, -curve
        cx, cy = mx + nx, my + ny
        self.elems.append(
            f'<path d="M {x1},{y1} Q {cx},{cy} {x2},{y2}" fill="none" '
            f'stroke="{c}" stroke-width="{STROKE_W}"{d} marker-end="url(#{mk})"/>'
        )
        if label:
            lx, ly = (x1 + 2 * cx + x2) / 4, (y1 + 2 * cy + y2) / 4
            self.text(lx, ly - 10, label, size=FS_LABEL, fill='text_light')

    def line(self, x1, y1, x2, y2, dash=False, color='border'):
        c = COLORS.get(color, color)
        d = ' stroke-dasharray="8,4"' if dash else ''
        self.elems.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{c}" stroke-width="{STROKE_W}"{d}/>'
        )

    def circle(self, cx, cy, r, fill='light', label=None, font_size=FS_SMALL):
        c = COLORS.get(fill, fill)
        self.elems.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" '
            f'stroke="{COLORS["border"]}" stroke-width="{STROKE_W}"/>'
        )
        if label:
            self.elems.append(
                f'<text x="{cx}" y="{cy}" font-family="{FONT}" font-size="{font_size}" '
                f'fill="{COLORS["text"]}" text-anchor="middle" dominant-baseline="central">'
                f'{_escape(label)}</text>'
            )

    def diamond(self, cx, cy, w, h, fill='light', label=None, font_size=FS_SMALL):
        c = COLORS.get(fill, fill)
        pts = f'{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}'
        self.elems.append(
            f'<polygon points="{pts}" fill="{c}" stroke="{COLORS["border"]}" stroke-width="{STROKE_W}"/>'
        )
        if label:
            self.elems.append(
                f'<text x="{cx}" y="{cy}" font-family="{FONT}" font-size="{font_size}" '
                f'fill="{COLORS["text"]}" text-anchor="middle" dominant-baseline="central">'
                f'{_escape(label)}</text>'
            )

    def brace_right(self, x, y1, y2, label=None):
        my = (y1 + y2) / 2
        d = (f'M {x},{y1} C {x + 20},{y1} {x + 20},{my - 5} {x + 25},{my} '
             f'C {x + 20},{my + 5} {x + 20},{y2} {x},{y2}')
        self.elems.append(
            f'<path d="{d}" fill="none" stroke="{COLORS["border"]}" stroke-width="{STROKE_W}"/>'
        )
        if label:
            self.text(x + 35, my, label, size=FS_SMALL, anchor='start')

    def group_box(self, x, y, w, h, label, fill='white'):
        """A dashed group boundary with a label at top-left."""
        self.rect(x, y, w, h, fill=fill, rx=8, dash=True)
        self.text(x + 12, y + 18, label, size=FS_SMALL, bold=True, fill='text_light', anchor='start')

    def badge(self, x, y, w, h, label, fill='dark', font_size=FS_SMALL):
        """Small rounded badge/tag."""
        self.rect(x, y, w, h, fill=fill, rx=h // 2)
        self.text(x + w / 2, y + h / 2, label, size=font_size, fill='white', bold=True)

    def render(self):
        if OMIT_TITLE:
            crop = TITLE_CROP_PX
            vb = f'0 {crop} {self.width} {self.height - crop}'
            h_attr = self.height - crop
        else:
            vb = f'0 0 {self.width} {self.height}'
            h_attr = self.height
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{self.width}" height="{h_attr}" '
            f'style="background:{COLORS["bg"]}">',
            _marker_def(),
        ]
        parts.extend(self.elems)
        parts.append('</svg>')
        return '\n'.join(parts)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.render())


def flow_lr(nodes, width=800, node_h=55, node_w=None, fills=None, spacing=25):
    """Left-to-right flow diagram: nodes connected by arrows."""
    n = len(nodes)
    if node_w is None:
        node_w = min(150, (width - spacing * (n + 1)) // n)
    total_w = n * node_w + (n - 1) * spacing
    x_start = (width - total_w) / 2
    height = node_h + 70
    svg = SVG(width, height)
    y = (height - node_h) / 2
    positions = []
    for i, label in enumerate(nodes):
        x = x_start + i * (node_w + spacing)
        f = (fills[i] if fills else 'light') if fills and i < len(fills) else 'light'
        svg.box(x, y, node_w, node_h, label, fill=f)
        positions.append((x, y))
        if i > 0:
            px = positions[i - 1][0] + node_w
            svg.arrow(px + 2, y + node_h / 2, x - 2, y + node_h / 2)
    return svg


def flow_tb(nodes, width=350, node_h=55, node_w=240, fills=None, spacing=35, arrow_labels=None):
    """Top-to-bottom flow diagram."""
    n = len(nodes)
    height = n * node_h + (n - 1) * spacing + 50
    svg = SVG(width, height)
    x = (width - node_w) / 2
    positions = []
    for i, label in enumerate(nodes):
        y = 25 + i * (node_h + spacing)
        f = (fills[i] if fills else 'light') if fills and i < len(fills) else 'light'
        svg.box(x, y, node_w, node_h, label, fill=f)
        positions.append((x, y))
        if i > 0:
            al = arrow_labels[i - 1] if arrow_labels and i - 1 < len(arrow_labels) else None
            svg.arrow(x + node_w / 2, positions[i - 1][1] + node_h + 2,
                      x + node_w / 2, y - 2, label=al)
    return svg


def tree_diagram(root, children, width=750, root_h=60, child_h=55, child_w=None, root_w=220):
    """Tree diagram: root node with children below."""
    n = len(children)
    if child_w is None:
        child_w = min(170, (width - 20) // max(n, 1))
    spacing = 20
    total_cw = n * child_w + (n - 1) * spacing
    x_start = (width - total_cw) / 2
    height = root_h + child_h + 120
    svg = SVG(width, height)
    rx = (width - root_w) / 2
    svg.box(rx, 20, root_w, root_h, root, fill='medium', bold=True)
    root_cx = width / 2
    root_bot = 20 + root_h
    for i, label in enumerate(children):
        cx = x_start + i * (child_w + spacing) + child_w / 2
        cy = root_bot + 55
        svg.line(root_cx, root_bot, cx, cy)
        svg.box(x_start + i * (child_w + spacing), cy, child_w, child_h, label)
    return svg


def layer_diagram(layers, width=600, layer_h=55, spacing=14):
    """Stacked horizontal layers (top = first layer)."""
    n = len(layers)
    lw = width - 80
    height = n * layer_h + (n - 1) * spacing + 50
    svg = SVG(width, height)
    x = 40
    for i, (label, fill) in enumerate(layers):
        y = 25 + i * (layer_h + spacing)
        svg.box(x, y, lw, layer_h, label, fill=fill)
    return svg


def comparison_lr(left_title, left_items, right_title, right_items, width=750, item_h=45):
    """Side-by-side comparison diagram."""
    col_w = (width - 100) // 2
    n = max(len(left_items), len(right_items))
    height = 80 + n * (item_h + 10) + 25
    svg = SVG(width, height)
    lx = 25
    rx = width - col_w - 25
    svg.box(lx, 20, col_w, 50, left_title, fill='medium', bold=True)
    svg.box(rx, 20, col_w, 50, right_title, fill='medium', bold=True)
    for i, label in enumerate(left_items):
        y = 85 + i * (item_h + 10)
        svg.box(lx, y, col_w, item_h, label, fill='light')
    for i, label in enumerate(right_items):
        y = 85 + i * (item_h + 10)
        svg.box(rx, y, col_w, item_h, label, fill='light')
    return svg


def cycle_diagram(nodes, width=480, height=480, radius=160):
    """Circular cycle diagram with arrows between nodes."""
    n = len(nodes)
    cx, cy = width / 2, height / 2
    svg = SVG(width, height)
    node_w, node_h = 120, 50
    positions = []
    for i in range(n):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        nx = cx + radius * math.cos(angle)
        ny = cy + radius * math.sin(angle)
        positions.append((nx, ny))
        svg.box(nx - node_w / 2, ny - node_h / 2, node_w, node_h, nodes[i], fill='light', font_size=FS_SMALL)

    for i in range(n):
        j = (i + 1) % n
        x1, y1 = positions[i]
        x2, y2 = positions[j]
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        ux, uy = dx / dist, dy / dist
        offset_start = max(node_w, node_h) / 2 + 5
        offset_end = max(node_w, node_h) / 2 + 5
        svg.arrow(x1 + ux * offset_start, y1 + uy * offset_start,
                  x2 - ux * offset_end, y2 - uy * offset_end)
    return svg
