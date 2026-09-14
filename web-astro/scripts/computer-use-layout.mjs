import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';
const row = (ids, options = {}) => ({ ids, ...options });
const heading = (ids) => row(ids, { size: 20, bold: true });
const title = (ids) => row(ids, { size: 18, bold: true });
const code = (ids) =>
  row(ids, { size: 14, mono: true, align: 'start', direction: 'ltr' });
const edge = (name, drawing) => `<g data-edge="${name}">${drawing}</g>`;
function panel(
  k,
  x,
  y,
  w,
  rows,
  { fill = '#f0f0f0', min = 0, name = '' } = {},
) {
  const heights = rows.map((r) => k.height(r.ids, w - 40, r));
  const h = Math.max(
    min,
    40 + heights.reduce((a, b) => a + b, 0) + (rows.length - 1) * 12,
  );
  let result = `<g data-panel="${name}">${k.card(x, y, w, h, { fill })}`,
    cursor = y + 20;
  rows.forEach((r, i) => {
    result += k.label(r.ids, x + 20, cursor, w - 40, heights[i], r);
    cursor += heights[i] + 12;
  });
  return { svg: result + '</g>', h };
}
// Vertical sequences reserve dedicated gutters for arrows in every language.
function sequence(k, y, stages, name) {
  let svg = '';
  stages.forEach((rows, i) => {
    const p = panel(k, 120, y, 760, rows, {
      name: `${name}-${i}`,
      fill: i % 2 ? '#ffffff' : '#f0f0f0',
    });
    svg += p.svg;
    y += p.h;
    if (i < stages.length - 1) {
      svg += edge(`${name}-${i}-${i + 1}`, k.arrow(500, y + 8, 500, y + 48));
      y += 56;
    }
  });
  return { svg, y };
}
function perceptionLoop(k) {
  const stages = [
    [heading(0), title(1), row(2), row(3, { muted: true })],
    [heading(5), title(6), row(7), title(8), row(9), code(10), code(11)],
    [heading(13), title(14), row(15), row(16), row(17), row(18), row(19)],
  ];
  let y = 24,
    svg = '',
    firstMid,
    lastMid;
  stages.forEach((rows, i) => {
    const p = panel(k, 120, y, 760, rows, {
      name: `perception-${i}`,
      fill: i === 1 ? '#d0d0d0' : '#f0f0f0',
    });
    svg += p.svg;
    if (!i) firstMid = y + p.h / 2;
    if (i === 2) lastMid = y + p.h / 2;
    y += p.h;
    if (i < 2) {
      const id = i === 0 ? 4 : 12,
        h = k.height(id, 280, { size: 14 }),
        gutter = Math.max(64, h + 24);
      svg += edge(
        i === 0 ? 'screenshot-inference' : 'inference-action',
        k.arrow(500, y + 8, 500, y + gutter - 8),
      );
      svg += k.label(id, 530, y + (gutter - h) / 2, 280, h, {
        size: 14,
        align: 'start',
      });
      y += gutter;
    }
  });
  svg += edge(
    'action-next-screenshot',
    k.path(`M888 ${lastMid} H948 V${firstMid} H888`),
  );
  y += 32;
  const footer = panel(
    k,
    120,
    y,
    760,
    [row(20, { bold: true }), row(21, { muted: true })],
    { name: 'loop-explanation', fill: '#ffffff' },
  );
  return k.svg(svg + footer.svg, y + footer.h + 24);
}
function actionSpace(k) {
  const groups = [
    [
      heading(0),
      title(1),
      code(2),
      code(3),
      code(4),
      title(5),
      code(6),
      code(7),
      title(8),
      code(9),
    ],
    [
      heading(10),
      title(11),
      code(12),
      title(13),
      code(14),
      title(15),
      code(16),
    ],
    [heading(21), title(22), code(23), code(24)],
    [heading(17), title(18), code(19), code(20)],
  ];
  let y = 24,
    svg = '';
  for (let i = 0; i < groups.length; i += 2) {
    const h = Math.max(
      ...groups.slice(i, i + 2).map((r) => panel(k, 0, 0, 464, r).h),
    );
    groups.slice(i, i + 2).forEach((r, j) => {
      svg += panel(k, 24 + j * 488, y, 464, r, {
        min: h,
        name: `actions-${i + j}`,
      }).svg;
    });
    y += h + 24;
  }
  const scaling = panel(k, 24, y, 952, [heading(25), row(26), row(27)], {
    fill: '#ffffff',
    name: 'coordinate-scaling',
  });
  svg += scaling.svg;
  y += scaling.h + 40;
  const h = k.height(28, 952, { size: 20, bold: true });
  svg += k.label(28, 24, y, 952, h, { size: 20, bold: true });
  y += h + 24;
  const steps = sequence(
    k,
    y,
    Array.from({ length: 5 }, (_, i) => [title(29 + i * 2), row(30 + i * 2)]),
    'form',
  );
  svg += steps.svg;
  const end = panel(k, 24, steps.y + 24, 952, [row(39, { muted: true })], {
    name: 'timing',
    fill: '#ffffff',
  });
  return k.svg(svg + end.svg, steps.y + 24 + end.h + 24);
}
function elementIndex(k) {
  const leftX = 24,
    rightX = 512,
    width = 464;
  const titleH = Math.max(
    k.height(0, 424, { size: 20, bold: true }),
    k.height(9, 424, { size: 20, bold: true }),
  );
  let left = k.label(0, leftX + 20, 44, 424, titleH, { size: 20, bold: true }),
    y = 44 + titleH + 24;
  // Annotation badges have their own column instead of covering the controls.
  for (const [badge, content] of [
    [2, 1],
    [4, 3],
    [6, 5],
    [8, 7],
  ]) {
    const h = Math.max(
      48,
      k.height(content, 304, { size: content === 1 ? 14 : 16 }) + 24,
    );
    left += `<g data-annotated-element="${badge}">${k.card(leftX + 20, y, 424, h, { fill: '#ffffff', dash: true })}${k.label(badge, leftX + 30, y + 12, 48, h - 24, { size: 14, bold: true })}${k.label(content, leftX + 92, y + 12, 304, h - 24, { size: content === 1 ? 14 : 16, mono: content === 1, align: 'start' })}</g>`;
    y += h + 16;
  }
  const list = [
    heading(9),
    ...Array.from({ length: 8 }, (_, i) => code(10 + i)),
    row(18, { muted: true }),
  ];
  const listPanel = panel(k, rightX, 24, width, list, { name: 'element-list' }),
    topH = Math.max(y - 24 + 4, listPanel.h);
  let svg = `<g data-panel="annotated-webpage">${k.card(leftX, 24, width, topH, { fill: '#ffffff' })}${left}</g>`;
  svg += panel(k, rightX, 24, width, list, {
    name: 'element-list',
    min: topH,
  }).svg;
  y = 24 + topH + 40;
  const h = k.height(19, 952, { size: 20, bold: true });
  svg += k.label(19, 24, y, 952, h, { size: 20, bold: true });
  const flow = sequence(
    k,
    y + h + 24,
    Array.from({ length: 5 }, (_, i) => [title([20 + i * 2, 21 + i * 2])]),
    'som',
  );
  const note = panel(k, 24, flow.y + 24, 952, [row(30, { muted: true })], {
    name: 'scope',
    fill: '#ffffff',
  });
  return k.svg(svg + flow.svg + note.svg, flow.y + 24 + note.h + 24);
}
function coordinateScaling(k) {
  let y = 24,
    svg = '';
  const stages = [
    [heading(0), title(1), row(2), row(3)],
    [heading(4), row(5), row(6), row(7), row(8, { muted: true })],
    [heading(9), row(10), title(11), row(12, { muted: true })],
  ];
  stages.forEach((rows, i) => {
    const p = panel(k, 160, y, 680, rows, {
      name: `resolution-${i}`,
      fill: i === 1 ? '#d0d0d0' : '#f0f0f0',
    });
    svg += p.svg;
    y += p.h;
    if (i < 2) {
      const id = 13 + i,
        h = k.height(id, 260, { size: 14 }),
        gutter = Math.max(72, h + 24);
      if (!i)
        svg += edge(
          'screen-downscale',
          k.arrow(500, y + 8, 500, y + gutter - 8),
        );
      else {
        svg += edge(
          'training-output',
          k.arrow(468, y + 8, 468, y + gutter - 8),
        );
        svg += edge(
          'output-training',
          k.arrow(532, y + gutter - 8, 532, y + 8),
        );
      }
      svg += k.label(id, 560, y + (gutter - h) / 2, 260, h, {
        size: 14,
        align: 'start',
      });
      y += gutter;
    }
  });
  for (const [name, rows] of [
    ['full-workflow', [heading(15), row(16)]],
    ['scaling-example', [title(17), row(18)]],
  ]) {
    y += 24;
    const p = panel(k, 24, y, 952, rows, { name, fill: '#ffffff' });
    svg += p.svg;
    y += p.h;
  }
  return k.svg(svg, y + 24);
}
export function layoutComputerUse(source, figure, { rtl = false } = {}) {
  const counts = { 11: 22, 12: 40, 13: 31, 14: 19 };
  if (!counts[figure])
    throw new Error(`Unsupported computer-use figure: ${figure}`);
  const labels = extractLabels(source, `6-${figure}`, [counts[figure]]),
    k = figureKit(labels, { rtl });
  return {
    11: perceptionLoop,
    12: actionSpace,
    13: elementIndex,
    14: coordinateScaling,
  }[figure](k);
}
