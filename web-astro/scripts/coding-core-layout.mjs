import { extractLabels, figureKit } from './chapter3-figure-kit.mjs';
const section = { size: 20, bold: true };
const title = { size: 18, bold: true };
const body = { size: 16 };
const code = { size: 14, mono: true };

export function layoutCodingCore(source, figure, { rtl = false } = {}) {
  if (![1, 2].includes(figure))
    throw new Error(`Unsupported coding core figure ${figure}`);
  const labels = extractLabels(
    source,
    `5-${figure}`,
    figure === 1 ? [41] : [48, 53, 59, 60],
  );
  if (
    (source.match(/<rect\b/g) || []).length !== (figure === 1 ? 24 : 27) ||
    (source.match(/<line\b/g) || []).length !== (figure === 1 ? 4 : 10)
  )
    throw new Error(`Figure 5-${figure} source structure changed`);
  const k = figureKit(labels, { rtl });
  return figure === 1 ? architecture(k) : workflow(k, source, rtl);
}

function pair(k, a, b, x, y, w, { fill = '#f0f0f0', h } = {}) {
  const ah = k.height(a, w - 32, title),
    bh = k.height(b, w - 32, body);
  const needed = 32 + ah + 8 + bh;
  return {
    h: h ?? needed,
    svg:
      k.card(x, y, w, h ?? needed, { fill }) +
      k.label(a, x + 16, y + 16, w - 32, ah, title) +
      k.label(b, x + 16, y + 24 + ah, w - 32, bh, body),
  };
}
function architecture(k) {
  const headingH = k.height(0, 904, section);
  const platformH =
    Math.max(...[1, 2, 3, 4, 5].map((id) => k.height(id, 140, body))) + 24;
  let y = 24;
  let out =
    k.card(24, y, 952, 24 + headingH + 20 + platformH + 24, {
      fill: '#ffffff',
      dash: true,
    }) + k.label(0, 48, y + 24, 904, headingH, section);
  const platformY = y + 24 + headingH + 20;
  for (let i = 0; i < 5; i++)
    out +=
      k.card(48 + i * 184, platformY, 164, platformH, { fill: '#d0d0d0' }) +
      k.label(i + 1, 60 + i * 184, platformY + 12, 140, platformH - 24, body);
  y = platformY + platformH + 24;
  const requestH = k.height(6, 400, body),
    requestGap = Math.max(72, requestH + 24);
  out +=
    `<g data-edge="gateway-runtime">${k.arrow(500, y + 8, 500, y + requestGap - 8)}</g>` +
    k.label(6, 524, y + (requestGap - requestH) / 2, 400, requestH, body);
  y += requestGap;
  const runtimeY = y,
    runtimeTitleH = k.height(7, 904, section);
  let tools = k.label(7, 48, y + 24, 904, runtimeTitleH, section);
  let rowY = y + 24 + runtimeTitleH + 24;
  for (const row of [
    [8, 10, 12, 14],
    [16, 18, 20],
  ]) {
    const heights = row.map((a) => pair(k, a, a + 1, 0, 0, 208).h),
      h = Math.max(...heights);
    row.forEach((a, i) => {
      const x = 48 + i * 232;
      tools +=
        `<g data-runtime-tool="${a}">` +
        pair(k, a, a + 1, x, rowY, 208, { h, fill: '#ffffff' }).svg +
        '</g>';
    });
    rowY += h + 20;
  }
  const runtimeBottom = rowY + 4;
  out += k.card(24, runtimeY, 952, runtimeBottom - runtimeY) + tools;
  const externalY = runtimeBottom + 64;
  const renderModule = (ids, x) => {
    const hs = ids.map((id, i) => k.height(id, 272, i === 0 ? title : body));
    const h = 32 + hs.reduce((a, b) => a + b, 0) + 16;
    let s = k.card(x, externalY, 304, h, { fill: '#d0d0d0' }),
      cy = externalY + 16;
    ids.forEach((id, i) => {
      s += k.label(id, x + 16, cy, 272, hs[i], i === 0 ? title : body);
      cy += hs[i] + 8;
    });
    return { h, s };
  };
  const web = renderModule([22, 23, 24], 48),
    browser = renderModule([25, 26, 27], 648);
  out += web.s + browser.s;
  out += `<g data-edge="web-runtime">${k.arrow(200, externalY - 8, 200, runtimeBottom + 8)}</g>`;
  out += `<g data-edge="runtime-browser">${k.arrow(800, runtimeBottom + 8, 800, externalY - 8)}</g>`;
  const externalBottom = externalY + Math.max(web.h, browser.h);
  const fileCaptionH = k.height(28, 240, body);
  const filesystemY = externalBottom + 64 + fileCaptionH;
  out += `<g data-edge="runtime-filesystem">${k.arrow(500, runtimeBottom + 8, 500, filesystemY - 8)}</g>`;
  out += k.label(28, 520, externalBottom + 24, 400, fileCaptionH, body);
  const fsTitleH = k.height(29, 904, section);
  let fs = k.label(29, 48, filesystemY + 24, 904, fsTitleH, section);
  rowY = filesystemY + 24 + fsTitleH + 24;
  for (const row of [
    [30, 32, 34],
    [36, 38],
  ]) {
    const h = Math.max(...row.map((a) => pair(k, a, a + 1, 0, 0, 288).h));
    row.forEach((a, i) => {
      fs +=
        `<g data-memory-file="${a}">` +
        pair(k, a, a + 1, 48 + i * 308, rowY, 288, { h, fill: '#ffffff' }).svg +
        '</g>';
    });
    rowY += h + 20;
  }
  out +=
    k.card(24, filesystemY, 952, rowY + 4 - filesystemY, {
      fill: '#ffffff',
      dash: true,
    }) + fs;
  y = rowY + 28;
  const bannerH = k.height(40, 904, title);
  out +=
    k.card(24, y, 952, bannerH + 32, { fill: '#d0d0d0' }) +
    k.label(40, 48, y + 16, 904, bannerH, title);
  return k.svg(out, y + bannerH + 56);
}

