#!/bin/bash

# Номыг бүхэлд нь нэг PDF файл болгон бүтээх.
# Загвар: ElegantBook
# Өнгөний сэдэв: Ногоовтор цэнхэр (cyan)
#
# Шаардлагатай зүйлс:
#   - pandoc
#   - xelatex
#   - ElegantBook class
#   - rsvg-convert (librsvg)
#   - pdfinfo (хуудасны тоог тодорхойлоход)
#   - Python 3
#
# Фонт:
#   macOS: Menlo / Arial Unicode MS
#   Linux: DejaVu Sans/Mono болон Noto CJK
#
# Linux дээр нөөц фонт руу автоматаар шилжинэ.
# Дэлгэрэнгүйг preamble.tex файлаас үзнэ үү.
#
# Ашиглах заавар:
#   cd book
#   bash build_pdf.sh
#
# Тайлбар:
# Бүлэг болон дэд хэсгийн дугаарыг document class автоматаар үүсгэнэ.
# Эх Markdown файлуудын гарчигт дугаарыг гараар бичээгүй.
# Дугаарлалтыг арилгасан өөрчлөлтийг git history хэсгээс үзнэ үү.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"


# ──────────────────────────────────────────────────────────────
# 1. Ажиллах орчны тохируулга
# ──────────────────────────────────────────────────────────────

# macOS дээр сөрөг нөлөөгүй, Linux/TeX Live дээр шаардлагатай.


# 1.1. XeTeX-ийн нэмэлт санах ойн тохиргоо
#
# Энэ ном маш том хэмжээтэй тул PDF-ийн хуудас боловсруулах үед
# XeTeX-ийн үндсэн санах ойн хязгаарыг давж болзошгүй.
#
# Болзошгүй алдаа:
# "TeX capacity exceeded ... [main memory size=5000000]"
#
# main_memory утга нь формат үүсгэх үед урьдчилан тогтоогддог.
#
# Харин extra_mem_top болон extra_mem_bot нь аль хэдийн үүссэн
# форматын нэмэлт санах ойн хэмжээг ажиллах үед тохируулах
# боломж олгодог.
#
# Иймээс xelatex форматыг дахин бүтээхийн оронд
# санах ойн нэмэлт хэмжээг энд тохируулж байна.

export extra_mem_top=8000000
export extra_mem_bot=8000000


# 1.2. METAFONT-оор TFM файл автоматаар үүсгэхийг идэвхгүй болгох
#
# Зөвхөн macOS дээр байдаг monospace фонт (Menlo)-ыг
# preamble.tex файл дотор \IfFontExistsTF ашиглан шалгадаг.
#
# Menlo фонт байхгүй системд kpathsea нь DejaVu Sans Mono
# нөөц фонт руу шилжихээс өмнө METAFONT ажиллуулж,
# Menlo.tfm файлыг үүсгэхийг оролдож болзошгүй.
#
# Энэ үйлдэл удаан, олон шаардлагагүй мэдээлэл хэвлэдэг
# бөгөөд эцэстээ амжилтгүй болдог.
#
# TFM файлыг ажиллах явцад автоматаар үүсгэхийг идэвхгүй болгосноор
# фонтын шалгалт шууд "not found" үр дүн буцааж,
# зөв нөөц фонт руу шилжих боломжтой болно.

export MKTEXTFM=0


# ──────────────────────────────────────────────────────────────
# 2. Гаралтын PDF файлын нэр
# ──────────────────────────────────────────────────────────────

OUT="AI-Agents-in-Depth-Bojie-Li-v2.0.pdf"


# ──────────────────────────────────────────────────────────────
# 3. Номын бүлгүүд
# ──────────────────────────────────────────────────────────────

CHAPTERS=(
    introduction.md
    chapter1.md
    chapter2.md
    chapter3.md
    chapter4.md
    chapter5.md
    chapter6.md
    chapter7.md
    chapter8.md
    chapter9.md
    chapter10.md
    afterword.md
)


# ──────────────────────────────────────────────────────────────
# 4. Бүх бүлгийн файл байгаа эсэхийг шалгах
# ──────────────────────────────────────────────────────────────

for ch in "${CHAPTERS[@]}"; do
    if [ ! -f "$ch" ]; then
        echo "Алдаа: $ch файл олдсонгүй" >&2
        exit 1
    fi
done


# ──────────────────────────────────────────────────────────────
# 5. PDF файл үүсгэх
# ──────────────────────────────────────────────────────────────

echo "Нийт ${#CHAPTERS[@]} файлаас PDF үүсгэж байна..."

pandoc "${CHAPTERS[@]}" \
    -o "$OUT" \
    --from=markdown+lists_without_preceding_blankline \
    --pdf-engine=xelatex \
    --lua-filter=crossref.lua \
    --lua-filter=experiment_box.lua \
    --toc \
    --toc-depth=3 \
    --number-sections \
    -V documentclass=elegantbook \
    -V classoption=lang=en \
    -V classoption=cyan \
    -V classoption=device=normal \
    -V author="Bojie Li" \
    --metadata title-meta="AI Agents in Depth: Design Principles and Engineering Practice" \
    --metadata author-meta="Bojie Li (English translation: Devaraj)" \
    -H preamble.tex \
    --include-before-body=cover.tex \
    --highlight-style=kate \
    --columns=80 \
    2>&1


# ──────────────────────────────────────────────────────────────
# 6. Үүсгэсэн PDF файлыг шалгах
# ──────────────────────────────────────────────────────────────

if [ -f "$OUT" ]; then

    # PDF файлын хэмжээг тодорхойлох.
    SIZE=$(du -h "$OUT" | cut -f1)

    # PDF файлын хуудасны тоог тодорхойлох.
    PAGES=$(python3 - "$OUT" <<'PY'
import subprocess
import re
import sys

pdf_path = sys.argv[1]

try:
    result = subprocess.run(
        ["pdfinfo", pdf_path],
        capture_output=True,
        text=True,
        check=False
    )

    match = re.search(
        r"Pages:\s+(\d+)",
        result.stdout
    )

    print(match.group(1) if match else "?")

except (OSError, subprocess.SubprocessError):
    print("?")
PY
)

    echo ""
    echo "Дууслаа: $OUT ($SIZE, $PAGES хуудас)"

else

    echo "Алдаа: PDF файл үүсгэж чадсангүй" >&2
    exit 1

fi