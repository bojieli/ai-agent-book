#!/usr/bin/env python3
"""Generate all SVG illustrations for Chapter 3 (知識庫與RAG).

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
    """本章知識脈絡"""
    w, h = 860, 580
    svg = SVG(w, h)

    svg.text(w / 2, 32, "第三章：知識庫與 RAG —— 知識脈絡", size=FS_TITLE, bold=True)

    # --- Row 1: RAG foundations ---
    r1_y = 70
    svg.rect(30, r1_y, 800, 130, fill='white', stroke='border', dash=True)
    svg.text(80, r1_y + 20, "RAG 基礎", size=FS_BODY, bold=True, anchor='start')

    boxes_r1 = [
        ("稠密嵌入", 50, "Word2Vec → BGE-M3"),
        ("稀疏嵌入", 230, "TF-IDF / BM25"),
        ("混合檢索 + 重排序", 410, "雙路召回 + Cross-Encoder"),
        ("多模態提取", 650, "原生 / 文字 / 工具"),
    ]
    for label, bx, sub in boxes_r1:
        svg.box(bx, r1_y + 38, 160, 50, label, fill='light', bold=True, font_size=FS_SMALL)
        svg.text(bx + 80, r1_y + 38 + 50 + 18, sub, size=FS_TINY, fill='text_light')

    # --- Arrow down ---
    svg.arrow(w / 2, r1_y + 130, w / 2, r1_y + 160)

    # --- Row 2: Advanced knowledge structuring ---
    r2_y = 230
    svg.rect(30, r2_y, 800, 100, fill='white', stroke='border', dash=True)
    svg.text(80, r2_y + 20, "從現有知識中學習", size=FS_BODY, bold=True, anchor='start')

    boxes_r2 = [
        ("RAPTOR\n樹狀層次索引", 50),
        ("GraphRAG\n實體關係圖譜", 230),
        ("Agentic RAG\n檢索工具化", 410),
        ("上下文感知檢索\n字首摘要增強", 590),
    ]
    for label, bx in boxes_r2:
        svg.box(bx, r2_y + 35, 160, 55, label, fill='medium', font_size=FS_SMALL)

    # --- Arrow down ---
    svg.arrow(w / 2, r2_y + 100, w / 2, r2_y + 130)

    # --- Row 3: Learning from experience ---
    r3_y = 360
    svg.rect(30, r3_y, 800, 100, fill='white', stroke='border', dash=True)
    svg.text(80, r3_y + 20, "從自主探索中學習", size=FS_BODY, bold=True, anchor='start')

    boxes_r3 = [
        ("後訓練\nRL → 肌肉記憶", 100),
        ("上下文學習\n推理時軟檢索", 330),
        ("外部化學習\n知識庫 + 工具生成", 560),
    ]
    for label, bx in boxes_r3:
        svg.box(bx, r3_y + 35, 200, 55, label, fill='light', font_size=FS_SMALL)

    # --- Bottom: core insight ---
    svg.rect(180, 490, 500, 44, fill='dark')
    svg.text(w / 2, 512, "苦澀的教訓：搜尋 + 學習 = 通用方法", size=FS_BODY, fill='white', bold=True)
    svg.arrow(w / 2, r3_y + 100, w / 2, 488)

    svg.save(os.path.join(OUT, 'fig3-1.svg'))


# ──────────────────────── fig3-2 ────────────────────────

def fig3_2():
    """RAG 端到端流水線（具體示例）"""
    w, h = 880, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "RAG 端到端流水線", size=FS_TITLE, bold=True)

    # Step 1: User query
    svg.box(20, 65, 180, 55, "① 使用者查詢", fill='medium', bold=True, font_size=FS_BODY)
    q_lines = ['"故意殺人罪判幾年？"']
    svg.text(110, 145, q_lines[0], size=FS_SMALL, fill='text_light')

    svg.arrow(200, 92, 238, 92)

    # Step 2: Retrieval
    svg.box(240, 65, 180, 55, "② 檢索 (Retrieval)", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 140, "稠密檢索 + BM25", size=FS_SMALL, fill='text_light')
    svg.text(330, 160, "→ Top-K 文字塊", size=FS_SMALL, fill='text_light')

    svg.arrow(420, 92, 458, 92)

    # Step 3: Augmentation
    svg.box(460, 65, 180, 55, "③ 增強 (Augment)", fill='light', bold=True, font_size=FS_BODY)
    svg.text(550, 140, "查詢 + 檢索結果", size=FS_SMALL, fill='text_light')
    svg.text(550, 160, "→ 構造完整 Prompt", size=FS_SMALL, fill='text_light')

    svg.arrow(640, 92, 678, 92)

    # Step 4: Generation
    svg.box(680, 65, 180, 55, "④ 生成 (Generate)", fill='medium', bold=True, font_size=FS_BODY)
    svg.text(770, 140, "LLM 綜合上下文", size=FS_SMALL, fill='text_light')
    svg.text(770, 160, "→ 生成回答", size=FS_SMALL, fill='text_light')

    # Concrete data flow example
    svg.line(20, 195, 860, 195, color='dark', dash=True)
    svg.text(w / 2, 215, "具體資料流示例", size=FS_BODY, bold=True)

    # Retrieved chunks
    svg.rect(20, 235, 400, 90, fill='code_bg', stroke='dark', rx=4)
    svg.text(220, 253, "檢索到的文字塊", size=FS_SMALL, bold=True)
    svg.mono(30, 278, "《刑法》第232條：故意殺人的，處死刑、", size=FS_TINY)
    svg.mono(30, 298, "無期徒刑或十年以上有期徒刑...", size=FS_TINY)

    # Augmented prompt
    svg.rect(440, 235, 420, 90, fill='code_bg', stroke='dark', rx=4)
    svg.text(650, 253, "增強後的 Prompt", size=FS_SMALL, bold=True)
    svg.mono(450, 278, "基於以下法條回答問題：", size=FS_TINY)
    svg.mono(450, 298, "[《刑法》第232條...]  問：故意殺人罪判幾年？", size=FS_TINY)

    # Generated answer
    svg.rect(20, 345, 840, 80, fill='light', stroke='border')
    svg.text(w / 2, 363, "生成的回答", size=FS_SMALL, bold=True)
    svg.mono(30, 390, "根據《刑法》第232條，故意殺人罪處死刑、無期徒刑或十年以上有期徒刑；", size=FS_TINY)
    svg.mono(30, 412, "情節較輕的，處三年以上十年以下有期徒刑。", size=FS_TINY)

    svg.save(os.path.join(OUT, 'fig3-2.svg'))


# ──────────────────────── fig3-3 ────────────────────────

def fig3_3():
    """稠密嵌入技術演進"""
    w, h = 860, 340
    svg = SVG(w, h)
    svg.text(w / 2, 30, "稠密嵌入技術演進", size=FS_TITLE, bold=True)

    items = [
        ("Word2Vec", "2013", "300維\n靜態詞向量", "共現關係\n預測訓練"),
        ("GloVe", "2014", "300維\n全域性統計", "矩陣分解\n+ 共現"),
        ("BERT", "2018", "768維\n上下文感知", "Transformer\nMLM預訓練"),
        ("Sentence-BERT", "2019", "768維\n句子級嵌入", "孿生網路\n對比學習"),
        ("BGE-M3", "2024", "1024維\n多語言長文字", "多階段\n混合訓練"),
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
             "靜態詞向量（一詞一向量）", size=FS_SMALL, fill='text_light')
    svg.text(pad_l + gap * 3.5, h - 18,
             "上下文感知嵌入（一詞多向量）", size=FS_SMALL, fill='text_light')

    svg.line(pad_l + gap * 1.5, 75, pad_l + gap * 1.5, h - 35, color='dark', dash=True)

    svg.save(os.path.join(OUT, 'fig3-3.svg'))


# ──────────────────────── fig3-4 ────────────────────────

def fig3_4():
    """HNSW 索引結構"""
    w, h = 750, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "HNSW 索引結構", size=FS_TITLE, bold=True)

    layers = [
        ("Layer 2（稀疏 · 長程連線）", 70, 3),
        ("Layer 1（中等密度）", 185, 6),
        ("Layer 0（稠密 · 全節點）", 300, 10),
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
    svg.text(w / 2 + 80, 148, "搜尋從頂層開始", size=FS_SMALL, fill='text_light')
    svg.arrow(w / 2 - 50, 245, w / 2 - 80, 280, color='border')
    svg.text(w / 2 + 60, 263, "逐層向下精煉", size=FS_SMALL, fill='text_light')

    # Key properties
    svg.rect(50, h - 45, 300, 32, fill='light')
    svg.text(200, h - 29, "支援增量更新 · 高召回率", size=FS_SMALL, bold=True)
    svg.rect(400, h - 45, 300, 32, fill='code_bg', stroke='dark', rx=4)
    svg.text(550, h - 29, "O(log N) 查詢複雜度", size=FS_SMALL)

    svg.save(os.path.join(OUT, 'fig3-4.svg'))


# ──────────────────────── fig3-5 ────────────────────────

def fig3_5():
    """BM25 評分機制"""
    w, h = 800, 380
    svg = SVG(w, h)
    svg.text(w / 2, 30, "BM25 評分機制", size=FS_TITLE, bold=True)

    # Formula
    svg.rect(40, 50, w - 80, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(60, 75,
             "Score(Q,D) = Σ IDF(qi) × TF(qi,D)×(k1+1) / (TF + k1×(1-b+b×|D|/avgdl))",
             size=FS_SMALL)

    # Three components
    boxes = [
        ("詞頻飽和 (TF)", 40, 'light', [
            "k₁ 控制飽和速度",
            "詞頻 ↑ 但貢獻遞減",
            "例: 出現 5→10 次",
            "得分僅增 ~20%",
        ]),
        ("逆文件頻率 (IDF)", 290, 'light', [
            "衡量詞的稀有度",
            "\"的\" → IDF ≈ 0",
            "\"量刑\" → IDF ≈ 5.2",
            "稀有詞權重 >> 常見詞",
        ]),
        ("長度歸一化 (b)", 540, 'light', [
            "b ∈ [0,1] 歸一化強度",
            "b=0: 不考慮長度",
            "b=1: 完全歸一化",
            "避免長文件偏倚",
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
    svg.text(w / 2, 339, "最終得分 = Σ  (TF飽和 × IDF加權 × 長度歸一化)", size=FS_BODY, bold=True)

    svg.save(os.path.join(OUT, 'fig3-5.svg'))


# ──────────────────────── fig3-6 ────────────────────────

def fig3_6():
    """混合檢索與重排序流水線（含分數示例）"""
    w, h = 880, 480
    svg = SVG(w, h)
    svg.text(w / 2, 30, "混合檢索與重排序流水線", size=FS_TITLE, bold=True)

    # Query
    svg.rect(30, 55, 160, 50, fill='medium')
    svg.text(110, 73, "使用者查詢", size=FS_BODY, bold=True)
    svg.mono(110, 93, '"kitty behavior"', size=FS_TINY, anchor='middle')

    # Dense retrieval
    svg.arrow(190, 68, 238, 68)
    svg.box(240, 50, 180, 50, "稠密檢索", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 118, "語義匹配: kitty ≈ cat", size=FS_SMALL, fill='text_light')

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
    svg.box(240, 250, 180, 50, "稀疏檢索 (BM25)", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 318, "精確匹配: \"kitty\" 關鍵詞", size=FS_SMALL, fill='text_light')

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
    svg.text(825, 250, "合併", size=FS_BODY, bold=True)
    svg.text(825, 275, "去重", size=FS_BODY, bold=True)
    svg.text(825, 300, "6→5", size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-6.svg'))


# ──────────────────────── fig3-7 ────────────────────────

def fig3_7():
    """RAPTOR 樹狀結構"""
    w, h = 800, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "RAPTOR 樹狀層次索引", size=FS_TITLE, bold=True)

    # Root
    svg.box(300, 55, 200, 50, "全域性摘要", fill='dark', bold=True, font_size=FS_BODY)
    svg.text(300 + 200 + 15, 80, "← 根節點", size=FS_SMALL, fill='text_light', anchor='start')

    # Mid-level
    mid_nodes = [("聚類摘要 A", 80), ("聚類摘要 B", 320), ("聚類摘要 C", 560)]
    for label, x in mid_nodes:
        svg.box(x, 150, 160, 48, label, fill='medium', font_size=FS_BODY)
    svg.line(400, 105, 160, 150, color='border')
    svg.line(400, 105, 400, 150, color='border')
    svg.line(400, 105, 640, 150, color='border')
    svg.text(35, 230, "中間層 ↑", size=FS_SMALL, fill='text_light', anchor='start')

    # Leaf nodes — 7 boxes evenly distributed, narrower to avoid overlap
    chunks = [
        [(40, "文字塊 1"), (140, "文字塊 2"), (240, "文字塊 3")],   # 聚類 A → cluster center ~160
        [(360, "文字塊 4"), (460, "文字塊 5")],                    # 聚類 B → cluster center ~410
        [(560, "文字塊 6"), (660, "文字塊 7")],                    # 聚類 C → cluster center ~640
    ]
    leaf_w = 88
    mid_cxs = [160, 400, 640]
    for gi, group in enumerate(chunks):
        for cx, label in group:
            svg.box(cx, 250, leaf_w, 40, label, fill='light', font_size=FS_SMALL)
            svg.line(cx + leaf_w / 2, 250, mid_cxs[gi], 198, color='dark')
    svg.text(35, 295, "葉子層 ↑", size=FS_SMALL, fill='text_light', anchor='start')

    # Original document
    svg.rect(40, 320, 720, 55, fill='white', stroke='dark', dash=True)
    svg.text(400, 340, "原始文件", size=FS_BODY, fill='text_light')
    for bx in range(60, 720, 110):
        svg.rect(bx, 350, 90, 16, fill='light')

    # Bottom label
    svg.text(w / 2, h - 20, "自下而上遞迴抽象：細節 → 主題 → 全域性概覽", size=FS_BODY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-7.svg'))


# ──────────────────────── fig3-8 ────────────────────────

def fig3_8():
    """GraphRAG 關係網路"""
    w, h = 750, 430
    svg = SVG(w, h)
    svg.text(w / 2, 28, "GraphRAG 實體-關係知識圖譜", size=FS_TITLE, bold=True)

    nodes = [
        ("Intel", 375, 100, 'medium'),
        ("SSE", 150, 190, 'light'),
        ("AVX", 550, 190, 'light'),
        ("XMM暫存器", 100, 320, 'light'),
        ("ADDPS", 280, 340, 'light'),
        ("YMM暫存器", 520, 320, 'light'),
        ("浮點運算", 375, 250, 'light'),
    ]
    node_r = 42

    # Community box（先繪製，作為底層背景，避免覆蓋後續節點和連線）
    svg.rect(50, 275, 300, 110, fill='none', stroke='border', dash=True)
    svg.text(200, 395, "社群: SSE 指令集", size=FS_SMALL, fill='text_light')

    for label, x, y, fill in nodes:
        svg.circle(x, y, node_r, fill=fill, label=label, font_size=FS_SMALL)

    edges = [
        (0, 1, "開發"), (0, 2, "開發"),
        (1, 3, "使用"), (1, 6, ""), (1, 4, "包含指令"),
        (2, 5, "使用"), (2, 6, "執行"),
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
    """Agentic RAG 與 Non-Agentic RAG 對比（具體示例）"""
    w, h = 880, 560
    svg = SVG(w, h)
    col_w = 400
    lx, rx = 20, 460

    # --- Left: Non-Agentic ---
    svg.rect(lx, 50, col_w, 45, fill='medium')
    svg.text(lx + col_w / 2, 73, "Non-Agentic RAG", size=FS_BODY, bold=True)

    steps_l = [
        ("查詢: \"醉酒過失致人重傷\n且有盜竊前科如何量刑？\"", 'light'),
        ("單次檢索:\n\"過失致人重傷量刑\"", 'light'),
        ("檢索結果: 僅找到過失傷害\n基本法條（上下文不完整）", 'code_bg'),
        ("直接生成: 遺漏\"醉酒\"\n和\"前科\"影響因素", 'light'),
    ]
    prev_y = 95
    for i, (s, fill) in enumerate(steps_l):
        y = 110 + i * 108
        svg.box(lx + 30, y, 340, 80, s, fill=fill, font_size=FS_SMALL)
        if i > 0:
            svg.arrow(lx + 200, prev_y + 80 + 2, lx + 200, y - 2)
        prev_y = y

    svg.text(lx + col_w / 2, h - 15, "單次直通 · 資訊不完整", size=FS_BODY, fill='text_light')

    # --- Separator ---
    svg.line(440, 50, 440, h - 5, color='dark', dash=True)

    # --- Right: Agentic ---
    svg.rect(rx, 50, col_w, 45, fill='medium')
    svg.text(rx + col_w / 2, 73, "Agentic RAG (ReAct)", size=FS_BODY, bold=True)

    steps_r = [
        ("思考: 需要分解為3個子問題", 'light'),
        ("搜尋①: \"過失致人重傷量刑\"\n搜尋②: \"醉酒刑事責任\"\n搜尋③: \"盜竊前科影響\"", 'code_bg'),
        ("觀察: 找到基本法條但\n缺少\"前科\"與\"過失傷害\"關聯", 'light'),
        ("搜尋④: \"累犯 不同罪名\n司法解釋\"", 'code_bg'),
        ("綜合: 完整回答含全部\n法條依據和量刑分析", 'medium'),
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

    svg.text(rx + col_w / 2, h - 15, "多輪迭代 · 資訊完整", size=FS_BODY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-9.svg'))


# ──────────────────────── fig3-10 ────────────────────────

def fig3_10():
    """Agentic RAG 系統架構（實驗 3.6）"""
    w, h = 880, 500
    svg = SVG(w, h)
    svg.text(w / 2, 30, "實驗 3.6：Agentic RAG 系統架構", size=FS_TITLE, bold=True)

    # Agent core
    svg.rect(220, 55, 440, 200, fill='white', stroke='border')
    svg.text(440, 78, "Agent (ReAct 迴圈)", size=FS_BODY, bold=True)

    # ReAct steps inside agent
    react_items = [
        ("① Thought (思考)", 240, 100, 180, 45, 'light'),
        ("② Action (行動)", 460, 100, 180, 45, 'medium'),
        ("③ Observation (觀察)", 350, 180, 180, 45, 'light'),
    ]
    for label, bx, by, bw, bh, fill in react_items:
        svg.box(bx, by, bw, bh, label, fill=fill, font_size=FS_SMALL, bold=True)

    svg.arrow(420, 122, 458, 122)
    svg.arrow(640, 130, 530, 178, color='border')
    svg.arrow(350, 202, 280, 145, color='border')

    # Loop label
    svg.text(360, 165, "迴圈直到資訊充分", size=FS_TINY, fill='text_light')

    # User
    svg.box(20, 95, 160, 55, "使用者查詢", fill='medium', bold=True, font_size=FS_BODY)
    svg.arrow(180, 122, 218, 122)

    # Final answer
    svg.box(700, 95, 160, 55, "最終回答", fill='medium', bold=True, font_size=FS_BODY)
    svg.arrow(660, 122, 698, 122)

    # Tool layer
    svg.rect(100, 290, 680, 85, fill='white', stroke='border', dash=True)
    svg.text(440, 312, "工具層", size=FS_BODY, bold=True)
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
    svg.text(440, 420, "知識庫後端（可切換）", size=FS_BODY, bold=True)
    backends = [
        ("retrieval-pipeline\n混合檢索", 120),
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
    """上下文感知檢索（具體字首示例）"""
    w, h = 880, 430
    svg = SVG(w, h)
    svg.text(w / 2, 30, "上下文感知檢索", size=FS_TITLE, bold=True)

    # Left: Traditional chunking
    svg.rect(20, 55, 400, 170, fill='white', stroke='border')
    svg.text(220, 78, "傳統分塊（無上下文）", size=FS_BODY, bold=True)

    svg.rect(40, 95, 360, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(50, 112, "該公司第二季度的收入增長了3%，", size=FS_TINY)
    svg.mono(50, 132, "主要由新產品線驅動。", size=FS_TINY)

    svg.text(220, 170, "問題：\"該公司\"是誰？哪一年？", size=FS_SMALL, fill='text_light')
    svg.text(220, 195, "→ 檢索時匹配大量無關公司的收入資料", size=FS_SMALL, fill='text_light')

    # Right: Contextual
    svg.rect(460, 55, 400, 170, fill='white', stroke='border')
    svg.text(660, 78, "上下文感知分塊", size=FS_BODY, bold=True)

    svg.rect(480, 95, 360, 35, fill='medium')
    svg.mono(490, 113, "[ACME公司 2025年Q2財報·關鍵業績指標]", size=FS_TINY)

    svg.rect(480, 130, 360, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(490, 148, "該公司第二季度的收入增長了3%，", size=FS_TINY)
    svg.mono(490, 168, "主要由新產品線驅動。", size=FS_TINY)

    svg.text(660, 200, "→ 精確匹配 ACME + Q2 + 收入增長", size=FS_SMALL, fill='text_light')

    # Arrow between
    svg.text(440, 140, "→", size=FS_TITLE, bold=True)

    # Process flow
    svg.line(20, 250, 860, 250, color='dark', dash=True)
    svg.text(w / 2, 275, "索引階段：LLM 生成上下文字首", size=FS_BODY, bold=True)

    flow_y = 300
    svg.box(30, flow_y, 180, 55, "原始文件", fill='light', bold=True, font_size=FS_BODY)
    svg.arrow(210, flow_y + 27, 248, flow_y + 27)

    svg.box(250, flow_y, 180, 55, "分塊", fill='light', bold=True, font_size=FS_BODY)
    svg.arrow(430, flow_y + 27, 468, flow_y + 27)

    svg.box(470, flow_y, 180, 55, "LLM 生成字首\n(prompt caching)", fill='medium',
            font_size=FS_SMALL, bold=True)
    svg.arrow(650, flow_y + 27, 688, flow_y + 27)

    svg.box(690, flow_y, 170, 55, "字首 + 原文\n→ 索引", fill='light', font_size=FS_SMALL, bold=True)

    # Stats
    svg.text(w / 2, h - 20,
             "效果：檢索失敗率 ↓49%（+BM25），↓67%（+重排序）—— Anthropic 資料",
             size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-11.svg'))


# ──────────────────────── fig3-12 ────────────────────────

def fig3_12():
    """結構化知識提取流水線（實驗 3.10）"""
    w, h = 880, 510
    svg = SVG(w, h)
    svg.text(w / 2, 30, "實驗 3.10：結構化知識提取（司法判例）", size=FS_TITLE, bold=True)

    # Phase 1 header
    svg.rect(20, 55, 840, 200, fill='white', stroke='border')
    svg.text(440, 78, "階段一：知識提取與結構化", size=FS_BODY, bold=True)

    # Raw cases
    svg.rect(40, 95, 180, 65, fill='code_bg', stroke='dark', rx=4)
    svg.text(130, 113, "原始判例文書", size=FS_SMALL, bold=True)
    svg.mono(50, 138, "CAIL2018 資料集", size=FS_TINY)

    svg.arrow(220, 127, 258, 127)

    # LLM extraction
    svg.rect(260, 95, 180, 65, fill='medium')
    svg.text(350, 113, "LLM 因子發現", size=FS_SMALL, bold=True)
    svg.text(350, 138, "自下而上 Schema", size=FS_SMALL, fill='text_light')

    svg.arrow(440, 127, 478, 127)

    # Structured JSON
    svg.rect(480, 95, 200, 65, fill='code_bg', stroke='dark', rx=4)
    svg.text(580, 113, "結構化 JSON", size=FS_SMALL, bold=True)
    svg.mono(490, 138, "{自首:true, 賠償:50萬,", size=FS_TINY)
    svg.mono(490, 155, " 傷害等級:重傷二級}", size=FS_TINY)

    # Schema detail
    svg.rect(40, 170, 400, 70, fill='light')
    svg.text(240, 188, "模組化資料模式", size=FS_SMALL, bold=True)
    svg.text(240, 212, "核心模式（自首/賠償/前科）+ 罪名擴充套件模式", size=FS_SMALL, fill='text_light')
    svg.text(240, 232, "（盜竊→涉案金額, 傷害→傷害等級）", size=FS_SMALL, fill='text_light')

    # Phase 2 header
    svg.rect(20, 270, 840, 200, fill='white', stroke='border')
    svg.text(440, 293, "階段二：因子分析與知識建模", size=FS_BODY, bold=True)

    # Vectorization
    svg.rect(40, 310, 200, 65, fill='light')
    svg.text(140, 328, "特徵向量化", size=FS_SMALL, bold=True)
    svg.text(140, 350, "獨熱編碼 + 多熱編碼", size=FS_SMALL, fill='text_light')
    svg.text(140, 370, "+ 對數變換 + 標準化", size=FS_SMALL, fill='text_light')

    svg.arrow(240, 342, 278, 342)

    # Clustering
    svg.rect(280, 310, 200, 65, fill='medium')
    svg.text(380, 328, "HDBSCAN 聚類", size=FS_SMALL, bold=True)
    svg.text(380, 350, "發現\"案件原型\"", size=FS_SMALL, fill='text_light')
    svg.text(380, 370, "如: 輕微口角→輕傷", size=FS_SMALL, fill='text_light')

    svg.arrow(480, 342, 518, 342)

    # Factor importance
    svg.rect(520, 310, 200, 65, fill='light')
    svg.text(620, 328, "因子重要性模型", size=FS_SMALL, bold=True)
    svg.text(620, 350, "量化各因素權重", size=FS_SMALL, fill='text_light')
    svg.text(620, 370, "構建量刑決策邏輯", size=FS_SMALL, fill='text_light')

    # Application
    svg.arrow(620, 375, 620, 400)
    svg.rect(40, 400, 720, 60, fill='light')
    svg.text(400, 420, "應用：對話式法律諮詢 Agent", size=FS_BODY, bold=True)
    svg.text(400, 445, "按因子重要性引導提問 → 檢索相似案件原型 → 資料驅動的量刑分析",
             size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-12.svg'))


# ──────────────────────── fig3-13 ────────────────────────

def fig3_13():
    """外部化學習迴圈（具體示例）"""
    w, h = 880, 490
    svg = SVG(w, h)
    svg.text(w / 2, 30, "外部化學習：從經驗到能力的閉環", size=FS_TITLE, bold=True)

    # Central Agent
    cx, cy = 440, 210
    svg.circle(cx, cy, 55, fill='medium', label="Agent", font_size=FS_BODY)

    # 5 steps around the loop
    steps = [
        ("① 執行任務", 120, 100, "處理退款請求\n呼叫客服API"),
        ("② 獲得反饋", 680, 100, "成功退款$45\n發現需驗證後四位"),
        ("③ 反思與提煉", 680, 310, "LLM 總結經驗:\n\"A公司退款須驗證\""),
        ("④ 存入知識庫", 340, 380, "經驗→向量化索引\n流程→生成工具程式碼"),
        ("⑤ 未來檢索複用", 120, 310, "相似任務→檢索經驗\n直接複用成功策略"),
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
    svg.text(120, 409, "知識: 概要/樹形總結", size=FS_SMALL, fill='white')
    svg.rect(670, 395, 180, 28, fill='dark')
    svg.text(760, 409, "工具: 流程→程式碼", size=FS_SMALL, fill='white')

    svg.save(os.path.join(OUT, 'fig3-13.svg'))


# ──────────────────────── fig3-14 ────────────────────────

def fig3_14():
    """GAIA 經驗學習系統（實驗 3.11）"""
    w, h = 880, 510
    svg = SVG(w, h)
    svg.text(w / 2, 30, "實驗 3.11：GAIA 經驗學習系統", size=FS_TITLE, bold=True)

    box_h = 60
    step_gap = 75
    base_y = 100

    # --- Left: Learning Mode ---
    lx = 20
    svg.rect(lx, 55, 400, 420, fill='white', stroke='border')
    svg.text(lx + 200, 80, "學習模式 (Learning Mode)", size=FS_BODY, bold=True)

    learn_steps = [
        ("GAIA 任務", 'medium', "複雜多步驟問題"),
        ("Agent 執行", 'light', "瀏覽器+檔案+程式碼直譯器"),
        ("任務成功？", 'light', "自動評估 (AWorld)"),
        ("LLM 反思 & 總結", 'medium', "提煉策略摘要"),
        ("經驗 → 向量化", 'light', "存入經驗知識庫"),
    ]
    for i, (label, fill, sub) in enumerate(learn_steps):
        y = base_y + i * step_gap
        svg.box(lx + 50, y, 300, box_h, label, sublabel=sub, fill=fill, bold=True, font_size=FS_BODY)
        if i > 0:
            svg.arrow(lx + 200, base_y + (i - 1) * step_gap + box_h + 2, lx + 200, y - 2)

    # --- Right: Apply Mode ---
    rx = 460
    svg.rect(rx, 55, 400, 420, fill='white', stroke='border')
    svg.text(rx + 200, 80, "應用模式 (Apply Mode)", size=FS_BODY, bold=True)

    apply_steps = [
        ("新 GAIA 任務", 'medium', "接收新問題"),
        ("語義檢索經驗", 'light', "在經驗庫中搜尋相似任務"),
        ("注入 System Prompt", 'medium', "歷史成功策略作為範例"),
        ("Agent 執行", 'light', "借鑑經驗，更高效解題"),
        ("成功率 ↑ 效率 ↑", 'dark', "自進化: 越做越強"),
    ]
    for i, (label, fill, sub) in enumerate(apply_steps):
        y = base_y + i * step_gap
        svg.box(rx + 50, y, 300, box_h, label, sublabel=sub, fill=fill, bold=True, font_size=FS_BODY)
        if i > 0:
            svg.arrow(rx + 200, base_y + (i - 1) * step_gap + box_h + 2, rx + 200, y - 2)

    # Arrow from learning to apply: the experience KB (centered vertically)
    kb_cy = base_y + 2 * step_gap + box_h / 2  # 與第 3 步中心對齊
    kb_x1, kb_x2 = 375, 505
    svg.rect(kb_x1, kb_cy - 25, kb_x2 - kb_x1, 50, fill='dark')
    svg.text((kb_x1 + kb_x2) / 2, kb_cy - 8, "經驗知識庫", size=FS_SMALL, fill='white', bold=True)
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
