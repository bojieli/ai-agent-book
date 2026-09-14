// Web-only reflows for Chapter 5 application and bootstrapping figures. The
// tracked SVGs remain the source of every localized label.

import { figureKit } from './chapter3-figure-kit.mjs';

const specifications = {
  8: { labels: [40], rect: 13, line: 4, path: 0, marker: 2, polygon: 2 },
  9: {
    labels: [39, 40, 42],
    rect: 17,
    line: 7,
    path: 1,
    marker: 2,
    polygon: 2,
  },
  10: { labels: [39], rect: 14, line: 5, path: 0, marker: 2, polygon: 2 },
  11: { labels: [43], rect: 13, line: 6, path: 0, marker: 2, polygon: 2 },
};

const count = (source, tag) =>
  (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;

function textNodes(source) {
  return [
    ...source.matchAll(/<text\b([^>]*?)(?:\/>|>([\s\S]*?)<\/text>)/g),
  ].map(([, attributes, pairedContent], index) => {
    const content = pairedContent ?? '';
    const coordinate = (name) =>
      Number(attributes.match(new RegExp(`\\b${name}="(-?[\\d.]+)`))?.[1]);
    let y = coordinate('y');
    if (y === 0) {
      const tspanY = content.match(/<tspan\b[^>]*\bdy="(-?[\d.]+)"/)?.[1];
      if (tspanY) y = Number(tspanY);
    }
    return {
      index,
      x: coordinate('x'),
      y,
      bold: /\bfont-weight="bold"/.test(attributes),
      mono: /Courier/.test(attributes),
      muted: /\bfill="#666666"/.test(attributes),
      content,
    };
  });
}

function labelsFor(source, figure, nodes) {
  const specification = specifications[figure];
  if (!specification)
    throw new Error(`Unsupported coding application figure: ${figure}`);
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !['rect', 'line', 'path', 'marker', 'polygon'].every(
      (tag) => count(source, tag) === specification[tag],
    )
  )
    throw new Error(
      `Figure 5-${figure} source structure changed; review its web layout.`,
    );
  const labels = nodes.map(({ content, mono }) => {
    const text = content
      .replace(/<tspan\b[^>]*>/g, '')
      .replace(/<\/tspan>/g, ' ');
    return mono
      ? text.replace(/[\r\n]/g, '').replace(/\s+$/, '')
      : text.replace(/\s+/g, ' ').trim();
  });
  if (
    !specification.labels.includes(labels.length) ||
    labels.some((label) => /<[^>]+>/.test(label))
  )
    throw new Error(
      `Figure 5-${figure} source labels changed; review its web layout.`,
    );
  return labels;
}

function edge(name, content, from, to, extra = '') {
  return `<g data-edge="${name}" data-from="${from}" data-to="${to}"${extra}>${content}</g>`;
}

function verticalEdge(kit, name, from, to, x, fromBottom, toTop, options) {
  return edge(
    name,
    kit.arrow(x, fromBottom + 8, x, toTop - 8, options),
    from,
    to,
  );
}

function rowMetrics(
  kit,
  ids,
  width,
  { size = 14, mono = false, min = 26 } = {},
) {
  const heights = ids.map((id) => kit.height(id, width, { size, mono, min }));
  return {
    heights,
    total:
      heights.reduce((sum, value) => sum + value, 0) +
      Math.max(0, heights.length - 1) * 4,
  };
}

function codeRows(kit, nodes, ids, x, y, width, metrics, rtl, key) {
  let content = '';
  ids.forEach((id, line) => {
    const label = kit
      .label(id, x, y, width, metrics.heights[line], {
        size: 14,
        mono: true,
        align: 'start',
        direction: rtl ? 'rtl' : 'ltr',
      })
      .replace(
        'overflow-wrap:anywhere',
        'white-space:pre-wrap;overflow-wrap:anywhere',
      );
    content += `<g data-code-line="${key}:${line}">${label}</g>`;
    y += metrics.heights[line] + 4;
  });
  return content;
}

function bodyRows(kit, ids, x, y, width, metrics, key) {
  let content = '';
  ids.forEach((id, line) => {
    content += `<g data-body-line="${key}:${line}">${kit.label(id, x, y, width, metrics.heights[line], { size: 16, align: 'start' })}</g>`;
    y += metrics.heights[line] + 4;
  });
  return content;
}

export function layoutCodingApplication(source, figure, { rtl = false } = {}) {
  const nodes = textNodes(source);
  const labels = labelsFor(source, figure, nodes);
  const kit = figureKit(labels, { rtl });
  if (figure === 8) return layoutDynamicForm(kit, nodes, rtl);
  if (figure === 9) return layoutArtifactFlow(kit, nodes, rtl);
  if (figure === 10) return layoutBootstrapping(kit, nodes, rtl);
  return layoutMetaAgent(kit, nodes, rtl);
}

