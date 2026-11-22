from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from homepage_index import MARKER, chapter_order, on_page_markdown, read_headings, render_cards

ROOT = Path(__file__).resolve().parents[1]


def test_every_homepage_uses_current_manuscript_titles_and_valid_links():
    # The lightweight registry CI does not install site-build dependencies.
    yaml = pytest.importorskip("yaml")
    config = yaml.load((ROOT / 'mkdocs.yml').read_text(), Loader=yaml.BaseLoader)
    config['config_file_path'] = str(ROOT / 'mkdocs.yml')
    for home in [ROOT / 'index.md', *ROOT.glob('index.*.md')]:
        page = SimpleNamespace(file=SimpleNamespace(src_uri=home.name))
        rendered = on_page_markdown(home.read_text(), page, config)
        code = home.name.split('.')[1] if home.name != 'index.md' else 'zh'
        language = config['extra']['languages'][code]
        assert MARKER not in rendered
        assert rendered.count('class="exp-card"') == 13
        for number in range(1, 11):
            source = ROOT / language['prefix'] / f"chapter{number}{language.get('suffix', '')}.md"
            title, _ = read_headings(source)
            import html
            assert html.escape(f'{number} · {title}') in rendered
            relative = '../' if code != 'zh' else ''
            assert f'href="{relative}{language["prefix"]}chapter{number}{language.get("suffix", "")}/"' in rendered


def test_manuscript_edit_and_navigation_order_flow_into_cards(tmp_path):
    book = tmp_path / 'book-test'
    book.mkdir()
    for slug in ['introduction', 'chapter1', 'chapter2', 'afterword', 'reference-answers']:
        (book / f'{slug}.xx.md').write_text(f'# {slug}\n\n## Before\n')
    nav = [{'Second': ['book/chapter2/index.md']}, {'First': ['book/chapter1/index.md']}]
    order = chapter_order(nav)
    language = {'prefix': 'book-test/', 'suffix': '.xx'}
    before = render_cards(tmp_path, language, order, translated=True)
    (book / 'chapter2.xx.md').write_text('# Updated & **clear**\n\n## New topic\n')
    after = render_cards(tmp_path, language, order, translated=True)
    assert '2 · chapter2' in before
    assert '2 · Updated &amp; clear' in after
    assert 'New topic' in after
    assert after.index('2 · Updated') < after.index('1 · chapter1')
    assert 'href="../book-test/chapter2.xx/"' in after


def test_headings_ignore_code_and_strip_inline_markup(tmp_path):
    source = tmp_path / 'chapter.md'
    source.write_text('# A `tool` & **context**\n\n```python\n# fake\n## fake section\n```\n\n## [Real](target) {#anchor}\n')
    assert read_headings(source) == ('A tool & context', ['Real'])


def test_missing_heading_and_duplicate_chapters_fail(tmp_path):
    source = tmp_path / 'chapter.md'
    source.write_text('No title\n')
    with pytest.raises(ValueError, match='level-one'):
        read_headings(source)
    with pytest.raises(ValueError, match='unique'):
        chapter_order(['book/chapter1/index.md', 'book/chapter1/index.md'])


def test_non_homepage_is_unchanged():
    assert on_page_markdown('# Chapter', None, {}) == '# Chapter'
