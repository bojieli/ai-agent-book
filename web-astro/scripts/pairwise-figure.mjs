// Web-only Figure 7-6 reflow. The localized SVG remains the source for the
// anonymous comparison, Elo formula, leaderboard, ratings, and training note.

import { figureKit } from './chapter3-figure-kit.mjs';

const count = (source, tag) =>
  (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;

function sourceLabels(source) {
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    count(source, 'rect') !== 7 ||
    count(source, 'circle') !== 0 ||
    count(source, 'line') !== 3 ||
    count(source, 'path') !== 0 ||
    count(source, 'marker') !== 2
  )
    throw new Error(
      'Figure 7-6 source structure changed; review its web layout.',
    );

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
  if (labels.length !== 42 || labels.some((label) => /<[^>]+>/.test(label)))
    throw new Error('Figure 7-6 source labels changed; review its web layout.');
  return labels;
}

export function layoutPairwise(source, { rtl = false } = {}) {
  const labels = sourceLabels(source);
  const kit = figureKit(labels, { rtl });
  const outerX = 24;
  const outerY = 24;
  const outerWidth = 952;
  const headingHeight = kit.height(0, 904, { size: 20, bold: true });
  const modelXs = [48, 552];
  const modelWidth = 400;
  const modelInner = modelWidth - 48;
  const modelTitleHeight = Math.max(
    ...[1, 5].map((id) => kit.height(id, modelInner, { size: 18, bold: true })),
  );
  const modelResponses = [
    [2, 3],
    [6, 7],
  ];
  const responseHeight = Math.max(
    ...modelResponses.map((ids) =>
      kit.height(ids, modelInner - 24, { size: 16, min: 28 }),
    ),
  );
  const responsePanelHeight = responseHeight + 24;
  const modelHeight = 18 + modelTitleHeight + 10 + responsePanelHeight + 18;
  const modelsY = outerY + 18 + headingHeight + 16;
  const mergeY = modelsY + modelHeight + 16;
  const verdictLabelHeight = kit.height(8, 352, {
    size: 18,
    bold: true,
    min: 28,
  });
  const verdictX = 300;
  const verdictY = mergeY + 32;
  const verdictWidth = 400;
  const verdictHeight = verdictLabelHeight + 20;
  const outerHeight = verdictY + verdictHeight + 18 - outerY;
  const outerBottom = outerY + outerHeight;

  const models = [1, 5]
    .map((title, model) => {
      const x = modelXs[model];
      const panelY = modelsY + 18 + modelTitleHeight + 10;
      return `<g data-comparison-model="${model === 0 ? 'a' : 'b'}">
        ${kit.card(x, modelsY, modelWidth, modelHeight)}
        ${kit.label(title, x + 24, modelsY + 18, modelInner, modelTitleHeight, { size: 18, bold: true })}
        ${kit.card(x + 16, panelY, modelWidth - 32, responsePanelHeight, { fill: '#f5f5f5' })}
        ${kit.label(modelResponses[model], x + 28, panelY + 12, modelInner - 24, responseHeight, { size: 16, align: 'start', direction: rtl ? 'rtl' : 'ltr' })}
      </g>`;
    })
    .join('');
  const modelBottom = modelsY + modelHeight;
  const comparisonEdges = `
    <g data-pairwise-edge="model-a-to-decision">${kit.path(`M${modelXs[0] + modelWidth / 2} ${modelBottom + 8} L${modelXs[0] + modelWidth / 2} ${mergeY} L500 ${mergeY}`, { arrow: false })}</g>
    <g data-pairwise-edge="model-b-to-decision">${kit.path(`M${modelXs[1] + modelWidth / 2} ${modelBottom + 8} L${modelXs[1] + modelWidth / 2} ${mergeY} L500 ${mergeY}`, { arrow: false })}</g>
    <g data-pairwise-edge="comparison-to-decision">${kit.arrow(500, mergeY, 500, verdictY - 8)}</g>`;

  const eloY = outerBottom + 56;
  const eloTitleHeight = kit.height(9, 904, { size: 18, bold: true });
  const formulaHeight = kit.height(10, 856, {
    size: 14,
    mono: true,
    min: 26,
  });
  const formulaPanelHeight = formulaHeight + 20;
  const eloHeight = 18 + eloTitleHeight + 10 + formulaPanelHeight + 18;
  const eloBottom = eloY + eloHeight;

  const leaderboardY = eloBottom + 56;
  const leaderboardHeadingHeight = kit.height(11, 904, {
    size: 20,
    bold: true,
  });
  const columnWidths = [90, 310, 130, 374];
  const columnXs = columnWidths.reduce(
    (xs, width, index) =>
      index === columnWidths.length - 1
        ? xs
        : [...xs, xs[xs.length - 1] + width],
    [48],
  );
  const cell = (id, column, y, height, { bold = false, muted = false } = {}) =>
    kit.label(
      id,
      columnXs[column] + 8,
      y + 10,
      columnWidths[column] - 16,
      height - 20,
      {
        size: 16,
        bold,
        muted,
      },
    );
  const tableHeaderHeight =
    20 +
    Math.max(
      ...[12, 13, 14, 15].map((id, column) =>
        kit.height(id, columnWidths[column] - 16, {
          size: 16,
          bold: true,
          min: 28,
        }),
      ),
    );
  const rows = Array.from({ length: 6 }, (_, row) =>
    Array.from({ length: 4 }, (_, column) => 16 + row * 4 + column),
  );
  const rowHeights = rows.map(
    (ids) =>
      20 +
      Math.max(
        ...ids.map((id, column) =>
          kit.height(id, columnWidths[column] - 16, {
            size: 16,
            bold: column === 0 || column === 2,
            min: 28,
          }),
        ),
      ),
  );
  const tableY = leaderboardY + 18 + leaderboardHeadingHeight + 14;
  const rowsHeight =
    rowHeights.reduce((sum, height) => sum + height, 0) +
    (rowHeights.length - 1) * 2;
  const leaderboardHeight =
    18 +
    leaderboardHeadingHeight +
    14 +
    tableHeaderHeight +
    2 +
    rowsHeight +
    18;
  const leaderboardBottom = leaderboardY + leaderboardHeight;
  let rowY = tableY + tableHeaderHeight + 2;
  let leaderboardRows = '';
  rows.forEach((ids, row) => {
    const height = rowHeights[row];
    const fill = row === 0 ? '#d0d0d0' : row === 1 ? '#f0f0f0' : '#ffffff';
    leaderboardRows += `<g data-leaderboard-row="${row + 1}">
      <rect x="48" y="${rowY}" width="904" height="${height}" rx="5" fill="${fill}"/>
      ${ids.map((id, column) => cell(id, column, rowY, height, { bold: column === 0 || column === 2, muted: column === 3 })).join('')}
    </g>`;
    rowY += height;
    if (row === 1)
      leaderboardRows += `<g data-ranking-divider="true">${kit.path(`M48 ${rowY + 1} L952 ${rowY + 1}`, { arrow: false, dash: true })}</g>`;
    rowY += 2;
  });

  const trainingY = leaderboardBottom + 40;
  const trainingWidth = 840;
  const trainingInner = trainingWidth - 48;
  const trainingTitleHeight = kit.height(40, trainingInner, {
    size: 18,
    bold: true,
  });
  const trainingCaptionHeight = kit.height(41, trainingInner, {
    size: 14,
    min: 25,
  });
  const trainingHeight =
    18 + trainingTitleHeight + 8 + trainingCaptionHeight + 18;
  const totalHeight = trainingY + trainingHeight + 24;

  const content = `
    <g data-anonymous-comparison="true">
      ${kit.card(outerX, outerY, outerWidth, outerHeight, { fill: '#ffffff', dash: true })}
      ${kit.label(0, 48, outerY + 18, 904, headingHeight, { size: 20, bold: true })}
      ${models}
      ${kit.label(4, 456, modelsY + modelHeight / 2 - 18, 88, 36, { size: 20, bold: true, muted: true })}
      ${comparisonEdges}
      ${kit.card(verdictX, verdictY, verdictWidth, verdictHeight, { fill: '#d0d0d0' })}
      ${kit.label(8, verdictX + 24, verdictY + 10, verdictWidth - 48, verdictLabelHeight, { size: 18, bold: true })}
    </g>
    <g data-pairwise-edge="decision-to-elo">${kit.arrow(500, outerBottom + 8, 500, eloY - 8)}</g>
    <g data-elo-update="true">
      ${kit.card(24, eloY, 952, eloHeight, { fill: '#f5f5f5' })}
      ${kit.label(9, 48, eloY + 18, 904, eloTitleHeight, { size: 18, bold: true })}
      ${kit.card(48, eloY + 18 + eloTitleHeight + 10, 904, formulaPanelHeight, { fill: '#ffffff' })}
      ${kit.label(10, 72, eloY + 18 + eloTitleHeight + 20, 856, formulaHeight, { size: 14, mono: true, direction: 'ltr' })}
    </g>
    <g data-pairwise-edge="elo-to-leaderboard">${kit.arrow(500, eloBottom + 8, 500, leaderboardY - 8)}</g>
    <g data-live-leaderboard="true">
      ${kit.card(24, leaderboardY, 952, leaderboardHeight, { fill: '#ffffff' })}
      ${kit.label(11, 48, leaderboardY + 18, 904, leaderboardHeadingHeight, { size: 20, bold: true })}
      <rect x="48" y="${tableY}" width="904" height="${tableHeaderHeight}" rx="5" fill="#f0f0f0" stroke="#999999" stroke-width="1.5"/>
      ${[12, 13, 14, 15].map((id, column) => cell(id, column, tableY, tableHeaderHeight, { bold: true })).join('')}
      ${leaderboardRows}
    </g>
    <g data-pairwise-training="true">
      ${kit.card(80, trainingY, trainingWidth, trainingHeight, { fill: '#d0d0d0' })}
      ${kit.label(40, 104, trainingY + 18, trainingInner, trainingTitleHeight, { size: 18, bold: true })}
      ${kit.label(41, 104, trainingY + 18 + trainingTitleHeight + 8, trainingInner, trainingCaptionHeight, { size: 14, muted: true })}
    </g>`;
  return kit.svg(content, totalHeight);
}
