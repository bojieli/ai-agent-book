// Grid shading encodes Q-values. Keep the original cells, arrows, and labels
// together; reflow only the explanatory key beside them for the web reader.
export function layoutGridWorld(source) {
  const grid = source.match(
    /<rect x="50" y="65"[\s\S]*?<line x1="425" y1="65" x2="425" y2="440"[^>]*\/>/,
  )?.[0];
  if (!grid)
    throw new Error('Figure 8-3 grid geometry changed; review its web layout.');
  const labels = [
    ...source
      .slice(source.indexOf(grid) + grid.length)
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((m) =>
    m[1]
      .replace(/<\/?tspan\b[^>]*>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  );
  if (labels.length !== 12)
    throw new Error('Figure 8-3 annotation count changed.');
  const rows = labels
    .map((label, i) => {
      const y = 32 + i * 47;
      return `<foreignObject x="620" y="${y}" width="450" height="45"><div xmlns="http://www.w3.org/1999/xhtml" dir="auto" data-label="${i}" style="height:100%;display:flex;align-items:center;font-family:Arial,Helvetica,sans-serif;font-size:${i === 0 ? 22 : 18}px;font-weight:${[0, 4, 9, 10, 11].includes(i) ? 700 : 400};line-height:1.25;color:#333333;overflow-wrap:anywhere">${label}</div></foreignObject>`;
    })
    .join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 620" width="1100" height="620" role="img" style="background:#ffffff"><g transform="translate(-35 -40) scale(1.45)"><g data-preserve-colors="true">${grid}</g></g>${rows}</svg>`;
}
