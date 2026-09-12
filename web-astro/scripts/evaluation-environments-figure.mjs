// Web-only Figure 7-2: give the two evaluation environments enough room for
// translated headings and keep the bidirectional exchange clear of its boxes.
// The tracked SVGs remain untouched and available through the original link.
export function layoutEvaluationEnvironments(source) {
  const labels = [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(
    (match) =>
      match[1]
        .replace(/<tspan\b[^>]*>/g, '')
        .replace(/<\/tspan>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim(),
  );
  if (labels.length !== 23 || labels.some((label) => /<[^>]+>/.test(label)))
    throw new Error(
      'Figure 7-2 source structure changed; review its web layout.',
    );

  const label = (
    index,
    x,
    y,
    width,
    height,
    { size = 18, weight = 400, mono = false, align = 'center' } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:${mono ? "'Courier New',monospace" : "Arial,'Helvetica Neue',Helvetica,sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.25;color:#333333;overflow-wrap:anywhere;white-space:${mono ? 'pre-wrap' : 'normal'};text-align:${align}"><div dir="auto">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (x, y, width, height) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="#f0f0f0" stroke="#7386a0" stroke-width="2"/>`;
  const codeBox = (x, y, width, height) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="6" fill="#f7f9fc" stroke="#999999" stroke-width="1.5"/>`;
  const arrow = (x1, y1, x2, y2) =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#333333" stroke-width="2.5" marker-end="url(#arrowhead)"/>`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 690" width="1120" height="690" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[10]}</title>
  <defs><marker id="arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker></defs>

  <rect x="20" y="20" width="530" height="650" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(0, 44, 34, 482, 52, { size: 24, weight: 700 })}
  <rect x="170" y="100" width="230" height="56" rx="8" fill="#d0d0d0" stroke="#7386a0" stroke-width="2"/>
  ${label(1, 184, 106, 202, 44, { size: 20, weight: 700 })}
  ${arrow(285, 158, 285, 190)}
  ${card(55, 195, 460, 115)}
  ${label(2, 76, 202, 418, 36, { size: 20, weight: 700 })}
  ${codeBox(75, 242, 420, 54)}
  ${label(3, 88, 247, 394, 21, { size: 15, mono: true, align: 'start' })}
  ${label(4, 88, 269, 394, 21, { size: 15, mono: true, align: 'start' })}
  ${arrow(285, 312, 285, 335)}
  ${card(55, 340, 460, 115)}
  ${label(5, 76, 347, 418, 36, { size: 20, weight: 700 })}
  ${codeBox(75, 387, 420, 54)}
  ${label(6, 88, 392, 394, 21, { size: 15, mono: true, align: 'start' })}
  ${label(7, 88, 414, 394, 21, { size: 15, mono: true, align: 'start' })}
  ${arrow(285, 457, 285, 480)}
  <rect x="135" y="485" width="300" height="52" rx="8" fill="#7386a0" stroke="#333333" stroke-width="2"/>
  ${label(8, 150, 491, 270, 40, { size: 19, weight: 700 })}
  ${codeBox(75, 552, 420, 64)}
  ${label(9, 90, 558, 390, 52, { size: 15, mono: true })}

  <rect x="570" y="20" width="530" height="650" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(10, 594, 34, 482, 52, { size: 24, weight: 700 })}
  <rect x="600" y="100" width="205" height="56" rx="8" fill="#d0d0d0" stroke="#7386a0" stroke-width="2"/>
  ${label(11, 614, 106, 177, 44, { size: 19, weight: 700 })}
  <rect x="865" y="100" width="205" height="56" rx="8" fill="#d0d0d0" stroke="#7386a0" stroke-width="2"/>
  ${label(12, 879, 106, 177, 44, { size: 19, weight: 700 })}
  ${arrow(815, 117, 855, 117)}
  ${arrow(855, 139, 815, 139)}
  ${label(13, 600, 160, 250, 32, { size: 14 })}
  ${arrow(968, 158, 968, 200)}
  ${card(605, 205, 460, 115)}
  ${label(14, 626, 212, 418, 36, { size: 20, weight: 700 })}
  ${codeBox(625, 252, 420, 54)}
  ${label(15, 638, 257, 394, 21, { size: 15, mono: true, align: 'start' })}
  ${label(16, 638, 279, 394, 21, { size: 14, mono: true, align: 'start' })}
  ${arrow(835, 322, 835, 345)}
  ${card(605, 350, 460, 135)}
  ${label(17, 626, 357, 418, 36, { size: 20, weight: 700 })}
  ${codeBox(625, 397, 420, 74)}
  ${label(18, 638, 400, 394, 21, { size: 14, mono: true, align: 'start' })}
  ${label(19, 638, 422, 394, 21, { size: 14, mono: true, align: 'start' })}
  ${label(20, 638, 444, 394, 21, { size: 13, mono: true, align: 'start' })}
  ${arrow(835, 487, 835, 510)}
  <rect x="685" y="515" width="300" height="52" rx="8" fill="#7386a0" stroke="#333333" stroke-width="2"/>
  ${label(21, 700, 521, 270, 40, { size: 19, weight: 700 })}
  ${codeBox(625, 582, 420, 64)}
  ${label(22, 640, 588, 390, 52, { size: 15, mono: true })}
</svg>`;
}
