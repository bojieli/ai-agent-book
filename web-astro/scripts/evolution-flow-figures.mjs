// Web-only reflows for Chapter 9's continual-evolution flows. Every label is
// taken from the tracked SVG for the active edition; the source art stays
// unchanged for print and for the original-image link.

import { palettes } from './figure-style.mjs';

const palette = palettes.light;

function sourceEntries(source, figure, expectedLabels, expectedShape) {
  const entries = [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b([^>]*)>([\s\S]*?)<\/text>/g),
  ].map((match, index) => {
    const attribute = (name) =>
      match[1].match(new RegExp(`\\b${name}="([^"]+)"`))?.[1];
    return {
      index,
      x: Number(attribute('x')),
      y: Number(attribute('y')),
      heading: /(?:^|\s)h(?:\s|$)/.test(attribute('class') || ''),
      value: match[2]
        .replace(/<tspan\b[^>]*>/g, '')
        .replace(/<\/tspan>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim(),
    };
  });
  const count = (tag) =>
    (source.match(new RegExp(`<${tag}\\b`, 'g')) || []).length;
  const allowedCount = Array.isArray(expectedLabels)
    ? expectedLabels.includes(entries.length)
    : entries.length === expectedLabels;
  const validShape = Object.entries(expectedShape).every(([tag, expected]) => {
    const actual = count(tag);
    return Array.isArray(expected)
      ? expected.includes(actual)
      : actual === expected;
  });

  if (
    !/<svg\b/.test(source) ||
    !/<\/svg>\s*$/.test(source) ||
    !allowedCount ||
    entries.some(
      ({ x, y, value }) =>
        !Number.isFinite(x) ||
        !Number.isFinite(y) ||
        !value ||
        /<[^>]+>/.test(value),
    ) ||
    !validShape
  )
    throw new Error(
      `Figure ${figure} source structure changed; review its web layout.`,
    );

  return entries;
}

function splitIntoGroups(entries, figure, classify, requiredGroups) {
  const groups = Object.fromEntries(requiredGroups.map((name) => [name, []]));
  for (const entry of entries) {
    const group = classify(entry);
    if (!groups[group])
      throw new Error(
        `Figure ${figure} source structure changed; review its web layout.`,
      );
    groups[group].push(entry);
  }
  if (Object.values(groups).some((items) => items.length === 0))
    throw new Error(
      `Figure ${figure} source structure changed; review its web layout.`,
    );
  return groups;
}

function helpers() {
  const label = (
    entry,
    x,
    y,
    width,
    height,
    {
      size = 17,
      weight = 400,
      align = 'center',
      muted = false,
      track = true,
    } = {},
  ) => `<foreignObject${track ? ` data-label="${entry.index}"` : ''} x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:Arial,'Helvetica Neue',Helvetica,sans-serif;font-size:${size}px;font-weight:${weight};line-height:1.3;color:${muted ? palette.muted : palette.ink};overflow-wrap:anywhere;word-break:normal;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%;unicode-bidi:plaintext">${entry.value}</div></div>
  </foreignObject>`;
  const stack = (entries, x, y, width, height, options = {}) => {
    const rowHeight = height / entries.length;
    return entries
      .map((entry, row) =>
        label(entry, x, y + row * rowHeight, width, rowHeight, options),
      )
      .join('');
  };
  const card = (
    x,
    y,
    width,
    height,
    { fill = palette.panel, dash = false, rx = 8, extra = '' } = {},
  ) =>
    `<rect${extra ? ` ${extra}` : ''} x="${x}" y="${y}" width="${width}" height="${height}" rx="${rx}" fill="${fill}" stroke="${palette.line}" stroke-width="2"${dash ? ' stroke-dasharray="8,6"' : ''}/>`;
  const arrow = (edge, path, { dash = false } = {}) =>
    `<path data-edge="${edge}" d="${path}" fill="none" stroke="${palette.muted}" stroke-width="2.5"${dash ? ' stroke-dasharray="8,6"' : ''} marker-end="url(#evolution-arrow)"/>`;
  const cardLabels = (entries, x, y, width, height) => {
    const sourceHeadings = entries.filter(({ heading }) => heading);
    const headings = sourceHeadings.length
      ? sourceHeadings
      : entries.slice(0, 1);
    const headingIds = new Set(headings.map(({ index }) => index));
    const details = entries.filter(({ index }) => !headingIds.has(index));
    const headingHeight = details.length
      ? Math.min(height * 0.44, Math.max(110, headings.length * 52))
      : height;
    return `${stack(headings, x, y, width, headingHeight, {
      size: 20,
      weight: 700,
    })}${
      details.length
        ? stack(
            details,
            x,
            y + headingHeight + 8,
            width,
            height - headingHeight - 8,
            {
              size: 17,
              muted: true,
            },
          )
        : ''
    }`;
  };
  return { arrow, card, cardLabels, label, stack };
}

