// Web-only reflows for Chapter 8's Q update, agent comparison, and VLM
// training figures. The tracked SVGs remain untouched and available through
// the original-image link.

function sourceLabels(source, figure, expectedLabels, expectedShape) {
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
  const shapeMatches = Object.entries(expectedShape).every(
    ([tag, expected]) => count(tag) === expected,
  );
  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    labels.length !== expectedLabels ||
    labels.some((label) => !label || /<[^>]+>/.test(label)) ||
    !shapeMatches
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
    {
      size = 18,
      weight = 400,
      mono = false,
      align = 'center',
      muted = false,
    } = {},
  ) => `<foreignObject x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;font-family:${mono ? "'Courier New',Courier,monospace" : "Arial,'Helvetica Neue',Helvetica,sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.28;color:${muted ? '#666666' : '#333333'};overflow-wrap:anywhere;word-break:normal;text-align:${align}"><div dir="auto" data-label="${index}" style="width:100%">${labels[index]}</div></div>
  </foreignObject>`;
  const card = (
    x,
    y,
    width,
    height,
    { fill = '#f0f0f0', dash = false, rx = 8 } = {},
  ) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="#7386a0" stroke-width="2"${dash ? ' stroke-dasharray="8,6"' : ''}/>`;
  const arrow = (x1, y1, x2, y2, muted = false) =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${muted ? '#666666' : '#333333'}" stroke-width="2.5" marker-end="url(#training-arrow)"/>`;
  return { label, card, arrow };
}

const definitions = `<defs>
  <marker id="training-arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="#333333"/></marker>
</defs>`;

