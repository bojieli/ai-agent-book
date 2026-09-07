import {
  loadPosition,
  positionKey,
  type ReadingPosition,
} from '../lib/reading-position';

export function initReadingPosition() {
  const article = document.getElementById('chapter-content');
  const chapter = article?.dataset.chapterKey;
  if (!article || !chapter) return;
  const saved = loadPosition(chapter);
  const banner = document.getElementById('resume-reading')!;
  const resume = document.getElementById('resume-reading-button')!;
  const info = document.getElementById('resume-reading-section')!;
  const headings = [...article.querySelectorAll<HTMLElement>('h2[id], h3[id]')];
  const blocks = [article, ...headings];
  let timer = 0;
  let dirty = false;
  let restoring = false;
  const top = (el: HTMLElement) => el.getBoundingClientRect().top + scrollY;
  function capture(): ReadingPosition | null {
    const start = top(article!);
    const end = start + article!.offsetHeight;
    const line = scrollY + 120;
    if (line < start) return null;
    const current = blocks.findLast((block) => top(block) <= line) ?? article!;
    const index = blocks.indexOf(current);
    const nextTop = blocks[index + 1] ? top(blocks[index + 1]) : end;
    return {
      version: 1,
      chapter: chapter!,
      section: current === article ? '' : current.id,
      sectionTitle:
        current === article
          ? document.querySelector('h1')!.textContent!.trim()
          : current.textContent!.trim(),
      offset: Math.max(
        0,
        Math.min(
          1,
          (line - top(current)) / Math.max(1, nextTop - top(current)),
        ),
      ),
      progress: Math.max(
        0,
        Math.min(1, (line - start) / Math.max(1, end - start)),
      ),
    };
  }
  function save() {
    clearTimeout(timer);
    if (!dirty || restoring) return;
    const value = capture();
    if (value) {
      try {
        localStorage.setItem(positionKey(chapter!), JSON.stringify(value));
      } catch {
        /* Reading still works when storage is unavailable. */
      }
    }
    dirty = false;
  }
  async function restore() {
    if (!saved || restoring) return;
    restoring = true;
    banner.hidden = true;
    // Wait for image dimensions and fonts before measuring a section's relative position.
    await Promise.all([
      document.fonts.ready,
      ...[...article!.querySelectorAll('img')].map((image) =>
        image.decode().catch(() => {}),
      ),
    ]);
    const current =
      blocks.find((block) => block.id === saved.section) ?? article!;
    const index = blocks.indexOf(current);
    const end = blocks[index + 1]
      ? top(blocks[index + 1])
      : top(article!) + article!.offsetHeight;
    const offset = current === article && saved.section ? 0 : saved.offset;
    const y = top(current) + offset * Math.max(1, end - top(current)) - 120;
    window.scrollTo({ top: Math.max(0, y), behavior: 'instant' });
    current.tabIndex = -1;
    current.focus({ preventScroll: true });
    // Let the resulting scroll event settle before tracking fresh reading progress.
    requestAnimationFrame(() => {
      restoring = false;
    });
  }
  if (saved && saved.progress > 0.005) {
    info.textContent = `${saved.sectionTitle} · ${Math.round(saved.progress * 100)}%`;
    banner.hidden = Boolean(location.hash);
    resume.addEventListener('click', () => void restore());
    document.getElementById('dismiss-resume')!.addEventListener('click', () => {
      banner.hidden = true;
    });
  }
  const url = new URL(location.href);
  if (url.searchParams.has('resume')) {
    url.searchParams.delete('resume');
    history.replaceState(history.state, '', url);
    // An explicit section link always takes precedence over a saved position.
    if (saved && !url.hash) void restore();
  }
  addEventListener(
    'scroll',
    () => {
      if (restoring) return;
      dirty = true;
      clearTimeout(timer);
      timer = window.setTimeout(save, 350);
    },
    { passive: true },
  );
  addEventListener('pagehide', save);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) save();
  });
}

export function initContinueReading() {
  const link = document.querySelector<HTMLAnchorElement>(
    '[data-continue-reading]',
  );
  if (!link?.dataset.chapterKey) return;
  const label = link.querySelector<HTMLElement>('[data-reading-label]')!;
  const original = label.textContent;
  const path = link.getAttribute('href')!;
  const info = document.getElementById('continue-reading-info')!;
  const update = () => {
    const saved = loadPosition(link.dataset.chapterKey!);
    const continuing = saved && saved.progress > 0.005;
    label.textContent = continuing ? link.dataset.continueReading! : original;
    link.href = continuing ? `${path}?resume=1` : path;
    info.hidden = !continuing;
    info.textContent = continuing
      ? `${saved.sectionTitle} · ${Math.round(saved.progress * 100)}%`
      : '';
  };
  update();
  addEventListener('pageshow', update);
  addEventListener('storage', update);
}
