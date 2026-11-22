import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

// Web-only reflows for the coding-production figures in Chapter 5. The
// localized SVGs remain the source of every label and code example.

const WIDTH = 1000;
const SECTION = { size: 20, bold: true };
const TITLE = { size: 18, bold: true };
const BODY = { size: 16 };
const BODY_BOLD = { size: 16, bold: true };
const CODE = { size: 14, mono: true };
const CAPTION = { size: 14, muted: true };

const sourceVariants = {
  5: {
    labels: [37],
    viewBoxes: ['0 40 880 520', '0 40 884 520'],
    shape: { rect: 10, line: 3, path: 0, polyline: 0, marker: 2, polygon: 2 },
  },
  6: {
    labels: [50],
    viewBoxes: ['0 40 880 480', '0 40 880 520'],
    shape: { rect: 13, line: 20, path: 0, polyline: 0, marker: 2, polygon: 2 },
  },
  7: {
    labels: [50, 51],
    viewBoxes: ['0 40 880 520'],
    shape: { rect: 10, line: 4, path: 0, polyline: 0, marker: 2, polygon: 2 },
  },
};

function count(source, tag) {
  return (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
}

function guardSource(source, figure, labels) {
  const variant = sourceVariants[figure];
  const viewBox = source.match(/<svg\b[^>]*\bviewBox="([^"]+)"/)?.[1];
  const shapeMatches = Object.entries(variant.shape).every(
    ([tag, expected]) => count(source, tag) === expected,
  );
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !variant.viewBoxes.includes(viewBox) ||
    !variant.labels.includes(labels.length) ||
    !shapeMatches
  )
    throw new Error(
      `Figure 5-${figure} source structure changed; review its web layout.`,
    );
}

function tag(element, attributes) {
  return element.replace(
    /^(<\w+)/,
    `$1 ${Object.entries(attributes)
      .map(([name, value]) => `${name}="${value}"`)
      .join(' ')}`,
  );
}

function codeMetrics(k, ids, width) {
  const heights = ids.map((id) =>
    k.height(id, width - 32, { ...CODE, min: 24 }),
  );
  return {
    heights,
    height: 24 + heights.reduce((sum, height) => sum + height, 0),
  };
}

function codeBlock(k, ids, x, y, width, metrics, attributes = {}) {
  let output = `<g ${Object.entries(attributes)
    .map(([name, value]) => `${name}="${value}"`)
    .join(' ')}>`;
  output += k.card(x, y, width, metrics.height, { fill: '#f0f0f0' });
  let lineY = y + 12;
  ids.forEach((id, index) => {
    output += k.label(id, x + 16, lineY, width - 32, metrics.heights[index], {
      ...CODE,
      align: 'left',
      direction: 'ltr',
    });
    lineY += metrics.heights[index];
  });
  return `${output}</g>`;
}

function edge(k, name, from, to, d, extra = {}) {
  return tag(k.path(d, { dash: extra['data-direction'] === 'return' }), {
    'data-edge': name,
    'data-from': from,
    'data-to': to,
    'data-route': 'gutter',
    'data-card-gap-start': 8,
    'data-card-gap-end': 8,
    ...extra,
  });
}

function finish(k, content, figure, height) {
  return k
    .svg(content, height, WIDTH)
    .replace(
      '<svg ',
      `<svg data-layout="coding-production" data-figure="5-${figure}" `,
    );
}

