import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

// Web-only reflows for the asynchronous-agent figures in Chapter 6. The
// localized SVG remains the source of every visible label.
const WIDTH = 1000;
const SECTION = { size: 20, bold: true };
const TITLE = { size: 18, bold: true };
const BODY = { size: 16 };
const BODY_BOLD = { size: 16, bold: true };
const CODE = { size: 14, mono: true };
const CAPTION = { size: 14, muted: true };

const variants = {
  1: {
    labels: [39],
    viewBoxes: ['0 40 880 500'],
    shape: { rect: 14, line: 9, path: 1, polygon: 2, marker: 2 },
  },
  2: {
    labels: [28],
    viewBoxes: ['0 40 880 540'],
    shape: { rect: 16, line: 3, path: 0, polygon: 2, marker: 2 },
  },
  3: {
    labels: [43],
    viewBoxes: ['0 40 880 440'],
    shape: { rect: 17, line: 12, path: 0, polygon: 2, marker: 2 },
  },
  4: {
    labels: [18],
    viewBoxes: ['0 40 880 480'],
    shape: { rect: 10, line: 8, path: 0, polygon: 2, marker: 2 },
  },
  5: {
    labels: [22],
    viewBoxes: ['0 0 880 540'],
    shape: { rect: 13, line: 0, path: 7, polygon: 0, marker: 1 },
  },
};

function count(source, tagName) {
  return (source.match(new RegExp(`<${tagName}\\b`, 'g')) || []).length;
}

