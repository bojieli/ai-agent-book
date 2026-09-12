// Web presentation only. Keep the source labels and, for the fidelity plot,
// the source point coordinates; move long descriptions to a numbered key.
function sourceLabels(source, count) {
  const labels = [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((m) =>
    m[1]
      .replace(/<tspan\b[^>]*>/g, '')
      .replace(/<\/tspan>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  );
  if (labels.length !== count || labels.some((s) => /<[^>]+>/.test(s)))
    throw new Error(
      'Evaluation spectrum source changed; review the web layout.',
    );
  return labels;
}
function text(
  labels,
  indices,
  x,
  y,
  width,
  height,
  size = 18,
  bold = false,
  align = 'center',
) {
  return `<foreignObject x="${x}" y="${y}" width="${width}" height="${height}"><div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;flex-direction:column;justify-content:center;font-family:Arial,Helvetica,sans-serif;font-size:${size}px;line-height:1.3;font-weight:${bold ? 700 : 400};color:#333333;text-align:${align};overflow-wrap:anywhere">${indices.map((i) => `<div dir="auto" data-label="${i}">${labels[i]}</div>`).join('')}</div></foreignObject>`;
}
const card = (x, y, w, h) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="#f0f0f0" stroke="#7386a0" stroke-width="1.5"/>`;
const defs =
  '<defs><marker id="spectrum-arrow" markerWidth="10" markerHeight="8" refX="10" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L10 4L0 8Z" fill="#333333"/></marker></defs>';

export function layoutVerificationSpectrum(source) {
  const labels = sourceLabels(source, 24);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 640" width="1120" height="640" role="img" style="background:#ffffff">${defs}
  ${text(labels, [0], 24, 12, 800, 50, 20, true, 'start')}
  ${text(labels, [1], 870, 12, 220, 50, 20, true, 'end')}
  <line x1="30" y1="76" x2="1090" y2="76" stroke="#333333" stroke-width="2" marker-end="url(#spectrum-arrow)"/>
  ${[0, 1, 2, 3]
    .map((c) => {
      const x = 24 + c * 278,
        i = 2 + c * 4;
      return `${card(x, 100, 238, 290)}
    ${text(labels, [i], x + 14, 108, 210, 64, 21, true)}
    ${text(labels, [i + 1], x + 14, 176, 210, 64, 17)}
    ${text(labels, [i + 2], x + 14, 242, 210, 64, 17)}
    ${text(labels, [i + 3], x + 14, 308, 210, 64, 17)}
    ${c < 3 ? `<line x1="${x + 246}" y1="245" x2="${x + 270}" y2="245" stroke="#7386a0" stroke-width="2" marker-end="url(#spectrum-arrow)"/>` : ''}`;
    })
    .join('')}
  ${[0, 1]
    .map((c) => {
      const x = 24 + c * 556,
        i = 18 + c * 3;
      return `${card(x, 414, 516, 205)}
    ${text(labels, [i], x + 16, 422, 484, 43, 21, true)}
    ${text(labels, [i + 1], x + 16, 470, 484, 68, 17)}
    ${text(labels, [i + 2], x + 16, 544, 484, 64, 17)}`;
    })
    .join('')}
  </svg>`;
}

export function layoutSimulationFidelity(source) {
  const labels = sourceLabels(source, 28);
  const circles = [...source.matchAll(/<circle\b[^>]*>/g)].map(([s]) => ({
    x: Number(s.match(/\bcx="([^"]+)"/)?.[1]),
    y: Number(s.match(/\bcy="([^"]+)"/)?.[1]),
  }));
  if (
    circles.length !== 6 ||
    circles.some(({ x, y }) => !Number.isFinite(x) || !Number.isFinite(y))
  )
    throw new Error('Figure 7-9 point geometry changed.');
  const trend = source.match(/<line\b[^>]*stroke-dasharray="8,4"[^>]*\/>/)?.[0];
  if (!trend) throw new Error('Figure 7-9 trend line missing.');
  const groups = [
    [6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16],
    [17, 18, 19, 20],
    [21, 22, 23, 24],
    [25, 26, 27],
  ];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 860" width="1120" height="860" role="img" style="background:#ffffff">${defs}
    ${text(labels, [1, 2, 3, 4, 5], 24, 150, 156, 210, 20, true)}
    <g transform="translate(100 -28)">
      <line x1="100" y1="420" x2="860" y2="420" stroke="#333333" stroke-width="2" marker-end="url(#spectrum-arrow)"/>
      <line x1="100" y1="420" x2="100" y2="65" stroke="#333333" stroke-width="2" marker-end="url(#spectrum-arrow)"/>
      ${trend}
      ${circles.map(({ x, y }, i) => `<circle data-point="${i + 1}" cx="${x}" cy="${y}" r="17" fill="#d0d0d0" stroke="#7386a0" stroke-width="2"/><text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" font-family="Arial,sans-serif" font-size="19" font-weight="700" fill="#333333">${i + 1}</text>`).join('')}
    </g>
    ${text(labels, [0], 210, 400, 770, 48, 22, true)}
    ${groups
      .map(([heading, ...details], i) => {
        const x = 24 + (i % 3) * 366,
          y = 474 + Math.floor(i / 3) * 185;
        return `${card(x, y, 340, 165)}
      <circle cx="${x + 27}" cy="${y + 30}" r="15" fill="#d0d0d0" stroke="#7386a0"/><text x="${x + 27}" y="${y + 30}" text-anchor="middle" dominant-baseline="central" font-family="Arial,sans-serif" font-size="17" fill="#333333">${i + 1}</text>
      ${text(labels, [heading], x + 53, y + 8, 270, 43, 21, true, 'start')}
      ${text(labels, details, x + 18, y + 56, 304, 98, 17, false, 'start')}`;
      })
      .join('')}
    </svg>`;
}
