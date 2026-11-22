"""Generate homepage chapter cards from the manuscripts during MkDocs builds."""
from __future__ import annotations

import html
from html.parser import HTMLParser
from pathlib import Path
import re

import markdown as md

MARKER = "<!-- book-chapter-index -->"


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def heading_text(value: str) -> str:
    value = re.sub(r"\s*\{[^}]*\}\s*$", "", value)
    parser = PlainText()
    parser.feed(md.markdown(value))
    return "".join(parser.parts).strip()


def read_headings(source: Path) -> tuple[str, list[str]]:
    """Read real headings, excluding heading-like lines in fenced examples."""
    title = None
    sections = []
    fence = None
    for line in source.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            run = match[1]
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not line.strip()[len(run):].strip():
                fence = None
            continue
        if fence:
            continue
        match = re.match(r"^(#{1,2})\s+(.+?)(?:\s+#+)?\s*$", line)
        if match:
            text = heading_text(match[2])
            if match[1] == "#" and title is None:
                title = text
            elif match[1] == "##" and len(sections) < 3:
                sections.append(text)
    if not title:
        raise ValueError(f"Homepage source has no level-one heading: {source}")
    return title, sections


def chapter_order(nav: list) -> list[str]:
    chapters = []

    def visit(item):
        if isinstance(item, str):
            match = re.fullmatch(r"book/(chapter\d+)/(?:index\.md)", item)
            if match:
                chapters.append(match[1])
        elif isinstance(item, dict):
            for value in item.values():
                visit(value)
        elif isinstance(item, list):
            for value in item:
                visit(value)

    visit(nav)
    if not chapters or len(set(chapters)) != len(chapters):
        raise ValueError("Homepage requires unique chapter index paths in the MkDocs navigation")
    return chapters


def render_cards(root: Path, language: dict, chapters: list[str], *, translated: bool) -> str:
    prefix = language["prefix"].rstrip("/")
    suffix = language.get("suffix", "")
    relative = "../" if translated else ""
    cards = []
    for slug in ["introduction", *chapters, "afterword", "reference-answers"]:
        title, sections = read_headings(root / prefix / f"{slug}{suffix}.md")
        number = slug.removeprefix("chapter") if slug.startswith("chapter") else ""
        label = f"{number} · {title}" if number else title
        href = f"{relative}{prefix}/{slug}{suffix}/"
        description = " · ".join(sections)
        card = (f'<a class="exp-card" href="{html.escape(href, quote=True)}">\n'
                f'<span class="exp-title">{html.escape(label)}</span>\n')
        if description:
            card += f'<span class="exp-desc">{html.escape(description)}</span>\n'
        cards.append(card + "</a>")
    return '<div class="exp-grid">\n\n' + "\n\n".join(cards) + "\n\n</div>"


def on_page_markdown(markdown: str, page, config, **kwargs):
    """Expand the homepage template; never rewrite checked-in source files."""
    if MARKER not in markdown:
        return markdown
    source = page.file.src_uri
    match = re.fullmatch(r"index(?:\.([\w-]+))?\.md", source)
    if not match or markdown.count(MARKER) != 1:
        raise ValueError(f"Unexpected homepage marker in {source}")
    code = match[1] or "zh"
    root = Path(config["config_file_path"]).resolve().parent
    cards = render_cards(root, config["extra"]["languages"][code],
                         chapter_order(config["nav"]), translated=bool(match[1]))
    return markdown.replace(MARKER, cards)
