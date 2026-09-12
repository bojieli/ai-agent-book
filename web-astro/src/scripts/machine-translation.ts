import { machineLanguage } from '../lib/machine-language';
import config from '../lib/machine-translation.json';

type Pass = {
  requests: number;
  done: number;
  sourceSeen: boolean;
  sourceDone: boolean;
};
// The lifecycle signatures follow the pinned library integration in extras/auto-translate.js.
interface Translator {
  selectLanguageTag: { show: boolean };
  service: { use(name: string): void };
  language: { setLocal(name: string): void };
  ignore: { tag: string[]; class: string[] };
  changeLanguage(name: string): void;
  lifecycle: {
    execute: {
      start: Array<(data: { uuid: string }) => void>;
      translateNetworkAfter: Array<
        (data: { uuid: string; result: number; from: string }) => void
      >;
      renderFinish: Array<(uuid: string) => void>;
      finally: Array<(data: { state: number }) => void>;
    };
  };
}

export function initMachineTranslation() {
  const url = new URL(location.href);
  const language = machineLanguage(url);
  // Explicit English URLs are the source. Maintained editions never load the service.
  if (!language || document.documentElement.lang !== 'en') return;
  const host = document.querySelector('#main-content');
  if (!host) return;
  const notice = document.createElement('aside');
  notice.className = 'machine-translation-notice';
  notice.dir = 'ltr';
  notice.lang = 'en';
  notice.setAttribute('role', 'note');
  const warning = document.createElement('strong');
  warning.textContent = `${language.label} — Machine translation · Not vetted`;
  const status = document.createElement('p');
  status.setAttribute('role', 'status');
  const details = document.createElement('p');
  details.textContent =
    'Automatically translated from English; not reviewed for accuracy. Figures and code remain in English. Highlights, notes, and saved reading position are unavailable in this view.';
  const off = document.createElement('a');
  url.searchParams.delete('translate');
  off.href = url.href;
  off.textContent = 'Read the English edition';
  notice.append(warning, status, details, off);
  host.prepend(notice);
  document.documentElement.dataset.machineTranslation = 'true';
  // Avoid saving translated quotes under the English edition's annotation scope.
  const label = document.querySelector('.current-language');
  if (label) label.textContent = `${language.label} (MT)`;
  document
    .querySelector('.language-picker a[aria-current]')
    ?.removeAttribute('aria-current');
  document
    .querySelector(`[data-machine-language="${language.name}"]`)
    ?.setAttribute('aria-current', 'page');

  // Keep the selected fallback while following links within the English edition.
  document.querySelectorAll<HTMLAnchorElement>('a[href]').forEach((link) => {
    if (link.closest('.language-picker, .machine-translation-notice')) return;
    const target = new URL(link.href);
    if (
      target.origin === location.origin &&
      (target.pathname.startsWith('/book-en/') || target.pathname === '/en/')
    ) {
      target.searchParams.set('translate', language.locale);
      link.href = target.href;
    }
  });
  let timer: ReturnType<typeof setTimeout>;
  const setState = (state: 'pending' | 'ok' | 'failed') => {
    notice.dataset.state = state;
    status.textContent =
      state === 'pending'
        ? 'Translating…'
        : state === 'ok'
          ? 'Machine translation applied. It may contain errors.'
          : 'Translation could not be completed. Some or all text may still be English.';
    document.documentElement.lang = state === 'ok' ? language.locale : 'en';
    document.documentElement.dir =
      state === 'ok' && language.dir === 'rtl' ? 'rtl' : 'ltr';
  };
  const armTimer = () => {
    clearTimeout(timer);
    timer = setTimeout(() => setState('failed'), config.failureTimeoutMs);
  };
  setState('pending');
  armTimer();
  const script = document.createElement('script');
  script.src = config.cdn;
  script.integrity = config.integrity;
  script.crossOrigin = 'anonymous';
  script.onerror = () => {
    notice.dataset.failure = 'library-load';
    clearTimeout(timer);
    setState('failed');
  };
  script.onload = () => {
    try {
      const translate = (window as unknown as { translate: Translator })
        .translate;
      translate.selectLanguageTag.show = false;
      translate.service.use(config.service);
      translate.language.setLocal(config.sourceLanguage);
      translate.ignore.tag.push('pre', 'code', 'svg');
      translate.ignore.class.push(
        'machine-translation-notice',
        'language-picker',
        'code-toolbar',
        'reader-controls',
        'reading-reminder',
        'highlights-panel',
        'mermaid',
        'arithmatex',
        'katex',
      );
      const passes = new Map<string, Pass>();
      const cycle = translate.lifecycle.execute;
      cycle.start.push((data) => {
        passes.set(data.uuid, {
          requests: 0,
          done: 0,
          sourceSeen: false,
          sourceDone: false,
        });
        setState('pending');
        armTimer();
      });
      cycle.translateNetworkAfter.push((data) => {
        const pass = passes.get(data.uuid);
        if (!pass) return;
        pass.requests++;
        if (data.result === 1) pass.done++;
        if (data.from === config.sourceLanguage) {
          pass.sourceSeen = true;
          if (data.result === 1) pass.sourceDone = true;
        }
        armTimer();
      });
      cycle.renderFinish.push((uuid) => {
        const pass = passes.get(uuid);
        passes.delete(uuid);
        clearTimeout(timer);
        const failed =
          pass &&
          pass.requests > 0 &&
          (pass.sourceSeen ? !pass.sourceDone : pass.done === 0);
        setState(failed ? 'failed' : 'ok');
      });
      cycle.finally.push((data) => {
        if (data.state === 5) {
          clearTimeout(timer);
          setState('ok');
        }
      });
      translate.changeLanguage(language.name);
    } catch (error) {
      notice.dataset.failure =
        error instanceof Error ? error.message : 'initialization';
      clearTimeout(timer);
      setState('failed');
    }
  };
  document.head.append(script);
}
