// Web-only reflows for Chapter 9's trajectory-verification and capability-
// update figures. The tracked SVGs remain the source of every localized label
// and stay available through the original-image link.

import { palettes } from './figure-style.mjs';

const palette = palettes.light;

function normalizeLabel(value) {
  return value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// A few translated source SVGs use adjacent text elements as authored line
// fragments. Join only elements with no separating whitespace so each logical
// label keeps the same slot across editions.
function semanticLabels(source) {
  const matches = [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ];
  const labels = [];
  for (let index = 0; index < matches.length; index += 1) {
    let value = normalizeLabel(matches[index][1]);
    while (
      index + 1 < matches.length &&
      source.slice(
        matches[index].index + matches[index][0].length,
        matches[index + 1].index,
      ) === ''
    ) {
      index += 1;
      value = normalizeLabel(`${value} ${matches[index][1]}`);
    }
    labels.push(value);
  }
  return labels;
}

function extractLabels(source, figure, expectedLabels, expectedShape) {
  const labels = semanticLabels(source);
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
    { size = 18, weight = 400, align = 'center', muted = false } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.32;color:${muted ? palette.muted : palette.ink};overflow-wrap:anywhere;word-break:normal;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%;unicode-bidi:plaintext">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (
    x,
    y,
    width,
    height,
    { fill = palette.panel, rx = 8, extra = '' } = {},
  ) =>
    `<rect${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="${palette.line}" stroke-width="2"/>`;
  const arrow = (edge, d) =>
    `<path data-edge="${edge}" d="${d}" fill="none" stroke="${palette.muted}" stroke-width="2.5" marker-end="url(#evolution-methods-arrow)"/>`;
  return { label, card, arrow };
}

const definitions = `<defs>
  <marker id="evolution-methods-arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="${palette.muted}"/></marker>
</defs>`;

export function layoutTrajectoryVerification(source) {
  const labels = extractLabels(source, '9-2', 21, {
    rect: 5,
    line: 2,
    path: 5,
    marker: 1,
  });
  const { label, card, arrow } = helpers(labels);
  const verifiers = [
    {
      kind: 'rubric',
      position: 'top',
      indices: [5, 6],
      y: 100,
      fill: palette.strong,
    },
    {
      kind: 'process',
      position: 'middle',
      indices: [3, 4],
      y: 330,
      fill: palette.panel,
    },
    {
      kind: 'outcome',
      position: 'bottom',
      indices: [1, 2],
      y: 560,
      fill: palette.panel,
    },
  ];
  const fields = [
    { key: 'outcome', indices: [8, 9] },
    { key: 'dimensions', indices: [10, 11] },
    { key: 'evidence', indices: [12, 13] },
    { key: 'failure', indices: [14, 15] },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 820" width="1320" height="820" role="img" aria-labelledby="trajectory-verification-title" style="background:${palette.surface}">
  <title id="trajectory-verification-title">${labels[0]}</title>
  ${definitions}

  ${label(0, 20, 14, 1280, 62, { size: 25, weight: 700 })}

  ${verifiers
    .map(
      ({
        kind,
        position,
        indices,
        y,
        fill,
      }) => `<g data-verifier="${kind}" data-layer-position="${position}" data-labels="${indices.join(' ')}">
    ${card(20, y, 300, 180, { fill, extra: `data-verifier-card="${kind}"` })}
    ${label(indices[0], 42, y + 20, 256, 54, { size: 21, weight: 700 })}
    <line x1="48" y1="${y + 84}" x2="292" y2="${y + 84}" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(indices[1], 42, y + 96, 256, 66, { size: 17, muted: true })}
  </g>`,
    )
    .join('')}

  ${arrow('rubric-to-evaluation', 'M 320 190 H 375 V 218 H 428')}
  ${arrow('process-to-evaluation', 'M 320 420 H 428')}
  ${arrow('outcome-to-evaluation', 'M 320 650 H 375 V 622 H 428')}

  <g data-stage="structured-evaluation" data-labels="7-16">
    ${card(430, 90, 470, 680, { fill: palette.strong, extra: 'data-stage-card="structured-evaluation"' })}
    ${label(7, 458, 108, 414, 62, { size: 23, weight: 700 })}
    <line x1="462" y1="180" x2="868" y2="180" stroke="${palette.line}" stroke-width="1.5"/>
    ${fields
      .map(({ key, indices }, row) => {
        const y = 197 + row * 105;
        return `<g data-evaluation-field="${key}" data-labels="${indices.join(' ')}">
          ${label(indices[0], 466, y, 398, 32, { size: 17, weight: 700, align: 'start' })}
          ${label(indices[1], 466, y + 34, 398, 58, { size: 17, align: 'start' })}
          ${row < fields.length - 1 ? `<line x1="466" y1="${y + 99}" x2="864" y2="${y + 99}" stroke="${palette.line}" stroke-width="1"/>` : ''}
        </g>`;
      })
      .join('')}
    <line x1="462" y1="628" x2="868" y2="628" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(16, 466, 648, 398, 92, { size: 17, weight: 700, muted: true })}
  </g>

  ${arrow('evaluation-to-diagnostic-signal', 'M 900 430 H 1018')}
  <g data-stage="diagnostic-signal" data-labels="17-20">
    ${card(1020, 252, 280, 356, { fill: palette.panel, extra: 'data-stage-card="diagnostic-signal"' })}
    ${label(17, 1042, 260, 236, 90, { size: 22, weight: 700 })}
    <line x1="1048" y1="354" x2="1272" y2="354" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(18, 1042, 370, 236, 62, { size: 17 })}
    ${label(19, 1042, 442, 236, 62, { size: 17 })}
    ${label(20, 1042, 514, 236, 76, { size: 17, muted: true })}
  </g>
