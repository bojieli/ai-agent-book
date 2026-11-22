// Web-only reflows for Chapter 3 retrieval-structure figures. The tracked
// SVGs remain the source of every localized label.

import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

const shapeCount = (source, tag) =>
  (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;

function assertShape(source, figure, expected) {
  const valid = Object.entries(expected).every(([tag, count]) =>
    Array.isArray(count)
      ? count.includes(shapeCount(source, tag))
      : shapeCount(source, tag) === count,
  );
  if (!valid)
    throw new Error(
      `Figure 3-${figure} source structure changed; review its web layout.`,
    );
}

function hybridMap(count) {
  if (count === 25)
    return {
      dense: {
        title: 2,
        caption: 3,
        rows: [
          [4, 5],
          [6, 7],
          [8, 9],
        ],
      },
      sparse: {
        title: 10,
        caption: 11,
        rows: [
          [12, 13],
          [14, 15],
          [16, 17],
        ],
      },
      fusion: { title: [18, 19], caption: 20 },
      reranker: { title: [21, 22], caption: 23 },
      final: 24,
    };
  if (count === 22)
    return {
      dense: {
        title: 2,
        caption: 3,
        rows: [
          [4, 5],
          [6, 7],
          [8, 9],
        ],
      },
      sparse: {
        title: [10, 11],
        caption: 12,
        rows: [
          [13, 14],
          [15, 16],
          [17, 18],
        ],
      },
      fusion: { title: [19, 20], caption: 21 },
    };
  return {
    dense: {
      title: 2,
      caption: 3,
      rows: [
        [4, 5],
        [6, 7],
        [8, 9],
      ],
    },
    sparse: {
      title: 10,
      caption: 11,
      rows: [
        [12, 13],
        [14, 15],
        [16, 17],
      ],
    },
    fusion: { title: [18, 19], caption: 20 },
  };
}

function layoutHybridRetrieval(labels, rtl) {
  const k = figureKit(labels, { rtl });
  const groups = hybridMap(labels.length);
  const laneTitleHeight = Math.max(
    k.height(groups.dense.title, 416, { size: 20, bold: true }),
    k.height(groups.sparse.title, 416, { size: 20, bold: true }),
  );
  const laneCaptionHeight = Math.max(
    k.height(groups.dense.caption, 416, { size: 16 }),
    k.height(groups.sparse.caption, 416, { size: 16 }),
  );
  const resultRowHeight = Math.max(
    ...[...groups.dense.rows, ...groups.sparse.rows].flatMap(
      ([document, score]) => [
        k.height(document, 310, { size: 14, mono: true }),
        k.height(score, 90, { size: 14 }),
      ],
    ),
  );
  const laneHeight =
    16 +
    laneTitleHeight +
    8 +
    laneCaptionHeight +
    12 +
    resultRowHeight * 3 +
    8 * 2 +
    16;
  const denseY = 24;
  const sparseY = denseY + laneHeight + 40;
  const lane = ({ title, caption, rows }, y, name) => {
    const captionY = y + 16 + laneTitleHeight + 8;
    const rowsY = captionY + laneCaptionHeight + 12;
    return `
    <g data-retrieval-lane="${name}">
      ${k.card(240, y, 448, laneHeight)}
      ${k.label(title, 256, y + 16, 416, laneTitleHeight, { size: 20, bold: true })}
      ${k.label(caption, 256, captionY, 416, laneCaptionHeight, { size: 16, muted: true })}
      ${rows
        .map(
          ([document, score], row) =>
            `${k.label(
              document,
              258,
              rowsY + row * (resultRowHeight + 8),
              310,
              resultRowHeight,
              {
                size: 14,
                mono: true,
                align: 'start',
                direction: rtl ? 'rtl' : 'ltr',
              },
            )}${k.label(
              score,
              580,
              rowsY + row * (resultRowHeight + 8),
              90,
              resultRowHeight,
              {
                size: 14,
                muted: true,
                align: 'end',
                direction: 'ltr',
              },
            )}`,
        )
        .join('')}
    </g>`;
  };

  const extended = Boolean(groups.reranker);
  const queryTitleHeight = k.height(0, 144, { size: 18, bold: true });
  const queryCodeHeight = k.height(1, 144, { size: 14, mono: true });
  const queryHeight = 16 + queryTitleHeight + 8 + queryCodeHeight + 16;
  const lanesBottom = sparseY + laneHeight;
  const queryY = denseY + (lanesBottom - denseY - queryHeight) / 2;
  const fusionTitleHeight = k.height(groups.fusion.title, 208, {
    size: 18,
    bold: true,
  });
  const fusionCaptionHeight = k.height(groups.fusion.caption, 208, {
    size: 14,
  });
  const fusionHeight = 20 + fusionTitleHeight + 10 + fusionCaptionHeight + 20;
  const fusionY = denseY + (lanesBottom - denseY - fusionHeight) / 2;
  const fusion = `
    <g data-retrieval-stage="fusion">
      ${k.card(736, fusionY, 240, fusionHeight, { fill: '#d0d0d0' })}
      ${k.label(groups.fusion.title, 752, fusionY + 20, 208, fusionTitleHeight, { size: 18, bold: true })}
      ${k.label(groups.fusion.caption, 752, fusionY + 30 + fusionTitleHeight, 208, fusionCaptionHeight, { size: 14, muted: true, direction: 'ltr' })}
    </g>`;
  let postProcessing = '';
  let postProcessingBottom = fusionY + fusionHeight;
  if (extended) {
    const rerankerTitleHeight = k.height(groups.reranker.title, 208, {
      size: 18,
      bold: true,
    });
    const rerankerCaptionHeight = k.height(groups.reranker.caption, 208, {
      size: 14,
    });
    const rerankerHeight =
      16 + rerankerTitleHeight + 10 + rerankerCaptionHeight + 16;
    const rerankerY = fusionY + fusionHeight + 48;
    const finalTitleHeight = k.height(groups.final, 208, {
      size: 18,
      bold: true,
    });
    const finalHeight = 16 + finalTitleHeight + 16;
    const finalY = rerankerY + rerankerHeight + 48;
    postProcessingBottom = finalY + finalHeight;
    postProcessing = `
      ${k.arrow(856, fusionY + fusionHeight + 8, 856, rerankerY - 8)}
      <g data-retrieval-stage="reranker">
        ${k.card(736, rerankerY, 240, rerankerHeight)}
        ${k.label(groups.reranker.title, 752, rerankerY + 16, 208, rerankerTitleHeight, { size: 18, bold: true })}
        ${k.label(groups.reranker.caption, 752, rerankerY + 26 + rerankerTitleHeight, 208, rerankerCaptionHeight, { size: 14, muted: true })}
      </g>
      ${k.arrow(856, rerankerY + rerankerHeight + 8, 856, finalY - 8)}
      <g data-retrieval-stage="final-ranking">
        ${k.card(736, finalY, 240, finalHeight, { fill: '#d0d0d0' })}
        ${k.label(groups.final, 752, finalY + 16, 208, finalTitleHeight, { size: 18, bold: true })}
      </g>`;
  }

  return k.svg(
    `<g data-figure="3-9" data-variant="${extended ? 'extended' : 'compact'}">
      ${k.card(16, queryY, 176, queryHeight, { fill: '#d0d0d0' })}
      ${k.label(0, 32, queryY + 16, 144, queryTitleHeight, { size: 18, bold: true })}
      ${k.label(1, 32, queryY + 24 + queryTitleHeight, 144, queryCodeHeight, { size: 14, mono: true, direction: rtl ? 'rtl' : 'ltr' })}
      ${lane(groups.dense, denseY, 'dense')}
      ${lane(groups.sparse, sparseY, 'sparse')}
      ${k.arrow(200, queryY + queryHeight * 0.38, 232, denseY + laneHeight / 2)}
      ${k.arrow(200, queryY + queryHeight * 0.62, 232, sparseY + laneHeight / 2)}
      ${k.arrow(696, denseY + laneHeight / 2, 728, fusionY + fusionHeight * 0.32)}
      ${k.arrow(696, sparseY + laneHeight / 2, 728, fusionY + fusionHeight * 0.68)}
      ${fusion}
      ${postProcessing}
    </g>`,
    Math.max(lanesBottom, postProcessingBottom) + 24,
  );
}

function recursiveMap(count) {
  if (count === 16)
    return {
      root: [0, 1],
      clusters: [2, 3, 4],
      middle: 5,
      chunks: [[6], [7], [8], [9], [10], [11], [12]],
      leaf: 13,
      document: 14,
      caption: 15,
    };
  return {
    root: [0, 1],
    clusters: [2, 3, 4],
    middle: 5,
    chunks: [
      [6, 7],
      [8, 9],
      [10, 11],
      [12, 13],
      [14, 15],
      [16, 17],
      [18, 19],
    ],
    leaf: 20,
    document: 21,
    caption: 22,
  };
}

function layoutRecursiveAbstraction(labels, rtl) {
  const k = figureKit(labels, { rtl });
  const groups = recursiveMap(labels.length);
  const clusterX = [240, 525, 753];
  const chunkX = Array.from({ length: 7 }, (_, index) => 176 + index * 114);
  const clusterCenters = clusterX.map((x) => x + 100);
  const chunkCenters = chunkX.map((x) => x + 50);
  const clusterChildren = [
    [0, 1, 2],
    [3, 4],
    [5, 6],
  ];
  const rootTitleHeight = k.height(groups.root[0], 418, {
    size: 20,
    bold: true,
  });
  const rootCaptionHeight = k.height(groups.root[1], 418, { size: 14 });
  const rootHeight = 16 + rootTitleHeight + 8 + rootCaptionHeight + 16;
  const rootY = 24;
  const clusterTitleHeight = Math.max(
    ...groups.clusters.map((index) =>
      k.height(index, 168, { size: 18, bold: true }),
    ),
  );
  const clusterHeight = 16 + clusterTitleHeight + 16;
  const clusterY = rootY + rootHeight + 56;
  const chunkTitleHeight = Math.max(
    ...groups.chunks.map((indices) =>
      k.height(indices, 76, { size: 16, bold: true }),
    ),
  );
  const chunkHeight = 16 + chunkTitleHeight + 16;
  const chunkY = clusterY + clusterHeight + 80;
  const documentTitleHeight = k.height(groups.document, 764, {
    size: 18,
    bold: true,
  });
  const documentHeight = 16 + documentTitleHeight + 16;
  const documentY = chunkY + chunkHeight + 40;
  const captionHeight = k.height(groups.caption, 936, { size: 14 });
  const captionY = documentY + documentHeight + 32;
  const branchY = rootY + rootHeight + 28;
  const leafBranchY = clusterY + clusterHeight + 40;
  const rootBranches = clusterCenters
    .map((center) =>
      k.path(
        `M575 ${rootY + rootHeight} L575 ${branchY} L${center} ${branchY} L${center} ${clusterY}`,
        { arrow: false },
      ),
    )
    .join('');
  const leafBranches = clusterChildren
    .map(
      (children, clusterIndex) =>
        `<g data-cluster-index="${clusterIndex}" data-chunk-columns="${children.join(' ')}">${children
          .map((chunkIndex) =>
            k.path(
              `M${clusterCenters[clusterIndex]} ${clusterY + clusterHeight} L${clusterCenters[clusterIndex]} ${leafBranchY} L${chunkCenters[chunkIndex]} ${leafBranchY} L${chunkCenters[chunkIndex]} ${chunkY}`,
              { arrow: false },
            ),
          )
          .join('')}</g>`,
    )
    .join('');
  const middleHeight = k.height(groups.middle, 128, { size: 14 });
  const leafHeight = k.height(groups.leaf, 128, { size: 14 });

  return k.svg(
    `<g data-figure="3-10" data-tree-connectors="directionless">
      ${rootBranches}
      ${leafBranches}
      ${k.card(350, rootY, 450, rootHeight, { fill: '#d0d0d0' })}
      ${k.label(groups.root[0], 366, rootY + 16, 418, rootTitleHeight, { size: 20, bold: true })}
      ${k.label(groups.root[1], 366, rootY + 24 + rootTitleHeight, 418, rootCaptionHeight, { size: 14, muted: true })}
      ${groups.clusters
        .map(
          (index, column) =>
            `${k.card(clusterX[column], clusterY, 200, clusterHeight)}${k.label(
              index,
              clusterX[column] + 16,
              clusterY + 16,
              168,
              clusterTitleHeight,
              { size: 18, bold: true },
            )}`,
        )
        .join('')}
      ${k.label(groups.middle, 24, clusterY + (clusterHeight - middleHeight) / 2, 128, middleHeight, { size: 14, muted: true, align: 'start' })}
      ${groups.chunks
        .map(
          (indices, column) =>
            `${k.card(chunkX[column], chunkY, 100, chunkHeight)}${k.label(
              indices,
              chunkX[column] + 12,
              chunkY + 16,
              76,
              chunkTitleHeight,
              { size: 16, bold: true },
            )}`,
        )
        .join('')}
      ${k.label(groups.leaf, 24, chunkY + (chunkHeight - leafHeight) / 2, 128, leafHeight, { size: 14, muted: true, align: 'start' })}
      ${k.card(176, documentY, 796, documentHeight, { fill: '#d0d0d0' })}
      ${k.label(groups.document, 192, documentY + 16, 764, documentTitleHeight, { size: 18, bold: true })}
      ${k.label(groups.caption, 32, captionY, 936, captionHeight, { size: 14, muted: true })}
    </g>`,
    captionY + captionHeight + 24,
  );
}

function graphMap(count) {
  if (count === 20)
    return {
      user: [0],
      doctorA: [1, 2],
      hospitalA: [3, 4],
      address: [5, 6],
      doctorB: [7, 8],
      hospitalB: [9, 10],
      relationships: [11, 12, 13, 14, 15],
      captions: [16, 17, 18, 19],
    };
  return {
    user: [0],
    doctorA: [1, 2],
    hospitalA: [3],
    address: [4, 5],
    doctorB: [6, 7],
    hospitalB: [8, 9],
    relationships: [10, 11, 12, 13, 14],
    captions: Array.from({ length: count - 15 }, (_, index) => index + 15),
  };
}

function layoutKnowledgeGraph(labels, rtl) {
  const k = figureKit(labels, { rtl });
  const groups = graphMap(labels.length);
  const [userA, userB, worksA, address, worksB] = groups.relationships;
  const specs = [
    {
      key: 'user',
      indices: groups.user,
      x: 24,
      width: 120,
      singleTitle: true,
      row: 'top',
    },
    {
      key: 'doctor-a',
      indices: groups.doctorA,
      x: 246,
      width: 190,
      row: 'top',
    },
    {
      key: 'hospital-a',
      indices: groups.hospitalA,
      x: 524,
      width: 190,
      singleTitle: true,
      row: 'top',
    },
    { key: 'address', indices: groups.address, x: 802, width: 174, row: 'top' },
    {
      key: 'doctor-b',
      indices: groups.doctorB,
      x: 246,
      width: 190,
      row: 'bottom',
    },
    {
      key: 'hospital-b',
      indices: groups.hospitalB,
      x: 524,
      width: 210,
      row: 'bottom',
    },
  ].map((spec) => {
    const title = spec.singleTitle ? spec.indices : spec.indices.slice(0, -1);
    const detail = spec.singleTitle ? [] : spec.indices.slice(-1);
    const titleHeight = k.height(title, spec.width - 32, {
      size: 18,
      bold: true,
    });
    const detailHeight = detail.length
      ? k.height(detail, spec.width - 32, { size: 16 })
      : 0;
    return {
      ...spec,
      title,
      detail,
      titleHeight,
      detailHeight,
      neededHeight:
        16 + titleHeight + (detail.length ? 8 + detailHeight : 0) + 16,
    };
  });
  const topHeight = Math.max(
    ...specs
      .filter(({ row }) => row === 'top')
      .map(({ neededHeight }) => neededHeight),
  );
  const bottomHeight = Math.max(
    ...specs
      .filter(({ row }) => row === 'bottom')
      .map(({ neededHeight }) => neededHeight),
  );
  const topY = 60;
  const bottomY = topY + topHeight + 80;
  const topCenter = topY + topHeight / 2;
  const bottomCenter = bottomY + bottomHeight / 2;
  const captionY = bottomY + bottomHeight + 48;
  const captionHeight = k.height(groups.captions, 936, { size: 14 });
  const relationshipHeight = Math.max(
    ...groups.relationships.map((index, position) =>
      k.height(index, [86, 92, 72, 72, 72][position], { size: 14 }),
    ),
  );
  const node = (spec) => {
    const y = spec.row === 'top' ? topY : bottomY;
    const cardHeight = spec.row === 'top' ? topHeight : bottomHeight;
    const textY = y + 16 + (cardHeight - spec.neededHeight) / 2;
    return `<g data-graph-node="${spec.key}">${k.card(spec.x, y, spec.width, cardHeight)}${k.label(
      spec.title,
      spec.x + 16,
      textY,
      spec.width - 32,
      spec.titleHeight,
      {
        size: 18,
        bold: true,
      },
    )}${
      spec.detail.length
        ? k.label(
            spec.detail,
            spec.x + 16,
            textY + 8 + spec.titleHeight,
            spec.width - 32,
            spec.detailHeight,
            { size: 16, muted: true },
          )
        : ''
    }</g>`;
  };

  return k.svg(
    `<g data-figure="3-11" data-graph="knowledge-relations">
      ${k.arrow(152, topCenter, 238, topCenter)}
      ${k.path(`M84 ${topY + topHeight + 8} L84 ${bottomCenter} L238 ${bottomCenter}`)}
      ${k.arrow(444, topCenter, 516, topCenter)}
      ${k.arrow(722, topCenter, 794, topCenter)}
      ${k.arrow(444, bottomCenter, 516, bottomCenter)}
      ${specs.map(node).join('')}
      ${k.label(userA, 152, topCenter - relationshipHeight - 4, 86, relationshipHeight, { size: 14, muted: true })}
      ${k.label(userB, 146, bottomCenter - relationshipHeight - 4, 92, relationshipHeight, { size: 14, muted: true })}
      ${k.label(worksA, 444, topCenter - relationshipHeight - 4, 72, relationshipHeight, { size: 14, muted: true })}
      ${k.label(address, 722, topCenter - relationshipHeight - 4, 72, relationshipHeight, { size: 14, muted: true })}
      ${k.label(worksB, 444, bottomCenter - relationshipHeight - 4, 72, relationshipHeight, { size: 14, muted: true })}
      ${k.label(groups.captions, 32, captionY, 936, captionHeight, { size: 14, muted: true, align: 'start' })}
    </g>`,
    captionY + captionHeight + 24,
  );
}

function layoutAgenticComparison(labels, rtl) {
  const k = figureKit(labels, { rtl });
  const panelTitleHeight = Math.max(
    k.height(0, 420, { size: 20, bold: true }),
    k.height(5, 420, { size: 20, bold: true }),
  );
  const panelSubtitleHeight = Math.max(
    k.height(1, 420, { size: 18, bold: true }),
    k.height(6, 420, { size: 18, bold: true }),
  );
  const panelHeight = 16 + panelTitleHeight + 8 + panelSubtitleHeight + 16;
  const panelY = 24;
  const rowPairs = [
    [2, 7],
    [3, 8],
    [4, 9],
  ];
  const rowLabelHeights = rowPairs.map(([left, right]) =>
    Math.max(
      k.height(left, 328, { size: 16 }),
      k.height(right, 308, { size: 16 }),
    ),
  );
  const rowHeights = rowLabelHeights.map((height) => 16 + height + 16);
  const rowY = [panelY + panelHeight + 48];
  rowY.push(rowY[0] + rowHeights[0] + 48);
  rowY.push(rowY[1] + rowHeights[1] + 48);
  const resultLabelHeight = k.height(11, 308, { size: 18, bold: true });
  const resultHeight = 16 + resultLabelHeight + 16;
  const resultY = rowY[2] + rowHeights[2] + 48;
  const panel = (x, title, subtitle, fill) => `
    ${k.card(x, panelY, 452, panelHeight, { fill })}
    ${k.label(title, x + 16, panelY + 16, 420, panelTitleHeight, { size: 20, bold: true })}
    ${k.label(subtitle, x + 16, panelY + 24 + panelTitleHeight, 420, panelSubtitleHeight, { size: 18, bold: true, muted: true })}`;
  const step = (index, x, y, width, height, labelHeight) => `
    ${k.card(x, y, width, height)}
    ${k.label(index, x + 16, y + 16, width - 32, labelHeight, { size: 16 })}`;
  const loopCaptionHeight = k.height(10, 62, { size: 14 });
  const secondCenter = rowY[1] + rowHeights[1] / 2;
  const thirdCenter = rowY[2] + rowHeights[2] / 2;
  const loopCaptionY = (secondCenter + thirdCenter - loopCaptionHeight) / 2;

  return k.svg(
    `<g data-figure="3-12" data-comparison="agentic-rag">
      ${panel(24, 0, 1, '#f0f0f0')}
      ${panel(524, 5, 6, '#eef3f6')}
      ${step(2, 70, rowY[0], 360, rowHeights[0], rowLabelHeights[0])}
      ${k.arrow(250, rowY[0] + rowHeights[0] + 8, 250, rowY[1] - 8)}
      ${step(3, 70, rowY[1], 360, rowHeights[1], rowLabelHeights[1])}
      ${k.arrow(250, rowY[1] + rowHeights[1] + 8, 250, rowY[2] - 8)}
      ${step(4, 70, rowY[2], 360, rowHeights[2], rowLabelHeights[2])}
      ${step(7, 548, rowY[0], 340, rowHeights[0], rowLabelHeights[0])}
      ${k.arrow(718, rowY[0] + rowHeights[0] + 8, 718, rowY[1] - 8)}
      ${step(8, 548, rowY[1], 340, rowHeights[1], rowLabelHeights[1])}
      ${k.arrow(718, rowY[1] + rowHeights[1] + 8, 718, rowY[2] - 8)}
      ${step(9, 548, rowY[2], 340, rowHeights[2], rowLabelHeights[2])}
      ${k.path(`M896 ${thirdCenter} L968 ${thirdCenter} L968 ${secondCenter} L896 ${secondCenter}`, { dash: true })}
      ${k.label(10, 898, loopCaptionY, 62, loopCaptionHeight, { size: 14, muted: true })}
      ${k.arrow(718, rowY[2] + rowHeights[2] + 8, 718, resultY - 8)}
      ${k.card(548, resultY, 340, resultHeight, { fill: '#dfeef0' })}
      ${k.label(11, 564, resultY + 16, 308, resultLabelHeight, { size: 18, bold: true })}
    </g>`,
    resultY + resultHeight + 24,
  );
}

export function layoutRetrievalStructure(source, figure, { rtl = false } = {}) {
  if (![9, 10, 11, 12].includes(figure))
    throw new Error('Unsupported retrieval structure figure');
  const allowed = { 9: [21, 22, 25], 10: [16, 23], 11: [17, 19, 20], 12: [12] }[
    figure
  ];
  const labels = extractLabels(source, `3-${figure}`, allowed);
  const expectedShapes = {
    9: { rect: [4, 5], line: [4, 6] },
    10: { rect: 18, line: 10 },
    11: { rect: 6, line: 5 },
    12: { rect: 9, line: 8 },
  };
  assertShape(source, figure, expectedShapes[figure]);
  if (figure === 9) return layoutHybridRetrieval(labels, rtl);
  if (figure === 10) return layoutRecursiveAbstraction(labels, rtl);
  if (figure === 11) return layoutKnowledgeGraph(labels, rtl);
  return layoutAgenticComparison(labels, rtl);
}
