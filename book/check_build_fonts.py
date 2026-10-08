#!/usr/bin/env python3
"""Fail before a release build if XeLaTeX would select non-Mac fallbacks."""
from pathlib import Path
import subprocess
import tempfile


def main():
    fonts = ('Songti SC', 'Menlo')
    checks = '\n'.join(
        r'\IfFontExistsTF{' + font + r'}{\typeout{Required font found: ' + font + r'}}'
        r'{\PackageError{book-fonts}{Required font missing: ' + font + r'}'
        r'{Use a macOS runner with the local book fonts installed.}}'
        for font in fonts
    )
    with tempfile.TemporaryDirectory(prefix='book-fonts-') as work:
        source = Path(work) / 'fonts.tex'
        source.write_text(
            '\\documentclass{article}\n\\usepackage{fontspec}\n' + checks +
            '\n\\begin{document}Font check.\\end{document}\n'
        )
        subprocess.run([
            'xelatex', '-no-pdf', '-interaction=nonstopmode', '-halt-on-error',
            str(source),
        ], cwd=work, check=True)


if __name__ == '__main__':
    main()
