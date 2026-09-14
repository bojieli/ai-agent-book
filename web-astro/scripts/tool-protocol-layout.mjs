import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';

// Reflow the source sequence and two-stage search without changing their labels.
export function layoutToolProtocol(source, figure, { rtl = false } = {}) {
  if (![1, 2].includes(figure))
    throw new Error(`Unsupported tool protocol figure: ${figure}`);
  const labels = extractLabels(source, `4-${figure}`, [figure === 1 ? 18 : 26]);
  if ((source.match(/<line\b/g) || []).length !== (figure === 1 ? 8 : 3))
    throw new Error(`Figure 4-${figure} source relationships changed`);
  const k = figureKit(labels, { rtl });
  return figure === 1 ? sequence(k) : discovery(k, rtl);
}

function sequence(k) {
  const headerH =
    Math.max(
      k.height(0, 228, { size: 20, bold: true }),
      k.height(1, 228, { size: 20, bold: true }),
    ) + 32;
  let content = [0, 1]
    .map((id, i) => {
      const x = i ? 718 : 158;
      return (
        k.card(x, 24, 260, headerH, { fill: '#d0d0d0' }) +
        k.label(id, x + 16, 40, 228, headerH - 32, { size: 20, bold: true })
      );
    })
    .join('');
  let y = 24 + headerH + 32;
  const stages = [
    { request: 2, code: 3, response: 4, details: [5], phase: 15 },
    { request: 6, code: 7, response: 8, details: [9, 10], phase: 16 },
    { request: 11, code: 12, response: 13, details: [14], phase: 17 },
  ];
  const left = 288,
    right = 848,
    textX = 312,
    textW = 512;
  for (const [index, stage] of stages.entries()) {
    const start = y;
    const requestH = k.height(stage.request, textW, { size: 18, bold: true });
    content +=
      `<g data-protocol-stage="${index}">` +
      k.label(stage.request, textX, y, textW, requestH, {
        size: 18,
        bold: true,
      });
    y += requestH + 12;
    content += `<g data-direction="request">${k.arrow(left + 8, y, right - 8, y)}</g>`;
    y += 12;
    const codeH = k.height(stage.code, textW, { size: 14, mono: true });
    content += k.label(stage.code, textX, y, textW, codeH, {
      size: 14,
      mono: true,
    });
    y += codeH + 28;
    const responseH = k.height(stage.response, textW, { size: 18, bold: true });
    content += k.label(stage.response, textX, y, textW, responseH, {
      size: 18,
      bold: true,
    });
    y += responseH + 12;
    content += `<g data-direction="response">${k.arrow(right - 8, y, left + 8, y, { dash: true })}</g>`;
    y += 16;
    const heights = stage.details.map((id) =>
      k.height(id, textW - 32, { size: 16 }),
    );
    const boxH =
      32 + heights.reduce((a, b) => a + b, 0) + (heights.length - 1) * 8;
    content += k.card(textX, y, textW, boxH);
    let detailY = y + 16;
    stage.details.forEach((id, i) => {
      content += k.label(id, textX + 16, detailY, textW - 32, heights[i], {
        size: 16,
      });
      detailY += heights[i] + 8;
    });
    y += boxH;
    const phaseH = k.height(stage.phase, 180, { size: 16, bold: true });
    content +=
      k.label(stage.phase, 32, start + (y - start - phaseH) / 2, 180, phaseH, {
        size: 16,
        bold: true,
        muted: true,
      }) + '</g>';
    y += index === 2 ? 24 : 44;
  }
  const lifelines = [left, right]
    .map((x) =>
      k.path(`M${x} ${24 + headerH} L${x} ${y - 8}`, {
        dash: true,
        arrow: false,
      }),
    )
    .join('');
  return k.svg(lifelines + content, y + 8);
}

