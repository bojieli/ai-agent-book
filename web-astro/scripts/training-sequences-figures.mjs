// Web-only reflows for Chapter 8's turn comparison and credit-assignment
// sequence. The tracked source SVGs remain the source of every localized
// label and are left untouched.

import { palettes } from './figure-style.mjs';

const palette = palettes.light;

function extractLabels(source, figure, expectedLabels, expectedShape) {
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
  const count = (tag) =>
    (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
  const validShape = Object.entries(expectedShape).every(
    ([tag, expected]) => count(tag) === expected,
  );

  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    labels.length !== expectedLabels ||
    labels.some((label) => !label || /<[^>]+>/.test(label)) ||
    !validShape
  )
    throw new Error(
      `Figure ${figure} source structure changed; review its web layout.`,
    );

  return labels;
}

function helpers(labels) {
  const label = (
    index,
    x,
    y,
    width,
    height,
    { size = 17, weight = 400, align = 'center', muted = false } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.3;color:${muted ? palette.muted : palette.ink};overflow-wrap:anywhere;word-break:normal;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%;unicode-bidi:plaintext">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (
    x,
    y,
    width,
    height,
    { fill = palette.panel, dash = false, rx = 8, extra = '' } = {},
  ) =>
    `<rect${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="${palette.line}" stroke-width="2"${dash ? ' stroke-dasharray="8,6"' : ''}/>`;
  const arrow = (transition, x1, y1, x2, y2) =>
    `<line data-transition="${transition}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${palette.muted}" stroke-width="2.5" marker-end="url(#training-sequence-arrow)"/>`;
  return { label, card, arrow };
}

const definitions = `<defs>
  <marker id="training-sequence-arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="${palette.muted}"/></marker>
</defs>`;

export function layoutTurnComparison(source) {
  const labels = extractLabels(source, '8-14', 26, {
    text: 26,
    rect: 2,
    line: 0,
    path: 0,
    polygon: 2,
    marker: 2,
  });
  const { label, card } = helpers(labels);
  const turnPanel = (
    kind,
    first,
    x,
    fill,
  ) => `<g data-turn="${kind}" data-labels="${first}-${first + 6}">
    ${card(x, 20, 590, 370, { fill, dash: true })}
    ${label(first, x + 24, 34, 542, 44, { size: 22, weight: 700, align: 'start', muted: true })}
    ${label(first + 1, x + 24, 80, 542, 58, { size: 21, weight: 700 })}
    <line x1="${x + 24}" y1="145" x2="${x + 566}" y2="145" stroke="${palette.line}" stroke-width="1.5"/>
    ${[first + 2, first + 3, first + 4, first + 5]
      .map((index, row) =>
        label(index, x + 28, 151 + row * 42, 534, 38, {
          size: 17,
          align: 'start',
          muted: true,
        }),
      )
      .join('')}
    ${label(first + 6, x + 28, 322, 534, 54, { size: 17, weight: 700, muted: true })}
  </g>`;
  const comparisons = [
    { key: 'credit-assignment', labels: [14, 15, 16] },
    { key: 'state-management', labels: [17, 18, 19] },
    { key: 'reward-design', labels: [20, 21, 22] },
    { key: 'exploration-cost', labels: [23, 24, 25] },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 784" width="1240" height="784" role="img" aria-labelledby="turn-comparison-title" style="background:${palette.surface}">
  <title id="turn-comparison-title">${labels[0]} · ${labels[7]} · ${labels[14]}</title>
  ${definitions}

  ${turnPanel('single', 0, 20, palette.surface)}
  ${turnPanel('multi', 7, 630, palette.panel)}

  ${comparisons
    .map(({ key, labels: indices }, row) => {
      const y = 414 + row * 90;
      return `<g data-comparison="${key}" data-labels="${indices.join(' ')}">
        ${card(20, y, 1200, 78, { fill: row % 2 ? palette.surface : palette.panel })}
        <rect x="20" y="${y}" width="240" height="78" rx="8" fill="${palette.strong}"/>
        <line x1="260" y1="${y + 12}" x2="260" y2="${y + 66}" stroke="${palette.line}" stroke-width="1.5"/>
        <line x1="740" y1="${y + 12}" x2="740" y2="${y + 66}" stroke="${palette.line}" stroke-width="1.5"/>
        ${label(indices[0], 40, y + 9, 200, 60, { size: 18, weight: 700 })}
        ${label(indices[1], 282, y + 9, 436, 60, { size: 17 })}
        ${label(indices[2], 762, y + 9, 436, 60, { size: 17 })}
      </g>`;
    })
    .join('')}
</svg>`;
}

export function layoutCreditAssignment(source) {
  const labels = extractLabels(source, '8-15', 28, {
    text: 28,
    rect: 8,
    line: 4,
    path: 0,
    polygon: 2,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const stepXs = [20, 288, 556, 824, 1092];
  const stepFills = [
    palette.panel,
    palette.panel,
    palette.strong,
    palette.panel,
    palette.strong,
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 742" width="1320" height="742" role="img" aria-labelledby="credit-assignment-title" style="background:${palette.surface}">
  <title id="credit-assignment-title">${labels[20]}</title>
  ${definitions}

  ${stepXs
    .map((x, step) => {
      const first = step * 4;
      return `<g data-step="${step + 1}" data-labels="${first} ${first + 1} ${first + 2} ${first + 3}">
        ${card(x, 20, 208, 246, {
          fill: stepFills[step],
          extra: `data-step-card="${step + 1}"`,
        })}
        ${label(first, x + 16, 32, 176, 42, { size: 21, weight: 700 })}
        <line x1="${x + 18}" y1="80" x2="${x + 190}" y2="80" stroke="${palette.line}" stroke-width="1.5"/>
        ${label(first + 1, x + 16, 88, 176, 48, { size: 17, muted: true })}
        ${label(first + 2, x + 16, 140, 176, 64, { size: 17 })}
        ${label(first + 3, x + 16, 211, 176, 40, { size: 19, weight: 700, muted: step === 2 })}
      </g>`;
    })
    .join('')}
  ${stepXs
    .slice(0, -1)
    .map((x, step) =>
      arrow(`${step + 1}-${step + 2}`, x + 212, 143, stepXs[step + 1] - 6, 143),
    )
    .join('')}

  <g data-credit-question="true" data-labels="20 21">
    ${card(20, 294, 1280, 164, { fill: palette.surface })}
    ${label(20, 52, 310, 1216, 52, { size: 23, weight: 700 })}
    <line x1="52" y1="371" x2="1268" y2="371" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(21, 52, 380, 1216, 62, { size: 18, muted: true })}
  </g>

  <g data-reward-approach="process" data-labels="22 23 24">
    ${card(20, 486, 630, 236, { fill: palette.panel })}
    ${label(22, 44, 500, 582, 48, { size: 21, weight: 700 })}
    <line x1="44" y1="558" x2="626" y2="558" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(23, 48, 568, 574, 58, { size: 18 })}
    ${label(24, 48, 636, 574, 68, { size: 17, muted: true })}
  </g>
  <g data-reward-approach="outcome" data-labels="25 26 27">
    ${card(670, 486, 630, 236, { fill: palette.strong })}
    ${label(25, 694, 500, 582, 48, { size: 21, weight: 700 })}
    <line x1="694" y1="558" x2="1276" y2="558" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(26, 698, 568, 574, 58, { size: 18 })}
    ${label(27, 698, 636, 574, 68, { size: 17, muted: true })}
  </g>
</svg>`;
}
