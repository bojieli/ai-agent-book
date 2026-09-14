import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

// Web-only reflows for Chapter 7's evaluation overview figures. Localized SVGs
// remain unchanged; every visible string is preserved from its source figure.
const WIDTH = 1000;
const HEADING = { size: 20, bold: true };
const TITLE = { size: 18, bold: true };
const BODY = { size: 16 };
const CODE = { size: 14, mono: true, align: 'start', direction: 'ltr' };
const CAPTION = { size: 14, muted: true };

const variants = {
  1: {
    labels: 24,
    viewBoxes: ['0 0 880 486'],
    shape: { rect: 12, line: 6, path: 1, marker: 2, polygon: 2 },
  },
  3: {
    labels: 34,
    viewBoxes: ['0 0 880 512'],
    shape: { rect: 11, line: 3, path: 0, marker: 3, polygon: 3 },
  },
  10: {
    labels: 39,
    viewBoxes: ['0 40 880 480', '0 40 940 480'],
    shape: { rect: 18, line: 8, path: 0, marker: [2, 3], polygon: [2, 3] },
  },
};

const row = (id, style = BODY) => ({ id, ...style });
const count = (source, name) =>
  (source.match(new RegExp(`<${name}\\b`, 'g')) || []).length;

function sourceLabels(source, figure) {
  const normalized = source.replace(/<text\b([^>]*)\/>/g, '<text$1></text>');
  const labels = extractLabels(normalized, `7-${figure}`, [
    variants[figure].labels,
  ]);
  const variant = variants[figure];
  const viewBox = source.match(/<svg\b[^>]*\bviewBox="([^"]+)"/)?.[1];
  const shapeMatches = Object.entries(variant.shape).every(
    ([name, expected]) => {
      const actual = count(source, name);
      return Array.isArray(expected)
        ? expected.includes(actual)
        : actual === expected;
    },
  );
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !variant.viewBoxes.includes(viewBox) ||
    labels.length !== variant.labels ||
    labels.some((value) => !value) ||
    !shapeMatches
  )
    throw new Error(
      `Figure 7-${figure} source structure changed; review its web layout.`,
    );
  return labels;
}

function tag(element, attributes) {
  return element.replace(
    /^(<\w+)/,
    `$1 ${Object.entries(attributes)
      .map(([name, value]) => `${name}="${value}"`)
      .join(' ')}`,
  );
}

function label(k, id, x, y, width, height, style = BODY) {
  return k
    .label(id, x, y, width, height, style)
    .replace('<foreignObject ', `<foreignObject data-label="${id}" `);
}

function card(k, x, y, width, height, options, attributes = {}) {
  return tag(k.card(x, y, width, height, options), attributes);
}

function edge(k, name, from, to, d, { gutter = 64, dash = false } = {}) {
  return tag(k.path(d, { dash }), {
    'data-edge': name,
    'data-from': from,
    'data-to': to,
    'data-route': 'gutter',
    'data-gutter-size': gutter,
    'data-card-gap-start': 8,
    'data-card-gap-end': 8,
  });
}

function metrics(k, rows, width, { padding = 20, gap = 12, min = 0 } = {}) {
  const heights = rows.map((item) =>
    k.height(item.id, width - padding * 2, item),
  );
  return {
    heights,
    height: Math.max(
      min,
      padding * 2 +
        heights.reduce((sum, height) => sum + height, 0) +
        Math.max(0, rows.length - 1) * gap,
    ),
  };
}

function panel(
  k,
  rows,
  x,
  y,
  width,
  measure,
  {
    fill = '#f0f0f0',
    dash = false,
    padding = 20,
    gap = 12,
    name,
    kind = 'node',
  } = {},
) {
  const attribute = `data-${kind}`;
  let output = `<g${name ? ` ${attribute}="${name}"` : ''}>${card(
    k,
    x,
    y,
    width,
    measure.height,
    { fill, dash },
    name ? { [attribute]: name } : {},
  )}`;
  let cursor = y + padding;
  rows.forEach((item, index) => {
    output += label(
      k,
      item.id,
      x + padding,
      cursor,
      width - padding * 2,
      measure.heights[index],
      item,
    );
    cursor += measure.heights[index] + gap;
  });
  return `${output}</g>`;
}

