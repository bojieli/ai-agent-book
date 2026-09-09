// Shared reading palette. Keep source geometry, text, and semantic color families.
// Never recolor embedded experimental pixels or screenshots.
export const palettes = {
  light: {
    paper: '#f7f9fc',
    surface: '#ffffff',
    panel: '#edf2f8',
    strong: '#dce7f5',
    ink: '#203047',
    muted: '#52627a',
    line: '#7386a0',
    inverse: '#ffffff',
    blue: '#dceaff',
    green: '#dcefe9',
    amber: '#fff0cb',
    red: '#f9e2e4',
  },
  dark: {
    paper: '#171e29',
    surface: '#1e2836',
    panel: '#273449',
    strong: '#344964',
    ink: '#e4ebf5',
    muted: '#b2bfd2',
    line: '#7c92af',
    inverse: '#172131',
    blue: '#263f61',
    green: '#23443f',
    amber: '#4c4026',
    red: '#503039',
  },
};
function color(hex, p, property) {
  let h = hex.slice(1);
  if (h.length === 3) h = [...h].map((x) => x + x).join('');
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  const high = Math.max(r, g, b),
    low = Math.min(r, g, b),
    light = (high + low) / 2;
  const text = property === 'color';
  if (text) return light > 220 ? p.inverse : light > 100 ? p.muted : p.ink;
  if (property === 'stroke') return p.line;
  if (high - low < 28) {
    if (light < 115) return p.ink;
    if (light < 190) return p.line;
    if (light < 230) return p.strong;
    if (light < 252) return p.panel;
    return p.surface;
  }
  if (r > b * 1.15 && g > b * 1.12 && Math.abs(r - g) < 85) return p.amber;
  if (r > g * 1.15 && r > b * 1.08) return light > 140 ? p.red : p.ink;
  if (g > r * 1.08 && g > b * 0.96) return light > 140 ? p.green : p.ink;
  return light > 130 ? p.blue : p.ink;
}
export function styleFigure(source, theme, { preserveHeatmap = false } = {}) {
  const protectedCells = [];
  if (preserveHeatmap)
    source = source.replace(
      /<rect\b[^>]*width="64"[^>]*height="64"[^>]*\/>|<text\b[^>]*>\d\.\d{2}<\/text>/g,
      (cell) => {
        protectedCells.push(cell);
        return `<!--DATA_CELL_${protectedCells.length - 1}-->`;
      },
    );
  const p = palettes[theme];
  // Only styles/attributes are transformed, never labels, IDs, or embedded data.
  let svg = source
    .replace(/<text\b[^>]*>/g, (tag) =>
      tag.replace(/fill="(#[\da-fA-F]{3,6}|white|black)"/, (_, value) => {
        const white = ['white', '#fff', '#ffffff'].includes(
          value.toLowerCase(),
        );
        return `fill="var(--figure-${white ? 'inverse' : 'ink'})"`;
      }),
    )
    .replace(
      /\b(fill|stroke)="(#[\da-fA-F]{3,8}|white|black)"/g,
      (_, prop, value) =>
        `${prop}="${color(value === 'white' ? '#ffffff' : value === 'black' ? '#000000' : value, p, prop)}"`,
    )
    .replace(
      /(background(?:-color)?|border(?:-color)?|border-left|color|fill|stroke)(\s*:\s*)([^;}"<]+)/g,
      (_full, prop, space, value) =>
        `${prop}${space}${value.replace(/#[\da-fA-F]{3,6}\b/g, (hex) => color(hex, p, prop.startsWith('border') ? 'stroke' : prop === 'background' || prop === 'background-color' ? 'fill' : prop))}`,
    );
  // Shared surface, corner treatment, and arrow weight; preserve chart cell geometry.
  svg = svg.replace(/<rect\b[^>]*\brx="([\d.]+)"[^>]*>/g, (tag, rx) =>
    Number(rx) >= 3 && Number(rx) <= 12
      ? tag.replace(/rx="[^"]*"/, 'rx="8"')
      : tag,
  );
  const background = `<style>svg{background:${p.paper}!important;--figure-ink:${p.ink};--figure-inverse:${p.inverse}} body{background:${p.paper}!important} line,path,polyline{stroke-linecap:round;stroke-linejoin:round}</style>`;
  return svg
    .replace(/(<svg\b[^>]*>)/, '$1' + background)
    .replace(/<!--DATA_CELL_(\d+)-->/g, (_, i) => protectedCells[Number(i)]);
}
export function frameRaster(bytes, mime, width, height, theme) {
  const p = palettes[theme],
    padding = 24;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width + padding * 2}" height="${height + padding * 2}" viewBox="0 0 ${width + padding * 2} ${height + padding * 2}" role="img"><title>Original image, presented without pixel changes</title><rect width="100%" height="100%" rx="8" fill="${p.paper}"/><image x="${padding}" y="${padding}" width="${width}" height="${height}" href="data:${mime};base64,${bytes.toString('base64')}"/></svg>`;
}
