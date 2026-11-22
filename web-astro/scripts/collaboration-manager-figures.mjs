// Web-only reflows for Chapter 10's manager-pattern examples. The tracked
// SVGs remain the source of every localized label and the original-image link.

import { palettes } from './figure-style.mjs';

const palette = palettes.light;

function normalizeLabel(value) {
  return value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

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

function helpers(labels, markerId) {
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
      mono = false,
      extra = '',
    } = {},
  ) => `<foreignObject data-label="${index}"${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:${mono ? "'SFMono-Regular',Consolas,'Liberation Mono',monospace" : "Arial,'Helvetica Neue',Helvetica,sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.32;color:${muted ? palette.muted : palette.ink};overflow-wrap:anywhere;word-break:normal;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%;unicode-bidi:plaintext">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (
    x,
    y,
    width,
    height,
    { fill = palette.panel, rx = 8, extra = '' } = {},
  ) =>
    `<rect${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="${palette.line}" stroke-width="2"/>`;
  const edge = (name, d, extra = '') =>
    `<path data-edge="${name}"${extra ? ` ${extra}` : ''} d="${d}" fill="none" stroke="${palette.muted}" stroke-width="2.5" marker-end="url(#${markerId})"/>`;
  const definitions = `<defs>
    <marker id="${markerId}" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="${palette.muted}"/></marker>
  </defs>`;
  return { label, card, edge, definitions };
}

export function layoutBookTranslationManager(source) {
  const labels = extractLabels(source, '10-5', 37, {
    rect: 9,
    line: 5,
    path: 0,
    marker: 3,
  });
  const { label, card, edge, definitions } = helpers(
    labels,
    'collaboration-manager-10-5-arrow',
  );
  const agents = [
    {
      kind: 'glossary',
      x: 20,
      indices: [2, 3, 4, 5, 6, 7, 8, 9],
      code: [7, 8, 9],
    },
    {
      kind: 'translation',
      x: 460,
      indices: [10, 11, 12, 13, 14, 15, 16],
      code: [15, 16],
    },
    {
      kind: 'proofreading',
      x: 900,
      indices: [17, 18, 19, 20, 21, 22, 23],
      code: [22, 23],
    },
  ];
  const artifacts = [
    { kind: 'glossary', indices: [27, 28], x: 40 },
    { kind: 'chapters', indices: [29, 30], x: 355 },
    { kind: 'review', indices: [31, 32], x: 670 },
    { kind: 'guide', indices: [33, 34], x: 985 },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1120" width="1320" height="1120" role="img" aria-labelledby="book-translation-manager-title" style="background:${palette.surface}">
  <title id="book-translation-manager-title">${labels[0]}</title>
  ${definitions}

  <g data-manager="translation" data-labels="0 1">
    ${card(310, 30, 700, 110, { fill: palette.strong, extra: 'data-node-card="manager"' })}
    ${label(0, 340, 42, 640, 42, { size: 25, weight: 700 })}
    ${label(1, 340, 84, 640, 48, { size: 17, weight: 700, muted: true })}
  </g>

  <g data-connector-gutter="manager-fanout">
    ${edge('manager-to-glossary', 'M 660 140 V 174 H 210 V 208')}
    ${edge('manager-to-translation', 'M 660 140 V 208')}
    ${edge('manager-to-proofreading', 'M 660 140 V 174 H 1110 V 208')}
  </g>

  ${agents
    .map(({ kind, x, indices, code }) => {
      const body = indices.slice(2, 5);
      return `<g data-agent="${kind}" data-labels="${indices.join(' ')}">
    ${card(x, 210, 400, 360, { fill: kind === 'translation' ? palette.strong : palette.panel, extra: `data-node-card="agent" data-agent-card="${kind}"` })}
    ${label(indices[0], x + 24, 226, 352, 38, { size: 22, weight: 700 })}
    ${label(indices[1], x + 24, 266, 352, 34, { size: 17, weight: 700, muted: true })}
    <line x1="${x + 30}" y1="308" x2="${x + 370}" y2="308" stroke="${palette.line}" stroke-width="1.5"/>
    ${body.map((index, row) => label(index, x + 24, 318 + row * 48, 352, 44, { size: 16, align: 'start', muted: row < 2 })).join('')}
    ${card(x + 20, 466, 360, code.length === 3 ? 96 : 88, { fill: palette.surface, rx: 6, extra: `data-code-card="${kind}"` })}
    ${code.map((index, row) => label(index, x + 32, code.length === 3 ? 470 + row * 24 : 470 + row * 40, 336, code.length === 3 && row < 2 ? 24 : 40, { size: 15, align: 'start', mono: true })).join('')}
  </g>`;
    })
    .join('')}

  <g data-connector-gutter="agent-handoffs">
    ${edge('glossary-to-translation', 'M 210 570 V 636 H 620 V 572', 'data-artifact="glossary" data-target-port="translation-input"')}
    ${label(24, 322, 584, 226, 42, { size: 16, weight: 700, extra: 'data-handoff-label="glossary"' })}
    ${edge('translation-to-proofreading', 'M 700 570 V 636 H 1110 V 572', 'data-artifact="translation" data-source-port="translation-output"')}
    ${label(25, 772, 584, 226, 42, { size: 16, weight: 700, extra: 'data-handoff-label="translation"' })}
  </g>

  <g data-shared-filesystem="true" data-labels="26-34">
    ${card(20, 680, 1280, 220, { fill: palette.strong, extra: 'data-node-card="filesystem"' })}
    ${label(26, 48, 696, 1224, 54, { size: 24, weight: 700 })}
    ${artifacts
      .map(
        ({
          kind,
          indices,
          x,
        }) => `<g data-artifact="${kind}" data-labels="${indices.join(' ')}">
      ${card(x, 766, 295, 112, { fill: palette.surface, extra: `data-artifact-card="${kind}"` })}
      ${label(indices[0], x + 18, 778, 259, 40, { size: 16, weight: 700, mono: true })}
      ${label(indices[1], x + 18, 824, 259, 40, { size: 16, muted: true })}
    </g>`,
      )
      .join('')}
  </g>

  <g data-context-isolation="true" data-labels="35 36">
    ${card(20, 930, 1280, 160, { fill: palette.panel, extra: 'data-node-card="context-isolation"' })}
    ${label(35, 52, 946, 1216, 48, { size: 23, weight: 700 })}
    <line x1="60" y1="1004" x2="1260" y2="1004" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(36, 58, 1018, 1204, 56, { size: 17, weight: 700, muted: true })}
  </g>
</svg>`;
}

