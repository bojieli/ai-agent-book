import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

// Web-only reflows for the voice architecture figures in Chapter 6. The
// localized SVGs remain the source of every visible label.
const WIDTH = 1000;
const SECTION = { size: 20, bold: true };
const TITLE = { size: 18, bold: true };
const BODY = { size: 16 };
const BODY_BOLD = { size: 16, bold: true };
const CAPTION = { size: 14, muted: true };

const sourceVariants = {
  6: {
    labels: [23],
    viewBoxes: ['0 40 780 300'],
    shape: { rect: 12, line: 3, path: 4, circle: 0, marker: 2 },
  },
  7: {
    labels: [19],
    viewBoxes: ['0 40 780 380'],
    shape: { rect: 13, line: 6, path: 0, circle: 0, marker: 2 },
  },
  8: {
    labels: [22],
    viewBoxes: ['0 40 780 360'],
    shape: { rect: 1, line: 21, path: 1, circle: 3, marker: 2 },
  },
  9: {
    labels: [46],
    viewBoxes: ['0 40 780 480'],
    shape: { rect: 10, line: 0, path: 0, circle: 0, marker: 2 },
  },
  10: {
    labels: [24],
    viewBoxes: ['0 40 780 430'],
    shape: { rect: 8, line: 3, path: 0, circle: 0, marker: 2 },
  },
};

function count(source, tag) {
  return (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
}

function guardSource(source, figure, labels) {
  const variant = sourceVariants[figure];
  const viewBox = source.match(/<svg\b[^>]*\bviewBox="([^"]+)"/)?.[1];
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !variant.viewBoxes.includes(viewBox) ||
    !variant.labels.includes(labels.length) ||
    !Object.entries(variant.shape).every(
      ([tag, expected]) => count(source, tag) === expected,
    )
  )
    throw new Error(
      `Figure 6-${figure} source structure changed; review its web layout.`,
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
      `<svg data-layout="voice-architecture" data-figure="6-${figure}" `,
    );
}

function stackedCard(k, ids, x, y, width, options = {}) {
  const [title, ...body] = ids;
  const innerWidth = width - 40;
  const titleHeight = k.height(title, innerWidth, options.titleStyle ?? TITLE);
  const bodyStyles = body.map(
    (_, index) => options.bodyStyles?.[index] ?? BODY,
  );
  const bodyHeights = body.map((id, index) =>
    k.height(id, innerWidth, bodyStyles[index]),
  );
  const height =
    options.height ??
    40 +
      titleHeight +
      (body.length ? 14 : 0) +
      bodyHeights.reduce((sum, value) => sum + value, 0) +
      Math.max(0, body.length - 1) * 8;
  let output = k.card(x, y, width, height, {
    fill: options.fill ?? '#f0f0f0',
    dash: options.dash,
  });
  output += k.label(title, x + 20, y + 20, innerWidth, titleHeight, {
    ...(options.titleStyle ?? TITLE),
    align: options.align ?? 'center',
  });
  let cursor = y + 20 + titleHeight + 14;
  body.forEach((id, index) => {
    output += k.label(id, x + 20, cursor, innerWidth, bodyHeights[index], {
      ...bodyStyles[index],
      align: options.align ?? 'center',
    });
    cursor += bodyHeights[index] + 8;
  });
  return { height, output };
}

