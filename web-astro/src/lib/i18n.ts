import editionData from './editions.json';
export type Locale = keyof typeof editionData;
export const editions = editionData;
export const locales = Object.keys(editions) as Locale[];
const catalogs = import.meta.glob<Record<string, string>>('./locales/*.json', {
  eager: true,
  import: 'default',
});
export function getMessages(locale: Locale): Record<string, string> {
  if (locale === 'en') return {};
  return catalogs[`./locales/${locale}.json`] ?? {};
}
export function translator(locale: Locale) {
  const messages = getMessages(locale);
  return (message: string) => messages[message] ?? message;
}
// Only the current edition's UI strings are delivered to the browser.
let currentMessages: Record<string, string> | undefined;
export function browserTranslator() {
  if (!currentMessages) {
    try {
      currentMessages = JSON.parse(
        document.getElementById('book-ui-messages')?.textContent ?? '{}',
      );
    } catch {
      currentMessages = {};
    }
  }
  return (message: string) => currentMessages?.[message] ?? message;
}
