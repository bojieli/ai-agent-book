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

export const originalFigureLabels = {
  en: 'Original figure',
  'zh-CN': '原始图片',
  'zh-TW': '原始圖片',
  ar: 'الصورة الأصلية',
  es: 'Figura original',
  he: 'האיור המקורי',
  hu: 'Eredeti ábra',
  id: 'Gambar asli',
  ja: '元の図',
  ko: '원본 그림',
  'pt-BR': 'Figura original',
  ru: 'Исходный рисунок',
  ta: 'அசல் படம்',
  tr: 'Özgün görsel',
  vi: 'Hình gốc',
};