function layoutSerialPipeline(k) {
  const stages = [
    { key: 'vad', ids: [0, 1, 2, 3, 4], strong: true },
    { key: 'asr', ids: [5, 6, 7, 8, 9] },
    { key: 'llm', ids: [10, 11, 12, 13, 14] },
    { key: 'tts', ids: [15, 16, 17, 18, 19] },
  ];
  const cardWidth = 208;
  const innerWidth = cardWidth - 40;
  const metrics = stages.map((stage) => ({
    ...stage,
    titleHeight: k.height(stage.ids[0], innerWidth, TITLE),
    subtitleHeight: k.height(stage.ids[1], innerWidth, BODY),
    durationHeight: k.height(stage.ids[2], innerWidth - 24, BODY_BOLD),
    detailHeights: stage.ids
      .slice(3)
      .map((id) => k.height(id, innerWidth, BODY)),
  }));
  const cardHeight = Math.max(
    ...metrics.map(
      (stage) =>
        44 +
        stage.titleHeight +
        stage.subtitleHeight +
        stage.durationHeight +
        stage.detailHeights.reduce((sum, value) => sum + value, 0) +
        42,
    ),
  );
  const y = 24;
  let content = '';
  metrics.forEach((stage, index) => {
    const x = 24 + index * 248;
    content += `<g data-pipeline-stage="${index + 1}" data-node="${stage.key}">`;
    content += k.card(x, y, cardWidth, cardHeight, {
      fill: stage.strong ? '#d0d0d0' : '#f0f0f0',
    });
    let cursor = y + 20;
    content += k.label(
      stage.ids[0],
      x + 20,
      cursor,
      innerWidth,
      stage.titleHeight,
      TITLE,
    );
    cursor += stage.titleHeight + 8;
    content += k.label(
      stage.ids[1],
      x + 20,
      cursor,
      innerWidth,
      stage.subtitleHeight,
      BODY,
    );
    cursor += stage.subtitleHeight + 14;
    content += k.card(
      x + 32,
      cursor,
      innerWidth - 24,
      stage.durationHeight + 16,
      {
        fill: '#ffffff',
      },
    );
    content += k.label(
      stage.ids[2],
      x + 44,
      cursor + 8,
      innerWidth - 48,
      stage.durationHeight,
      BODY_BOLD,
    );
    cursor += stage.durationHeight + 28;
    stage.ids.slice(3).forEach((id, detailIndex) => {
      content += k.label(
        id,
        x + 20,
        cursor,
        innerWidth,
        stage.detailHeights[detailIndex],
        BODY,
      );
      cursor += stage.detailHeights[detailIndex] + 6;
    });
    content += '</g>';
    if (index < stages.length - 1)
      content += edge(
        k,
        `${stage.key}-to-${stages[index + 1].key}`,
        stage.key,
        stages[index + 1].key,
        `M${x + cardWidth + 8} ${y + cardHeight / 2} L${x + 240} ${y + cardHeight / 2}`,
        { 'data-gutter-size': 40 },
      );
  });
  let cursor = y + cardHeight + 40;
  const headingHeight = k.height(20, 904, SECTION);
  const bodyHeight = k.height(21, 904, BODY);
  const captionHeight = k.height(22, 904, CAPTION);
  const summaryHeight = 40 + headingHeight + bodyHeight + captionHeight + 28;
  content += `<g data-serial-summary="true">${k.card(
    24,
    cursor,
    952,
    summaryHeight,
    { fill: '#ffffff', dash: true },
  )}`;
  content += k.label(20, 48, cursor + 20, 904, headingHeight, SECTION);
  content += k.label(
    21,
    48,
    cursor + 28 + headingHeight,
    904,
    bodyHeight,
    BODY,
  );
  content += k.label(
    22,
    48,
    cursor + 36 + headingHeight + bodyHeight,
    904,
    captionHeight,
    CAPTION,
  );
  content += '</g>';
  return finish(k, content, 6, cursor + summaryHeight + 24);
}

const timelineStages = [
  { key: 'vad-wait', label: 0, duration: 1, start: 0, min: 500, max: 800 },
  { key: 'asr', label: 2, duration: 3, start: 500, min: 50, max: 200 },
  { key: 'llm-ttft', label: 4, duration: 5, start: 550, min: 100, max: 500 },
  {
    key: 'llm-generation',
    label: 6,
    duration: 7,
    start: 650,
    min: 100,
    max: 300,
  },
  { key: 'tts', label: 8, duration: 9, start: 750, min: 200, max: 500 },
];

