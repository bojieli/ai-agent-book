// Web-only reflows for the Chapter 3 memory foundations. Localized source
// SVGs remain untouched and supply every visible label.

import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

const expected = {
  1: { labels: [15, 16], rect: [5], line: [2], circle: [0], marker: [2] },
  3: { labels: [23], rect: [10], line: [9], circle: [0], marker: [1] },
  4: { labels: [16, 17], rect: [4, 6], line: [6], circle: [0], marker: [2] },
  5: { labels: [21, 22], rect: [7], line: [4], circle: [0], marker: [2] },
  7: { labels: [7], rect: [5, 7], line: [17], circle: [19], marker: [2] },
};

function count(source, tag) {
  return (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
}

function labelsFor(source, figure) {
  const specification = expected[figure];
  if (!specification) throw new Error('Unsupported memory-foundation figure');
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !['rect', 'line', 'circle', 'marker'].every((tag) =>
      specification[tag].includes(count(source, tag)),
    )
  )
    throw new Error(
      `Figure 3-${figure} source structure changed; review its web layout.`,
    );
  return extractLabels(source, `3-${figure}`, specification.labels);
}

function edge(name, content, from = '', to = '') {
  return `<g data-edge="${name}"${from ? ` data-from="${from}"` : ''}${to ? ` data-to="${to}"` : ''}>${content}</g>`;
}

function layoutOverview(labels, rtl) {
  const kit = figureKit(labels, { rtl });
  const { arrow, card, height, label, svg } = kit;
  const margin = 24;
  const gap = 32;
  const columnWidth = 460;
  const innerWidth = columnWidth - 48;
  const columns = [
    { x: margin, title: 0, items: [2, 3, 4, 5, 6], key: 'user-memory' },
    {
      x: margin + columnWidth + gap,
      title: 1,
      items: [7, 8, 9, 10, 11],
      key: 'knowledge-base',
    },
  ];
  const titleHeight =
    Math.max(
      ...columns.map(({ title }) =>
        height(title, innerWidth, { size: 20, bold: true }),
      ),
    ) + 8;
  const headingCardHeight = titleHeight + 32;
  const bodyRows = columns.map(({ items }) =>
    items.map((item) => height(item, innerWidth, { size: 16, min: 30 })),
  );
  const bodyHeight =
    Math.max(
      ...bodyRows.map((rows) => rows.reduce((sum, value) => sum + value, 0)),
    ) + 32;
  const bodyY = margin + headingCardHeight + 16;
  const bodyBottom = bodyY + bodyHeight;
  const foundationY = bodyBottom + 48;
  const foundationTitleHeight = height(12, 904, { size: 18, bold: true }) + 8;
  const foundationBodyHeight = height(13, 904, { size: 16, min: 28 });
  const foundationHeight =
    24 + foundationTitleHeight + foundationBodyHeight + 16;
  const captionIndices = labels.slice(14).map((_, offset) => 14 + offset);
  const captionY = foundationY + foundationHeight + 16;
  const captionHeight = height(captionIndices, 920, { size: 14, min: 42 });

  const content = `${columns
    .map(({ x, title, items, key }, column) => {
      let y = bodyY + 16;
      const rows = items
        .map((item, row) => {
          const rowHeight = bodyRows[column][row];
          const rendered = label(item, x + 24, y, innerWidth, rowHeight, {
            size: 16,
            align: 'start',
          });
          y += rowHeight;
          return rendered;
        })
        .join('');
      return `<g data-region="${key}">
        ${card(x, margin, columnWidth, headingCardHeight, { fill: '#d0d0d0' })}
        ${label(title, x + 24, margin + 16, innerWidth, titleHeight, { size: 20, bold: true })}
        ${card(x, bodyY, columnWidth, bodyHeight)}
        ${rows}
      </g>`;
    })
    .join('')}
    ${edge('foundation-to-user-memory', arrow(254, foundationY - 8, 254, bodyBottom + 8), 'shared-foundation', 'user-memory')}
    ${edge('foundation-to-knowledge-base', arrow(746, foundationY - 8, 746, bodyBottom + 8), 'shared-foundation', 'knowledge-base')}
    <g data-region="shared-foundation">
      ${card(margin, foundationY, 952, foundationHeight, { fill: '#f5f5f5' })}
      ${label(12, 48, foundationY + 16, 904, foundationTitleHeight, { size: 18, bold: true })}
      ${label(13, 48, foundationY + 16 + foundationTitleHeight, 904, foundationBodyHeight, { size: 16 })}
    </g>
    ${label(captionIndices, 40, captionY, 920, captionHeight, { size: 14, muted: true })}`;
  return svg(content, captionY + captionHeight + 20);
}

