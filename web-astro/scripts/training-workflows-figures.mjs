// Web-only reflows for Chapter 8's SFT pipeline and tool-use RL loop. The
// tracked source SVGs remain the source of every localized label.

function extractLabels(source, figure, expectedLabels, expectedShape) {
  const labels = [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((match) =>
    match[1]
      .replace(/<tspan\b[^>]*>/g, '')
      .replace(/<\/tspan>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  );
  const count = (tag) =>
    (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
  const validLabelCount = Array.isArray(expectedLabels)
    ? expectedLabels.includes(labels.length)
    : labels.length === expectedLabels;
  const validShape = Object.entries(expectedShape).every(([tag, expected]) => {
    const actual = count(tag);
    return Array.isArray(expected)
      ? expected.includes(actual)
      : actual === expected;
  });
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !validLabelCount ||
    labels.some((label) => !label || /<[^>]+>/.test(label)) ||
    !validShape
  )
    throw new Error(
      `Figure ${figure} source structure changed; review its web layout.`,
    );
  return labels;
}

function helpers(labels) {
  const label = (
    index,
    x,
    y,
    width,
    height,
    { size = 17, weight = 400, align = 'center', muted = false } = {},
  ) => `<foreignObject data-label="${index}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.3;color:${muted ? '#666666' : '#333333'};overflow-wrap:anywhere;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (x, y, width, height, { fill = '#f0f0f0', dash = false } = {}) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="${fill}" stroke="#7386a0" stroke-width="2"${dash ? ' stroke-dasharray="8,6"' : ''}/>`;
  const arrow = (path, { muted = false } = {}) =>
    `<path d="${path}" fill="none" stroke="${muted ? '#666666' : '#333333'}" stroke-width="2.5" marker-end="url(#training-arrow)"/>`;
  return { label, card, arrow };
}

const definitions = `<defs>
  <marker id="training-arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker>
</defs>`;

function stageNumber(number, x, y) {
  return `<circle cx="${x}" cy="${y}" r="17" fill="#d0d0d0" stroke="#7386a0" stroke-width="2"/><text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" font-family="Arial,'Helvetica Neue',Helvetica,sans-serif" font-size="17" font-weight="700" fill="#333333">${number}</text>`;
}

export function layoutSftPipeline(source) {
  const labels = extractLabels(source, '8-10', 28, {
    text: 28,
    rect: 4,
    line: 2,
    path: 0,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const stages = [
    { x: 20, labels: [0, 1, 2, 3, 4] },
    { x: 395, labels: [5, 6, 7, 8, 9] },
    { x: 770, labels: [10, 11, 12, 13, 14] },
  ];
  const protocols = [
    [16, 17, 18],
    [19, 20, 21],
    [22, 23, 24],
    [25, 26, 27],
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 770" width="1120" height="770" role="img" aria-labelledby="sft-title" style="background:#ffffff">
  <title id="sft-title">${labels[0]} · ${labels[5]} · ${labels[10]}</title>
  ${definitions}

  ${stages
    .map(
      ({ x, labels: indices }, stage) => `${card(x, 20, 330, 350, {
        fill: stage === 0 ? '#d0d0d0' : '#f0f0f0',
      })}
    ${stageNumber(stage + 1, x + 30, 50)}
    ${label(indices[0], x + 58, 30, 250, 82, { size: 22, weight: 700, align: 'start' })}
    ${label(indices[1], x + 22, 122, 286, 40, { size: 17, muted: true })}
    ${label(indices[2], x + 22, 168, 286, 46, { size: 16, muted: true })}
    ${label(indices[3], x + 22, 220, 286, 48, { size: 16, muted: true })}
    ${label(indices[4], x + 22, 274, 286, 72, { size: 16, muted: true })}`,
    )
    .join('')}
  ${arrow('M352 195 H383')}
  ${arrow('M727 195 H758')}

  ${card(20, 402, 1080, 344, { fill: '#f5f5f5' })}
  ${label(15, 48, 414, 1024, 46, { size: 23, weight: 700 })}
  ${protocols
    .map((indices, column) => {
      const x = 42 + column * 264;
      return `${card(x, 476, 244, 244, { fill: '#ffffff' })}
      ${label(indices[0], x + 16, 490, 212, 52, { size: 19, weight: 700 })}
      ${label(indices[1], x + 16, 552, 212, 62, { size: 16, muted: true })}
      ${label(indices[2], x + 16, 624, 212, 76, { size: 16, muted: true })}`;
    })
    .join('')}
</svg>`;
}

export function layoutToolRl(source) {
  const labels = extractLabels(source, '8-16', [18, 19], {
    text: [18, 19],
    rect: 5,
    line: 4,
    path: 1,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const challenges = [
    [12, 13],
    [14, 15],
    labels.length === 19 ? [16, 17, 18] : [16, 17],
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 1060" width="1120" height="1060" role="img" aria-labelledby="tool-rl-title" style="background:#ffffff">
  <title id="tool-rl-title">${labels[0]} · ${labels[7]} · ${labels[11]}</title>
  ${definitions}

  ${card(30, 70, 270, 280, { fill: '#d0d0d0' })}
  ${label(0, 52, 86, 226, 82, { size: 21, weight: 700 })}
  ${label(1, 52, 186, 226, 60, { size: 17, muted: true })}
  ${label(2, 52, 256, 226, 76, { size: 16, muted: true })}

  ${card(420, 20, 280, 188)}
  ${label(3, 442, 36, 236, 82, { size: 21, weight: 700 })}
  ${label(4, 442, 126, 236, 62, { size: 16, muted: true })}

  ${card(420, 288, 280, 188)}
  ${label(5, 442, 304, 236, 82, { size: 21, weight: 700 })}
  ${label(6, 442, 394, 236, 62, { size: 16, muted: true })}

  ${card(820, 70, 270, 280, { fill: '#f5f5f5' })}
  ${label(7, 842, 86, 226, 82, { size: 21, weight: 700 })}
  ${label(8, 842, 186, 226, 60, { size: 17, muted: true })}
  ${label(9, 842, 256, 226, 76, { size: 17, muted: true })}

  ${arrow('M312 125 C346 125 370 104 408 104')}
  ${arrow('M712 104 C748 104 772 125 808 125')}
  ${arrow('M560 220 V276')}
  ${arrow('M712 382 C760 382 770 285 808 285')}
  ${arrow('M955 362 V520 H165 V362')}
  ${label(10, 330, 538, 460, 65, { size: 17, muted: true })}

  ${card(20, 625, 1080, 408, { fill: '#f5f5f5' })}
  ${label(11, 48, 639, 1024, 54, { size: 23, weight: 700 })}
  ${challenges
    .map((indices, column) => {
      const x = 42 + column * 352;
      const detailHeight = indices.length === 3 ? 72 : 150;
      return `${card(x, 711, 330, 298, { fill: '#ffffff' })}
      ${stageNumber(column + 1, x + 30, 741)}
      ${label(indices[0], x + 58, 721, 250, 82, { size: 19, weight: 700, align: 'start' })}
      ${indices
        .slice(1)
        .map((index, row) =>
          label(index, x + 20, 813 + row * 78, 290, detailHeight, {
            size: 17,
            muted: true,
          }),
        )
        .join('')}`;
    })
    .join('')}
</svg>`;
}