export function layoutRlInteraction(source) {
  const labels = sourceLabels(source, '8-1', 27, {
    text: 27,
    rect: 7,
    line: 6,
    path: 0,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const participant = (first, x, fill) => `${card(x, 35, 340, 315, { fill })}
    ${label(first, x + 20, 48, 300, 80, { size: 23, weight: 700 })}
    ${label(first + 1, x + 20, 136, 300, 52, { size: 18 })}
    ${label(first + 2, x + 20, 198, 300, 64, { size: 18 })}
    ${label(first + 3, x + 20, 274, 300, 62, { size: 16, muted: true })}`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 820" width="1320" height="820" role="img" aria-labelledby="title" style="background:#ffffff">
    <title id="title">${labels[0]} · ${labels[4]}</title>
    ${definitions}
    ${participant(0, 120, '#d0d0d0')}
    ${participant(4, 860, '#f0f0f0')}
    ${label(8, 485, 74, 350, 92, { size: 20, weight: 700 })}
    ${arrow(478, 180, 842, 180)}
    ${arrow(842, 240, 478, 240)}
    ${label(9, 485, 258, 350, 88, { size: 20, weight: 700 })}
    <line x1="20" y1="380" x2="1300" y2="380" stroke="#999999" stroke-width="1"/>
    ${label(10, 40, 394, 1240, 70, { size: 23, weight: 700 })}
    ${Array.from({ length: 5 }, (_, step) => {
      const x = 20 + step * 272;
      const first = 11 + step * 3;
      return `${card(x, 480, 192, 210, { fill: '#f5f5f5' })}
        ${label(first, x + 14, 493, 164, 58, { size: 17, weight: 700 })}
        ${label(first + 1, x + 14, 558, 164, 80, { size: 17, muted: true })}
        ${label(first + 2, x + 14, 648, 164, 30, { size: 18, weight: 700 })}
        ${step < 4 ? arrow(x + 204, 585, x + 260, 585, true) : ''}`;
    }).join('')}
    ${label(26, 40, 726, 1240, 74, { size: 19, muted: true })}
  </svg>`;
}

// Give actions their own lanes instead of placing text on diagonal connectors.
export function layoutMdp(source) {
  const labels = sourceLabels(source, '8-2', 13, {
    text: 13,
    rect: 5,
    line: 3,
    path: 2,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const room = (index, x, y, width = 175) =>
    `${card(x, y, width, 90, { fill: index === 4 ? '#d0d0d0' : '#f0f0f0' })}
     ${label(index, x + 14, y + 12, width - 28, 66, { size: 20, weight: 700 })}`;
  const branch = (from, to, d) =>
    `<path data-from="${from}" data-to="${to}" d="${d}" fill="none" stroke="#333333" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#training-arrow)"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 690" width="1120" height="690" role="img" aria-labelledby="title" style="background:#ffffff">
    <title id="title">${labels[11]}</title>
    ${definitions}
    ${branch(0, 1, 'M 107.5 229 V 110 H 328')}
    ${branch(0, 2, 'M 107.5 331 V 410 H 328')}
    ${branch(1, 3, 'M 541 110 H 782.5 V 229')}
    ${branch(2, 3, 'M 541 410 H 782.5 V 331')}
    <g data-from="3" data-to="4">${arrow(877, 280, 918, 280)}</g>
    ${room(0, 20, 235)}
    ${room(1, 335, 65, 200)}
    ${room(2, 335, 365, 200)}
    ${room(3, 695, 235)}
    ${room(4, 925, 235)}
    ${label(5, 120, 20, 200, 76, { size: 18, muted: true })}
    ${label(6, 120, 430, 200, 80, { size: 18, muted: true })}
    ${label(7, 550, 20, 215, 76, { size: 18, muted: true })}
    ${label(8, 550, 430, 215, 80, { size: 18, muted: true })}
    ${label(9, 882, 344, 218, 110, { size: 18, muted: true })}
    ${label(10, 935, 176, 155, 44, { size: 21, weight: 700 })}
    ${card(20, 530, 1080, 140, { fill: '#ffffff' })}
    ${label(11, 45, 541, 1030, 48, { size: 23, weight: 700 })}
    ${label(12, 55, 592, 1010, 62, { size: 17, muted: true })}
  </svg>`;
}

export function layoutQUpdate(source) {
  const labels = sourceLabels(source, '8-4', 22, {
    text: 22,
    rect: 1,
    line: 0,
    path: 0,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const groups = [
    [3, 4, 5],
    [6, 7],
    [8, 9],
    [10, 11, 12],
    [13, 14, 15],
  ];
  const xs = [45, 255, 465, 675, 885];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 760" width="1120" height="760" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[2]}</title>
  ${definitions}

  ${card(20, 20, 1080, 120, { fill: '#ffffff' })}
  ${label(0, 55, 34, 1010, 52, { size: 24, weight: 700, mono: true })}
  ${label(1, 80, 88, 960, 36, { size: 16, muted: true })}

  ${card(20, 160, 1080, 290, { fill: '#ffffff', dash: true })}
  ${label(2, 50, 174, 1020, 48, { size: 23, weight: 700 })}
  ${groups
    .map((indices, position) => {
      const x = xs[position];
      const body = indices
        .slice(1)
        .map((index, detail) =>
          label(index, x + 14, 304 + detail * 60, 157, 54, {
            size: detail === 0 ? 17 : 15,
            weight: detail === 0 ? 700 : 400,
            muted: detail > 0,
          }),
        )
        .join('');
      return `${card(x, 232, 185, 196)}
      ${label(indices[0], x + 14, 244, 157, 50, { size: 16, weight: 700, muted: true })}
      ${body}
      ${position < xs.length - 1 ? arrow(x + 192, 330, x + 203, 330, true) : ''}`;
    })
    .join('')}

  ${card(20, 470, 1080, 150, { fill: '#f5f5f5' })}
  ${label(16, 45, 488, 160, 112, { size: 20, weight: 700 })}
  <line x1="220" y1="490" x2="220" y2="600" stroke="#999999" stroke-width="1.5"/>
  ${label(17, 245, 484, 830, 58, { size: 17, mono: true, align: 'start' })}
  ${label(18, 245, 548, 830, 58, { size: 17, mono: true, align: 'start' })}

  ${card(30, 644, 270, 86, { fill: '#ffffff' })}
  ${label(19, 48, 657, 234, 60, { size: 17, weight: 700 })}
  ${card(320, 644, 480, 86, { fill: '#f0f0f0' })}
  ${label(20, 342, 655, 436, 64, { size: 17, weight: 700 })}
  ${card(820, 644, 270, 86, { fill: '#ffffff' })}
  ${label(21, 838, 657, 234, 60, { size: 17, weight: 700 })}
</svg>`;
}

export function layoutTrainingAgents(source) {
  const labels = sourceLabels(source, '8-7', 31, {
    text: 31,
    rect: 11,
    line: 6,
    path: 0,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const leftSteps = [
    [2, 3],
    [4, 5],
    [6, 7],
    [8, 9],
  ];
  const rightSteps = [
    [10, 11],
    [12, 13],
    [14, 15],
    [16, 17],
  ];
  const ys = [80, 215, 350, 485];
  const agent = (heading, steps, panelX, cardX) => `${card(
    panelX,
    20,
    525,
    610,
    { fill: '#ffffff', dash: true },
  )}
    ${label(heading, panelX + 25, 32, 475, 36, { size: 22, weight: 700, align: 'start' })}
    ${steps
      .map(
        ([title, detail], position) => `${card(cardX, ys[position], 485, 110)}
        ${label(title, cardX + 20, ys[position] + 10, 445, 40, { size: 18, weight: 700 })}
        ${label(detail, cardX + 20, ys[position] + 52, 445, 48, { size: 14, mono: position === 3, muted: true })}
        ${position < 3 ? arrow(cardX + 242.5, ys[position] + 113, cardX + 242.5, ys[position + 1] - 8) : ''}`,
      )
      .join('')}`;

  const columns = [
    { x: 50, width: 280 },
    { x: 350, width: 320 },
    { x: 690, width: 380 },
  ];
  const cell = (index, column, y, height, options = {}) => {
    const { x, width } = columns[column];
    return label(index, x, y, width, height, options);
  };
  const rows = [
    [22, 23, 24],
    [25, 26, 27],
    [28, 29, 30],
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 1080" width="1120" height="1080" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[0]} · ${labels[1]} · ${labels[18]}</title>
  ${definitions}

  ${agent(0, leftSteps, 20, 40)}
  ${agent(1, rightSteps, 575, 595)}

  ${card(20, 650, 1080, 410, { fill: '#ffffff' })}
  ${label(18, 50, 663, 1020, 44, { size: 24, weight: 700 })}
  <rect x="40" y="720" width="1040" height="55" rx="6" fill="#d0d0d0" stroke="#7386a0" stroke-width="1.5"/>
  ${cell(19, 0, 728, 39, { size: 17, weight: 700 })}
  ${cell(20, 1, 728, 39, { size: 17, weight: 700 })}
  ${cell(21, 2, 728, 39, { size: 17, weight: 700 })}
  ${rows
    .map(([metric, qLearning, llm], position) => {
      const y = 785 + position * 90;
      return `<rect x="40" y="${y}" width="1040" height="80" rx="6" fill="${position % 2 === 0 ? '#f5f5f5' : '#f0f0f0'}"/>
      ${cell(metric, 0, y + 8, 64, { size: 17, weight: 700, align: 'start' })}
      ${cell(qLearning, 1, y + 8, 64, { size: 16, muted: true })}
      ${cell(llm, 2, y + 8, 64, { size: 16, muted: true })}`;
    })
    .join('')}
  <line x1="340" y1="720" x2="340" y2="1045" stroke="#999999" stroke-width="1.5"/>
  <line x1="680" y1="720" x2="680" y2="1045" stroke="#999999" stroke-width="1.5"/>
</svg>`;
}

export function layoutVlmTraining(source) {
  const labels = sourceLabels(source, '8-9', 27, {
    text: 27,
    rect: 5,
    line: 4,
    path: 0,
    marker: 2,
  });
  const { label, card, arrow } = helpers(labels);
  const modelCard = (x, heading, subtype, details, fill = '#f0f0f0') => `${card(
    x,
    230,
    300,
    330,
    { fill },
  )}
    ${label(heading, x + 20, 244, 260, 42, { size: 22, weight: 700 })}
    ${label(subtype, x + 20, 288, 260, 34, { size: 16, muted: true })}
    <line x1="${x + 24}" y1="332" x2="${x + 276}" y2="332" stroke="#999999" stroke-width="1.5"/>
    ${details
      .map((index, position) =>
        label(index, x + 20, 342 + position * 50, 260, 44, {
          size: 15,
          mono: position === 1 && x === 410,
          weight: position === 1 && x === 410 ? 700 : 400,
          muted: position !== 1 || x !== 410,
        }),
      )
      .join('')}`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 750" width="1120" height="750" role="img" aria-labelledby="title" style="background:#ffffff">
  <title id="title">${labels[22]} · ${labels[0]} · ${labels[6]} · ${labels[12]} · ${labels[24]}</title>
  ${definitions}

  ${card(20, 20, 300, 120, { fill: '#ffffff' })}
  ${label(22, 42, 32, 256, 40, { size: 20, weight: 700 })}
  ${label(23, 42, 76, 256, 48, { size: 15, muted: true })}
  ${arrow(170, 144, 170, 222)}

  ${card(800, 20, 300, 120, { fill: '#ffffff' })}
  ${label(24, 822, 32, 256, 40, { size: 20, weight: 700 })}
  ${label(25, 822, 75, 256, 50, { size: 14, muted: true })}
  ${arrow(950, 222, 950, 144)}

  ${modelCard(20, 0, 1, [2, 3, 4, 5], '#d0d0d0')}
  ${modelCard(410, 6, 7, [8, 9, 10, 11])}
  ${modelCard(800, 12, 13, [14, 15, 16, 17])}

  ${label(18, 325, 342, 80, 38, { size: 15, weight: 700 })}
  ${arrow(328, 400, 402, 400)}
  ${label(19, 325, 420, 80, 38, { size: 15, muted: true })}
  ${label(20, 715, 342, 80, 38, { size: 15, weight: 700 })}
  ${arrow(718, 400, 792, 400)}
  ${label(21, 715, 420, 80, 38, { size: 15, muted: true })}

  ${card(20, 590, 1080, 140, { fill: '#f5f5f5' })}
  ${label(26, 55, 607, 1010, 106, { size: 18, weight: 700 })}
</svg>`;
}

// Give stage descriptions and the format-stability connector separate space.
export function layoutSftToRl(source, { english = false } = {}) {
  const labels = sourceLabels(source, '8-11', 17, {
    text: 17,
    rect: 3,
    line: 1,
    path: 0,
    marker: 2,
  });
  if (english) labels[12] = 'When is SFT needed before RL?';
  const { label, card, arrow } = helpers(labels);
  const stage = (first, x, fill) => `${card(x, 20, 440, 430, { fill })}
    ${label(first, x + 24, 35, 392, 70, { size: 23, weight: 700 })}
    ${[1, 2, 3, 4]
      .map((offset) =>
        label(first + offset, x + 24, 120 + (offset - 1) * 78, 392, 70, {
          size: offset === 4 ? 17 : 18,
          muted: offset !== 4,
        }),
      )
      .join('')}`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 880" width="1120" height="880" role="img" aria-labelledby="title" style="background:#ffffff">
    <title id="title">${labels[0]} · ${labels[7]}</title>
    ${definitions}
    ${stage(0, 20, '#f0f0f0')}
    ${stage(7, 660, '#d0d0d0')}
    ${label(5, 480, 154, 160, 64, { size: 20, weight: 700, muted: true })}
    ${label(6, 480, 224, 160, 64, { size: 20, weight: 700, muted: true })}
    ${arrow(478, 320, 642, 320)}
    ${card(20, 480, 1080, 155, { fill: '#ffffff' })}
    ${label(12, 45, 490, 1030, 50, { size: 22, weight: 700 })}
    ${label(13, 50, 550, 1020, 70, { size: 18, muted: true })}
    ${label(14, 40, 655, 1040, 60, { size: 23, weight: 700 })}
    ${label(15, 40, 720, 1040, 60, { size: 19, muted: true })}
    ${label(16, 40, 795, 1040, 64, { size: 18, muted: true })}
  </svg>`;
}

// Keep the source token order and probabilities, with distinct regions for
// the sequence, candidate distribution, loss, and explanatory takeaway.
export function layoutNextToken(source, { chineseExampleSource } = {}) {
  const shape = {
    text: 21,
    rect: 13,
    line: 1,
    path: 0,
    marker: 2,
  };
  const labels = sourceLabels(source, '8-8', 21, shape);
  // A token-prediction example must retain its original language: translating
  // individual tokens changes what the illustrated distribution predicts.
  if (chineseExampleSource) {
    const original = sourceLabels(chineseExampleSource, '8-8', 21, shape);
    for (const index of [0, 1, 2, 3, 4, 5, 6, 7, 11, 13, 15, 17])
      labels[index] = original[index];
    labels.push(
      'Chinese example: “An agent needs to perform tasks in a real environment.” 中 and 里 mean “in”; 下 means “under”.',
    );
  }
  const { label, card, arrow } = helpers(labels);
  const probabilities = [12, 14, 16, 18].map((index) => {
    if (!/^\d+(\.\d+)?%$/.test(labels[index]))
      throw new Error(
        'Figure 8-8 probability format changed; review its web layout.',
      );
    const value = Number.parseFloat(labels[index]);
    if (value < 0 || value > 100)
      throw new Error('Figure 8-8 probability out of range.');
    return value;
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 780" width="1120" height="780" role="img" aria-labelledby="title" style="background:#ffffff">
    <title id="title">${labels[10]}</title>
    ${definitions}
    ${Array.from({ length: 8 }, (_, index) => {
      const x = 70 + index * 122;
      return `${card(x, 40, 104, 95, { fill: index < 5 ? '#d0d0d0' : index === 5 ? '#f0f0f0' : '#ffffff' })}
        ${label(index, x + 9, 50, 86, 75, { size: 18, weight: index === 5 ? 700 : 400 })}`;
    }).join('')}
    ${label(8, 20, 55, 35, 65, { size: 22, muted: true })}
    ${label(9, 1050, 55, 50, 65, { size: 22, muted: true })}
    ${arrow(732, 145, 732, 200)}
    ${chineseExampleSource ? label(21, 35, 215, 195, 315, { size: 17, muted: true, align: 'start' }) : ''}
    ${card(260, 210, 800, 320, { fill: '#ffffff' })}
    ${label(10, 280, 224, 760, 62, { size: 22, weight: 700 })}
    ${probabilities
      .map((value, row) => {
        const y = 294 + row * 54;
        return `${label(11 + row * 2, 280, y, 175, 48, { size: 20, align: 'end' })}
        <rect x="485" y="${y + 13}" width="330" height="22" rx="4" fill="#f5f5f5"/>
        <rect data-probability="${value}" x="485" y="${y + 13}" width="${value * 3.3}" height="22" rx="4" fill="#999999"/>
        ${label(12 + row * 2, 860, y, 165, 48, { size: 20, weight: 700, align: 'start' })}`;
      })
      .join('')}
    ${card(20, 560, 1080, 90, { fill: '#f0f0f0' })}
    ${label(19, 45, 575, 1030, 60, { size: 22, weight: 700 })}
    ${label(20, 40, 680, 1040, 80, { size: 20, muted: true })}
  </svg>`;
}