function finish(k, content, figure, height) {
  return k
    .svg(content, height, WIDTH)
    .replace(
      '<svg ',
      `<svg data-layout="evaluation-overview" data-figure="7-${figure}" `,
    );
}

export function layoutEvaluationOverview(source, { rtl = false } = {}) {
  const k = figureKit(sourceLabels(source, 1), { rtl });
  const stageX = 128;
  const stageWidth = 848;
  const innerX = 152;
  const innerWidth = 800;
  const verticalGutter = 64;
  let y = 24;
  let output = '';

  const successRows = [row(0, HEADING), row(1, CAPTION)];
  const success = metrics(k, successRows, stageWidth, {
    padding: 24,
    gap: 8,
  });
  output += panel(k, successRows, stageX, y, stageWidth, success, {
    padding: 24,
    gap: 8,
    name: 'success-definition',
    kind: 'section',
  });
  let previousBottom = y + success.height;

  y = previousBottom + verticalGutter;
  output += edge(
    k,
    'success-to-task-bank',
    'success-definition',
    'task-bank',
    `M552 ${previousBottom + 8} L552 ${y - 8}`,
  );
  const taskHeading = k.height(2, innerWidth, HEADING);
  const taskRows = [
    [row(3, TITLE), row(4, CAPTION)],
    [row(5, TITLE), row(6, CAPTION)],
    [row(7, TITLE), row(8, CAPTION)],
  ];
  const taskGap = 64;
  const taskWidth = (innerWidth - taskGap * 2) / 3;
  const taskMeasures = taskRows.map((rows) =>
    metrics(k, rows, taskWidth, { min: 112 }),
  );
  const taskCardHeight = Math.max(...taskMeasures.map((item) => item.height));
  taskMeasures.forEach((item) => (item.height = taskCardHeight));
  const taskHeight = 24 + taskHeading + 20 + taskCardHeight + 24;
  output += `<g data-section="task-bank">${card(
    k,
    stageX,
    y,
    stageWidth,
    taskHeight,
    {},
    { 'data-section': 'task-bank' },
  )}${label(k, 2, innerX, y + 24, innerWidth, taskHeading, HEADING)}`;
  const taskCardY = y + 24 + taskHeading + 20;
  const taskNames = [
    'public-benchmarks',
    'business-set',
    'production-feedback',
  ];
  taskRows.forEach((rows, index) => {
    output += panel(
      k,
      rows,
      innerX + index * (taskWidth + taskGap),
      taskCardY,
      taskWidth,
      taskMeasures[index],
      { fill: '#ffffff', name: taskNames[index] },
    );
  });
  output += '</g>';
  const taskMid = taskCardY + taskCardHeight / 2;
  previousBottom = y + taskHeight;

  y = previousBottom + verticalGutter;
  output += edge(
    k,
    'task-bank-to-verification',
    'task-bank',
    'verification-spectrum',
    `M552 ${previousBottom + 8} L552 ${y - 8}`,
  );
  const verificationHeading = k.height(9, innerWidth, HEADING);
  const verificationCaption = k.height(10, innerWidth, CAPTION);
  const verificationRows = [
    [row(11, TITLE), row(12, CAPTION)],
    [row(13, TITLE), row(14, CAPTION)],
    [row(15, TITLE), row(16, CAPTION)],
    [row(17, TITLE), row(18, CAPTION)],
  ];
  const verificationGap = 80;
  const verificationWidth = (innerWidth - verificationGap) / 2;
  const verificationMeasures = verificationRows.map((rows) =>
    metrics(k, rows, verificationWidth, { min: 112 }),
  );
  const verificationCardHeight = Math.max(
    ...verificationMeasures.map((item) => item.height),
  );
  verificationMeasures.forEach(
    (item) => (item.height = verificationCardHeight),
  );
  const verificationHeight =
    24 +
    verificationHeading +
    8 +
    verificationCaption +
    20 +
    verificationCardHeight * 2 +
    64 +
    24;
  output += `<g data-section="verification-spectrum">${card(
    k,
    stageX,
    y,
    stageWidth,
    verificationHeight,
    {},
    { 'data-section': 'verification-spectrum' },
  )}${label(k, 9, innerX, y + 24, innerWidth, verificationHeading, HEADING)}${label(
    k,
    10,
    innerX,
    y + 32 + verificationHeading,
    innerWidth,
    verificationCaption,
    CAPTION,
  )}`;
  const verificationCardY = y + 52 + verificationHeading + verificationCaption;
  const verificationNames = [
    'deterministic',
    'checklist',
    'rubric-llm',
    'pairwise',
  ];
  const verificationPositions = [
    [innerX, verificationCardY],
    [innerX + verificationWidth + verificationGap, verificationCardY],
    [
      innerX + verificationWidth + verificationGap,
      verificationCardY + verificationCardHeight + 64,
    ],
    [innerX, verificationCardY + verificationCardHeight + 64],
  ];
  verificationRows.forEach((rows, index) => {
    const [x, cardY] = verificationPositions[index];
    output += panel(
      k,
      rows,
      x,
      cardY,
      verificationWidth,
      verificationMeasures[index],
      { fill: '#ffffff', name: verificationNames[index] },
    );
  });
  const topArrowY = verificationCardY + verificationCardHeight / 2;
  const bottomCardY = verificationCardY + verificationCardHeight + 64;
  const bottomArrowY = bottomCardY + verificationCardHeight / 2;
  const rightCenterX =
    innerX + verificationWidth + verificationGap + verificationWidth / 2;
  output += edge(
    k,
    'deterministic-to-checklist',
    'deterministic',
    'checklist',
    `M${innerX + verificationWidth + 8} ${topArrowY} L${innerX + verificationWidth + verificationGap - 8} ${topArrowY}`,
    { gutter: verificationGap },
  );
  output += edge(
    k,
    'checklist-to-rubric-llm',
    'checklist',
    'rubric-llm',
    `M${rightCenterX} ${verificationCardY + verificationCardHeight + 8} L${rightCenterX} ${bottomCardY - 8}`,
  );
  output += edge(
    k,
    'rubric-llm-to-pairwise',
    'rubric-llm',
    'pairwise',
    `M${innerX + verificationWidth + verificationGap - 8} ${bottomArrowY} L${innerX + verificationWidth + 8} ${bottomArrowY}`,
    { gutter: verificationGap },
  );
  output += '</g>';
  previousBottom = y + verificationHeight;

  y = previousBottom + verticalGutter;
  output += edge(
    k,
    'verification-to-results',
    'verification-spectrum',
    'results',
    `M552 ${previousBottom + 8} L552 ${y - 8}`,
  );
  const resultRows = [row(19, HEADING), row(20)];
  const result = metrics(k, resultRows, stageWidth, {
    padding: 24,
    gap: 8,
  });
  output += panel(k, resultRows, stageX, y, stageWidth, result, {
    padding: 24,
    gap: 8,
    name: 'results',
    kind: 'section',
  });
  const resultMid = y + result.height / 2;
  output += edge(
    k,
    'results-to-task-bank',
    'results',
    'task-bank',
    `M120 ${resultMid} H24 V${taskMid} H120`,
    { gutter: 104, dash: true },
  );
  const loopCaption = k.height(21, 72, CAPTION);
  output += label(
    k,
    21,
    40,
    (resultMid + taskMid - loopCaption) / 2,
    72,
    loopCaption,
    CAPTION,
  ).replace(
    '<foreignObject ',
    '<foreignObject data-arrow-caption="results-to-task-bank" ',
  );

  y += result.height + 24;
  const infrastructureRows = [row(22, TITLE), row(23, CAPTION)];
  const infrastructure = metrics(k, infrastructureRows, stageWidth, {
    padding: 24,
    gap: 8,
  });
  output += panel(
    k,
    infrastructureRows,
    stageX,
    y,
    stageWidth,
    infrastructure,
    {
      fill: '#f3f0e8',
      padding: 24,
      gap: 8,
      name: 'supporting-infrastructure',
      kind: 'section',
    },
  );
  return finish(k, output, 1, y + infrastructure.height + 24);
}

