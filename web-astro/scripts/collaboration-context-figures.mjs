// Web-only reflows for Chapter 10's collaboration-context figures. The
// tracked SVGs remain the source of every localized label and are not edited.

import { palettes } from './figure-style.mjs';

const palette = palettes.light;

function normalizeLabel(value) {
  return value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function sourceLabels(source) {
  return [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((match) => normalizeLabel(match[1]));
}

function extractLabels(source, figure, expected) {
  const labels = sourceLabels(source);
  const count = (tag) =>
    (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
  const shapeMatches = Object.entries(expected.shape).every(
    ([tag, wanted]) => count(tag) === wanted,
  );
  const empty = labels
    .map((label, index) => (label ? -1 : index))
    .filter((index) => index >= 0);

  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !source.includes(`viewBox="${expected.viewBox}"`) ||
    labels.length !== expected.labels ||
    !shapeMatches ||
    empty.join(' ') !== (expected.empty || []).join(' ')
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
    {
      size = 17,
      weight = 400,
      align = 'center',
      muted = false,
      inverse = false,
      family = 'sans',
      extra = '',
    } = {},
  ) => `<foreignObject data-source-label="${index}"${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:${family === 'mono' ? "'SFMono-Regular',Consolas,'Liberation Mono',monospace" : "Arial,'Helvetica Neue',Helvetica,sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.3;color:${inverse ? palette.inverse : muted ? palette.muted : palette.ink};overflow-wrap:anywhere;word-break:normal;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%;unicode-bidi:plaintext">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (
    x,
    y,
    width,
    height,
    { fill = palette.panel, rx = 8, dash = '', extra = '' } = {},
  ) =>
    `<rect${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="${palette.line}" stroke-width="2"${dash ? ` stroke-dasharray="${dash}"` : ''}/>`;
  const edge = (name, from, to, d, { muted = false, dashed = false } = {}) =>
    `<path data-edge="${name}" data-from="${from}" data-to="${to}" data-route="gutter" d="${d}" fill="none" stroke="${muted ? palette.muted : palette.ink}" stroke-width="2.5"${dashed ? ' stroke-dasharray="7 6"' : ''} marker-end="url(#collaboration-context-arrow)"/>`;
  const separator = (x1, y1, x2, y2) =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${palette.line}" stroke-width="1.5"/>`;
  return { label, card, edge, separator };
}

const definitions = `<defs>
  <marker id="collaboration-context-arrow" markerWidth="11" markerHeight="9" refX="10" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 11 4.5, 0 9" fill="${palette.ink}"/></marker>
</defs>`;

export function layoutSharedContextComparison(source) {
  const labels = extractLabels(source, '10-1', {
    labels: 37,
    viewBox: '0 40 780 520',
    shape: {
      text: 37,
      rect: 10,
      line: 0,
      path: 0,
      polyline: 0,
      marker: 2,
      polygon: 2,
      g: 8,
    },
  });
  const { label, card, separator } = helpers(labels);
  const sharedPhases = [
    { key: 'requirements', title: 1, details: [2, 3, 4, 5], y: 132 },
    { key: 'engineering', title: 6, details: [7, 8, 9, 10], y: 412 },
    { key: 'review', title: 11, details: [12, 13, 14, 15], y: 692 },
  ];
  const isolatedAgents = [
    { key: 'glossary', title: 20, details: [21, 22, 23], y: 132 },
    { key: 'translation', title: 24, details: [25, 26, 27], y: 352 },
    { key: 'proofreading', title: 28, details: [29, 30, 31], y: 572 },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1260" width="1320" height="1260" role="img" aria-labelledby="shared-context-comparison-title" style="background:${palette.surface}">
  <title id="shared-context-comparison-title">${labels[0]} · ${labels[19]}</title>

  <g data-collaboration-model="shared-context" data-labels="0-18">
    ${card(20, 20, 630, 1220, { fill: palette.surface, dash: '9 6', extra: 'data-model-panel="shared-context"' })}
    ${label(0, 52, 42, 566, 68, { size: 23, weight: 700 })}
    ${sharedPhases
      .map(
        ({
          key,
          title,
          details,
          y,
        }) => `<g data-phase="${key}" data-labels="${title} ${details.join(' ')}">
      ${card(42, y, 586, 260, { fill: title === 1 ? palette.strong : palette.panel, extra: `data-phase-card="${key}"` })}
      ${label(title, 66, y + 14, 538, 52, { size: 20, weight: 700, align: 'start' })}
      ${separator(68, y + 74, 602, y + 74)}
      ${details.map((index, row) => label(index, 68, y + 84 + row * 42, 534, 40, { size: 16, align: 'start', family: 'mono', muted: row === 0 })).join('')}
    </g>`,
      )
      .join('')}
    ${card(42, 972, 586, 84, { fill: palette.strong, extra: 'data-shared-history="true"' })}
    ${label(16, 66, 986, 538, 56, { size: 18, weight: 700 })}
    ${label(17, 66, 1080, 538, 52, { size: 18, weight: 700 })}
    ${label(18, 66, 1140, 538, 74, { size: 17, muted: true })}
  </g>

  <g data-collaboration-model="isolated-context" data-labels="19-36">
    ${card(670, 20, 630, 1220, { fill: palette.surface, dash: '9 6', extra: 'data-model-panel="isolated-context"' })}
    ${label(19, 702, 42, 566, 68, { size: 23, weight: 700 })}
    ${isolatedAgents
      .map(
        ({
          key,
          title,
          details,
          y,
        }) => `<g data-isolated-agent="${key}" data-labels="${title} ${details.join(' ')}">
      ${card(692, y, 586, 200, { fill: palette.panel, extra: `data-isolated-card="${key}"` })}
      ${label(title, 716, y + 12, 538, 44, { size: 20, weight: 700, align: 'start' })}
      ${separator(718, y + 62, 1252, y + 62)}
      ${details.map((index, row) => label(index, 718, y + 68 + row * 42, 534, 40, { size: 16, align: 'start', family: 'mono', muted: row === 0 })).join('')}
    </g>`,
      )
      .join('')}
    <g data-shared-file-system="true" data-labels="32 33 34">
      ${card(692, 792, 586, 210, { fill: palette.strong, extra: 'data-shared-file-system-card="true"' })}
      ${label(32, 716, 808, 538, 50, { size: 20, weight: 700 })}
      ${separator(718, 866, 1252, 866)}
      ${label(33, 718, 876, 534, 58, { size: 16, family: 'mono' })}
      ${label(34, 718, 940, 534, 46, { size: 16, muted: true })}
    </g>
    ${label(35, 716, 1040, 538, 54, { size: 18, weight: 700 })}
    ${label(36, 716, 1110, 538, 90, { size: 17, muted: true })}
  </g>
</svg>`;
}

export function layoutVirtualFilesystemMounts(source) {
  const labels = extractLabels(source, '10-2', {
    labels: 35,
    viewBox: '0 40 780 460',
    shape: {
      text: 35,
      rect: 10,
      line: 10,
      path: 0,
      polyline: 1,
      marker: 2,
      polygon: 2,
      g: 0,
    },
  });
  const { label, card, edge, separator } = helpers(labels);
  const regions = [
    { key: 'private', first: 8, last: 14, x: 20, fill: palette.panel },
    { key: 'shared', first: 15, last: 20, x: 340, fill: palette.strong },
    { key: 'external', first: 21, last: 26, x: 660, fill: palette.panel },
    { key: 'system', first: 27, last: 32, x: 980, fill: palette.panel },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1010" width="1320" height="1010" role="img" aria-labelledby="virtual-filesystem-title" style="background:${palette.surface}">
  <title id="virtual-filesystem-title">${labels[2]}</title>
  ${definitions}

  <g data-actor="agents" data-labels="0 1">
    ${card(20, 40, 230, 60, { extra: 'data-actor-card="agent-a"' })}
    ${label(0, 42, 50, 186, 40, { size: 19, weight: 700 })}
    ${card(20, 130, 230, 60, { extra: 'data-actor-card="agent-b"' })}
    ${label(1, 42, 140, 186, 40, { size: 19, weight: 700 })}
  </g>
  <g data-node="virtual-filesystem" data-labels="2 3">
    ${card(460, 40, 400, 175, { fill: palette.strong, extra: 'data-root-card="true"' })}
    ${label(2, 486, 52, 348, 76, { size: 22, weight: 700 })}
    ${separator(490, 136, 830, 136)}
    ${label(3, 486, 146, 348, 54, { size: 16, family: 'mono', muted: true })}
  </g>
  <g data-actor="user" data-labels="4 5">
    ${card(1060, 40, 240, 150, { fill: palette.surface, extra: 'data-actor-card="user"' })}
    ${label(4, 1084, 58, 192, 48, { size: 20, weight: 700 })}
    ${label(5, 1084, 118, 192, 48, { size: 17, muted: true })}
  </g>

  ${edge('agent-a-to-root', 'agent-a', 'virtual-filesystem', 'M 250 70 H 460')}
  ${edge('agent-b-to-root', 'agent-b', 'virtual-filesystem', 'M 250 160 H 360 V 140 H 460')}
  ${edge('root-to-private', 'virtual-filesystem', 'private', 'M 660 215 V 290 H 170 V 370', { muted: true })}
  ${edge('root-to-shared', 'virtual-filesystem', 'shared', 'M 660 215 V 290 H 490 V 370', { muted: true })}
  ${edge('root-to-external', 'virtual-filesystem', 'external', 'M 660 215 V 290 H 810 V 370', { muted: true })}
  ${edge('root-to-system', 'virtual-filesystem', 'system', 'M 660 215 V 290 H 1130 V 370', { muted: true })}
  ${edge('user-to-shared', 'user', 'shared', 'M 1180 190 H 1290 V 830 H 490 V 780', { dashed: true })}
  ${label(6, 1080, 220, 180, 50, { size: 16, muted: true, extra: 'data-edge-label="user-to-shared"' })}
  ${label(7, 520, 296, 280, 48, { size: 17, weight: 700, muted: true, extra: 'data-edge-label="mount-fanout"' })}

  ${regions
    .map(({ key, first, last, x, fill }) => {
      const details = Array.from(
        { length: last - first - 2 },
        (_, index) => first + 3 + index,
      );
      const detailHeight = key === 'private' ? 53 : 70;
      return `<g data-region="${key}" data-labels="${first}-${last}">
      ${card(x, 370, 300, 410, { fill, extra: `data-region-card="${key}"` })}
      ${label(first, x + 22, 388, 256, 66, { size: 20, weight: 700 })}
      ${label(first + 1, x + 22, 464, 256, 46, { size: 17, family: 'mono', weight: 700 })}
      ${label(first + 2, x + 22, 514, 256, 38, { size: 16, muted: true })}
      ${separator(x + 24, 562, x + 276, 562)}
      ${details.map((index, row) => label(index, x + 22, 572 + row * detailHeight, 256, detailHeight - 4, { size: 16, weight: row === details.length - 1 ? 700 : 400, muted: row === details.length - 1 })).join('')}
    </g>`;
    })
    .join('')}

  <g data-external-source="true" data-labels="33 34">
    ${card(660, 855, 300, 130, { fill: palette.surface, dash: '7 5', extra: 'data-external-source-card="true"' })}
    ${label(33, 682, 870, 256, 42, { size: 17, muted: true })}
    ${label(34, 682, 920, 256, 46, { size: 18, weight: 700 })}
  </g>
  ${edge('external-source-to-external', 'external-source', 'external', 'M 810 855 V 780')}
</svg>`;
}

export function layoutProposerReviewerLoop(source) {
  const labels = extractLabels(source, '10-3', {
    labels: 37,
    empty: [6],
    viewBox: '0 40 780 490',
    shape: {
      text: 37,
      rect: 10,
      line: 4,
      path: 0,
      polyline: 0,
      marker: 2,
      polygon: 2,
      g: 0,
    },
  });
  const { label, card, edge, separator } = helpers(labels);
  const rounds = [
    { key: 'round-1', first: 23, x: 40, fill: palette.panel },
    { key: 'round-2', first: 26, x: 470, fill: palette.panel },
    { key: 'round-3', first: 29, x: 900, fill: palette.strong },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1090" width="1320" height="1090" role="img" aria-labelledby="proposer-reviewer-title" style="background:${palette.surface}">
  <title id="proposer-reviewer-title">${labels[0]} · ${labels[11]} · ${labels[22]}</title>
  ${definitions}

  <g data-agent="proposer" data-labels="0-10">
    ${card(20, 30, 500, 470, { fill: palette.panel, extra: 'data-agent-card="proposer"' })}
    ${label(0, 48, 48, 444, 48, { size: 23, weight: 700 })}
    ${label(1, 48, 106, 444, 54, { size: 17, muted: true })}
    ${card(45, 174, 450, 225, { fill: palette.surface, extra: 'data-proposer-artifact="true"' })}
    ${Array.from({ length: 8 }, (_, row) => label(2 + row, 66, 184 + row * 23, 408, row === 7 ? 42 : 23, { size: 16, family: 'mono', align: 'start', extra: `data-artifact-line="${row}"` })).join('')}
    ${label(10, 48, 410, 444, 70, { size: 16, weight: 700, muted: true })}
  </g>

  <g data-agent="reviewer" data-labels="11-19">
    ${card(800, 30, 500, 470, { fill: palette.strong, extra: 'data-agent-card="reviewer"' })}
    ${label(11, 828, 48, 444, 48, { size: 23, weight: 700 })}
    ${card(825, 112, 450, 88, { fill: palette.surface, extra: 'data-review-stage="render-and-evaluate"' })}
    ${label(12, 846, 120, 408, 34, { size: 17, align: 'start' })}
    ${label(13, 846, 158, 408, 34, { size: 17, align: 'start' })}
    ${card(825, 218, 450, 170, { fill: palette.surface, extra: 'data-review-stage="structured-feedback"' })}
    ${label(14, 846, 228, 408, 34, { size: 18, weight: 700, align: 'start' })}
    ${separator(848, 266, 1252, 266)}
    ${Array.from({ length: 4 }, (_, row) => label(15 + row, 846, 272 + row * 27, 408, 27, { size: 16, family: 'mono', align: 'start' })).join('')}
    ${label(19, 828, 404, 444, 70, { size: 16, weight: 700, muted: true })}
  </g>

  ${edge('proposer-to-reviewer', 'proposer', 'reviewer', 'M 520 175 H 800')}
  ${label(20, 548, 122, 224, 42, { size: 18, weight: 700, extra: 'data-edge-label="proposer-to-reviewer"' })}
  ${edge('reviewer-to-proposer', 'reviewer', 'proposer', 'M 800 345 H 520')}
  ${label(21, 548, 356, 224, 46, { size: 18, weight: 700, extra: 'data-edge-label="reviewer-to-proposer"' })}

  <g data-process="iterative-improvement" data-labels="22-31">
    ${card(20, 540, 1280, 290, { fill: palette.surface, extra: 'data-iteration-panel="true"' })}
    ${label(22, 48, 558, 1224, 52, { size: 22, weight: 700 })}
    ${rounds
      .map(
        ({
          key,
          first,
          x,
          fill,
        }) => `<g data-round="${key}" data-labels="${first} ${first + 1} ${first + 2}">
      ${card(x, 640, 380, 156, { fill, extra: `data-round-card="${key}"` })}
      ${label(first, x + 24, 654, 332, 42, { size: 20, weight: 700, align: 'start' })}
      ${separator(x + 26, 704, x + 354, 704)}
      ${label(first + 1, x + 24, 714, 332, 42, { size: 17, align: 'start' })}
      ${label(first + 2, x + 24, 758, 332, 28, { size: 17, weight: 700, align: 'start', muted: first !== 29 })}
    </g>`,
      )
      .join('')}
    ${edge('round-1-to-round-2', 'round-1', 'round-2', 'M 420 718 H 470', { muted: true })}
    ${edge('round-2-to-round-3', 'round-2', 'round-3', 'M 850 718 H 900', { muted: true })}
  </g>

  <g data-comparison="single-vs-dual-agent" data-labels="32-36">
    ${card(20, 860, 1280, 210, { fill: palette.panel, extra: 'data-context-cost-panel="true"' })}
    ${label(32, 48, 876, 1224, 48, { size: 22, weight: 700 })}
    ${separator(660, 936, 660, 1048)}
    ${label(33, 56, 942, 570, 44, { size: 17, weight: 700, align: 'start', muted: true })}
    ${label(34, 56, 992, 570, 48, { size: 16, align: 'start', muted: true })}
    ${label(35, 694, 942, 570, 44, { size: 17, weight: 700, align: 'start' })}
    ${label(36, 694, 992, 570, 48, { size: 16, align: 'start' })}
  </g>
</svg>`;
}

export function layoutManagerSequentialCoordination(source) {
  const labels = extractLabels(source, '10-4', {
    labels: 27,
    viewBox: '0 40 780 455',
    shape: {
      text: 27,
      rect: 8,
      line: 5,
      path: 0,
      polyline: 0,
      marker: 2,
      polygon: 2,
      g: 0,
    },
  });
  const { label, card, edge, separator } = helpers(labels);
  const agents = [
    { key: 'agent-a', first: 4, x: 20 },
    { key: 'agent-b', first: 9, x: 460 },
    { key: 'agent-c', first: 14, x: 900 },
  ];
  const sequenceX = [40, 250, 460, 670, 880, 1090];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 920" width="1320" height="920" role="img" aria-labelledby="manager-sequential-title" style="background:${palette.surface}">
  <title id="manager-sequential-title">${labels[0]} · ${labels[19]}</title>
  ${definitions}

  <g data-manager="true" data-labels="0-3">
    ${card(300, 30, 720, 220, { fill: palette.strong, extra: 'data-manager-card="true"' })}
    ${label(0, 336, 48, 648, 54, { size: 24, weight: 700 })}
    ${label(1, 336, 112, 648, 48, { size: 18, weight: 700, muted: true })}
    ${separator(340, 168, 980, 168)}
    ${label(2, 336, 176, 648, 30, { size: 16, family: 'mono' })}
    ${label(3, 336, 208, 648, 30, { size: 16, family: 'mono' })}
  </g>

  ${edge('manager-to-agent-a', 'manager', 'agent-a', 'M 420 250 V 310 H 220 V 390', { muted: true })}
  ${edge('manager-to-agent-b', 'manager', 'agent-b', 'M 660 250 V 390', { muted: true })}
  ${edge('manager-to-agent-c', 'manager', 'agent-c', 'M 900 250 V 310 H 1100 V 390', { muted: true })}

  ${agents
    .map(
      ({
        key,
        first,
        x,
      }) => `<g data-sub-agent="${key}" data-step="${(first - 4) / 5 + 1}" data-labels="${first}-${first + 4}">
    ${card(x, 390, 400, 280, { fill: palette.panel, extra: `data-sub-agent-card="${key}"` })}
    ${label(first, x + 26, 408, 348, 48, { size: 22, weight: 700 })}
    ${label(first + 1, x + 26, 464, 348, 50, { size: 18, weight: 700, muted: true })}
    ${separator(x + 28, 522, x + 372, 522)}
    ${label(first + 2, x + 26, 534, 348, 44, { size: 17 })}
    ${label(first + 3, x + 26, 582, 348, 44, { size: 17 })}
    ${card(x + 274, 630, 100, 28, { fill: palette.muted, rx: 14, extra: `data-step-chip="${(first - 4) / 5 + 1}"` })}
    ${label(first + 4, x + 280, 632, 88, 24, { size: 16, weight: 700, inverse: true, extra: 'data-inverse-label="true"' })}
  </g>`,
    )
    .join('')}

  ${edge('agent-a-to-agent-b', 'agent-a', 'agent-b', 'M 420 530 H 460')}
  ${edge('agent-b-to-agent-c', 'agent-b', 'agent-c', 'M 860 530 H 900')}

  <g data-sequential-flow="true" data-labels="19-26">
    ${card(20, 710, 1280, 190, { fill: palette.surface, extra: 'data-sequential-flow-card="true"' })}
    ${label(19, 48, 724, 1224, 48, { size: 22, weight: 700 })}
    ${sequenceX.map((x, index) => label(20 + index, x, 786, 185, 54, { size: 16, weight: index % 2 === 0 ? 700 : 400, muted: index % 2 === 1, extra: `data-sequence-index="${index + 1}"` })).join('')}
    ${label(26, 48, 850, 1224, 36, { size: 17, weight: 700, muted: true })}
  </g>
</svg>`;
}
