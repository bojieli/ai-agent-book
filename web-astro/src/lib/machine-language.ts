import config from './machine-translation.json' with { type: 'json' };

export function machineLanguage(url: URL) {
  if (url.pathname !== '/en/' && !url.pathname.startsWith('/book-en/'))
    return undefined;
  return config.languages.find(
    (language) => language.locale === url.searchParams.get('translate'),
  );
}