export function layoutDualControl(source, { rtl = false } = {}) {
  const k = figureKit(sourceLabels(source, 3), { rtl });
  const userRows = [
    row(0, HEADING),
    row(1, CODE),
    row(2, CODE),
    row(3, CAPTION),
  ];
  const agentRows = [row(4, HEADING), row(5), row(6, CAPTION), row(7, CAPTION)];
  const actorWidth = 384;
  const dialogueWidth = 168;
  const user = metrics(k, userRows, actorWidth);
  const agent = metrics(k, agentRows, actorWidth);
  const firstCaption = k.height(8, dialogueWidth, CAPTION);
  const secondCaption = k.height(9, dialogueWidth, CAPTION);
  const actorHeight = Math.max(
    user.height,
    agent.height,
    80 + firstCaption + secondCaption,
    220,
  );
  user.height = actorHeight;
  agent.height = actorHeight;
  let output = panel(k, userRows, 24, 24, actorWidth, user, {
    fill: '#ffffff',
    dash: true,
    name: 'user-simulator',
  });
  output += panel(k, agentRows, 592, 24, actorWidth, agent, {
    fill: '#ffffff',
    dash: true,
    name: 'agent',
  });
  let captionY = 44;
  output += '<g data-dialogue="bidirectional" data-caption-labels="8 9">';
  output += label(
    k,
    8,
    416,
    captionY,
    dialogueWidth,
    firstCaption,
    CAPTION,
  ).replace(
    '<foreignObject ',
    '<foreignObject data-dialogue-caption="shared" ',
  );
  captionY += firstCaption + 4;
  output += label(
    k,
    9,
    416,
    captionY,
    dialogueWidth,
    secondCaption,
    CAPTION,
  ).replace(
    '<foreignObject ',
    '<foreignObject data-dialogue-caption="shared" ',
  );
  let arrowY = captionY + secondCaption + 8;
  output += edge(
    k,
    'user-to-agent-dialogue',
    'user-simulator',
    'agent',
    `M416 ${arrowY} L584 ${arrowY}`,
    { gutter: 184 },
  );
  arrowY += 24;
  output += edge(
    k,
    'agent-to-user-dialogue',
    'agent',
    'user-simulator',
    `M584 ${arrowY} L416 ${arrowY}`,
    { gutter: 184 },
  );
  output += '</g>';

  const environmentY = 24 + actorHeight + 64;
  output += edge(
    k,
    'user-to-shared-environment',
    'user-simulator',
    'device-state',
    `M216 ${32 + actorHeight} L216 ${environmentY - 8}`,
  );
  output += edge(
    k,
    'agent-to-shared-environment',
    'agent',
    'carrier-state',
    `M784 ${32 + actorHeight} L784 ${environmentY - 8}`,
  );
  const environmentHeading = k.height(10, 904, HEADING);
  const environmentRows = [
    [row(11, TITLE), row(12), row(13, CODE), row(14, CODE)],
    [row(15, TITLE), row(16), row(17, CODE), row(18, CODE)],
  ];
  const environmentMeasures = environmentRows.map((rows) =>
    metrics(k, rows, 424),
  );
  const environmentCardHeight = Math.max(
    ...environmentMeasures.map((item) => item.height),
  );
  environmentMeasures.forEach((item) => (item.height = environmentCardHeight));
  const environmentHeight =
    24 + environmentHeading + 20 + environmentCardHeight + 24;
  output += `<g data-section="shared-environment">${card(
    k,
    24,
    environmentY,
    952,
    environmentHeight,
    { fill: '#f3f0e8' },
    { 'data-section': 'shared-environment' },
  )}${label(k, 10, 48, environmentY + 24, 904, environmentHeading, HEADING)}`;
  const environmentCardY = environmentY + 44 + environmentHeading;
  output += panel(
    k,
    environmentRows[0],
    48,
    environmentCardY,
    424,
    environmentMeasures[0],
    { fill: '#ffffff', name: 'device-state' },
  );
  output += panel(
    k,
    environmentRows[1],
    528,
    environmentCardY,
    424,
    environmentMeasures[1],
    { fill: '#ffffff', name: 'carrier-state' },
  );
  output += '</g>';

  const rereadY = environmentY + environmentHeight + 24;
  const rereadRows = [row(19, CAPTION)];
  const reread = metrics(k, rereadRows, 952, { min: 64 });
  output += panel(k, rereadRows, 24, rereadY, 952, reread, {
    fill: '#ffffff',
    dash: true,
    name: 'reread-note',
  });

  const verificationY = rereadY + reread.height + 24;
  const verificationHeading = k.height(20, 904, HEADING);
  const checkRows = [
    [row(21, TITLE), row(22, CAPTION), row(23, CAPTION)],
    [row(24, TITLE), row(25, CODE), row(26, CAPTION)],
    [row(27, TITLE), row(28, CAPTION), row(29, CAPTION)],
    [row(30, TITLE), row(31, CAPTION), row(32, CAPTION)],
  ];
  const checkGap = 16;
  const checkWidth = (904 - checkGap * 3) / 4;
  const checkMeasures = checkRows.map((rows) =>
    metrics(k, rows, checkWidth, { padding: 16, gap: 8 }),
  );
  const checkHeight = Math.max(...checkMeasures.map((item) => item.height));
  checkMeasures.forEach((item) => (item.height = checkHeight));
  const rewardHeight = k.height(33, 904, CODE);
  const verificationHeight =
    24 + verificationHeading + 20 + checkHeight + 20 + rewardHeight + 24;
  output += `<g data-section="verification">${card(
    k,
    24,
    verificationY,
    952,
    verificationHeight,
    {},
    { 'data-section': 'verification' },
  )}${label(k, 20, 48, verificationY + 24, 904, verificationHeading, HEADING)}`;
  const checksY = verificationY + 44 + verificationHeading;
  const checkNames = [
    'environment-assertions',
    'actions',
    'communicated-info',
    'natural-language-assertions',
  ];
  checkRows.forEach((rows, index) => {
    output += panel(
      k,
      rows,
      48 + index * (checkWidth + checkGap),
      checksY,
      checkWidth,
      checkMeasures[index],
      {
        fill: '#ffffff',
        padding: 16,
        gap: 8,
        name: checkNames[index],
      },
    );
  });
  output += label(
    k,
    33,
    48,
    checksY + checkHeight + 20,
    904,
    rewardHeight,
    CODE,
  );
  output += '</g>';
  return finish(k, output, 3, verificationY + verificationHeight + 24);
}

