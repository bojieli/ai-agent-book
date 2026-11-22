"""Regenerate the preface figures with retained technical labels and grayscale styling."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'book' / 'images' / 'revised'
FONT = 'Source Han Sans CN'
from typography import typeset


class Figure:
    def __init__(self, title, description, height):
        self.parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="{height/6:.2f}mm" viewBox="0 0 900 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#333333"/></marker></defs>',
            f'<rect width="900" height="{height}" fill="#ffffff"/>',
        ]

    def box(self, x, y, w, h, fill='#f2f2f2'):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="#333333" stroke-width="1.8"/>')

    def text(self, x, y, value, size=22, bold=False):
        for i, line in enumerate(value.split('\n')):
            self.parts.append(f'<text x="{x}" y="{y+i*(size+10)}" text-anchor="middle" font-family="{FONT}" font-size="{size}" font-weight="{700 if bold else 400}" fill="#292929">{escape(line)}</text>')

    def path(self, points, arrow=False):
        d='M '+' L '.join(f'{x} {y}' for x,y in points)
        self.parts.append(f'<path d="{d}" fill="none" stroke="#333333" stroke-width="1.8"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')

    def save(self, name):
        (ROOT/name).write_text(typeset('\n'.join(self.parts+['</svg>']), name))


def components():
    f = Figure('Agent = LLM + 上下文 + 工具',
               '从一项账单委托开始，自上而下读。模型先决定查询账单，工具返回明细；明细进入上下文，模型据此决定下一步。', 680)
    steps = [
        ('上下文', '用户委托：查清本月多收的费用'),
        ('LLM', '决定先查本月账单'),
        ('工具', '账单接口返回一笔漫游费'),
        ('上下文', '用户的委托和查到的明细都在这里'),
        ('LLM', '决定向客服询问这笔漫游费的计费依据'),
    ]
    for i, (component, example) in enumerate(steps):
        y = 20 + i * 134
        f.box(24, y, 180, 90, fill='#dedede')
        f.box(214, y, 660, 90, fill='#ffffff')
        f.text(114, y + 56, component, 28, True)
        f.text(544, y + 56, example, 26)
        if i < len(steps) - 1:
            f.path([(544, y + 90), (544, y + 130)], arrow=True)
    f.save('fig0-1.svg')


def roadmap():
    f=Figure('全书结构：构建 Agent 与提升 Agent 能力','第一至六章建立构建方法，第七章提供评估反馈，第八至十章从参数、系统更新与协作提升能力。',890)
    f.box(20,20,400,65,fill='#dedede')
    f.text(220,60,'第一部分：如何构建 Agent',24,True)
    f.box(480,20,400,65,fill='#dedede')
    f.text(680,60,'第二部分：如何提升能力',24,True)
    chapters = [
        ('第 1 章 AI Agent 入门', '模型怎样调用工具？'),
        ('第 2 章 上下文工程', '这一次决策需要哪些信息？'),
        ('第 3 章 用户记忆和知识库', '上次谈过的事怎样找回来？'),
        ('第 4 章 工具', '怎样查状态、办业务？'),
        ('第 5 章 Coding Agent\n与通用 Agent', '能否写个程序来办这件事？'),
        ('第 6 章 交互', '用户中途插话怎么办？'),
    ]
    for i, (chapter, question) in enumerate(chapters):
        y = 110 + i*124
        f.text(220, y+28, chapter, 22, True)
        f.text(220, y+(100 if i == 4 else 70), question, 20)
        if i < len(chapters)-1:
            f.path([(20, y+114), (420, y+114)])
    f.box(480,110,400,115)
    f.text(680,153,'第 7 章 Agent 的评估',22,True)
    f.text(680,204,'哪里出错？改过后有效吗？',20)
    f.path([(680,225),(680,247),(500,247),(500,747)])
    for y, chapter, question in [
        (282,'第 8 章 模型后训练','怎样用训练更新模型？'),
        (482,'第 9 章 持续进化','怎样用运行经验改进系统？'),
        (682,'第 10 章 多 Agent 协作','多位成员怎样分工、交接？'),
    ]:
        f.path([(500,y+65),(522,y+65)],arrow=True)
        f.box(522,y,358,130)
        f.text(701,y+46,chapter,22,True)
        f.text(701,y+94,question,20)
    f.save('fig0-2.svg')


if __name__ == '__main__':
    components()
    roadmap()