function sequenceRow(kit, groups, widths, title, y, tone) {
  const { arrow, card, height, label } = kit;
  const xs = widths.map(
    (_, index) =>
      24 +
      widths.slice(0, index).reduce((sum, width) => sum + width, 0) +
      index * 48,
  );
  const metrics = groups.map(({ heading, detail = [] }, index) => {
    const headingHeight =
      height(heading, widths[index] - 32, {
        size: 18,
        bold: true,
      }) + 8;
    const detailHeight = detail.length
      ? height(detail, widths[index] - 32, {
          size: 15,
          min: 26,
        })
      : 0;
    return { headingHeight, detailHeight };
  });
  const cardHeight =
    Math.max(
      ...metrics.map(
        ({ headingHeight, detailHeight }) => headingHeight + detailHeight,
      ),
    ) + 32;
  const cards = groups
    .map(({ heading, detail = [], key }, index) => {
      const { headingHeight, detailHeight } = metrics[index];
      return `<g data-stage="${key}">
        ${card(xs[index], y, widths[index], cardHeight, { fill: tone })}
        ${label(heading, xs[index] + 16, y + 16, widths[index] - 32, headingHeight, { size: 18, bold: true })}
        ${detail.length ? label(detail, xs[index] + 16, y + 16 + headingHeight, widths[index] - 32, detailHeight, { size: 15, muted: true }) : ''}
      </g>`;
    })
    .join('');
  const arrows = groups
    .slice(0, -1)
    .map((group, index) =>
      edge(
        `${group.key}-to-${groups[index + 1].key}`,
        arrow(
          xs[index] + widths[index] + 8,
          y + cardHeight / 2,
          xs[index + 1] - 8,
          y + cardHeight / 2,
        ),
        group.key,
        groups[index + 1].key,
      ),
    )
    .join('');
  const headingHeight =
    height(title, 952, { size: 20, bold: true, min: 34 }) + 8;
  return {
    content: `${label(title, 24, y - headingHeight - 8, 952, headingHeight, { size: 20, bold: true, align: 'start' })}${cards}${arrows}`,
    bottom: y + cardHeight,
  };
}

function layoutMem0(labels, rtl) {
  const kit = figureKit(labels, { rtl });
  const { height, label, path, svg } = kit;
  const top = sequenceRow(
    kit,
    [
      { heading: [1], key: 'v2-dialogue' },
      { heading: [2], detail: [3], key: 'v2-extract' },
      { heading: [4], detail: [5], key: 'v2-search' },
      { heading: [6], detail: [7], key: 'v2-decide' },
      { heading: [8, 9], key: 'v2-write-action' },
    ],
    [120, 140, 140, 140, 220],
    0,
    64,
    '#f4f4f4',
  );
  const topCaptionY = top.bottom + 12;
  const topCaptionHeight = height(10, 920, { size: 14, min: 32 });
  const dividerY = topCaptionY + topCaptionHeight + 16;
  const lowerY = dividerY + 64;
  const lower = sequenceRow(
    kit,
    [
      { heading: [12], key: 'v3-dialogue' },
      { heading: [13], detail: [14], key: 'v3-extract' },
      { heading: [15], detail: [16], key: 'v3-store' },
      { heading: [17], detail: [18], key: 'v3-retrieval' },
      { heading: [19], detail: [20], key: 'v3-ranked-results' },
    ],
    [120, 140, 140, 220, 140],
    11,
    lowerY,
    '#e8f3ec',
  );
  const scoreY = lower.bottom + 14;
  const scoreHeight = height(21, 920, { size: 14, min: 30 });
  const noteY = scoreY + scoreHeight + 4;
  const noteHeight = height(22, 920, { size: 14, min: 30 });
  return svg(
    `${top.content}
      ${label(10, 40, topCaptionY, 920, topCaptionHeight, { size: 14, muted: true })}
      ${path(`M24 ${dividerY} H976`, { arrow: false })}
      ${lower.content}
      ${label(21, 40, scoreY, 920, scoreHeight, { size: 14, muted: true })}
      ${label(22, 40, noteY, 920, noteHeight, { size: 14, muted: true })}`,
    noteY + noteHeight + 18,
  );
}