const definitions = `<defs>
  <marker id="evolution-arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><polygon points="0 0, 10 4, 0 8" fill="${palette.muted}"/></marker>
</defs>`;

const stageXs = [20, 285, 550, 815, 1080];
const stageWidth = 210;

function pipelineArrows(arrow, y) {
  return stageXs
    .slice(0, -1)
    .map((x, stage) =>
      arrow(
        `stage-${stage + 1}-to-${stage + 2}`,
        `M${x + stageWidth + 8} ${y} H${stageXs[stage + 1] - 12}`,
      ),
    )
    .join('');
}

export function layoutEvolutionLoop(source) {
  const entries = sourceEntries(source, '9-1', [16, 17, 18, 19, 20], {
    text: [16, 17, 18, 19, 20],
    rect: 9,
    path: 6,
    line: 1,
    marker: 1,
  });
  const groups = splitIntoGroups(
    entries,
    '9-1',
    ({ x, y }) => {
      if (y < 50) return 'title';
      if (y >= 200) return 'footer';
      if (x < 190) return 'task';
      if (x < 370) return 'trajectory';
      if (x < 550) return 'signals';
      if (x < 810) return 'updates';
      return 'release';
    },
    ['title', 'task', 'trajectory', 'signals', 'updates', 'release', 'footer'],
  );
  const { arrow, card, cardLabels, label, stack } = helpers();
  const stages = [
    groups.task,
    groups.trajectory,
    groups.signals,
    groups.updates,
    groups.release,
  ];
  const updatesHeading = groups.updates.filter(({ heading }) => heading);
  const updateKinds = groups.updates.filter(({ heading }) => !heading);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 700" width="1320" height="700" role="img" aria-labelledby="evolution-loop-title" style="background:${palette.surface}">
  <title id="evolution-loop-title">${groups.title[0].value}</title>
  ${definitions}

  ${stack(groups.title, 50, 18, 1220, 76, { size: 24, weight: 700 })}
  ${stages
    .map(
      (items, stage) => `<g data-stage="${stage + 1}">
      ${card(stageXs[stage], 130, stageWidth, 300, {
        fill: stage === 2 || stage === 3 ? palette.strong : palette.panel,
      })}
      ${
        stage === 3
          ? `${stack(updatesHeading, stageXs[stage] + 16, 144, 178, 80, {
              size: 20,
              weight: 700,
            })}${updateKinds
              .map((entry, item) => {
                const x = stageXs[stage] + 14;
                const y = 224 + item * 50;
                return `${card(x, y, 182, 48, { fill: palette.surface })}${label(
                  entry,
                  x + 8,
                  y + 1,
                  166,
                  46,
                  { size: 17, muted: true },
                )}`;
              })
              .join('')}`
          : cardLabels(items, stageXs[stage] + 16, 144, 178, 270)
      }
    </g>`,
    )
    .join('')}
  ${pipelineArrows(arrow, 280)}
  ${arrow('release-to-execute', 'M1185 442 V492 H125 V442', { dash: true })}

  ${stack(
    groups.footer.filter(({ heading }) => heading),
    120,
    510,
    1080,
    62,
    {
      size: 22,
      weight: 700,
    },
  )}
  ${stack(
    groups.footer.filter(({ heading }) => !heading),
    110,
    580,
    1100,
    78,
    {
      size: 17,
      muted: true,
    },
  )}
  <line x1="300" y1="676" x2="1020" y2="676" stroke="${palette.line}" stroke-width="1.5"/>
</svg>`;
}

export function layoutExperienceKnowledge(source) {
  const entries = sourceEntries(source, '9-4', [20, 21, 22, 24, 28], {
    text: [20, 21, 22, 24, 28],
    rect: 6,
    path: 6,
    line: 0,
    marker: 1,
  });
  const groups = splitIntoGroups(
    entries,
    '9-4',
    ({ x, y }) => {
      if (y < 50) return 'title';
      if (y > 290) return 'note';
      if (y > 200) return 'feedback';
      if (x < 200) return 'raw';
      if (x < 400) return 'evaluation';
      if (x < 610) return 'compare';
      if (x < 820) return 'document';
      return 'retrieval';
    },
    [
      'title',
      'raw',
      'evaluation',
      'compare',
      'document',
      'retrieval',
      'feedback',
      'note',
    ],
  );
  const { arrow, card, cardLabels, stack } = helpers();
  const stages = [
    groups.raw,
    groups.evaluation,
    groups.compare,
    groups.document,
    groups.retrieval,
  ];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 840" width="1320" height="840" role="img" aria-labelledby="experience-knowledge-title" style="background:${palette.surface}">
  <title id="experience-knowledge-title">${groups.title[0].value}</title>
  ${definitions}

  ${stack(groups.title, 50, 18, 1220, 82, { size: 24, weight: 700 })}
  ${stages
    .map(
      (items, stage) => `<g data-stage="${stage + 1}">
      ${card(stageXs[stage], 130, stageWidth, 400, {
        fill: stage === 2 || stage === 3 ? palette.strong : palette.panel,
      })}
      ${cardLabels(items, stageXs[stage] + 16, 146, 178, 368)}
    </g>`,
    )
    .join('')}
  ${pipelineArrows(arrow, 330)}
  ${arrow('retrieval-to-comparison', 'M1185 542 V660 H655 V542', { dash: true })}
  ${stack(groups.feedback, 760, 576, 420, 60, { size: 17, muted: true })}

  ${card(150, 710, 1020, 104, { fill: palette.surface })}
  ${stack(groups.note, 180, 724, 960, 76, { size: 17, muted: true })}
</svg>`;
}