function guardSource(source, figure, labels) {
  const variant = variants[figure];
  const viewBox = source.match(/<svg\b[^>]*\bviewBox="([^"]+)"/)?.[1];
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !variant.viewBoxes.includes(viewBox) ||
    !variant.labels.includes(labels.length) ||
    !Object.entries(variant.shape).every(
      ([tagName, expected]) => count(source, tagName) === expected,
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

function edge(k, name, from, to, d, { dash = false, gutter = 32 } = {}) {
  return tag(k.path(d, { dash }), {
    'data-edge': name,
    'data-from': from,
    'data-to': to,
    'data-route': 'gutter',
    'data-card-gap-start': 8,
    'data-card-gap-end': 8,
    'data-gutter-size': gutter,
  });
}

function finish(k, content, figure, height) {
  return k
    .svg(content, height, WIDTH)
    .replace(
      '<svg ',
      `<svg data-layout="async-architecture" data-figure="6-${figure}" `,
    );
}

function pairMetrics(k, titleId, bodyIds, width, titleStyle = TITLE) {
  const title = k.height(titleId, width - 32, titleStyle);
  const body = k.height(bodyIds, width - 32, BODY);
  return { title, body, height: 32 + title + 8 + body };
}

function pairCard(
  k,
  titleId,
  bodyIds,
  x,
  y,
  width,
  metrics,
  { fill = '#f0f0f0', attributes = {}, titleStyle = TITLE } = {},
) {
  return `<g ${Object.entries(attributes)
    .map(([name, value]) => `${name}="${value}"`)
    .join(' ')}>${k.card(x, y, width, metrics.height, { fill })}${k.label(
    titleId,
    x + 16,
    y + 16,
    width - 32,
    metrics.title,
    titleStyle,
  )}${k.label(
    bodyIds,
    x + 16,
    y + 24 + metrics.title,
    width - 32,
    metrics.body,
    BODY,
  )}</g>`;
}

function layoutEventArchitecture(k) {
  let out = '';
  let y = 24;
  const sourceTitleH = k.height(0, 904, SECTION);
  const sources = [
    [1, 2, [3, 4]],
    [5, 6, [7, 8]],
    [9, 10, [11, 12]],
    [13, 14, [15, 16]],
  ].map(([titleId, eventId, payloadIds]) => {
    const title = k.height(titleId, 408, TITLE);
    const event = k.height(eventId, 408, CODE);
    const payload = k.height(payloadIds, 408, CODE);
    return { titleId, eventId, payloadIds, title, event, payload };
  });
  const sourceRows = [
    Math.max(
      ...sources
        .slice(0, 2)
        .map((item) => 36 + item.title + item.event + item.payload),
    ),
    Math.max(
      ...sources
        .slice(2)
        .map((item) => 36 + item.title + item.event + item.payload),
    ),
  ];
  const sourceSectionH =
    24 + sourceTitleH + 20 + sourceRows[0] + 20 + sourceRows[1] + 24;
  out += k.card(24, y, 952, sourceSectionH, { fill: '#ffffff', dash: true });
  out += k.label(0, 48, y + 24, 904, sourceTitleH, SECTION);
  let cardY = y + 24 + sourceTitleH + 20;
  sources.forEach((item, index) => {
    if (index === 2) cardY += sourceRows[0] + 20;
    const x = index % 2 === 0 ? 48 : 512;
    const rowH = sourceRows[Math.floor(index / 2)];
    out += `<g data-event-source="${index + 1}">${k.card(x, cardY, 440, rowH, {
      fill: '#f0f0f0',
    })}${k.label(item.titleId, x + 16, cardY + 16, 408, item.title, TITLE)}`;
    let lineY = cardY + 24 + item.title;
    out += k.label(item.eventId, x + 16, lineY, 408, item.event, {
      ...CODE,
      align: 'left',
      direction: 'ltr',
    });
    lineY += item.event;
    out += k.label(item.payloadIds, x + 16, lineY, 408, item.payload, {
      ...CODE,
      align: 'left',
      direction: 'ltr',
    });
    out += '</g>';
  });
  y += sourceSectionH;

  out += edge(
    k,
    'sources-to-queue',
    'event-sources',
    'event-queue',
    `M500 ${y + 8} V${y + 48}`,
    {
      gutter: 56,
    },
  );
  y += 56;
  const queueTitleH = k.height(17, 904, SECTION);
  const queueCards = [18, 20, 22, 24].map((id) =>
    pairMetrics(k, id, id + 1, 216, BODY_BOLD),
  );
  const queueRowH = Math.max(...queueCards.map((item) => item.height));
  const queueH = 24 + queueTitleH + 20 + queueRowH + 24;
  out += k.card(24, y, 952, queueH, { fill: '#ffffff', dash: true });
  out += k.label(17, 48, y + 24, 904, queueTitleH, SECTION);
  const queueY = y + 24 + queueTitleH + 20;
  queueCards.forEach((metrics, index) => {
    metrics.height = queueRowH;
    out += pairCard(
      k,
      18 + index * 2,
      19 + index * 2,
      36 + index * 232,
      queueY,
      216,
      metrics,
      {
        fill: index === 2 ? '#d0d0d0' : '#f0f0f0',
        attributes: { 'data-queue-event': index + 1 },
        titleStyle: BODY_BOLD,
      },
    );
  });
  y += queueH;

  const fetchH = k.height(27, 360, BODY);
  out += edge(
    k,
    'queue-to-processing',
    'event-queue',
    'agent-processing',
    `M500 ${y + 8} V${y + 64 + fetchH}`,
    {
      gutter: 80 + fetchH,
    },
  );
  out += k.label(27, 524, y + 24, 360, fetchH, BODY);
  y += 80 + fetchH;
  const processTitleH = k.height(26, 904, SECTION);
  const processCards = [28, 30, 32, 34, 36].map((id) =>
    pairMetrics(k, id, id + 1, 616, BODY_BOLD),
  );
  const processFlowH =
    processCards.reduce((sum, item) => sum + item.height, 0) +
    48 * (processCards.length - 1);
  const processH = 24 + processTitleH + 20 + processFlowH + 24;
  out += k.card(24, y, 952, processH, { fill: '#ffffff', dash: true });
  out += k.label(26, 48, y + 24, 904, processTitleH, SECTION);
  let processY = y + 24 + processTitleH + 20;
  const stagePositions = [];
  processCards.forEach((metrics, index) => {
    stagePositions.push(processY);
    out += pairCard(
      k,
      28 + index * 2,
      29 + index * 2,
      192,
      processY,
      616,
      metrics,
      {
        fill: [0, 4].includes(index) ? '#d0d0d0' : '#f0f0f0',
        attributes: { 'data-processing-stage': index + 1 },
        titleStyle: BODY_BOLD,
      },
    );
    if (index < 4) {
      const nextY = processY + metrics.height + 48;
      out += edge(
        k,
        `processing-${index + 1}-to-${index + 2}`,
        `processing-${index + 1}`,
        `processing-${index + 2}`,
        `M500 ${processY + metrics.height + 8} V${nextY - 8}`,
        { gutter: 48 },
      );
      processY = nextY;
    }
  });
  const firstCenter = stagePositions[0] + processCards[0].height / 2;
  const lastCenter = stagePositions[4] + processCards[4].height / 2;
  const loopH = k.height(38, 112, BODY);
  out += edge(
    k,
    'result-to-router-loop',
    'result-handling',
    'router',
    `M816 ${lastCenter} H952 V${firstCenter} H816`,
    { dash: true, gutter: 168 },
  );
  out += k.label(
    38,
    824,
    (firstCenter + lastCenter - loopH) / 2,
    112,
    loopH,
    BODY,
  );
  return finish(k, out, 1, y + processH + 24);
}

function sectionFrame(k, y, height, name) {
  return tag(k.card(24, y, 952, height, { fill: '#ffffff', dash: true }), {
    'data-scheduling-pattern': name,
  });
}

function layoutSchedulingPatterns(k, labels) {
  const hasEmptyMarker = labels.length === 28;
  const parallelOffset = hasEmptyMarker ? 0 : -1;
  let out = '';
  let y = 24;
  [0, 1, 2].forEach((id, index) => {
    const x = 258 + index * 244;
    const h = k.height(id, 180, BODY_BOLD);
    out += k.card(x, y, 180, h + 24, { fill: '#f0f0f0' });
    out += k.label(id, x + 12, y + 12, 156, h, BODY_BOLD);
  });
  y += 72;

  // CJK punctuation can wrap sooner in the browser than the shared estimator;
  // reserve the two-line height while keeping the source heading intact.
  const cancelHeading = k.height([3, 4], 150, SECTION);
  const interruptH = k.height(6, 376, BODY_BOLD);
  const initial = [5, 8].map((id) => ({ id, h: k.height(id, 228, BODY) }));
  const initialH = Math.max(...initial.map((item) => item.h + 32));
  const finalH = k.height(10, 240, BODY);
  const cancelContentH = Math.max(
    initialH * 2 + 16,
    interruptH + 48 + finalH + 32,
  );
  const cancelH = 24 + Math.max(cancelHeading, cancelContentH) + 24;
  out += sectionFrame(k, y, cancelH, 'cancellation');
  out += k.label([3, 4], 48, y + 24, 184, cancelHeading, SECTION);
  const cancelY = y + 24;
  initial.forEach((item, index) => {
    const cy = cancelY + index * (initialH + 16);
    out += `<g data-cancelled-work="${index + 1}">${k.card(
      256,
      cy,
      260,
      initialH,
      {
        fill: index === 0 ? '#d0d0d0' : '#f0f0f0',
      },
    )}${k.label(item.id, 272, cy + 16, 228, item.h, BODY)}</g>`;
    const markerId = index === 0 ? 7 : 9;
    const markerH = k.height(markerId, 40, BODY_BOLD);
    out += k.card(548, cy + (initialH - markerH - 16) / 2, 56, markerH + 16, {
      fill: '#d0d0d0',
    });
    out += k.label(
      markerId,
      556,
      cy + (initialH - markerH) / 2,
      40,
      markerH,
      BODY_BOLD,
    );
    out += edge(
      k,
      `cancel-${index + 1}`,
      index === 0 ? 'llm-reasoning' : 'tool-execution',
      'cancelled',
      `M524 ${cy + initialH / 2} H540`,
      { dash: true, gutter: 32 },
    );
  });
  out += k.label(6, 624, cancelY, 328, interruptH, BODY_BOLD);
  out += k.card(624, cancelY + interruptH + 48, 328, finalH + 32, {
    fill: '#d0d0d0',
  });
  out += k.label(10, 640, cancelY + interruptH + 64, 296, finalH, BODY);
  out += edge(
    k,
    'interrupt-to-new-reasoning',
    'interrupt',
    'new-reasoning',
    `M788 ${cancelY + interruptH + 8} V${cancelY + interruptH + 40}`,
    { gutter: 48 },
  );
  y += cancelH + 56;

  const queueHeading = k.height([11, 12], 150, SECTION);
  const queueGap = 40;
  const queueTop = [13, 14, 15].map((id, index) => ({
    id,
    width: [160, 240, 216][index],
  }));
  queueTop.forEach((item) => {
    item.h = k.height(item.id, item.width - (item.id === 14 ? 48 : 32), BODY);
  });
  const queueTopH = Math.max(...queueTop.map((item) => item.h + 32));
  const userH = k.height(16, 288, BODY);
  const waitingH = k.height(17, 240, BODY);
  const batchId = hasEmptyMarker ? 19 : 18;
  const batchH = k.height(batchId, 454, BODY);
  const emptyH = hasEmptyMarker ? k.height(18, 24, BODY) : 0;
  const queueContentH =
    queueTopH + 24 + Math.max(userH + 32, waitingH + 32) + 48 + batchH + 32;
  const queueH = 24 + Math.max(queueHeading, queueContentH) + 24;
  out += sectionFrame(k, y, queueH, 'queue');
  out += k.label([11, 12], 48, y + 24, 184, queueHeading, SECTION);
  const topY = y + 24;
  let x = 256;
  queueTop.forEach((item, index) => {
    out += `<g data-queue-stage="${index + 1}">${k.card(
      x,
      topY,
      item.width,
      queueTopH,
      {
        fill: index === 1 ? '#f0f0f0' : '#d0d0d0',
      },
    )}${k.label(item.id, x + 16, topY + 16, item.width - 32, item.h, BODY)}</g>`;
    if (index < 2) {
      const nextX = x + item.width + queueGap;
      out += edge(
        k,
        `queue-${index + 1}-to-${index + 2}`,
        `queue-${index + 1}`,
        `queue-${index + 2}`,
        `M${x + item.width + 8} ${topY + queueTopH / 2} H${nextX - 8}`,
        {
          gutter: queueGap,
        },
      );
    }
    x += item.width + queueGap;
  });
  const eventY = topY + queueTopH + 24;
  out += k.card(256, eventY, 320, userH + 32, { fill: '#ffffff' });
  out += k.label(16, 272, eventY + 16, 288, userH, BODY);
  out += k.card(616, eventY, 272, waitingH + 32, { fill: '#f0f0f0' });
  out += k.label(17, 632, eventY + 16, 240, waitingH, BODY);
  out += edge(
    k,
    'user-update-to-waiting',
    'user-update',
    'queue-waiting',
    `M584 ${eventY + (userH + 32) / 2} H608`,
    {
      gutter: 40,
    },
  );
  const batchY = eventY + Math.max(userH + 32, waitingH + 32) + 48;
  out += k.card(438, batchY, 514, batchH + 32, { fill: '#d0d0d0' });
  out += k.label(batchId, 454, batchY + 16, 482, batchH, BODY);
  if (hasEmptyMarker) out += k.label(18, 406, batchY + 16, 24, emptyH, BODY);
  out += edge(
    k,
    'waiting-to-batch-append',
    'queue-waiting',
    'batch-append',
    `M752 ${eventY + waitingH + 40} V${batchY - 8}`,
    {
      gutter: 48,
    },
  );
  y += queueH + 56;

  const p = (semanticId) => semanticId + parallelOffset;
  const parallelHeading = k.height([p(20), p(21)], 184, SECTION);
  const mainH = k.height(p(22), 664, BODY);
  const branchIds = [p(23), p(24), p(25)];
  const branchWidths = [280, 160, 152];
  const branch = branchIds.map((id, index) => ({
    id,
    width: branchWidths[index],
    h: k.height(id, branchWidths[index] - 24, BODY),
  }));
  const branchH = Math.max(...branch.map((item) => item.h + 32));
  const replyH = k.height(p(26), 408, BODY);
  const tagH = k.height(p(27), 664, CAPTION);
  const parallelContentH =
    mainH + 32 + 24 + branchH + 48 + replyH + 32 + 20 + tagH;
  const parallelH = 24 + Math.max(parallelHeading, parallelContentH) + 24;
  out += sectionFrame(k, y, parallelH, 'parallel');
  out += k.label([p(20), p(21)], 48, y + 24, 184, parallelHeading, SECTION);
  const mainY = y + 24;
  out += k.card(256, mainY, 696, mainH + 32, { fill: '#f0f0f0' });
  out += k.label(p(22), 272, mainY + 16, 664, mainH, BODY);
  const branchY = mainY + mainH + 56;
  x = 256;
  branch.forEach((item, index) => {
    out += `<g data-parallel-stage="${index + 1}">${k.card(
      x,
      branchY,
      item.width,
      branchH,
      {
        fill: index === 1 ? '#d0d0d0' : '#f0f0f0',
      },
    )}${k.label(item.id, x + 12, branchY + 16, item.width - 24, item.h, BODY)}</g>`;
    if (index < branch.length - 1) {
      const nextX = x + item.width + 40;
      out += edge(
        k,
        `parallel-${index + 1}-to-${index + 2}`,
        `parallel-${index + 1}`,
        `parallel-${index + 2}`,
        `M${x + item.width + 8} ${branchY + branchH / 2} H${nextX - 8}`,
        {
          gutter: 40,
        },
      );
    }
    x += item.width + 40;
  });
  const replyY = branchY + branchH + 48;
  out += k.card(512, replyY, 440, replyH + 32, { fill: '#d0d0d0' });
  out += k.label(p(26), 528, replyY + 16, 408, replyH, BODY);
  out += edge(
    k,
    'weather-to-reply',
    'weather',
    'immediate-reply',
    `M896 ${branchY + branchH + 8} V${replyY - 8}`,
    {
      gutter: 48,
    },
  );
  out += k.label(p(27), 272, replyY + replyH + 44, 664, tagH, CAPTION);
  return finish(k, out, 2, y + parallelH + 24);
}

function layoutRuntimeArchitecture(k) {
  let out = '';
  let y = 24;
  const externalTitleH = k.height(0, 904, SECTION);
  const external = [1, 3, 5, 7, 9, 11].map((id) =>
    pairMetrics(k, id, id + 1, 288, BODY_BOLD),
  );
  const externalRows = [0, 1].map((row) =>
    Math.max(
      ...external.slice(row * 3, row * 3 + 3).map((item) => item.height),
    ),
  );
  const externalH =
    24 + externalTitleH + 20 + externalRows[0] + 20 + externalRows[1] + 24;
  out += k.card(24, y, 952, externalH, { fill: '#ffffff', dash: true });
  out += k.label(0, 48, y + 24, 904, externalTitleH, SECTION);
  let rowY = y + 24 + externalTitleH + 20;
  external.forEach((metrics, index) => {
    if (index === 3) rowY += externalRows[0] + 20;
    metrics.height = externalRows[Math.floor(index / 3)];
    out += pairCard(
      k,
      1 + index * 2,
      2 + index * 2,
      48 + (index % 3) * 308,
      rowY,
      288,
      metrics,
      {
        attributes: { 'data-external-source': index + 1 },
        titleStyle: BODY_BOLD,
      },
    );
  });
  y += externalH;
  out += edge(
    k,
    'events-to-http-endpoint',
    'external-events',
    'http-endpoint',
    `M500 ${y + 8} V${y + 48}`,
    {
      gutter: 56,
    },
  );
  y += 56;

  const runtimeTitleH = k.height(13, 904, SECTION);
  const runtime = [14, 16, 18, 20, 22].map((id) =>
    pairMetrics(k, id, id + 1, 616, BODY_BOLD),
  );
  const runtimeH =
    24 +
    runtimeTitleH +
    20 +
    runtime.reduce((sum, item) => sum + item.height, 0) +
    48 * (runtime.length - 1) +
    24;
  out += k.card(24, y, 952, runtimeH, { fill: '#ffffff', dash: true });
  out += k.label(13, 48, y + 24, 904, runtimeTitleH, SECTION);
  let runtimeY = y + 24 + runtimeTitleH + 20;
  runtime.forEach((metrics, index) => {
    out += pairCard(
      k,
      14 + index * 2,
      15 + index * 2,
      192,
      runtimeY,
      616,
      metrics,
      {
        fill: [0, 4].includes(index) ? '#d0d0d0' : '#f0f0f0',
        attributes: { 'data-runtime-stage': index + 1 },
        titleStyle: BODY_BOLD,
      },
    );
    if (index < 4) {
      const nextY = runtimeY + metrics.height + 48;
      out += edge(
        k,
        `runtime-${index + 1}-to-${index + 2}`,
        `runtime-${index + 1}`,
        `runtime-${index + 2}`,
        `M500 ${runtimeY + metrics.height + 8} V${nextY - 8}`,
        {
          gutter: 48,
        },
      );
      runtimeY = nextY;
    }
  });
  y += runtimeH;
  out += edge(
    k,
    'runtime-to-tools',
    'agent-loop',
    'mcp-tools',
    `M476 ${y + 8} V${y + 64}`,
    {
      gutter: 72,
    },
  );
  out += edge(
    k,
    'tools-to-runtime',
    'mcp-tools',
    'agent-loop',
    `M524 ${y + 64} V${y + 8}`,
    {
      dash: true,
      gutter: 72,
    },
  );
  y += 72;

  const toolsTitleH = k.height(24, 904, SECTION);
  const toolGroups = [
    [25, [26, 27]],
    [28, [29, 30]],
    [31, [32, 33]],
    [34, [35, 36]],
  ].map(([titleId, codeIds]) => {
    const title = k.height(titleId, 408, TITLE);
    const code = k.height(codeIds, 408, CODE);
    return { titleId, codeIds, title, code, height: 32 + title + 8 + code };
  });
  const toolRows = [
    Math.max(...toolGroups.slice(0, 2).map((item) => item.height)),
    Math.max(...toolGroups.slice(2).map((item) => item.height)),
  ];
  const toolsH = 24 + toolsTitleH + 20 + toolRows[0] + 20 + toolRows[1] + 24;
  out += k.card(24, y, 952, toolsH, { fill: '#ffffff', dash: true });
  out += k.label(24, 48, y + 24, 904, toolsTitleH, SECTION);
  rowY = y + 24 + toolsTitleH + 20;
  toolGroups.forEach((item, index) => {
    if (index === 2) rowY += toolRows[0] + 20;
    const x = index % 2 === 0 ? 48 : 512;
    const h = toolRows[Math.floor(index / 2)];
    out += `<g data-tool-group="${index + 1}">${k.card(x, rowY, 440, h, {
      fill: '#f0f0f0',
    })}${k.label(item.titleId, x + 16, rowY + 16, 408, item.title, TITLE)}${k.label(
      item.codeIds,
      x + 16,
      rowY + 24 + item.title,
      408,
      item.code,
      { ...CODE, align: 'left', direction: 'ltr' },
    )}</g>`;
  });
  y += toolsH + 56;

  const persistenceTitleH = k.height(37, 904, SECTION);
  const persistence = [38, 39, 40, 41, 42].map((id) => ({
    id,
    h: k.height(id, 144, BODY),
  }));
  const persistenceRowH = Math.max(...persistence.map((item) => item.h + 32));
  const persistenceH = 24 + persistenceTitleH + 20 + persistenceRowH + 24;
  out += k.card(24, y, 952, persistenceH, { fill: '#ffffff', dash: true });
  out += k.label(37, 48, y + 24, 904, persistenceTitleH, SECTION);
  const persistenceY = y + 24 + persistenceTitleH + 20;
  persistence.forEach((item, index) => {
    const x = 48 + index * 184;
    out += `<g data-persistence-item="${index + 1}">${k.card(
      x,
      persistenceY,
      164,
      persistenceRowH,
      {
        fill: '#f0f0f0',
      },
    )}${k.label(item.id, x + 10, persistenceY + 16, 144, item.h, BODY)}</g>`;
  });
  return finish(k, out, 3, y + persistenceH + 24);
}

function layoutAsyncTimeline(k) {
  let out = '';
  let y = 24;
  const milestoneIds = [9, 12, 14];
  const milestones = milestoneIds.map((id) => ({
    id,
    h: k.height(id, 180, BODY_BOLD),
  }));
  const milestoneH = Math.max(...milestones.map((item) => item.h + 24));
  milestones.forEach((item, index) => {
    const x = 376 + index * 204;
    out += `<g data-milestone="${index + 1}">${k.card(x, y, 188, milestoneH, {
      fill: index === 1 ? '#f0f0f0' : '#d0d0d0',
    })}${k.label(item.id, x + 4, y + 12, 180, item.h, BODY_BOLD)}</g>`;
  });
  const milestoneBottom = y + milestoneH;
  y += milestoneH + 72;

  const laneLabelWidth = 152;
  const eventSpecs = [
    [
      0,
      [
        [5, 216, 184],
        [10, 580, 172],
        [15, 768, 208],
      ],
    ],
    [1, [[6, 280, 292]]],
    [2, [[7, 280, 472]]],
    [
      3,
      [
        // End Tool C before its cancellation badge so the milestone does not
        // cover the localized task description.
        [8, 280, 340],
        [13, 652, 48],
      ],
    ],
    [
      4,
      [
        [11, 580, 172],
        [16, 768, 208],
      ],
    ],
  ];
  const lanes = eventSpecs.map(([laneId, events]) => {
    const labelH = k.height(laneId, laneLabelWidth, BODY_BOLD);
    const measured = events.map(([id, x, width]) => ({
      id,
      x,
      width,
      h: k.height(id, width - 24, id === 17 ? CODE : BODY),
    }));
    return {
      laneId,
      labelH,
      events: measured,
      height: Math.max(labelH + 24, ...measured.map((item) => item.h + 24), 64),
    };
  });
  const timelineBottom =
    y + lanes.reduce((sum, lane) => sum + lane.height + 16, 0);
  const milestoneHeaderCenters = [470, 674, 878];
  const milestoneXs = [
    lanes[1].events[0].x + lanes[1].events[0].width,
    lanes[3].events[1].x + lanes[3].events[1].width / 2,
    lanes[2].events[0].x + lanes[2].events[0].width,
  ];
  milestoneXs.forEach((x, index) => {
    const trackY = milestoneBottom + 20 + index * 14;
    out += `<path data-milestone-leader="${index + 1}" data-milestone-target-x="${x}" d="M${milestoneHeaderCenters[index]} ${milestoneBottom + 8} V${trackY} H${x} V${y}" fill="none" stroke="#666666" stroke-width="1.5"/>`;
    out += `<path data-milestone-line="${index + 1}" data-time-x="${x}" d="M${x} ${y} V${timelineBottom - 16}" fill="none" stroke="#999999" stroke-width="2" stroke-dasharray="6 5"/>`;
  });
  const lanePositions = [];
  lanes.forEach((lane, laneIndex) => {
    lanePositions.push(y);
    out += k.label(
      lane.laneId,
      24,
      y + 12,
      laneLabelWidth,
      lane.labelH,
      BODY_BOLD,
    );
    out += `<path data-lane="${laneIndex + 1}" d="M192 ${y + lane.height / 2} H976" fill="none" stroke="#999999" stroke-width="2" stroke-dasharray="6 5"/>`;
    lane.events.forEach((item, eventIndex) => {
      out += `<g data-timeline-event="${laneIndex + 1}-${eventIndex + 1}">${k.card(
        item.x,
        y + (lane.height - item.h - 24) / 2,
        item.width,
        item.h + 24,
        {
          fill:
            item.id === 13
              ? '#d0d0d0'
              : [5, 10, 15].includes(item.id)
                ? '#d0d0d0'
                : '#f0f0f0',
        },
      )}${k.label(
        item.id,
        item.x + 12,
        y + (lane.height - item.h) / 2,
        item.width - 24,
        item.h,
        item.id === 13 ? BODY_BOLD : BODY,
      )}</g>`;
    });
    y += lane.height + 16;
  });

  const launchBottom = lanePositions[0] + lanes[0].height;
  [1, 2, 3].forEach((laneNumber) => {
    const targetY = lanePositions[laneNumber] + lanes[laneNumber].height / 2;
    out += edge(
      k,
      `launch-tool-${laneNumber}`,
      'launch-tools',
      `tool-${laneNumber}`,
      `M264 ${launchBottom + 8} V${targetY} H272`,
      { gutter: 64 },
    );
  });
  const keyH = k.height(17, 904, CODE);
  out += k.card(24, y + 8, 952, keyH + 32, { fill: '#f0f0f0' });
  out += k.label(17, 48, y + 24, 904, keyH, {
    ...CODE,
    align: 'left',
    direction: 'ltr',
  });
  return finish(k, out, 4, y + keyH + 64);
}

function flowRow(k, pairs, y, name) {
  const widths = [272, 272, 272];
  const xs = [48, 364, 680];
  const metrics = pairs.map(([titleId, bodyId], index) =>
    pairMetrics(k, titleId, bodyId, widths[index]),
  );
  const rowH = Math.max(...metrics.map((item) => item.height));
  let output = '';
  metrics.forEach((item, index) => {
    item.height = rowH;
    output += pairCard(
      k,
      pairs[index][0],
      pairs[index][1],
      xs[index],
      y,
      widths[index],
      item,
      {
        fill: index === 1 ? '#f0f0f0' : '#ffffff',
        attributes: { 'data-flow': name, 'data-stage': index + 1 },
      },
    );
    if (index < 2)
      output += edge(
        k,
        `${name}-${index + 1}-to-${index + 2}`,
        `${name}-${index + 1}`,
        `${name}-${index + 2}`,
        `M${xs[index] + widths[index] + 8} ${y + rowH / 2} H${xs[index + 1] - 8}`,
        {
          gutter: 44,
        },
      );
  });
  return { output, height: rowH };
}

function layoutNativeAsynchrony(k) {
  let out = '';
  let y = 24;
  const compatibilityTitleH = k.height(0, 904, SECTION);
  const compatibilityY = y + 24 + compatibilityTitleH + 20;
  const compatibility = flowRow(
    k,
    [
      [1, 2],
      [3, 4],
      [5, 6],
    ],
    compatibilityY,
    'compatibility',
  );
  const compatibilityH =
    24 + compatibilityTitleH + 20 + compatibility.height + 24;
  out += k.card(24, y, 952, compatibilityH, { fill: '#ffffff', dash: true });
  out += k.label(0, 48, y + 24, 904, compatibilityTitleH, SECTION);
  out += compatibility.output;
  y += compatibilityH + 56;

  const nativeTitleH = k.height(7, 904, SECTION);
  const firstY = y + 24 + nativeTitleH + 20;
  const waiting = flowRow(
    k,
    [
      [8, 9],
      [10, 11],
      [12, 13],
    ],
    firstY,
    'work-while-waiting',
  );
  const updateY = firstY + waiting.height + 28;
  const updates = flowRow(
    k,
    [
      [14, 15],
      [16, 17],
      [18, 19],
    ],
    updateY,
    'mid-task-update',
  );
  const nativeH =
    24 + nativeTitleH + 20 + waiting.height + 28 + updates.height + 24;
  out += k.card(24, y, 952, nativeH, { fill: '#ffffff', dash: true });
  out += k.label(7, 48, y + 24, 904, nativeTitleH, SECTION);
  out += waiting.output + updates.output;
  y += nativeH + 40;

  const summaryH = k.height(20, 904, TITLE);
  const captionH = k.height(21, 904, BODY);
  const bannerH = 24 + summaryH + 8 + captionH + 24;
  out += k.card(24, y, 952, bannerH, { fill: '#d0d0d0' });
  out += k.label(20, 48, y + 24, 904, summaryH, TITLE);
  out += k.label(21, 48, y + 32 + summaryH, 904, captionH, BODY);
  return finish(k, out, 5, y + bannerH + 24);
}

export function layoutAsyncArchitecture(
  source,
  figureNumber,
  { rtl = false } = {},
) {
  if (![1, 2, 3, 4, 5].includes(figureNumber))
    throw new Error(`Unsupported async-architecture figure ${figureNumber}`);
  // Three Figure 6-2 translations serialize the intentionally empty timeline
  // marker as a self-closing text node. Normalize only that XML spelling so it
  // remains a source-backed (empty) label with the same semantic index.
  const normalized = source.replace(/<text\b([^>]*)\/>/g, '<text$1></text>');
  const labels = extractLabels(
    normalized,
    `6-${figureNumber}`,
    variants[figureNumber].labels,
  );
  guardSource(source, figureNumber, labels);
  const k = figureKit(labels, { rtl });
  if (figureNumber === 1) return layoutEventArchitecture(k);
  if (figureNumber === 2) return layoutSchedulingPatterns(k, labels);
  if (figureNumber === 3) return layoutRuntimeArchitecture(k);
  if (figureNumber === 4) return layoutAsyncTimeline(k);
  return layoutNativeAsynchrony(k);
}