function discovery(k, rtl) {
  const align = rtl ? 'right' : 'left';
  let y = 24,
    content = '';
  const requestH = k.height(0, 728, { size: 18, bold: true });
  content += k.card(120, y, 760, requestH + 32, { fill: '#d0d0d0' });
  content += k.label(0, 136, y + 16, 728, requestH, { size: 18, bold: true });
  y += requestH + 32;
  content += k.arrow(500, y + 8, 500, y + 40);
  y += 48;
  const codeH = k.height(1, 608, { size: 14, mono: true });
  content += k.card(180, y, 640, codeH + 32, { fill: '#d0d0d0' });
  content += k.label(1, 196, y + 16, 608, codeH, {
    size: 14,
    mono: true,
    direction: rtl ? 'rtl' : 'ltr',
  });
  y += codeH + 32;
  content += k.arrow(500, y + 8, 500, y + 40);
  y += 48;
  const headingH = k.height(2, 904, { size: 20, bold: true });
  const serverW = 164,
    serverTextW = 140;
  const titleH = Math.max(
    ...[3, 5, 7, 9, 11].map((id) =>
      k.height(id, serverTextW, { size: 18, bold: true }),
    ),
  );
  const scoreH = Math.max(
    ...[4, 6, 8, 10, 12].map((id) => k.height(id, serverTextW, { size: 14 })),
  );
  const serverH = 32 + titleH + 8 + scoreH;
  const layerH = 24 + headingH + 24 + serverH + 24;
  content += k.card(24, y, 952, layerH, { fill: '#ffffff', dash: true });
  content += k.label(2, 48, y + 24, 904, headingH, {
    size: 20,
    bold: true,
    align,
  });
  const rowY = y + 24 + headingH + 24;
  for (let i = 0; i < 5; i++) {
    const x = 48 + i * 184;
    content +=
      `<g data-server="${i}">` +
      k.card(x, rowY, serverW, serverH, {
        fill: i === 0 ? '#d0d0d0' : '#f0f0f0',
      });
    content += k.label(3 + i * 2, x + 12, rowY + 16, serverTextW, titleH, {
      size: 18,
      bold: true,
    });
    content +=
      k.label(4 + i * 2, x + 12, rowY + 24 + titleH, serverTextW, scoreH, {
        size: 14,
        muted: true,
      }) + '</g>';
  }
  y += layerH;
  const topCaptionH = k.height(13, 680, { size: 16 });
  const gutter = Math.max(80, topCaptionH + 32);
  // The selected server leads into the second search stage, not into another server.
  content += `<g data-selected-server="0">${k.arrow(130, rowY + serverH + 8, 130, y + gutter - 8)}</g>`;
  content += k.label(
    13,
    166,
    y + (gutter - topCaptionH) / 2,
    680,
    topCaptionH,
    { size: 16, muted: true, align },
  );
  y += gutter;
  const toolHeadingH = k.height(14, 904, { size: 20, bold: true });
  let tools = k.label(14, 48, y + 24, 904, toolHeadingH, {
    size: 20,
    bold: true,
    align,
  });
  let toolY = y + 24 + toolHeadingH + 24;
  for (const row of [
    [0, 1, 2],
    [3, 4],
  ]) {
    const nameH = Math.max(
      ...row.map((i) => k.height(15 + i * 2, 256, { size: 14, mono: true })),
    );
    const detailH = Math.max(
      ...row.map((i) => k.height(16 + i * 2, 256, { size: 16 })),
    );
    const h = 32 + nameH + 10 + detailH;
    row.forEach((i, col) => {
      const x = 48 + col * 308;
      tools +=
        `<g data-tool="${i}">` +
        k.card(x, toolY, 288, h, {
          fill: [1, 2].includes(i) ? '#d0d0d0' : '#f0f0f0',
        });
      tools += k.label(15 + i * 2, x + 16, toolY + 16, 256, nameH, {
        size: 14,
        mono: true,
      });
      tools +=
        k.label(16 + i * 2, x + 16, toolY + 26 + nameH, 256, detailH, {
          size: 16,
          muted: true,
        }) + '</g>';
    });
    toolY += h + 20;
  }
  const returnH = k.height(25, 872, { size: 14, mono: true });
  tools += k.card(48, toolY + 4, 904, returnH + 32, { fill: '#d0d0d0' });
  tools += k.label(25, 64, toolY + 20, 872, returnH, {
    size: 14,
    mono: true,
    direction: rtl ? 'rtl' : 'ltr',
  });
  const bottom = toolY + 4 + returnH + 32 + 24;
  content +=
    k.card(24, y, 952, bottom - y, { fill: '#ffffff', dash: true }) + tools;
  return k.svg(content, bottom + 24);
}
