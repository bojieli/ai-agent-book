"""Catch new reflection questions landing without their reference answers."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def answer_sections(path):
    return re.split(r'^## .+$', path.read_text(encoding='utf-8'), flags=re.M)[1:]


def questions(path):
    return re.findall(r'^(\d+)\. [★]+ (.+)$', path.read_text(encoding='utf-8'), re.M)


def test_chinese_questions_have_matching_reference_answers():
    sections = answer_sections(ROOT / 'book/reference-answers.md')
    assert len(sections) == 10
    for number, section in enumerate(sections, 1):
        expected = [n for n, text in questions(ROOT / f'book/chapter{number}.md')]
        actual = re.findall(r'^\*\*(\d+)\. ', section, re.M)
        assert expected, f'Chapter {number} has no parsed questions'
        assert actual == expected, f'Chapter {number}: questions {expected}, answers {actual}'


def test_chapter9_answers_cover_each_completed_translation():
    checked = set()
    for book in ROOT.glob('book*'):
        if not book.is_dir():
            continue
        for answer_file in book.glob('reference-answers*.md'):
            sections = answer_sections(answer_file)
            if not sections:
                # Some filenames redirect to the edition's canonical answer
                # file. Hebrew explicitly links to English pending translation.
                continue
            assert len(sections) == 10, answer_file
            chapter_file = next(book.glob('chapter9*.md'))
            expected = questions(chapter_file)
            actual = re.findall(r'^\*\*(\d+)\. \(★★★?\) (.+)\*\*$', sections[8], re.M)
            assert expected, chapter_file
            assert [n for n, _ in actual] == [n for n, _ in expected], answer_file
            assert actual[-1] == expected[-1], answer_file
            checked.add(book.name)
    assert checked == {p.name for p in ROOT.glob('book*') if p.is_dir()} - {'book-he'}
