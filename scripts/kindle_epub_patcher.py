"""
# Amazon Kindle EPUB Reflowable Layout Patcher
#
# This script processes a Pandoc-generated EPUB file to ensure strict compatibility with Amazon's Send-to-Kindle (KFX) reflowable format.
# 1. Replaces MathML tags with high-res PNG images via CodeCogs API, as Kindle rejects MathML.
# 2. Converts all SVG images to PNG using PyMuPDF to prevent E016 Print Replica fallback.
# 3. Strips hardcoded mobile font sizes and fixes `display: block` on tables in CSS.
# 4. Injects word-wrap CSS to prevent long URLs or code strings from breaking the viewport.
# 5. Removes Pandoc's inline `<style>` tags that force absolute positioning and non-wrapping code blocks.
"""

import sys
import zipfile
import os
import re
import urllib.request
import urllib.parse
import html
import tempfile

try:
    import pymupdf
except ImportError:
    print("[ERROR] pymupdf is not installed. Please run: pip install pymupdf")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python make_epub_resizable.py <path_to_epub>")
    sys.exit(1)

epub_path = sys.argv[1]
if not epub_path.lower().endswith('.epub'):
    print("[ERROR] The file must be an .epub file.")
    sys.exit(1)

out_epub_path = epub_path[:-5] + "-kindle-img.epub"
math_cache = {}
new_images = {} # { filename: bytes }
manifest_additions = []

print(f"Reading input EPUB: {epub_path}")
print("1. Converting SVG to PNG...")
print("2. Downloading LaTeX equations as PNGs...")
print("3. Patching CSS and HTML layout bugs...")