function layoutReviewLoop(labels, rtl, k) {
  const align = rtl ? 'right' : 'left';
  const cardY = 24;
  const cardWidth = 404;
  const innerWidth = cardWidth - 40;

  const proposer = {
    title: k.height(0, innerWidth, TITLE),
    input: k.height(1, innerWidth, BODY_BOLD),
    inputCode: codeMetrics(k, [2], innerWidth),
    output: k.height(3, innerWidth, BODY_BOLD),
    outputCode: codeMetrics(k, [4, 5, 6, 7, 8, 9, 10, 11, 12], innerWidth),
  };
  proposer.height =
    20 +
    proposer.title +
    18 +
    proposer.input +
    8 +
    proposer.inputCode.height +
    18 +
    proposer.output +
    8 +
    proposer.outputCode.height +
    20;

  const reviewer = {
    title: k.height(13, innerWidth, TITLE),
    render: k.height(14, innerWidth, BODY_BOLD),
    renderCode: codeMetrics(k, [15, 16], innerWidth),
    review: k.height(17, innerWidth, BODY_BOLD),
    reviewCode: codeMetrics(k, [18, 19, 20, 21, 22, 23], innerWidth),
  };
  reviewer.height =
    20 +
    reviewer.title +
    18 +
    reviewer.render +
    8 +
    reviewer.renderCode.height +
    18 +
    reviewer.review +
    8 +
    reviewer.reviewCode.height +
    20;

  const cardHeight = Math.max(proposer.height, reviewer.height, 500);
  let content = `<g data-agent="proposer" data-labels="0-12">${tag(
    k.card(24, cardY, cardWidth, cardHeight, { fill: '#ffffff', dash: true }),
    { 'data-agent-card': 'proposer' },
  )}`;
  let y = cardY + 20;
  content += k.label(0, 44, y, innerWidth, proposer.title, TITLE);
  y += proposer.title + 18;
  content += k.label(1, 44, y, innerWidth, proposer.input, {
    ...BODY_BOLD,
    align,
  });
  y += proposer.input + 8;
  content += codeBlock(k, [2], 44, y, innerWidth, proposer.inputCode, {
    'data-code-block': 'proposer-input',
  });
  y += proposer.inputCode.height + 18;
  content += k.label(3, 44, y, innerWidth, proposer.output, {
    ...BODY_BOLD,
    align,
  });
  y += proposer.output + 8;
  content += codeBlock(
    k,
    [4, 5, 6, 7, 8, 9, 10, 11, 12],
    44,
    y,
    innerWidth,
    proposer.outputCode,
    { 'data-code-block': 'proposer-output', 'data-code-lines': 9 },
  );
  content += '</g>';

  content += `<g data-agent="reviewer" data-labels="13-23">${tag(
    k.card(572, cardY, cardWidth, cardHeight, { fill: '#ffffff', dash: true }),
    { 'data-agent-card': 'reviewer' },
  )}`;
  y = cardY + 20;
  content += k.label(13, 592, y, innerWidth, reviewer.title, TITLE);
  y += reviewer.title + 18;
  content += k.label(14, 592, y, innerWidth, reviewer.render, {
    ...BODY_BOLD,
    align,
  });
  y += reviewer.render + 8;
  content += codeBlock(k, [15, 16], 592, y, innerWidth, reviewer.renderCode, {
    'data-code-block': 'reviewer-render',
    'data-code-lines': 2,
  });
  y += reviewer.renderCode.height + 18;
  content += k.label(17, 592, y, innerWidth, reviewer.review, {
    ...BODY_BOLD,
    align,
  });
  y += reviewer.review + 8;
  content += codeBlock(
    k,
    [18, 19, 20, 21, 22, 23],
    592,
    y,
    innerWidth,
    reviewer.reviewCode,
    { 'data-code-block': 'reviewer-analysis', 'data-code-lines': 6 },
  );
  content += '</g>';

  const forwardCaption = k.height(24, 120, CAPTION);
  const returnCaption = k.height(25, 120, CAPTION);
  const iterationText = k.height(26, 104, { size: 14, bold: true });
  const forwardCaptionY = cardY + 92;
  const forwardY = forwardCaptionY + forwardCaption + 8;
  const iterationY = forwardY + 44;
  const returnCaptionY = iterationY + iterationText + 44;
  const returnY = returnCaptionY + returnCaption + 8;
  content += `<g data-review-loop="true" data-gutter-size="144">`;
  content += k
    .label(24, 440, forwardCaptionY, 120, forwardCaption, {
      ...CAPTION,
      direction: rtl ? 'rtl' : 'ltr',
    })
    .replace('<foreignObject ', '<foreignObject data-arrow-caption="24" ');
  content += edge(
    k,
    'proposer-to-reviewer',
    'proposer',
    'reviewer',
    `M436 ${forwardY} L564 ${forwardY}`,
    { 'data-direction': 'forward', 'data-gutter-size': 144 },
  );
  content += tag(
    k.card(436, iterationY, 128, iterationText + 16, { fill: '#d0d0d0' }),
    {
      'data-iteration-badge': 'true',
    },
  );
  content += k.label(26, 448, iterationY + 8, 104, iterationText, {
    size: 14,
    bold: true,
  });
  content += k
    .label(25, 440, returnCaptionY, 120, returnCaption, {
      ...CAPTION,
      direction: rtl ? 'rtl' : 'ltr',
    })
    .replace('<foreignObject ', '<foreignObject data-arrow-caption="25" ');
  content += edge(
    k,
    'reviewer-to-proposer',
    'reviewer',
    'proposer',
    `M564 ${returnY} L436 ${returnY}`,
    { 'data-direction': 'return', 'data-gutter-size': 144 },
  );
  content += '</g>';

  const headingY = cardY + cardHeight + 40;
  const headingHeight = k.height(27, 952, SECTION);
  content += k.label(27, 24, headingY, 952, headingHeight, SECTION);

  const benefits = [
    { title: 28, body: [29, 30], key: 'single-agent-problem' },
    { title: 31, body: [32, 33], key: 'separation-advantages' },
    { title: 34, body: [35, 36], key: 'actual-effect' },
  ].map((benefit) => ({
    ...benefit,
    titleHeight: k.height(benefit.title, 264, TITLE),
    bodyHeights: benefit.body.map((id) => k.height(id, 264, BODY)),
  }));
  const benefitHeight = Math.max(
    ...benefits.map(
      (benefit) =>
        24 +
        benefit.titleHeight +
        16 +
        benefit.bodyHeights.reduce((sum, height) => sum + height, 0) +
        (benefit.body.length - 1) * 10 +
        24,
    ),
  );
  const benefitY = headingY + headingHeight + 20;
  benefits.forEach((benefit, index) => {
    const x = 24 + index * 324;
    content += `<g data-benefit="${benefit.key}">${k.card(
      x,
      benefitY,
      304,
      benefitHeight,
    )}`;
    content += k.label(
      benefit.title,
      x + 20,
      benefitY + 20,
      264,
      benefit.titleHeight,
      TITLE,
    );
    let bodyY = benefitY + 20 + benefit.titleHeight + 16;
    benefit.body.forEach((id, bodyIndex) => {
      content += k.label(
        id,
        x + 20,
        bodyY,
        264,
        benefit.bodyHeights[bodyIndex],
        {
          ...BODY,
          muted: true,
        },
      );
      bodyY += benefit.bodyHeights[bodyIndex] + 10;
    });
    content += '</g>';
  });

  return finish(k, content, 5, benefitY + benefitHeight + 24);
}