export function layoutManagerParallelCoordination(source) {
  const labels = extractLabels(source, '10-6', 28, {
    rect: 7,
    line: 5,
    path: 0,
    marker: 2,
  });
  const { label, card, edge, definitions } = helpers(
    labels,
    'collaboration-manager-10-6-arrow',
  );
  const agents = [
    { number: 1, x: 20, first: 3, state: 'running' },
    { number: 2, x: 340, first: 7, state: 'running' },
    { number: 3, x: 660, first: 11, state: 'completed' },
    { number: 4, x: 980, first: 15, state: 'waiting' },
  ];
  const messages = [
    { route: 'manager-to-agent-1', indices: [20, 21] },
    { route: 'agent-3-to-manager', indices: [22, 23] },
    { route: 'agent-1-to-agent-2', indices: [24, 25] },
    { route: 'manager-to-agent-4', indices: [26, 27] },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1110" width="1320" height="1110" role="img" aria-labelledby="manager-parallel-title" style="background:${palette.surface}">
  <title id="manager-parallel-title">${labels[0]} · ${labels[2]}</title>
  ${definitions}

  <g data-manager="parallel" data-labels="0 1">
    ${card(310, 30, 700, 110, { fill: palette.strong, extra: 'data-node-card="manager"' })}
    ${label(0, 340, 42, 640, 42, { size: 25, weight: 700 })}
    ${label(1, 340, 84, 640, 48, { size: 17, weight: 700, muted: true })}
  </g>

  <g data-message-bus="true" data-labels="2">
    ${card(110, 180, 1100, 76, { fill: palette.strong, extra: 'data-node-card="message-bus"' })}
    ${label(2, 142, 194, 1036, 48, { size: 23, weight: 700 })}
  </g>
  <g data-connector-gutter="manager-to-bus">
    ${edge('manager-to-message-bus', 'M 660 140 V 178')}
  </g>
  <g data-connector-gutter="bus-fanout">
    ${agents.map(({ number, x }) => edge(`message-bus-to-agent-${number}`, `M 660 256 V 286 H ${x + 150} V 328`)).join('')}
  </g>

  ${agents
    .map(
      ({
        number,
        x,
        first,
        state,
      }) => `<g data-agent="${number}" data-state="${state}" data-labels="${first}-${first + 3}">
    ${card(x, 330, 300, 220, { fill: state === 'completed' ? palette.strong : palette.panel, extra: `data-node-card="agent" data-agent-card="${number}"` })}
    ${label(first, x + 20, 348, 260, 38, { size: 22, weight: 700 })}
    ${label(first + 1, x + 20, 394, 260, 52, { size: 17, weight: 700 })}
    <line x1="${x + 26}" y1="454" x2="${x + 274}" y2="454" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(first + 2, x + 20, 464, 260, 36, { size: 17, weight: 700, muted: state !== 'completed' })}
    ${label(first + 3, x + 20, 506, 260, 30, { size: 16, muted: true })}
  </g>`,
    )
    .join('')}

  <g data-message-log="true" data-labels="19-27">
    ${card(20, 600, 1280, 480, { fill: palette.panel, extra: 'data-node-card="message-log"' })}
    ${label(19, 50, 618, 1220, 58, { size: 24, weight: 700 })}
    ${messages
      .map(({ route, indices }, row) => {
        const y = 696 + row * 90;
        return `<g data-message-route="${route}" data-labels="${indices.join(' ')}">
      ${card(45, y, 280, 68, { fill: palette.strong, rx: 6, extra: `data-route-card="${route}"` })}
      ${label(indices[0], 62, y + 8, 246, 52, { size: 17, weight: 700 })}
      ${card(350, y, 925, 68, { fill: palette.surface, rx: 6, extra: `data-message-card="${route}"` })}
      ${label(indices[1], 368, y + 7, 889, 54, { size: 15, align: 'start', mono: true })}
    </g>`;
      })
      .join('')}
  </g>
</svg>`;
}

export function layoutPhoneComputerCollaboration(source) {
  const labels = extractLabels(source, '10-7', 31, {
    rect: 12,
    line: 8,
    path: 0,
    marker: 3,
  });
  const { label, card, edge, definitions } = helpers(
    labels,
    'collaboration-manager-10-7-arrow',
  );
  const agents = [
    {
      kind: 'phone',
      x: 20,
      title: [0, 1],
      stages: [
        { kind: 'voice-input', indices: [2, 3] },
        { kind: 'speech-recognition', indices: [4, 5] },
        { kind: 'language-reasoning', indices: [6, 7] },
        { kind: 'voice-response', indices: [8, 9] },
      ],
    },
    {
      kind: 'computer',
      x: 680,
      title: [10, 11],
      stages: [
        { kind: 'screenshot', indices: [12, 13] },
        { kind: 'vision', indices: [14, 15] },
        { kind: 'planning', indices: [16, 17] },
        { kind: 'execution', indices: [18, 19] },
      ],
    },
  ];
  const messages = [
    { direction: 'phone-to-computer', indices: [22, 23] },
    { direction: 'computer-to-phone', indices: [24, 25] },
    { direction: 'phone-to-computer', indices: [26, 27] },
    { direction: 'computer-to-phone', indices: [28, 29] },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1240" width="1320" height="1240" role="img" aria-labelledby="phone-computer-title" style="background:${palette.surface}">
  <title id="phone-computer-title">${labels[0]} · ${labels[10]}</title>
  ${definitions}

  ${agents
    .map(
      ({
        kind,
        x,
        title,
        stages,
      }) => `<g data-agent="${kind}" data-labels="${title.join(' ')}">
    ${card(x, 30, 620, 650, { fill: palette.panel, extra: `data-node-card="agent" data-agent-card="${kind}"` })}
    ${label(title[0], x + 28, 48, 564, 42, { size: 25, weight: 700 })}
    ${label(title[1], x + 28, 94, 564, 40, { size: 17, weight: 700, muted: true })}
    ${stages
      .map(({ kind: stageKind, indices }, row) => {
        const y = 154 + row * 125;
        return `<g data-stage="${stageKind}" data-labels="${indices.join(' ')}">
      ${card(x + 30, y, 560, 96, { fill: row === 0 || row === 3 ? palette.strong : palette.surface, rx: 6, extra: `data-stage-card="${stageKind}"` })}
      ${label(indices[0], x + 52, y + 10, 516, 34, { size: 19, weight: 700, align: 'start' })}
      ${label(indices[1], x + 52, y + 47, 516, 38, { size: 16, align: 'start', muted: true })}
    </g>`;
      })
      .join('')}
    <g data-connector-gutter="${kind}-react-loop">
      ${stages
        .slice(0, -1)
        .map((_, row) =>
          edge(
            `${kind}-stage-${row + 1}-to-${row + 2}`,
            `M ${x + 310} ${250 + row * 125} V ${277 + row * 125}`,
            `data-agent-flow="${kind}"`,
          ),
        )
        .join('')}
    </g>
  </g>`,
    )
    .join('')}

  <g data-connector-gutter="websocket-channel">
    ${edge('phone-agent-to-websocket', 'M 290 680 V 738', 'data-channel="websocket" data-direction="send"')}
    ${edge('websocket-to-phone-agent', 'M 370 738 V 682', 'data-channel="websocket" data-direction="receive"')}
    ${edge('computer-agent-to-websocket', 'M 950 680 V 738', 'data-channel="websocket" data-direction="send"')}
    ${edge('websocket-to-computer-agent', 'M 1030 738 V 682', 'data-channel="websocket" data-direction="receive"')}
  </g>
  <g data-channel="websocket" data-direction="bidirectional" data-labels="20">
    ${card(140, 740, 1040, 80, { fill: palette.strong, extra: 'data-node-card="websocket"' })}
    ${label(20, 170, 752, 980, 56, { size: 22, weight: 700 })}
  </g>

  <g data-message-stream="bidirectional" data-labels="21-30">
    ${card(20, 870, 1280, 340, { fill: palette.panel, extra: 'data-node-card="message-stream"' })}
    ${label(21, 52, 888, 1216, 58, { size: 23, weight: 700 })}
    ${messages
      .map(({ direction, indices }, row) => {
        const y = 960 + row * 54;
        return `<g data-message-direction="${direction}" data-labels="${indices.join(' ')}">
      ${card(48, y, 270, 44, { fill: palette.strong, rx: 6, extra: `data-direction-card="${direction}"` })}
      ${label(indices[0], 62, y + 5, 242, 34, { size: 16, weight: 700 })}
      ${card(340, y, 932, 44, { fill: palette.surface, rx: 6, extra: `data-message-card="${direction}"` })}
      ${label(indices[1], 356, y + 4, 900, 36, { size: 15, align: 'start', mono: true })}
    </g>`;
      })
      .join('')}
    ${label(30, 54, 1178, 1212, 26, { size: 16, weight: 700, muted: true })}
  </g>
</svg>`;
}

export function layoutCascadingTermination(source) {
  const labels = extractLabels(source, '10-8', 46, {
    rect: 9,
    line: 9,
    path: 0,
    marker: 2,
  });
  const { label, card, edge, definitions } = helpers(
    labels,
    'collaboration-manager-10-8-arrow',
  );
  const agents = [
    { number: 1, x: 20, first: 2, state: 'searching' },
    { number: 2, x: 280, first: 6, state: 'not-found' },
    { number: 3, x: 540, first: 10, state: 'found' },
    { number: 4, x: 800, first: 14, state: 'terminated' },
    { number: '5-10', x: 1060, first: 18, state: 'terminated' },
  ];
  const timeline = [
    { event: 'launch', first: 23 },
    { event: 'partial-completion', first: 26 },
    { event: 'target-found', first: 29 },
    { event: 'termination-broadcast', first: 32 },
    { event: 'results-returned', first: 35 },
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1140" width="1320" height="1140" role="img" aria-labelledby="cascading-termination-title" style="background:${palette.surface}">
  <title id="cascading-termination-title">${labels[0]} · ${labels[22]}</title>
  ${definitions}

  <g data-manager="search" data-labels="0 1">
    ${card(310, 30, 700, 110, { fill: palette.strong, extra: 'data-node-card="manager"' })}
    ${label(0, 340, 42, 640, 42, { size: 25, weight: 700 })}
    ${label(1, 340, 84, 640, 48, { size: 17, weight: 700, muted: true })}
  </g>

  <g data-connector-gutter="manager-fanout">
    ${agents.map(({ number, x }) => edge(`manager-to-agent-${number}`, `M 660 140 V 176 H ${x + 120} V 228`)).join('')}
  </g>
  ${agents
    .map(
      ({
        number,
        x,
        first,
        state,
      }) => `<g data-agent="${number}" data-state="${state}" data-labels="${first}-${first + 3}">
    ${card(x, 230, 240, 250, { fill: state === 'found' ? palette.strong : palette.panel, extra: `data-node-card="agent" data-agent-card="${number}"` })}
    ${label(first, x + 18, 246, 204, 38, { size: 21, weight: 700 })}
    ${label(first + 1, x + 18, 290, 204, 32, { size: 15, weight: 700, mono: true, muted: true })}
    <line x1="${x + 24}" y1="330" x2="${x + 216}" y2="330" stroke="${palette.line}" stroke-width="1.5"/>
    ${label(first + 2, x + 18, 340, 204, 64, { size: 16, weight: 700 })}
    ${label(first + 3, x + 18, 414, 204, 48, { size: 17, weight: 700, muted: state !== 'found' })}
  </g>`,
    )
    .join('')}

  <g data-connector-gutter="success-trigger">
    ${edge('agent-3-success-to-cascade', 'M 660 480 V 528', 'data-trigger="target-found"')}
  </g>
  <g data-termination-sequence="cascading" data-labels="22-37">
    ${card(20, 530, 1280, 300, { fill: palette.panel, extra: 'data-node-card="termination-sequence"' })}
    ${label(22, 52, 548, 1216, 54, { size: 24, weight: 700 })}
    ${timeline
      .map(({ event, first }, step) => {
        const x = 30 + step * 260;
        return `<g data-termination-event="${event}" data-step="${step + 1}" data-labels="${first}-${first + 2}">
      ${card(x, 620, 220, 190, { fill: event === 'target-found' ? palette.strong : palette.surface, rx: 6, extra: `data-event-card="${event}"` })}
      ${label(first, x + 16, 634, 188, 34, { size: 18, weight: 700 })}
      ${label(first + 1, x + 16, 679, 188, 48, { size: 16, weight: 700 })}
      ${label(first + 2, x + 16, 735, 188, 58, { size: 15, muted: true })}
    </g>`;
      })
      .join('')}
    <g data-connector-gutter="termination-timeline">
      ${timeline
        .slice(0, -1)
        .map((_, step) =>
          edge(
            `termination-step-${step + 1}-to-${step + 2}`,
            `M ${250 + step * 260} 715 H ${288 + step * 260}`,
            'data-timeline-edge="true"',
          ),
        )
        .join('')}
    </g>
  </g>

  <g data-result="found" data-labels="38-41">
    ${card(20, 860, 630, 250, { fill: palette.panel, extra: 'data-node-card="result"' })}
    ${label(38, 48, 878, 574, 48, { size: 23, weight: 700 })}
    <line x1="54" y1="936" x2="616" y2="936" stroke="${palette.line}" stroke-width="1.5"/>
    ${[39, 40, 41].map((index, row) => label(index, 54, 948 + row * 50, 562, 44, { size: 16, align: 'start', mono: true })).join('')}
  </g>
  <g data-performance-comparison="true" data-labels="42-45">
    ${card(670, 860, 630, 250, { fill: palette.strong, extra: 'data-node-card="performance"' })}
    ${label(42, 698, 878, 574, 48, { size: 23, weight: 700 })}
    <line x1="704" y1="936" x2="1266" y2="936" stroke="${palette.line}" stroke-width="1.5"/>
    ${[43, 44, 45].map((index, row) => label(index, 704, 948 + row * 50, 562, 44, { size: 16, weight: index === 44 ? 700 : 400, align: 'start', muted: index !== 44 })).join('')}
  </g>
</svg>`;
}