function textNodes(source) {
  return [...source.matchAll(/<text\b([^>]*)>([\s\S]*?)<\/text>/g)].map(
    ([, attributes, content], index) => {
      const value = (name) =>
        Number(attributes.match(new RegExp(`\\b${name}="(-?[\\d.]+)`))?.[1]);
      let y = value('y');
      if (y === 0) {
        const firstOffset = content.match(/<tspan\b[^>]*\bdy="([\d.]+)"/)?.[1];
        if (firstOffset) y = Number(firstOffset);
      }
      return { index, x: value('x'), y };
    },
  );
}

function layoutMemoryTypes(source, labels, rtl) {
  const kit = figureKit(labels, { rtl });
  const { card, height, label, path, svg } = kit;
  const nodes = textNodes(source);
  const working = nodes
    .filter(({ y }) => y >= 250 && y < 345)
    .map(({ index }) => index);
  const longTermHeading = nodes
    .filter(({ y }) => y < 80)
    .map(({ index }) => index);
  const caption = nodes.filter(({ y }) => y >= 350).map(({ index }) => index);
  const transfer = nodes
    .filter(({ y }) => y >= 190 && y < 225)
    .map(({ index }) => index);
  const memories = [160, 460, 760].map((sourceX) =>
    nodes
      .filter(({ x, y }) => Math.abs(x - sourceX) < 2 && y >= 80 && y < 175)
      .map(({ index }) => index),
  );
  if (
    working.length !== 3 ||
    longTermHeading.length !== 1 ||
    ![1, 2].includes(caption.length) ||
    transfer.length !== 2 ||
    memories.some((group) => group.length < 3 || group.length > 4)
  )
    throw new Error('Figure 3-4 source roles changed; review its web layout.');

  const headingHeight =
    height(longTermHeading, 952, { size: 20, bold: true, min: 38 }) + 8;
  const topY = 24 + headingHeight + 12;
  const memoryWidth = 296;
  const memoryXs = [24, 352, 680];
  const groupMetrics = memories.map((group) => ({
    title:
      height(group[0], memoryWidth - 40, {
        size: 18,
        bold: true,
        min: 30,
      }) + 8,
    subtype: height(group[1], memoryWidth - 40, { size: 14, min: 24 }),
    body: height(group.slice(2), memoryWidth - 40, { size: 16, min: 34 }),
  }));
  const memoryHeight =
    Math.max(
      ...groupMetrics.map(({ title, subtype, body }) => title + subtype + body),
    ) + 32;
  const topBottom = topY + memoryHeight;
  const transferHeight = Math.max(
    ...transfer.map((item) => height(item, 264, { size: 16, min: 30 })),
  );
  const transferY = topBottom + 28;
  const workingY = Math.max(topBottom + 128, transferY + transferHeight + 44);
  const workingWidth = 360;
  const workingX = 320;
  const workingTitleHeight =
    height(working[0], workingWidth - 48, {
      size: 18,
      bold: true,
      min: 30,
    }) + 8;
  const workingSubtypeHeight = height(working[1], workingWidth - 48, {
    size: 14,
  });
  const workingBodyHeight =
    workingSubtypeHeight + height(working[2], workingWidth - 48, { size: 16 });
  const workingHeight = workingTitleHeight + workingBodyHeight + 32;
  const captionY = workingY + workingHeight + 20;
  const captionHeight = height(caption, 920, { size: 14, min: 42 });
  const routeNames = ['episodic', 'semantic', 'procedural'];
  const routes = [
    {
      down: `M162 ${topBottom + 8} H370 V${workingY - 8}`,
      up: `M390 ${workingY - 8} V${topBottom + 18} H182 V${topBottom + 8}`,
    },
    {
      down: `M490 ${topBottom + 8} V${workingY - 8}`,
      up: `M510 ${workingY - 8} V${topBottom + 8}`,
    },
    {
      down: `M838 ${topBottom + 8} H630 V${workingY - 8}`,
      up: `M610 ${workingY - 8} V${topBottom + 18} H818 V${topBottom + 8}`,
    },
  ];

  return svg(
    `${label(longTermHeading, 24, 24, 952, headingHeight, { size: 20, bold: true })}
      ${memories
        .map(
          (group, index) => `<g data-memory-type="${routeNames[index]}">
          ${card(memoryXs[index], topY, memoryWidth, memoryHeight)}
          ${label(group[0], memoryXs[index] + 20, topY + 16, memoryWidth - 40, groupMetrics[index].title, { size: 18, bold: true })}
          <g data-memory-subtype="${routeNames[index]}">
            ${label(group[1], memoryXs[index] + 20, topY + 16 + groupMetrics[index].title, memoryWidth - 40, groupMetrics[index].subtype, { size: 14, muted: true })}
          </g>
          <g data-memory-description="${routeNames[index]}">
            ${label(group.slice(2), memoryXs[index] + 20, topY + 16 + groupMetrics[index].title + groupMetrics[index].subtype, memoryWidth - 40, groupMetrics[index].body, { size: 16, muted: true })}
          </g>
        </g>`,
        )
        .join('')}
      ${routeNames
        .map((name, index) => {
          return `${edge(`${name}-to-working`, path(routes[index].down), name, 'working-memory')}${edge(`working-to-${name}`, path(routes[index].up), 'working-memory', name)}`;
        })
        .join('')}
      <g data-connector-caption="selective-transfer">
        ${card(24, transferY, 296, transferHeight + 16, { fill: '#ffffff' })}
        ${label(transfer[0], 40, transferY + 8, 264, transferHeight, { size: 16, muted: true })}
      </g>
      <g data-connector-caption="activation-loading">
        ${card(680, transferY, 296, transferHeight + 16, { fill: '#ffffff' })}
        ${label(transfer[1], 696, transferY + 8, 264, transferHeight, { size: 16, muted: true })}
      </g>
      <g data-region="working-memory">
        ${card(workingX, workingY, workingWidth, workingHeight, { fill: '#d0d0d0' })}
        ${label(working[0], workingX + 24, workingY + 16, workingWidth - 48, workingTitleHeight, { size: 18, bold: true })}
        ${label(working[1], workingX + 24, workingY + 16 + workingTitleHeight, workingWidth - 48, workingSubtypeHeight, { size: 14, muted: true })}
        ${label(working[2], workingX + 24, workingY + 16 + workingTitleHeight + workingSubtypeHeight, workingWidth - 48, workingBodyHeight - workingSubtypeHeight, { size: 16, muted: true })}
      </g>
      ${label(caption, 40, captionY, 920, captionHeight, { size: 14, muted: true })}`,
    captionY + captionHeight + 20,
  );
}

