// Web-only layout for Figure 1-1. Keep the tracked PDF/MkDocs sources unchanged.
// SVG text does not wrap; bounded XHTML labels allow each source translation to
// wrap naturally, including CJK and right-to-left scripts, without shrinking it.
export function layoutAgentLoop(source) {
  const labels = [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(
    (match) => match[1],
  );
  if (labels.length !== 18 || labels.some((label) => /<[^>]+>/.test(label))) {
    throw new Error(
      'Figure 1-1 source structure changed; review its web layout.',
    );
  }
  const title = source.match(/<title\b[^>]*>([\s\S]*?)<\/title>/)?.[1];
  const description = source.match(/<desc\b[^>]*>([\s\S]*?)<\/desc>/)?.[1];
  if (!title || !description)
    throw new Error('Figure 1-1 requires its source title and description.');
  const label = (index, x, y, width, height, size = 15, weight = 400) => `
    <foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
      <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:center;text-align:center;font-family:Arial,Helvetica,'PingFang SC','Microsoft YaHei',sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.35;color:#333;overflow-wrap:anywhere">
        <div dir="auto">${labels[index]}</div>
      </div>
    </foreignObject>`;
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 650" width="900" height="650" role="img" aria-labelledby="title desc">
  <title id="title">${title}</title>
  <desc id="desc">${description}</desc>
  <defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 10 4 0 8Z" fill="#333"/></marker></defs>
  <rect width="900" height="650" fill="white"/>
  <g stroke="#444" stroke-width="2" fill="white">
    <rect x="28" y="24" width="432" height="602" rx="12"/>
    <rect x="58" y="82" width="372" height="530" rx="10" fill="#f3f3f3" stroke="#666" stroke-dasharray="8 4"/>
    <rect x="145" y="160" width="250" height="108" rx="7"/>
    <rect x="145" y="298" width="250" height="132" rx="8" fill="#d5d5d5"/>
    <rect x="145" y="470" width="250" height="76" rx="7"/>
    <rect x="620" y="82" width="252" height="530" rx="12" fill="#eee"/>
    <rect x="640" y="214" width="212" height="104" rx="7"/>
  </g>
  <g fill="none" stroke="#333" stroke-width="2.2" marker-end="url(#arrow)">
    <path d="M270 270V295"/>
    <path d="M270 432V467"/>
    <path d="M620 190H398"/>
    <path d="M398 508H617"/>
  </g>
  <path d="M638 338H854" stroke="#b0b0b0"/>
  ${label(0, 44, 34, 400, 36, 20, 700)}
  ${label(1, 74, 90, 340, 60, 17, 700)}
  ${label(2, 157, 170, 226, 27, 17, 700)}
  ${label(3, 157, 202, 226, 56, 14)}
  ${label(4, 157, 310, 226, 30, 20, 700)}
  ${label(5, 157, 346, 226, 72)}
  ${label(6, 157, 478, 226, 60, 17, 700)}
  ${label(7, 74, 552, 340, 54, 14)}
  ${label(8, 634, 94, 224, 56, 20, 700)}
  ${label(9, 634, 151, 224, 48, 14)}
  ${label(10, 652, 222, 188, 32, 17, 700)}
  ${label(11, 652, 257, 188, 53, 14)}
  ${label(12, 638, 348, 216, 54)}
  ${label(13, 638, 404, 216, 54)}
  ${label(14, 638, 460, 216, 54)}
  ${label(15, 638, 516, 216, 84)}
  ${label(16, 470, 150, 140, 34)}
  ${label(17, 470, 468, 140, 34)}
</svg>\n`;
}
