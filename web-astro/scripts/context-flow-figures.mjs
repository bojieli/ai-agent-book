// Web-only spacing for the API/context flows. Source files and labels stay intact.
const number = (tag, name) =>
  Number(tag.match(new RegExp(`\\b${name}="([\\d.]+)"`))?.[1]);
const set = (tag, values) =>
  Object.entries(values).reduce(
    (result, [name, value]) =>
      result.replace(new RegExp(`\\b${name}="[^"]*"`), `${name}="${value}"`),
    tag,
  );

export function layoutContextFlow(source, figure, { rtl = false } = {}) {
  if (![2, 3, 4, 5, 8, 11].includes(figure))
    throw new Error('Unsupported context flow figure');
  const expectedLines = { 2: 1, 3: 4, 4: 4, 5: 6, 8: 1, 11: 2 }[figure];
  if ([...source.matchAll(/<line\b/g)].length !== expectedLines)
    throw new Error(
      `Figure 2-${figure} source structure changed; review its web layout.`,
    );

  // Explicit user-space units prevent stroke width from doubling the arrowhead.
  source = source.replace(/<marker\b[^>]*>[\s\S]*?<\/marker>/g, (marker) => {
    const id = marker.match(/\bid="([^"]+)"/)[1];
    const fill = marker.match(/\bfill="([^"]+)"/)[1];
    return `<marker id="${id}" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="${fill}"/></marker>`;
  });

  if (figure === 2) {
    source = source.replace(/<svg\b[^>]*>/, (tag) =>
      set(tag, { width: 940 }).replace('0 40 900 300', '0 40 940 300'),
    );
    source = source.replace(/<(?:rect|text)\b[^>]*>/g, (tag) => {
      const x = number(tag, 'x');
      if (x >= 490) return set(tag, { x: x + 40 });
      if (x === 440) return set(tag, { x: 470, y: 149 });
      if (x === 450) return set(tag, { x: 470 });
      return tag;
    });
    return source.replace(/<line\b[^>]*\/>/, (tag) =>
      set(tag, { x1: 418, x2: 522 }),
    );
  }

  if (figure === 3) {
    source = source.replace(/<svg\b[^>]*>/, (tag) =>
      set(tag, { height: 490 }).replace('0 40 900 430', '0 40 900 490'),
    );
    source = source.replace(/<(?:rect|text)\b[^>]*>/g, (tag) => {
      const y = number(tag, 'y');
      if (y >= 286) tag = set(tag, { y: y + 60 });
      else if (y >= 220) tag = set(tag, { y: y + 30 });
      if (number(tag, 'x') === 425)
        tag = set(tag, { y: number(tag, 'y') - 12 });
      return tag;
    });
    return source.replace(/<line\b[^>]*\/>/g, (tag) => {
      const y = number(tag, 'y1');
      if (y === 145) return set(tag, { x1: 378, x2: 472 });
      if (y === 198) return set(tag, { y1: 206, y2: 242 });
      if (y === 270) return set(tag, { y1: 308, y2: 352 });
      return set(tag, { x1: 472, x2: 378, y1: 399, y2: 399 });
    });
  }

  // Wrapped connector captions stay in dedicated gutters, including RTL editions.
  const caption = (content, x, y, width, height, align = 'center') =>
    `<foreignObject data-connector-caption="true" x="${x}" y="${y}" width="${width}" height="${height}"><div xmlns="http://www.w3.org/1999/xhtml" dir="${rtl ? 'rtl' : 'ltr'}" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.35;color:#666666;text-align:${align};overflow-wrap:anywhere">${content}</div></foreignObject>`;

  if (figure === 5) {
    source = source.replace(/<svg\b[^>]*>/, (tag) =>
      set(tag, { width: 1044, height: 220 }).replace(
        '0 40 900 184',
        '0 40 1044 220',
      ),
    );
    source = source.replace(
      /<text\b[^>]*\by="176"[^>]*>([\s\S]*?)<\/text>/,
      (_, text) => caption(text, 30, 198, 984, 48),
    );
    let column = -1;
    source = source.replace(/<(?:rect|text)\b[^>]*>/g, (tag) => {
      if (tag.startsWith('<rect')) column++;
      return set(tag, { x: number(tag, 'x') + column * 48 });
    });
    let index = 0;
    source = source.replace(/<line\b[^>]*\/>/g, (tag) => {
      if (tag.includes('stroke-dasharray')) return '';
      const x = 26 + index++ * 264;
      return set(tag, { x1: x + 208, x2: x + 256 });
    });
    return source.replace(
      '</svg>',
      '<path data-tool-return="true" d="M918 136 V170 Q918 178 910 178 H662 Q654 178 654 170 V136" fill="none" stroke="#333333" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#ah)"/></svg>',
    );
  }

  if (figure === 8) {
    source = source.replace(/<svg\b[^>]*>/, (tag) =>
      set(tag, { width: 1000 }).replace('0 30 900 260', '0 30 1000 260'),
    );
    source = source.replace(
      /<text\b[^>]*\bx="375\.0"[^>]*>([\s\S]*?)<\/text>/,
      (_, text) => caption(text, 342, 120, 166, 36),
    );
    source = source.replace(
      /<text\b[^>]*\bx="645"[^>]*>([\s\S]*?)<\/text>/,
      (_, text) => caption(text, 530, 210, 430, 68),
    );
    source = source.replace(/<(?:rect|text)\b[^>]*>/g, (tag) =>
      number(tag, 'x') >= 420 ? set(tag, { x: number(tag, 'x') + 100 }) : tag,
    );
    return source.replace(/<line\b[^>]*\/>/, (tag) =>
      set(tag, { x1: 338, x2: 512 }),
    );
  }

  if (figure === 11) {
    source = source.replace(/<svg\b[^>]*>/, (tag) =>
      set(tag, { height: 625 }).replace('0 40 820 525', '0 40 820 625'),
    );
    source = source.replace(
      /<text\b[^>]*\by="(?:173|353)"[^>]*>([\s\S]*?)<\/text>/g,
      (tag, text) =>
        caption(
          text,
          124,
          number(tag, 'y') === 173 ? 176 : 406,
          630,
          48,
          'start',
        ),
    );
    source = source.replace(/<(?:rect|text)\b[^>]*>/g, (tag) => {
      const y = number(tag, 'y');
      return y >= 370
        ? set(tag, { y: y + 100 })
        : y >= 190
          ? set(tag, { y: y + 50 })
          : tag;
    });
    return source.replace(/<line\b[^>]*\/>/g, (tag) =>
      set(tag, {
        x1: 100,
        x2: 100,
        y1: number(tag, 'y1') === 162 ? 168 : 398,
        y2: number(tag, 'y1') === 162 ? 232 : 462,
      }),
    );
  }

  // Keep message widths; use the unused right-hand space for 40px gutters.
  source = source.replace(/<(?:rect|text)\b[^>]*>/g, (tag) => {
    const x = number(tag, 'x'),
      y = number(tag, 'y');
    if (y === 244 && x >= 60)
      return set(tag, { x: 60 + ((x - 60) / 156) * 180 });
    if (y === 267) {
      const index = x === 714 ? 4 : (x - 130) / 156;
      return set(tag, { x: 60 + index * 180 + (index === 4 ? 30 : 70) });
    }
    return tag;
  });
  let index = 0;
  return source.replace(/<line\b[^>]*\/>/g, (tag) => {
    const x = 60 + index++ * 180;
    return set(tag, { x1: x + 148, x2: x + 172 });
  });
}
