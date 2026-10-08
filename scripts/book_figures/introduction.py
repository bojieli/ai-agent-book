"""Regenerate the preface figures with retained technical labels and grayscale styling."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'book' / 'images'
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
    f=Figure('Agent = LLM + 上下文 + 工具','三类功能要素及对应章节；评估覆盖整体系统，交互、持续进化与协作综合运用三类要素。',825)
    f.box(320,20,260,80,fill='#dedede')
    f.text(450,53,'Agent',26,True)
    f.text(450,83,'自主决策系统',20)
    f.path([(450,100),(450,125)])
    f.path([(160,150),(160,125),(740,125),(740,150)])
    f.path([(450,125),(450,150)])
    columns=[
        (20,'LLM','大脑','理解 · 思考\n规划 · 决策',
         '第 8 章 模型后训练','工具调用决策\nSFT · 强化学习'),
        (310,'上下文','当前决策视野','指令 · 记忆 · 知识\n工具定义 · 轨迹 · 状态',
         '第 2、3 章','上下文工程 · 用户记忆\n知识库 · 提示工程\nKV Cache · 压缩\nRAG · 结构化索引\nAgentic RAG'),
        (600,'工具','感官和手脚','感知 · 执行\n协作 · 代码',
         '第 4、5 章','工具 · Coding Agent\nMCP · 工具安全\n代码即思考 · Agent 自举'),
    ]
    for x,title,metaphor,functions,chapters,details in columns:
        f.box(x,150,280,395,fill='#ffffff')
        f.box(x,150,280,165,fill='#dedede')
        f.text(x+140,184,title,25,True)
        f.text(x+140,218,metaphor,22,True)
        f.text(x+140,253,functions,20)
        f.text(x+140,351,chapters,22,True)
        f.text(x+140,386,details,20)
    f.box(20,565,860,72)
    f.text(450,594,'第 7 章 Agent 的评估',22,True)
    f.text(450,626,'环境 · 指标 · 数据 · 系统反馈',20)
    for x,title,details in [
        (20,'第 6 章 交互','多模态 · 语音\nComputer Use · 机器人\n异步事件架构'),
        (310,'第 9 章 持续进化','运行经验 · 持续更新\n验证 · 发布 · 回滚'),
        (600,'第 10 章 多 Agent 协作','分工 · 通信 · 协作\nAgent 社会与经济'),
    ]:
        f.box(x,650,280,150)
        f.text(x+140,683,title,22,True)
        f.text(x+140,718,details,20)
    f.save('fig0-1.svg')


def roadmap():
    f=Figure('全书结构：构建 Agent 与提升 Agent 能力','第一至六章建立构建方法，第七章提供评估反馈，第八至十章从参数、系统更新与协作提升能力。',890)
    f.box(20,20,400,65,fill='#dedede')
    f.text(220,60,'第一部分：如何构建 Agent',24,True)
    f.box(480,20,400,65,fill='#dedede')
    f.text(680,60,'第二部分：如何提升能力',24,True)
    left=[
        ('第 1 章 AI Agent 入门','概念框架 · ReAct · Harness'),
        ('第 2 章 上下文工程','任务状态 · Prompt · 压缩'),
        ('第 3 章 用户记忆和知识库','跨会话记忆 · RAG · 知识组织'),
        ('第 4 章 工具','MCP · 感知与执行 · 安全'),
        ('第 5 章 Coding Agent\n与通用 Agent','代码生成 · 通用能力 · 自举'),
        ('第 6 章 交互','观测与动作空间的扩展'),
    ]
    for i,(title,detail) in enumerate(left):
        y=110+i*126
        f.box(20,y,400,105)
        f.text(220,y+32,title,22,True)
        f.text(220,y+(90 if '\n' in title else 75),detail,20)
        if i<5:f.path([(220,y+105),(220,y+126)],arrow=True)
    f.box(480,110,400,115)
    f.text(680,145,'第 7 章 Agent 的评估',22,True)
    f.text(680,180,'环境 · 指标 · 统计',20)
    f.text(680,211,'可度量的反馈',20)
    f.path([(680,225),(680,247),(505,247),(505,755)])
    for y,title,detail,level in [
        (280,'第 8 章 模型后训练','SFT · RL · 奖励设计','模型参数'),
        (485,'第 9 章 Agent 的持续进化','经验 · 更新 · 发布与回滚','单体系统'),
        (690,'第 10 章 多 Agent 协作','分工 · 通信 · 协调','群体系统'),
    ]:
        f.path([(505,y+65),(540,y+65)],arrow=True)
        f.box(540,y,340,155)
        f.text(710,y+38,title,21,True)
        f.text(710,y+82,detail,20)
        f.text(710,y+123,level,20)
    f.save('fig0-2.svg')


if __name__ == '__main__':
    components()
    roadmap()
