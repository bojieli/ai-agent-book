export function initFigureViewer() {
  const get = <T extends HTMLElement>(id: string) =>
    document.getElementById(id) as T;
  const dialog = document.querySelector<HTMLDialogElement>('.figure-dialog')!;
  const canvas = document.querySelector<HTMLElement>('.figure-canvas')!;
  const image = get<HTMLImageElement>('expanded-figure');
  const smaller = get<HTMLButtonElement>('figure-zoom-out');
  const larger = get<HTMLButtonElement>('figure-zoom-in');
  const output = get<HTMLOutputElement>('figure-zoom-level');
  const levels = [1, 1.5, 2, 3, 4];
  let index = 0;
  let fitWidth = 0;
  let opener: HTMLButtonElement | undefined;
  let drag:
    { id: number; x: number; y: number; left: number; top: number } | undefined;

  function applyZoom(center = true) {
    if (!fitWidth) return;
    const before = image.getBoundingClientRect();
    const viewport = canvas.getBoundingClientRect();
    const centerX = viewport.left + canvas.clientLeft + canvas.clientWidth / 2;
    const centerY = viewport.top + canvas.clientTop + canvas.clientHeight / 2;
    const fractionX = before.width
      ? Math.max(0, Math.min(1, (centerX - before.left) / before.width))
      : 0.5;
    const fractionY = before.height
      ? Math.max(0, Math.min(1, (centerY - before.top) / before.height))
      : 0.5;
    image.style.width = `${fitWidth * levels[index]}px`;
    const after = image.getBoundingClientRect();
    // Preserve the point on the image, accounting for padding and centered margins.
    canvas.scrollLeft = center
      ? canvas.scrollLeft + after.left + fractionX * after.width - centerX
      : 0;
    canvas.scrollTop = center
      ? canvas.scrollTop + after.top + fractionY * after.height - centerY
      : 0;
    canvas.dataset.zoomed = String(index > 0);
    output.value = `${Math.round(levels[index] * 100)}%`;
    smaller.disabled = index === 0;
    larger.disabled = index === levels.length - 1;
  }
  function fit() {
    if (!dialog.open || !image.naturalWidth || !image.naturalHeight) return;
    fitWidth = Math.min(
      image.naturalWidth,
      canvas.clientWidth - 32,
      ((canvas.clientHeight - 32) * image.naturalWidth) / image.naturalHeight,
    );
    applyZoom(false);
  }
  image.addEventListener('load', fit);
  smaller.addEventListener('click', () => {
    index = Math.max(0, index - 1);
    applyZoom();
  });
  larger.addEventListener('click', () => {
    index = Math.min(levels.length - 1, index + 1);
    applyZoom();
  });
  get('figure-fit').addEventListener('click', () => {
    index = 0;
    fit();
  });
  get('close-figure').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    drag = undefined;
    delete canvas.dataset.dragging;
    opener?.focus({ preventScroll: true });
  });
  new ResizeObserver(() => {
    if (dialog.open) fit();
  }).observe(canvas);
  // Touch and trackpad scrolling stay native; mouse users can drag the enlarged canvas.
  canvas.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'mouse' || event.button !== 0 || index === 0)
      return;
    event.preventDefault();
    canvas.focus({ preventScroll: true });
    drag = {
      id: event.pointerId,
      x: event.clientX,
      y: event.clientY,
      left: canvas.scrollLeft,
      top: canvas.scrollTop,
    };
    canvas.setPointerCapture(event.pointerId);
    canvas.dataset.dragging = 'true';
  });
  canvas.addEventListener('pointermove', (event) => {
    if (!drag || drag.id !== event.pointerId) return;
    canvas.scrollLeft = drag.left + drag.x - event.clientX;
    canvas.scrollTop = drag.top + drag.y - event.clientY;
  });
  for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) {
    canvas.addEventListener(name, () => {
      drag = undefined;
      delete canvas.dataset.dragging;
    });
  }
  return (source: HTMLImageElement, button: HTMLButtonElement) => {
    opener = button;
    index = 0;
    fitWidth = 0;
    image.style.width = '';
    image.src = source.currentSrc || source.src;
    image.alt = source.alt;
    get<HTMLAnchorElement>('figure-original').href = image.src;
    get('figure-caption').textContent = source.alt;
    dialog.showModal();
    fit();
  };
}