function pipelineStage(k, stage, x, y, width, rtl, rowHeight) {
  const innerWidth = width - 40;
  const titleHeight = k.height(stage.title, innerWidth, TITLE);
  const codeIds = new Set([2, 11, 14, 24, 25, 26, 33, 34, 36, 40]);
  const styles = stage.details.map((id) => (codeIds.has(id) ? CODE : BODY));
  const heights = stage.details.map((id, i) =>
    k.height(id, innerWidth, styles[i]),
  );
  const height =
    rowHeight ??
    40 + titleHeight + 16 + heights.reduce((a, b) => a + b, 0) + 12;
  let output = `<g data-pipeline="${stage.pipeline}" data-stage="${stage.order}" data-node="${stage.key}">`;
  output += k.card(x, y, width, height, {
    fill: stage.strong ? '#d0d0d0' : '#f0f0f0',
  });
  output += k.label(stage.title, x + 20, y + 20, innerWidth, titleHeight, {
    ...TITLE,
    align: rtl ? 'right' : 'left',
  });
  let cursor = y + 20 + titleHeight + 16;
  stage.details.forEach((id, i) => {
    output += k.label(id, x + 20, cursor, innerWidth, heights[i], {
      ...styles[i],
      align: rtl ? 'right' : 'left',
      direction: styles[i].mono ? 'ltr' : rtl ? 'rtl' : 'ltr',
    });
    cursor += heights[i] + 6;
  });
  return { output: `${output}</g>`, height };
}

