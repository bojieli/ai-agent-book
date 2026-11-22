// Web-only reflows for Chapter 10's MetaGPT, generative-agent society,
// and voice-Werewolf figures. The tracked SVGs remain the source of every
// localized label and stay available through the original-image link.

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

function extractLabels(source, figure, expectedLabels, expectedShape) {
  const labels = sourceLabels(source);
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

function helpers(labels, markerId) {
  const label = (
    index,
    x,
    y,
    width,
    height,
    { size = 18, weight = 400, align = 'start', muted = false } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};box-sizing:border-box;font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.3;color:${muted ? palette.muted : palette.ink};overflow-wrap:anywhere;word-break:normal;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%;unicode-bidi:plaintext">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (
    x,
    y,
    width,
    height,
    { fill = palette.panel, rx = 8, extra = '' } = {},
  ) =>
    `<rect${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="${palette.line}" stroke-width="2"/>`;
  const arrow = (edge, d, { dashed = false } = {}) =>
    `<path data-edge="${edge}" d="${d}" fill="none" stroke="${palette.muted}" stroke-width="2.5"${dashed ? ' stroke-dasharray="9 6"' : ''} marker-end="url(#${markerId})"/>`;
  return { label, card, arrow };
}

function definitions(markerId) {
  return `<defs>
  <marker id="${markerId}" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="${palette.muted}"/></marker>
</defs>`;
}