function layoutRagFlow(source, labels, rtl) {
  const kit = figureKit(labels, { rtl });
  const { arrow, card, height, label, svg } = kit;
  const stageEnd = labels.length - 10;
  const nodes = textNodes(source).slice(0, stageEnd);
  const sourceCenters = [110, 330, 550, 770];
  const stageNames = ['query', 'retrieval', 'augmentation', 'generation'];
  const groups = sourceCenters.map((center) =>
    nodes.filter(({ x }) => Math.abs(x - center) < 45),
  );
  if (groups.some((group) => group.length < 2 || group.length > 3))
    throw new Error('Figure 3-5 source roles changed; review its web layout.');
  const stages = groups.map((group) => ({
    heading: group.filter(({ y }) => y < 125).map(({ index }) => index),
    detail: group.filter(({ y }) => y >= 125).map(({ index }) => index),
  }));
  if (stages.some(({ heading, detail }) => !heading.length || !detail.length))
    throw new Error('Figure 3-5 source roles changed; review its web layout.');

  const margin = 24;
  const gap = 48;
  const stageWidth = 202;
  const stageXs = sourceCenters.map(
    (_, index) => margin + index * (stageWidth + gap),
  );
  const stageMetrics = stages.map(({ heading, detail }) => ({
    heading:
      height(heading, stageWidth - 32, {
        size: 18,
        bold: true,
        min: 34,
      }) + 8,
    detail: height(detail, stageWidth - 32, { size: 16, min: 52 }),
  }));
  const stageHeight =
    Math.max(...stageMetrics.map((metric) => metric.heading + metric.detail)) +
    32;
  const stageY = 24;
  const stageBottom = stageY + stageHeight;
  const flowHeading = stageEnd;
  const leftHeader = stageEnd + 1;
  const leftBody = [stageEnd + 2, stageEnd + 3];
  const rightHeader = stageEnd + 4;
  const rightBody = [stageEnd + 5, stageEnd + 6];
  const responseHeader = stageEnd + 7;
  const responseBody = [stageEnd + 8, stageEnd + 9];
  const flowTitleY = stageBottom + 24;
  const flowTitleHeight =
    height(flowHeading, 952, { size: 20, bold: true, min: 38 }) + 8;
  const dataY = flowTitleY + flowTitleHeight + 12;
  const dataWidth = 460;
  const dataInner = dataWidth - 48;
  const dataHeaderHeight =
    Math.max(
      height(leftHeader, dataInner, { size: 18, bold: true, min: 34 }),
      height(rightHeader, dataInner, { size: 18, bold: true, min: 34 }),
    ) + 8;
  // The print figure uses monospace styling for the legal example. Arabic and
  // Hebrew editions contain natural-language prose here, so keep their RTL
  // direction instead of forcing the kit's code-oriented LTR monospace mode.
  const exampleMono = !rtl;
  const dataBodyHeight = Math.max(
    height(leftBody, dataInner, { size: 14, mono: exampleMono, min: 70 }),
    height(rightBody, dataInner, { size: 14, mono: exampleMono, min: 70 }),
  );
  const dataHeight = 24 + dataHeaderHeight + dataBodyHeight + 18;
  const responseY = dataY + dataHeight + 16;
  const responseHeaderHeight =
    height(responseHeader, 904, { size: 18, bold: true, min: 34 }) + 8;
  const responseBodyHeight = height(responseBody, 904, {
    size: 14,
    mono: exampleMono,
    min: 62,
  });
  const responseHeight = 24 + responseHeaderHeight + responseBodyHeight + 18;

  return svg(
    `${stages
      .map(
        ({ heading, detail }, index) => `<g data-stage="${stageNames[index]}">
        ${card(stageXs[index], stageY, stageWidth, stageHeight, { fill: index === 0 || index === 3 ? '#d0d0d0' : '#f0f0f0' })}
        ${label(heading, stageXs[index] + 16, stageY + 16, stageWidth - 32, stageMetrics[index].heading, { size: 18, bold: true })}
        ${label(detail, stageXs[index] + 16, stageY + 16 + stageMetrics[index].heading, stageWidth - 32, stageMetrics[index].detail, { size: 16, muted: true })}
      </g>`,
      )
      .join('')}
      ${stageNames
        .slice(0, -1)
        .map((name, index) =>
          edge(
            `${name}-to-${stageNames[index + 1]}`,
            arrow(
              stageXs[index] + stageWidth + 8,
              stageY + stageHeight / 2,
              stageXs[index + 1] - 8,
              stageY + stageHeight / 2,
            ),
            name,
            stageNames[index + 1],
          ),
        )
        .join('')}
      ${label(flowHeading, 24, flowTitleY, 952, flowTitleHeight, { size: 20, bold: true })}
      <g data-example="retrieved-text">
        ${card(24, dataY, dataWidth, dataHeight, { fill: '#f5f5f5' })}
        ${label(leftHeader, 48, dataY + 16, dataInner, dataHeaderHeight, { size: 18, bold: true })}
        ${label(leftBody, 48, dataY + 16 + dataHeaderHeight, dataInner, dataBodyHeight, { size: 14, mono: exampleMono, align: 'start' })}
      </g>
      <g data-example="augmented-prompt">
        ${card(516, dataY, dataWidth, dataHeight, { fill: '#f5f5f5' })}
        ${label(rightHeader, 540, dataY + 16, dataInner, dataHeaderHeight, { size: 18, bold: true })}
        ${label(rightBody, 540, dataY + 16 + dataHeaderHeight, dataInner, dataBodyHeight, { size: 14, mono: exampleMono, align: 'start' })}
      </g>
      <g data-example="generated-answer">
        ${card(24, responseY, 952, responseHeight)}
        ${label(responseHeader, 48, responseY + 16, 904, responseHeaderHeight, { size: 18, bold: true })}
        ${label(responseBody, 48, responseY + 16 + responseHeaderHeight, 904, responseBodyHeight, { size: 14, mono: exampleMono, align: 'start' })}
      </g>`,
    responseY + responseHeight + 24,
  );
}