function renderPipeline(k, stages, y, rtl) {
  const width = 444;
  const heights = stages.map(
    (stage) => pipelineStage(k, stage, 0, 0, width, rtl).height,
  );
  const rowHeights = [
    Math.max(heights[0], heights[1]),
    Math.max(heights[2], heights[3]),
    heights[4],
  ];
  const rowY = [y, y + rowHeights[0] + 64];
  rowY.push(rowY[1] + rowHeights[1] + 64);
  const positions = [
    { x: 24, y: rowY[0] },
    { x: 532, y: rowY[0] },
    { x: 532, y: rowY[1] },
    { x: 24, y: rowY[1] },
    { x: 24, y: rowY[2] },
  ];
  const nodes = stages.map((stage, index) => ({
    ...stage,
    ...positions[index],
    width,
    height: rowHeights[Math.floor(index / 2)],
  }));
  let output = nodes
    .map(
      (node) =>
        pipelineStage(k, node, node.x, node.y, width, rtl, node.height).output,
    )
    .join('');
  const routes = [
    `M476 ${nodes[0].y + nodes[0].height / 2} H500 V${nodes[1].y + nodes[1].height / 2} H524`,
    `M754 ${nodes[1].y + nodes[1].height + 8} L754 ${nodes[2].y - 8}`,
    `M524 ${nodes[2].y + nodes[2].height / 2} H500 V${nodes[3].y + nodes[3].height / 2} H476`,
    `M246 ${nodes[3].y + nodes[3].height + 8} L246 ${nodes[4].y - 8}`,
  ];
  for (let index = 0; index < 4; index++)
    output += edge(
      k,
      `${nodes[index].key}-to-${nodes[index + 1].key}`,
      nodes[index].key,
      nodes[index + 1].key,
      routes[index],
      {
        'data-gutter-size':
          index % 2 === 0
            ? 64
            : nodes[index + 1].y - (nodes[index].y + nodes[index].height),
        'data-pipeline': nodes[index].pipeline,
      },
    );
  return { output, bottom: nodes[4].y + nodes[4].height };
}

function phaseHeader(k, id, y) {
  const height = k.height(id, 904, SECTION) + 24;
  return {
    output:
      tag(k.card(24, y, 952, height, { fill: '#d0d0d0' }), {
        'data-phase-header': id === 0 ? 1 : 2,
      }) + k.label(id, 48, y + 12, 904, height - 24, SECTION),
    height,
  };
}

