"""Check Kindle resource rewriting independently from the installed browser."""
from zipfile import ZipFile

import pytest

pytest.importorskip("playwright.sync_api")
pytest.importorskip("lxml.etree")
import kindle_epub_patcher as patcher


def test_unannotated_math_and_source_text_survive(tmp_path, monkeypatch):
    original = tmp_path / "source.epub"
    converted = tmp_path / "result.epub"
    with ZipFile(original, "w") as epub:
        epub.writestr("mimetype", b"application/epub+zip")
        epub.writestr("META-INF/container.xml", '<container><rootfile full-path="B/book.opf"/></container>')
        epub.writestr("B/book.opf", f'<package xmlns="{patcher.OPF[1:-1]}"><manifest>'
                      '<item id="ch" properties="mathml" href="text/1.xhtml" media-type="application/xhtml+xml"/>'
                      '<item id="fig" href="fig.svg" media-type="image/svg+xml"/></manifest></package>')
        epub.writestr("B/fig.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        epub.writestr("B/text/1.xhtml", f'<html xmlns="{patcher.XHTML[1:-1]}"><body>'
                      f'<p>Before <math xmlns="{patcher.MATH[1:-1]}"><mi>x</mi></math> after.</p>'
                      '<img src="../fig.svg"/><code>fig.svg</code>'
                      '<a href="https://example.org/fig.svg">Source</a></body></html>')
    monkeypatch.setattr(patcher, "render", lambda page, markup: (b"PNG fixture", 16))
    patcher.convert(original, converted, None)
    with ZipFile(converted) as epub:
        chapter = patcher.xml(epub.read("B/text/1.xhtml"))
        formula, diagram = chapter.findall(".//{*}img")
        assert formula.get("alt") == "x"
        assert formula.tail == " after."
        assert diagram.get("src") == "../fig.svg.png"
        assert chapter.find(".//{*}code").text == "fig.svg"
        assert chapter.find(".//{*}a").get("href") == "https://example.org/fig.svg"
        assert epub.read("B/media/kindle-formula-1.png") == b"PNG fixture"
        assert epub.read("B/fig.svg.png") == b"PNG fixture"