</svg>`;
}

export function layoutEvolutionMethods(source) {
  const labels = extractLabels(source, '9-3', 18, {
    rect: 5,
    line: 1,
    path: 1,
    marker: 0,
  });
  const { label, card } = helpers(labels);
  const carriers = [
    {
      kind: 'knowledge',
      first: 1,
      x: 20,
      y: 174,
      fill: palette.panel,
      attribute: 13,
    },
    { kind: 'instructions', first: 4, x: 670, y: 174, fill: palette.panel },
    { kind: 'programs', first: 7, x: 20, y: 414, fill: palette.panel },
    {
      kind: 'parameters',
      first: 10,
      x: 670,
      y: 414,
      fill: palette.strong,
      attribute: 14,
    },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 900" width="1320" height="900" role="img" aria-labelledby="evolution-methods-title" style="background:${palette.surface}">
  <title id="evolution-methods-title">${labels[0]} · ${labels[15]}</title>

  ${label(0, 20, 14, 1280, 64, { size: 25, weight: 700 })}
  ${card(170, 92, 980, 58, { fill: palette.surface, extra: 'data-relationship-note="complementary"' })}
  ${label(15, 198, 100, 924, 42, { size: 21, weight: 700 })}

  ${carriers
    .map(
      ({
        kind,
        first,
        x,
        y,
        fill,
        attribute,
      }) => `<g data-carrier="${kind}" data-relationship="complementary" data-labels="${first} ${first + 1} ${first + 2}${attribute === undefined ? '' : ` ${attribute}`}"${attribute === undefined ? '' : ` data-attached-attribute="${attribute}"`}>
    ${card(x, y, 630, 212, { fill, extra: `data-carrier-card="${kind}"` })}
    ${label(first, x + 24, y + 16, 582, 46, { size: 22, weight: 700 })}
    <line x1="${x + 30}" y1="${y + 72}" x2="${x + 600}" y2="${y + 72}" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(first + 1, x + 28, y + 80, 574, 42, { size: 18 })}
    ${label(first + 2, x + 28, y + 122, 574, 36, { size: 17, weight: 700, muted: true })}
    ${
      attribute === undefined
        ? ''
        : `<line x1="${x + 30}" y1="${y + 162}" x2="${x + 600}" y2="${y + 162}" stroke="${palette.line}" stroke-width="1"/>
    <g data-carrier-attribute="${attribute}" data-attached-to="${kind}">${label(attribute, x + 28, y + 168, 574, 36, { size: 17, weight: 700 })}</g>`
    }
  </g>`,
    )
    .join('')}

  <g data-deployment-question="true" data-labels="16 17">
    ${card(20, 662, 1280, 210, { fill: palette.strong, extra: 'data-deployment-card="true"' })}
    ${label(16, 54, 680, 1212, 78, { size: 21, weight: 700 })}
    <line x1="60" y1="770" x2="1260" y2="770" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(17, 54, 784, 1212, 70, { size: 17, muted: true })}
  </g>
</svg>`;
}
