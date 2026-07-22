#!/usr/bin/env python3
"""Chapter 8 figures — Agent's self-evolution.

NOTE: this generator was previously a stray copy of chapter 9's figures, which
left fig8-1..fig8-7 showing chapter-9 content. It has been rewritten so each
figure matches its caption in chapter8.md. Figures are built with svg_lib;
titles live in the body text (svg_lib strips in-figure titles).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_lib import SVG, FS_SMALL, FS_TINY, FS_BODY

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')


def _pipeline(stages, fname, W=880, feedback=None):
    """Horizontal stage pipeline with an optional dashed feedback loop."""
    n = len(stages)
    bw = min(190, (W - 40 - (n - 1) * 22) // n)
    bh, gap = 84, 22
    H = 234 if feedback else 174   # +24 for the 40px title-crop margin
    s = SVG(W, H)
    x0 = (W - (n * bw + (n - 1) * gap)) / 2
    y = 48                          # start below the TITLE_CROP_PX=40 line
    pos = []
    for i, (lab, sub) in enumerate(stages):
        x = x0 + i * (bw + gap)
        s.box(x, y, bw, bh, lab, sublabel=sub, bold=True, fill='light')
        pos.append(x)
        if i > 0:
            s.arrow(pos[i - 1] + bw + 2, y + bh / 2, x - 2, y + bh / 2)
    if feedback:
        lx = pos[-1] + bw / 2
        fx = pos[0] + bw / 2
        ry = y + bh + 34
        s.line(lx, y + bh, lx, ry, dash=True)
        s.line(lx, ry, fx, ry, dash=True)
        s.arrow(fx, ry, fx, y + bh + 2, dash=True)
        s.text((lx + fx) / 2, ry + 18, feedback, size=FS_SMALL, fill='text_light')
    s.save(os.path.join(OUT, fname + '.svg'))


def fig8_1():  #Externalized learning loop
    _pipeline([("タスクの完了", "生の経験を生成"), ("経験の精製", "要約・圧縮・構造化"),
               ("外部システムに保存", "知識ベース/ツール、検索可能"), ("検索して再利用", "次のタスクで呼び出す")],
              'fig8-1', feedback="経験は永続的に蓄積され、セッションを越えて再利用される")


def fig8_2():  #GAIA experience learning system
    _pipeline([("成功した軌跡", "タスク完了のプロセス"), ("方策の要約", "知識の要約へ精製"),
               ("知識要約ベース", "意味的インデックスを構築"), ("検索による注入", "Agent が意思決定時に使用")],
              'fig8-2', feedback="類似タスクで過去の経験を再利用")


def fig8_3():  #Hierarchical tool matching (server level → tool level)
    W, H = 620, 354
    s = SVG(W, H)
    cx = W / 2
    s.box(cx - 150, 46, 300, 52, "ユーザークエリ", sublabel="「このファイルをデバッグして」", bold=True, fill='light')
    s.arrow(cx, 100, cx, 120)
    s.box(cx - 220, 122, 440, 62, "レイヤー1: サーバーレベルの意味検索",
          sublabel="数百の MCP サーバー → 関連する Top-K サーバーを想起", bold=True, fill='light')
    s.arrow(cx, 186, cx, 208)
    s.box(cx - 220, 210, 440, 62, "レイヤー2: ツールレベルの意味検索",
          sublabel="Top-K サーバーのツール内でのみマッチ → Top-N ツール", bold=True, fill='light')
    s.arrow(cx, 274, cx, 296)
    s.box(cx - 150, 298, 300, 46, "選択されたツール",
          sublabel="候補範囲を大幅に絞り込み、選択コストを削減", bold=True, fill='light')
    s.save(os.path.join(OUT, 'fig8-3.svg'))


def fig8_4():  #KV Cache Optimization for Dynamic Tool Loading (Naive vs Optimized)
    W, H = 860, 244
    s = SVG(W, H)
    s.text(220, 46, "素朴な方式: 全ツール定義をシステムプロンプトに配置", size=FS_SMALL, bold=True, fill='darker')
    s.rect(30, 62, 380, 70, fill='#f0d8d8')
    s.text(220, 84, "システムプロンプト + 全ツール定義", size=FS_SMALL, bold=True)
    s.text(220, 108, "ツールの変更 → KV キャッシュ全体が無効化", size=FS_TINY, fill='text_light')
    s.rect(30, 140, 380, 46, fill='light')
    s.text(220, 163, "毎ラウンド再計算、高コスト", size=FS_SMALL)

    s.text(640, 46, "最適化方式: ツール定義をオンデマンドで読み込み", size=FS_SMALL, bold=True, fill='darker')
    s.rect(450, 62, 380, 40, fill='#d8e8d8')
    s.text(640, 82, "安定したシステムプロンプト（キャッシュヒットする接頭辞）", size=FS_SMALL, bold=True)
    s.rect(450, 106, 380, 40, fill='light')
    s.text(640, 126, "オンデマンドで追加されるツール定義（変化する部分）", size=FS_SMALL)
    s.rect(450, 150, 380, 40, fill='light')
    s.text(640, 170, "会話の軌跡", size=FS_SMALL)
    s.text(640, 206, "安定した接頭辞は不変 → KV Cache を継続的に再利用", size=FS_TINY, fill='text_light')
    s.line(430, 54, 430, 220, dash=True)
    s.save(os.path.join(OUT, 'fig8-4.svg'))


def fig8_5():  #Agent Self-Evolution Pipeline (Requirement Identification → Tool Search → Code Encapsulation → Tool Registration)
    _pipeline([("① ニーズの特定", "既存ツールでは不十分"), ("② ツール検索", "オープンワールド検索"),
               ("③ コードのカプセル化", "生成してカプセル化"), ("④ ツールの登録", "ライブラリに組み込み再利用")],
              'fig8-5', feedback="新たに登録されたツールは後続のタスクで再利用され、能力の境界を継続的に拡張する")


def fig8_6():  #Voyager Continuous Learning Architecture (Curriculum Generator + Skill Library + Iterative Prompting)
    _pipeline([("カリキュラム生成器", "段階的に新しいタスクを提案"), ("反復的プロンプティング機構", "スキルコードを生成しデバッグ"),
               ("スキルライブラリ", "再利用可能なスキルを保存")],
              'fig8-6', W=760, feedback="スキルの蓄積がより難しいタスクを解放（オープンワールド探索）")


def fig8_7():  #Experiment 8-5 Self-Evolution Pipeline (Search → Evaluate → Test → Encapsulate → Reuse)
    _pipeline([("① 検索", "オープンなネットワークでツールを探す"), ("② 評価", "適合性を判断"), ("③ テスト", "使用可能かを検証"),
               ("④ パッケージ化", "標準ツールへ包む"), ("⑤ 再利用", "ツールライブラリに組み込む")],
              'fig8-7', W=940, feedback="新しいツールは蓄積され後続のタスクで再利用される")


if __name__ == '__main__':
    for fn in (fig8_1, fig8_2, fig8_3, fig8_4, fig8_5, fig8_6, fig8_7):
        fn()
        print('saved', fn.__name__)
