export interface ReadingPosition {
  version: 1;
  chapter: string;
  section: string;
  sectionTitle: string;
  offset: number;
  progress: number;
}
export const positionKey = (chapter: string) =>
  `book-reading-position:${chapter}`;
export function parsePosition(
  raw: string | null,
  chapter: string,
): ReadingPosition | null {
  try {
    const p = JSON.parse(raw ?? 'null');
    if (
      !p ||
      p.version !== 1 ||
      p.chapter !== chapter ||
      typeof p.section !== 'string' ||
      p.section.length > 500 ||
      typeof p.sectionTitle !== 'string' ||
      p.sectionTitle.length > 500 ||
      !Number.isFinite(p.offset) ||
      p.offset < 0 ||
      p.offset > 1 ||
      !Number.isFinite(p.progress) ||
      p.progress < 0 ||
      p.progress > 1
    )
      return null;
    return p;
  } catch {
    return null;
  }
}
export function loadPosition(chapter: string): ReadingPosition | null {
  try {
    return parsePosition(localStorage.getItem(positionKey(chapter)), chapter);
  } catch {
    return null;
  }
}