export function layoutMetaGPTCollaboration(source) {
  const labels = extractLabels(source, '10-9', 47, {
    rect: 17,
    line: 4,
    path: 1,
    marker: 2,
    polygon: 2,
  });
  const markerId = 'collaboration-society-arrow';
  const { label, card, arrow } = helpers(labels, markerId);
  const roles = [
    { kind: 'product-manager', first: 0, y: 30, fill: palette.strong },
    { kind: 'architect', first: 7, y: 310, fill: palette.panel },
    { kind: 'project-manager', first: 14, y: 590, fill: palette.panel },
    { kind: 'engineer', first: 21, y: 870, fill: palette.panel },
    { kind: 'qa', first: 28, y: 1150, fill: palette.strong },
  ];
  const edges = [
    ['product-to-architect', 260, 310],
    ['architect-to-project', 540, 590],
    ['project-to-engineer', 820, 870],
    ['engineer-to-qa', 1100, 1150],
  ];
  const insights = [
    { kind: 'documents', indices: [39, 40], x: 70, y: 1700 },
    { kind: 'decoupling', indices: [41, 42], x: 750, y: 1700 },
    { kind: 'control-flow', indices: [43, 44], x: 70, y: 1880 },
    { kind: 'exception-channel', indices: [45, 46], x: 750, y: 1880 },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1480 2080" width="1480" height="2080" role="img" aria-labelledby="metagpt-collaboration-title" style="background:${palette.surface}">
  <title id="metagpt-collaboration-title">${labels[38]}</title>
  ${definitions(markerId)}

  ${roles
    .map(
      (
        { kind, first, y, fill },
        position,
      ) => `<g data-role="${kind}" data-flow-position="${position + 1}" data-labels="${Array.from({ length: 7 }, (_, offset) => first + offset).join(' ')}">
    ${card(120, y, 1120, 230, { fill, extra: `data-role-card="${kind}"` })}
    ${label(first, 150, y + 12, 1060, 48, { size: 23, weight: 700, align: 'center' })}
    <line x1="158" y1="${y + 66}" x2="1202" y2="${y + 66}" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(first + 1, 158, y + 72, 1044, 44, { size: 18, muted: true })}
    ${label(first + 2, 158, y + 122, 150, 38, { size: 18, weight: 700 })}
    ${[first + 3, first + 4, first + 5]
      .map((index, row) =>
        label(index, 326, y + 112 + row * 36, 660, 34, {
          size: 17,
        }),
      )
      .join('')}
    <g data-artifact-for="${kind}">
      ${card(1004, y + 130, 198, 62, { fill: palette.surface })}
      ${label(first + 6, 1018, y + 136, 170, 50, { size: 17, weight: 700, align: 'center' })}
    </g>
  </g>`,
    )
    .join('')}

  ${edges
    .map(([edge, start, end]) => arrow(edge, `M 680 ${start} V ${end - 2}`))
    .join('')}
  ${arrow('qa-to-engineer', 'M 1240 1265 H 1460 V 985 H 1242', { dashed: true })}
  ${label(35, 1262, 1032, 190, 90, { size: 17, weight: 700, align: 'center', muted: true })}

  <g data-shared-directory="true" data-labels="36 37">
    ${card(120, 1430, 1120, 150, { fill: palette.strong, extra: 'data-shared-directory-card="true"' })}
    ${label(36, 154, 1444, 1052, 42, { size: 22, weight: 700, align: 'center' })}
    <line x1="164" y1="1494" x2="1196" y2="1494" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(37, 154, 1504, 1052, 58, { size: 17, align: 'center' })}
  </g>

  <g data-design-principles="true" data-labels="38 39 40 41 42 43 44 45 46">
    ${label(38, 80, 1610, 1280, 58, { size: 25, weight: 700, align: 'center' })}
    ${insights
      .map(
        ({
          kind,
          indices,
          x,
          y,
        }) => `<g data-design-principle="${kind}" data-labels="${indices.join(' ')}">
      ${card(x, y, 610, 154, { fill: palette.panel, extra: `data-principle-card="${kind}"` })}
      ${label(indices[0], x + 24, y + 14, 562, 44, { size: 20, weight: 700 })}
      <line x1="${x + 28}" y1="${y + 64}" x2="${x + 582}" y2="${y + 64}" stroke="${palette.line}" stroke-width="1"/>
      ${label(indices[1], x + 24, y + 72, 562, 66, { size: 17, muted: true })}
    </g>`,
      )
      .join('')}
  </g>
</svg>`;
}

export function layoutAITownArchitecture(source) {
  const labels = extractLabels(source, '10-10', 43, {
    rect: 7,
    line: 2,
    path: 0,
    marker: 2,
    polygon: 2,
  });
  const markerId = 'collaboration-society-arrow';
  const { label, card, arrow } = helpers(labels, markerId);
  const memories = [
    [4, 5],
    [6, 7],
    [8, 9],
    [10, 11],
    [12, 13],
  ];
  const reflections = [
    [15, 16],
    [17, 18],
    [19, 20],
    [21, 22],
  ];
  const plan = [24, 25, 26, 27, 28, 30];
  const behaviors = [
    { kind: 'socializing', indices: [34, 35], x: 100, y: 1970 },
    { kind: 'information', indices: [36, 37], x: 690, y: 1970 },
    { kind: 'election', indices: [38, 39], x: 100, y: 2140 },
    { kind: 'relationships', indices: [40, 41], x: 690, y: 2140 },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 2440" width="1320" height="2440" role="img" aria-labelledby="ai-town-title" style="background:${palette.surface}">
  <title id="ai-town-title">${labels[0]} · ${labels[33]}</title>
  ${definitions(markerId)}

  <g data-agent-profile="isabella" data-labels="0 1 2">
    ${card(100, 30, 1120, 140, { fill: palette.strong, extra: 'data-agent-profile-card="isabella"' })}
    ${label(0, 130, 44, 1060, 46, { size: 24, weight: 700, align: 'center' })}
    ${label(1, 130, 92, 510, 50, { size: 18, weight: 700, align: 'center' })}
    ${label(2, 680, 92, 510, 50, { size: 18, align: 'center', muted: true })}
  </g>

  <g data-agent-component="memory" data-labels="3 4 5 6 7 8 9 10 11 12 13">
    ${card(100, 220, 1120, 490, { fill: palette.panel, extra: 'data-component-card="memory"' })}
    ${label(3, 130, 234, 1060, 50, { size: 23, weight: 700, align: 'center' })}
    <line x1="138" y1="292" x2="1182" y2="292" stroke="${palette.line}" stroke-width="1.5"/>
    ${memories
      .map(
        (
          [event, score],
          row,
        ) => `<g data-memory-entry="${row + 1}" data-labels="${event} ${score}">
      ${label(event, 142, 306 + row * 78, 700, 62, { size: 18 })}
      ${label(score, 870, 306 + row * 78, 306, 62, { size: 17, muted: true })}
      ${row < memories.length - 1 ? `<line x1="146" y1="${376 + row * 78}" x2="1174" y2="${376 + row * 78}" stroke="${palette.line}" stroke-width="1"/>` : ''}
    </g>`,
      )
      .join('')}
  </g>

  ${arrow('memory-to-reflection', 'M 660 710 V 780')}
  ${label(31, 700, 720, 260, 50, { size: 17, weight: 700, muted: true })}

  <g data-agent-component="reflection" data-labels="14 15 16 17 18 19 20 21 22">
    ${card(100, 790, 1120, 430, { fill: palette.strong, extra: 'data-component-card="reflection"' })}
    ${label(14, 130, 804, 1060, 50, { size: 23, weight: 700, align: 'center' })}
    <line x1="138" y1="862" x2="1182" y2="862" stroke="${palette.line}" stroke-width="1.5"/>
    ${reflections
      .map(
        (
          [question, answer],
          row,
        ) => `<g data-reflection-entry="${row + 1}" data-labels="${question} ${answer}">
      ${label(question, 142, 876 + row * 82, 500, 66, { size: 18, weight: 700 })}
      ${label(answer, 674, 876 + row * 82, 502, 66, { size: 17, muted: true })}
      ${row < reflections.length - 1 ? `<line x1="146" y1="${950 + row * 82}" x2="1174" y2="${950 + row * 82}" stroke="${palette.line}" stroke-width="1"/>` : ''}
    </g>`,
      )
      .join('')}
  </g>

  ${arrow('reflection-to-planning', 'M 660 1220 V 1290')}
  ${label(32, 700, 1230, 260, 50, { size: 17, weight: 700, muted: true })}

  <g data-agent-component="planning" data-labels="23 24 25 26 27 28 29 30">
    ${card(100, 1300, 1120, 540, { fill: palette.panel, extra: 'data-component-card="planning"' })}
    ${label(23, 130, 1314, 1060, 50, { size: 23, weight: 700, align: 'center' })}
    <line x1="138" y1="1372" x2="1182" y2="1372" stroke="${palette.line}" stroke-width="1.5"/>
    ${plan
      .map(
        (
          index,
          row,
        ) => `<g data-plan-step="${row + 1}" data-labels="${index}${index === 28 ? ' 29' : ''}">
      ${label(index, 152, 1384 + row * 72, index === 28 ? 700 : 1024, 62, { size: 18 })}
      ${index === 28 ? label(29, 880, 1384 + row * 72, 296, 62, { size: 17, weight: 700, align: 'center', muted: true }) : ''}
      ${row < plan.length - 1 ? `<line x1="156" y1="${1452 + row * 72}" x2="1168" y2="${1452 + row * 72}" stroke="${palette.line}" stroke-width="1"/>` : ''}
    </g>`,
      )
      .join('')}
  </g>

  <g data-emergent-behavior="true" data-labels="33 34 35 36 37 38 39 40 41 42">
    ${label(33, 80, 1880, 1160, 62, { size: 25, weight: 700, align: 'center' })}
    ${behaviors
      .map(
        ({
          kind,
          indices,
          x,
          y,
        }) => `<g data-behavior="${kind}" data-labels="${indices.join(' ')}">
      ${card(x, y, 530, 140, { fill: palette.strong, extra: `data-behavior-card="${kind}"` })}
      ${label(indices[0], x + 22, y + 14, 486, 44, { size: 20, weight: 700 })}
      <line x1="${x + 26}" y1="${y + 64}" x2="${x + 504}" y2="${y + 64}" stroke="${palette.line}" stroke-width="1"/>
      ${label(indices[1], x + 22, y + 72, 486, 52, { size: 17, muted: true })}
    </g>`,
      )
      .join('')}
    ${card(100, 2310, 1120, 100, { fill: palette.surface, extra: 'data-emergence-note="true"' })}
    ${label(42, 130, 2320, 1060, 80, { size: 18, weight: 700, align: 'center', muted: true })}
  </g>
</svg>`;
}

