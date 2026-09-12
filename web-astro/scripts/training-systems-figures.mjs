// Web-only reflows for Chapter 8's SandboxFusion example and Agent-R1
// training system. Every localized label comes from the tracked source SVG.

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
    {
      size = 17,
      weight = 400,
      mono = false,
      align = 'center',
      muted = false,
    } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:${mono ? "'Courier New',Courier,monospace" : "Arial,'Helvetica Neue',Helvetica,sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.28;color:${muted ? '#666666' : '#333333'};overflow-wrap:anywhere;word-break:normal;white-space:${mono ? 'pre-wrap' : 'normal'};text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (x, y, width, height, { fill = '#f0f0f0', dash = false } = {}) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="${fill}" stroke="#7386a0" stroke-width="2"${dash ? ' stroke-dasharray="8,6"' : ''}/>`;
  const arrow = (path, edge, { muted = false } = {}) =>
    `<path data-edge="${edge}" d="${path}" fill="none" stroke="${muted ? '#666666' : '#333333'}" stroke-width="2.5" marker-end="url(#training-system-arrow)"/>`;
  return { label, card, arrow };
}

const definitions = `<defs>
  <marker id="training-system-arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker>
</defs>`;

export function layoutReTool(source) {
  const labels = extractLabels(source, '8-17', 35, {
    text: 35,
    rect: 9,
    line: 4,
    path: 2,
    marker: 2,
    polygon: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const trace = [
    { indices: [0, 1, 2], y: 20, height: 120, fill: '#f0f0f0' },
    {
      indices: [3, 4, 5, 6, 7, 8],
      y: 194,
      height: 170,
      fill: '#f5f5f5',
      mono: true,
    },
    {
      indices: [9, 10, 11, 12],
      y: 418,
      height: 128,
      fill: '#d0d0d0',
      mono: true,
    },
    { indices: [13, 14, 15], y: 600, height: 120, fill: '#f0f0f0' },
    { indices: [16, 17], y: 774, height: 100, fill: '#d0d0d0' },
  ];
  const traceCards = trace
    .map(({ indices, y, height, fill, mono = false }, step) => {
      const headingHeight = step === 1 ? 40 : 42;
      const details = indices.slice(1);
      const detailHeight = (height - headingHeight - 16) / details.length;
      return `<g data-step="${step + 1}">
        ${card(20, y, 580, height, { fill })}
        ${label(indices[0], 42, y + 10, 536, headingHeight, { size: 20, weight: 700, align: 'start' })}
        ${details
          .map((index, row) =>
            label(
              index,
              48,
              y + headingHeight + 8 + row * detailHeight,
              524,
              detailHeight,
              { size: 17, mono, align: 'start', muted: !mono },
            ),
          )
          .join('')}
      </g>`;
    })
    .join('');

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 900" width="1240" height="900" role="img" aria-labelledby="training-system-title" style="background:#ffffff">
  <title id="training-system-title">${labels[18]} · ${labels[25]} · ${labels[31]}</title>
  ${definitions}

  <g data-section="execution-trace">
    ${traceCards}
    ${arrow('M310 142 V192', 'trace-1-2', { muted: true })}
    ${arrow('M310 366 V416', 'trace-2-3', { muted: true })}
    ${arrow('M310 548 V598', 'trace-3-4', { muted: true })}
    ${arrow('M310 722 V772', 'trace-4-5', { muted: true })}
  </g>

  <g data-section="sandbox">
    ${card(760, 48, 460, 296, { fill: '#f0f0f0' })}
    ${label(18, 786, 62, 408, 52, { size: 24, weight: 700 })}
    ${label(19, 790, 122, 400, 42, { size: 18, muted: true })}
    ${label(20, 790, 168, 400, 46, { size: 18, muted: true })}
    ${label(21, 790, 218, 400, 42, { size: 17, mono: true, muted: true })}
    ${label(22, 790, 264, 400, 62, { size: 17, muted: true })}
  </g>

  <g data-section="sandbox-connectors">
    ${label(23, 622, 196, 116, 38, { size: 17, weight: 700 })}
    ${arrow('M612 242 H748', 'code-to-sandbox')}
    ${label(24, 616, 366, 96, 38, { size: 17, weight: 700 })}
    ${arrow('M748 298 H724 V458 H612', 'result-to-feedback')}
  </g>

  <g data-section="training-results">
    ${card(640, 482, 580, 398, { fill: '#f5f5f5' })}
    ${label(25, 666, 496, 528, 48, { size: 24, weight: 700 })}
    ${card(660, 560, 272, 298, { fill: '#ffffff' })}
    ${label(26, 676, 572, 240, 44, { size: 17, weight: 700, align: 'start' })}
    ${label(27, 676, 618, 240, 46, { size: 17, muted: true, align: 'start' })}
    ${label(28, 676, 668, 240, 52, { size: 17, muted: true, align: 'start' })}
    ${label(29, 676, 724, 240, 58, { size: 17, muted: true, align: 'start' })}
    ${label(30, 676, 786, 240, 58, { size: 17, muted: true, align: 'start' })}
    ${card(950, 560, 250, 298, { fill: '#ffffff' })}
    ${label(31, 966, 576, 218, 58, { size: 19, weight: 700 })}
    ${label(32, 966, 650, 218, 52, { size: 17, muted: true })}
    ${label(33, 966, 714, 218, 52, { size: 17, muted: true })}
    ${label(34, 966, 778, 218, 64, { size: 18, weight: 700 })}
  </g>
</svg>`;
}

export function layoutTrainingSystem(source) {
  const labels = extractLabels(source, '8-18', 54, {
    text: 54,
    rect: 12,
    line: 3,
    path: 0,
    marker: 2,
    polygon: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const stages = [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [8, 9, 10, 11],
    [12, 13, 14, 15],
  ];
  const tools = [
    [17, 18, 19, 20],
    [21, 22, 23, 24],
    [25, 26, 27, 28],
    [29, 30, 31, 32],
    [33, 34, 35, 36],
    [37, 38, 39, 40],
  ];
  const rollout = [
    [42, 43, 44],
    [45, 46, 47],
    [48, 49, 50],
    [51, 52, 53],
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1120" width="1320" height="1120" role="img" aria-labelledby="agent-r1-title" style="background:#ffffff">
  <title id="agent-r1-title">${labels[0]} · ${labels[16]} · ${labels[41]}</title>
  ${definitions}

  <g data-section="training-pipeline">
    ${stages
      .map((indices, stage) => {
        const x = 20 + stage * 330;
        return `<g data-stage="${stage + 1}">
          ${card(x, 20, 250, 240, { fill: stage === 0 || stage === 3 ? '#d0d0d0' : '#f0f0f0' })}
          ${label(indices[0], x + 18, 32, 214, 64, { size: 20, weight: 700 })}
          ${label(indices[1], x + 18, 100, 214, 48, { size: 17, muted: true })}
          ${label(indices[2], x + 18, 150, 214, 48, { size: 17, muted: true })}
          ${label(indices[3], x + 18, 200, 214, 48, { size: 17, muted: true })}
        </g>`;
      })
      .join('')}
    ${arrow('M282 140 H338', 'stage-1-2')}
    ${arrow('M612 140 H668', 'stage-2-3')}
    ${arrow('M942 140 H998', 'stage-3-4')}
  </g>

  <g data-section="tool-ecosystem">
    ${card(20, 300, 1280, 520, { fill: '#f5f5f5' })}
    ${label(16, 48, 314, 1224, 52, { size: 24, weight: 700 })}
    ${tools
      .map((indices, position) => {
        const column = position % 3;
        const row = Math.floor(position / 3);
        const x = 55 + column * 415;
        const y = 380 + row * 220;
        return `<g data-tool-group="${position + 1}">
          ${card(x, y, 380, 204, { fill: '#ffffff' })}
          ${label(indices[0], x + 18, y + 8, 344, 44, { size: 19, weight: 700 })}
          ${label(indices[1], x + 18, y + 54, 344, 48, { size: 17, muted: true })}
          ${label(indices[2], x + 18, y + 102, 344, 48, { size: 17, muted: true })}
          ${label(indices[3], x + 18, y + 150, 344, 48, { size: 17, muted: true })}
        </g>`;
      })
      .join('')}
  </g>

  <g data-section="distributed-rollout">
    ${card(20, 850, 1280, 250, { fill: '#f0f0f0' })}
    ${label(41, 48, 864, 1224, 48, { size: 24, weight: 700 })}
    ${rollout
      .map((indices, column) => {
        const x = 45 + column * 310;
        return `<g data-rollout-metric="${column + 1}">
          ${card(x, 926, 290, 166, { fill: '#ffffff' })}
          ${label(indices[0], x + 16, 934, 258, 52, { size: 19, weight: 700 })}
          ${label(indices[1], x + 16, 988, 258, 48, { size: 17, muted: true })}
          ${label(indices[2], x + 16, 1038, 258, 48, { size: 17, muted: true })}
        </g>`;
      })
      .join('')}
  </g>
</svg>`;
}
