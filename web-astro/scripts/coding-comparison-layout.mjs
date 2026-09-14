// Web-only reflows for the Chapter 5 search and editing comparisons. The
// localized SVGs remain the source of every visible label.

import { figureKit } from './chapter3-figure-kit.mjs';

const specifications = {
  3: { labels: [33], rect: 16, line: 0, path: 0, marker: 2 },
  4: {
    labels: [52, 61, 65, 67, 68],
    rect: 20,
    line: 1,
    path: 0,
    marker: 2,
  },
};

const count = (source, tag) =>
  (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;

function sourceLabels(source, figure, nodes) {
  const specification = specifications[figure];
  if (!specification)
    throw new Error(`Unsupported coding comparison figure: ${figure}`);
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !['rect', 'line', 'path', 'marker'].every(
      (tag) => count(source, tag) === specification[tag],
    )
  )
    throw new Error(
      `Figure 5-${figure} source structure changed; review its web layout.`,
    );
  const labels = nodes.map(({ content }) =>
    content
      .replace(/<tspan\b[^>]*>/g, '')
      .replace(/<\/tspan>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  );
  if (
    !specification.labels.includes(labels.length) ||
    labels.some((text) => /<[^>]+>/.test(text))
  )
    throw new Error(
      `Figure 5-${figure} source labels changed; review its web layout.`,
    );
  return labels;
}

function textNodes(source) {
  return [
    ...source.matchAll(/<text\b([^>]*?)(?:\/>|>([\s\S]*?)<\/text>)/g),
  ].map(([, attributes, pairedContent], index) => {
    const content = pairedContent ?? '';
    const coordinate = (name) =>
      Number(attributes.match(new RegExp(`\\b${name}="(-?[\\d.]+)`))?.[1]);
    let y = coordinate('y');
    if (y === 0) {
      const firstTspanY = content.match(/<tspan\b[^>]*\bdy="(-?[\d.]+)"/)?.[1];
      if (firstTspanY) y = Number(firstTspanY);
    }
    return {
      index,
      x: coordinate('x'),
      y,
      muted: /\bfill="#666666"/.test(attributes),
      content,
    };
  });
}

export function layoutCodingComparison(source, figure, { rtl = false } = {}) {
  const nodes = textNodes(source);
  const labels = sourceLabels(source, figure, nodes);
  const kit = figureKit(labels, { rtl });
  return figure === 3
    ? layoutSearchComparison(kit, rtl)
    : layoutEditingComparison(kit, nodes, labels.length, rtl);
}

function layoutSearchComparison(kit, rtl) {
  const methods = [
    {
      title: 0,
      queryTitle: 1,
      query: 2,
      resultTitle: 3,
      results: [4, 5, 6],
      caption: 7,
    },
    {
      title: 8,
      queryTitle: 9,
      query: 10,
      resultTitle: 11,
      results: [12, 13, 14],
      caption: 15,
    },
    {
      title: 16,
      queryTitle: 17,
      query: 18,
      resultTitle: 19,
      results: [20, 21, 22],
      caption: 23,
    },
    {
      title: 24,
      queryTitle: 25,
      query: 26,
      resultTitle: 27,
      results: [28, 29, 30, 31],
      caption: 32,
    },
  ];
  const cardWidth = 464;
  const innerWidth = 416;
  const codeWidth = 400;
  const titleHeight = Math.max(
    ...methods.map(({ title }) =>
      kit.height(title, innerWidth, { size: 20, bold: true }),
    ),
  );
  const fieldTitleHeight = Math.max(
    ...methods.flatMap(({ queryTitle, resultTitle }) =>
      [queryTitle, resultTitle].map((id) =>
        kit.height(id, innerWidth, { size: 18, bold: true }),
      ),
    ),
  );
  const queryHeight = Math.max(
    ...methods.map(({ query }) =>
      kit.height(query, codeWidth, { size: 14, mono: true, min: 26 }),
    ),
  );
  const resultHeights = methods.map(({ results }) =>
    results.map((id) =>
      kit.height(id, codeWidth, { size: 14, mono: true, min: 26 }),
    ),
  );
  const resultHeight = Math.max(
    ...resultHeights.map(
      (heights) =>
        heights.reduce((sum, value) => sum + value, 0) +
        (heights.length - 1) * 4,
    ),
  );
  const captionHeight = Math.max(
    ...methods.map(({ caption }) =>
      kit.height(caption, innerWidth, { size: 16, min: 28 }),
    ),
  );
  const headerHeight = titleHeight + 32;
  const queryPanelHeight = queryHeight + 24;
  const resultPanelHeight = resultHeight + 24;
  const cardHeight =
    headerHeight +
    20 +
    fieldTitleHeight +
    8 +
    queryPanelHeight +
    18 +
    fieldTitleHeight +
    8 +
    resultPanelHeight +
    18 +
    captionHeight +
    18;
  const rowGap = 24;

  const content = methods
    .map((method, methodIndex) => {
      const column = methodIndex % 2;
      const row = Math.floor(methodIndex / 2);
      const x = 24 + column * (cardWidth + 24);
      const y = 24 + row * (cardHeight + rowGap);
      let cursor = y + headerHeight + 20;
      let rendered = `<g data-search-method="${methodIndex}">
        ${kit.card(x, y, cardWidth, cardHeight, { fill: '#ffffff' })}
        ${kit.card(x, y, cardWidth, headerHeight, { fill: methodIndex === 0 || methodIndex === 3 ? '#d0d0d0' : '#f0f0f0' })}
        ${kit.label(method.title, x + 24, y + 16, innerWidth, titleHeight, { size: 20, bold: true })}`;
      rendered += kit.label(
        method.queryTitle,
        x + 24,
        cursor,
        innerWidth,
        fieldTitleHeight,
        { size: 18, bold: true, align: 'start' },
      );
      cursor += fieldTitleHeight + 8;
      rendered += `<g data-code-kind="query">${kit.card(x + 16, cursor, cardWidth - 32, queryPanelHeight, { fill: '#f5f5f5' })}${kit.label(method.query, x + 32, cursor + 12, codeWidth, queryHeight, { size: 14, mono: true, align: 'start', direction: rtl ? 'rtl' : 'ltr' })}</g>`;
      cursor += queryPanelHeight + 18;
      rendered += kit.label(
        method.resultTitle,
        x + 24,
        cursor,
        innerWidth,
        fieldTitleHeight,
        { size: 18, bold: true, align: 'start' },
      );
      cursor += fieldTitleHeight + 8;
      rendered += `<g data-code-kind="result">${kit.card(x + 16, cursor, cardWidth - 32, resultPanelHeight, { fill: '#f5f5f5' })}`;
      let lineY = cursor + 12;
      method.results.forEach((id, line) => {
        rendered += `<g data-search-code-line="${methodIndex}:${line}">${kit.label(id, x + 32, lineY, codeWidth, resultHeights[methodIndex][line], { size: 14, mono: true, align: 'start', direction: rtl ? 'rtl' : 'ltr' })}</g>`;
        lineY += resultHeights[methodIndex][line] + 4;
      });
      rendered += '</g>';
      cursor += resultPanelHeight + 18;
      rendered += `${kit.label(method.caption, x + 24, cursor, innerWidth, captionHeight, { size: 16, muted: true, align: 'start' })}</g>`;
      return rendered;
    })
    .join('');

  return kit.svg(content, 24 + cardHeight * 2 + rowGap + 24);
}

function editingGroups(nodes, labelCount) {
  if (nodes.length !== labelCount)
    throw new Error(
      'Figure 5-4 text extraction changed; review its web layout.',
    );
  const adoptionPosition = nodes.findIndex(({ y }) => y >= 330);
  if (adoptionPosition < 0)
    throw new Error(
      'Figure 5-4 adoption section changed; review its web layout.',
    );
  const comparison = nodes.slice(0, adoptionPosition);
  const headingPositions = comparison
    .map(({ y }, position) => (y < 100 ? position : -1))
    .filter((position) => position >= 0);
  if (headingPositions.length !== 5)
    throw new Error(
      'Figure 5-4 method headings changed; review its web layout.',
    );
  const methods = headingPositions.map((start, method) => {
    const end = headingPositions[method + 1] ?? comparison.length;
    const group = comparison.slice(start, end);
    const detailStart = group.findIndex(
      ({ y }, position) => position > 0 && y >= 210,
    );
    if (detailStart < 0)
      throw new Error(
        'Figure 5-4 method details changed; review its web layout.',
      );
    return {
      title: group[0].index,
      code: group.slice(1, detailStart),
      details: group.slice(detailStart),
    };
  });
  const expectedCodeCounts = [6, 5, [4, 5], 5, 5];
  if (
    methods.some(({ code, details }, method) => {
      const allowed = Array.isArray(expectedCodeCounts[method])
        ? expectedCodeCounts[method]
        : [expectedCodeCounts[method]];
      return (
        !allowed.includes(code.length) ||
        details.length < 2 ||
        details.length > 5
      );
    })
  )
    throw new Error('Figure 5-4 method rows changed; review its web layout.');

  const adoptionNodes = nodes.slice(adoptionPosition);
  const adoption = { title: adoptionNodes[0].index, rows: [] };
  for (const node of adoptionNodes.slice(1)) {
    if (Math.abs(node.x - 240) < 2)
      adoption.rows.push({ label: node.index, values: [] });
    else if (adoption.rows.length) adoption.rows.at(-1).values.push(node.index);
    else
      throw new Error(
        'Figure 5-4 adoption rows changed; review its web layout.',
      );
  }
  if (
    adoption.rows.length !== 5 ||
    adoption.rows.some(({ values }) => values.length < 1 || values.length > 2)
  )
    throw new Error('Figure 5-4 adoption rows changed; review its web layout.');
  return { methods, adoption };
}

function layoutEditingComparison(kit, nodes, labelCount, rtl) {
  const { methods, adoption } = editingGroups(nodes, labelCount);
  const cardWidth = 464;
  const innerWidth = 416;
  const codeWidth = 400;
  const titleHeight = Math.max(
    ...methods.map(({ title }) =>
      kit.height(title, innerWidth, { size: 20, bold: true }),
    ),
  );
  const codeHeights = methods.map(({ code }) =>
    code.map(({ index }) =>
      kit.height(index, codeWidth, { size: 14, mono: true, min: 26 }),
    ),
  );
  const codeContentHeight = Math.max(
    ...codeHeights.map(
      (heights) =>
        heights.reduce((sum, value) => sum + value, 0) +
        (heights.length - 1) * 4,
    ),
  );
  const detailGroups = methods.map(({ details }) => {
    const groups = [];
    for (const node of details) {
      if (!groups.length || groups.at(-1).muted !== node.muted)
        groups.push({ ids: [], muted: node.muted });
      groups.at(-1).ids.push(node.index);
    }
    return groups;
  });
  const detailHeights = detailGroups.map((groups) =>
    groups.map(({ ids }) => kit.height(ids, innerWidth, { size: 16, min: 28 })),
  );
  const detailContentHeight = Math.max(
    ...detailHeights.map(
      (heights) =>
        heights.reduce((sum, value) => sum + value, 0) +
        (heights.length - 1) * 4,
    ),
  );
  const headerHeight = titleHeight + 32;
  const codePanelHeight = codeContentHeight + 24;
  const cardHeight =
    headerHeight + 16 + codePanelHeight + 16 + detailContentHeight + 20;
  const cardGap = 24;
  let content = '';
  methods.forEach((method, methodIndex) => {
    const row = Math.floor(methodIndex / 2);
    const column = methodIndex % 2;
    const x = methodIndex === 4 ? 268 : 24 + column * (cardWidth + 24);
    const y = 24 + row * (cardHeight + cardGap);
    const codeY = y + headerHeight + 16;
    content += `<g data-editing-method="${methodIndex}">
      ${kit.card(x, y, cardWidth, cardHeight, { fill: '#ffffff' })}
      ${kit.card(x, y, cardWidth, headerHeight, { fill: methodIndex === 0 || methodIndex === 4 ? '#d0d0d0' : '#f0f0f0' })}
      ${kit.label(method.title, x + 24, y + 16, innerWidth, titleHeight, { size: 20, bold: true })}
      ${kit.card(x + 16, codeY, cardWidth - 32, codePanelHeight, { fill: '#f5f5f5' })}`;
    let cursor = codeY + 12;
    method.code.forEach((node, line) => {
      const rawText = node.content.replace(/<\/?tspan\b[^>]*>/g, '');
      const indent = /^\s{2,}/.test(rawText) ? 20 : 0;
      content += `<g data-method-code="${methodIndex}:${line}">${kit.label(node.index, x + 32 + indent, cursor, codeWidth - indent, codeHeights[methodIndex][line], { size: 14, mono: true, align: 'start', direction: rtl ? 'rtl' : 'ltr' })}</g>`;
      cursor += codeHeights[methodIndex][line] + 4;
    });
    cursor = codeY + codePanelHeight + 16;
    detailGroups[methodIndex].forEach((group, line) => {
      content += `<g data-method-detail="${methodIndex}:${line}">${kit.label(group.ids, x + 24, cursor, innerWidth, detailHeights[methodIndex][line], { size: 16, muted: group.muted, align: 'start' })}</g>`;
      cursor += detailHeights[methodIndex][line] + 4;
    });
    content += '</g>';
  });

  const methodsBottom = 24 + cardHeight * 3 + cardGap * 2;
  const sectionY = methodsBottom + 48;
  const sectionTitleHeight = kit.height(adoption.title, 952, {
    size: 20,
    bold: true,
  });
  content += `<g data-adoption-section="ranked-comparison">
    ${kit.label(adoption.title, 24, sectionY, 952, sectionTitleHeight, { size: 20, bold: true })}`;
  let rowY = sectionY + sectionTitleHeight + 24;
  const barWidths = [600, 470, 390, 320, 250];
  adoption.rows.forEach(({ label, values }, row) => {
    const labelHeight = kit.height(label, 260, { size: 18, bold: true });
    const valueHeight = kit.height(values, barWidths[row] - 32, {
      size: 16,
    });
    const rowHeight = Math.max(labelHeight, valueHeight) + 24;
    content += `<g data-adoption-rank="${row + 1}" data-bar-width="${barWidths[row]}">
      ${kit.label(label, 24, rowY + 12, 260, labelHeight, { size: 18, bold: true, align: 'end' })}
      ${kit.card(308, rowY, barWidths[row], rowHeight, { fill: row === 0 ? '#d0d0d0' : row < 3 ? '#f0f0f0' : '#f5f5f5' })}
      ${kit.label(values, 324, rowY + 12, barWidths[row] - 32, valueHeight, { size: 16, align: 'start' })}
    </g>`;
    rowY += rowHeight + 12;
  });
  content += '</g>';
  return kit.svg(content, rowY + 12);
}
