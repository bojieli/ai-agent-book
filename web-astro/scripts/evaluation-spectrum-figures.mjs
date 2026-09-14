// Web-only reflows for the Chapter 7 verification spectrum and simulation
// fidelity chart. Every visible content label comes from the localized SVG.

import { figureKit } from './chapter3-figure-kit.mjs';

const specifications = {
  4: { labels: 24, rect: 6, circle: 0, line: 4, path: 0, marker: 2 },
  9: { labels: 28, rect: 0, circle: 6, line: 3, path: 0, marker: 2 },
};

const count = (source, tag) =>
  (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;

function sourceLabels(source, figure) {
  const specification = specifications[figure];
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !['rect', 'circle', 'line', 'path', 'marker'].every(
      (tag) => count(source, tag) === specification[tag],
    )
  )
    throw new Error(
      `Figure 7-${figure} source structure changed; review its web layout.`,
    );

  const labels = [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((match) =>
    match[1]
      .replace(/<tspan\b[^>]*>/g, '')
      .replace(/<\/tspan>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  );
  if (
    labels.length !== specification.labels ||
    labels.some((label) => /<[^>]+>/.test(label))
  )
    throw new Error(
      `Figure 7-${figure} source labels changed; review its web layout.`,
    );
  return labels;
}

export function layoutVerificationSpectrum(source, { rtl = false } = {}) {
  const labels = sourceLabels(source, 4);
  const kit = figureKit(labels, { rtl });
  const cardWidth = 202;
  const cardXs = [24, 274, 524, 774];
  const innerWidth = cardWidth - 40;
  const axisHeight = Math.max(
    kit.height(0, 760, { size: 20, bold: true }),
    kit.height(1, 160, { size: 20, bold: true }),
  );
  const axisY = 24;
  const lineY = axisY + axisHeight + 12;
  const cardY = lineY + 24;
  const titleHeight = Math.max(
    ...[2, 6, 10, 14].map((id) =>
      kit.height(id, innerWidth, { size: 18, bold: true }),
    ),
  );
  const bodyHeights = [0, 1, 2].map((row) =>
    Math.max(
      ...[3 + row, 7 + row, 11 + row, 15 + row].map((id) =>
        kit.height(id, innerWidth, { size: 16, min: 28 }),
      ),
    ),
  );
  const cardHeight =
    18 + titleHeight + 14 + bodyHeights.reduce((sum, h) => sum + h, 0) + 48;

  const stages = [2, 6, 10, 14]
    .map((title, stage) => {
      const x = cardXs[stage];
      let cursor = cardY + 18;
      let result = `<g data-spectrum-stage="${stage}">${kit.card(x, cardY, cardWidth, cardHeight)}`;
      result += kit.label(title, x + 20, cursor, innerWidth, titleHeight, {
        size: 18,
        bold: true,
      });
      cursor += titleHeight + 14;
      for (let row = 0; row < 3; row++) {
        result += kit.label(
          title + row + 1,
          x + 20,
          cursor,
          innerWidth,
          bodyHeights[row],
          { size: 16 },
        );
        cursor += bodyHeights[row] + 12;
      }
      return `${result}</g>`;
    })
    .join('');

  const edges = cardXs
    .slice(0, -1)
    .map((x, stage) => {
      const start = x + cardWidth + 8;
      const end = cardXs[stage + 1] - 8;
      const y = cardY + cardHeight / 2;
      return `<g data-spectrum-edge="${stage}-${stage + 1}" data-start-x="${start}" data-end-x="${end}">${kit.arrow(start, y, end, y)}</g>`;
    })
    .join('');

  const summaryY = cardY + cardHeight + 32;
  const summaryWidth = 464;
  const summaryInner = summaryWidth - 40;
  const summaryTitleHeight = Math.max(
    ...[18, 21].map((id) =>
      kit.height(id, summaryInner, { size: 18, bold: true }),
    ),
  );
  const summaryBodyHeight = Math.max(
    ...[19, 22].map((id) => kit.height(id, summaryInner, { size: 16 })),
  );
  const summaryCaptionHeight = Math.max(
    ...[20, 23].map((id) =>
      kit.height(id, summaryInner, { size: 14, min: 25 }),
    ),
  );
  const summaryHeight =
    18 +
    summaryTitleHeight +
    10 +
    summaryBodyHeight +
    8 +
    summaryCaptionHeight +
    18;
  const summaries = [18, 21]
    .map((title, summary) => {
      const x = summary === 0 ? 24 : 512;
      let cursor = summaryY + 18;
      return `<g data-spectrum-summary="${summary}">
        ${kit.card(x, summaryY, summaryWidth, summaryHeight, { fill: '#f3f0e8' })}
        ${kit.label(title, x + 20, cursor, summaryInner, summaryTitleHeight, { size: 18, bold: true })}
        ${kit.label(title + 1, x + 20, (cursor += summaryTitleHeight + 10), summaryInner, summaryBodyHeight, { size: 16 })}
        ${kit.label(title + 2, x + 20, (cursor += summaryBodyHeight + 8), summaryInner, summaryCaptionHeight, { size: 14, muted: true })}
      </g>`;
    })
    .join('');

  const content = `
    ${kit.label(0, 24, axisY, 760, axisHeight, { size: 20, bold: true })}
    ${kit.label(1, 816, axisY, 160, axisHeight, { size: 20, bold: true })}
    <g data-spectrum-axis="true">${kit.arrow(24, lineY, 976, lineY)}</g>
    ${stages}${edges}${summaries}`;
  return kit.svg(content, summaryY + summaryHeight + 24);
}

function chartGeometry(source) {
  const circles = [...source.matchAll(/<circle\b[^>]*>/g)].map(
    ([element], index) => ({
      element: element.replace(
        '<circle',
        `<circle data-chart-point="${index + 1}"`,
      ),
      x: Number(element.match(/\bcx="([^"]+)"/)?.[1]),
      y: Number(element.match(/\bcy="([^"]+)"/)?.[1]),
    }),
  );
  if (
    circles.length !== 6 ||
    circles.some(({ x, y }) => !Number.isFinite(x) || !Number.isFinite(y))
  )
    throw new Error('Figure 7-9 point geometry changed.');
  const trend = source.match(
    /<line\b[^>]*stroke-dasharray="8,4"[^>]*\/\s*>/,
  )?.[0];
  if (!trend) throw new Error('Figure 7-9 trend line missing.');
  return { circles, trend };
}

export function layoutSimulationFidelity(source, { rtl = false } = {}) {
  const labels = sourceLabels(source, 9);
  const { circles, trend } = chartGeometry(source);
  const kit = figureKit(labels, { rtl });
  const xAxisY = 420;
  const xTitleHeight = kit.height(0, 700, { size: 20, bold: true });
  const yTitleHeight = kit.height([1, 2, 3, 4, 5], 760, {
    size: 16,
    bold: true,
  });
  const pointKeys = circles
    .map(
      ({ x, y }, point) =>
        `${kit.card(x + 10, y - 32, 26, 26, { fill: '#ffffff' })}<foreignObject data-point-key="${point + 1}" x="${x + 10}" y="${y - 32}" width="26" height="26"><div xmlns="http://www.w3.org/1999/xhtml" style="box-sizing:border-box;width:100%;font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:700;line-height:26px;color:#333333;text-align:center">${point + 1}</div></foreignObject>`,
    )
    .join('');

  const groups = [
    { title: [6], details: [7, 8] },
    { title: [9, 10], details: [11, 12] },
    { title: [13, 14], details: [15, 16] },
    { title: [17, 18], details: [19, 20] },
    { title: [21, 22], details: [23, 24] },
    { title: [25], details: [26, 27] },
  ];
  const cardWidth = 301;
  const innerWidth = cardWidth - 48;
  const titleHeight = Math.max(
    ...groups.map(({ title }) =>
      kit.height(title, cardWidth - 86, { size: 18, bold: true }),
    ),
  );
  const detailHeight = Math.max(
    ...groups.map(({ details }) =>
      kit.height(details, innerWidth, { size: 14, min: 46 }),
    ),
  );
  const cardHeight = 18 + titleHeight + 10 + detailHeight + 18;
  const cardY = xAxisY + xTitleHeight + 56;
  const cards = groups
    .map(({ title, details }, point) => {
      const x = 24 + (point % 3) * 325.5;
      const y = cardY + Math.floor(point / 3) * (cardHeight + 24);
      return `<g data-fidelity-key="${point + 1}">
        ${kit.card(x, y, cardWidth, cardHeight)}
        <foreignObject data-key-number="${point + 1}" x="${x + 16}" y="${y + 16}" width="28" height="28"><div xmlns="http://www.w3.org/1999/xhtml" style="box-sizing:border-box;width:100%;font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:700;line-height:28px;color:#333333;text-align:center">${point + 1}</div></foreignObject>
        ${kit.label(title, x + 52, y + 18, cardWidth - 70, titleHeight, { size: 18, bold: true, align: 'start' })}
        ${kit.label(details, x + 24, y + 18 + titleHeight + 10, innerWidth, detailHeight, { size: 14, muted: true, align: 'start' })}
      </g>`;
    })
    .join('');
  const totalHeight = cardY + cardHeight * 2 + 24 + 24;
  const content = `
    <g data-chart-axis="x">${kit.arrow(100, xAxisY, 860, xAxisY)}</g>
    <g data-chart-axis="y">${kit.arrow(100, xAxisY, 100, 90)}</g>
    <g data-chart-trend="true">${trend}</g>
    <g data-chart-points="true">${circles.map(({ element }) => element).join('')}</g>
    ${pointKeys}
    ${kit.label([1, 2, 3, 4, 5], 100, 24, 760, yTitleHeight, { size: 16, bold: true })}
    ${kit.label(0, 180, xAxisY + 12, 700, xTitleHeight, { size: 20, bold: true })}
    ${cards}`;
  return kit.svg(content, totalHeight);
}
