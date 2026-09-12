// Web-only Figure 7-5: route the three evidence sources through one input bus
// and give structured scores and aggregation rules separate readable columns.
// The tracked SVGs remain untouched and available through the original link.
export function layoutLlmJudge(source) {
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
  if (labels.length !== 35 || labels.some((label) => /<[^>]+>/.test(label)))
    throw new Error(
      'Figure 7-5 source structure changed; review its web layout.',
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
  const divider = (x1, y, x2) =>
    `<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke="#999999" stroke-width="1.5"/>`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 820" width="1120" height="820" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[15]} · ${labels[17]}</title>
  <defs><marker id="arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker></defs>

  ${card(30, 20, 330, 230, '#d0d0d0')}
  ${label(0, 48, 34, 294, 42, { size: 23, weight: 700 })}
  ${divider(48, 82, 342)}
  ${label(1, 52, 92, 286, 32, { size: 16, mono: true, align: 'start' })}
  ${label(2, 52, 124, 286, 32, { size: 16, mono: true, align: 'start' })}
  ${label(3, 52, 156, 286, 40, { size: 16, mono: true, align: 'start' })}
  ${label(4, 52, 200, 286, 32, { size: 16, mono: true, align: 'start' })}

  ${card(395, 20, 330, 230)}
  ${label(5, 413, 34, 294, 42, { size: 23, weight: 700 })}
  ${divider(413, 82, 707)}
  ${label(6, 417, 92, 286, 32, { size: 16, mono: true, align: 'start' })}
  ${label(7, 417, 126, 286, 48, { size: 15, mono: true, align: 'start' })}
  ${label(8, 417, 176, 286, 48, { size: 15, mono: true, align: 'start' })}
  ${label(9, 417, 226, 286, 1, { size: 1 })}

  ${card(760, 20, 330, 230)}
  ${label(10, 778, 34, 294, 42, { size: 22, weight: 700 })}
  ${divider(778, 82, 1072)}
  ${label(11, 782, 92, 286, 38, { size: 15, mono: true, align: 'start' })}
  ${label(12, 782, 132, 286, 32, { size: 16, mono: true, align: 'start' })}
  ${label(13, 782, 164, 286, 32, { size: 16, mono: true, align: 'start' })}
  ${label(14, 782, 196, 286, 40, { size: 16, mono: true, align: 'start' })}

  <line x1="195" y1="252" x2="195" y2="280" stroke="#333333" stroke-width="2.5"/>
  <line x1="560" y1="252" x2="560" y2="280" stroke="#333333" stroke-width="2.5"/>
  <line x1="925" y1="252" x2="925" y2="280" stroke="#333333" stroke-width="2.5"/>
  <line x1="195" y1="280" x2="925" y2="280" stroke="#333333" stroke-width="2.5"/>
  <line x1="560" y1="280" x2="560" y2="310" stroke="#333333" stroke-width="2.5" marker-end="url(#arrowhead)"/>

  <rect x="330" y="315" width="460" height="80" rx="10" fill="#7386a0" stroke="#333333" stroke-width="2"/>
  ${label(15, 350, 324, 420, 35, { size: 22, weight: 700 })}
  ${label(16, 350, 359, 420, 27, { size: 14, muted: true })}
  <line x1="560" y1="397" x2="560" y2="430" stroke="#333333" stroke-width="2.5" marker-end="url(#arrowhead)"/>

  <rect x="30" y="435" width="1060" height="355" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(17, 55, 450, 1010, 42, { size: 26, weight: 700 })}
  ${card(55, 505, 500, 255, '#f5f5f5')}
  ${label(18, 75, 518, 180, 48, { size: 16, mono: true, align: 'start' })}
  ${label(19, 260, 518, 62, 48, { size: 20, weight: 700 })}
  ${label(20, 328, 518, 205, 48, { size: 14, align: 'start', muted: true })}
  ${divider(75, 570, 535)}
  ${label(21, 75, 577, 180, 48, { size: 16, mono: true, align: 'start' })}
  ${label(22, 260, 577, 62, 48, { size: 20, weight: 700 })}
  ${label(23, 328, 577, 205, 48, { size: 14, align: 'start', muted: true })}
  ${divider(75, 629, 535)}
  ${label(24, 75, 636, 180, 48, { size: 16, mono: true, align: 'start' })}
  ${label(25, 260, 636, 62, 48, { size: 18, weight: 700 })}
  ${label(26, 328, 636, 205, 48, { size: 14, align: 'start', muted: true })}
  ${divider(75, 688, 535)}
  ${label(27, 75, 695, 180, 48, { size: 16, mono: true, align: 'start' })}
  ${label(28, 260, 695, 62, 48, { size: 20, weight: 700 })}
  ${label(29, 328, 695, 205, 48, { size: 14, align: 'start', muted: true })}

  ${card(575, 505, 490, 255)}
  ${label(30, 595, 518, 450, 42, { size: 22, weight: 700 })}
  ${divider(595, 568, 1045)}
  ${label(31, 597, 578, 446, 38, { size: 15, mono: true, align: 'start' })}
  ${label(32, 597, 618, 446, 38, { size: 15, mono: true, align: 'start' })}
  ${label(33, 597, 658, 446, 38, { size: 15, mono: true, align: 'start' })}
  ${label(34, 597, 698, 446, 48, { size: 14, mono: true, align: 'start' })}
</svg>`;
}
