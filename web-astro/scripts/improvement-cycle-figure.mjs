// Web-only Figure 7-8: separate the five improvement stages into roomy panels
// and route the iteration loop through a dedicated outer gutter.
// The tracked SVGs remain untouched and available through the original link.
export function layoutImprovementCycle(source) {
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
  if (labels.length !== 37 || labels.some((label) => /<[^>]+>/.test(label)))
    throw new Error(
      'Figure 7-8 source structure changed; review its web layout.',
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
  const hypothesisRow = (
    chip,
    detail,
    y,
  ) => `${card(590, y, 145, 45, '#d0d0d0')}
    ${label(chip, 600, y + 3, 125, 39, { size: 14, weight: 700 })}
    ${label(detail, 750, y, 295, 45, { size: 14, mono: true, align: 'start' })}`;
  const experimentCard = (
    heading,
    result,
    cost,
    x,
    fill,
  ) => `${card(x, 376, 235, 142, fill)}
    ${label(heading, x + 14, 385, 207, 38, { size: 17, weight: 700 })}
    <line x1="${x + 18}" y1="430" x2="${x + 217}" y2="430" stroke="#999999" stroke-width="1.5"/>
    ${label(result, x + 14, 438, 207, 35, { size: 15 })}
    ${label(cost, x + 14, 476, 207, 31, { size: 14, muted: true })}`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 900" width="1120" height="900" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[12]} · ${labels[30]}</title>
  <defs><marker id="arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker></defs>

  ${card(30, 20, 500, 250)}
  ${label(0, 52, 34, 456, 48, { size: 22, weight: 700 })}
  <line x1="52" y1="91" x2="508" y2="91" stroke="#999999" stroke-width="1.5"/>
  ${label(1, 55, 102, 450, 30, { size: 15, mono: true, align: 'start' })}
  ${label(2, 55, 135, 450, 30, { size: 15, mono: true, align: 'start' })}
  ${label(3, 55, 168, 450, 30, { size: 15, mono: true, align: 'start' })}
  ${label(4, 55, 201, 450, 50, { size: 15, mono: true, align: 'start' })}

  ${arrow(532, 145, 568, 145)}
  ${card(570, 20, 500, 250)}
  ${label(5, 592, 30, 456, 56, { size: 21, weight: 700 })}
  <line x1="592" y1="94" x2="1048" y2="94" stroke="#999999" stroke-width="1.5"/>
  ${hypothesisRow(6, 7, 105)}
  ${hypothesisRow(8, 9, 158)}
  ${hypothesisRow(10, 11, 211)}

  ${arrow(820, 272, 820, 306)}
  <rect x="30" y="311" width="1040" height="244" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(12, 55, 324, 990, 42, { size: 22, weight: 700 })}
  ${experimentCard(13, 14, 15, 50, '#d0d0d0')}
  ${experimentCard(16, 17, 18, 305, '#d0d0d0')}
  ${experimentCard(19, 20, 21, 560, '#f0f0f0')}
  ${experimentCard(22, 23, 24, 815, '#d0d0d0')}

  ${arrow(290, 557, 290, 586)}
  ${card(30, 591, 520, 220)}
  ${label(25, 52, 598, 476, 56, { size: 21, weight: 700 })}
  <line x1="52" y1="660" x2="528" y2="660" stroke="#999999" stroke-width="1.5"/>
  ${label(26, 55, 663, 470, 36, { size: 14, mono: true, align: 'start' })}
  ${label(27, 55, 699, 470, 36, { size: 14, mono: true, align: 'start' })}
  ${label(28, 55, 735, 470, 36, { size: 14, mono: true, align: 'start' })}
  ${label(29, 55, 771, 470, 36, { size: 14, mono: true, align: 'start' })}

  ${arrow(552, 701, 588, 701)}
  ${card(590, 591, 480, 220, '#d0d0d0')}
  ${label(30, 612, 598, 436, 56, { size: 21, weight: 700 })}
  <line x1="612" y1="660" x2="1048" y2="660" stroke="#999999" stroke-width="1.5"/>
  ${label(31, 615, 663, 430, 36, { size: 14, mono: true, align: 'start' })}
  ${label(32, 615, 699, 430, 36, { size: 14, mono: true, align: 'start' })}
  ${label(33, 615, 735, 430, 36, { size: 14, mono: true, align: 'start' })}
  ${label(34, 615, 771, 430, 36, { size: 14, mono: true, align: 'start' })}

  <path d="M 1072 701 H 1095 V 145 H 1074" fill="none" stroke="#333333" stroke-width="2.5" marker-end="url(#arrowhead)"/>
  ${label(35, 990, 278, 105, 28, { size: 15, weight: 700, muted: true })}

  ${card(55, 833, 1010, 50, '#999999')}
  ${label(36, 78, 838, 964, 40, { size: 16, weight: 700 })}
</svg>`;
}
