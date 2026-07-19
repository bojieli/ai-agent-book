#!/usr/bin/env python3
"""Generate all SVG illustrations for Chapter 3 (知识库与RAG).

Figures (14 total):
  fig3-1:  Chapter roadmap
  fig3-2:  RAG end-to-end pipeline (concrete example)
  fig3-3:  Dense embedding evolution (with dimensions & training)
  fig3-4:  HNSW index structure (enlarged)
  fig3-5:  BM25 scoring mechanism (enlarged)
  fig3-6:  Hybrid retrieval + reranking (with scores)
  fig3-7:  RAPTOR tree structure (enlarged)
  fig3-8:  GraphRAG relation network (enlarged)
  fig3-9:  Agentic vs Non-Agentic RAG (concrete queries)
  fig3-10: Agentic RAG system architecture (Exp 3.6)
  fig3-11: Contextual retrieval (concrete prefix example)
  fig3-12: Structured knowledge extraction pipeline (Exp 3.10)
  fig3-13: Externalized learning loop (concrete)
  fig3-14: GAIA experience learning (Exp 3.11)
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from svg_lib import (
    SVG, COLORS, FONT, MONO, STROKE_W, CORNER_R, _escape, _marker_def,
    FS_TITLE, FS_BODY, FS_SMALL, FS_TINY, FS_LABEL,
)

OUT = os.path.join(os.path.dirname(__file__), 'images')


# ──────────────────────── Helpers ────────────────────────

def _pill(svg, x, y, w, h, label, fill='light', font_size=FS_SMALL, bold=False):
    """Rounded pill / tag shape."""
    svg.rect(x, y, w, h, fill=fill, rx=h // 2)
    c = 'white' if fill in ('dark', 'darker') else 'text'
    svg.text(x + w / 2, y + h / 2, label, size=font_size, fill=c, bold=bold)


# ──────────────────────── fig3-1 ────────────────────────

def fig3_1():
    """本章知识脉络"""
    w, h = 860, 580
    svg = SVG(w, h)

    svg.text(w / 2, 32, "第三章：知识库与 RAG —— 知识脉络", size=FS_TITLE, bold=True)

    # --- Row 1: RAG foundations ---
    r1_y = 70
    svg.rect(30, r1_y, 800, 130, fill='white', stroke='border', dash=True)
    svg.text(80, r1_y + 20, "RAG 基础", size=FS_BODY, bold=True, anchor='start')

    boxes_r1 = [
        ("稠密嵌入", 50, "Word2Vec → BGE-M3"),
        ("稀疏嵌入", 230, "TF-IDF / BM25"),
        ("混合检索 + 重排序", 410, "双路召回 + Cross-Encoder"),
        ("多模态提取", 650, "原生 / 文本 / 工具"),
    ]
    for label, bx, sub in boxes_r1:
        svg.box(bx, r1_y + 38, 160, 50, label, fill='light', bold=True, font_size=FS_SMALL)
        svg.text(bx + 80, r1_y + 38 + 50 + 18, sub, size=FS_TINY, fill='text_light')

    # --- Arrow down ---
    svg.arrow(w / 2, r1_y + 130, w / 2, r1_y + 160)

    # --- Row 2: Advanced knowledge structuring ---
    r2_y = 230
    svg.rect(30, r2_y, 800, 100, fill='white', stroke='border', dash=True)
    svg.text(80, r2_y + 20, "从现有知识中学习", size=FS_BODY, bold=True, anchor='start')

    boxes_r2 = [
        ("RAPTOR\n树状层次索引", 50),
        ("GraphRAG\n实体关系图谱", 230),
        ("Agentic RAG\n检索工具化", 410),
        ("上下文感知检索\n前缀摘要增强", 590),
    ]
    for label, bx in boxes_r2:
        svg.box(bx, r2_y + 35, 160, 55, label, fill='medium', font_size=FS_SMALL)

    # --- Arrow down ---
    svg.arrow(w / 2, r2_y + 100, w / 2, r2_y + 130)

    # --- Row 3: Learning from experience ---
    r3_y = 360
    svg.rect(30, r3_y, 800, 100, fill='white', stroke='border', dash=True)
    svg.text(80, r3_y + 20, "从自主探索中学习", size=FS_BODY, bold=True, anchor='start')

    boxes_r3 = [
        ("后训练\nRL → 肌肉记忆", 100),
        ("上下文学习\n推理时软检索", 330),
        ("外部化学习\n知识库 + 工具生成", 560),
    ]
    for label, bx in boxes_r3:
        svg.box(bx, r3_y + 35, 200, 55, label, fill='light', font_size=FS_SMALL)

    # --- Bottom: core insight ---
    svg.rect(180, 490, 500, 44, fill='dark')
    svg.text(w / 2, 512, "苦涩的教训：搜索 + 学习 = 通用方法", size=FS_BODY, fill='white', bold=True)
    svg.arrow(w / 2, r3_y + 100, w / 2, 488)

    svg.save(os.path.join(OUT, 'fig3-1.svg'))


# ──────────────────────── fig3-2 ────────────────────────

def fig3_2():
    """RAG 端到端流水线（具体示例）"""
    w, h = 880, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "RAG 端到端流水线", size=FS_TITLE, bold=True)

    # Step 1: User query
    svg.box(20, 65, 180, 55, "① 用户查询", fill='medium', bold=True, font_size=FS_BODY)
    q_lines = ['"故意杀人罪判几年？"']
    svg.text(110, 145, q_lines[0], size=FS_SMALL, fill='text_light')

    svg.arrow(200, 92, 238, 92)

    # Step 2: Retrieval
    svg.box(240, 65, 180, 55, "② 检索 (Retrieval)", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 140, "稠密检索 + BM25", size=FS_SMALL, fill='text_light')
    svg.text(330, 160, "→ Top-K 文本块", size=FS_SMALL, fill='text_light')

    svg.arrow(420, 92, 458, 92)

    # Step 3: Augmentation
    svg.box(460, 65, 180, 55, "③ 增强 (Augment)", fill='light', bold=True, font_size=FS_BODY)
    svg.text(550, 140, "查询 + 检索结果", size=FS_SMALL, fill='text_light')
    svg.text(550, 160, "→ 构造完整 Prompt", size=FS_SMALL, fill='text_light')

    svg.arrow(640, 92, 678, 92)

    # Step 4: Generation
    svg.box(680, 65, 180, 55, "④ 生成 (Generate)", fill='medium', bold=True, font_size=FS_BODY)
    svg.text(770, 140, "LLM 综合上下文", size=FS_SMALL, fill='text_light')
    svg.text(770, 160, "→ 生成回答", size=FS_SMALL, fill='text_light')

    # Concrete data flow example
    svg.line(20, 195, 860, 195, color='dark', dash=True)
    svg.text(w / 2, 215, "具体数据流示例", size=FS_BODY, bold=True)

    # Retrieved chunks
    svg.rect(20, 235, 400, 90, fill='code_bg', stroke='dark', rx=4)
    svg.text(220, 253, "检索到的文本块", size=FS_SMALL, bold=True)
    svg.mono(30, 278, "《刑法》第232条：故意杀人的，处死刑、", size=FS_TINY)
    svg.mono(30, 298, "无期徒刑或十年以上有期徒刑...", size=FS_TINY)

    # Augmented prompt
    svg.rect(440, 235, 420, 90, fill='code_bg', stroke='dark', rx=4)
    svg.text(650, 253, "增强后的 Prompt", size=FS_SMALL, bold=True)
    svg.mono(450, 278, "基于以下法条回答问题：", size=FS_TINY)
    svg.mono(450, 298, "[《刑法》第232条...]  问：故意杀人罪判几年？", size=FS_TINY)

    # Generated answer
    svg.rect(20, 345, 840, 80, fill='light', stroke='border')
    svg.text(w / 2, 363, "生成的回答", size=FS_SMALL, bold=True)
    svg.mono(30, 390, "根据《刑法》第232条，故意杀人罪处死刑、无期徒刑或十年以上有期徒刑；", size=FS_TINY)
    svg.mono(30, 412, "情节较轻的，处三年以上十年以下有期徒刑。", size=FS_TINY)

    svg.save(os.path.join(OUT, 'fig3-2.svg'))


# ──────────────────────── fig3-3 ────────────────────────

def fig3_3():
    """稠密嵌入技术演进"""
    w, h = 860, 340
    svg = SVG(w, h)
    svg.text(w / 2, 30, "稠密嵌入技术演进", size=FS_TITLE, bold=True)

    items = [
        ("Word2Vec", "2013", "300维\n静态词向量", "共现关系\n预测训练"),
        ("GloVe", "2014", "300维\n全局统计", "矩阵分解\n+ 共现"),
        ("BERT", "2018", "768维\n上下文感知", "Transformer\nMLM预训练"),
        ("Sentence-BERT", "2019", "768维\n句子级嵌入", "孪生网络\n对比学习"),
        ("BGE-M3", "2024", "1024维\n多语言长文本", "多阶段\n混合训练"),
    ]
    n = len(items)
    pad_l, pad_r = 80, 80
    usable = w - pad_l - pad_r
    gap = usable / (n - 1)
    line_y = 90

    svg.line(pad_l - 30, line_y, w - pad_r + 30, line_y, color='dark')
    svg.elems.append(
        f'<polygon points="{w - pad_r + 30},{line_y - 6} {w - pad_r + 42},{line_y} '
        f'{w - pad_r + 30},{line_y + 6}" fill="{COLORS["dark"]}"/>'
    )

    for i, (name, year, dims, training) in enumerate(items):
        x = pad_l + i * gap
        svg.circle(x, line_y, 8, fill='dark')
        svg.text(x, line_y - 30, name, size=FS_BODY, bold=True)
        svg.text(x, line_y + 28, year, size=FS_SMALL, fill='text_light')

        svg.rect(x - 65, line_y + 50, 130, 55, fill='light')
        for j, dl in enumerate(dims.split('\n')):
            svg.text(x, line_y + 68 + j * 22, dl, size=FS_SMALL)

        svg.rect(x - 65, line_y + 115, 130, 55, fill='code_bg', stroke='dark', rx=4)
        for j, tl in enumerate(training.split('\n')):
            svg.text(x, line_y + 133 + j * 22, tl, size=FS_SMALL, fill='text_light')

    # Bottom labels
    svg.text(pad_l + gap * 0.5, h - 18,
             "静态词向量（一词一向量）", size=FS_SMALL, fill='text_light')
    svg.text(pad_l + gap * 3.5, h - 18,
             "上下文感知嵌入（一词多向量）", size=FS_SMALL, fill='text_light')

    svg.line(pad_l + gap * 1.5, 75, pad_l + gap * 1.5, h - 35, color='dark', dash=True)

    svg.save(os.path.join(OUT, 'fig3-3.svg'))


# ──────────────────────── fig3-4 ────────────────────────

def fig3_4():
    """HNSW 索引结构"""
    w, h = 750, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "HNSW 索引结构", size=FS_TITLE, bold=True)

    layers = [
        ("Layer 2（稀疏 · 长程连接）", 70, 3),
        ("Layer 1（中等密度）", 185, 6),
        ("Layer 0（稠密 · 全节点）", 300, 10),
    ]
    for label, base_y, count in layers:
        svg.rect(30, base_y - 30, w - 60, 90, fill='white', stroke='dark', dash=True)
        svg.text(100, base_y - 14, label, size=FS_SMALL, fill='text_light', anchor='start')
        spacing = (w - 140) / (count + 1)
        positions = []
        for j in range(count):
            cx = 70 + spacing * (j + 1)
            cy = base_y + 25
            svg.circle(cx, cy, 14, fill='light')
            positions.append((cx, cy))
        for j in range(count - 1):
            skip = 1 if count <= 6 else (2 if j % 2 == 0 else 1)
            if j + skip < count:
                x1, y1 = positions[j]
                x2, y2 = positions[j + skip]
                svg.line(x1 + 14, y1, x2 - 14, y2, color='dark')

    # Search path arrows
    svg.arrow(w / 2, 130, w / 2 - 50, 165, color='border')
    svg.text(w / 2 + 80, 148, "搜索从顶层开始", size=FS_SMALL, fill='text_light')
    svg.arrow(w / 2 - 50, 245, w / 2 - 80, 280, color='border')
    svg.text(w / 2 + 60, 263, "逐层向下精炼", size=FS_SMALL, fill='text_light')

    # Key properties
    svg.rect(50, h - 45, 300, 32, fill='light')
    svg.text(200, h - 29, "支持增量更新 · 高召回率", size=FS_SMALL, bold=True)
    svg.rect(400, h - 45, 300, 32, fill='code_bg', stroke='dark', rx=4)
    svg.text(550, h - 29, "O(log N) 查询复杂度", size=FS_SMALL)

    svg.save(os.path.join(OUT, 'fig3-4.svg'))


# ──────────────────────── fig3-5 ────────────────────────

def fig3_5():
    """BM25 评分机制"""
    w, h = 800, 380
    svg = SVG(w, h)
    svg.text(w / 2, 30, "BM25 评分机制", size=FS_TITLE, bold=True)

    # Formula
    svg.rect(40, 50, w - 80, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(60, 75,
             "Score(Q,D) = Σ IDF(qi) × TF(qi,D)×(k1+1) / (TF + k1×(1-b+b×|D|/avgdl))",
             size=FS_SMALL)

    # Three components
    boxes = [
        ("词频饱和 (TF)", 40, 'light', [
            "k₁ 控制饱和速度",
            "词频 ↑ 但贡献递减",
            "例: 出现 5→10 次",
            "得分仅增 ~20%",
        ]),
        ("逆文档频率 (IDF)", 290, 'light', [
            "衡量词的稀有度",
            "\"的\" → IDF ≈ 0",
            "\"量刑\" → IDF ≈ 5.2",
            "稀有词权重 >> 常见词",
        ]),
        ("长度归一化 (b)", 540, 'light', [
            "b ∈ [0,1] 归一化强度",
            "b=0: 不考虑长度",
            "b=1: 完全归一化",
            "避免长文档偏倚",
        ]),
    ]
    for title, bx, fill, details in boxes:
        svg.rect(bx, 120, 220, 170, fill=fill)
        svg.text(bx + 110, 148, title, size=FS_BODY, bold=True)
        svg.line(bx + 20, 163, bx + 200, 163, color='dark')
        for k, line in enumerate(details):
            svg.text(bx + 110, 190 + k * 28, line, size=FS_SMALL, fill='text_light')

    # Result bar
    for bx in [150, 400, 650]:
        svg.line(bx, 290, bx, 315, color='dark')
    svg.rect(40, 315, w - 80, 48, fill='medium')
    svg.text(w / 2, 339, "最终得分 = Σ  (TF饱和 × IDF加权 × 长度归一化)", size=FS_BODY, bold=True)

    svg.save(os.path.join(OUT, 'fig3-5.svg'))


# ──────────────────────── fig3-6 ────────────────────────

def fig3_6():
    """混合检索与重排序流水线（含分数示例）"""
    w, h = 880, 480
    svg = SVG(w, h)
    svg.text(w / 2, 30, "混合检索与重排序流水线", size=FS_TITLE, bold=True)

    # Query
    svg.rect(30, 55, 160, 50, fill='medium')
    svg.text(110, 73, "用户查询", size=FS_BODY, bold=True)
    svg.mono(110, 93, '"kitty behavior"', size=FS_TINY, anchor='middle')

    # Dense retrieval
    svg.arrow(190, 68, 238, 68)
    svg.box(240, 50, 180, 50, "稠密检索", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 118, "语义匹配: kitty ≈ cat", size=FS_SMALL, fill='text_light')

    dense_results = [
        ("doc3: \"feline habits and cat play...\"", "cos=0.87"),
        ("doc7: \"cat grooming patterns...\"", "cos=0.82"),
        ("doc1: \"pet care basics...\"", "cos=0.71"),
    ]
    for i, (doc, score) in enumerate(dense_results):
        y = 140 + i * 32
        svg.mono(250, y, doc, size=FS_TINY)
        svg.text(700, y, score, size=FS_TINY, fill='text_light', anchor='start')

    # Sparse retrieval
    svg.arrow(190, 90, 238, 270)
    svg.box(240, 250, 180, 50, "稀疏检索 (BM25)", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 318, "精确匹配: \"kitty\" 关键词", size=FS_SMALL, fill='text_light')

    sparse_results = [
        ("doc5: \"kitty litter training...\"", "BM25=8.4"),
        ("doc9: \"kitty adoption guide...\"", "BM25=6.1"),
        ("doc2: \"kitten health tips...\"", "BM25=3.2"),
    ]
    for i, (doc, score) in enumerate(sparse_results):
        y = 340 + i * 32
        svg.mono(250, y, doc, size=FS_TINY)
        svg.text(700, y, score, size=FS_TINY, fill='text_light', anchor='start')

    # Merge + rerank
    svg.arrow(770, 180, 808, 220)
    svg.arrow(770, 370, 808, 330)

    svg.rect(790, 215, 70, 120, fill='medium')
    svg.text(825, 250, "合并", size=FS_BODY, bold=True)
    svg.text(825, 275, "去重", size=FS_BODY, bold=True)
    svg.text(825, 300, "6→5", size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-6.svg'))


# ──────────────────────── fig3-7 ────────────────────────

def fig3_7():
    """RAPTOR 树状结构"""
    w, h = 800, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "RAPTOR 树状层次索引", size=FS_TITLE, bold=True)

    # Root
    svg.box(300, 55, 200, 50, "全局摘要", fill='dark', bold=True, font_size=FS_BODY)
    svg.text(300 + 200 + 15, 80, "← 根节点", size=FS_SMALL, fill='text_light', anchor='start')

    # Mid-level
    mid_nodes = [("聚类摘要 A", 80), ("聚类摘要 B", 320), ("聚类摘要 C", 560)]
    for label, x in mid_nodes:
        svg.box(x, 150, 160, 48, label, fill='medium', font_size=FS_BODY)
    svg.line(400, 105, 160, 150, color='border')
    svg.line(400, 105, 400, 150, color='border')
    svg.line(400, 105, 640, 150, color='border')
    svg.text(35, 230, "中间层 ↑", size=FS_SMALL, fill='text_light', anchor='start')

    # Leaf nodes — 7 boxes evenly distributed, narrower to avoid overlap
    chunks = [
        [(40, "文本块 1"), (140, "文本块 2"), (240, "文本块 3")],   # 聚类 A → cluster center ~160
        [(360, "文本块 4"), (460, "文本块 5")],                    # 聚类 B → cluster center ~410
        [(560, "文本块 6"), (660, "文本块 7")],                    # 聚类 C → cluster center ~640
    ]
    leaf_w = 88
    mid_cxs = [160, 400, 640]
    for gi, group in enumerate(chunks):
        for cx, label in group:
            svg.box(cx, 250, leaf_w, 40, label, fill='light', font_size=FS_SMALL)
            svg.line(cx + leaf_w / 2, 250, mid_cxs[gi], 198, color='dark')
    svg.text(35, 295, "叶子层 ↑", size=FS_SMALL, fill='text_light', anchor='start')

    # Original document
    svg.rect(40, 320, 720, 55, fill='white', stroke='dark', dash=True)
    svg.text(400, 340, "原始文档", size=FS_BODY, fill='text_light')
    for bx in range(60, 720, 110):
        svg.rect(bx, 350, 90, 16, fill='light')

    # Bottom label
    svg.text(w / 2, h - 20, "自下而上递归抽象：细节 → 主题 → 全局概览", size=FS_BODY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-7.svg'))


# ──────────────────────── fig3-8 ────────────────────────

def fig3_8():
    """GraphRAG 关系网络"""
    w, h = 750, 430
    svg = SVG(w, h)
    svg.text(w / 2, 28, "GraphRAG 实体-关系知识图谱", size=FS_TITLE, bold=True)

    nodes = [
        ("Intel", 375, 100, 'medium'),
        ("SSE", 150, 190, 'light'),
        ("AVX", 550, 190, 'light'),
        ("XMM寄存器", 100, 320, 'light'),
        ("ADDPS", 280, 340, 'light'),
        ("YMM寄存器", 520, 320, 'light'),
        ("浮点运算", 375, 250, 'light'),
    ]
    node_r = 42

    # Community box（先绘制，作为底层背景，避免覆盖后续节点和连线）
    svg.rect(50, 275, 300, 110, fill='none', stroke='border', dash=True)
    svg.text(200, 395, "社区: SSE 指令集", size=FS_SMALL, fill='text_light')

    for label, x, y, fill in nodes:
        svg.circle(x, y, node_r, fill=fill, label=label, font_size=FS_SMALL)

    edges = [
        (0, 1, "开发"), (0, 2, "开发"),
        (1, 3, "使用"), (1, 6, ""), (1, 4, "包含指令"),
        (2, 5, "使用"), (2, 6, "执行"),
        (6, 3, ""), (6, 5, "操作"),
    ]
    for i, j, elabel in edges:
        x1, y1 = nodes[i][1], nodes[i][2]
        x2, y2 = nodes[j][1], nodes[j][2]
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        ux, uy = dx / dist, dy / dist
        ax1 = x1 + ux * (node_r + 3)
        ay1 = y1 + uy * (node_r + 3)
        ax2 = x2 - ux * (node_r + 14)
        ay2 = y2 - uy * (node_r + 14)
        svg.arrow(ax1, ay1, ax2, ay2, label=elabel, color='dark')

    svg.save(os.path.join(OUT, 'fig3-8.svg'))


# ──────────────────────── fig3-9 ────────────────────────

def fig3_9():
    """Agentic RAG 与 Non-Agentic RAG 对比（具体示例）"""
    w, h = 880, 560
    svg = SVG(w, h)
    col_w = 400
    lx, rx = 20, 460

    # --- Left: Non-Agentic ---
    svg.rect(lx, 50, col_w, 45, fill='medium')
    svg.text(lx + col_w / 2, 73, "Non-Agentic RAG", size=FS_BODY, bold=True)

    steps_l = [
        ("查询: \"醉酒过失致人重伤\n且有盗窃前科如何量刑？\"", 'light'),
        ("单次检索:\n\"过失致人重伤量刑\"", 'light'),
        ("检索结果: 仅找到过失伤害\n基本法条（上下文不完整）", 'code_bg'),
        ("直接生成: 遗漏\"醉酒\"\n和\"前科\"影响因素", 'light'),
    ]
    prev_y = 95
    for i, (s, fill) in enumerate(steps_l):
        y = 110 + i * 108
        svg.box(lx + 30, y, 340, 80, s, fill=fill, font_size=FS_SMALL)
        if i > 0:
            svg.arrow(lx + 200, prev_y + 80 + 2, lx + 200, y - 2)
        prev_y = y

    svg.text(lx + col_w / 2, h - 15, "单次直通 · 信息不完整", size=FS_BODY, fill='text_light')

    # --- Separator ---
    svg.line(440, 50, 440, h - 5, color='dark', dash=True)

    # --- Right: Agentic ---
    svg.rect(rx, 50, col_w, 45, fill='medium')
    svg.text(rx + col_w / 2, 73, "Agentic RAG (ReAct)", size=FS_BODY, bold=True)

    steps_r = [
        ("思考: 需要分解为3个子问题", 'light'),
        ("搜索①: \"过失致人重伤量刑\"\n搜索②: \"醉酒刑事责任\"\n搜索③: \"盗窃前科影响\"", 'code_bg'),
        ("观察: 找到基本法条但\n缺少\"前科\"与\"过失伤害\"关联", 'light'),
        ("搜索④: \"累犯 不同罪名\n司法解释\"", 'code_bg'),
        ("综合: 完整回答含全部\n法条依据和量刑分析", 'medium'),
    ]
    ys = []
    for i, (s, fill) in enumerate(steps_r):
        y = 105 + i * 86
        hh = 68
        svg.box(rx + 30, y, 340, hh, s, fill=fill, font_size=FS_SMALL)
        ys.append(y)
        if i > 0:
            svg.arrow(rx + 200, ys[i - 1] + hh + 2, rx + 200, y - 2)

    # Iteration loop arrow
    loop_x = rx + 370 + 10
    svg.elems.append(
        f'<path d="M {loop_x},{ys[2] + 34} C {loop_x + 28},{ys[2] + 34} '
        f'{loop_x + 28},{ys[1] + 34} {loop_x},{ys[1] + 34}" '
        f'fill="none" stroke="{COLORS["border"]}" stroke-width="{STROKE_W}" '
        f'stroke-dasharray="6,3" marker-end="url(#ah)"/>'
    )
    svg.text(loop_x + 4, (ys[1] + ys[2]) / 2 + 34, "迭代", size=FS_SMALL, fill='text_light',
             anchor='start')

    svg.text(rx + col_w / 2, h - 15, "多轮迭代 · 信息完整", size=FS_BODY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-9.svg'))


# ──────────────────────── fig3-10 ────────────────────────

def fig3_10():
    """Agentic RAG 系统架构（实验 3.6）"""
    w, h = 880, 500
    svg = SVG(w, h)
    svg.text(w / 2, 30, "实验 3.6：Agentic RAG 系统架构", size=FS_TITLE, bold=True)

    # Agent core
    svg.rect(220, 55, 440, 200, fill='white', stroke='border')
    svg.text(440, 78, "Agent (ReAct 循环)", size=FS_BODY, bold=True)

    # ReAct steps inside agent
    react_items = [
        ("① Thought (思考)", 240, 100, 180, 45, 'light'),
        ("② Action (行动)", 460, 100, 180, 45, 'medium'),
        ("③ Observation (观察)", 350, 180, 180, 45, 'light'),
    ]
    for label, bx, by, bw, bh, fill in react_items:
        svg.box(bx, by, bw, bh, label, fill=fill, font_size=FS_SMALL, bold=True)

    svg.arrow(420, 122, 458, 122)
    svg.arrow(640, 130, 530, 178, color='border')
    svg.arrow(350, 202, 280, 145, color='border')

    # Loop label
    svg.text(360, 165, "循环直到信息充分", size=FS_TINY, fill='text_light')

    # User
    svg.box(20, 95, 160, 55, "用户查询", fill='medium', bold=True, font_size=FS_BODY)
    svg.arrow(180, 122, 218, 122)

    # Final answer
    svg.box(700, 95, 160, 55, "最终回答", fill='medium', bold=True, font_size=FS_BODY)
    svg.arrow(660, 122, 698, 122)

    # Tool layer
    svg.rect(100, 290, 680, 85, fill='white', stroke='border', dash=True)
    svg.text(440, 312, "工具层", size=FS_BODY, bold=True)
    tools = [
        ("knowledge_base_search", 120, 330, 220),
        ("web_search", 370, 330, 140),
        ("code_interpreter", 540, 330, 160),
    ]
    for label, tx, ty, tw in tools:
        svg.rect(tx, ty, tw, 35, fill='light')
        svg.mono(tx + tw / 2, ty + 17, label, size=FS_TINY, anchor='middle')

    svg.arrow(440, 255, 440, 288)
    svg.arrow(440, 288, 440, 255)

    # Knowledge base backends
    svg.rect(100, 400, 680, 85, fill='white', stroke='dark', dash=True)
    svg.text(440, 420, "知识库后端（可切换）", size=FS_BODY, bold=True)
    backends = [
        ("retrieval-pipeline\n混合检索", 120),
        ("structured-index\nRAPTOR/GraphRAG", 340),
        ("contextual-retrieval\n上下文感知", 560),
    ]
    for label, bx in backends:
        svg.box(bx, 435, 180, 45, label, fill='light', font_size=FS_SMALL)

    svg.arrow(230, 365, 230, 398)
    svg.arrow(440, 375, 440, 398)

    svg.save(os.path.join(OUT, 'fig3-10.svg'))


# ──────────────────────── fig3-11 ────────────────────────

def fig3_11():
    """上下文感知检索（具体前缀示例）"""
    w, h = 880, 430
    svg = SVG(w, h)
    svg.text(w / 2, 30, "上下文感知检索", size=FS_TITLE, bold=True)

    # Left: Traditional chunking
    svg.rect(20, 55, 400, 170, fill='white', stroke='border')
    svg.text(220, 78, "传统分块（无上下文）", size=FS_BODY, bold=True)

    svg.rect(40, 95, 360, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(50, 112, "该公司第二季度的收入增长了3%，", size=FS_TINY)
    svg.mono(50, 132, "主要由新产品线驱动。", size=FS_TINY)

    svg.text(220, 170, "问题：\"该公司\"是谁？哪一年？", size=FS_SMALL, fill='text_light')
    svg.text(220, 195, "→ 检索时匹配大量无关公司的收入数据", size=FS_SMALL, fill='text_light')

    # Right: Contextual
    svg.rect(460, 55, 400, 170, fill='white', stroke='border')
    svg.text(660, 78, "上下文感知分块", size=FS_BODY, bold=True)

    svg.rect(480, 95, 360, 35, fill='medium')
    svg.mono(490, 113, "[ACME公司 2025年Q2财报·关键业绩指标]", size=FS_TINY)

    svg.rect(480, 130, 360, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(490, 148, "该公司第二季度的收入增长了3%，", size=FS_TINY)
    svg.mono(490, 168, "主要由新产品线驱动。", size=FS_TINY)

    svg.text(660, 200, "→ 精确匹配 ACME + Q2 + 收入增长", size=FS_SMALL, fill='text_light')

    # Arrow between
    svg.text(440, 140, "→", size=FS_TITLE, bold=True)

    # Process flow
    svg.line(20, 250, 860, 250, color='dark', dash=True)
    svg.text(w / 2, 275, "索引阶段：LLM 生成上下文前缀", size=FS_BODY, bold=True)

    flow_y = 300
    svg.box(30, flow_y, 180, 55, "原始文档", fill='light', bold=True, font_size=FS_BODY)
    svg.arrow(210, flow_y + 27, 248, flow_y + 27)

    svg.box(250, flow_y, 180, 55, "分块", fill='light', bold=True, font_size=FS_BODY)
    svg.arrow(430, flow_y + 27, 468, flow_y + 27)

    svg.box(470, flow_y, 180, 55, "LLM 生成前缀\n(prompt caching)", fill='medium',
            font_size=FS_SMALL, bold=True)
    svg.arrow(650, flow_y + 27, 688, flow_y + 27)

    svg.box(690, flow_y, 170, 55, "前缀 + 原文\n→ 索引", fill='light', font_size=FS_SMALL, bold=True)

    # Stats
    svg.text(w / 2, h - 20,
             "效果：检索失败率 ↓49%（+BM25），↓67%（+重排序）—— Anthropic 数据",
             size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-11.svg'))


# ──────────────────────── fig3-12 ────────────────────────

def fig3_12():
    """结构化知识提取流水线（实验 3.10）"""
    w, h = 880, 510
    svg = SVG(w, h)
    svg.text(w / 2, 30, "实验 3.10：结构化知识提取（司法判例）", size=FS_TITLE, bold=True)

    # Phase 1 header
    svg.rect(20, 55, 840, 200, fill='white', stroke='border')
    svg.text(440, 78, "阶段一：知识提取与结构化", size=FS_BODY, bold=True)

    # Raw cases
    svg.rect(40, 95, 180, 65, fill='code_bg', stroke='dark', rx=4)
    svg.text(130, 113, "原始判例文书", size=FS_SMALL, bold=True)
    svg.mono(50, 138, "CAIL2018 数据集", size=FS_TINY)

    svg.arrow(220, 127, 258, 127)

    # LLM extraction
    svg.rect(260, 95, 180, 65, fill='medium')
    svg.text(350, 113, "LLM 因子发现", size=FS_SMALL, bold=True)
    svg.text(350, 138, "自下而上 Schema", size=FS_SMALL, fill='text_light')

    svg.arrow(440, 127, 478, 127)

    # Structured JSON
    svg.rect(480, 95, 200, 65, fill='code_bg', stroke='dark', rx=4)
    svg.text(580, 113, "结构化 JSON", size=FS_SMALL, bold=True)
    svg.mono(490, 138, "{自首:true, 赔偿:50万,", size=FS_TINY)
    svg.mono(490, 155, " 伤害等级:重伤二级}", size=FS_TINY)

    # Schema detail
    svg.rect(40, 170, 400, 70, fill='light')
    svg.text(240, 188, "模块化数据模式", size=FS_SMALL, bold=True)
    svg.text(240, 212, "核心模式（自首/赔偿/前科）+ 罪名扩展模式", size=FS_SMALL, fill='text_light')
    svg.text(240, 232, "（盗窃→涉案金额, 伤害→伤害等级）", size=FS_SMALL, fill='text_light')

    # Phase 2 header
    svg.rect(20, 270, 840, 200, fill='white', stroke='border')
    svg.text(440, 293, "阶段二：因子分析与知识建模", size=FS_BODY, bold=True)

    # Vectorization
    svg.rect(40, 310, 200, 65, fill='light')
    svg.text(140, 328, "特征向量化", size=FS_SMALL, bold=True)
    svg.text(140, 350, "独热编码 + 多热编码", size=FS_SMALL, fill='text_light')
    svg.text(140, 370, "+ 对数变换 + 标准化", size=FS_SMALL, fill='text_light')

    svg.arrow(240, 342, 278, 342)

    # Clustering
    svg.rect(280, 310, 200, 65, fill='medium')
    svg.text(380, 328, "HDBSCAN 聚类", size=FS_SMALL, bold=True)
    svg.text(380, 350, "发现\"案件原型\"", size=FS_SMALL, fill='text_light')
    svg.text(380, 370, "如: 轻微口角→轻伤", size=FS_SMALL, fill='text_light')

    svg.arrow(480, 342, 518, 342)

    # Factor importance
    svg.rect(520, 310, 200, 65, fill='light')
    svg.text(620, 328, "因子重要性模型", size=FS_SMALL, bold=True)
    svg.text(620, 350, "量化各因素权重", size=FS_SMALL, fill='text_light')
    svg.text(620, 370, "构建量刑决策逻辑", size=FS_SMALL, fill='text_light')

    # Application
    svg.arrow(620, 375, 620, 400)
    svg.rect(40, 400, 720, 60, fill='light')
    svg.text(400, 420, "应用：对话式法律咨询 Agent", size=FS_BODY, bold=True)
    svg.text(400, 445, "按因子重要性引导提问 → 检索相似案件原型 → 数据驱动的量刑分析",
             size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-12.svg'))


# ──────────────────────── fig3-13 ────────────────────────

def fig3_13():
    """外部化学习循环（具体示例）"""
    w, h = 880, 490
    svg = SVG(w, h)
    svg.text(w / 2, 30, "外部化学习：从经验到能力的闭环", size=FS_TITLE, bold=True)

    # Central Agent
    cx, cy = 440, 210
    svg.circle(cx, cy, 55, fill='medium', label="Agent", font_size=FS_BODY)

    # 5 steps around the loop
    steps = [
        ("① 执行任务", 120, 100, "处理退款请求\n调用客服API"),
        ("② 获得反馈", 680, 100, "成功退款$45\n发现需验证后四位"),
        ("③ 反思与提炼", 680, 310, "LLM 总结经验:\n\"A公司退款须验证\""),
        ("④ 存入知识库", 340, 380, "经验→向量化索引\n流程→生成工具代码"),
        ("⑤ 未来检索复用", 120, 310, "相似任务→检索经验\n直接复用成功策略"),
    ]

    positions = []
    for label, x, y, detail in steps:
        svg.box(x, y, 200, 80, label + "\n" + detail,
                fill='light', font_size=FS_SMALL)
        positions.append((x + 100, y + 40))

    # Arrows connecting steps
    arrow_pairs = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
    ]
    for si, ei in arrow_pairs:
        sx, sy = positions[si]
        ex, ey = positions[ei]
        dx, dy = ex - sx, ey - sy
        dist = math.sqrt(dx * dx + dy * dy)
        ux, uy = dx / dist, dy / dist
        svg.arrow(sx + ux * 105, sy + uy * 45,
                  ex - ux * 105, ey - uy * 45, color='dark')

    # Two output types
    svg.rect(30, 395, 180, 28, fill='dark')
    svg.text(120, 409, "知识: 概要/树形总结", size=FS_SMALL, fill='white')
    svg.rect(670, 395, 180, 28, fill='dark')
    svg.text(760, 409, "工具: 流程→代码", size=FS_SMALL, fill='white')

    svg.save(os.path.join(OUT, 'fig3-13.svg'))


# ──────────────────────── fig3-14 ────────────────────────

def fig3_14():
    """GAIA 经验学习系统（实验 3.11）"""
    w, h = 880, 510
    svg = SVG(w, h)
    svg.text(w / 2, 30, "实验 3.11：GAIA 经验学习系统", size=FS_TITLE, bold=True)

    box_h = 60
    step_gap = 75
    base_y = 100

    # --- Left: Learning Mode ---
    lx = 20
    svg.rect(lx, 55, 400, 420, fill='white', stroke='border')
    svg.text(lx + 200, 80, "学习模式 (Learning Mode)", size=FS_BODY, bold=True)

    learn_steps = [
        ("GAIA 任务", 'medium', "复杂多步骤问题"),
        ("Agent 执行", 'light', "浏览器+文件+代码解释器"),
        ("任务成功？", 'light', "自动评估 (AWorld)"),
        ("LLM 反思 & 总结", 'medium', "提炼策略摘要"),
        ("经验 → 向量化", 'light', "存入经验知识库"),
    ]
    for i, (label, fill, sub) in enumerate(learn_steps):
        y = base_y + i * step_gap
        svg.box(lx + 50, y, 300, box_h, label, sublabel=sub, fill=fill, bold=True, font_size=FS_BODY)
        if i > 0:
            svg.arrow(lx + 200, base_y + (i - 1) * step_gap + box_h + 2, lx + 200, y - 2)

    # --- Right: Apply Mode ---
    rx = 460
    svg.rect(rx, 55, 400, 420, fill='white', stroke='border')
    svg.text(rx + 200, 80, "应用模式 (Apply Mode)", size=FS_BODY, bold=True)

    apply_steps = [
        ("新 GAIA 任务", 'medium', "接收新问题"),
        ("语义检索经验", 'light', "在经验库中搜索相似任务"),
        ("注入 System Prompt", 'medium', "历史成功策略作为范例"),
        ("Agent 执行", 'light', "借鉴经验，更高效解题"),
        ("成功率 ↑ 效率 ↑", 'dark', "自进化: 越做越强"),
    ]
    for i, (label, fill, sub) in enumerate(apply_steps):
        y = base_y + i * step_gap
        svg.box(rx + 50, y, 300, box_h, label, sublabel=sub, fill=fill, bold=True, font_size=FS_BODY)
        if i > 0:
            svg.arrow(rx + 200, base_y + (i - 1) * step_gap + box_h + 2, rx + 200, y - 2)

    # Arrow from learning to apply: the experience KB (centered vertically)
    kb_cy = base_y + 2 * step_gap + box_h / 2  # 与第 3 步中心对齐
    kb_x1, kb_x2 = 375, 505
    svg.rect(kb_x1, kb_cy - 25, kb_x2 - kb_x1, 50, fill='dark')
    svg.text((kb_x1 + kb_x2) / 2, kb_cy - 8, "经验知识库", size=FS_SMALL, fill='white', bold=True)
    svg.text((kb_x1 + kb_x2) / 2, kb_cy + 12, "(向量索引)", size=FS_TINY, fill='white')

    # Last learn step right-middle → KB left
    last_y = base_y + 4 * step_gap + box_h / 2
    svg.arrow(lx + 350, last_y, kb_x1 - 2, kb_cy + 10)
    # KB right → second apply step left-middle
    apply2_y = base_y + 1 * step_gap + box_h / 2
    svg.arrow(kb_x2 + 2, kb_cy - 10, rx + 50, apply2_y)

    svg.save(os.path.join(OUT, 'fig3-14.svg'))


# ──────────────────────── Main ────────────────────────

ALL_FIGS = [
    fig3_1, fig3_2, fig3_3, fig3_4, fig3_5, fig3_6, fig3_7,
    fig3_8, fig3_9, fig3_10, fig3_11, fig3_12, fig3_13, fig3_14,
]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for fn in ALL_FIGS:
        fn()
        print(f"  ✓ {fn.__name__}: {fn.__doc__}")
    print(f"\nDone — {len(ALL_FIGS)} SVGs saved to {OUT}/")