export function layoutVoiceWerewolfSystem(source) {
  const labels = extractLabels(source, '10-11', 48, {
    rect: 11,
    line: 5,
    path: 0,
    marker: 2,
    polygon: 2,
  });
  const markerId = 'collaboration-society-arrow';
  const { label, card, arrow } = helpers(labels, markerId);
  const roles = [
    {
      kind: 'werewolf-1',
      indices: [3, 4, 5, 6],
      badge: 7,
      y: 280,
      fill: palette.red,
    },
    {
      kind: 'werewolf-2',
      indices: [8, 9, 10, 11],
      badge: 12,
      y: 530,
      fill: palette.red,
    },
    {
      kind: 'seer',
      indices: [13, 14, 15, 16],
      badge: 17,
      y: 780,
      fill: palette.blue,
    },
    { kind: 'witch', indices: [18, 19, 20, 21], y: 1030, fill: palette.green },
    {
      kind: 'villager',
      indices: [22, 23, 24, 25],
      y: 1280,
      fill: palette.panel,
    },
  ];
  const access = [
    [27, 28],
    [29, 30],
    [31, 32],
    [33, 34],
  ];
  const phases = [
    { kind: 'discussion', first: 36, x: 100, y: 2110 },
    { kind: 'voting', first: 39, x: 690, y: 2110 },
    { kind: 'night', first: 42, x: 100, y: 2310 },
    { kind: 'human', first: 45, x: 690, y: 2310 },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 2520" width="1320" height="2520" role="img" aria-labelledby="voice-werewolf-title" style="background:${palette.surface}">
  <title id="voice-werewolf-title">${labels[0]} · ${labels[35]}</title>
  ${definitions(markerId)}

  <g data-controller="judge" data-labels="0 1 2">
    ${card(180, 30, 1040, 170, { fill: palette.strong, extra: 'data-controller-card="judge"' })}
    ${label(0, 212, 44, 976, 48, { size: 24, weight: 700, align: 'center' })}
    ${label(1, 212, 96, 976, 42, { size: 18, align: 'center' })}
    ${label(2, 212, 140, 976, 42, { size: 18, weight: 700, align: 'center', muted: true })}
  </g>

  <line data-role-bus="judge" x1="90" y1="115" x2="90" y2="1390" stroke="${palette.muted}" stroke-width="2.5"/>
  <line data-role-bus-entry="judge" x1="90" y1="115" x2="178" y2="115" stroke="${palette.muted}" stroke-width="2.5"/>
  ${roles
    .map(({ kind, y }) => arrow(`judge-to-${kind}`, `M 90 ${y + 110} H 178`))
    .join('')}

  ${roles
    .map(
      ({
        kind,
        indices,
        badge,
        y,
        fill,
      }) => `<g data-player-role="${kind}" data-labels="${indices.join(' ')}${badge === undefined ? '' : ` ${badge}`}">
    ${card(180, y, 1040, 220, { fill, extra: `data-role-card="${kind}"` })}
    ${label(indices[0], 208, y + 14, badge === undefined ? 984 : 690, 70, { size: 22, weight: 700 })}
    ${badge === undefined ? '' : `<g data-private-knowledge-for="${kind}">${card(930, y + 12, 260, 74, { fill: palette.surface })}${label(badge, 944, y + 16, 232, 66, { size: 17, weight: 700, align: 'center' })}</g>`}
    <line x1="214" y1="${y + 98}" x2="1186" y2="${y + 98}" stroke="${palette.line}" stroke-width="1.5"/>
    ${indices
      .slice(1)
      .map((index, column) =>
        label(index, 210 + column * 326, y + 108, 300, 92, {
          size: 17,
          align: 'center',
          muted: true,
        }),
      )
      .join('')}
  </g>`,
    )
    .join('')}

  <g data-information-access="role-filtered" data-labels="26 27 28 29 30 31 32 33 34">
    ${card(100, 1540, 1120, 430, { fill: palette.strong, extra: 'data-access-card="role-filtered"' })}
    ${label(26, 132, 1556, 1056, 58, { size: 24, weight: 700, align: 'center' })}
    <line x1="138" y1="1622" x2="1182" y2="1622" stroke="${palette.line}" stroke-width="1.5"/>
    ${access
      .map(
        (
          [role, context],
          row,
        ) => `<g data-access-row="${row + 1}" data-labels="${role} ${context}">
      ${label(role, 148, 1640 + row * 76, 230, 62, { size: 18, weight: 700 })}
      ${label(context, 404, 1640 + row * 76, 772, 62, { size: 17, muted: true })}
      ${row < access.length - 1 ? `<line x1="152" y1="${1710 + row * 76}" x2="1168" y2="${1710 + row * 76}" stroke="${palette.line}" stroke-width="1"/>` : ''}
    </g>`,
      )
      .join('')}
  </g>

  <g data-voice-loop="true" data-labels="35 36 37 38 39 40 41 42 43 44 45 46 47">
    ${label(35, 80, 2020, 1160, 62, { size: 25, weight: 700, align: 'center' })}
    ${phases
      .map(
        ({
          kind,
          first,
          x,
          y,
        }) => `<g data-voice-phase="${kind}" data-labels="${first} ${first + 1} ${first + 2}">
      ${card(x, y, 530, 170, { fill: palette.panel, extra: `data-phase-card="${kind}"` })}
      ${label(first, x + 24, y + 14, 482, 46, { size: 21, weight: 700, align: 'center' })}
      <line x1="${x + 28}" y1="${y + 66}" x2="${x + 502}" y2="${y + 66}" stroke="${palette.line}" stroke-width="1"/>
      ${label(first + 1, x + 24, y + 76, 482, 38, { size: 17, align: 'center' })}
      ${label(first + 2, x + 24, y + 118, 482, 38, { size: 17, align: 'center', muted: true })}
    </g>`,
      )
      .join('')}
  </g>
</svg>`;
}
