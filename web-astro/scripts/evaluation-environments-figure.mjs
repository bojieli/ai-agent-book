import {
  evaluationKit,
  row,
  heading,
  title,
  code,
  edge,
  panel,
} from './evaluation-layout-kit.mjs';

export function layoutEvaluationEnvironments(source, options = {}) {
  const k = evaluationKit(source, 2, 23, options),
    width = 416;
  const headH = Math.max(
    k.height(0, 416, { size: 20, bold: true }),
    k.height(10, 416, { size: 20, bold: true }),
  );
  let left = k.label(0, 48, 44, 416, headH, { size: 20, bold: true }),
    right = k.label(10, 536, 44, 416, headH, { size: 20, bold: true });
  let ly = 44 + headH + 24,
    ry = ly;
  const agent = panel(k, 48, ly, width, [title(1)], {
    name: 'tool-agent',
    fill: '#d0d0d0',
  });
  left += agent.svg;
  ly += agent.h;
  for (const [name, rows] of [
    ['tool-execution', [title(2), code(3), code(4)]],
    ['verifier', [title(5), code(6), code(7)]],
    ['tool-reward', [title(8)]],
  ]) {
    left += edge(name, k.arrow(256, ly + 8, 256, ly + 48));
    ly += 56;
    const p = panel(k, 48, ly, width, rows, { name });
    left += p.svg;
    ly += p.h;
  }
  const noteL = panel(k, 48, ly + 24, width, [row(9, { muted: true })], {
    name: 'tool-features',
    fill: '#ffffff',
  });
  left += noteL.svg;
  ly += 24 + noteL.h;
  // The two participants use their own cards, with opposite arrows in the gap.
  const participantW = 176,
    participantH = Math.max(
      panel(k, 0, 0, participantW, [title(11)]).h,
      panel(k, 0, 0, participantW, [title(12)]).h,
    );
  right += panel(k, 536, ry, participantW, [title(11)], {
    name: 'user-simulator',
    min: participantH,
    fill: '#d0d0d0',
  }).svg;
  right += panel(k, 776, ry, participantW, [title(12)], {
    name: 'interaction-agent',
    min: participantH,
    fill: '#d0d0d0',
  }).svg;
  right += edge(
    'user-agent',
    k.arrow(720, ry + participantH / 2 - 12, 768, ry + participantH / 2 - 12),
  );
  right += edge(
    'agent-user',
    k.arrow(768, ry + participantH / 2 + 12, 720, ry + participantH / 2 + 12),
  );
  ry += participantH;
  const utteranceH = k.height(13, 260, { size: 14 }),
    gutter = Math.max(64, utteranceH + 24);
  right += k.label(13, 536, ry + 12, 260, utteranceH, {
    size: 14,
    align: 'start',
  });
  right += edge('interaction-tool', k.arrow(864, ry + 8, 864, ry + gutter - 8));
  ry += gutter;
  const tools = panel(k, 536, ry, width, [title(14), code(15), code(16)], {
    name: 'interaction-tool',
  });
  right += tools.svg;
  ry += tools.h;
  for (const [name, rows] of [
    ['double-verification', [title(17), code(18), code(19), code(20)]],
    ['interaction-reward', [title(21)]],
  ]) {
    right += edge(name, k.arrow(744, ry + 8, 744, ry + 48));
    ry += 56;
    const p = panel(k, 536, ry, width, rows, { name });
    right += p.svg;
    ry += p.h;
  }
  const noteR = panel(k, 536, ry + 24, width, [row(22, { muted: true })], {
    name: 'interaction-features',
    fill: '#ffffff',
  });
  right += noteR.svg;
  ry += 24 + noteR.h;
  const h = Math.max(ly, ry) + 24;
  return k.svg(
    `<g data-environment="tool-calling">${k.card(24, 24, 464, h - 24, { fill: '#ffffff', dash: true })}${left}</g><g data-environment="interaction">${k.card(512, 24, 464, h - 24, { fill: '#ffffff', dash: true })}${right}</g>`,
    h + 24,
  );
}