function layoutDynamicForm(kit, nodes, rtl) {
  const stageX = 120;
  const stageWidth = 760;
  const innerWidth = 712;
  const gap = 64;
  let y = 24;
  let content = '';

  const userTitleH = kit.height(0, innerWidth, { size: 18, bold: true });
  const userBodyH = kit.height(1, innerWidth, { size: 16 });
  const userH = 20 + userTitleH + 8 + userBodyH + 20;
  content += `<g data-form-stage="user">${kit.card(stageX, y, stageWidth, userH, { fill: '#d0d0d0' })}${kit.label(0, stageX + 24, y + 20, innerWidth, userTitleH, { size: 18, bold: true })}${kit.label(1, stageX + 24, y + 28 + userTitleH, innerWidth, userBodyH, { size: 16, muted: true })}</g>`;
  const userBottom = y + userH;

  const formCodeY = userBottom + gap;
  content += verticalEdge(
    kit,
    'user-to-form-code',
    'user',
    'form-code',
    500,
    userBottom,
    formCodeY,
  );
  const codeTitleH = kit.height(2, innerWidth, { size: 18, bold: true });
  const formCode = rowMetrics(
    kit,
    Array.from({ length: 10 }, (_, index) => index + 3),
    innerWidth - 32,
    { size: 14, mono: true },
  );
  const formCodeH = 20 + codeTitleH + 16 + formCode.total + 32 + 20;
  content += `<g data-form-stage="form-code">${kit.card(stageX, formCodeY, stageWidth, formCodeH, { fill: '#ffffff', dash: true })}${kit.label(2, stageX + 24, formCodeY + 20, innerWidth, codeTitleH, { size: 18, bold: true })}${kit.card(stageX + 24, formCodeY + 36 + codeTitleH, innerWidth, formCode.total + 24, { fill: '#f5f5f5' })}${codeRows(
    kit,
    nodes,
    Array.from({ length: 10 }, (_, index) => index + 3),
    stageX + 40,
    formCodeY + 48 + codeTitleH,
    innerWidth - 32,
    formCode,
    rtl,
    'form-html',
  )}</g>`;
  const formCodeBottom = formCodeY + formCodeH;

  const renderedY = formCodeBottom + gap;
  content += verticalEdge(
    kit,
    'form-code-to-rendered-form',
    'form-code',
    'rendered-form',
    500,
    formCodeBottom,
    renderedY,
  );
  const renderedTitleH = kit.height(13, innerWidth, { size: 18, bold: true });
  const fields = [
    [14, 15],
    [16, 17],
    [18, 19],
    [20, 21],
  ];
  const fieldLabelH = Math.max(
    ...fields.map(([label]) =>
      kit.height(label, 300, { size: 16, bold: true }),
    ),
  );
  const fieldValueH = Math.max(
    ...fields.map(([, value]) =>
      kit.height(value, 300, { size: 14, mono: true }),
    ),
  );
  const fieldH = 16 + fieldLabelH + 8 + fieldValueH + 16;
  const submitH = kit.height(22, 208, { size: 18, bold: true });
  const renderedH = 20 + renderedTitleH + 20 + fieldH * 2 + 16 + submitH + 40;
  content += `<g data-form-stage="rendered-form">${kit.card(stageX, renderedY, stageWidth, renderedH, { fill: '#ffffff' })}${kit.label(13, stageX + 24, renderedY + 20, innerWidth, renderedTitleH, { size: 18, bold: true })}`;
  const fieldsY = renderedY + 40 + renderedTitleH;
  fields.forEach(([label, value], field) => {
    const column = field % 2;
    const row = Math.floor(field / 2);
    const x = stageX + 24 + column * 356;
    const fieldY = fieldsY + row * (fieldH + 8);
    content += `<g data-form-field="${field}">${kit.card(x, fieldY, 340, fieldH, { fill: '#f5f5f5' })}${kit.label(label, x + 16, fieldY + 16, 308, fieldLabelH, { size: 16, bold: true, align: 'start' })}${kit.label(value, x + 16, fieldY + 24 + fieldLabelH, 308, fieldValueH, { size: 14, mono: true, align: 'start', direction: rtl ? 'rtl' : 'ltr' })}</g>`;
  });
  content += `${kit.card(380, renderedY + renderedH - submitH - 36, 240, submitH + 16, { fill: '#d0d0d0' })}${kit.label(22, 396, renderedY + renderedH - submitH - 28, 208, submitH, { size: 18, bold: true })}</g>`;
  const renderedBottom = renderedY + renderedH;

  const jsonY = renderedBottom + gap;
  content += verticalEdge(
    kit,
    'rendered-form-to-json',
    'rendered-form',
    'json',
    500,
    renderedBottom,
    jsonY,
  );
  const jsonTitleH = kit.height(23, innerWidth, { size: 18, bold: true });
  const jsonIds = [24, 25, 26, 27];
  const json = rowMetrics(kit, jsonIds, innerWidth - 32, {
    size: 14,
    mono: true,
  });
  const jsonH = 20 + jsonTitleH + 16 + json.total + 32 + 20;
  content += `<g data-form-stage="json">${kit.card(stageX, jsonY, stageWidth, jsonH, { fill: '#ffffff', dash: true })}${kit.label(23, stageX + 24, jsonY + 20, innerWidth, jsonTitleH, { size: 18, bold: true })}${kit.card(stageX + 24, jsonY + 36 + jsonTitleH, innerWidth, json.total + 24, { fill: '#f5f5f5' })}${codeRows(kit, nodes, jsonIds, stageX + 40, jsonY + 48 + jsonTitleH, innerWidth - 32, json, rtl, 'json')}</g>`;
  const jsonBottom = jsonY + jsonH;

  const agentY = jsonBottom + gap;
  content += verticalEdge(
    kit,
    'json-to-agent',
    'json',
    'agent',
    500,
    jsonBottom,
    agentY,
  );
  const agentTitleH = kit.height(28, innerWidth, { size: 20, bold: true });
  const agentCodeH = kit.height(29, innerWidth, { size: 14, mono: true });
  const agentH = 20 + agentTitleH + 10 + agentCodeH + 20;
  content += `<g data-form-stage="agent">${kit.card(stageX, agentY, stageWidth, agentH, { fill: '#d0d0d0' })}${kit.label(28, stageX + 24, agentY + 20, innerWidth, agentTitleH, { size: 20, bold: true })}${kit.label(29, stageX + 24, agentY + 30 + agentTitleH, innerWidth, agentCodeH, { size: 14, mono: true, direction: rtl ? 'rtl' : 'ltr' })}</g>`;

  const comparisonY = agentY + agentH + 48;
  const comparisonTitleH = kit.height(30, 904, { size: 20, bold: true });
  const comparisonIds = Array.from({ length: 8 }, (_, index) => index + 31);
  const comparison = rowMetrics(kit, comparisonIds, 872, {
    size: 16,
  });
  const comparisonH = 20 + comparisonTitleH + 16 + comparison.total + 32 + 20;
  content += `<g data-form-comparison="plain-text-vs-form">${kit.card(24, comparisonY, 952, comparisonH, { fill: '#f0f0f0' })}${kit.label(30, 48, comparisonY + 20, 904, comparisonTitleH, { size: 20, bold: true })}${kit.card(48, comparisonY + 36 + comparisonTitleH, 904, comparison.total + 24, { fill: '#f5f5f5' })}${bodyRows(kit, comparisonIds, 64, comparisonY + 48 + comparisonTitleH, 872, comparison, 'comparison')}</g>`;
  const noteY = comparisonY + comparisonH + 20;
  const noteH = kit.height(39, 920, { size: 16 });
  content += kit.label(39, 40, noteY, 920, noteH, {
    size: 16,
    muted: true,
  });
  return kit.svg(content, noteY + noteH + 20);
}