function layoutLatencyTimeline(k) {
  const plotX = 270;
  const plotWidth = 670;
  const scale = plotWidth / 2300;
  let y = 24;
  let content = `<g data-chart="serial-latency" data-axis-min="0" data-axis-max="2300" data-best-total-ms="950" data-worst-total-ms="2300">`;
  for (const stage of timelineStages) {
    const labelHeight = k.height(stage.label, 214, BODY_BOLD);
    const durationHeight = k.height(stage.duration, 154, CAPTION);
    const rowHeight = Math.max(52, labelHeight, durationHeight);
    content += `<g data-latency-stage="${stage.key}" data-start-ms="${stage.start}" data-min-ms="${stage.min}" data-max-ms="${stage.max}">`;
    content += k.label(
      stage.label,
      24,
      y + (rowHeight - labelHeight) / 2,
      214,
      labelHeight,
      { ...BODY_BOLD, align: 'right' },
    );
    const barX = plotX + stage.start * scale;
    content += `<rect data-duration-range="maximum" x="${barX}" y="${y + 7}" width="${stage.max * scale}" height="38" rx="6" fill="#e0e0e0" stroke="#999999" stroke-width="1.5"/>`;
    content += `<rect data-duration-range="minimum" x="${barX}" y="${y + 7}" width="${stage.min * scale}" height="38" rx="6" fill="#d0d0d0" stroke="#666666" stroke-width="1.5"/>`;
    content += k.label(
      stage.duration,
      barX + stage.max * scale + 12,
      y + (rowHeight - durationHeight) / 2,
      154,
      durationHeight,
      { ...CAPTION, align: 'left' },
    );
    content += '</g>';
    y += rowHeight + 14;
  }
  const axisY = y + 6;
  content += `<line data-time-axis="true" x1="${plotX}" y1="${axisY}" x2="${plotX + plotWidth}" y2="${axisY}" stroke="#666666" stroke-width="2"/>`;
  [0, 500, 1000, 1500, 2000].forEach((value, index) => {
    const x = plotX + value * scale;
    content += `<line data-time-tick="${value}" x1="${x}" y1="${axisY - 6}" x2="${x}" y2="${axisY + 6}" stroke="#666666" stroke-width="2"/>`;
    content += k.label(10 + index, x - 45, axisY + 12, 90, 28, CAPTION);
  });
  content += '</g>';

  y = axisY + 64;
  const headingHeight = k.height(15, 904, SECTION);
  content += k.label(15, 48, y, 904, headingHeight, SECTION);
  y += headingHeight + 18;
  const summaries = [
    { id: 16, kind: 'best', fill: '#d0d0d0' },
    { id: 17, kind: 'worst', fill: '#e0e0e0' },
    { id: 18, kind: 'context', fill: '#ffffff' },
  ].map((item) => ({
    ...item,
    height: k.height(item.id, 264, item.kind === 'context' ? CAPTION : TITLE),
  }));
  const cardHeight = Math.max(...summaries.map((item) => item.height)) + 32;
  summaries.forEach((item, index) => {
    const x = 24 + index * 324;
    content += `<g data-response-summary="${item.kind}">${k.card(
      x,
      y,
      304,
      cardHeight,
      { fill: item.fill },
    )}${k.label(
      item.id,
      x + 20,
      y + 16,
      264,
      item.height,
      item.kind === 'context' ? CAPTION : TITLE,
    )}</g>`;
  });
  return finish(k, content, 7, y + cardHeight + 24);
}

