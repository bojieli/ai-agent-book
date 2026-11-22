"""Check Kindle resource rewriting independently from the installed browser."""
from zipfile import ZipFile

import pytest

pytest.importorskip("playwright.sync_api")
pytest.importorskip("lxml.etree")
from scripts import kindle_epub_patcher as patcher


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


@pytest.mark.parametrize("other_figure", [False, True])
def test_pandoc_cover_exposes_raster_and_preserves_manifest(tmp_path, other_figure):
    source, result = tmp_path / "original.epub", tmp_path / "reader.epub"
    extra = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>' if other_figure else ""
    with ZipFile(source, "w") as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr("META-INF/container.xml", '<container><rootfile full-path="EPUB/content.opf"/></container>')
        z.writestr("EPUB/content.opf", f'<package xmlns="{patcher.OPF[1:-1]}"><manifest>'
                   '<item id="cover" href="text/cover.xhtml" media-type="application/xhtml+xml" properties="svg scripted"/>'
                   '<item id="jpeg" href="media/cover%20image.jpg" properties="cover-image" media-type="image/jpeg"/>'
                   '</manifest><spine><itemref idref="cover"/></spine></package>')
        z.writestr("EPUB/media/cover image.jpg", b"unmodified raster")
        z.writestr("EPUB/text/cover.xhtml", f'<html xmlns="{patcher.XHTML[1:-1]}"><head><title>书名</title></head>'
                   '<body><div id="cover-image"><svg xmlns="http://www.w3.org/2000/svg" id="anchor" viewBox="0 0 100 200">'
                   '<image xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="../media/cover%20image.jpg"/>'
                   f'</svg>after</div>{extra}</body></html>')
    patcher.convert(source, result, None)
    with ZipFile(result) as z:
        doc = patcher.xml(z.read("EPUB/text/cover.xhtml"))
        img = doc.find(f".//{patcher.XHTML}img")
        assert (img.get("src"), img.get("alt"), img.get("id"), img.tail) == (
            "../media/cover%20image.jpg", "书名", "anchor", "after")
        assert z.read("EPUB/media/cover image.jpg") == b"unmodified raster"
        assert len(doc.findall(f".//{patcher.SVG}svg")) == int(other_figure)
        package = patcher.xml(z.read("EPUB/content.opf"))
        assert package.find('.//{*}item[@id="cover"]').get("properties").split() == (
            ["svg", "scripted"] if other_figure else ["scripted"])
        assert package.find('.//{*}item[@id="jpeg"]').get("properties") == "cover-image"
        assert package.find(".//{*}itemref").get("idref") == "cover"