export function layoutEvolutionDeployment(source) {
  const entries = sourceEntries(source, '9-5', [17, 19, 20, 21, 22, 23], {
    text: [17, 19, 20, 21, 22, 23],
    rect: 11,
    path: 8,
    line: 0,
    marker: 1,
  });
  const groups = splitIntoGroups(
    entries,
    '9-5',
    ({ x, y }) => {
      if (y < 45) return 'title';
      if (y < 75) return 'version';
      if (y > 420) return 'trust';
      if (y >= 315) {
        if (x < 280) return 'diagnose';
        if (x < 480) return 'change';
        if (x < 680) return 'validate';
        return 'promote';
      }
      if (y > 205 && y < 260) return 'log';
      if (x < 100 && y < 200) return 'onlineHeading';
      if (x < 100) return 'offlineHeading';
      if (x < 400) return 'stable';
      if (x < 600) return 'tasks';
      return 'record';
    },
    [
      'title',
      'version',
      'trust',
      'diagnose',
      'change',
      'validate',
      'promote',
      'log',
      'onlineHeading',
      'offlineHeading',
      'stable',
      'tasks',
      'record',
    ],
  );
  const { arrow, card, label } = helpers();
  // Rejoin the print SVG's hard-wrapped fragments into natural paragraphs.
  // Keep each fragment's identity so label-preservation checks remain exact.
  const paragraph = (items, x, y, width, height, options = {}) =>
    label(
      {
        index: items[0].index,
        value: items
          .map(
            ({ index, value }) =>
              `<span data-source-label="${index}">${value}</span>`,
          )
          .join(' '),
      },
      x,
      y,
      width,
      height,
      { ...options, track: false },
    );
  const online = [groups.stable, groups.tasks, groups.record];
  const onlineXs = [126, 526, 926];
  const offline = [
    groups.diagnose,
    groups.change,
    groups.validate,
    groups.promote,
  ];
  // The offline row returns toward the stable agent, making a compact cycle.
  const offlineXs = [1016, 706, 396, 86];

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 808" width="1320" height="808" role="img" aria-labelledby="evolution-deployment-title" style="background:${palette.surface}">
  <title id="evolution-deployment-title">${groups.title[0].value}</title>
  ${definitions}

  ${paragraph(groups.title, 60, 12, 1200, 66, { size: 24, weight: 700 })}
  ${card(60, 100, 1200, 216, { fill: palette.surface, rx: 12 })}
  ${card(60, 406, 1200, 300, { fill: palette.panel, rx: 12 })}
  ${paragraph(groups.onlineHeading, 360, 114, 600, 48, { size: 22, weight: 700 })}
  ${paragraph(groups.offlineHeading, 360, 420, 600, 48, { size: 22, weight: 700 })}

  ${online
    .map(
      (items, stage) => `<g data-online-stage="${stage + 1}">
    ${card(onlineXs[stage], 178, 268, 112, { fill: palette.panel, rx: 10 })}
    ${paragraph(items, onlineXs[stage] + 20, 190, 228, 88, { size: 20, weight: 700 })}
  </g>`,
    )
    .join('')}
  ${arrow('online-1-to-2', 'M406 234 H514')}
  ${arrow('online-2-to-3', 'M806 234 H914')}

  ${arrow('experience-to-diagnosis', 'M1060 302 V360 H1130 V474', { dash: true })}
  ${paragraph(groups.log, 710, 327, 300, 66, { size: 18, weight: 700, muted: true })}
  ${arrow('release-to-stable', 'M200 474 V360 H260 V302', { dash: true })}
  ${paragraph(groups.version, 310, 327, 300, 66, { size: 18, weight: 700, muted: true })}

  ${offline
    .map(
      (items, stage) => `<g data-offline-stage="${stage + 1}">
    ${card(offlineXs[stage], 486, 228, 200, { fill: stage === 3 ? palette.strong : palette.surface, rx: 10 })}
    ${paragraph(
      items.filter(({ y }) => y < 360),
      offlineXs[stage] + 18,
      492,
      192,
      106,
      { size: 20, weight: 700 },
    )}
    <line x1="${offlineXs[stage] + 24}" y1="600" x2="${offlineXs[stage] + 204}" y2="600" stroke="${palette.line}" stroke-width="1"/>
    ${paragraph(
      items.filter(({ y }) => y >= 360),
      offlineXs[stage] + 18,
      606,
      192,
      70,
      { size: 17, muted: true },
    )}
  </g>`,
    )
    .join('')}
  ${arrow('offline-1-to-2', 'M1004 586 H946')}
  ${arrow('offline-2-to-3', 'M694 586 H636')}
  ${arrow('offline-3-to-4', 'M384 586 H326')}

  <line x1="120" y1="736" x2="1200" y2="736" stroke="${palette.line}" stroke-width="1.5"/>
  ${paragraph(groups.trust, 90, 750, 1140, 48, { size: 17, muted: true })}
</svg>`;
}