function artifactGroups(nodes) {
  const topProblem = nodes.findIndex(({ y }) => y >= 170 && y < 260);
  const bottomTitle = nodes.findIndex(({ y }) => y >= 270);
  if (topProblem < 0 || bottomTitle < 0 || bottomTitle !== topProblem + 1)
    throw new Error('Figure 5-9 section order changed; review its web layout.');
  const topBody = nodes.slice(2, topProblem);
  const topHeadings = topBody
    .map((node, position) => (node.bold ? position : -1))
    .filter((position) => position >= 0);
  if (topHeadings.length !== 5)
    throw new Error(
      'Figure 5-9 traditional stages changed; review its web layout.',
    );
  const traditional = topHeadings.map((start, stage) => ({
    title: topBody[start].index,
    detail: topBody
      .slice(start + 1, topHeadings[stage + 1] ?? topBody.length)
      .map(({ index }) => index),
  }));

  const summaryStart = nodes.findIndex(
    ({ y }, index) => index > bottomTitle && y >= 450,
  );
  const bottomBody = nodes.slice(bottomTitle + 2, summaryStart);
  const bottomHeadings = bottomBody
    .map((node, position) =>
      node.bold && node.y >= 315 && node.y < 375 ? position : -1,
    )
    .filter((position) => position >= 0);
  if (bottomHeadings.length !== 3)
    throw new Error(
      'Figure 5-9 artifact stages changed; review its web layout.',
    );
  const artifact = bottomHeadings.map((start, stage) => ({
    title: bottomBody[start].index,
    rows: bottomBody.slice(
      start + 1,
      bottomHeadings[stage + 1] ?? bottomBody.length,
    ),
  }));
  const summary = nodes
    .slice(summaryStart, summaryStart + 2)
    .map(({ index }) => index);
  const dataLabel = nodes.slice(summaryStart + 2).map(({ index }) => index);
  if (
    traditional.some(({ detail }) => detail.length < 1 || detail.length > 2) ||
    artifact[0].rows.length !== 6 ||
    artifact[1].rows.length !== 6 ||
    ![4, 5].includes(artifact[2].rows.length) ||
    summary.length !== 2 ||
    dataLabel.length > 1
  )
    throw new Error('Figure 5-9 stage rows changed; review its web layout.');
  return {
    topTitle: nodes[0].index,
    topBadge: nodes[1].index,
    traditional,
    problem: nodes[topProblem].index,
    bottomTitle: nodes[bottomTitle].index,
    bottomBadge: nodes[bottomTitle + 1].index,
    artifact,
    summary,
    dataLabel,
  };
}

