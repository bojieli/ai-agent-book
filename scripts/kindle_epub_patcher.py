"""Build a reflowable Kindle copy of a Pandoc EPUB using a local Chromium renderer."""
import argparse
import base64
import posixpath
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from lxml import etree as ET
from playwright.sync_api import sync_playwright

OPF = "{http://www.idpf.org/2007/opf}"
XHTML = "{http://www.w3.org/1999/xhtml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
CSS = b"""
/* Reflow code and tables on narrow Kindle screens. */
body { overflow-wrap: break-word; }
table { display: table; max-width: 100%; }
pre, pre > code.sourceCode { white-space: pre-wrap; overflow-wrap: anywhere; }
pre > code.sourceCode > span { display: inline; }
img.kindle-math { display: inline; vertical-align: middle; max-width: 100%; height: auto; }
img.kindle-display { display: block; margin: 0.5em auto; }
"""


def xml(data):
    return ET.fromstring(data, ET.XMLParser(resolve_entities=False, no_network=True))


def member(document, href):
    return posixpath.normpath(posixpath.join(posixpath.dirname(document), unquote(href)))


def render(page, markup):
    page.set_content('<body style="margin:0;background:white"><span id="figure" '
                     'style="display:inline-block;width:max-content;line-height:normal">'
                     + markup + '</span></body>')
    figure = page.locator("#figure")
    image = figure.locator("img")
    if image.count():
        image.evaluate("img => img.decode()")
    size = figure.bounding_box()
    if not size or min(size["width"], size["height"]) <= 0:
        raise ValueError("Could not measure the illustration")
    return figure.screenshot(), size["width"]


def convert(source, destination, page):
    with ZipFile(source) as original:
        entries = {name: original.read(name) for name in original.namelist()}
    package = xml(entries["META-INF/container.xml"]).find(".//{*}rootfile").get("full-path")
    opf = xml(entries[package])
    manifest = opf.find(OPF + "manifest")
    svg_paths = {}
    for item in manifest.findall(OPF + "item"):
        href = item.get("href")
        path = member(package, href)
        if item.get("media-type") == "image/svg+xml":
            # Keep the original filename stem even when a same-named PNG already exists.
            target = path + ".png"
            if target in entries:
                raise ValueError(f"PNG path already occupied: {target}")
            data = base64.b64encode(entries[path]).decode("ascii")
            entries[target], _ = render(page, f'<img src="data:image/svg+xml;base64,{data}">')
            del entries[path]
            item.set("href", href + ".png")
            item.set("media-type", "image/png")
            svg_paths[path] = target
        elif item.get("media-type") == "text/css":
            entries[path] += CSS

    formula_cache = {}
    reserved_ids = {item.get("id") for item in manifest}
    for item in manifest.findall(OPF + "item"):
        if item.get("media-type") != "application/xhtml+xml":
            continue
        path = member(package, item.get("href"))
        doc = xml(entries[path])
        for element in doc.iter():
            for attr in ("src", "href", "{http://www.w3.org/1999/xlink}href", "data"):
                value = element.get(attr)
                if not value:
                    continue
                link = urlsplit(value)
                if not link.scheme and not link.netloc and member(path, link.path) in svg_paths:
                    element.set(attr, link._replace(path=link.path + ".png").geturl())

        for math in doc.iter(MATH + "math"):
            markup = ET.tostring(math, encoding="unicode", with_tail=False)
            if markup not in formula_cache:
                key = f"kindle-formula-{len(formula_cache) + 1}"
                href = f"media/{key}.png"
                target = member(package, href)
                if target in entries or key in reserved_ids:
                    raise ValueError(f"Formula name already in use: {key}")
                entries[target], width = render(page, markup)
                ET.SubElement(manifest, OPF + "item", id=key, href=href,
                              attrib={"media-type": "image/png"})
                formula_cache[markup] = target, width
            target, width = formula_cache[markup]
            image = ET.Element(XHTML + "img")
            annotation = math.find('.//{*}annotation[@encoding="application/x-tex"]')
            description = math.get("alttext") or (
                annotation.text if annotation is not None else "".join(math.itertext())
            )
            if not description:
                raise ValueError(f"Formula has no accessible text in {path}")
            image.set("alt", description)
            image.set("src", posixpath.relpath(target, posixpath.dirname(path)))
            image.set("class", "kindle-math kindle-display" if math.get("display") == "block" else "kindle-math")
            image.set("style", f"width: {width / 16:.3f}em")
            if math.get("id"):
                image.set("id", math.get("id"))
            image.tail = math.tail
            math.getparent().replace(math, image)
        properties = item.get("properties", "").split()
        if "mathml" in properties:
            properties.remove("mathml")
            if properties:
                item.set("properties", " ".join(properties))
            else:
                del item.attrib["properties"]
        entries[path] = ET.tostring(doc.getroottree(), encoding="utf-8", xml_declaration=True)
    entries[package] = ET.tostring(opf, encoding="utf-8", xml_declaration=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as output:
        output.writestr("mimetype", entries.pop("mimetype"), compress_type=ZIP_STORED)
        for path, content in entries.items():
            output.writestr(path, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    output = args.source.with_name(args.source.stem + "-kindle.epub")
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(device_scale_factor=2, java_script_enabled=False, offline=True)
        candidate = Path(tmp) / output.name
        convert(args.source, candidate, page)
        browser.close()
        candidate.replace(output)
    print(output)


if __name__ == "__main__":
    main()
