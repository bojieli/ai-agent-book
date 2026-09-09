import { availableChapters } from './available-chapters.mjs';
import { editions, translator, type Locale } from './i18n';
const chapterSources = import.meta.glob<string>(
  ['../../../book/chapter*.md', '../../../book-*/chapter*.md'],
  {
    query: '?raw',
    import: 'default',
    eager: true,
  },
);

export const repo = 'https://github.com/bojieli/ai-agent-book';
export const originalSite = 'https://bojieli.github.io/ai-agent-book';
const descriptions = [
  'The model, the context, the tools—and the loop that brings them together.',
  'Build the working context that makes an agent effective.',
  'Connect agents to what they know and what they remember.',
  'Give agents reliable interfaces to act on the world.',
  'Use code as a tool for creating new capabilities.',
  'Extend agents across voice, vision, interfaces, and time.',
  'Measure behavior, compare systems, and learn from failures.',
  'Understand how supervised learning and reinforcement learning shape models.',
  'Turn execution experience into lasting improvements.',
  'Coordinate agents, share context, and divide complex work.',
];
export function getBook(locale: Locale, chapterNumber = 1) {
  const edition = editions[locale];
  const t = translator(locale);
  const chapterPath = edition.chapter;
  const chapters = Array.from({ length: 10 }, (_, index) => {
    const number = index + 1;
    const source =
      chapterSources[
        `../../../${edition.directory}/chapter${number}${edition.suffix}.md`
      ];
    const title = source.match(/^#\s+(.+)$/m)?.[1] ?? `Chapter ${number}`;
    return {
      number,
      label: String(number).padStart(2, '0'),
      title,
      description: t(descriptions[index]),
      href: availableChapters.includes(number)
        ? `/${edition.directory}/chapter${number}${edition.suffix}/`
        : `${originalSite}/${edition.directory}/chapter${number}${edition.suffix}/`,
      external: !availableChapters.includes(number),
    };
  });
  const firstChapter =
    chapterSources[
      `../../../${edition.directory}/chapter${chapterNumber}${edition.suffix}.md`
    ];
  // CJK prose has no spaces between words; estimate characters and Latin words separately.
  const cjk =
    firstChapter.match(/[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]/g)?.length ??
    0;
  const words = firstChapter
    .replace(/[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]/g, ' ')
    .split(/\s+/)
    .filter(Boolean).length;
  const readingMinutes = Math.max(1, Math.ceil(cjk / 400 + words / 220));
  return { chapters, chapterPath, readingMinutes };
}