function layoutArtifactFlow(kit, nodes, rtl) {
  const groups = artifactGroups(nodes);
  const outerX = 16;
  const outerWidth = 968;
  const titleWidth = 720;
  const badgeTextWidth = 160;
  const topTitleH = kit.height(groups.topTitle, titleWidth, {
    size: 20,
    bold: true,
  });
  const topBadgeH = kit.height(groups.topBadge, badgeTextWidth, {
    size: 16,
    bold: true,
  });
  const stageWidth = 140;
  const stageGap = 58;
  const stageTitleH = Math.max(
    ...groups.traditional.map(({ title }) =>
      kit.height(title, stageWidth - 24, { size: 18, bold: true }),
    ),
  );
  const stageDetailH = Math.max(
    ...groups.traditional.map(({ detail }) =>
      kit.height(detail, stageWidth - 24, { size: 16 }),
    ),
  );
  const stageH = 16 + stageTitleH + 8 + stageDetailH + 16;
  const problemH = kit.height(groups.problem, 888, { size: 16 });
  const traditionalY = 24;
  const stagesY = traditionalY + 24 + Math.max(topTitleH, topBadgeH) + 24;
  const problemY = stagesY + stageH + 20;
  const traditionalH = problemY - traditionalY + problemH + 44;
  let content = `<g data-flow-mode="traditional">${kit.card(outerX, traditionalY, outerWidth, traditionalH, { fill: '#ffffff', dash: true })}${kit.label(groups.topTitle, 40, traditionalY + 24, titleWidth, topTitleH, { size: 20, bold: true, align: 'start' })}${kit.card(784, traditionalY + 20, 176, topBadgeH + 16, { fill: '#d0d0d0' })}${kit.label(groups.topBadge, 792, traditionalY + 28, badgeTextWidth, topBadgeH, { size: 16, bold: true })}`;
  const stageStartX = 34;
  groups.traditional.forEach(({ title, detail }, stage) => {
    const x = stageStartX + stage * (stageWidth + stageGap);
    content += `<g data-traditional-stage="${stage}">${kit.card(x, stagesY, stageWidth, stageH, { fill: stage % 2 ? '#f0f0f0' : '#d0d0d0' })}${kit.label(title, x + 12, stagesY + 16, stageWidth - 24, stageTitleH, { size: 18, bold: true })}${kit.label(detail, x + 12, stagesY + 24 + stageTitleH, stageWidth - 24, stageDetailH, { size: 16, muted: true })}</g>`;
    if (stage < 4) {
      const nextX = x + stageWidth + stageGap;
      content += edge(
        `traditional-${stage}-to-${stage + 1}`,
        kit.arrow(
          x + stageWidth + 8,
          stagesY + stageH / 2,
          nextX - 8,
          stagesY + stageH / 2,
        ),
        `traditional-${stage}`,
        `traditional-${stage + 1}`,
      );
    }
  });
  content += `${kit.card(40, problemY, 920, problemH + 24, { fill: '#f5f5f5' })}${kit.label(groups.problem, 56, problemY + 12, 888, problemH, { size: 16 })}</g>`;

  const artifactY = traditionalY + traditionalH + 48;
  const artifactTitleH = kit.height(groups.bottomTitle, titleWidth, {
    size: 20,
    bold: true,
  });
  const artifactBadgeH = kit.height(groups.bottomBadge, badgeTextWidth, {
    size: 16,
    bold: true,
  });
  const artifactWidth = 260;
  const artifactGap = 64;
  const artifactTitleRowH = Math.max(
    ...groups.artifact.map(({ title }) =>
      kit.height(title, artifactWidth - 32, { size: 18, bold: true }),
    ),
  );
  const artifactRows = groups.artifact.map(({ rows }) => {
    const caption = rows.filter(({ mono }) => !mono).map(({ index }) => index);
    const code = rows.filter(({ mono }) => mono).map(({ index }) => index);
    const captionH = caption.length
      ? kit.height(caption, artifactWidth - 32, { size: 16 })
      : 0;
    const codeMetric = rowMetrics(kit, code, artifactWidth - 48, {
      size: 14,
      mono: true,
    });
    return { caption, captionH, code, codeMetric };
  });
  const artifactContentH = Math.max(
    ...artifactRows.map(
      ({ captionH, codeMetric }) =>
        (captionH ? captionH + 10 : 0) + codeMetric.total,
    ),
  );
  const artifactCardH =
    20 + artifactTitleRowH + 16 + artifactContentH + 32 + 20;
  const artifactCardsY =
    artifactY + 24 + Math.max(artifactTitleH, artifactBadgeH) + 24;
  const curveBottom = artifactCardsY + artifactCardH + 64;
  const dataLabelH = groups.dataLabel.length
    ? kit.height(groups.dataLabel, 260, { size: 14 })
    : 0;
  const summaryTitleH = kit.height(groups.summary[0], 888, {
    size: 18,
    bold: true,
  });
  const summaryBodyH = kit.height(groups.summary[1], 888, { size: 16 });
  const summaryY = curveBottom + Math.max(0, dataLabelH) + 20;
  const artifactBottom = summaryY + summaryTitleH + 8 + summaryBodyH + 36;
  content += `<g data-flow-mode="artifact">${kit.card(outerX, artifactY, outerWidth, artifactBottom - artifactY, { fill: '#ffffff', dash: true })}${kit.label(groups.bottomTitle, 40, artifactY + 24, titleWidth, artifactTitleH, { size: 20, bold: true, align: 'start' })}${kit.card(784, artifactY + 20, 176, artifactBadgeH + 16, { fill: '#d0d0d0' })}${kit.label(groups.bottomBadge, 792, artifactY + 28, badgeTextWidth, artifactBadgeH, { size: 16, bold: true })}`;
  const artifactStartX = 46;
  groups.artifact.forEach(({ title }, stage) => {
    const x = artifactStartX + stage * (artifactWidth + artifactGap);
    const row = artifactRows[stage];
    let rowY = artifactCardsY + 20 + artifactTitleRowH + 16;
    content += `<g data-artifact-stage="${stage}">${kit.card(x, artifactCardsY, artifactWidth, artifactCardH, { fill: stage === 1 ? '#d0d0d0' : '#f0f0f0' })}${kit.label(title, x + 16, artifactCardsY + 20, artifactWidth - 32, artifactTitleRowH, { size: 18, bold: true })}`;
    if (row.caption.length) {
      content += kit.label(
        row.caption,
        x + 16,
        rowY,
        artifactWidth - 32,
        row.captionH,
        { size: 16, muted: true },
      );
      rowY += row.captionH + 10;
    }
    content += `${kit.card(x + 16, rowY, artifactWidth - 32, row.codeMetric.total + 24, { fill: '#f5f5f5' })}${codeRows(kit, nodes, row.code, x + 24, rowY + 12, artifactWidth - 48, row.codeMetric, rtl, `artifact-${stage}`)}</g>`;
    if (stage < 2) {
      const nextX = x + artifactWidth + artifactGap;
      content += edge(
        `artifact-${stage}-to-${stage + 1}`,
        kit.arrow(
          x + artifactWidth + 8,
          artifactCardsY + artifactCardH / 2,
          nextX - 8,
          artifactCardsY + artifactCardH / 2,
        ),
        `artifact-${stage}`,
        `artifact-${stage + 1}`,
      );
    }
  });
  const frontendCenter =
    artifactStartX + artifactWidth + artifactGap + artifactWidth / 2;
  const visualizationCenter =
    artifactStartX + 2 * (artifactWidth + artifactGap) + artifactWidth / 2;
  content += edge(
    'frontend-to-visualization-data',
    kit.path(
      `M${frontendCenter} ${artifactCardsY + artifactCardH + 8} C${frontendCenter} ${curveBottom} ${visualizationCenter} ${curveBottom} ${visualizationCenter} ${artifactCardsY + artifactCardH + 8}`,
      { dash: true },
    ),
    'artifact-1',
    'artifact-2',
    ' data-kind="data"',
  );
  if (groups.dataLabel.length)
    content += kit.label(
      groups.dataLabel,
      548,
      artifactCardsY + artifactCardH + 24,
      260,
      dataLabelH,
      { size: 14, muted: true },
    );
  content += `${kit.label(groups.summary[0], 56, summaryY, 888, summaryTitleH, { size: 18, bold: true })}${kit.label(groups.summary[1], 56, summaryY + summaryTitleH + 8, 888, summaryBodyH, { size: 16 })}</g>`;
  return kit.svg(content, artifactBottom + 24);
}