function layoutUtilizationCurve(k) {
  const plot = { x: 130, y: 72, width: 620, height: 360 };
  const px = (rho) => plot.x + rho * plot.width;
  const py = (latency) => plot.y + plot.height - (latency / 12) * plot.height;
  let content = `<g data-chart="utilization-latency" data-formula="S/(1-rho)" data-idle-latency-s="1" data-x-min="0" data-x-max="1" data-y-min="0" data-y-max="12">`;
  const yTitleHeight = k.height(1, plot.width, TITLE);
  content += k.label(1, plot.x, 24, plot.width, yTitleHeight, TITLE);
  content += `<rect x="${plot.x}" y="${plot.y}" width="${plot.width}" height="${plot.height}" fill="#ffffff" stroke="#999999" stroke-width="1.5"/>`;
  [0, 2, 4, 6, 8, 10, 12].forEach((value, index) => {
    const y = py(value);
    content += `<line data-y-grid="${value}" x1="${plot.x}" y1="${y}" x2="${plot.x + plot.width}" y2="${y}" stroke="${value === 0 ? '#666666' : '#e0e0e0'}" stroke-width="${value === 0 ? 2 : 1.5}"${value === 0 ? '' : ' stroke-dasharray="6 5"'}/>`;
    content += k.label(8 + index, 76, y - 14, 42, 28, {
      ...CAPTION,
      align: 'right',
    });
  });
  [0, 0.2, 0.4, 0.6, 0.8, 1].forEach((value, index) => {
    const x = px(value);
    content += `<line data-x-tick="${value}" x1="${x}" y1="${plot.y + plot.height}" x2="${x}" y2="${plot.y + plot.height + 7}" stroke="#666666" stroke-width="2"/>`;
    content += k.label(
      2 + index,
      x - 34,
      plot.y + plot.height + 12,
      68,
      28,
      CAPTION,
    );
  });
  const overflowRho = 11 / 12;
  const points = Array.from({ length: 37 }, (_, index) => index * 0.025)
    .map((rho) => [rho, 1 / (1 - rho)])
    .concat([[overflowRho, 12]]);
  const curve = points
    .map(
      ([rho, latency], index) =>
        `${index ? 'L' : 'M'}${px(rho).toFixed(2)} ${py(latency).toFixed(2)}`,
    )
    .join(' ');
  content += `<path data-series="queue-latency" data-samples="38" data-overflow-rho="${overflowRho}" d="${curve}" fill="none" stroke="#333333" stroke-width="3"/>`;
  content += '</g>';

  const annotations = [
    {
      rho: overflowRho,
      latency: 12,
      labels: [19],
      key: 'saturation',
      boundary: true,
    },
    { rho: 0.8, latency: 5, labels: [17, 18], key: 'unacceptable' },
    { rho: 0.5, latency: 2, labels: [15, 16], key: 'tolerance' },
  ];
  let annotationY = 88;
  annotations.forEach((annotation) => {
    const heights = annotation.labels.map((id, index) =>
      k.height(id, 176, index === 0 ? BODY_BOLD : CAPTION),
    );
    const height = 24 + heights.reduce((sum, value) => sum + value, 0) + 8;
    const pointX = px(annotation.rho);
    const pointY = py(annotation.latency);
    const boundary = annotation.boundary
      ? ' data-overflow-boundary="y-max"'
      : '';
    const calloutCenterY = annotationY + height / 2;
    content += `<circle data-curve-point="${annotation.key}" data-rho="${annotation.rho}" data-latency-s="${annotation.latency}"${boundary} cx="${pointX}" cy="${pointY}" r="5" fill="#333333"/>`;
    content += `<path data-annotation-line="${annotation.key}" data-route="right-elbow" d="M${pointX + 7} ${pointY} H758 V${calloutCenterY} H766" fill="none" stroke="#999999" stroke-width="1.5"/>`;
    content += `<g data-curve-annotation="${annotation.key}">${k.card(
      774,
      annotationY,
      202,
      height,
      { fill: '#f5f5f5' },
    )}`;
    let cursor = annotationY + 12;
    annotation.labels.forEach((id, index) => {
      content += k.label(id, 787, cursor, 176, heights[index], {
        ...(index === 0 ? BODY_BOLD : CAPTION),
        align: 'left',
      });
      cursor += heights[index] + 4;
    });
    content += '</g>';
    annotationY += height + 20;
  });
  const xTitleHeight = k.height(0, plot.width, TITLE);
  let y = plot.y + plot.height + 48;
  content += k.label(0, plot.x, y, plot.width, xTitleHeight, TITLE);
  y += xTitleHeight + 24;
  const formulaHeight = k.height(20, 904, TITLE);
  const contextHeight = k.height(21, 904, BODY);
  content += `<g data-chart-caption="true">${k.card(
    24,
    y,
    952,
    40 + formulaHeight + contextHeight + 8,
    { fill: '#f0f0f0' },
  )}`;
  content += k.label(20, 48, y + 20, 904, formulaHeight, TITLE);
  content += k.label(21, 48, y + 28 + formulaHeight, 904, contextHeight, BODY);
  content += '</g>';
  return finish(k, content, 8, y + 64 + formulaHeight + contextHeight);
}

