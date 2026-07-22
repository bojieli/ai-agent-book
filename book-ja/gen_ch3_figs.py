#!/usr/bin/env python3
"""Generate all SVG illustrations for Chapter 3 (Knowledge Base & RAG).

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
    """Knowledge map of this chapter"""
    w, h = 860, 580
    svg = SVG(w, h)

    svg.text(w / 2, 32, "第3章：知識ベースと RAG — 知識マップ", size=FS_TITLE, bold=True)

    # --- Row 1: RAG foundations ---
    r1_y = 70
    svg.rect(30, r1_y, 800, 130, fill='white', stroke='border', dash=True)
    svg.text(80, r1_y + 20, "RAG の基礎", size=FS_BODY, bold=True, anchor='start')

    boxes_r1 = [
        ("密ベクトル埋め込み", 50, "Word2Vec → BGE-M3"),
        ("疎ベクトル埋め込み", 230, "TF-IDF / BM25"),
        ("ハイブリッド検索＋リランキング", 410, "二塔検索 + Cross-Encoder"),
        ("マルチモーダル抽出", 650, "ネイティブ / テキスト / ツール"),
    ]
    for label, bx, sub in boxes_r1:
        svg.box(bx, r1_y + 38, 160, 50, label, fill='light', bold=True, font_size=FS_SMALL)
        svg.text(bx + 80, r1_y + 38 + 50 + 18, sub, size=FS_TINY, fill='text_light')

    # --- Arrow down ---
    svg.arrow(w / 2, r1_y + 130, w / 2, r1_y + 160)

    # --- Row 2: Advanced knowledge structuring ---
    r2_y = 230
    svg.rect(30, r2_y, 800, 100, fill='white', stroke='border', dash=True)
    svg.text(80, r2_y + 20, "既存の知識から学ぶ", size=FS_BODY, bold=True, anchor='start')

    boxes_r2 = [
        ("RAPTOR\n 木構造の階層インデックス", 50),
        ("GraphRAG\n エンティティ関係グラフ", 230),
        ("エージェント化 RAG\n ツールとしての検索", 410),
        ("コンテキスト対応検索\n プレフィックス要約による強化", 590),
    ]
    for label, bx in boxes_r2:
        svg.box(bx, r2_y + 35, 160, 55, label, fill='medium', font_size=FS_SMALL)

    # --- Arrow down ---
    svg.arrow(w / 2, r2_y + 100, w / 2, r2_y + 130)

    # --- Row 3: Learning from experience ---
    r3_y = 360
    svg.rect(30, r3_y, 800, 100, fill='white', stroke='border', dash=True)
    svg.text(80, r3_y + 20, "自律的な探索から学ぶ", size=FS_BODY, bold=True, anchor='start')

    boxes_r3 = [
        ("ポストトレーニング\n RL → マッスルメモリ", 100),
        ("インコンテキスト学習\n 推論時のソフト検索", 330),
        ("外部化学習\n 知識ベース＋ツール生成", 560),
    ]
    for label, bx in boxes_r3:
        svg.box(bx, r3_y + 35, 200, 55, label, fill='light', font_size=FS_SMALL)

    # --- Bottom: core insight ---
    svg.rect(180, 490, 500, 44, fill='dark')
    svg.text(w / 2, 512, "Bitter Lesson：探索＋学習＝汎用的な手法", size=FS_BODY, fill='white', bold=True)
    svg.arrow(w / 2, r3_y + 100, w / 2, 488)

    svg.save(os.path.join(OUT, 'fig3-1.svg'))


# ──────────────────────── fig3-2 ────────────────────────

def fig3_2():
    """RAG End-to-End Pipeline (Concrete Example)"""
    w, h = 880, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "RAG のエンドツーエンドパイプライン", size=FS_TITLE, bold=True)

    # Step 1: User query
    svg.box(20, 65, 180, 55, "① ユーザークエリ", fill='medium', bold=True, font_size=FS_BODY)
    q_lines = ['「故意殺人は何年の刑になるか？」']
    svg.text(110, 145, q_lines[0], size=FS_SMALL, fill='text_light')

    svg.arrow(200, 92, 238, 92)

    # Step 2: Retrieval
    svg.box(240, 65, 180, 55, "② 検索", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 140, "密検索 + BM25", size=FS_SMALL, fill='text_light')
    svg.text(330, 160, "→ 上位 K 件のテキストチャンク", size=FS_SMALL, fill='text_light')

    svg.arrow(420, 92, 458, 92)

    # Step 3: Augmentation
    svg.box(460, 65, 180, 55, "③ 拡張", fill='light', bold=True, font_size=FS_BODY)
    svg.text(550, 140, "クエリ＋検索結果", size=FS_SMALL, fill='text_light')
    svg.text(550, 160, "→ 完全なプロンプトを構築", size=FS_SMALL, fill='text_light')

    svg.arrow(640, 92, 678, 92)

    # Step 4: Generation
    svg.box(680, 65, 180, 55, "④ 生成", fill='medium', bold=True, font_size=FS_BODY)
    svg.text(770, 140, "LLM がコンテキストを統合", size=FS_SMALL, fill='text_light')
    svg.text(770, 160, "→ 回答を生成", size=FS_SMALL, fill='text_light')

    # Concrete data flow example
    svg.line(20, 195, 860, 195, color='dark', dash=True)
    svg.text(w / 2, 215, "データフローの例", size=FS_BODY, bold=True)

    # Retrieved chunks
    svg.rect(20, 235, 400, 90, fill='code_bg', stroke='dark', rx=4)
    svg.text(220, 253, "検索されたテキストチャンク", size=FS_SMALL, bold=True)
    svg.mono(30, 278, "刑法第232条：故意に他人を殺害した者は、死刑、", size=FS_TINY)
    svg.mono(30, 298, "無期懲役または10年以上の有期懲役に処する……", size=FS_TINY)

    # Augmented prompt
    svg.rect(440, 235, 420, 90, fill='code_bg', stroke='dark', rx=4)
    svg.text(650, 253, "拡張されたプロンプト", size=FS_SMALL, bold=True)
    svg.mono(450, 278, "以下の法律の条文に基づいて質問に答えてください：", size=FS_TINY)
    svg.mono(450, 298, "[刑法第232条……] Q：故意殺人の量刑は？", size=FS_TINY)

    # Generated answer
    svg.rect(20, 345, 840, 80, fill='light', stroke='border')
    svg.text(w / 2, 363, "生成された回答", size=FS_SMALL, bold=True)
    svg.mono(30, 390, "刑法第232条によると、故意殺人罪は死刑、無期懲役または10年以上の有期懲役に処せられる。", size=FS_TINY)
    svg.mono(30, 412, "情状が軽い場合は、3年以上10年以下の有期懲役に処せられる。", size=FS_TINY)

    svg.save(os.path.join(OUT, 'fig3-2.svg'))


# ──────────────────────── fig3-3 ────────────────────────

def fig3_3():
    """Evolution of dense embedding techniques"""
    w, h = 860, 340
    svg = SVG(w, h)
    svg.text(w / 2, 30, "密な埋め込み技術の進化", size=FS_TITLE, bold=True)

    items = [
        ("Word2Vec", "2013", "300次元\n静的な単語ベクトル", "共起\n予測的学習"),
        ("GloVe", "2014", "300次元\nグローバル統計", "行列分解\n＋共起"),
        ("BERT", "2018", "768次元\nコンテキスト対応", "Transformer\nMLM 事前学習"),
        ("Sentence-BERT", "2019", "768次元\n文レベルの埋め込み", "シャム（Siamese）ネットワーク\n対照学習"),
        ("BGE-M3", "2024", "1024次元\n多言語・長文", "多段階\nハイブリッド学習"),
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
             "静的な単語ベクトル（1単語につき1ベクトル）", size=FS_SMALL, fill='text_light')
    svg.text(pad_l + gap * 3.5, h - 18,
             "コンテキスト対応の埋め込み（1単語につき複数ベクトル）", size=FS_SMALL, fill='text_light')

    svg.line(pad_l + gap * 1.5, 75, pad_l + gap * 1.5, h - 35, color='dark', dash=True)

    svg.save(os.path.join(OUT, 'fig3-3.svg'))


# ──────────────────────── fig3-4 ────────────────────────

def fig3_4():
    """HNSW index structure"""
    w, h = 750, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "HNSW インデックス構造", size=FS_TITLE, bold=True)

    layers = [
        ("レイヤー2（疎・長距離接続）", 70, 3),
        ("レイヤー1（中密度）", 185, 6),
        ("レイヤー0（密・全ノード）", 300, 10),
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
    svg.text(w / 2 + 80, 148, "最上位レイヤーから探索を開始", size=FS_SMALL, fill='text_light')
    svg.arrow(w / 2 - 50, 245, w / 2 - 80, 280, color='border')
    svg.text(w / 2 + 60, 263, "下位レイヤーへ段階的に絞り込む", size=FS_SMALL, fill='text_light')

    # Key properties
    svg.rect(50, h - 45, 300, 32, fill='light')
    svg.text(200, h - 29, "増分更新に対応・高い再現率", size=FS_SMALL, bold=True)
    svg.rect(400, h - 45, 300, 32, fill='code_bg', stroke='dark', rx=4)
    svg.text(550, h - 29, "O(log N) のクエリ計算量", size=FS_SMALL)

    svg.save(os.path.join(OUT, 'fig3-4.svg'))


# ──────────────────────── fig3-5 ────────────────────────

def fig3_5():
    """BM25 scoring mechanism"""
    w, h = 800, 380
    svg = SVG(w, h)
    svg.text(w / 2, 30, "BM25 のスコアリング機構", size=FS_TITLE, bold=True)

    # Formula
    svg.rect(40, 50, w - 80, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(60, 75,
             "Score(Q,D) = Σ IDF(qi) × TF(qi,D)×(k1+1) / (TF + k1×(1-b+b×|D|/avgdl))",
             size=FS_SMALL)

    # Three components
    boxes = [
        ("単語頻度の飽和（TF）", 40, 'light', [
            "k₁ が飽和の速さを制御",
            "TF ↑ でも寄与は逓減",
            "例：出現5→10回",
            "スコアの増加はわずか約20%",
        ]),
        ("逆文書頻度（IDF）", 290, 'light', [
            "単語の希少性を測る",
            "「の」 → IDF ≈ 0",
            "「量刑」 → IDF ≈ 5.2",
            "希少語の重み >> 一般語",
        ]),
        ("文書長の正規化（b）", 540, 'light', [
            "b ∈ [0,1] は正規化の強さ",
            "b=0：文書長を無視",
            "b=1：完全に正規化",
            "長文への偏りを防ぐ",
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
    svg.text(w / 2, 339, "最終スコア = Σ（TF 飽和 × IDF 重み付け × 文書長正規化）", size=FS_BODY, bold=True)

    svg.save(os.path.join(OUT, 'fig3-5.svg'))


# ──────────────────────── fig3-6 ────────────────────────

def fig3_6():
    """Hybrid retrieval and re-ranking pipeline (with score examples)"""
    w, h = 880, 480
    svg = SVG(w, h)
    svg.text(w / 2, 30, "ハイブリッド検索とリランキングのパイプライン", size=FS_TITLE, bold=True)

    # Query
    svg.rect(30, 55, 160, 50, fill='medium')
    svg.text(110, 73, "ユーザークエリ", size=FS_BODY, bold=True)
    svg.mono(110, 93, '「にゃんこの行動」', size=FS_TINY, anchor='middle')

    # Dense retrieval
    svg.arrow(190, 68, 238, 68)
    svg.box(240, 50, 180, 50, "密検索", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 118, "意味的マッチング：にゃんこ ≈ 猫", size=FS_SMALL, fill='text_light')

    dense_results = [
        ("doc3:「猫の習性と遊び……」", "cos=0.87"),
        ("doc7:「猫のグルーミングの習性……」", "cos=0.82"),
        ("doc1:「ペットケアの基礎……」", "cos=0.71"),
    ]
    for i, (doc, score) in enumerate(dense_results):
        y = 140 + i * 32
        svg.mono(250, y, doc, size=FS_TINY)
        svg.text(700, y, score, size=FS_TINY, fill='text_light', anchor='start')

    # Sparse retrieval
    svg.arrow(190, 90, 238, 270)
    svg.box(240, 250, 180, 50, "疎検索（BM25）", fill='light', bold=True, font_size=FS_BODY)
    svg.text(330, 318, "完全一致：「にゃんこ」キーワード", size=FS_SMALL, fill='text_light')

    sparse_results = [
        ("doc5:「にゃんこのトイレのしつけ……」", "BM25=8.4"),
        ("doc9:「にゃんこの里親ガイド……」", "BM25=6.1"),
        ("doc2:「子猫の健康アドバイス……」", "BM25=3.2"),
    ]
    for i, (doc, score) in enumerate(sparse_results):
        y = 340 + i * 32
        svg.mono(250, y, doc, size=FS_TINY)
        svg.text(700, y, score, size=FS_TINY, fill='text_light', anchor='start')

    # Merge + rerank
    svg.arrow(770, 180, 808, 220)
    svg.arrow(770, 370, 808, 330)

    svg.rect(790, 215, 70, 120, fill='medium')
    svg.text(825, 250, "統合", size=FS_BODY, bold=True)
    svg.text(825, 275, "重複除去", size=FS_BODY, bold=True)
    svg.text(825, 300, "6→5", size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-6.svg'))


# ──────────────────────── fig3-7 ────────────────────────

def fig3_7():
    """RAPTOR tree structure"""
    w, h = 800, 440
    svg = SVG(w, h)
    svg.text(w / 2, 30, "RAPTOR の木構造による階層インデックス", size=FS_TITLE, bold=True)

    # Root
    svg.box(300, 55, 200, 50, "全体要約", fill='dark', bold=True, font_size=FS_BODY)
    svg.text(300 + 200 + 15, 80, "← ルートノード", size=FS_SMALL, fill='text_light', anchor='start')

    # Mid-level
    mid_nodes = [("クラスタ要約 A", 80), ("クラスタ要約 B", 320), ("クラスタ要約 C", 560)]
    for label, x in mid_nodes:
        svg.box(x, 150, 160, 48, label, fill='medium', font_size=FS_BODY)
    svg.line(400, 105, 160, 150, color='border')
    svg.line(400, 105, 400, 150, color='border')
    svg.line(400, 105, 640, 150, color='border')
    svg.text(35, 230, "中間層 ↑", size=FS_SMALL, fill='text_light', anchor='start')

    # Leaf nodes — 7 boxes evenly distributed, narrower to avoid overlap
    chunks = [
        [(40, "テキストチャンク1"), (140, "テキストチャンク2"), (240, "テキストチャンク3")],   # Cluster A → cluster center ~160
        [(360, "テキストチャンク4"), (460, "テキストチャンク5")],                    # Cluster B → cluster center ~410
        [(560, "テキストチャンク6"), (660, "テキストチャンク7")],                    # Cluster C → cluster center ~640
    ]
    leaf_w = 88
    mid_cxs = [160, 400, 640]
    for gi, group in enumerate(chunks):
        for cx, label in group:
            svg.box(cx, 250, leaf_w, 40, label, fill='light', font_size=FS_SMALL)
            svg.line(cx + leaf_w / 2, 250, mid_cxs[gi], 198, color='dark')
    svg.text(35, 295, "リーフ層 ↑", size=FS_SMALL, fill='text_light', anchor='start')

    # Original document
    svg.rect(40, 320, 720, 55, fill='white', stroke='dark', dash=True)
    svg.text(400, 340, "元の文書", size=FS_BODY, fill='text_light')
    for bx in range(60, 720, 110):
        svg.rect(bx, 350, 90, 16, fill='light')

    # Bottom label
    svg.text(w / 2, h - 20, "ボトムアップの再帰的抽象化：詳細 → トピック → 全体像", size=FS_BODY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-7.svg'))


# ──────────────────────── fig3-8 ────────────────────────

def fig3_8():
    """GraphRAG relational network"""
    w, h = 750, 430
    svg = SVG(w, h)
    svg.text(w / 2, 28, "GraphRAG のエンティティ関係知識グラフ", size=FS_TITLE, bold=True)

    nodes = [
        ("Intel", 375, 100, 'medium'),
        ("SSE", 150, 190, 'light'),
        ("AVX", 550, 190, 'light'),
        ("XMMレジスタ", 100, 320, 'light'),
        ("ADDPS", 280, 340, 'light'),
        ("YMMレジスタ", 520, 320, 'light'),
        ("FP演算", 375, 250, 'light'),
    ]
    node_r = 42

    # Community box (drawn first, as background layer, to avoid covering subsequent nodes and edges)
    svg.rect(50, 275, 300, 110, fill='none', stroke='border', dash=True)
    svg.text(200, 395, "コミュニティ：SSE 命令セット", size=FS_SMALL, fill='text_light')

    for label, x, y, fill in nodes:
        svg.circle(x, y, node_r, fill=fill, label=label, font_size=FS_SMALL)

    edges = [
        (0, 1, "開発"), (0, 2, "開発"),
        (1, 3, "使用"), (1, 6, ""), (1, 4, "含む"),
        (2, 5, "使用"), (2, 6, "実行"),
        (6, 3, ""), (6, 5, "演算"),
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
    """Agentic RAG vs Non-Agentic RAG (Specific Example)"""
    w, h = 880, 560
    svg = SVG(w, h)
    col_w = 400
    lx, rx = 20, 460

    # --- Left: Non-Agentic ---
    svg.rect(lx, 50, col_w, 45, fill='medium')
    svg.text(lx + col_w / 2, 73, "非エージェント型 RAG", size=FS_BODY, bold=True)

    steps_l = [
        ("クエリ：「飲酒状態で過失により重傷を負わせ、\nかつ窃盗の前科がある場合の量刑は？」", 'light'),
        ("単一の検索：\n「過失により重傷を負わせた場合の量刑」", 'light'),
        ("検索結果：過失傷害の基本的な条文のみを発見\n（コンテキストが不完全）", 'code_bg'),
        ("直接生成：「飲酒」と「前科」という\n影響要因が欠落", 'light'),
    ]
    prev_y = 95
    for i, (s, fill) in enumerate(steps_l):
        y = 110 + i * 108
        svg.box(lx + 30, y, 340, 80, s, fill=fill, font_size=FS_SMALL)
        if i > 0:
            svg.arrow(lx + 200, prev_y + 80 + 2, lx + 200, y - 2)
        prev_y = y

    svg.text(lx + col_w / 2, h - 15, "単一パス・不完全な情報", size=FS_BODY, fill='text_light')

    # --- Separator ---
    svg.line(440, 50, 440, h - 5, color='dark', dash=True)

    # --- Right: Agentic ---
    svg.rect(rx, 50, col_w, 45, fill='medium')
    svg.text(rx + col_w / 2, 73, "エージェント化 RAG（ReAct）", size=FS_BODY, bold=True)

    steps_r = [
        ("思考：3つのサブ質問に分解する必要がある", 'light'),
        ("検索①：「過失により重傷を負わせた場合の量刑」\n検索②：「飲酒に対する刑事責任」\n検索③：「窃盗の前科の影響」", 'code_bg'),
        ("観察：基本的な条文は見つかったが\n「前科」と「過失傷害」の関連が欠けている", 'light'),
        ("検索④：「異なる罪種の累犯\n司法解釈」", 'code_bg'),
        ("統合：すべての法律の条文と量刑分析を\n含む完全な回答", 'medium'),
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
    svg.text(loop_x + 4, (ys[1] + ys[2]) / 2 + 34, "反復", size=FS_SMALL, fill='text_light',
             anchor='start')

    svg.text(rx + col_w / 2, h - 15, "複数回の反復・完全な情報", size=FS_BODY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-9.svg'))


# ──────────────────────── fig3-10 ────────────────────────

def fig3_10():
    """Agentic RAG System Architecture (Experiment 3.6)"""
    w, h = 880, 500
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 3.6：エージェント化 RAG のシステムアーキテクチャ", size=FS_TITLE, bold=True)

    # Agent core
    svg.rect(220, 55, 440, 200, fill='white', stroke='border')
    svg.text(440, 78, "Agent（ReAct ループ）", size=FS_BODY, bold=True)

    # ReAct steps inside agent
    react_items = [
        ("① 思考", 240, 100, 180, 45, 'light'),
        ("② 行動", 460, 100, 180, 45, 'medium'),
        ("③ 観察", 350, 180, 180, 45, 'light'),
    ]
    for label, bx, by, bw, bh, fill in react_items:
        svg.box(bx, by, bw, bh, label, fill=fill, font_size=FS_SMALL, bold=True)

    svg.arrow(420, 122, 458, 122)
    svg.arrow(640, 130, 530, 178, color='border')
    svg.arrow(350, 202, 280, 145, color='border')

    # Loop label
    svg.text(360, 165, "情報が十分になるまでループ", size=FS_TINY, fill='text_light')

    # User
    svg.box(20, 95, 160, 55, "ユーザークエリ", fill='medium', bold=True, font_size=FS_BODY)
    svg.arrow(180, 122, 218, 122)

    # Final answer
    svg.box(700, 95, 160, 55, "最終的な回答", fill='medium', bold=True, font_size=FS_BODY)
    svg.arrow(660, 122, 698, 122)

    # Tool layer
    svg.rect(100, 290, 680, 85, fill='white', stroke='border', dash=True)
    svg.text(440, 312, "ツール層", size=FS_BODY, bold=True)
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
    svg.text(440, 420, "知識ベースのバックエンド（切り替え可能）", size=FS_BODY, bold=True)
    backends = [
        ("retrieval-pipeline\nハイブリッド検索", 120),
        ("structured-index\nRAPTOR/GraphRAG", 340),
        ("contextual-retrieval\nコンテキスト対応", 560),
    ]
    for label, bx in backends:
        svg.box(bx, 435, 180, 45, label, fill='light', font_size=FS_SMALL)

    svg.arrow(230, 365, 230, 398)
    svg.arrow(440, 375, 440, 398)

    svg.save(os.path.join(OUT, 'fig3-10.svg'))


# ──────────────────────── fig3-11 ────────────────────────

def fig3_11():
    """Context-aware retrieval (specific prefix example)"""
    w, h = 880, 430
    svg = SVG(w, h)
    svg.text(w / 2, 30, "コンテキスト対応検索", size=FS_TITLE, bold=True)

    # Left: Traditional chunking
    svg.rect(20, 55, 400, 170, fill='white', stroke='border')
    svg.text(220, 78, "従来のチャンク分割（コンテキストなし）", size=FS_BODY, bold=True)

    svg.rect(40, 95, 360, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(50, 112, "同社の第2四半期の売上は3%増加し、", size=FS_TINY)
    svg.mono(50, 132, "主に新製品ラインが牽引した。", size=FS_TINY)

    svg.text(220, 170, "疑問：「同社」とはどこの会社？どの年？", size=FS_SMALL, fill='text_light')
    svg.text(220, 195, "→ 検索が無関係な多数の企業の売上データに一致してしまう", size=FS_SMALL, fill='text_light')

    # Right: Contextual
    svg.rect(460, 55, 400, 170, fill='white', stroke='border')
    svg.text(660, 78, "コンテキスト対応のチャンク分割", size=FS_BODY, bold=True)

    svg.rect(480, 95, 360, 35, fill='medium')
    svg.mono(490, 113, "[ACME 社 2025年 Q2 決算報告 ・ 主要業績指標]", size=FS_TINY)

    svg.rect(480, 130, 360, 50, fill='code_bg', stroke='dark', rx=4)
    svg.mono(490, 148, "同社の第2四半期の売上は3%増加し、", size=FS_TINY)
    svg.mono(490, 168, "主に新製品ラインが牽引した。", size=FS_TINY)

    svg.text(660, 200, "→ ACME + Q2 + 売上成長 に正確に一致", size=FS_SMALL, fill='text_light')

    # Arrow between
    svg.text(440, 140, "→", size=FS_TITLE, bold=True)

    # Process flow
    svg.line(20, 250, 860, 250, color='dark', dash=True)
    svg.text(w / 2, 275, "インデックス化の段階：LLM がコンテキストのプレフィックスを生成", size=FS_BODY, bold=True)

    flow_y = 300
    svg.box(30, flow_y, 180, 55, "元の文書", fill='light', bold=True, font_size=FS_BODY)
    svg.arrow(210, flow_y + 27, 248, flow_y + 27)

    svg.box(250, flow_y, 180, 55, "チャンク分割", fill='light', bold=True, font_size=FS_BODY)
    svg.arrow(430, flow_y + 27, 468, flow_y + 27)

    svg.box(470, flow_y, 180, 55, "LLM がプレフィックスを生成\n（プロンプトキャッシュ）", fill='medium',
            font_size=FS_SMALL, bold=True)
    svg.arrow(650, flow_y + 27, 688, flow_y + 27)

    svg.box(690, flow_y, 170, 55, "プレフィックス＋元のテキスト\n→ インデックス", fill='light', font_size=FS_SMALL, bold=True)

    # Stats
    svg.text(w / 2, h - 20,
             "効果：検索失敗率 ↓49%（+BM25）、↓67%（+リランキング）— Anthropic のデータ",
             size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-11.svg'))


# ──────────────────────── fig3-12 ────────────────────────

def fig3_12():
    """Structured knowledge extraction pipeline (Experiment 3.10)"""
    w, h = 880, 510
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 3.10：構造化された知識抽出（判例）", size=FS_TITLE, bold=True)

    # Phase 1 header
    svg.rect(20, 55, 840, 200, fill='white', stroke='border')
    svg.text(440, 78, "フェーズ1：知識の抽出と構造化", size=FS_BODY, bold=True)

    # Raw cases
    svg.rect(40, 95, 180, 65, fill='code_bg', stroke='dark', rx=4)
    svg.text(130, 113, "元の判決文書", size=FS_SMALL, bold=True)
    svg.mono(50, 138, "CAIL2018 データセット", size=FS_TINY)

    svg.arrow(220, 127, 258, 127)

    # LLM extraction
    svg.rect(260, 95, 180, 65, fill='medium')
    svg.text(350, 113, "LLM による要因の発見", size=FS_SMALL, bold=True)
    svg.text(350, 138, "ボトムアップのスキーマ", size=FS_SMALL, fill='text_light')

    svg.arrow(440, 127, 478, 127)

    # Structured JSON
    svg.rect(480, 95, 200, 65, fill='code_bg', stroke='dark', rx=4)
    svg.text(580, 113, "構造化された JSON", size=FS_SMALL, bold=True)
    svg.mono(490, 138, "{voluntary_surrender:true, compensation:500000,", size=FS_TINY)
    svg.mono(490, 155, " injury_level:severe_second_degree}", size=FS_TINY)

    # Schema detail
    svg.rect(40, 170, 400, 70, fill='light')
    svg.text(240, 188, "モジュール化されたデータスキーマ", size=FS_SMALL, bold=True)
    svg.text(240, 212, "コアスキーマ（自首／賠償／前科）＋罪状拡張スキーマ", size=FS_SMALL, fill='text_light')
    svg.text(240, 232, "（窃盗→被害額、傷害→傷害の程度）", size=FS_SMALL, fill='text_light')

    # Phase 2 header
    svg.rect(20, 270, 840, 200, fill='white', stroke='border')
    svg.text(440, 293, "フェーズ2：要因分析と知識モデリング", size=FS_BODY, bold=True)

    # Vectorization
    svg.rect(40, 310, 200, 65, fill='light')
    svg.text(140, 328, "特徴のベクトル化", size=FS_SMALL, bold=True)
    svg.text(140, 350, "One-hot エンコーディング＋multi-hot エンコーディング", size=FS_SMALL, fill='text_light')
    svg.text(140, 370, "＋対数変換＋標準化", size=FS_SMALL, fill='text_light')

    svg.arrow(240, 342, 278, 342)

    # Clustering
    svg.rect(280, 310, 200, 65, fill='medium')
    svg.text(380, 328, "HDBSCAN クラスタリング", size=FS_SMALL, bold=True)
    svg.text(380, 350, "「事案プロトタイプ」を発見", size=FS_SMALL, fill='text_light')
    svg.text(380, 370, "例：軽微な口論 → 軽傷", size=FS_SMALL, fill='text_light')

    svg.arrow(480, 342, 518, 342)

    # Factor importance
    svg.rect(520, 310, 200, 65, fill='light')
    svg.text(620, 328, "要因重要度モデル", size=FS_SMALL, bold=True)
    svg.text(620, 350, "各要因の重みを定量化", size=FS_SMALL, fill='text_light')
    svg.text(620, 370, "量刑判断のロジックを構築", size=FS_SMALL, fill='text_light')

    # Application
    svg.arrow(620, 375, 620, 400)
    svg.rect(40, 400, 720, 60, fill='light')
    svg.text(400, 420, "応用：対話型の法律相談 Agent", size=FS_BODY, bold=True)
    svg.text(400, 445, "要因重要度に基づいて質問を誘導 → 類似の事案プロトタイプを検索 → データ駆動の量刑分析",
             size=FS_SMALL, fill='text_light')

    svg.save(os.path.join(OUT, 'fig3-12.svg'))


# ──────────────────────── fig3-13 ────────────────────────

def fig3_13():
    """Externalized learning loop (concrete example)"""
    w, h = 880, 490
    svg = SVG(w, h)
    svg.text(w / 2, 30, "外部化学習：経験から能力への閉ループ", size=FS_TITLE, bold=True)

    # Central Agent
    cx, cy = 440, 210
    svg.circle(cx, cy, 55, fill='medium', label="Agent", font_size=FS_BODY)

    # 5 steps around the loop
    steps = [
        ("① タスクを実行", 120, 100, "返金リクエストを処理\nカスタマーサービス API を呼び出す"),
        ("② フィードバックを取得", 680, 100, "45ドルの返金に成功\n下4桁の確認が必要と判明"),
        ("③ 振り返って抽出", 680, 310, "LLM が経験を要約：\n「A社の返金には確認が必要」"),
        ("④ 知識ベースに保存", 340, 380, "経験 → ベクトル化インデックス\n手順 → ツールコードを生成"),
        ("⑤ 将来の検索と再利用", 120, 310, "類似タスク → 経験を検索\n成功した戦略を直接再利用"),
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
    svg.text(120, 409, "知識：要約／ツリー要約", size=FS_SMALL, fill='white')
    svg.rect(670, 395, 180, 28, fill='dark')
    svg.text(760, 409, "ツール：手順 → コード", size=FS_SMALL, fill='white')

    svg.save(os.path.join(OUT, 'fig3-13.svg'))


# ──────────────────────── fig3-14 ────────────────────────

def fig3_14():
    """GAIA experience learning system (Experiment 3.11)"""
    w, h = 880, 510
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 3.11：GAIA 経験学習システム", size=FS_TITLE, bold=True)

    box_h = 60
    step_gap = 75
    base_y = 100

    # --- Left: Learning Mode ---
    lx = 20
    svg.rect(lx, 55, 400, 420, fill='white', stroke='border')
    svg.text(lx + 200, 80, "学習モード", size=FS_BODY, bold=True)

    learn_steps = [
        ("GAIA タスク", 'medium', "複雑な多段階の問題"),
        ("Agent の実行", 'light', "ブラウザ + ファイル + コードインタプリタ"),
        ("タスクは成功したか？", 'light', "自動評価（AWorld）"),
        ("LLM の振り返りと要約", 'medium', "戦略の要約を抽出"),
        ("経験 → ベクトル化", 'light', "経験知識ベースに保存"),
    ]
    for i, (label, fill, sub) in enumerate(learn_steps):
        y = base_y + i * step_gap
        svg.box(lx + 50, y, 300, box_h, label, sublabel=sub, fill=fill, bold=True, font_size=FS_BODY)
        if i > 0:
            svg.arrow(lx + 200, base_y + (i - 1) * step_gap + box_h + 2, lx + 200, y - 2)

    # --- Right: Apply Mode ---
    rx = 460
    svg.rect(rx, 55, 400, 420, fill='white', stroke='border')
    svg.text(rx + 200, 80, "適用モード", size=FS_BODY, bold=True)

    apply_steps = [
        ("新しい GAIA タスク", 'medium', "新しい質問を受け取る"),
        ("経験の意味的検索", 'light', "経験ベースで類似タスクを検索"),
        ("システムプロンプトに注入", 'medium', "過去の成功した戦略を例として"),
        ("Agent の実行", 'light', "経験を活用してより効率的に問題を解決"),
        ("成功率 ↑ 効率 ↑", 'dark', "自己進化：時とともに強くなる"),
    ]
    for i, (label, fill, sub) in enumerate(apply_steps):
        y = base_y + i * step_gap
        svg.box(rx + 50, y, 300, box_h, label, sublabel=sub, fill=fill, bold=True, font_size=FS_BODY)
        if i > 0:
            svg.arrow(rx + 200, base_y + (i - 1) * step_gap + box_h + 2, rx + 200, y - 2)

    # Arrow from learning to apply: the experience KB (centered vertically)
    kb_cy = base_y + 2 * step_gap + box_h / 2  #Align with Step 3 Center
    kb_x1, kb_x2 = 375, 505
    svg.rect(kb_x1, kb_cy - 25, kb_x2 - kb_x1, 50, fill='dark')
    svg.text((kb_x1 + kb_x2) / 2, kb_cy - 8, "経験知識ベース", size=FS_SMALL, fill='white', bold=True)
    svg.text((kb_x1 + kb_x2) / 2, kb_cy + 12, "（ベクトルインデックス）", size=FS_TINY, fill='white')

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
