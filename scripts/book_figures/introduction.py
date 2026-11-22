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
               '左列是三类功能，右列是对应章节；下方列出综合运用这些要素的章节。', 955)
    f.box(20, 12, 860, 60, fill='#dedede')
    f.text(450, 52, 'Agent（自主决策系统）= LLM + 上下文 + 工具', 28, True)
    rows = [
        (88, 150, 'LLM', '大脑', '理解 · 思考\n规划 · 决策',
         '第 8 章 模型后训练', '工具调用决策\nSFT · 强化学习'),
        (250, 210, '上下文', '当前决策视野', '指令 · 记忆 · 知识\n工具定义 · 轨迹 · 状态',
         '第 2、3 章', '上下文工程 · 提示工程\nKV Cache · 压缩 · 用户记忆\n知识库 · RAG · 结构化索引\nAgentic RAG'),
        (472, 174, '工具', '感官和手脚', '感知 · 执行\n协作 · 代码',
         '第 4、5 章', '工具 · Coding Agent\nMCP · 工具安全\n代码即思考 · Agent 自举'),
    ]
    for y, height, component, metaphor, functions, chapters, details in rows:
        f.box(20, y, 410, height, fill='#f2f2f2')
        f.box(438, y, 442, height, fill='#ffffff')
        f.text(225, y+40, f'{component}（{metaphor}）', 28, True)
        f.text(225, y+85, functions, 26)
        f.text(659, y+40, chapters, 28, True)
        f.text(659, y+85, details, 26)
    f.text(450, 690, '整套系统的交互、评估、进化与协作', 28, True)
    topics = [
        ('第 6 章 交互', '多模态 · 语音 · Computer Use\n机器人 · 异步事件架构'),
        ('第 7 章 评估', '环境 · 指标 · 数据 · 系统反馈'),
        ('第 9 章 持续进化', '运行经验 · 持续更新 · 验证 · 发布 · 回滚'),
        ('第 10 章 多 Agent 协作', '分工 · 通信 · 协作 · Agent 社会与经济'),
    ]
    for i, (chapter, details) in enumerate(topics):
        y = 731 + i*51 + (38 if i else 0)
        f.path([(20,y-29),(880,y-29)])
        f.text(175, y, chapter, 26)
        f.text(601, y, details, 26)
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
