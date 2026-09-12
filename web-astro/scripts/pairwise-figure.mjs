// Web-only Figure 7-6: keep the anonymous comparison, Elo update, leaderboard,
// and pairwise-training note in distinct bands with room for translations.
// The tracked SVGs remain untouched and available through the original link.
export function layoutPairwise(source) {
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
  if (labels.length !== 42 || labels.some((label) => /<[^>]+>/.test(label)))
    throw new Error(
      'Figure 7-6 source structure changed; review its web layout.',
    );

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
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:${mono ? "'Courier New',monospace" : "Arial,'Helvetica Neue',Helvetica,sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.25;color:${muted ? '#666666' : '#333333'};overflow-wrap:anywhere;white-space:${mono ? 'pre-wrap' : 'normal'};text-align:${align}"><div dir="auto" style="width:100%">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (x, y, width, height, fill = '#f0f0f0') =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="10" fill="${fill}" stroke="#7386a0" stroke-width="2"/>`;
  const arrow = (x1, y1, x2, y2) =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#333333" stroke-width="2.5" marker-end="url(#arrowhead)"/>`;
  const divider = (y, dashed = false) =>
    `<line x1="55" y1="${y}" x2="1065" y2="${y}" stroke="#999999" stroke-width="1.5"${dashed ? ' stroke-dasharray="7,5"' : ''}/>`;

  const columns = [
    { x: 58, width: 92 },
    { x: 165, width: 365 },
    { x: 545, width: 150 },
    { x: 710, width: 345 },
  ];
  const tableLabel = (index, column, y, height, options = {}) => {
    const { x, width } = columns[column];
    return label(index, x, y, width, height, options);
  };

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 880" width="1120" height="880" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[11]}</title>
  <defs><marker id="arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker></defs>

  <rect x="30" y="20" width="1060" height="270" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(0, 55, 34, 1010, 42, { size: 25, weight: 700 })}
  ${card(55, 86, 455, 130)}
  ${label(1, 75, 94, 415, 32, { size: 19, weight: 700 })}
  <rect x="75" y="128" width="415" height="80" rx="8" fill="#f5f5f5" stroke="#999999" stroke-width="1.5"/>
  ${label(2, 90, 132, 385, 34, { size: 13, mono: true, align: 'start' })}
  ${label(3, 90, 168, 385, 34, { size: 13, mono: true, align: 'start' })}

  ${label(4, 520, 123, 80, 56, { size: 25, weight: 700, muted: true })}

  ${card(610, 86, 455, 130)}
  ${label(5, 630, 94, 415, 32, { size: 19, weight: 700 })}
  <rect x="630" y="128" width="415" height="80" rx="8" fill="#f5f5f5" stroke="#999999" stroke-width="1.5"/>
  ${label(6, 645, 133, 385, 68, { size: 13, mono: true, align: 'start' })}
  ${label(7, 645, 202, 1, 1, { size: 1, mono: true, align: 'start' })}

  <line x1="282" y1="218" x2="282" y2="228" stroke="#333333" stroke-width="2"/>
  <line x1="838" y1="218" x2="838" y2="228" stroke="#333333" stroke-width="2"/>
  <line x1="282" y1="228" x2="838" y2="228" stroke="#333333" stroke-width="2"/>
  ${arrow(560, 228, 560, 233)}
  <rect x="320" y="236" width="480" height="50" rx="10" fill="#d0d0d0" stroke="#7386a0" stroke-width="2"/>
  ${label(8, 340, 238, 440, 46, { size: 18, weight: 700 })}

  ${arrow(560, 292, 560, 322)}
  ${card(30, 327, 1060, 105, '#f5f5f5')}
  ${label(9, 55, 338, 1010, 30, { size: 21, weight: 700 })}
  ${label(10, 65, 369, 990, 52, { size: 15, mono: true })}

  ${arrow(560, 434, 560, 462)}
  <rect x="30" y="467" width="1060" height="302" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2"/>
  ${label(11, 55, 479, 1010, 36, { size: 23, weight: 700 })}
  <rect x="50" y="523" width="1020" height="36" rx="6" fill="#f0f0f0" stroke="#999999" stroke-width="1.5"/>
  ${tableLabel(12, 0, 526, 30, { size: 17, weight: 700 })}
  ${tableLabel(13, 1, 526, 30, { size: 17, weight: 700 })}
  ${tableLabel(14, 2, 526, 30, { size: 17, weight: 700 })}
  ${tableLabel(15, 3, 526, 30, { size: 17, weight: 700 })}

  <rect x="50" y="566" width="1020" height="32" rx="5" fill="#d0d0d0"/>
  ${tableLabel(16, 0, 568, 28, { size: 16, weight: 700 })}
  ${tableLabel(17, 1, 568, 28, { size: 16 })}
  ${tableLabel(18, 2, 568, 28, { size: 16, weight: 700 })}
  ${tableLabel(19, 3, 568, 28, { size: 16, muted: true })}
  <rect x="50" y="600" width="1020" height="32" rx="5" fill="#f0f0f0"/>
  ${tableLabel(20, 0, 602, 28, { size: 16, weight: 700 })}
  ${tableLabel(21, 1, 602, 28, { size: 16 })}
  ${tableLabel(22, 2, 602, 28, { size: 16, weight: 700 })}
  ${tableLabel(23, 3, 602, 28, { size: 16, muted: true })}
  ${divider(637, true)}
  ${tableLabel(24, 0, 642, 28, { size: 16, weight: 700 })}
  ${tableLabel(25, 1, 642, 28, { size: 16 })}
  ${tableLabel(26, 2, 642, 28, { size: 16, weight: 700 })}
  ${tableLabel(27, 3, 642, 28, { size: 16, muted: true })}
  ${tableLabel(28, 0, 674, 28, { size: 16, weight: 700 })}
  ${tableLabel(29, 1, 674, 28, { size: 16 })}
  ${tableLabel(30, 2, 674, 28, { size: 16, weight: 700 })}
  ${tableLabel(31, 3, 674, 28, { size: 16, muted: true })}
  ${tableLabel(32, 0, 706, 28, { size: 16, weight: 700 })}
  ${tableLabel(33, 1, 706, 28, { size: 16 })}
  ${tableLabel(34, 2, 706, 28, { size: 16, weight: 700 })}
  ${tableLabel(35, 3, 706, 28, { size: 16, muted: true })}
  ${tableLabel(36, 0, 738, 28, { size: 16, weight: 700 })}
  ${tableLabel(37, 1, 738, 28, { size: 16 })}
  ${tableLabel(38, 2, 738, 28, { size: 16, weight: 700 })}
  ${tableLabel(39, 3, 738, 28, { size: 16, muted: true })}

  ${card(80, 790, 960, 78, '#d0d0d0')}
  ${label(40, 105, 796, 910, 27, { size: 18, weight: 700 })}
  ${label(41, 105, 824, 910, 36, { size: 14, muted: true })}
</svg>`;
}
