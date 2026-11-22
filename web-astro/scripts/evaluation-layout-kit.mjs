import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';
export const row = (ids, options = {}) => ({ ids, ...options });
export const heading = (ids) => row(ids, { size: 20, bold: true });
export const title = (ids) => row(ids, { size: 18, bold: true });
export const code = (ids) => row(ids, { size: 14, mono: true, align: 'start' });
export const edge = (name, drawing) => `<g data-edge="${name}">${drawing}</g>`;
export function evaluationKit(source, number, count, options = {}) {
  const normalized = source.replace(/<text\b([^>]*)\/>/g, '<text$1></text>');
  const labels = extractLabels(normalized, `7-${number}`, [count]);
  const k = figureKit(labels, options);
  // Retain indentation in code examples without baking source line positions
  // into the new layout. The original label text remains independently traceable.
  const indents = [
    ...normalized.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((m) => Math.min(8, (m[1].match(/^ +/)?.[0] ?? '').length) * 8.4);
  return {
    ...k,
    height(ids, width, opts = {}) {
      return k.height(
        ids,
        width - (opts.mono && !Array.isArray(ids) ? indents[ids] : 0),
        opts,
      );
    },
    label(ids, x, y, width, h, opts = {}) {
      const indent = opts.mono && !Array.isArray(ids) ? indents[ids] : 0;
      return k.label(ids, x + indent, y, width - indent, h, opts);
    },
  };
}
export function panel(
  k,
  x,
  y,
  width,
  rows,
  { fill = '#f0f0f0', min = 0, name = '', dash = false } = {},
) {
  const heights = rows.map((r) => k.height(r.ids, width - 40, r));
  const h = Math.max(
    min,
    40 + heights.reduce((a, b) => a + b, 0) + (rows.length - 1) * 12,
  );
  let svg = `<g data-panel="${name}">${k.card(x, y, width, h, { fill, dash })}`,
    cursor = y + 20;
  rows.forEach((r, i) => {
    svg += k.label(r.ids, x + 20, cursor, width - 40, heights[i], r);
    cursor += heights[i] + 12;
  });
  return { svg: svg + '</g>', h };
}
