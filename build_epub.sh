#!/usr/bin/env bash
# Build EPUB 3 editions from the Markdown sources.
# Usage: ./build_epub.sh [all|zh-CN|zh-TW|en|ta|vi|ja]
# Note: `all` does NOT include ja yet — the Japanese PDF/EPUB pipeline is not
# validated in CI. Build it explicitly with `./build_epub.sh ja` once the
# Japanese fonts and `book-ja/build_pdf.sh` output are confirmed to work.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SELECTION="${1:-all}"

for command in pandoc pdftoppm python3; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "Error: $command is required." >&2
        exit 1
    fi
done

case "$SELECTION" in
    all|zh-CN|zh-TW|en|ta|vi|ja) ;;
    *)
        echo "Usage: $0 [all|zh-CN|zh-TW|en|ta|vi|ja]" >&2
        exit 2
        ;;
esac

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ai-agent-book-epub.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

build_edition() {
    local language="$1"
    local directory title author pdf output title_label toc_label
    local -a chapters

    case "$language" in
        zh-CN)
            directory="book"
            title="深入理解 AI Agent：设计原理与工程实践"
            author="李博杰"
            pdf="深入理解-AI-Agent-李博杰-v1.2.pdf"
            output="深入理解-AI-Agent-李博杰-v1.2.epub"
            title_label="扉页"
            toc_label="目录"
            chapters=(introduction.md chapter{1..10}.md afterword.md)
            ;;
        zh-TW)
            directory="book-zhtw"
            title="深入理解 AI Agent：設計原理與工程實踐"
            author="李博杰；台灣正體翻譯：tigercosmos"
            pdf="深入理解-AI-Agent-李博杰-v1.2-zhtw.pdf"
            output="深入理解-AI-Agent-李博杰-v1.2-zhtw.epub"
            title_label="扉頁"
            toc_label="目錄"
            chapters=(introduction.zhtw.md chapter{1..10}.zhtw.md afterword.zhtw.md)
            ;;
        en)
            directory="book-en"
            title="AI Agents in Depth: Design Principles and Engineering Practice"
            author="Bojie Li; English translation: Devaraj"
            pdf="AI-Agents-in-Depth-Bojie-Li-v1.2.pdf"
            output="AI-Agents-in-Depth-Bojie-Li-v1.2.epub"
            title_label="Title Page"
            toc_label="Table of Contents"
            chapters=(introduction.md chapter{1..10}.md afterword.md)
            ;;
        ta)
            directory="book-ta"
            title="AI Agents ஆழத்தில்: வடிவமைப்பு கோட்பாடுகள் மற்றும் பொறியியல் நடைமுறைகள்"
            author="Bojie Li; தமிழ் மொழிபெயர்ப்பு: Devaraj"
            pdf="AI-Agents-in-Depth-Bojie-Li-v1.2-ta.pdf"
            output="AI-Agents-in-Depth-Bojie-Li-v1.2-ta.epub"
            title_label="தலைப்புப் பக்கம்"
            toc_label="பொருளடக்கம்"
            chapters=(introduction.ta.md chapter{1..10}.ta.md afterword.ta.md)
            ;;
        vi)
            directory="book-vi"
            title="Hiểu sâu về AI Agent: Nguyên lý thiết kế và thực hành kỹ thuật"
            author="Lý Bác Kiệt; bản dịch tiếng Việt: Toàn Nguyễn"
            pdf="AI-Agents-in-Depth-Bojie-Li-v1.2-vi.pdf"
            output="AI-Agents-in-Depth-Bojie-Li-v1.2-vi.epub"
            title_label="Trang tiêu đề"
            toc_label="Mục lục"
            chapters=(introduction.vi.md glossary.vi.md chapter{1..10}.vi.md afterword.vi.md)
            ;;
        ja)
            directory="book-ja"
            title="AI Agent 徹底解説：設計原理とエンジニアリング実践"
            author="李博杰；日本語訳：Ikko Eltociear Ashimine"
            pdf="AI-Agents-in-Depth-Bojie-Li-v1.2-ja.pdf"
            output="AI-Agents-in-Depth-Bojie-Li-v1.2-ja.epub"
            title_label="扉"
            toc_label="目次"
            chapters=(introduction.ja.md chapter{1..10}.ja.md afterword.ja.md)
            ;;
    esac

    local edition_dir="$ROOT/$directory"
    local chapter
    for chapter in "${chapters[@]}" "$pdf"; do
        if [ ! -f "$edition_dir/$chapter" ]; then
            echo "Error: $directory/$chapter not found." >&2
            exit 1
        fi
    done

    local cover="$TMP_DIR/cover-$language.jpg"
    pdftoppm -f 1 -singlefile -jpeg -r 160 \
        "$edition_dir/$pdf" "${cover%.jpg}"

    echo "Building $language EPUB..."
    (
        cd "$edition_dir"
        pandoc "${chapters[@]}" \
            -o "$output" \
            --from markdown+lists_without_preceding_blankline \
            --to epub3 \
            --standalone \
            --toc \
            --toc-depth=3 \
            --number-sections \
            --mathml \
            --split-level=1 \
            --highlight-style=kate \
            --css="$ROOT/epub.css" \
            --epub-cover-image="$cover" \
            --metadata title="$title" \
            --metadata author="$author" \
            --metadata lang="$language" \
            --metadata identifier="https://github.com/bojieli/ai-agent-book#$language"
    )

    python3 "$ROOT/flatten_epub_toc.py" \
        "$edition_dir/$output" "$title_label" "$toc_label"

    if command -v epubcheck >/dev/null 2>&1; then
        epubcheck "$edition_dir/$output"
    else
        echo "Built $directory/$output (install epubcheck to validate it)."
    fi
}

if [ "$SELECTION" = "all" ]; then
    for language in zh-CN zh-TW en ta vi; do
        build_edition "$language"
    done
else
    build_edition "$SELECTION"
fi
