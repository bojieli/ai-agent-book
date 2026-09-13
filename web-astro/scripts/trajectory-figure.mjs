// Figure 1-4: a readable message timeline with a dedicated explanation column.
// Preserve all localized source labels, examples, and numerical results.
export function layoutTrajectory(source, { rtl = false } = {}) {
  const labels = [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(
    (match) =>
      match[1]
        .replace(/<tspan\b[^>]*>/g, '')
        .replace(/<\/tspan>/g, ' ')
        .trim(),
  );
  if (labels.length !== 29 || labels.some((label) => /<[^>]+>/.test(label)))
    throw new Error(
      'Figure 1-4 source structure changed; review its web layout.',
    );

  const label = (
    indices,
    x,
    y,
    width,
    height,
    { bold = false, mono = false, size = 16, muted = false } = {},
  ) => {
    const content = indices
      .map(
        (index) => `<span data-source-label="${index}">${labels[index]}</span>`,
      )
      .join(' ');
    return `<foreignObject x="${x}" y="${y}" width="${width}" height="${height}"><div xmlns="http://www.w3.org/1999/xhtml" dir="${mono ? 'ltr' : rtl ? 'rtl' : 'ltr'}" style="font-family:${mono ? "'Courier New',monospace" : 'Arial,Helvetica,sans-serif'};font-size:${size}px;font-weight:${bold ? 700 : 400};line-height:1.4;color:${muted ? '#666666' : '#333333'};overflow-wrap:anywhere">${content}</div></foreignObject>`;
  };
  const rect = (x, y, width, height, fill = '#ffffff') =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="${fill}" stroke="#999999" stroke-width="1.5"/>`;
  const round = (index, y) =>
    `<circle cx="48" cy="${y + 16}" r="6" fill="#333333"/>${label([index], 80, y, 608, 36, { bold: true, size: 20 })}`;
  const message = (
    heading,
    body,
    y,
    height,
    { mono = false, fill = '#ffffff', split = false } = {},
  ) => {
    const textY = y + 40;
    return `<g data-message="${heading}">${rect(80, y, 608, height, fill)}${label([heading], 100, y + 14, 568, 26, { bold: true, size: 15, muted: true })}${
      split
        ? body
            .map((index, i) =>
              label([index], 100, textY + i * 30, 568, 30, {
                mono,
                size: mono ? 15 : 16,
              }),
            )
            .join('')
        : label(body, 100, textY, 568, height - 48, {
            mono,
            size: mono ? 15 : 16,
          })
    }</g>`;
  };

  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1008" viewBox="0 0 1080 1008" role="img">
  <path data-round-timeline="true" d="M48 48 V842" fill="none" stroke="#999999" stroke-width="2"/>
  ${round(0, 24)}
  ${message(1, [2], 72, 100)}
  ${message(3, [4], 184, 100, { fill: '#f0f0f0' })}
  ${message(5, [6, 7], 296, 102, { mono: true, split: true, fill: '#f5f5f5' })}
  ${message(8, [9, 10], 410, 102, { mono: true, split: true })}
  ${round(11, 538)}
  ${message(12, [13], 582, 100, { fill: '#f0f0f0' })}
  ${message(14, [15], 694, 100, { mono: true, fill: '#f5f5f5' })}
  ${round(16, 826)}
  ${message(17, [18], 870, 100, { fill: '#d0d0d0' })}

  <path data-trajectory-bracket="true" d="M708 72 H724 V970 H708 M724 196 H752" fill="none" stroke="#999999" stroke-width="1.5"/>
  ${rect(752, 72, 296, 248, '#f0f0f0')}
  ${label([19], 776, 96, 248, 48, { bold: true, size: 22 })}
  ${label([20], 776, 146, 248, 28, { muted: true, size: 18 })}
  ${label([21, 22, 23], 776, 184, 248, 112, { size: 19 })}

  ${rect(752, 344, 296, 344)}
  ${label([24], 776, 366, 248, 48, { bold: true, size: 18 })}
  <path d="M776 414 H1024 M776 542 H1024" fill="none" stroke="#999999" stroke-width="1"/>
  ${label([25], 776, 436, 248, 52, { bold: true })}
  ${label([26], 776, 490, 248, 44, { size: 15, muted: true })}
  ${label([27], 776, 560, 248, 52, { bold: true })}
  ${label([28], 776, 622, 248, 44, { size: 15, muted: true })}
</svg>`;
}
