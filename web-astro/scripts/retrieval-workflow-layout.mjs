import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

// Group translated line fragments by their source card, never by English wording.
function cardLabels(source) {
  const groups = [];
  let card = -1,
    index = 0;
  for (const match of source.matchAll(
    /<rect\b[^>]*>|<text\b[^>]*>[\s\S]*?<\/text>/g,
  )) {
    if (match[0].startsWith('<rect')) groups[++card] = [];
    else groups[card].push(index++);
  }
  return groups;
}

export function layoutRetrievalWorkflow(source, figure, options = {}) {
  const labels = extractLabels(
    source,
    `3-${figure}`,
    { 13: [18, 19], 14: [19, 20, 21], 15: [23] }[figure] || [],
  );
  const { label, height, card, arrow, path, svg } = figureKit(labels, options);
  const groups = cardLabels(source);
  const title = { size: 18, bold: true };
  const section = { size: 20, bold: true };
  const body = { size: 16 };
  const note = { size: 14, muted: true };
  const mono = { size: 14, mono: true };
  const box = (ids, x, y, w, h, style = title) =>
    card(x, y, w, h) +
    label(
      ids,
      x + 16,
      y + (h - height(ids, w - 32, style)) / 2,
      w - 32,
      height(ids, w - 32, style),
      style,
    );

  if (figure === 13) {
    if (groups.length !== 14)
      throw new Error('Figure 3-13 card structure changed');
    const headingH = height(groups[0], 500, section) + 8;
    const rowY = 24 + 20 + headingH;
    const rowH =
      Math.max(
        ...[1, 2, 4, 5].map((i) => height(groups[i], i < 3 ? 188 : 126, title)),
      ) + 32;
    const observationY = rowY + rowH + 48;
    const observationH = height(groups[3][0], 208, title) + 32;
    const repeatY = observationY + observationH + 16;
    const repeatH = height(groups[3].slice(1), 500, note);
    const agentBottom = repeatY + repeatH + 20;
    const center = rowY + rowH / 2;
    let out = card(230, 24, 540, agentBottom - 24, { fill: '#ffffff' });
    out += label(groups[0], 250, 44, 500, headingH, section);
    out +=
      box(groups[1], 250, rowY, 220, rowH) +
      box(groups[2], 530, rowY, 220, rowH);
    out += box(groups[3][0], 380, observationY, 240, observationH);
    out += label(groups[3].slice(1), 250, repeatY, 500, repeatH, note);
    out +=
      box(groups[4], 24, rowY, 158, rowH) +
      box(groups[5], 818, rowY, 158, rowH);
    out +=
      arrow(190, center, 222, center) +
      arrow(778, center, 810, center) +
      arrow(478, center, 522, center);
    out += path(
      `M640 ${rowY + rowH + 8} V${observationY + observationH / 2} H628`,
    );
    out += path(
      `M372 ${observationY + observationH / 2} H360 V${rowY + rowH + 8}`,
    );

    const toolsY = agentBottom + 56;
    const toolsHeadingH = height(groups[6], 912, section) + 8;
    const toolsRowY = toolsY + 16 + toolsHeadingH;
    const toolsRowH =
      Math.max(...[7, 8, 9].map((i) => height(groups[i], 256, mono))) + 32;
    const toolsBottom = toolsRowY + toolsRowH + 20;
    out += card(24, toolsY, 952, toolsBottom - toolsY, {
      fill: '#ffffff',
      dash: true,
    });
    out += label(groups[6], 44, toolsY + 16, 912, toolsHeadingH, section);
    [7, 8, 9].forEach((g, i) => {
      out += box(groups[g], 44 + i * 312, toolsRowY, 288, toolsRowH, mono);
    });
    out +=
      arrow(480, agentBottom + 8, 480, toolsY - 8) +
      arrow(520, toolsY - 8, 520, agentBottom + 8);

    const backendY = toolsBottom + 56;
    const backendHeadingH = height(groups[10], 912, section) + 8;
    const backendRowY = backendY + 16 + backendHeadingH;
    const backendHeights = [11, 12, 13].map(
      (g) =>
        height(groups[g][0], 256, mono) +
        8 +
        height(groups[g].slice(1), 256, body),
    );
    const backendRowH = Math.max(...backendHeights) + 32;
    const bottom = backendRowY + backendRowH + 20;
    out += card(24, backendY, 952, bottom - backendY, {
      fill: '#ffffff',
      dash: true,
    });
    out += label(groups[10], 44, backendY + 16, 912, backendHeadingH, section);
    [11, 12, 13].forEach((g, i) => {
      const x = 44 + i * 312,
        h = height(groups[g][0], 256, mono);
      out += card(x, backendRowY, 288, backendRowH);
      out += label(groups[g][0], x + 16, backendRowY + 16, 256, h, mono);
      out += label(
        groups[g].slice(1),
        x + 16,
        backendRowY + 24 + h,
        256,
        backendRowH - h - 40,
        body,
      );
    });
    out +=
      arrow(188, toolsRowY + toolsRowH + 8, 188, backendY - 8) +
      arrow(500, toolsBottom + 8, 500, backendY - 8);
    return svg(out, bottom + 24);
  }

  if (figure === 14) {
    if (groups.length !== 9 || labels[10] !== '→')
      throw new Error('Figure 3-14 card structure changed');
    const panelWidth = 440,
      innerWidth = 400;
    const headingH =
      Math.max(height(0, innerWidth, title), height(5, innerWidth, title)) + 8;
    const prefixH = height(6, 368, note) + 32;
    const quoteH =
      Math.max(height([1, 2], 368, body), height([7, 8], 368, body)) + 32;
    const quoteY = 24 + 20 + headingH + prefixH + 12;
    const leftQuoteY = 44 + headingH;
    const resultY = quoteY + quoteH + 16;
    const leftResultY = leftQuoteY + quoteH + 16;
    const leftTailH =
      height(3, innerWidth, body) + 12 + height(4, innerWidth, body);
    const rightTailH = height(9, innerWidth, body);
    const panelH =
      Math.max(leftResultY + leftTailH, resultY + rightTailH) + 20 - 24;
    let out =
      card(24, 24, panelWidth, panelH, { fill: '#ffffff' }) +
      card(536, 24, panelWidth, panelH, { fill: '#ffffff' });
    out +=
      label(0, 44, 44, 400, headingH, title) +
      label(5, 556, 44, 400, headingH, title);
    // Matching quote typography; the new context has its own block above the right quote.
    out += card(556, 44 + headingH, 400, prefixH, { fill: '#d0d0d0' });
    out += label(6, 572, 60 + headingH, 368, prefixH - 32, note);
    out +=
      card(44, leftQuoteY, 400, quoteH) +
      label([1, 2], 60, leftQuoteY + 16, 368, quoteH - 32, {
        ...body,
        align: 'start',
      });
    out +=
      card(556, quoteY, 400, quoteH) +
      label([7, 8], 572, quoteY + 16, 368, quoteH - 32, {
        ...body,
        align: 'start',
      });
    out += label(3, 44, leftResultY, 400, height(3, 400, body), body);
    out += label(
      4,
      44,
      leftResultY + height(3, 400, body) + 12,
      400,
      height(4, 400, body),
      body,
    );
    out += label(9, 556, resultY, 400, height(9, 400, body), body);
    out += path(
      `M472 ${leftQuoteY + quoteH / 2} H500 V${quoteY + quoteH / 2} H528`,
    );
    const headingY = 24 + panelH + 32;
    const indexHeadingH = height(11, 928, section);
    out += label(11, 36, headingY, 928, indexHeadingH, section);
    const rowY = headingY + indexHeadingH + 20;
    const stages = [groups[5], groups[6], groups[7], groups[8].slice(0, -1)];
    const rowH = Math.max(...stages.map((ids) => height(ids, 170, title))) + 32;
    stages.forEach((ids, i) => {
      const x = 36 + i * 242;
      out += box(ids, x, rowY, 202, rowH);
      if (i < 3)
        out += arrow(x + 210, rowY + rowH / 2, x + 234, rowY + rowH / 2);
    });
    const footer = groups[8].at(-1),
      footerY = rowY + rowH + 24,
      footerH = height(footer, 928, note);
    out += label(footer, 36, footerY, 928, footerH, note);
    return svg(out, footerY + footerH + 24);
  }

  const columnX = [44, 364, 684],
    columnWidth = 272,
    textWidth = 240;
  const firstX = [44, 340, 636],
    firstWidths = [248, 248, 320];
  const panelTitleH =
    Math.max(height(0, 912, section), height(11, 912, section)) + 8;
  const firstRowY = 24 + 20 + panelTitleH;
  const firstTitles = [1, 3, 5],
    firstBodies = [[2], [4], [6, 7]];
  const firstTitleH =
    Math.max(
      ...firstTitles.map((id, i) => height(id, firstWidths[i] - 32, title)),
    ) + 8;
  const firstBodyH = Math.max(
    ...firstBodies.map((ids, i) =>
      height(ids, firstWidths[i] - 32, i === 2 ? mono : body),
    ),
  );
  const firstRowH = 32 + firstTitleH + firstBodyH;
  const schemaY = firstRowY + firstRowH + 20;
  const schemaTitleH = height(8, 880, title);
  const schemaBodyH = height(9, 880, body),
    schemaExampleH = height(10, 880, body);
  const schemaH = 32 + schemaTitleH + 8 + schemaBodyH + 8 + schemaExampleH;
  const firstBottom = schemaY + schemaH + 20;
  let out = card(24, 24, 952, firstBottom - 24, { fill: '#ffffff' });
  out += label(0, 44, 44, 912, panelTitleH, section);
  firstX.forEach((x, i) => {
    out += card(x, firstRowY, firstWidths[i], firstRowH);
    out += label(
      firstTitles[i],
      x + 16,
      firstRowY + 16,
      firstWidths[i] - 32,
      firstTitleH,
      title,
    );
    out += label(
      firstBodies[i],
      x + 16,
      firstRowY + 16 + firstTitleH,
      firstWidths[i] - 32,
      firstBodyH,
      i === 2 ? { ...mono, align: 'start' } : body,
    );
    if (i < 2)
      out += arrow(
        x + firstWidths[i] + 8,
        firstRowY + firstRowH / 2,
        firstX[i + 1] - 8,
        firstRowY + firstRowH / 2,
      );
  });
  out += card(44, schemaY, 912, schemaH);
  out += label(8, 60, schemaY + 16, 880, schemaTitleH, title);
  out += label(9, 60, schemaY + 24 + schemaTitleH, 880, schemaBodyH, body);
  out += label(
    10,
    60,
    schemaY + 32 + schemaTitleH + schemaBodyH,
    880,
    schemaExampleH,
    body,
  );
  const secondY = firstBottom + 24,
    secondRowY = secondY + 20 + panelTitleH;
  const titles = [12, 15, 18],
    bodies = [
      [13, 14],
      [16, 17],
      [19, 20],
    ];
  const secondTitleH =
    Math.max(...titles.map((i) => height(i, textWidth, title))) + 8;
  const secondBodyH = Math.max(
    ...bodies.map((ids) => height(ids, textWidth, body)),
  );
  const secondRowH = 32 + secondTitleH + secondBodyH;
  const appY = secondRowY + secondRowH + 48;
  const appTitleH = height(21, 880, title),
    appBodyH = height(22, 880, body);
  const appH = 32 + appTitleH + 8 + appBodyH,
    bottom = appY + appH + 20;
  out += card(24, secondY, 952, bottom - secondY, { fill: '#ffffff' });
  out += label(11, 44, secondY + 20, 912, panelTitleH, section);
  columnX.forEach((x, i) => {
    out += card(x, secondRowY, columnWidth, secondRowH);
    out += label(
      titles[i],
      x + 16,
      secondRowY + 16,
      textWidth,
      secondTitleH,
      title,
    );
    out += label(
      bodies[i],
      x + 16,
      secondRowY + 16 + secondTitleH,
      textWidth,
      secondBodyH,
      body,
    );
    if (i < 2)
      out += arrow(
        x + columnWidth + 8,
        secondRowY + secondRowH / 2,
        columnX[i + 1] - 8,
        secondRowY + secondRowH / 2,
      );
  });
  out += arrow(820, secondRowY + secondRowH + 8, 820, appY - 8);
  out += card(44, appY, 912, appH, { fill: '#d0d0d0' });
  out += label(21, 60, appY + 16, 880, appTitleH, title);
  out += label(22, 60, appY + 24 + appTitleH, 880, appBodyH, body);
  return svg(out, bottom + 24);
}