function layoutProductionPipeline(labels, rtl, k) {
  const phaseOne = [
    { title: 1, details: [2, 3, 4], key: 'pdf-input', strong: true },
    { title: 5, details: [6, 7, 8], key: 'content-planning' },
    { title: 9, details: [10, 11, 12], key: 'slidev-generation' },
    { title: 13, details: [14, 15, 16], key: 'rendering-check', strong: true },
    { title: 17, details: [18, 19, 20], key: 'iterative-fix' },
  ].map((stage, index) => ({ ...stage, pipeline: 1, order: index + 1 }));
  const phaseTwo = [
    { title: 23, details: [24, 25, 26], key: 'page-screenshots', strong: true },
    { title: 27, details: [28, 29, 30], key: 'script-generation' },
    { title: 31, details: [32, 33, 34], key: 'tts-synthesis' },
    { title: 35, details: [36, 37, 38], key: 'audio-video-sync', strong: true },
    { title: 39, details: [40, 41, 42], key: 'final-video', strong: true },
  ].map((stage, index) => ({ ...stage, pipeline: 2, order: index + 1 }));

  let y = 24;
  const headerOne = phaseHeader(k, 0, y);
  let content = headerOne.output;
  y += headerOne.height + 24;
  const first = renderPipeline(k, phaseOne, y, rtl);
  content += first.output;

  const phaseCaptionHeight = k.height(21, 400, CAPTION);
  const headerTwoY = first.bottom + Math.max(112, phaseCaptionHeight + 48);
  const connectorStart = first.bottom + 8;
  const connectorEnd = headerTwoY - 8;
  const connectorLane = first.bottom + (headerTwoY - first.bottom) / 2;
  content += edge(
    k,
    'ppt-complete-to-video-phase',
    'iterative-fix',
    'video-phase',
    `M246 ${connectorStart} V${connectorLane} H500 V${connectorEnd}`,
    { 'data-gutter-size': headerTwoY - first.bottom },
  );
  content += k
    .label(
      21,
      536,
      first.bottom + (headerTwoY - first.bottom - phaseCaptionHeight) / 2,
      400,
      phaseCaptionHeight,
      CAPTION,
    )
    .replace(
      '<foreignObject ',
      '<foreignObject data-phase-connector-caption="true" ',
    );
  const headerTwo = phaseHeader(k, 22, headerTwoY);
  content += headerTwo.output;
  y = headerTwoY + headerTwo.height + 24;
  const second = renderPipeline(k, phaseTwo, y, rtl);
  content += second.output;

  const acceptanceY = second.bottom + 40;
  const acceptanceHeading = k.height(43, 952, SECTION);
  content += `<line x1="24" y1="${acceptanceY}" x2="976" y2="${acceptanceY}" stroke="#999999" stroke-width="2" stroke-dasharray="8 6"/>`;
  content += k.label(43, 24, acceptanceY + 20, 952, acceptanceHeading, SECTION);
  y = acceptanceY + 20 + acceptanceHeading + 20;
  const criteria = [
    { badge: 44, body: 45 },
    { badge: 46, body: 47 },
    { badge: 48, body: 49 },
  ].map((criterion) => ({
    ...criterion,
    badgeHeight: k.height(criterion.badge, 180, TITLE),
    bodyHeight: k.height(criterion.body, 652, BODY),
  }));
  for (const [index, criterion] of criteria.entries()) {
    const height = Math.max(criterion.badgeHeight, criterion.bodyHeight) + 28;
    content += `<g data-acceptance-criterion="${index + 1}">${k.card(
      52,
      y,
      896,
      height,
      { fill: index === 2 ? '#d0d0d0' : '#f0f0f0' },
    )}`;
    content += k.label(criterion.badge, 72, y + 14, 180, height - 28, TITLE);
    content += k.label(criterion.body, 276, y + 14, 652, height - 28, {
      ...BODY,
      align: rtl ? 'right' : 'left',
    });
    content += '</g>';
    y += height + 16;
  }

  return finish(k, content, 6, y + 8);
}

function verticalCodeStage(k, stage, y, rtl) {
  const cardX = 48;
  const cardWidth = 904;
  const innerWidth = cardWidth - 40;
  const titleHeight = k.height(stage.title, innerWidth, TITLE);
  const code = codeMetrics(k, stage.lines, innerWidth);
  const height = 20 + titleHeight + 14 + code.height + 20;
  let output = `<g data-production-stage="${stage.order}" data-node="${stage.key}">`;
  output += k.card(cardX, y, cardWidth, height, {
    fill: stage.strong ? '#d0d0d0' : '#ffffff',
    dash: true,
  });
  output += k.label(stage.title, cardX + 20, y + 20, innerWidth, titleHeight, {
    ...TITLE,
    align: rtl ? 'right' : 'left',
  });
  output += codeBlock(
    k,
    stage.lines,
    cardX + 20,
    y + 20 + titleHeight + 14,
    innerWidth,
    code,
    { 'data-stage-code': stage.key, 'data-code-lines': stage.lines.length },
  );
  return { output: `${output}</g>`, height };
}

