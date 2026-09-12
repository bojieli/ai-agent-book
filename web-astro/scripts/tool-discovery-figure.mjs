// Wrap Figure 4-4's side annotations within the canvas. Source SVGs stay intact.
export function layoutToolDiscovery(source, { rtl = false } = {}) {
  const annotations = [
    ...source.matchAll(/<text\b[^>]*\bx="600"[^>]*>([\s\S]*?)<\/text>/g),
  ];
  if (annotations.length < 4)
    throw new Error('Unexpected Figure 4-4 annotations');
  const groups = [[], []];
  for (const annotation of annotations) {
    const y = Number(annotation[0].match(/\by="([\d.]+)"/)?.[1]);
    if (!Number.isFinite(y)) throw new Error('Missing annotation position');
    groups[y < 380 ? 0 : 1].push(annotation);
    source = source.replace(annotation[0], '');
  }
  for (const [index, group] of groups.entries()) {
    const heading = group.filter((a) => a[0].includes('font-weight="bold"'));
    const detail = group.filter((a) => !a[0].includes('font-weight="bold"'));
    if (!heading.length || !detail.length)
      throw new Error('Incomplete figure annotation');
    const text = (items) => items.map((a) => `<span>${a[1]}</span>`).join(' ');
    const block = `<foreignObject x="600" y="${index === 0 ? 282 : 436}" width="260" height="132"><div xmlns="http://www.w3.org/1999/xhtml" dir="${rtl ? 'rtl' : 'ltr'}" style="font-family:Arial,'Helvetica Neue',sans-serif;font-size:14px;line-height:1.35;overflow-wrap:anywhere;color:#333333"><div style="font-weight:700">${text(heading)}</div><div style="margin-top:7px;font-size:12.5px;color:#666666">${text(detail)}</div></div></foreignObject>`;
    source = source.replace('</svg>', `${block}</svg>`);
  }
  return source;
}
