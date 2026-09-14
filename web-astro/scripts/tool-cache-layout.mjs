import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

const SECTION = { size: 20, bold: true };
const CARD_TITLE = { size: 18, bold: true };
const BODY = { size: 16 };
const BODY_BOLD = { size: 16, bold: true };
const CAPTION = { size: 14, muted: true };
const CODE = { size: 14, mono: true };

function sourceStructure(source, figure, labels) {
  const expected = {
    3: { labels: [38], rects: 11, lines: 1, arrows: 0 },
    4: { labels: [17, 19], rects: 13, lines: 2, arrows: 2 },
  }[figure];
  if (!expected) throw new Error('Unsupported tool-cache figure');
  const count = (pattern) => [...source.matchAll(pattern)].length;
  if (
    !expected.labels.includes(labels.length) ||
    count(/<rect\b/g) !== expected.rects ||
    count(/<line\b/g) !== expected.lines ||
    count(/\bmarker-end=/g) !== expected.arrows
  )
    throw new Error(
      `Figure 4-${figure} source structure changed; review its web layout.`,
    );
}

function tag(element, attributes) {
  return element.replace(
    /^<([a-zA-Z]+)/,
    (_, name) =>
      `<${name} ${Object.entries(attributes)
        .map(([key, value]) => `${key}="${value}"`)
        .join(' ')}`,
  );
}

function layoutComparison(labels, rtl) {
  const { label, height, card, svg } = figureKit(labels, { rtl });
  const panelWidth = 464;
  const innerWidth = 424;
  const panelX = [24, 512];
  const innerX = panelX.map((x) => x + 20);
  const sectionHeight =
    Math.max(height(0, innerWidth, SECTION), height(10, innerWidth, SECTION)) +
    4;
  const stackY = 24 + 20 + sectionHeight + 16;

  const stackCard = (specification, x, y, stack, position) => {
    const {
      title,
      body,
      metric,
      bodyStyle = BODY,
      fill = '#f0f0f0',
    } = specification;
    const contentWidth = innerWidth - 32;
    const titleHeight =
      title == null ? 0 : height(title, contentWidth, CARD_TITLE);
    const bodyHeight = body == null ? 0 : height(body, contentWidth, bodyStyle);
    const metricHeight =
      metric == null ? 0 : height(metric, contentWidth - 16, CAPTION);
    const contentGaps = title != null && body != null ? 8 : 0;
    const metricSpace = metric == null ? 0 : 12 + metricHeight + 16;
    const cardHeight =
      32 + titleHeight + contentGaps + bodyHeight + metricSpace;
    let out = tag(card(x, y, innerWidth, cardHeight, { fill }), {
      'data-stack': stack,
      'data-card': position,
    });
    let cursor = y + 16;
    if (title != null) {
      out += label(
        title,
        x + 16,
        cursor,
        contentWidth,
        titleHeight,
        CARD_TITLE,
      );
      cursor += titleHeight + contentGaps;
    }
    if (body != null)
      out += label(body, x + 16, cursor, contentWidth, bodyHeight, bodyStyle);
    if (metric != null) {
      const metricY = y + cardHeight - metricHeight - 12;
      out += tag(
        card(x + 12, metricY - 4, innerWidth - 24, metricHeight + 8, {
          fill: '#ffffff',
        }),
        { 'data-metric': metric },
      );
      out += label(
        metric,
        x + 20,
        metricY,
        innerWidth - 40,
        metricHeight,
        CAPTION,
      );
    }
    return { out, height: cardHeight };
  };

  const naive = [
    { title: 1, body: [2, 3], metric: 4 },
    { title: 5, body: 6 },
    { title: 7, body: 8, bodyStyle: CODE },
    { title: 9, fill: '#d0d0d0' },
  ];
  const optimized = [
    { title: 11, body: [12, 13], metric: 14 },
    { title: 15, body: 16, metric: 17, fill: '#f5f5f5' },
    { title: 18, body: 19 },
    { title: 20, body: 21, metric: 22 },
    { title: 23, body: 24 },
    { title: 25, body: 26, metric: 27, fill: '#f5f5f5' },
    { title: 28, fill: '#d0d0d0' },
  ];

  const renderStack = (specifications, x, name) => {
    let y = stackY;
    let out = '';
    specifications.forEach((specification, index) => {
      const rendered = stackCard(specification, x, y, name, index);
      out += rendered.out;
      y += rendered.height + 12;
    });
    return { out, bottom: y - 12 };
  };

  const naiveStack = renderStack(naive, innerX[0], 'naive');
  const optimizedStack = renderStack(optimized, innerX[1], 'optimized');
  const stackBottom = Math.max(naiveStack.bottom, optimizedStack.bottom);
  let out = tag(
    card(panelX[0], 24, panelWidth, naiveStack.bottom - 24 + 20, {
      fill: '#ffffff',
    }),
    { 'data-region': 'naive-context-stack' },
  );
  out += tag(
    card(panelX[1], 24, panelWidth, optimizedStack.bottom - 24 + 20, {
      fill: '#ffffff',
    }),
    { 'data-region': 'optimized-context-stack' },
  );
  out += label(0, innerX[0], 44, innerWidth, sectionHeight, SECTION);
  out += label(10, innerX[1], 44, innerWidth, sectionHeight, SECTION);
  out += naiveStack.out + optimizedStack.out;

  const dividerY = stackBottom + 44;
  out += `<line data-divider="comparison" x1="24" y1="${dividerY}" x2="976" y2="${dividerY}" stroke="#999999" stroke-width="2" stroke-dasharray="8 5"/>`;
  const tableY = dividerY + 24;
  const widths = [252, 338, 338];
  const xs = [24, 288, 638];
  const headerIds = [29, 30, 31];
  const headerHeight =
    Math.max(
      ...headerIds.map((id, index) =>
        height(id, widths[index] - 32, CARD_TITLE),
      ),
    ) + 32;
  const rows = [
    [32, 33, 34],
    [35, 36, 37],
  ];
  const rowHeights = rows.map(
    (row) =>
      Math.max(
        ...row.map((id, index) =>
          height(id, widths[index] - 32, index === 0 ? BODY_BOLD : BODY),
        ),
      ) + 32,
  );
  out += `<g data-region="comparison-table">`;
  headerIds.forEach((id, index) => {
    out += tag(
      card(xs[index], tableY, widths[index], headerHeight, {
        fill: '#d0d0d0',
      }),
      { 'data-table-cell': `header-${index}` },
    );
    out += label(
      id,
      xs[index] + 16,
      tableY + 16,
      widths[index] - 32,
      headerHeight - 32,
      CARD_TITLE,
    );
  });
  let rowY = tableY + headerHeight + 12;
  rows.forEach((row, rowIndex) => {
    row.forEach((id, columnIndex) => {
      out += tag(
        card(xs[columnIndex], rowY, widths[columnIndex], rowHeights[rowIndex], {
          fill: columnIndex === 0 ? '#ffffff' : '#f0f0f0',
        }),
        { 'data-table-cell': `${rowIndex}-${columnIndex}` },
      );
      out += label(
        id,
        xs[columnIndex] + 16,
        rowY + 16,
        widths[columnIndex] - 32,
        rowHeights[rowIndex] - 32,
        columnIndex === 0 ? BODY_BOLD : BODY,
      );
    });
    rowY += rowHeights[rowIndex] + 12;
  });
  out += '</g>';
  return svg(out, rowY + 12).replace(
    '<svg ',
    '<svg data-layout="tool-cache" data-figure="4-3" ',
  );
}

