import {
  evaluationKit,
  row,
  heading,
  title,
  edge,
  panel,
} from './evaluation-layout-kit.mjs';
export function layoutImprovementCycle(source, options = {}) {
  const k = evaluationKit(source, 8, 37, options),
    leftX = 24,
    rightX = 512,
    w = 424;
  const observationRows = [heading(0), row(1), row(2), row(3), row(4)];
  const hypothesisRows = [
    heading(5),
    title(6),
    row(7),
    title(8),
    row(9),
    title(10),
    row(11),
  ];
  const topH = Math.max(
    panel(k, 0, 0, w, observationRows).h,
    panel(k, 0, 0, w, hypothesisRows).h,
  );
  let svg =
    panel(k, leftX, 24, w, observationRows, { name: 'observation', min: topH })
      .svg +
    panel(k, rightX, 24, w, hypothesisRows, { name: 'hypothesis', min: topH })
      .svg;
  svg += edge(
    'observation-hypothesis',
    k.arrow(456, 24 + topH / 2, 504, 24 + topH / 2),
  );
  let y = 24 + topH;
  svg += edge('hypothesis-experiment', k.arrow(724, y + 8, 724, y + 48));
  y += 56;
  const h = k.height(12, 864, { size: 20, bold: true });
  let experiments = k.label(12, 48, y + 20, 864, h, { size: 20, bold: true }),
    cy = y + 40 + h;
  for (let r = 0; r < 2; r++) {
    const groups = [0, 1].map((c) => [
      title(13 + (r * 2 + c) * 3),
      row(14 + (r * 2 + c) * 3),
      row(15 + (r * 2 + c) * 3, { muted: true }),
    ]);
    const rh = Math.max(...groups.map((rows) => panel(k, 0, 0, 408, rows).h));
    groups.forEach((rows, c) => {
      experiments += panel(k, 48 + c * 432, cy, 408, rows, {
        name: `experiment-${r * 2 + c}`,
        min: rh,
        fill: r === 1 && c === 0 ? '#f0f0f0' : '#d0d0d0',
      }).svg;
    });
    cy += rh + 24;
  }
  svg += `<g data-experiments="true">${k.card(24, y, 912, cy - y, { fill: '#ffffff', dash: true })}${experiments}</g>`;
  y = cy;
  svg += edge('experiment-decision', k.arrow(236, y + 8, 236, y + 48));
  y += 56;
  const decisions = [heading(25), row(26), row(27), row(28), row(29)];
  const iteration = [heading(30), row(31), row(32), row(33), row(34)];
  const bottomH = Math.max(
    panel(k, 0, 0, w, decisions).h,
    panel(k, 0, 0, w, iteration).h,
  );
  svg +=
    panel(k, leftX, y, w, decisions, { name: 'decision', min: bottomH }).svg +
    panel(k, rightX, y, w, iteration, {
      name: 'iteration',
      min: bottomH,
      fill: '#d0d0d0',
    }).svg;
  svg += edge(
    'decision-iteration',
    k.arrow(456, y + bottomH / 2, 504, y + bottomH / 2),
  );
  // Return to the hypothesis stage through a lane outside every panel.
  svg += edge(
    'iteration-hypothesis',
    k.path(`M944 ${y + bottomH / 2} H976 V${24 + topH / 2} H944`),
  );
  const loopH = k.height(35, 384, { size: 14, bold: true });
  svg += k.label(35, 532, y + bottomH + 20, 384, loopH, {
    size: 14,
    bold: true,
  });
  const footer = panel(
    k,
    24,
    y + bottomH + 40 + loopH,
    912,
    [row(36, { bold: true })],
    { name: 'methodology', fill: '#d0d0d0' },
  );
  return k.svg(svg + footer.svg, y + bottomH + 40 + loopH + footer.h + 24);
}
