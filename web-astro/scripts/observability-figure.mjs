import {
  evaluationKit,
  row,
  heading,
  title,
  panel,
} from './evaluation-layout-kit.mjs';
export function layoutObservability(source, options = {}) {
  const k = evaluationKit(source, 7, 26, options),
    leftW = 600,
    rightX = 656,
    rightW = 320;
  const headH = Math.max(
    k.height(0, 552, { size: 20, bold: true }),
    k.height(14, 272, { size: 20, bold: true }),
  );
  let left = k.label(0, 48, 44, 552, headH, { size: 20, bold: true }),
    right = k.label(14, 680, 44, 272, headH, { size: 20, bold: true });
  const start = 44 + headH + 24;
  let y = start;
  const nodes = [];
  const rows = [
    [title(1)],
    [title(2), row(3, { muted: true })],
    [title(4), row(5, { muted: true })],
    [title(6), row(7, { muted: true })],
    [title(8), row(9, { muted: true })],
    [title(10), row(11, { muted: true })],
    [title(12), row(13, { muted: true })],
  ];
  rows.forEach((r, i) => {
    const child = i === 3 || i === 4,
      x = child ? 144 : 104,
      w = 600 - x;
    const p = panel(k, x, y, w, r, {
      name: `trace-${i}`,
      fill: i === 0 ? '#d0d0d0' : child ? '#f5f5f5' : '#f0f0f0',
    });
    left += `<g data-trace-depth="${child ? 1 : 0}">${p.svg}</g>`;
    nodes.push({
      x: child ? 124 : 76,
      y: y + p.h / 2,
      top: y,
      bottom: y + p.h,
      cardX: x,
    });
    y += p.h + 24;
  });
  let spine = k.path(`M76 ${nodes[0].y} V${nodes[6].y}`, { arrow: false });
  // The child branch begins below the parent tool card, never through its text.
  spine += k.path(`M124 ${nodes[2].bottom + 8} V${nodes[4].y}`, {
    arrow: false,
  });
  nodes.forEach((n) => {
    spine += k.path(`M${n.x} ${n.y} H${n.cardX - 8}`, { arrow: false });
    spine += `<circle cx="${n.x}" cy="${n.y}" r="4" fill="#666666"/>`;
  });
  let ry = start;
  for (const [i, r] of [
    [0, [title(15), row(16), row(17), row(18)]],
    [1, [title(19), row(20), row(21)]],
    [2, [title(22), row(23, { min: 51 }), row(24)]],
  ]) {
    const p = panel(k, rightX + 16, ry, rightW - 32, r, {
      name: `dashboard-${i}`,
    });
    right += p.svg;
    ry += p.h + 24;
  }
  const bottom = Math.max(y, ry),
    frameH = bottom - 24;
  let svg = `<g data-trace-tree="true">${k.card(24, 24, leftW, frameH, { fill: '#ffffff', dash: true })}${spine}${left}</g><g data-dashboard="true">${k.card(rightX, 24, rightW, frameH, { fill: '#ffffff', dash: true })}${right}</g>`;
  const footer = panel(k, 24, bottom + 24, 952, [row(25, { bold: true })], {
    name: 'closed-loop',
    fill: '#d0d0d0',
  });
  svg += footer.svg;
  return k.svg(svg, bottom + 24 + footer.h + 24);
}