function layoutRealtimeComparison(k, rtl) {
  const products = [
    { key: 'openai-realtime', ids: [0, 1, 2, 3, 4, 5, 6] },
    { key: 'gemini-live', ids: [7, 8, 9, 10, 11, 12] },
    { key: 'qwen3-omni', ids: [13, 14, 15, 16, 17, 18], strong: true },
    { key: 'step-audio-2', ids: [19, 20, 21, 22, 23, 24] },
  ];
  const width = 464;
  const innerWidth = width - 40;
  const productMetrics = products.map((product) => ({
    ...product,
    titleHeight: k.height(product.ids[0], innerWidth, TITLE),
    modelHeight: k.height(product.ids[1], innerWidth - 32, BODY_BOLD),
    detailHeights: product.ids
      .slice(2)
      .map((id) => k.height(id, innerWidth, BODY)),
  }));
  const rowHeights = [0, 1].map((row) =>
    Math.max(
      ...productMetrics
        .slice(row * 2, row * 2 + 2)
        .map(
          (product) =>
            60 +
            product.titleHeight +
            product.modelHeight +
            product.detailHeights.reduce((sum, value) => sum + value, 0) +
            product.detailHeights.length * 6,
        ),
    ),
  );
  let content = '';
  let y = 24;
  productMetrics.forEach((product, index) => {
    const row = Math.floor(index / 2);
    const x = 24 + (index % 2) * 488;
    const cardY = y + (row === 1 ? rowHeights[0] + 20 : 0);
    const height = rowHeights[row];
    content += `<g data-realtime-product="${product.key}">${k.card(
      x,
      cardY,
      width,
      height,
      { fill: product.strong ? '#d0d0d0' : '#f0f0f0' },
    )}`;
    let cursor = cardY + 20;
    content += k.label(
      product.ids[0],
      x + 20,
      cursor,
      innerWidth,
      product.titleHeight,
      TITLE,
    );
    cursor += product.titleHeight + 12;
    content += k.card(
      x + 36,
      cursor,
      innerWidth - 32,
      product.modelHeight + 16,
      {
        fill: '#ffffff',
      },
    );
    content += k.label(
      product.ids[1],
      x + 52,
      cursor + 8,
      innerWidth - 64,
      product.modelHeight,
      BODY_BOLD,
    );
    cursor += product.modelHeight + 28;
    product.ids.slice(2).forEach((id, detailIndex) => {
      content += k.label(
        id,
        x + 20,
        cursor,
        innerWidth,
        product.detailHeights[detailIndex],
        { ...BODY, muted: detailIndex === product.detailHeights.length - 1 },
      );
      cursor += product.detailHeights[detailIndex] + 6;
    });
    content += '</g>';
  });
  y += rowHeights[0] + rowHeights[1] + 52;

  const limitationHeadingHeight = k.height(25, 904, SECTION);
  content += k.label(25, 48, y, 904, limitationHeadingHeight, SECTION);
  y += limitationHeadingHeight + 18;
  const limitations = [
    { key: 'turn-detection', ids: [26, 27, 28] },
    { key: 'interruption', ids: [29, 30, 31] },
    { key: 'root-cause', ids: [32, 33, 34] },
  ];
  const limitationCards = limitations.map((item) => ({
    ...item,
    card: stackedCard(k, item.ids, 0, 0, 304, {
      titleStyle: TITLE,
      bodyStyles: [BODY, BODY],
    }),
  }));
  const limitationHeight = Math.max(
    ...limitationCards.map((item) => item.card.height),
  );
  limitationCards.forEach((item, index) => {
    const x = 24 + index * 324;
    const card = stackedCard(k, item.ids, x, y, 304, {
      height: limitationHeight,
      titleStyle: TITLE,
      bodyStyles: [BODY, BODY],
      align: rtl ? 'right' : 'center',
      fill: '#ffffff',
    });
    content += `<g data-common-limitation="${item.key}">${card.output}</g>`;
  });
  y += limitationHeight + 40;

  const architectureHeadingHeight = k.height(35, 904, SECTION);
  content += k.label(35, 48, y, 904, architectureHeadingHeight, SECTION);
  y += architectureHeadingHeight + 18;
  const rows = [
    [36, 37],
    [38, 39],
    [40, 41],
    [42, 43],
    [44, 45],
  ];
  rows.forEach(([name, flow], index) => {
    const nameHeight = k.height(name, 224, BODY_BOLD);
    const flowHeight = k.height(flow, 638, BODY);
    const rowHeight = Math.max(nameHeight, flowHeight) + 28;
    content += `<g data-architecture-row="${index + 1}">${k.card(
      24,
      y,
      952,
      rowHeight,
      { fill: index === 4 ? '#d0d0d0' : '#f0f0f0' },
    )}`;
    content += k.label(name, 44, y + 14, 224, nameHeight, {
      ...BODY_BOLD,
      align: rtl ? 'right' : 'left',
    });
    content += k.label(flow, 298, y + 14, 658, flowHeight, {
      ...BODY,
      align: rtl ? 'right' : 'left',
    });
    content += '</g>';
    y += rowHeight + 10;
  });
  return finish(k, content, 9, y + 14);
}

