const REVEAL_PADDING = 16;
const FOLLOW_DELAY = 120;

export interface RevealGeometry {
  scrollTop: number;
  maxScrollTop: number;
  viewportTop: number;
  viewportBottom: number;
  itemTop: number;
  itemBottom: number;
  padding: number;
}

export function revealScrollTop({
  scrollTop,
  maxScrollTop,
  viewportTop,
  viewportBottom,
  itemTop,
  itemBottom,
  padding,
}: RevealGeometry): number | null {
  const safeTop = viewportTop + padding;
  const safeBottom = viewportBottom - padding;
  let delta = 0;
  if (itemTop < safeTop) delta = itemTop - safeTop;
  else if (itemBottom > safeBottom) delta = itemBottom - safeBottom;
  const target = Math.max(0, Math.min(maxScrollTop, scrollTop + delta));
  return Math.abs(target - scrollTop) < 0.5 ? null : target;
}

function revealInSidebar(
  sidebar: HTMLElement,
  item: HTMLElement,
  behavior: ScrollBehavior,
) {
  const viewport = sidebar.getBoundingClientRect();
  if (sidebar.clientHeight <= 0 || viewport.height <= 0) return;
  const rect = item.getBoundingClientRect();
  const top = revealScrollTop({
    scrollTop: sidebar.scrollTop,
    maxScrollTop: Math.max(0, sidebar.scrollHeight - sidebar.clientHeight),
    viewportTop: viewport.top,
    viewportBottom: viewport.bottom,
    itemTop: rect.top,
    itemBottom: rect.bottom,
    padding: REVEAL_PADDING,
  });
  if (top !== null) sidebar.scrollTo({ top, behavior });
}

interface RevealFollowerOptions {
  delay?: number;
  behavior?: () => ScrollBehavior;
  setTimer?: (callback: () => void, delay: number) => TimerHandle;
  clearTimer?: (timer: TimerHandle) => void;
}

type TimerHandle = ReturnType<typeof setTimeout> | number;

export function createRevealFollower<T>(
  reveal: (item: T, behavior: ScrollBehavior) => void,
  options: RevealFollowerOptions = {},
) {
  const delay = options.delay ?? FOLLOW_DELAY;
  const behavior = options.behavior ?? (() => 'smooth');
  const setTimer = options.setTimer ?? globalThis.setTimeout;
  const clearTimer = options.clearTimer ?? globalThis.clearTimeout;
  let item: T | null = null;
  let pointerInside = false;
  let focusInside = false;
  let timer: TimerHandle | undefined;

  const cancel = () => {
    if (timer !== undefined) clearTimer(timer);
    timer = undefined;
  };
  const request = (instant = false) => {
    cancel();
    if (item === null || pointerInside || focusInside) return;
    if (instant) {
      reveal(item, 'auto');
      return;
    }
    timer = setTimer(() => {
      timer = undefined;
      if (item !== null && !pointerInside && !focusInside)
        reveal(item, behavior());
    }, delay);
  };

  return {
    setItem(next: T | null, instant = false) {
      item = next;
      request(instant);
    },
    setPointerInside(inside: boolean) {
      pointerInside = inside;
      request();
    },
    setFocusInside(inside: boolean) {
      focusInside = inside;
      request();
    },
    refresh() {
      request();
    },
  };
}

function isVisible(element: HTMLElement | null): element is HTMLElement {
  return Boolean(
    element &&
    element.clientHeight > 0 &&
    element.getBoundingClientRect().height > 0,
  );
}

export function initReaderNavigation() {
  const chapterRail = document.querySelector<HTMLElement>('.chapter-rail');
  const currentChapter = chapterRail?.querySelector<HTMLElement>(
    '.chapter-navigation a.active',
  );
  const outlineRail = document.querySelector<HTMLElement>('.outline-rail');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const outlineFollower = createRevealFollower<HTMLElement>(
    (item, behavior) => {
      if (outlineRail) revealInSidebar(outlineRail, item, behavior);
    },
    { behavior: () => (reducedMotion.matches ? 'auto' : 'smooth') },
  );

  if (isVisible(chapterRail) && currentChapter)
    revealInSidebar(chapterRail, currentChapter, 'auto');

  if (outlineRail) {
    outlineFollower.setPointerInside(outlineRail.matches(':hover'));
    outlineFollower.setFocusInside(
      outlineRail.contains(document.activeElement),
    );
    outlineRail.addEventListener('pointerenter', () =>
      outlineFollower.setPointerInside(true),
    );
    outlineRail.addEventListener('pointerleave', () =>
      outlineFollower.setPointerInside(false),
    );
    outlineRail.addEventListener('focusin', () =>
      outlineFollower.setFocusInside(true),
    );
    outlineRail.addEventListener('focusout', () => {
      queueMicrotask(() =>
        outlineFollower.setFocusInside(
          outlineRail.contains(document.activeElement),
        ),
      );
    });
  }

  let refreshPending = false;
  const refresh = () => {
    refreshPending = false;
    const visible = isVisible(chapterRail);
    if (visible && currentChapter)
      revealInSidebar(chapterRail, currentChapter, 'auto');
    outlineFollower.refresh();
  };
  const scheduleRefresh = () => {
    if (refreshPending) return;
    refreshPending = true;
    requestAnimationFrame(refresh);
  };

  addEventListener('resize', scheduleRefresh);
  const resizeObserver = new ResizeObserver(scheduleRefresh);
  for (const element of [
    chapterRail,
    chapterRail?.querySelector('.chapter-navigation'),
    outlineRail,
    outlineRail?.querySelector('.section-outline'),
  ])
    if (element) resizeObserver.observe(element);

  return {
    setActiveOutline(item: HTMLElement | null, instant = false) {
      outlineFollower.setItem(item, instant);
    },
  };
}
