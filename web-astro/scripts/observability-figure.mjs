// Web-only Figure 7-7: give the detailed execution trace more space than the
// summary dashboard, show nested operations on a timeline, and let the closed
// loop message wrap in a dedicated footer. The tracked SVGs remain untouched.
export function layoutObservability(source) {
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
  if (labels.length !== 26 || labels.some((label) => /<[^>]+>/.test(label)))
    throw new Error(
      'Figure 7-7 source structure changed; review its web layout.',
    );

  const label = (
    index,
    x,
    y,
    width,
    height,
    { size = 18, weight = 400, align = 'center', muted = false } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.25;color:${muted ? '#666666' : '#333333'};overflow-wrap:anywhere;text-align:${align}"><div dir="auto" style="width:100%">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (x, y, width, height, fill = '#f0f0f0') =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="10" fill="${fill}" stroke="#7386a0" stroke-width="2"/>`;
  const traceCard = (heading, detail, y, child = false, strong = false) => {
    const x = child ? 155 : 110;
    const width = child ? 485 : 530;
    return `${card(x, y, width, 70, strong ? '#d0d0d0' : child ? '#f5f5f5' : '#f0f0f0')}
      ${label(heading, x + 18, y + 7, width - 36, detail === null ? 56 : 29, { size: strong ? 17 : 18, weight: 700, align: strong ? 'center' : 'start' })}
      ${detail === null ? '' : label(detail, x + 18, y + 36, width - 36, 27, { size: 16, align: 'start', muted: true })}`;
  };
  const node = (y, child = false) => {
    const x = child ? 130 : 85;
    const cardX = child ? 155 : 110;
    return `<line x1="${x}" y1="${y}" x2="${cardX}" y2="${y}" stroke="#7386a0" stroke-width="2"/><circle cx="${x}" cy="${y}" r="6" fill="#7386a0"/>`;
  };

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 820" width="1120" height="820" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[14]}</title>

  <rect x="30" y="20" width="640" height="680" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(0, 55, 36, 590, 42, { size: 25, weight: 700 })}
  <line x1="85" y1="127" x2="85" y2="615" stroke="#7386a0" stroke-width="2.5"/>
  <line x1="130" y1="369" x2="130" y2="451" stroke="#7386a0" stroke-width="2"/>
  ${node(127)}
  ${traceCard(1, null, 92, false, true)}
  ${node(205)}
  ${traceCard(2, 3, 170)}
  ${node(287)}
  ${traceCard(4, 5, 252)}
  <!-- Start the child branch at the tool card's bottom edge, outside its text. -->
  <line x1="130" y1="322" x2="130" y2="369" stroke="#7386a0" stroke-width="2"/>
  ${node(369, true)}
  ${traceCard(6, 7, 334, true)}
  ${node(451, true)}
  ${traceCard(8, 9, 416, true)}
  ${node(533)}
  ${traceCard(10, 11, 498)}
  ${node(615)}
  ${traceCard(12, 13, 580)}

  <rect x="700" y="20" width="390" height="680" rx="10" fill="#ffffff" stroke="#7386a0" stroke-width="2" stroke-dasharray="8,6"/>
  ${label(14, 720, 36, 350, 42, { size: 25, weight: 700 })}
  ${card(725, 92, 340, 180)}
  ${label(15, 745, 105, 300, 38, { size: 22, weight: 700 })}
  ${label(16, 745, 151, 300, 34, { size: 16, align: 'start', muted: true })}
  ${label(17, 745, 187, 300, 34, { size: 16, align: 'start', muted: true })}
  ${label(18, 745, 223, 300, 38, { size: 15, align: 'start', muted: true })}
  ${card(725, 292, 340, 150)}
  ${label(19, 745, 305, 300, 38, { size: 22, weight: 700 })}
  ${label(20, 745, 353, 300, 36, { size: 16, align: 'start', muted: true })}
  ${label(21, 745, 393, 300, 34, { size: 16, align: 'start', muted: true })}
  ${card(725, 462, 340, 205)}
  ${label(22, 745, 475, 300, 38, { size: 22, weight: 700 })}
  ${label(23, 745, 527, 300, 50, { size: 16, align: 'start', muted: true })}
  ${label(24, 745, 590, 300, 56, { size: 16, align: 'start', muted: true })}

  <rect x="30" y="725" width="1060" height="75" rx="12" fill="#d0d0d0" stroke="#7386a0" stroke-width="2"/>
  ${label(25, 65, 735, 990, 55, { size: 19, weight: 700 })}
</svg>`;
}
