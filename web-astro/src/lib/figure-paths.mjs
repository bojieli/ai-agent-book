// Originals retain their source paths; presentation assets have distinct URLs.
export function figurePaths(directory, image) {
  const name = image.replace(/^images\//, '').replace(/\.[^.]+$/, '');
  const base = `/figures/book/${directory}/${name}`;
  return {
    original: `/${directory}/${image}`,
    light: `${base}-light.svg`,
    dark: `${base}-dark.svg`,
  };
}

export const sourceFigureLabels = {
  en: 'Source figure',
  'zh-CN': '来源图',
  'zh-TW': '來源圖',
  ar: 'الشكل المصدر',
  es: 'Figura de origen',
  he: 'איור המקור',
  hu: 'Forrásábra',
  id: 'Gambar sumber',
  ja: '出典の図',
  ko: '출처 그림',
  'pt-BR': 'Figura de origem',
  ru: 'Исходный рисунок',
  ta: 'மூலப் படம்',
  tr: 'Kaynak şekil',
  vi: 'Hình nguồn',
};
