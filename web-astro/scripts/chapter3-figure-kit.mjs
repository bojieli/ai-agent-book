// Shared typography and layout primitives for the web edition of Chapter 3.
// Source SVG text is kept as content; browser line wrapping replaces font shrinking.
export function extractLabels(source, figure, allowedCounts) {
  const labels = [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(
    ([, text]) =>
      text
        .replace(/<tspan\b[^>]*>/g, '')
        .replace(/<\/tspan>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim(),
  );
  if (
    !allowedCounts.includes(labels.length) ||
    labels.some((text) => /<[^>]+>/.test(text))
  )
    throw new Error(
      `Figure ${figure} source labels changed; review its web layout.`,
    );
  return labels;
}

const plain = (text) =>
  text.replace(/&(?:quot|apos|amp|lt|gt|#\d+|#x[\da-f]+);/gi, 'x');
// Arial/Helvetica advance widths avoid reserving whole extra rows for short Latin
// labels. Other scripts keep a conservative fallback and are checked in-browser.
const advances = {
  normal: [
    667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 556, 556, 500, 556,
    556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500,
    278, 556, 500, 722, 500, 500, 500,
  ],
  bold: [
    722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 556, 611, 556, 611,
    556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611, 611, 611, 389, 556,
    333, 611, 556, 778, 556, 556, 500,
  ],
};
const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
function units(text, bold = false) {
  return [...plain(text)].reduce((sum, c) => {
    const base = c.normalize('NFD')[0];
    const index = alphabet.indexOf(base);
    if (index >= 0)
      return sum + advances[bold ? 'bold' : 'normal'][index] / 1000;
    if (/[\u0400-\u04ff]/.test(c)) return sum + (bold ? 0.7 : 0.6);
    if (/[\u2190-\u21ff\u2460-\u24ff]/.test(c)) return sum + 1;
    return (
      sum +
      (/\s/.test(c)
        ? 0.278
        : /[\u2e80-\u9fff\uac00-\ud7af\u3040-\u30ff]/.test(c)
          ? 1
          : /[\u0590-\u08ff\u0b80-\u0bff]/.test(c)
            ? 0.78
            : /[MW@%]/.test(c)
              ? 0.9
              : /[il.,:;'!|]/.test(c)
                ? 0.3
                : /[A-Z]/.test(c)
                  ? 0.65
                  : 0.52)
    );
  }, 0);
}

export function figureKit(labels, { rtl = false } = {}) {
  const indices = (value) => (Array.isArray(value) ? value : [value]);
  // Source diagrams sometimes split a Japanese word across separate text nodes.
  const separator = (left, right) =>
    /[\u2e80-\u9fff\u3040-\u30ff]$/.test(left) &&
    /^[\u2e80-\u9fff\u3040-\u30ff]/.test(right)
      ? ''
      : ' ';
  const joined = (value) =>
    indices(value).reduce(
      (text, id, position, ids) =>
        text +
        (position ? separator(labels[ids[position - 1]], labels[id]) : '') +
        labels[id],
      '',
    );
  const height = (
    value,
    width,
    { size = 16, mono = false, bold = false, min = 0 } = {},
  ) => {
    const text = joined(value);
    const capacity = width / size / 1.025;
    let lines = 1,
      used = 0;
    for (const word of plain(text).split(/\s+/)) {
      // Monospace fallbacks still use full-width glyphs for CJK text.
      let weight = mono
        ? [...word].reduce((sum, char) => sum + Math.max(0.61, units(char)), 0)
        : units(word, bold);
      let gap = used ? (mono ? 0.61 : 0.278) : 0;
      if (used && used + weight + gap > capacity) {
        lines++;
        used = 0;
        gap = 0;
      }
      while (weight > capacity) {
        lines++;
        weight -= capacity;
      }
      used += gap + weight;
    }
    return Math.max(min, Math.ceil(lines * size * 1.45 + 4));
  };
  const label = (
    value,
    x,
    y,
    width,
    h,
    {
      size = 16,
      bold = false,
      mono = false,
      muted = false,
      align = 'center',
      direction,
    } = {},
  ) => {
    const content = indices(value)
      .map(
        (i, position, ids) =>
          (position ? separator(labels[ids[position - 1]], labels[i]) : '') +
          `<span data-source-label="${i}">${labels[i]}</span>`,
      )
      .join('');
    return `<foreignObject x="${x}" y="${y}" width="${width}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" dir="${direction ?? (mono ? 'ltr' : rtl ? 'rtl' : 'ltr')}" style="box-sizing:border-box;width:100%;font-family:${mono ? "'Courier New',Courier,monospace" : 'Arial,Helvetica,sans-serif'};font-size:${size}px;font-weight:${bold ? 700 : 400};line-height:1.45;color:${muted ? '#666666' : '#333333'};text-align:${align};overflow-wrap:anywhere">${content}</div></foreignObject>`;
  };
  const card = (x, y, width, h, { fill = '#f0f0f0', dash = false } = {}) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${h}" rx="8" fill="${fill}" stroke="#999999" stroke-width="1.5"${dash ? ' stroke-dasharray="6 5"' : ''}/>`;
  const path = (d, { arrow = true, dash = false } = {}) =>
    `<path d="${d}" fill="none" stroke="#666666" stroke-width="2"${dash ? ' stroke-dasharray="6 5"' : ''}${arrow ? ' marker-end="url(#ch3-arrow)"' : ''}/>`;
  const arrow = (x1, y1, x2, y2, options) =>
    path(`M${x1} ${y1} L${x2} ${y2}`, options);
  const svg = (content, h, width = 1000) =>
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${h}" viewBox="0 0 ${width} ${h}" role="img"><defs><marker id="ch3-arrow" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#666666"/></marker></defs>${content}</svg>`;
  return { label, height, card, path, arrow, svg };
}