function layoutBootstrapping(kit, nodes, rtl) {
  const evolution = [
    [0, 1],
    [2, 3],
    [4, 5],
    [6, 7],
  ];
  const stageWidth = 200;
  const gap = 48;
  const titleH = Math.max(
    ...evolution.map(([title]) =>
      kit.height(title, 168, { size: 18, bold: true }),
    ),
  );
  const bodyH = Math.max(
    ...evolution.map(([, body]) => kit.height(body, 168, { size: 16 })),
  );
  const stageH = 16 + titleH + 8 + bodyH + 16;
  const stagesY = 24;
  let content = '<g data-evolution-sequence="four-stages">';
  evolution.forEach(([title, body], stage) => {
    const x = 28 + stage * (stageWidth + gap);
    content += `<g data-evolution-stage="${stage}">${kit.card(x, stagesY, stageWidth, stageH, { fill: stage < 2 ? '#f0f0f0' : '#d0d0d0' })}${kit.label(title, x + 16, stagesY + 16, 168, titleH, { size: 18, bold: true })}${kit.label(body, x + 16, stagesY + 24 + titleH, 168, bodyH, { size: 16, muted: true })}</g>`;
    if (stage < 3) {
      const nextX = x + stageWidth + gap;
      content += edge(
        `evolution-${stage}-to-${stage + 1}`,
        kit.arrow(
          x + stageWidth + 8,
          stagesY + stageH / 2,
          nextX - 8,
          stagesY + stageH / 2,
        ),
        `evolution-${stage}`,
        `evolution-${stage + 1}`,
      );
    }
  });
  content += '</g>';

  const comparisonY = stagesY + stageH + 48;
  const comparisonTitleH = Math.max(
    kit.height(8, 416, { size: 18, bold: true }),
    kit.height(10, 416, { size: 18, bold: true }),
  );
  const comparisonBodyH = Math.max(
    kit.height(9, 416, { size: 16 }),
    kit.height(11, 416, { size: 16 }),
  );
  const comparisonH = 20 + comparisonTitleH + 8 + comparisonBodyH + 20;
  for (const [column, pair] of [
    [0, [8, 9]],
    [1, [10, 11]],
  ]) {
    const x = column ? 512 : 24;
    content += `<g data-bootstrap-comparison="${column}">${kit.card(x, comparisonY, 464, comparisonH, { fill: column ? '#d0d0d0' : '#f0f0f0' })}${kit.label(pair[0], x + 24, comparisonY + 20, 416, comparisonTitleH, { size: 18, bold: true })}${kit.label(pair[1], x + 24, comparisonY + 28 + comparisonTitleH, 416, comparisonBodyH, { size: 16, muted: true })}</g>`;
  }

  const agentsY = comparisonY + comparisonH + 48;
  const agentWidth = 404;
  const innerWidth = 356;
  const agentTitleH = Math.max(
    kit.height(12, agentWidth - 32, { size: 20, bold: true }),
    kit.height(26, agentWidth - 32, { size: 20, bold: true }),
  );
  const panelTitleH = Math.max(
    ...[13, 18, 27, 32].map((id) =>
      kit.height(id, innerWidth - 32, { size: 18, bold: true }),
    ),
  );
  const originalSystem = rowMetrics(kit, [14, 15, 16, 17], innerWidth - 32, {
    size: 16,
  });
  const originalCode = rowMetrics(kit, [19, 20, 21, 22], innerWidth - 32, {
    size: 14,
    mono: true,
  });
  const newSystem = rowMetrics(kit, [28, 29, 30, 31], innerWidth - 32, {
    size: 16,
  });
  const newCode = rowMetrics(kit, [33, 34, 35, 36], innerWidth - 32, {
    size: 14,
    mono: true,
  });
  const systemH = Math.max(originalSystem.total, newSystem.total);
  const codeH = Math.max(originalCode.total, newCode.total);
  const summaryTitleH = Math.max(
    kit.height(23, innerWidth, { size: 16 }),
    kit.height(37, innerWidth, { size: 16 }),
  );
  const summaryBodyH = Math.max(
    kit.height(24, innerWidth, { size: 14 }),
    kit.height(38, innerWidth, { size: 14 }),
  );
  const panelH = 16 + panelTitleH + 12;
  const agentH =
    20 +
    agentTitleH +
    20 +
    panelH +
    systemH +
    16 +
    panelH +
    codeH +
    20 +
    summaryTitleH +
    8 +
    summaryBodyH +
    20;
  const agentData = [
    {
      title: 12,
      systemTitle: 13,
      systemIds: [14, 15, 16, 17],
      systemMetric: originalSystem,
      codeTitle: 18,
      codeIds: [19, 20, 21, 22],
      codeMetric: originalCode,
      summary: [23, 24],
    },
    {
      title: 26,
      systemTitle: 27,
      systemIds: [28, 29, 30, 31],
      systemMetric: newSystem,
      codeTitle: 32,
      codeIds: [33, 34, 35, 36],
      codeMetric: newCode,
      summary: [37, 38],
    },
  ];
  agentData.forEach((agent, column) => {
    const x = column ? 572 : 24;
    let cursor = agentsY + 20;
    content += `<g data-agent-version="${column ? 'new' : 'original'}">${kit.card(x, agentsY, agentWidth, agentH, { fill: '#ffffff', dash: true })}${kit.label(agent.title, x + 16, cursor, agentWidth - 32, agentTitleH, { size: 20, bold: true })}`;
    cursor += agentTitleH + 20;
    content += `${kit.card(x + 16, cursor, agentWidth - 32, panelH + systemH, { fill: column ? '#d0d0d0' : '#f0f0f0' })}${kit.label(agent.systemTitle, x + 32, cursor + 16, innerWidth - 32, panelTitleH, { size: 18, bold: true })}`;
    cursor += panelH;
    agent.systemIds.forEach((id, line) => {
      content += kit.label(
        id,
        x + 32,
        cursor,
        innerWidth - 32,
        agent.systemMetric.heights[line],
        {
          size: 16,
          align: 'start',
        },
      );
      cursor += agent.systemMetric.heights[line] + 4;
    });
    cursor = agentsY + 20 + agentTitleH + 20 + panelH + systemH + 16;
    content += `${kit.card(x + 16, cursor, agentWidth - 32, panelH + codeH, { fill: '#f5f5f5' })}${kit.label(agent.codeTitle, x + 32, cursor + 16, innerWidth - 32, panelTitleH, { size: 18, bold: true })}`;
    cursor += panelH;
    content += codeRows(
      kit,
      nodes,
      agent.codeIds,
      x + 32,
      cursor,
      innerWidth - 32,
      agent.codeMetric,
      rtl,
      column ? 'new-agent' : 'original-agent',
    );
    cursor =
      agentsY +
      20 +
      agentTitleH +
      20 +
      panelH +
      systemH +
      16 +
      panelH +
      codeH +
      20;
    content += `${kit.label(agent.summary[0], x + 24, cursor, innerWidth, summaryTitleH, { size: 16 })}${kit.label(agent.summary[1], x + 24, cursor + summaryTitleH + 8, innerWidth, summaryBodyH, { size: 14, muted: true })}</g>`;
  });
  const copyH = kit.height(25, 120, { size: 14, bold: true });
  const arrowY = agentsY + agentH / 2;
  content += `${kit.label(25, 440, arrowY - copyH - 12, 120, copyH, { size: 14, bold: true })}${edge('original-to-new-agent', kit.arrow(436, arrowY, 564, arrowY), 'original-agent', 'new-agent')}`;
  return kit.svg(content, agentsY + agentH + 24);
}

