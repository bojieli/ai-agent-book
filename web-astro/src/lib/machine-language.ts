import { withBase } from './site-path.mjs';
import config from './machine-translation.json' with { type: 'json' };

export function machineLanguage(url: URL, base?: string) {
  if (
    url.pathname !== withBase('/en/', base) &&
    !url.pathname.startsWith(withBase('/book-en/', base))
  )
    return undefined;
  return config.languages.find(
    (language) => language.locale === url.searchParams.get('translate'),
  );
}