function node(cx, cy) {
  return `<circle cx="${cx}" cy="${cy}" r="14" fill="#f0f0f0" stroke="#666666" stroke-width="2"/>`;
}

function layerEdges(kit, name, centers, cy, pairs) {
  return pairs
    .map(([from, to], index) =>
      edge(
        `${name}-${index + 1}`,
        kit.arrow(centers[from] + 14, cy, centers[to] - 14, cy, {
          arrow: false,
        }),
        `${name}-node-${from + 1}`,
        `${name}-node-${to + 1}`,
      ),
    )
    .join('');
}

function layoutLayeredSearch(labels, rtl) {
  const kit = figureKit(labels, { rtl });
  const { card, height, label, path, svg } = kit;
  const layers = [
    {
      key: 'layer-2',
      y: 24,
      centers: [360, 500, 640],
      pairs: [
        [0, 1],
        [1, 2],
      ],
      label: 0,
    },
    {
      key: 'layer-1',
      y: 198,
      centers: [250, 350, 450, 550, 650, 750],
      pairs: [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 4],
        [4, 5],
      ],
      label: 1,
    },
    {
      key: 'layer-0',
      y: 372,
      centers: [140, 220, 300, 380, 460, 540, 620, 700, 780, 860],
      pairs: [
        [0, 2],
        [1, 2],
        [2, 4],
        [3, 4],
        [4, 6],
        [5, 6],
        [6, 8],
        [7, 8],
      ],
      label: 2,
    },
  ];
  const layerHeight = 124;
  const cyOffset = 82;
  const firstBottom = layers[0].y + layerHeight;
  const secondBottom = layers[1].y + layerHeight;
  const resultY = layers[2].y + layerHeight + 32;
  const resultTextHeight = Math.max(
    height(5, 412, { size: 16, bold: true, min: 30 }) + 8,
    height(6, 412, { size: 16, min: 30 }),
  );
  const resultHeight = resultTextHeight + 32;
  return svg(
    `${layers
      .map(
        ({
          key,
          y,
          centers,
          pairs,
          label: labelIndex,
        }) => `<g data-layer="${key}">
        ${card(24, y, 952, layerHeight, { fill: '#ffffff', dash: true })}
        ${label(labelIndex, 48, y + 14, 904, height(labelIndex, 904, { size: 16, bold: true, min: 28 }) + 8, { size: 16, bold: true, muted: true, align: 'start' })}
        ${layerEdges(kit, key, centers, y + cyOffset, pairs)}
        ${centers.map((center) => node(center, y + cyOffset)).join('')}
      </g>`,
      )
      .join('')}
      ${edge('layer-2-to-layer-1', path(`M500 ${firstBottom + 8} L450 ${layers[1].y - 8}`), 'layer-2', 'layer-1')}
      ${label(3, 574, firstBottom + 5, 378, 44, { size: 16, muted: true })}
      ${edge('layer-1-to-layer-0', path(`M450 ${secondBottom + 8} L410 ${layers[2].y - 8}`), 'layer-1', 'layer-0')}
      ${label(4, 574, secondBottom + 5, 378, 44, { size: 16, muted: true })}
      <g data-result="incremental-update">
        ${card(24, resultY, 460, resultHeight)}
        ${label(5, 48, resultY + 16, 412, resultTextHeight, { size: 16, bold: true })}
      </g>
      <g data-result="query-complexity">
        ${card(516, resultY, 460, resultHeight, { fill: '#f5f5f5' })}
        ${label(6, 540, resultY + 16, 412, resultTextHeight, { size: 16 })}
      </g>`,
    resultY + resultHeight + 24,
  );
}

export function layoutMemoryFoundation(source, figure, { rtl = false } = {}) {
  const labels = labelsFor(source, figure);
  if (figure === 1) return layoutOverview(labels, rtl);
  if (figure === 3) return layoutMem0(labels, rtl);
  if (figure === 4) return layoutMemoryTypes(source, labels, rtl);
  if (figure === 5) return layoutRagFlow(source, labels, rtl);
  return layoutLayeredSearch(labels, rtl);
}
