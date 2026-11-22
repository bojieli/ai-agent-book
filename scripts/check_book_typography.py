#!/usr/bin/env python3
"""Check referenced vector diagrams after rebuilding the book figures.

Needs fontTools for generation and Playwright/Chromium for geometric checks.
Optional --baseline compares every technical character before outline conversion.
Generated proof files and reports stay in book/build/.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://www.w3.org/2000/svg'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline')
    parser.add_argument('--text-changes', type=Path,
                        help='Reviewed removals/additions for the specified baseline')
    args = parser.parse_args()
    changes = json.loads(args.text_changes.read_text()) if args.text_changes else {}
    figures = []
    for chapter in ['introduction'] + [f'chapter{i}' for i in range(1, 11)]:
        source = ROOT / 'book' / (chapter + '.md')
        figures.extend((title, source.parent / url) for title, url in
                       re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', source.read_text()))
    out = ROOT / 'book/build/typography'
    out.mkdir(parents=True, exist_ok=True)
    parts = ['<meta charset="utf-8"><style>section{width:450px}svg{width:100%;height:auto}</style>']
    text_checks, vectors = [], []
    for _, path in figures:
        if path.suffix != '.svg':
            continue
        root = ET.parse(path).getroot()
        if not root.findall('s:g[@data-font]', NS):
            continue  # Original product screenshots keep their embedded image.
        assert not root.findall('.//s:text', NS), f'Unoutlined text: {path}'
        vectors.append(path.name)
        parts.append(f'<section id="{path.stem}">{path.read_text()}</section>')
        if args.baseline:
            old = subprocess.check_output(['git', 'show', f'{args.baseline}:book/images/{path.name}'], cwd=ROOT, text=True)
            before = ''.join(el.text or '' for el in ET.fromstring(old).findall('s:text', NS))
            if not before:
                before = ''.join(el.get('aria-label', '') for el in
                                 ET.fromstring(old).findall('s:g[@data-font]', NS))
            for edit in changes.get(path.name, []):
                assert before.count(edit['before']) == 1, f'Ambiguous text edit: {path}'
                before = before.replace(edit['before'], edit['after'], 1)
            after = ''.join(el.get('aria-label', '') for el in root.findall('s:g[@data-font]', NS))
            assert before == after, f'Technical text changed: {path}'
            text_checks.append(path.name)
    html = out / 'figures.html'
    html.write_text(''.join(parts))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html.as_uri())
        issues = page.evaluate('''() => [...document.querySelectorAll('section')].flatMap(s => {
          const svg=s.querySelector('svg'), vb=svg.viewBox.baseVal;
          const texts=[...svg.querySelectorAll('g[data-font]')], issues=[];
          for(let i=0;i<texts.length;i++) {
            const a=texts[i].getBBox(), label=texts[i].getAttribute('aria-label');
            if(a.x < -1 || a.y < -1 || a.x+a.width > vb.width+1 || a.y+a.height > vb.height+1)
              issues.push({figure:s.id,type:'boundary',label});
            for(let j=i+1;j<texts.length;j++) {
              const b=texts[j].getBBox();
              if(Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>2 &&
                 Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>3)
                issues.push({figure:s.id,type:'overlap',label,other:texts[j].getAttribute('aria-label')});
            }
          }
          return issues;
        })''')
        browser.close()
    report = {'referenced_figures': len(figures), 'outlined_vectors': len(vectors),
              'verified_technical_text': len(text_checks),
              'reviewed_text_changes': len(set(vectors) & changes.keys()),
              'issues': issues}
    (out / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False))
    assert not issues


if __name__ == '__main__':
    main()