function layoutParallelThinking(k, rtl) {
  let content = '';
  let y = 24;
  const input = stackedCard(k, [0, 1], 250, y, 500, {
    fill: '#d0d0d0',
    titleStyle: TITLE,
    bodyStyles: [BODY],
  });
  content += `<g data-node="user-input">${input.output}</g>`;
  const inputBottom = y + input.height;
  const parallelY = inputBottom + 64;
  const parallelHeadingHeight = k.height(2, 792, SECTION);
  const thoughtWidth = 384;
  const thoughtIds = [
    { key: 'fast-thinking', ids: [3, 4], fill: '#f0f0f0' },
    { key: 'slow-thinking', ids: [5, 6], fill: '#e0e0e0' },
  ];
  const thoughtMetrics = thoughtIds.map((thought) =>
    stackedCard(k, thought.ids, 0, 0, thoughtWidth, {
      titleStyle: TITLE,
      bodyStyles: [BODY],
    }),
  );
  const thoughtHeight = Math.max(...thoughtMetrics.map((card) => card.height));
  const thoughtY = parallelY + 20 + parallelHeadingHeight + 18;
  const parallelHeight = 40 + parallelHeadingHeight + 18 + thoughtHeight;
  content += `<g data-node="parallel-thinking">${k.card(
    80,
    parallelY,
    840,
    parallelHeight,
    { fill: '#ffffff', dash: true },
  )}`;
  content += k.label(2, 104, parallelY + 20, 792, parallelHeadingHeight, {
    ...SECTION,
    align: rtl ? 'right' : 'left',
  });
  thoughtIds.forEach((thought, index) => {
    const x = 104 + index * 408;
    const card = stackedCard(k, thought.ids, x, thoughtY, thoughtWidth, {
      height: thoughtHeight,
      fill: thought.fill,
      titleStyle: TITLE,
      bodyStyles: [BODY],
    });
    content += `<g data-thought-path="${thought.key}">${card.output}</g>`;
  });
  content += '</g>';
  content += edge(
    k,
    'input-to-parallel-thinking',
    'user-input',
    'parallel-thinking',
    `M500 ${inputBottom + 8} L500 ${parallelY - 8}`,
    { 'data-gutter-size': 64 },
  );

  const parallelBottom = parallelY + parallelHeight;
  const thoughtBottom = thoughtY + thoughtHeight;
  const experienceY = parallelBottom + 88;
  const experience = stackedCard(k, [7, 8, 9, 10, 11], 200, experienceY, 600, {
    fill: '#f5f5f5',
    titleStyle: SECTION,
    bodyStyles: [BODY, BODY, BODY_BOLD, BODY],
  });
  content += `<g data-node="user-experience">${experience.output}</g>`;
  const routeY = parallelBottom + 40;
  content += edge(
    k,
    'fast-thinking-to-experience',
    'fast-thinking',
    'user-experience',
    `M296 ${thoughtBottom + 8} V${routeY} H400 V${experienceY - 8}`,
    { 'data-gutter-size': 88 },
  );
  content += edge(
    k,
    'slow-thinking-to-experience',
    'slow-thinking',
    'user-experience',
    `M704 ${thoughtBottom + 8} V${routeY} H600 V${experienceY - 8}`,
    { 'data-gutter-size': 88 },
  );

  y = experienceY + experience.height + 40;
  const issuesHeadingHeight = k.height(12, 904, SECTION);
  content += k.label(12, 48, y, 904, issuesHeadingHeight, SECTION);
  y += issuesHeadingHeight + 18;
  const issues = [
    { key: 'overthinking', ids: [13, 14] },
    { key: 'inconsistency', ids: [15, 16] },
  ];
  const issueMetrics = issues.map((issue) =>
    stackedCard(k, issue.ids, 0, 0, 464, {
      titleStyle: TITLE,
      bodyStyles: [BODY],
    }),
  );
  const issueHeight = Math.max(...issueMetrics.map((card) => card.height));
  issues.forEach((issue, index) => {
    const x = 24 + index * 488;
    const card = stackedCard(k, issue.ids, x, y, 464, {
      height: issueHeight,
      titleStyle: TITLE,
      bodyStyles: [BODY],
      fill: '#f0f0f0',
    });
    content += `<g data-issue="${issue.key}">${card.output}</g>`;
  });

  y += issueHeight + 40;
  const conclusions = [
    {
      key: 'advisor-improvement',
      ids: [17, 18, 19],
      bodyStyles: [BODY, BODY],
      fill: '#f0f0f0',
    },
    {
      key: 'fundamental-limitations',
      ids: [20, [21, 22], 23],
      bodyStyles: [BODY, BODY],
      fill: '#e0e0e0',
    },
  ];
  const conclusionMetrics = conclusions.map((item) => {
    const titleHeight = k.height(item.ids[0], 424, TITLE);
    const bodyHeights = item.ids
      .slice(1)
      .map((ids, index) => k.height(ids, 424, item.bodyStyles[index]));
    return {
      ...item,
      titleHeight,
      bodyHeights,
      height:
        40 +
        titleHeight +
        14 +
        bodyHeights.reduce((sum, value) => sum + value, 0) +
        8,
    };
  });
  const conclusionHeight = Math.max(
    ...conclusionMetrics.map((item) => item.height),
  );
  conclusionMetrics.forEach((item, index) => {
    const x = 24 + index * 488;
    content += `<g data-conclusion="${item.key}">${k.card(
      x,
      y,
      464,
      conclusionHeight,
      { fill: item.fill },
    )}`;
    content += k.label(
      item.ids[0],
      x + 20,
      y + 20,
      424,
      item.titleHeight,
      TITLE,
    );
    let cursor = y + 34 + item.titleHeight;
    item.ids.slice(1).forEach((ids, bodyIndex) => {
      content += k.label(
        ids,
        x + 20,
        cursor,
        424,
        item.bodyHeights[bodyIndex],
        item.bodyStyles[bodyIndex],
      );
      cursor += item.bodyHeights[bodyIndex] + 8;
    });
    content += '</g>';
  });
  return finish(k, content, 10, y + conclusionHeight + 24);
}

export function layoutVoiceArchitecture(
  source,
  figureNumber,
  { rtl = false } = {},
) {
  if (![6, 7, 8, 9, 10].includes(figureNumber))
    throw new Error(`Unsupported voice architecture figure ${figureNumber}`);
  const labels = extractLabels(
    source,
    `6-${figureNumber}`,
    sourceVariants[figureNumber].labels,
  );
  guardSource(source, figureNumber, labels);
  const k = figureKit(labels, { rtl });
  if (figureNumber === 6) return layoutSerialPipeline(k);
  if (figureNumber === 7) return layoutLatencyTimeline(k);
  if (figureNumber === 8) return layoutUtilizationCurve(k);
  if (figureNumber === 9) return layoutRealtimeComparison(k, rtl);
  return layoutParallelThinking(k, rtl);
}