function workflow(k, source, rtl) {
  const nodes = [...source.matchAll(/<text\b[^>]*>[\s\S]*?<\/text>/g)].map(
    (m, id) => ({ id, position: m.index }),
  );
  const divider = source.search(/<line\b[^>]*y1="320"/);
  const containers = [...source.matchAll(/<rect\b[^>]*width="155"[^>]*>/g)];
  const groups = containers.map((container, i) => {
    const end = containers[i + 1]?.index ?? divider;
    const region = source.slice(container.index, end);
    const tools = [...region.matchAll(/<rect\b[^>]*width="139"[^>]*>/g)].map(
      (m) => m.index + container.index,
    );
    const heading = nodes.find((n) => n.position > container.index).id;
    return {
      heading,
      steps: tools.map((position, j) =>
        nodes
          .filter(
            (n) => n.position > position && n.position < (tools[j + 1] ?? end),
          )
          .map((n) => n.id),
      ),
    };
  });
  if (
    groups.length !== 5 ||
    groups.some(
      (g) => g.steps.length !== 3 || g.steps.some((s) => s.length < 2),
    )
  )
    throw new Error('Figure 5-2 tool groups changed');
  let out = '',
    y = 24;
  for (const [i, g] of groups.entries()) {
    const headingH = k.height(g.heading, 904, section);
    const heights = g.steps.map((s) => {
      const sh = k.height(s[0], 256, code),
        dh = k.height(s.slice(1), 256, body);
      return { sh, dh, h: 32 + sh + 12 + dh };
    });
    const rowH = Math.max(...heights.map((h) => h.h)),
      stageH = 24 + headingH + 20 + rowH + 24;
    out +=
      `<g data-stage="${i + 1}">` +
      k.card(24, y, 952, stageH, { fill: '#ffffff' });
    out += k.label(g.heading, 48, y + 24, 904, headingH, {
      ...section,
      align: rtl ? 'right' : 'left',
    });
    const cy = y + 24 + headingH + 20;
    g.steps.forEach((s, j) => {
      const x = 48 + j * 308;
      out += k.card(x, cy, 288, rowH, {
        fill: [0, 3].includes(i) ? '#d0d0d0' : '#f0f0f0',
      });
      out += k.label(s[0], x + 16, cy + 16, 256, heights[j].sh, code);
      out += k.label(
        s.slice(1),
        x + 16,
        cy + 28 + heights[j].sh,
        256,
        heights[j].dh,
        { ...body, direction: rtl ? 'rtl' : 'ltr' },
      );
    });
    out += '</g>';
    y += stageH;
    if (i < 4) {
      out += `<g data-edge="stage-${i + 1}-${i + 2}">${k.arrow(500, y + 8, 500, y + 48)}</g>`;
      y += 56;
    }
  }
  const tail = nodes.filter((n) => n.position > divider).map((n) => n.id);
  if (tail.length !== 12) throw new Error('Figure 5-2 feedback labels changed');
  y += 32;
  const feedbackH = k.height(tail[0], 904, section);
  out += k.label(tail[0], 48, y, 904, feedbackH, section);
  y += feedbackH + 24;
  let feedbackBottom = y;
  for (let i = 0; i < 3; i++) {
    const p = pair(
      k,
      tail[1 + i * 2],
      tail[2 + i * 2],
      24,
      feedbackBottom,
      588,
    );
    out += p.svg;
    feedbackBottom += p.h + 16;
  }
  let utilityY = y;
  for (let i = 7; i < 11; i++) {
    const h = k.height(tail[i], 288, body);
    out +=
      k.card(656, utilityY, 320, h + 32, { fill: '#ffffff' }) +
      k.label(tail[i], 672, utilityY + 16, 288, h, body);
    utilityY += h + 48;
  }
  y = Math.max(feedbackBottom, utilityY) + 16;
  const lastH = k.height(tail[11], 904, title);
  out +=
    k.card(24, y, 952, lastH + 32, { fill: '#d0d0d0' }) +
    k.label(tail[11], 48, y + 16, 904, lastH, title);
  return k.svg(out, y + lastH + 56);
}