function layoutTrajectory(labels, rtl) {
  const { label, height, card, path, svg } = figureKit(labels, { rtl });
  const pageX = 24;
  const pageWidth = 952;
  const prefixInnerX = 48;
  const prefixInnerWidth = 904;
  const prefixTitleHeight = height(0, prefixInnerWidth, SECTION) + 4;
  const prefixTitleY = 44;
  const prefixCardY = prefixTitleY + prefixTitleHeight + 16;
  const prefixRows = [1, 2].map((id) =>
    Math.max(
      52,
      height(id, prefixInnerWidth - 32, id === 1 ? CARD_TITLE : BODY_BOLD) + 24,
    ),
  );
  const prefixBottom = prefixCardY + prefixRows[0] + 12 + prefixRows[1] + 20;
  let out = tag(
    card(pageX, 24, pageWidth, prefixBottom - 24, {
      fill: '#ffffff',
      dash: true,
    }),
    { 'data-region': 'static-prefix' },
  );
  out += label(
    0,
    prefixInnerX,
    prefixTitleY,
    prefixInnerWidth,
    prefixTitleHeight,
    SECTION,
  );
  let prefixY = prefixCardY;
  [1, 2].forEach((id, index) => {
    out += tag(
      card(prefixInnerX, prefixY, prefixInnerWidth, prefixRows[index], {
        fill: '#d0d0d0',
      }),
      { 'data-prefix-row': index },
    );
    out += label(
      id,
      prefixInnerX + 16,
      prefixY + 12,
      prefixInnerWidth - 32,
      prefixRows[index] - 24,
      index === 0 ? CARD_TITLE : BODY_BOLD,
    );
    prefixY += prefixRows[index] + 12;
  });

  const trajectoryY = prefixBottom + 32;
  const trajectoryWidth = 628;
  const trajectoryInnerX = 48;
  const trajectoryInnerWidth = 572;
  const trajectoryTitleHeight = height(3, trajectoryWidth - 40, SECTION) + 4;
  const firstEventY = trajectoryY + 20 + trajectoryTitleHeight + 16;
  const eventIds = [4, 5, 6, 7, 8, 9, 10, 11, 12];
  const injectionIds = new Set([6, 10]);
  const eventHeights = eventIds.map((id) =>
    Math.max(
      50,
      height(
        id,
        trajectoryInnerWidth - 32,
        injectionIds.has(id) ? BODY_BOLD : BODY,
      ) + 24,
    ),
  );
  const eventYs = [];
  let eventY = firstEventY;
  eventIds.forEach((id, index) => {
    eventYs.push(eventY);
    eventY += eventHeights[index] + 10;
  });
  const trajectoryBottom = eventY - 10 + 20;
  out += tag(
    card(pageX, trajectoryY, trajectoryWidth, trajectoryBottom - trajectoryY, {
      fill: '#ffffff',
      dash: true,
    }),
    { 'data-region': 'append-only-trajectory' },
  );
  out += label(
    3,
    pageX + 20,
    trajectoryY + 20,
    trajectoryWidth - 40,
    trajectoryTitleHeight,
    SECTION,
  );
  eventIds.forEach((id, index) => {
    const injection = injectionIds.has(id);
    out += tag(
      card(
        trajectoryInnerX,
        eventYs[index],
        trajectoryInnerWidth,
        eventHeights[index],
        { fill: injection ? '#d8e8d8' : '#f0f0f0' },
      ),
      {
        'data-trajectory-event': index,
        ...(injection ? { 'data-schema-injection': id } : {}),
      },
    );
    out += label(
      id,
      trajectoryInnerX + 16,
      eventYs[index] + 12,
      trajectoryInnerWidth - 32,
      eventHeights[index] - 24,
      injection ? BODY_BOLD : BODY,
    );
  });

  const calloutGroups =
    labels.length === 19
      ? [
          { title: 13, body: 14 },
          { title: [15, 16], body: [17, 18] },
        ]
      : [
          { title: 13, body: 14 },
          { title: 15, body: 16 },
        ];
  const calloutX = 720;
  const calloutWidth = 256;
  const callouts = calloutGroups.map(({ title, body }) => {
    const titleHeight = height(title, calloutWidth - 32, BODY_BOLD);
    const bodyHeight = height(body, calloutWidth - 32, CAPTION);
    return {
      title,
      body,
      titleHeight,
      bodyHeight,
      height: 32 + titleHeight + 8 + bodyHeight,
    };
  });
  const injectionIndexes = [2, 6];
  callouts.forEach((callout, index) => {
    const eventIndex = injectionIndexes[index];
    callout.eventCenter = eventYs[eventIndex] + eventHeights[eventIndex] / 2;
    callout.y = Math.max(
      trajectoryY + 20 + trajectoryTitleHeight,
      callout.eventCenter - callout.height / 2,
      index === 0 ? 0 : callouts[index - 1].y + callouts[index - 1].height + 32,
    );
    callout.center = callout.y + callout.height / 2;
    out += tag(
      card(calloutX, callout.y, calloutWidth, callout.height, {
        fill: '#ffffff',
      }),
      { 'data-callout': index + 1 },
    );
    out += label(
      callout.title,
      calloutX + 16,
      callout.y + 16,
      calloutWidth - 32,
      callout.titleHeight,
      BODY_BOLD,
    );
    out += label(
      callout.body,
      calloutX + 16,
      callout.y + 24 + callout.titleHeight,
      calloutWidth - 32,
      callout.bodyHeight,
      CAPTION,
    );
    const connector = path(
      `M628 ${callout.eventCenter} H676 V${callout.center} H712`,
      { dash: true },
    );
    out += tag(connector, {
      'data-edge': `schema-callout-${index + 1}`,
      'data-card-gap-start': 8,
      'data-card-gap-end': 8,
    });
  });

  const bottom = Math.max(
    trajectoryBottom,
    ...callouts.map((callout) => callout.y + callout.height),
  );
  return svg(out, bottom + 24).replace(
    '<svg ',
    '<svg data-layout="tool-cache" data-figure="4-4" ',
  );
}

export function layoutToolCache(source, figure, { rtl = false } = {}) {
  if (![3, 4].includes(figure))
    throw new Error('Unsupported tool-cache figure');
  const labels = extractLabels(
    source,
    `4-${figure}`,
    {
      3: [38],
      4: [17, 19],
    }[figure],
  );
  sourceStructure(source, figure, labels);
  return figure === 3
    ? layoutComparison(labels, rtl)
    : layoutTrajectory(labels, rtl);
}
