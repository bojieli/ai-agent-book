import editions from './editions.json' with { type: 'json' };

export function sourceEdition(path = '') {
  const directory = path.replaceAll('\\', '/').split('/').at(-2);
  const entry = Object.entries(editions).find(
    ([, edition]) => edition.directory === directory,
  );
  if (!entry)
    throw new Error(`Unknown book edition for Markdown source: ${path}`);
  return { locale: entry[0], ...entry[1] };
}
