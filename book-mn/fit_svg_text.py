"""Номын репозиторт хадгалагдсан SVG файлын текстийн халилтыг тухайн файлд нь засна.

Энэ хэрэгсэл диск дээрх SVG бүрд svg_lib.fit_overflow өргөний загварыг ашиглана.
Агуулж буй тэгш өнцөгт эсвэл зургийн хүрээнээс хэтэрсэн текстийн зөвхөн
фонтын хэмжээг багасгана. Байрлалыг огт өөрчилдөггүй учир аюулгүй бөгөөд
давтан ажиллуулахад нэмэлт өөрчлөлт гарахгүй.

Ашиглах заавар:
    python3 fit_svg_text.py                 # images/*.svg бүх файлыг засна
    python3 fit_svg_text.py images/fig6-3.svg ...   # тодорхой файлуудыг засна
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_lib import fit_overflow

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')


def process(path):
    with open(path, encoding='utf-8') as f:
        original = f.read()
    fixed = fit_overflow(original)
    if fixed != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed)
        return True
    return False


def main(argv):
    targets = argv[1:] or sorted(glob.glob(os.path.join(IMG, '*.svg')))
    changed = 0
    for path in targets:
        if process(path):
            changed += 1
            print(f'  fitted {os.path.basename(path)}')
    print(f'\nAdjusted {changed}/{len(targets)} SVG file(s).')


if __name__ == '__main__':
    main(sys.argv)
