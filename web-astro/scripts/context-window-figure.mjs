// Web-only Figure 2-1: separate the context brace from its label and let
// translated text wrap. Preserve every source label, including example code.
export function layoutContextWindow(source) {
  const labels = [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(
    (match) => match[1],
  );
  if (labels.length !== 19 || labels.some((label) => /<[^>]+>/.test(label))) {
    throw new Error(
      'Figure 2-1 source structure changed; review its web layout.',
    );
  }
  const label = (index, x, y, width, height, heading = false) => `
  <foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;font-family:${heading ? 'Arial,Helvetica,sans-serif' : "'Courier New',monospace"};font-size:${heading ? 20 : 15}px;font-weight:${heading ? 700 : 400};line-height:1.35;color:#333;overflow-wrap:anywhere;white-space:pre-wrap"><div dir="auto">${labels[index]}</div></div>
  </foreignObject>`;
  const cards = [
    { y: 24, height: 132, start: 0, rows: 2, fill: '#e3e6e8' },
    { y: 168, height: 120, start: 3, rows: 2, fill: '#f4f5f6' },
    { y: 300, height: 150, start: 6, rows: 3, fill: '#f4f5f6' },
    { y: 462, height: 144, start: 10, rows: 2, fill: '#edf0f2' },
    { y: 618, height: 120, start: 13, rows: 1, fill: '#fff' },
  ];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 870" width="980" height="870" role="img" aria-labelledby="title" style="background:#fff">
  <title id="title">${labels[15]} ${labels[16]}</title>
  ${cards
    .map((card) => {
      const rowHeight = (card.height - 48) / card.rows;
      return `<rect x="24" y="${card.y}" width="730" height="${card.height}" rx="8" fill="${card.fill}" stroke="#727980" stroke-width="1.5"/>
      ${label(card.start, 42, card.y + 6, 694, 36, true)}
      ${Array.from({ length: card.rows }, (_, i) => label(card.start + i + 1, 42, card.y + 42 + i * rowHeight, 694, rowHeight)).join('')}`;
    })
    .join('')}
  <path d="M766 24H788V738H766 M788 381H804" fill="none" stroke="#727980" stroke-width="2"/>
  ${label(15, 818, 321, 142, 52, true)}
  ${label(16, 818, 379, 142, 52, true)}
  <rect x="24" y="762" width="932" height="88" rx="8" fill="#f5f6f7" stroke="#d4d8db"/>
  ${label(17, 42, 768, 896, 30)}
  ${label(18, 42, 802, 896, 44)}
</svg>`;
}