try:
    with zipfile.ZipFile(epub_path, 'r') as z_in:
        item_list = z_in.infolist()
        
        with zipfile.ZipFile(out_epub_path, 'w') as z_out:
            # 1. Write mimetype first, strictly UNCOMPRESSED
            for item in item_list:
                if item.filename == 'mimetype':
                    content = z_in.read(item.filename)
                    z_out.writestr(item, content, compress_type=zipfile.ZIP_STORED)
                    break
                    
            # 2. Process all other files
            for item in item_list:
                if item.filename == 'mimetype':
                    continue
                    
                content = z_in.read(item.filename)
                
                # Check if it's an HTML file to process MathML and rename SVGs
                if item.filename.endswith('.xhtml') or item.filename.endswith('.html'):
                    try:
                        text = content.decode('utf-8')
                        
                        def math_replacer(match):
                            tex = match.group(1)
                            tex_unescaped = html.unescape(tex).strip()
                            
                            if tex_unescaped not in math_cache:
                                math_id = f"math_{len(math_cache)+1:03d}"
                                img_filename = f"media/{math_id}.png"
                                
                                url = 'https://latex.codecogs.com/png.image?%5Cdpi%7B150%7D%5Cbg_white%20' + urllib.parse.quote(tex_unescaped)
                                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                                try:
                                    img_data = urllib.request.urlopen(req).read()
                                    new_images[img_filename] = img_data
                                    manifest_additions.append(f'<item id="{math_id}" href="{img_filename}" media-type="image/png" />')
                                    math_cache[tex_unescaped] = img_filename
                                except Exception as e:
                                    return f" <code>{tex}</code> "
                            else:
                                img_filename = math_cache[tex_unescaped]
                            
                            if '/' in item.filename:
                                depth = item.filename.count('/')
                                rel_path = '../' * depth + img_filename
                                if item.filename.startswith('EPUB/'):
                                    rel_path = '../' * (depth - 1) + img_filename
                            else:
                                rel_path = img_filename
                                
                            return f'<img src="{rel_path}" alt="{html.escape(tex_unescaped)}" style="vertical-align: middle; max-width: 100%;" class="math-img" />'

                        # Replace MathML blocks
                        if '<math' in text:
                            text = re.sub(
                                r'<math[^>]*>.*?<annotation encoding="application/x-tex">(.*?)</annotation>.*?</math>',
                                math_replacer,
                                text,
                                flags=re.DOTALL
                            )
                            text = re.sub(r'<math[^>]*>.*?</math>', r'', text, flags=re.DOTALL)
                        
                        # Fix Pandoc's inline <style> block that injects un-reflowable CSS
                        if '<style' in text:
                            text = text.replace('white-space: pre;', 'white-space: pre-wrap;')
                            text = text.replace('position: relative;', '')
                            text = text.replace('display: inline-block;', '')
                            text = text.replace('overflow: auto;', 'overflow: visible;')
                            
                        # Replace all .svg references with .png
                        text = text.replace('.svg', '.png')
                        
                        content = text.encode('utf-8')
                    except UnicodeDecodeError:
                        pass
                
                # Check if it's content.opf, inject manifest additions and fix SVGs
                elif item.filename.endswith('.opf'):
                    try:
                        text = content.decode('utf-8')
                        # Replace .svg with .png globally in the manifest
                        text = text.replace('.svg', '.png')
                        text = text.replace('media-type="image/svg+xml"', 'media-type="image/png"')
                        pass # We will write this file at the end
                    except UnicodeDecodeError:
                        pass
                
                # Check if it's CSS
                elif item.filename.endswith('.css'):
                    try:
                        text = content.decode('utf-8')
                        if '@media (max-width: 30em)' in text:
                            if 'word-wrap: break-word;' not in text:
                                text = text.replace(
                                    '  widows: 2;\n',
                                    '  widows: 2;\n  word-wrap: break-word;\n  overflow-wrap: break-word;\n'
                                )
                            if 'body { font-size: 0.95em; }' in text:
                                text = text.replace('  body { font-size: 0.95em; }\n', '')
                                
                        if 'table {' in text:
                            text = re.sub(r'display:\s*block;\s*(/\*[^*]*\*/)?', '', text)
                            text = re.sub(r'overflow-x:\s*auto;', '', text)
                            
                        content = text.encode('utf-8')
                    except UnicodeDecodeError:
                        pass
                
                # Convert SVG files to PNG
                elif item.filename.endswith('.svg'):
                    try:
                        # Write SVG to a temp file
                        temp_svg = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
                        temp_svg.write(content)
                        temp_svg.close()
                        
                        # Convert to PNG using PyMuPDF
                        doc = pymupdf.open(temp_svg.name)
                        # High DPI pixmap
                        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2))
                        temp_png = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                        temp_png.close()
                        pix.save(temp_png.name)
                        
                        # Read the converted PNG
                        with open(temp_png.name, "rb") as f:
                            png_content = f.read()
                            
                        os.unlink(temp_svg.name)
                        os.unlink(temp_png.name)
                        
                        # Update the filename inside the ZIP
                        new_item = zipfile.ZipInfo(item.filename.replace('.svg', '.png'))
                        # Copy compression settings
                        new_item.compress_type = zipfile.ZIP_DEFLATED
                        z_out.writestr(new_item, png_content)
                        continue
                        
                    except Exception as e:
                        print(f"Failed to convert SVG {item.filename}: {e}")
                        # Fallback: keep original but rename to PNG (will break, but better than crashing)
                        new_item = zipfile.ZipInfo(item.filename.replace('.svg', '.png'))
                        z_out.writestr(new_item, content)
                        continue
                
                if not item.filename.endswith('.opf'):
                    z_out.writestr(item, content, compress_type=zipfile.ZIP_DEFLATED)
            
            # Now write the new math images
            for img_filename, img_data in new_images.items():
                z_out.writestr(f"EPUB/{img_filename}", img_data, compress_type=zipfile.ZIP_STORED)
                
            # Finally, write the patched content.opf
            for item in item_list:
                if item.filename.endswith('.opf'):
                    content = z_in.read(item.filename)
                    text = content.decode('utf-8')
                    # Apply the SVG renames
                    text = text.replace('.svg', '.png')
                    text = text.replace('media-type="image/svg+xml"', 'media-type="image/png"')
                    
                    if manifest_additions:
                        inject_str = '\n    '.join(manifest_additions) + '\n  </manifest>'
                        text = text.replace('</manifest>', inject_str)
                    z_out.writestr(item, text.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)

    print("-" * 50)
    print(f"[SUCCESS] Kindle-ready EPUB with image-based Math and SVG-to-PNG converted!")
    print(f"Output File: {out_epub_path}")

except Exception as e:
    print(f"[ERROR] An unexpected error occurred: {e}")
    import traceback
    traceback.print_exc()
