import {
  evaluationKit,
  row,
  heading,
  title,
  edge,
  panel,
} from './evaluation-layout-kit.mjs';
export function layoutLlmJudge(source, options = {}) {
  const k = evaluationKit(source, 5, 35, options);
  const evidence = [
    [heading(0), row(1), row(2), row(3, { min: 51 }), row(4)],
    [heading(5), row(6), row([7, 8]), row(9)],
    [heading(10), row(11), row(12), row(13), row(14)],
  ];
  const sourceH = Math.max(
    ...evidence.map((rows) => panel(k, 0, 0, 296, rows).h),
  );
  let svg = '';
  evidence.forEach((rows, i) => {
    svg += panel(k, 24 + i * 328, 24, 296, rows, {
      name: `evidence-${i}`,
      min: sourceH,
      fill: i ? '#f0f0f0' : '#d0d0d0',
    }).svg;
  });
  const bottom = 24 + sourceH,
    busY = bottom + 40,
    judgeY = bottom + 88;
  for (const x of [172, 500, 828])
    svg += k.path(`M${x} ${bottom + 8} V${busY}`, { arrow: false });
  svg += `<g data-input-bus="true">${k.path(`M172 ${busY} H828`, { arrow: false })}</g>`;
  svg += edge('evidence-judge', k.arrow(500, busY, 500, judgeY - 8));
  const judge = panel(
    k,
    160,
    judgeY,
    680,
    [heading(15), row(16, { muted: true })],
    { name: 'judge', fill: '#d0d0d0' },
  );
  svg += judge.svg;
  let y = judgeY + judge.h;
  svg += edge('judge-output', k.arrow(500, y + 8, 500, y + 48));
  y += 56;
  const outputH = k.height(17, 904, { size: 20, bold: true });
  let body = k.label(17, 48, y + 20, 904, outputH, { size: 20, bold: true }),
    scoreY = y + 40 + outputH;
  const rowHeights = Array.from(
    { length: 4 },
    (_, i) =>
      Math.max(
        k.height(18 + i * 3, 280, { size: 16, bold: true }),
        k.height(19 + i * 3, 80, { size: 18, bold: true }),
      ) +
      k.height(20 + i * 3, 384, { size: 16 }) +
      36,
  );
  const scoreH = rowHeights.reduce((a, b) => a + b, 0) + 20;
  body += k.card(48, scoreY, 424, scoreH, { fill: '#f5f5f5' });
  let cursor = scoreY + 16;
  for (let i = 0; i < 4; i++) {
    const label = 18 + i * 3,
      th = Math.max(
        k.height(label, 280, { size: 16, bold: true }),
        k.height(label + 1, 80, { size: 18, bold: true }),
      ),
      dh = k.height(label + 2, 384, { size: 16 });
    body += `<g data-score-row="${i}">${k.label(label, 68, cursor, 280, th, { size: 16, bold: true, align: 'start' })}${k.label(label + 1, 360, cursor, 80, th, { size: 18, bold: true })}${k.label(label + 2, 68, cursor + th + 8, 384, dh, { size: 16, muted: true, align: 'start' })}</g>`;
    cursor += rowHeights[i];
    if (i < 3) body += k.path(`M68 ${cursor - 12} H452`, { arrow: false });
  }
  const aggregation = panel(
    k,
    496,
    scoreY,
    456,
    [heading(30), row(31), row(32), row(33), row(34)],
    { name: 'aggregation', min: scoreH },
  );
  body += aggregation.svg;
  const outHeight = 40 + outputH + Math.max(scoreH, aggregation.h) + 24;
  return k.svg(
    svg +
      `<g data-output="structured">${k.card(24, y, 952, outHeight, { fill: '#ffffff', dash: true })}${body}</g>`,
    y + outHeight + 24,
  );
}