export function layoutEmbodiedEvaluation(source, { rtl = false } = {}) {
  const k = figureKit(sourceLabels(source, 10), { rtl });
  const topY = 24;
  const observationX = 24;
  const observationWidth = 240;
  const modelX = 336;
  const modelWidth = 328;
  const simulatorX = 736;
  const simulatorWidth = 240;
  const observationInner = 200;
  const modelInner = 280;
  let output = '';

  const observationHeading = k.height(0, observationInner, HEADING);
  const observationRows = [
    [row(1, TITLE), row(2, CAPTION)],
    [row(3, TITLE), row(4, CAPTION)],
    [row(5, TITLE), row(6, CAPTION)],
    [row(7, CODE)],
  ];
  const observationMeasures = observationRows.map((rows, index) =>
    metrics(k, rows, observationInner, {
      padding: 16,
      gap: 8,
      min: index < 3 ? 88 : 72,
    }),
  );
  const observationContentHeight =
    24 +
    observationHeading +
    20 +
    observationMeasures.reduce((sum, item) => sum + item.height, 0) +
    16 * (observationMeasures.length - 1) +
    24;

  const modelHeading = k.height(8, modelInner, HEADING);
  const modelRows = [
    [row(9, TITLE), row(10, CAPTION)],
    [row(11, TITLE), row(12, CAPTION)],
    [row(13, TITLE), row(14), row(15, CODE)],
    [row(16, TITLE)],
  ];
  const modelMeasures = modelRows.map((rows, index) =>
    metrics(k, rows, modelInner, {
      padding: 16,
      gap: 8,
      min: index === 2 ? 132 : 88,
    }),
  );
  const modelContentHeight =
    24 +
    modelHeading +
    20 +
    modelMeasures.reduce((sum, item) => sum + item.height, 0) +
    64 * (modelMeasures.length - 1) +
    24;

  const simulatorHeading = k.height(17, observationInner, HEADING);
  const simulatorRows = [
    [row(18, TITLE), row(19)],
    [row(20, TITLE), row(21)],
    [row(22, TITLE), row(23)],
  ];
  const simulatorMeasures = simulatorRows.map((rows) =>
    metrics(k, rows, observationInner, {
      padding: 16,
      gap: 8,
      min: 104,
    }),
  );
  const simulatorContentHeight =
    24 +
    simulatorHeading +
    20 +
    simulatorMeasures.reduce((sum, item) => sum + item.height, 0) +
    16 * (simulatorMeasures.length - 1) +
    24;
  const baseTopHeight = Math.max(
    observationContentHeight,
    modelContentHeight,
    simulatorContentHeight,
    640,
  );
  const actionCaption = k.height(24, modelInner, CAPTION);
  const observationCaption = k.height(25, observationInner, CAPTION);
  const flowBandHeight = 40 + actionCaption + observationCaption;
  const topHeight = baseTopHeight + flowBandHeight;

  output += `<g data-section="multimodal-observation">${card(
    k,
    observationX,
    topY,
    observationWidth,
    topHeight,
    { fill: '#ffffff', dash: true },
    { 'data-section': 'multimodal-observation' },
  )}${label(
    k,
    0,
    observationX + 20,
    topY + 24,
    observationInner,
    observationHeading,
    HEADING,
  )}`;
  let cursor = topY + 44 + observationHeading;
  const observationNames = [
    'head-camera',
    'left-wrist-camera',
    'right-wrist-camera',
    'joint-state',
  ];
  const observationCenters = [];
  observationRows.forEach((rows, index) => {
    output += panel(
      k,
      rows,
      observationX + 20,
      cursor,
      observationInner,
      observationMeasures[index],
      {
        fill: index === 3 ? '#f7f9fc' : '#f0f0f0',
        padding: 16,
        gap: 8,
        name: observationNames[index],
      },
    );
    observationCenters.push(cursor + observationMeasures[index].height / 2);
    cursor += observationMeasures[index].height + 16;
  });
  output += '</g>';

  output += `<g data-section="vla-model">${card(
    k,
    modelX,
    topY,
    modelWidth,
    topHeight,
    { fill: '#ffffff', dash: true },
    { 'data-section': 'vla-model' },
  )}${label(k, 8, modelX + 24, topY + 24, modelInner, modelHeading, HEADING)}`;
  cursor = topY + 44 + modelHeading;
  const modelNames = [
    'vision-encoder',
    'language-model',
    'action-decoder',
    'instruction',
  ];
  modelRows.forEach((rows, index) => {
    output += panel(
      k,
      rows,
      modelX + 24,
      cursor,
      modelInner,
      modelMeasures[index],
      {
        fill:
          index === 0 || index === 2
            ? '#d0d0d0'
            : index === 3
              ? '#ffffff'
              : '#f0f0f0',
        padding: 16,
        gap: 8,
        name: modelNames[index],
      },
    );
    if (index < 3) {
      const fromBottom = cursor + modelMeasures[index].height;
      const nextY = fromBottom + 64;
      output += edge(
        k,
        ['vision-to-language', 'language-to-action', 'instruction-to-action'][
          index
        ],
        ['vision-encoder', 'language-model', 'instruction'][index],
        ['language-model', 'action-decoder', 'action-decoder'][index],
        index < 2
          ? `M500 ${fromBottom + 8} L500 ${nextY - 8}`
          : `M540 ${nextY - 8} L540 ${fromBottom + 8}`,
      );
      cursor = nextY;
    }
  });
  output += '</g>';

  output += `<g data-section="simulator">${card(
    k,
    simulatorX,
    topY,
    simulatorWidth,
    topHeight,
    { fill: '#ffffff', dash: true },
    { 'data-section': 'simulator' },
  )}${label(
    k,
    17,
    simulatorX + 20,
    topY + 24,
    observationInner,
    simulatorHeading,
    HEADING,
  )}`;
  cursor = topY + 44 + simulatorHeading;
  const simulatorNames = [
    'dual-arm-robot',
    'environment-randomization',
    'physics-simulation',
  ];
  simulatorRows.forEach((rows, index) => {
    output += panel(
      k,
      rows,
      simulatorX + 20,
      cursor,
      observationInner,
      simulatorMeasures[index],
      {
        fill: index === 1 ? '#d0d0d0' : '#f0f0f0',
        padding: 16,
        gap: 8,
        name: simulatorNames[index],
      },
    );
    cursor += simulatorMeasures[index].height + 16;
  });
  output += '</g>';

  output += edge(
    k,
    'head-camera-to-vla',
    'head-camera',
    'vla-model',
    `M272 ${observationCenters[0]} L328 ${observationCenters[0]}`,
    { gutter: 72 },
  );
  output += edge(
    k,
    'joint-state-to-vla',
    'joint-state',
    'vla-model',
    `M272 ${observationCenters[3]} L328 ${observationCenters[3]}`,
    { gutter: 72 },
  );
  const actionCaptionY = topY + baseTopHeight + 16;
  const actionY = actionCaptionY + actionCaption / 2;
  const observationCaptionY = actionCaptionY + actionCaption + 8;
  const observationY = observationCaptionY + observationCaption / 2;
  output += label(
    k,
    24,
    modelX + 24,
    actionCaptionY,
    modelInner,
    actionCaption,
    CAPTION,
  ).replace(
    '<foreignObject ',
    '<foreignObject data-arrow-caption="model-to-simulator" ',
  );
  output += edge(
    k,
    'model-to-simulator',
    'action-decoder',
    'simulator',
    `M672 ${actionY} L728 ${actionY}`,
    { gutter: 72 },
  );
  output += label(
    k,
    25,
    simulatorX + 20,
    observationCaptionY,
    observationInner,
    observationCaption,
    CAPTION,
  ).replace(
    '<foreignObject ',
    '<foreignObject data-arrow-caption="simulator-to-model" ',
  );
  output += edge(
    k,
    'simulator-to-model',
    'simulator',
    'vision-encoder',
    `M728 ${observationY} L672 ${observationY}`,
    { gutter: 72 },
  );

  const headingY = topY + topHeight + 40;
  output += `<line data-divider="evaluation-metrics" x1="24" y1="${headingY - 20}" x2="976" y2="${headingY - 20}" stroke="#999999" stroke-width="2" stroke-dasharray="6 5"/>`;
  const metricHeading = k.height(26, 952, HEADING);
  output += label(k, 26, 24, headingY, 952, metricHeading, HEADING);
  const metricRows = [
    [row(27, TITLE), row(28, CAPTION), row(29, CAPTION)],
    [row(30, TITLE), row(31, CAPTION), row(32, CAPTION)],
    [row(33, TITLE), row(34, CAPTION), row(35, CAPTION)],
    [row(36, TITLE), row(37, CAPTION), row(38, CAPTION)],
  ];
  const metricGap = 16;
  const metricWidth = (952 - metricGap * 3) / 4;
  const metricMeasures = metricRows.map((rows) =>
    metrics(k, rows, metricWidth, { padding: 16, gap: 8, min: 156 }),
  );
  const metricHeight = Math.max(...metricMeasures.map((item) => item.height));
  metricMeasures.forEach((item) => (item.height = metricHeight));
  const metricsY = headingY + metricHeading + 20;
  const metricNames = [
    'success-rate',
    'completion-time',
    'generalization',
    'sim-to-real',
  ];
  metricRows.forEach((rows, index) => {
    output += panel(
      k,
      rows,
      24 + index * (metricWidth + metricGap),
      metricsY,
      metricWidth,
      metricMeasures[index],
      { padding: 16, gap: 8, name: metricNames[index] },
    );
  });
  return finish(k, output, 10, metricsY + metricHeight + 24);
}
