// Web-only reflows for Chapter 7's overview, dual-control, and embodied
// evaluation figures. The tracked SVGs remain untouched and available through
// the original-image link.

function extractLabels(source, figure, expectedLabels, expectedShape) {
  const normalizedSource = source.replace(
    /<text\b([^>]*)\/>/g,
    '<text$1></text>',
  );
  const labels = [
    ...normalizedSource.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((match) =>
    match[1]
      .replace(/<tspan\b[^>]*>/g, '')
      .replace(/<\/tspan>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  );
  const count = (tag) =>
    (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
  const shapeMatches = Object.entries(expectedShape).every(
    ([tag, expected]) => {
      const actual = count(tag);
      return Array.isArray(expected)
        ? expected.includes(actual)
        : actual === expected;
    },
  );
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    labels.length !== expectedLabels ||
    labels.some((value) => !value || /<[^>]+>/.test(value)) ||
    !shapeMatches
  )
    throw new Error(
      `Figure ${figure} source structure changed; review its web layout.`,
    );
  return labels;
}

function helpers(labels) {
  const label = (
    index,
    x,
    y,
    width,
    height,
    {
      size = 18,
      weight = 400,
      mono = false,
      align = 'center',
      muted = false,
    } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:${mono ? "'Courier New',Courier,monospace" : "Arial,'Helvetica Neue',Helvetica,sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.25;color:${muted ? '#666666' : '#333333'};overflow-wrap:anywhere;white-space:${mono ? 'pre-wrap' : 'normal'};text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (
    x,
    y,
    width,
    height,
    { fill = '#f0f0f0', dash = false, rx = 8 } = {},
  ) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="#7386a0" stroke-width="2"${dash ? ' stroke-dasharray="8,6"' : ''}/>`;
  const arrow = (x1, y1, x2, y2, { muted = false } = {}) =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${muted ? '#666666' : '#333333'}" stroke-width="2.5" marker-end="url(#arrowhead)"/>`;
  return { label, card, arrow };
}

const definitions = `<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker>
</defs>`;

export function layoutEvaluationOverview(source) {
  const labels = extractLabels(source, '7-1', 24, {
    text: 24,
    rect: 12,
    line: 6,
    path: 1,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 808" width="1120" height="808" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[9]} · ${labels[19]}</title>
  ${definitions}

  ${card(80, 20, 960, 82)}
  ${label(0, 105, 30, 910, 34, { size: 24, weight: 700 })}
  ${label(1, 105, 64, 910, 28, { size: 16, muted: true })}
  ${arrow(560, 104, 560, 126)}

  ${card(80, 130, 960, 218)}
  ${label(2, 105, 140, 910, 38, { size: 23, weight: 700 })}
  ${card(105, 188, 286, 140, { fill: '#ffffff' })}
  ${label(3, 120, 198, 256, 70, { size: 18, weight: 700 })}
  ${label(4, 120, 272, 256, 44, { size: 15, muted: true })}
  ${card(417, 188, 286, 140, { fill: '#ffffff' })}
  ${label(5, 432, 198, 256, 70, { size: 18, weight: 700 })}
  ${label(6, 432, 272, 256, 44, { size: 15, muted: true })}
  ${card(729, 188, 286, 140, { fill: '#ffffff' })}
  ${label(7, 744, 198, 256, 70, { size: 18, weight: 700 })}
  ${label(8, 744, 272, 256, 44, { size: 15, muted: true })}
  ${arrow(560, 350, 560, 372)}

  ${card(80, 376, 960, 210)}
  ${label(9, 105, 386, 910, 36, { size: 23, weight: 700 })}
  ${label(10, 105, 422, 910, 28, { size: 15, muted: true })}
  ${card(105, 462, 205, 104, { fill: '#ffffff' })}
  ${label(11, 120, 472, 175, 42, { size: 17, weight: 700 })}
  ${label(12, 120, 516, 175, 38, { size: 14, muted: true })}
  ${arrow(312, 514, 340, 514, { muted: true })}
  ${card(344, 462, 205, 104, { fill: '#ffffff' })}
  ${label(13, 359, 472, 175, 42, { size: 17, weight: 700 })}
  ${label(14, 359, 516, 175, 38, { size: 14, muted: true })}
  ${arrow(551, 514, 579, 514, { muted: true })}
  ${card(583, 462, 205, 104, { fill: '#ffffff' })}
  ${label(15, 598, 472, 175, 42, { size: 17, weight: 700 })}
  ${label(16, 598, 516, 175, 38, { size: 14, muted: true })}
  ${arrow(790, 514, 818, 514, { muted: true })}
  ${card(822, 462, 193, 104, { fill: '#ffffff' })}
  ${label(17, 837, 472, 163, 42, { size: 17, weight: 700 })}
  ${label(18, 837, 516, 163, 38, { size: 14, muted: true })}
  ${arrow(560, 588, 560, 610)}

  ${card(80, 614, 960, 84)}
  ${label(19, 105, 624, 910, 34, { size: 23, weight: 700 })}
  ${label(20, 105, 658, 910, 30, { size: 16, muted: true })}

  <path d="M80 656 H12 V239 H76" fill="none" stroke="#333333" stroke-width="2.5" stroke-dasharray="7,6" marker-end="url(#arrowhead)"/>
  <g transform="translate(20 578) rotate(-90)">
    ${label(21, 0, 0, 278, 42, { size: 14, muted: true })}
  </g>

  ${card(80, 718, 960, 70, { fill: '#f3f0e8' })}
  ${label(22, 105, 725, 910, 26, { size: 18, weight: 700 })}
  ${label(23, 105, 751, 910, 30, { size: 14, muted: true })}
</svg>`;
}

export function layoutDualControl(source) {
  const labels = extractLabels(source, '7-3', 34, {
    text: 34,
    rect: 11,
    line: 3,
    path: 0,
    marker: 3,
  });
  const { label, card, arrow } = helpers(labels);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 888" width="1120" height="888" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[4]} · ${labels[10]}</title>
  ${definitions}

  ${card(20, 20, 430, 210)}
  ${label(0, 42, 32, 386, 38, { size: 22, weight: 700 })}
  ${label(1, 42, 76, 386, 54, { size: 14, mono: true, align: 'start' })}
  ${label(2, 42, 134, 386, 42, { size: 14, mono: true, align: 'start' })}
  ${label(3, 42, 180, 386, 36, { size: 14, align: 'start', muted: true })}
  ${card(670, 20, 430, 210)}
  ${label(4, 692, 32, 386, 38, { size: 22, weight: 700 })}
  ${label(5, 692, 76, 386, 40, { size: 15, align: 'start' })}
  ${label(6, 692, 120, 386, 46, { size: 14, align: 'start', muted: true })}
  ${label(7, 692, 172, 386, 44, { size: 14, align: 'start', muted: true })}

  ${label(8, 468, 28, 184, 42, { size: 15, muted: true })}
  ${arrow(458, 82, 662, 82, { muted: true })}
  ${label(9, 468, 100, 184, 46, { size: 15, muted: true })}
  ${arrow(662, 160, 458, 160, { muted: true })}
  ${arrow(235, 232, 235, 260)}
  ${arrow(885, 232, 885, 260)}

  ${card(20, 264, 1080, 300, { fill: '#f3f0e8' })}
  ${label(10, 48, 275, 1024, 48, { size: 23, weight: 700 })}
  ${card(45, 334, 500, 210, { fill: '#ffffff' })}
  ${label(11, 65, 344, 460, 34, { size: 19, weight: 700 })}
  ${label(12, 65, 381, 460, 42, { size: 15, align: 'start', muted: true })}
  ${label(13, 65, 426, 460, 54, { size: 14, mono: true, align: 'start' })}
  ${label(14, 65, 486, 460, 42, { size: 14, mono: true, align: 'start' })}
  ${card(575, 334, 500, 210, { fill: '#ffffff' })}
  ${label(15, 595, 344, 460, 34, { size: 19, weight: 700 })}
  ${label(16, 595, 381, 460, 42, { size: 15, align: 'start', muted: true })}
  ${label(17, 595, 426, 460, 54, { size: 14, mono: true, align: 'start' })}
  ${label(18, 595, 486, 460, 42, { size: 14, mono: true, align: 'start' })}

  ${card(20, 584, 1080, 76, { fill: '#ffffff', dash: true })}
  ${label(19, 45, 594, 1030, 56, { size: 16, muted: true })}

  ${card(20, 684, 1080, 184)}
  ${label(20, 45, 692, 1030, 36, { size: 22, weight: 700 })}
  ${card(45, 736, 245, 88, { fill: '#ffffff' })}
  ${label(21, 57, 742, 221, 25, { size: 15, mono: true, weight: 700 })}
  ${label(22, 57, 768, 221, 24, { size: 14, muted: true })}
  ${label(23, 57, 793, 221, 25, { size: 13, muted: true })}
  ${card(307, 736, 245, 88, { fill: '#ffffff' })}
  ${label(24, 319, 742, 221, 25, { size: 15, mono: true, weight: 700 })}
  ${label(25, 319, 768, 221, 24, { size: 13, mono: true })}
  ${label(26, 319, 793, 221, 25, { size: 13, muted: true })}
  ${card(569, 736, 245, 88, { fill: '#ffffff' })}
  ${label(27, 581, 742, 221, 25, { size: 14, mono: true, weight: 700 })}
  ${label(28, 581, 768, 221, 24, { size: 13, muted: true })}
  ${label(29, 581, 793, 221, 25, { size: 13, muted: true })}
  ${card(831, 736, 244, 88, { fill: '#ffffff' })}
  ${label(30, 843, 742, 220, 25, { size: 15, mono: true, weight: 700 })}
  ${label(31, 843, 768, 220, 24, { size: 13, muted: true })}
  ${label(32, 843, 793, 220, 25, { size: 13, muted: true })}
  ${label(33, 45, 832, 1030, 28, { size: 14, mono: true, muted: true })}
</svg>`;
}

export function layoutEmbodiedEvaluation(source) {
  const labels = extractLabels(source, '7-10', 39, {
    text: 39,
    rect: 18,
    line: 8,
    path: 0,
    marker: [2, 3],
  });
  const { label, card, arrow } = helpers(labels);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 1000" width="1120" height="1000" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[8]} · ${labels[17]} · ${labels[26]}</title>
  ${definitions}

  ${card(20, 20, 270, 600, { fill: '#ffffff', dash: true })}
  ${label(0, 40, 32, 230, 70, { size: 22, weight: 700 })}
  ${card(40, 115, 230, 100)}
  ${label(1, 55, 122, 200, 50, { size: 17, weight: 700 })}
  ${label(2, 55, 174, 200, 28, { size: 14, muted: true })}
  ${card(40, 230, 230, 100)}
  ${label(3, 55, 237, 200, 50, { size: 17, weight: 700 })}
  ${label(4, 55, 290, 200, 28, { size: 14, muted: true })}
  ${card(40, 345, 230, 100)}
  ${label(5, 55, 352, 200, 50, { size: 17, weight: 700 })}
  ${label(6, 55, 405, 200, 28, { size: 14, muted: true })}
  ${card(40, 475, 230, 105, { fill: '#f7f9fc' })}
  ${label(7, 55, 486, 200, 83, { size: 15, mono: true })}

  ${card(350, 20, 400, 600, { fill: '#ffffff', dash: true })}
  ${label(8, 375, 32, 350, 70, { size: 21, weight: 700 })}
  ${card(375, 115, 350, 95, { fill: '#d0d0d0' })}
  ${label(9, 395, 124, 310, 38, { size: 18, weight: 700 })}
  ${label(10, 395, 164, 310, 34, { size: 14, muted: true })}
  ${arrow(550, 212, 550, 233)}
  ${card(375, 238, 350, 95)}
  ${label(11, 395, 247, 310, 38, { size: 18, weight: 700 })}
  ${label(12, 395, 287, 310, 34, { size: 14, muted: true })}
  ${arrow(550, 335, 550, 356)}
  ${card(375, 361, 350, 150, { fill: '#d0d0d0' })}
  ${label(13, 395, 370, 310, 38, { size: 18, weight: 700 })}
  ${label(14, 395, 410, 310, 40, { size: 14, muted: true })}
  ${label(15, 395, 453, 310, 48, { size: 13, mono: true })}
  ${card(375, 545, 350, 60)}
  ${label(16, 392, 553, 316, 44, { size: 15, weight: 700 })}
  ${arrow(550, 543, 550, 514)}

  ${arrow(292, 160, 342, 160)}
  ${arrow(292, 525, 342, 525)}

  ${card(850, 20, 250, 600, { fill: '#ffffff', dash: true })}
  ${label(17, 870, 32, 210, 70, { size: 21, weight: 700 })}
  ${card(870, 115, 210, 110)}
  ${label(18, 884, 124, 182, 44, { size: 17, weight: 700 })}
  ${label(19, 884, 171, 182, 40, { size: 14, muted: true })}
  ${card(870, 250, 210, 120, { fill: '#d0d0d0' })}
  ${label(20, 884, 259, 182, 46, { size: 17, weight: 700 })}
  ${label(21, 884, 308, 182, 50, { size: 14, muted: true })}
  ${card(870, 400, 210, 170)}
  ${label(22, 884, 410, 182, 84, { size: 16, weight: 700 })}
  ${label(23, 884, 498, 182, 62, { size: 14, muted: true })}

  ${label(25, 754, 108, 92, 34, { size: 14, muted: true })}
  ${arrow(848, 155, 752, 155)}
  ${label(24, 754, 263, 92, 34, { size: 14, muted: true })}
  ${arrow(752, 310, 848, 310)}

  <line x1="20" y1="655" x2="1100" y2="655" stroke="#999999" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(26, 45, 670, 1030, 44, { size: 25, weight: 700 })}
  ${card(20, 730, 255, 240)}
  ${label(27, 38, 746, 219, 52, { size: 19, weight: 700 })}
  ${label(28, 38, 805, 219, 68, { size: 16, muted: true })}
  ${label(29, 38, 878, 219, 68, { size: 16, muted: true })}
  ${card(295, 730, 255, 240)}
  ${label(30, 313, 746, 219, 52, { size: 19, weight: 700 })}
  ${label(31, 313, 805, 219, 68, { size: 16, muted: true })}
  ${label(32, 313, 878, 219, 68, { size: 16, muted: true })}
  ${card(570, 730, 255, 240)}
  ${label(33, 588, 746, 219, 52, { size: 19, weight: 700 })}
  ${label(34, 588, 805, 219, 68, { size: 16, muted: true })}
  ${label(35, 588, 878, 219, 68, { size: 16, muted: true })}
  ${card(845, 730, 255, 240)}
  ${label(36, 863, 746, 219, 52, { size: 19, weight: 700 })}
  ${label(37, 863, 805, 219, 68, { size: 16, muted: true })}
  ${label(38, 863, 878, 219, 68, { size: 16, muted: true })}
</svg>`;
}