function layoutMetaAgent(kit, nodes, rtl) {
  const requirementTitleH = kit.height(0, 712, { size: 18, bold: true });
  const requirementBodyH = kit.height(1, 712, { size: 16 });
  const requirementH = 20 + requirementTitleH + 8 + requirementBodyH + 20;
  const requirementY = 24;
  let content = `<g data-meta-region="requirement">${kit.card(120, requirementY, 760, requirementH, { fill: '#d0d0d0' })}${kit.label(0, 144, requirementY + 20, 712, requirementTitleH, { size: 18, bold: true })}${kit.label(1, 144, requirementY + 28 + requirementTitleH, 712, requirementBodyH, { size: 16, muted: true })}</g>`;

  const metaY = requirementY + requirementH + 64;
  const metaTitleH = kit.height(2, 904, { size: 20, bold: true });
  const stages = [
    { title: 3, rows: [4, 5, 6, 7, 8, 9] },
    { title: 10, rows: [11, 12, 13, 14, 15] },
    { title: 16, rows: [17, 18, 19, 20, 21, 22] },
    { title: 23, rows: [24, 25, 26, 27, 28, 29] },
  ];
  const stageWidth = 760;
  const stageInner = 712;
  const stageTitleH = Math.max(
    ...stages.map(({ title }) =>
      kit.height(title, stageInner, { size: 18, bold: true }),
    ),
  );
  const stageRows = stages.map(({ rows }) =>
    rows.map((id) => ({
      id,
      height: kit.height(id, stageInner, {
        size: nodes[id].mono ? 14 : 16,
        mono: nodes[id].mono,
        min: 26,
      }),
    })),
  );
  const stageHeights = stageRows.map(
    (rows) =>
      20 +
      stageTitleH +
      12 +
      rows.reduce((sum, row) => sum + row.height, 0) +
      (rows.length - 1) * 4 +
      20,
  );
  const stageGap = 64;
  const stageStartY = metaY + 24 + metaTitleH + 24;
  const stageYs = stageHeights.map((_, index) =>
    stageHeights
      .slice(0, index)
      .reduce((sum, height) => sum + height + stageGap, stageStartY),
  );
  const metaBottom = stageYs[3] + stageHeights[3] + 24;
  content += verticalEdge(
    kit,
    'requirement-to-meta-agent',
    'requirement',
    'meta-agent',
    500,
    requirementY + requirementH,
    metaY,
  );
  content += `<g data-meta-region="meta-agent">${kit.card(24, metaY, 952, metaBottom - metaY, { fill: '#ffffff', dash: true })}${kit.label(2, 48, metaY + 24, 904, metaTitleH, { size: 20, bold: true })}`;
  stages.forEach(({ title, rows }, stage) => {
    const y = stageYs[stage];
    content += `<g data-meta-stage="${stage + 1}">${kit.card(120, y, stageWidth, stageHeights[stage], { fill: stage === 2 ? '#d0d0d0' : '#f0f0f0' })}${kit.label(title, 144, y + 20, stageInner, stageTitleH, { size: 18, bold: true })}`;
    let cursor = y + 32 + stageTitleH;
    rows.forEach((id, row) => {
      const metric = stageRows[stage][row];
      content += kit.label(id, 144, cursor, stageInner, metric.height, {
        size: nodes[id].mono ? 14 : 16,
        mono: nodes[id].mono,
        muted: nodes[id].muted,
        align: 'start',
        direction: nodes[id].mono && rtl ? 'rtl' : undefined,
      });
      cursor += metric.height + 4;
    });
    content += '</g>';
    if (stage < 3)
      content += verticalEdge(
        kit,
        `meta-stage-${stage + 1}-to-${stage + 2}`,
        `meta-stage-${stage + 1}`,
        `meta-stage-${stage + 2}`,
        500,
        y + stageHeights[stage],
        stageYs[stage + 1],
      );
  });
  content += '</g>';

  const generatedY = metaBottom + 64;
  content += verticalEdge(
    kit,
    'meta-agent-to-generated-agent',
    'meta-agent',
    'generated-agent',
    500,
    metaBottom,
    generatedY,
  );
  const generatedTitleH = kit.height(30, 904, { size: 20, bold: true });
  const generatedItems = [
    [31, 32],
    [33, 34],
    [35, 36],
    [37, 38],
  ];
  const itemTitleH = Math.max(
    ...generatedItems.map(([title]) =>
      kit.height(title, 404, { size: 14, mono: true }),
    ),
  );
  const itemBodyH = Math.max(
    ...generatedItems.map(([, body]) => kit.height(body, 404, { size: 16 })),
  );
  const itemH = 16 + itemTitleH + 8 + itemBodyH + 16;
  const generatedH = 24 + generatedTitleH + 20 + itemH * 2 + 16 + 24;
  content += `<g data-meta-region="generated-agent">${kit.card(24, generatedY, 952, generatedH, { fill: '#ffffff', dash: true })}${kit.label(30, 48, generatedY + 24, 904, generatedTitleH, { size: 20, bold: true })}`;
  const itemsY = generatedY + 44 + generatedTitleH;
  generatedItems.forEach(([title, body], item) => {
    const x = item % 2 ? 516 : 48;
    const y = itemsY + Math.floor(item / 2) * (itemH + 8);
    content += `<g data-generated-item="${item}">${kit.card(x, y, 436, itemH, { fill: '#f0f0f0' })}${kit.label(title, x + 16, y + 16, 404, itemTitleH, { size: 14, mono: true })}${kit.label(body, x + 16, y + 24 + itemTitleH, 404, itemBodyH, { size: 16, muted: true })}</g>`;
  });
  content += '</g>';

  const comparisonY = generatedY + generatedH + 48;
  const comparisonTitleH = Math.max(
    kit.height(39, 416, { size: 18, bold: true }),
    kit.height(41, 416, { size: 18, bold: true }),
  );
  const comparisonBodyH = Math.max(
    kit.height(40, 416, { size: 16 }),
    kit.height(42, 416, { size: 16 }),
  );
  const comparisonH = 20 + comparisonTitleH + 8 + comparisonBodyH + 20;
  content += `<g data-meta-comparison="from-scratch">${kit.card(24, comparisonY, 464, comparisonH, { fill: '#f0f0f0' })}${kit.label(39, 48, comparisonY + 20, 416, comparisonTitleH, { size: 18, bold: true })}${kit.label(40, 48, comparisonY + 28 + comparisonTitleH, 416, comparisonBodyH, { size: 16, muted: true })}</g><g data-meta-comparison="from-example">${kit.card(512, comparisonY, 464, comparisonH, { fill: '#d0d0d0' })}${kit.label(41, 536, comparisonY + 20, 416, comparisonTitleH, { size: 18, bold: true })}${kit.label(42, 536, comparisonY + 28 + comparisonTitleH, 416, comparisonBodyH, { size: 16 })}</g>`;
  return kit.svg(content, comparisonY + comparisonH + 24);
}