function layoutRegressionAutomation(labels, rtl, k) {
  const spanishVariant = labels.length === 50;
  const issueEnd = spanishVariant ? 46 : 47;
  const summaryStart = issueEnd + 1;
  const stages = [
    { title: 0, lines: [1, 2, 3, 4, 5, 6, 7, 8], key: 'log-collection' },
    {
      title: 9,
      lines: [10, 11, 12, 13, 14, 15, 16, 17, 18],
      key: 'llm-analysis',
    },
    {
      title: 19,
      lines: [20, 21, 22, 23, 24, 25, 26],
      key: 'structured-report',
    },
    {
      title: 27,
      lines: [28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
      key: 'regression-test',
    },
    {
      title: 38,
      lines: Array.from({ length: issueEnd - 38 }, (_, index) => 39 + index),
      key: 'github-issue',
    },
  ].map((stage, index) => ({ ...stage, order: index + 1 }));

  let y = 24;
  let content = '';
  let previous = null;
  for (const stage of stages) {
    const rendered = verticalCodeStage(k, stage, y, rtl);
    if (previous)
      content += edge(
        k,
        `${previous.key}-to-${stage.key}`,
        previous.key,
        stage.key,
        `M500 ${previous.bottom + 8} L500 ${y - 8}`,
        { 'data-gutter-size': 64 },
      );
    content += rendered.output;
    previous = { key: stage.key, bottom: y + rendered.height };
    y += rendered.height + 64;
  }
  y = previous.bottom + 32;

  const summaryTitle = k.height(summaryStart, 864, SECTION);
  const summaryBody = k.height(summaryStart + 1, 864, BODY);
  const outcome = k.height(summaryStart + 2, 864, BODY_BOLD);
  const summaryHeight =
    24 + summaryTitle + 12 + summaryBody + 12 + outcome + 24;
  content += `<g data-automation-summary="true">${k.card(
    48,
    y,
    904,
    summaryHeight,
    { fill: '#d0d0d0' },
  )}`;
  let summaryY = y + 24;
  content += k.label(summaryStart, 68, summaryY, 864, summaryTitle, SECTION);
  summaryY += summaryTitle + 12;
  content += k.label(summaryStart + 1, 68, summaryY, 864, summaryBody, BODY);
  summaryY += summaryBody + 12;
  content += k.label(summaryStart + 2, 68, summaryY, 864, outcome, BODY_BOLD);
  content += '</g>';

  return finish(k, content, 7, y + summaryHeight + 24);
}

export function layoutCodingProduction(source, figure, { rtl = false } = {}) {
  if (![5, 6, 7].includes(figure))
    throw new Error(`Unsupported coding-production figure: ${figure}`);
  const variant = sourceVariants[figure];
  // Some localized sources use self-closing text elements for intentionally
  // blank code rows. Pair them for extraction while leaving the source intact.
  const extractableSource = source.replace(
    /<text\b([^>]*)\/>/g,
    '<text$1></text>',
  );
  const labels = extractLabels(
    extractableSource,
    `5-${figure}`,
    variant.labels,
  );
  // Preserve source code indentation as layout, without altering label text.
  const indents = [
    ...extractableSource.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map(
    ([, text]) =>
      Math.min(8, text.replace(/<[^>]*>/g, '').match(/^ +/)?.[0].length ?? 0) *
      8.4,
  );
  const base = figureKit(labels, { rtl });
  const inset = (id, options) =>
    options?.mono && !Array.isArray(id) ? indents[id] : 0;
  const k = {
    ...base,
    height(id, width, options) {
      return base.height(id, width - inset(id, options), options);
    },
    label(id, x, y, width, height, options) {
      const shift = inset(id, options);
      return base.label(id, x + shift, y, width - shift, height, options);
    },
  };
  guardSource(source, figure, labels);
  if (figure === 5) return layoutReviewLoop(labels, rtl, k);
  if (figure === 6) return layoutProductionPipeline(labels, rtl, k);
  return layoutRegressionAutomation(labels, rtl, k);
}
