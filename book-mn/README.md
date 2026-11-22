# AI Agent-ийг гүнзгий ойлгох

Дизайны зарчим ба инженерчлэлийн практик. Зохиогч: Bojie Li. Монгол орчуулга: [ZERO1zx1](https://github.com/ZERO1zx1).

[中文](../README.md) · [English](../docs/en/README.md) · [Español](../docs/es/README.md) · [Bahasa Indonesia](../docs/id/README.md) · [العربية](../docs/ar/README.md) · [繁體中文（台灣）](../docs/zh-TW/README.md) · [Русский](../docs/ru/README.md) · [Tiếng Việt](../docs/vi/README.md) · [தமிழ்](../docs/ta/README.md) · [日本語](../docs/ja/README.md) · [Türkçe](../docs/tr/README.md) · [한국어](../docs/ko/README.md) · [Magyar](../docs/hu/README.md) · [עברית](../README.he.md) · [Português (Brasil)](../README.ptbr.md) · **Монгол**

> **1.4 хувилбартай харьцуулбал:** 2.0 болон 3.0 хувилбарт хуучин 4-р бүлгийн асинхрон харилцан үйлчлэл, 9-р бүлгийн мультимодал агентын материалыг нэгтгэн шинэ 6-р бүлэг болгосон. Өмнөх 6, 7, 8-р бүлэг одоо 7, 8, 9-р бүлэг болсон.

**Цахим ном татах:** [PDF](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-mn.pdf) · [EPUB](https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-mn.epub)

## Агуулга

- [Танилцуулга](introduction.md)
- [1. AI Агентуудтай ажиллаж эхлэх нь](chapter1.md)
- [2. Контекстийн инженерчлэл](chapter2.md)
- [3. Хэрэглэгч Санах ой болон Мэдлэгийн сан](chapter3.md)
- [4. Tools](chapter4.md)
- [5. Agent код бичих болон код үүсгэх](chapter5.md)
- [6. Харилцан үйлчлэл: Ажиглалт болон үйл ажиллагааны орон зайг өргөжүүлэх нь](chapter6.md)
- [7. Agents-г үнэлэх](chapter7.md)
- [8. Model Training-ийн дараах](chapter8.md)
- [9. Agents-ийн тасралтгүй хувьсал](chapter9.md)
- [10. Олон Agent Хамтын ажиллагаа](chapter10.md)
- [Төгсгөлийн үг: Агент = LLM + Контекст + Хэрэгслүүд томьёонд эргэн очих нь](afterword.md)
- [Бодох асуултуудын жишиг хариулт](reference-answers.md)

## PDF үүсгэх

Репозиторийн үндсэн хавтсаас дараах командыг ажиллуулна. Pandoc, XeLaTeX, ElegantBook, GNU FreeFont болон librsvg хэрэгтэй.

```sh
bash book-mn/build_pdf.sh
bash build_epub.sh mn
```

PDF нь `book-mn/AI-Agents-in-Depth-Bojie-Li-v3.0-mn.pdf` файлд үүснэ.
