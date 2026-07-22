#!/usr/bin/env python3
"""Generate all SVG illustrations for Chapter 5 (Code Generation).

Figures (11 total):
  fig5-1:  OpenClaw architecture — Coding Agent as core of general Agent
  fig5-2:  Coding Agent multi-phase workflow (concrete file ops & tool calls)
  fig5-3:  Search tool comparison (4 types with real query examples)
  fig5-4:  File editing approach comparison (5 methods with code diffs)
  fig5-5:  PPT generation pipeline (Proposer-Reviewer with Slidev code)
  fig5-6:  Exp 5.6+5.7 — Paper-to-PPT/Video pipeline
  fig5-7:  Exp 5.10 — Production log diagnosis pipeline
  fig5-8:  Dynamic form generation (LLM → HTML form → JSON → continue)
  fig5-9:  SQL query agent (artifact mode, data bypasses LLM)
  fig5-10: Agent bootstrap cycle (self-replication concept)
  fig5-11: Exp 5.14 — Agent that creates agents (meta-agent)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from svg_lib import (
    SVG, COLORS, FONT, MONO, STROKE_W, CORNER_R, _escape,
    FS_TITLE, FS_BODY, FS_SMALL, FS_TINY, FS_LABEL,
)

OUT = os.path.join(os.path.dirname(__file__), 'images')


def _pill(svg, x, y, w, h, label, fill='light', font_size=FS_SMALL, bold=False):
    svg.rect(x, y, w, h, fill=fill, rx=h // 2)
    c = 'white' if fill in ('dark', 'darker') else 'text'
    svg.text(x + w / 2, y + h / 2, label, size=font_size, fill=c, bold=bold)


# ──────────────────────── fig5-1 (NEW: OpenClaw arch) ──────

def fig5_1():
    """OpenClaw architecture: Coding Agent as core of general Agent"""
    w, h = 980, 600
    svg = SVG(w, h)
    svg.text(w / 2, 30, "OpenClaw アーキテクチャ: 汎用 Agent の中核としての Coding Agent", size=FS_TITLE, bold=True)

    # Top: multi-platform messaging gateway
    gw_y, gw_h = 58, 66
    svg.group_box(60, gw_y, w - 120, gw_h, "マルチプラットフォームメッセージゲートウェイ（ユーザー対話層）")
    channels = ["WhatsApp", "Telegram", "iMessage", "Slack", "CLI"]
    pill_w, pill_h = 130, 32
    total_pw = len(channels) * pill_w + (len(channels) - 1) * 18
    px_start = (w - total_pw) / 2
    for i, ch in enumerate(channels):
        px = px_start + i * (pill_w + 18)
        svg.rect(px, gw_y + 26, pill_w, pill_h, fill='medium', rx=pill_h // 2)
        svg.text(px + pill_w / 2, gw_y + 26 + pill_h / 2, ch, size=FS_SMALL)

    svg.arrow(w / 2, gw_y + gw_h + 2, w / 2, 158)
    svg.text(w / 2 + 12, 134, "自然言語リクエスト", size=FS_LABEL, fill='text_light', anchor='start')

    # Center: Coding Agent runtime — widened to fit 4 tools comfortably
    ca_x, ca_y, ca_w, ca_h = 200, 160, 580, 210
    svg.rect(ca_x, ca_y, ca_w, ca_h, fill='light')
    svg.rect(ca_x, ca_y, ca_w, 40, fill='darker', rx=6)
    svg.text(ca_x + ca_w / 2, ca_y + 20,
             "Coding Agent ランタイム（推論＋実行コア）", size=FS_BODY, bold=True, fill='white')

    tools = [
        ("Code Interpreter", "コード実行"), ("Bash Shell", "システムコマンド"),
        ("Read File", "ファイル読み取り"), ("Write File", "ファイル書き込み"),
        ("Edit File", "ファイル編集"), ("Glob", "ファイル検索"), ("Grep", "内容検索"),
    ]
    tw, th, tgap = 132, 60, 12
    for ri, row in enumerate([tools[:4], tools[4:]]):
        row_total_w = len(row) * tw + (len(row) - 1) * tgap
        rx_start = ca_x + (ca_w - row_total_w) / 2
        ry = ca_y + 56 + ri * (th + tgap)
        for ci, (name, desc) in enumerate(row):
            tx = rx_start + ci * (tw + tgap)
            svg.rect(tx, ry, tw, th, fill='white')
            svg.text(tx + tw / 2, ry + 22, name, size=FS_TINY, bold=True)
            svg.text(tx + tw / 2, ry + 42, desc, size=FS_TINY, fill='text_light')

    # Left: Deep Research
    dr_x, dr_y, dr_w, dr_h = 22, 198, 158, 86
    svg.rect(dr_x, dr_y, dr_w, dr_h, fill='medium')
    svg.text(dr_x + dr_w / 2, dr_y + 22, "Web 検索モジュール", size=FS_SMALL, bold=True)
    svg.text(dr_x + dr_w / 2, dr_y + 44, "Deep Research", size=FS_TINY, fill='text_light')
    svg.text(dr_x + dr_w / 2, dr_y + 66, "Web リクエスト・解析", size=FS_TINY, fill='text_light')
    svg.arrow(dr_x + dr_w + 2, dr_y + dr_h / 2, ca_x - 2, ca_y + ca_h / 2)

    # Right: Computer Use
    cu_x, cu_y, cu_w, cu_h = 800, 198, 158, 86
    svg.rect(cu_x, cu_y, cu_w, cu_h, fill='medium')
    svg.text(cu_x + cu_w / 2, cu_y + 22, "ブラウザ自動化", size=FS_SMALL, bold=True)
    svg.text(cu_x + cu_w / 2, cu_y + 44, "Computer Use", size=FS_TINY, fill='text_light')
    svg.text(cu_x + cu_w / 2, cu_y + 66, "Playwright DOM", size=FS_TINY, fill='text_light')
    svg.arrow(ca_x + ca_w + 2, ca_y + ca_h / 2, cu_x - 2, cu_y + cu_h / 2)

    # Bottom: file system layer
    fs_y, fs_h = 410, 140
    svg.arrow(w / 2, ca_y + ca_h + 2, w / 2, fs_y - 2)
    svg.text(w / 2 + 12, 390, "ファイルの読み取り／書き込み", size=FS_LABEL, fill='text_light', anchor='start')
    svg.group_box(60, fs_y, w - 120, fs_h, "ファイルシステム（メモリ・知識・能力ハブ）")

    mem_items = [
        ("MEMORY.md", "高レベルの事実／ユーザー設定"),
        ("daily/YYYY-MM-DD.md", "日次アーカイブ／対話ログ"),
        ("SOUL.md", "Agent のアイデンティティと行動ルール"),
        ("知識ベースファイル", "タスク経験／自己進化"),
        ("Git バージョン管理", "メモリのロールバック／履歴監査"),
    ]
    item_w, item_h, item_gap = 162, 76, 16
    total_iw = len(mem_items) * item_w + (len(mem_items) - 1) * item_gap
    ix_start = (w - total_iw) / 2
    for i, (title, desc) in enumerate(mem_items):
        ix = ix_start + i * (item_w + item_gap)
        iy = fs_y + 34
        svg.rect(ix, iy, item_w, item_h, fill='white')
        svg.text(ix + item_w / 2, iy + 26, title, size=FS_TINY, bold=True)
        svg.text(ix + item_w / 2, iy + 52, desc, size=FS_TINY, fill='text_light')

    # Very bottom: LLM as OS
    os_y = fs_y + fs_h + 16
    svg.rect(60, os_y, w - 120, 38, fill='darker', rx=6)
    svg.text(w / 2, os_y + 19,
             "LLM ＝ 新しいオペレーティングシステム：知能の複雑さを隠蔽し、統一された抽象を提供", size=FS_SMALL, bold=True, fill='white')

    svg.save(os.path.join(OUT, 'fig5-1.svg'))


# ──────────────────────── fig5-2 (was fig5-1) ────────────────────────

def fig5_2():
    """Coding Agent multi-phase workflow (concrete tool calls)"""
    w, h = 880, 580
    svg = SVG(w, h)
    svg.text(w / 2, 30, "Coding Agent の階層型ワークフロー", size=FS_TITLE, bold=True)

    phases = [
        ("① プロジェクトドキュメント化", 'medium', [
            ("read_file", "README.md, ARCHITECTURE.md"),
            ("glob", "**/*.py, **/*.ts"),
            ("write_file", "→ CLAUDE.md プロジェクトガイドを生成"),
        ]),
        ("② 要件理解", 'light', [
            ("ask_user", "「最適化の目標はレイテンシかスループットか？」"),
            ("grep", "\"latency|throughput\" src/"),
            ("read_file", "src/config.py（現在のパラメータ）"),
        ]),
        ("③ 設計ドキュメント", 'light', [
            ("write_file", "design.md（方式比較）"),
            ("ask_user", "設計を提出 → 承認待ち"),
            ("—", "人間のレビュー後 → 続行"),
        ]),
        ("④ コーディングとテスト", 'medium', [
            ("edit_file", "old_str→new_str でコード修正"),
            ("bash", "pytest tests/ -v"),
            ("edit_file", "失敗したテストを修正 → 再実行"),
        ]),
        ("⑤ レビューと納品", 'light', [
            ("bash", "ruff check src/（lint）"),
            ("read_file", "セルフレビュー：可読性／セキュリティ／パフォーマンス"),
            ("edit_file", "ARCHITECTURE.md を更新"),
        ]),
    ]

    phase_w = 155
    phase_gap = 12
    total_w = len(phases) * phase_w + (len(phases) - 1) * phase_gap
    sx = (w - total_w) / 2

    for i, (title, fill, steps) in enumerate(phases):
        x = sx + i * (phase_w + phase_gap)
        ph = 240
        svg.rect(x, 55, phase_w, ph, fill=fill)
        svg.text(x + phase_w / 2, 78, title, size=FS_SMALL, bold=True)
        svg.line(x + 8, 92, x + phase_w - 8, 92, color='dark')

        for j, (tool, desc) in enumerate(steps):
            ty = 110 + j * 70
            _pill(svg, x + 8, ty, phase_w - 16, 22, tool, fill='dark', font_size=11, bold=True)
            svg.text_block(x + 10, ty + 26, phase_w - 20, desc.split('\n'),
                           size=10, min_size=7, anchor='start', mono=True, line_gap=1.45)

        if i < len(phases) - 1:
            ax = x + phase_w + 2
            svg.arrow(ax, 55 + ph / 2, ax + phase_gap - 4, 55 + ph / 2)

    # Bottom: feedback loops
    svg.line(30, 320, w - 30, 320, color='dark', dash=True)
    svg.text(w / 2, 340, "クローズドループのフィードバック機構", size=FS_BODY, bold=True)

    loops = [
        ("テスト失敗 → コード修正 → 再テスト", "④ 内側ループ：平均 2〜3 ラウンドで収束"),
        ("Lint エラー → 即修正 → 再チェック", "⑤ 内側ループ：編集後に自動でトリガー"),
        ("レビューで問題発見 → ④ に戻って修正", "⑤→④ ロールバック：納品品質を保証"),
    ]
    ly = 365
    for label, note in loops:
        svg.rect(80, ly, 500, 46, fill='light')
        svg.text(330, ly + 15, label, size=FS_SMALL, bold=True)
        svg.text(330, ly + 34, note, size=FS_TINY, fill='text_light')
        ly += 50

    # Annotations on the right
    annots = [
        "Agent ステータスバー：cwd、git ブランチ",
        "Agent ステータスバー：未ステージの変更",
        "ツール出力：head/tail による切り詰め",
        "永続的なターミナルセッション",
    ]
    for i, ann in enumerate(annots):
        svg.rect(610, 365 + i * 50, 250, 38, fill='code_bg', stroke='dark', rx=4)
        svg.text(735, 384 + i * 50, ann, size=FS_TINY, fill='text_light')

    svg.text(w / 2, 565, "行動前に計画・全過程で検証・ドキュメントとコードが共進化", size=FS_BODY, bold=True, fill='darker')

    svg.save(os.path.join(OUT, 'fig5-2.svg'))


# ──────────────────────── fig5-3 ────────────────────────

def fig5_3():
    """Search tool comparison (four tools + actual query examples)"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "4 つの検索ツールの比較", size=FS_TITLE, bold=True)

    tools = [
        ("正規表現による内容マッチ（grep）", 'medium',
         "rg \"def handle_.*\" --type py",
         ["src/api.py:42:  def handle_request(..)",
          "src/api.py:89:  def handle_timeout(..)",
          "src/ws.py:15:   def handle_connect(..)"],
         "厳密なテキスト → すべての出現位置"),
        ("ファイル名マッチ（glob）", 'light',
         "glob: **/test_*.py",
         ["tests/test_api.py",
          "tests/test_auth.py",
          "tests/unit/test_parser.py"],
         "パスパターン → ファイル内容は読まない"),
        ("セマンティックコード検索", 'light',
         "「ユーザー入力のバリデーション処理」",
         ["[0.91] src/validators.py:validate_input()",
          "[0.87] src/forms.py:sanitize_fields()",
          "[0.82] src/api.py:check_params()"],
         "自然言語 → ベクトル + BM25 ハイブリッド"),
        ("シンボル定義／参照", 'medium',
         "find_references: UserService",
         ["定義: src/services/user.py:12",
          "参照: src/api/routes.py:34 (import)",
          "参照: src/api/routes.py:56 (call)",
          "参照: tests/test_user.py:8 (test)"],
         "AST レベル → 同名を区別"),
    ]

    col_w = (w - 60) // 2
    col_gap = 20

    for i, (title, fill, query, results, note) in enumerate(tools):
        col = i % 2
        row = i // 2
        x = 20 + col * (col_w + col_gap)
        y = 55 + row * 260

        svg.rect(x, y, col_w, 240, fill='white', stroke='border')
        svg.rect(x, y, col_w, 36, fill=fill, rx=CORNER_R)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(x + col_w / 2, y + 18, title, size=FS_SMALL, bold=True, fill=tc)

        svg.text(x + 12, y + 54, "クエリ:", size=FS_TINY, bold=True, anchor='start', fill='text_light')
        svg.rect(x + 8, y + 64, col_w - 16, 24, fill='code_bg', stroke='dark', rx=3)
        svg.mono(x + 14, y + 76, query, size=11)

        svg.text(x + 12, y + 102, "結果:", size=FS_TINY, bold=True, anchor='start', fill='text_light')
        rh = len(results) * 20 + 12
        svg.rect(x + 8, y + 112, col_w - 16, rh, fill='code_bg', stroke='dark', rx=3)
        for j, r in enumerate(results):
            svg.mono(x + 14, y + 128 + j * 20, r, size=10)

        svg.text(x + col_w / 2, y + 226, note, size=FS_TINY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig5-3.svg'))


# ──────────────────────── fig5-3 ────────────────────────

def fig5_4():
    """File Editing Scheme Comparison (Five Methods + Code Examples)"""
    w, h = 900, 700
    svg = SVG(w, h)
    svg.text(w / 2, 28, "5 つのファイル編集方式の比較", size=FS_TITLE, bold=True)

    approaches = [
        ("Diff ＋ Apply モデル", "dark",
         ["LLM が Diff 記述を出力:",
          "- def foo(x):",
          "    return x",
          "+ def foo(x, y=0):",
          "+   return x + y",
          "→ 小モデルが位置特定して適用"],
         "利点：関心の分離",
         "欠点：わずかなズレで位置ずれが発生"),
        ("旧文字列 → 新文字列", "medium",
         ['old: "def foo(x):\\n',
          '       return x"',
          'new: "def foo(x, y=0):\\n',
          '       return x + y"',
          "→ 厳密な文字列マッチで置換"],
         "利点：予測可能で曖昧さがない",
         "欠点：大量削除では全文出力が必要"),
        ("行番号による位置指定", "light",
         ["42〜43 行目を削除して挿入:",
          "  def foo(x, y=0):",
          "    return x + y",
          "",
          "→ 行番号で正確な範囲を指定"],
         "利点：大規模な操作で効率的",
         "欠点：長いファイルでは行番号がずれやすい"),
        ("Vim 風コマンド", "light",
         ["42G  (42 行目へジャンプ)",
          "cw   (単語を置換)",
          "dd   (行を削除)",
          "yy/p (コピー／貼り付け)",
          "→ 豊富な編集セマンティクス"],
         "利点：移動／再編成が効率的",
         "欠点：弱いモデルではエラーが増える"),
        ("先頭・末尾マッチ", "medium",
         ['start: "def foo(x):"',
          'end:   "    return x"',
          'new: "def foo(x, y=0):',
          '       return x + y"',
          "→ 境界だけで位置特定できる"],
         "利点：全文出力なしで大量削除",
         "欠点：境界の組み合わせが一意でなければならない"),
    ]

    col_w = 168
    col_gap = 10
    total_cw = len(approaches) * col_w + (len(approaches) - 1) * col_gap
    sx = (w - total_cw) / 2

    max_code_h = max(len(a[2]) for a in approaches) * 17 + 14
    py = 101 + max_code_h + 12   # common top for every Adv/Disadv box (keeps them aligned)
    box_h = 80
    for i, (title, fill, code_lines, pro, con) in enumerate(approaches):
        x = sx + i * (col_w + col_gap)

        svg.rect(x, 55, col_w, 38, fill=fill, rx=CORNER_R)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(x + col_w / 2, 74, title, size=FS_TINY, bold=True, fill=tc)

        code_h = len(code_lines) * 17 + 14
        svg.rect(x, 101, col_w, code_h, fill='code_bg', stroke='dark', rx=3)
        for j, line in enumerate(code_lines):
            svg.mono(x + 6, 117 + j * 17, line, size=11)

        svg.rect(x + 4, py, col_w - 8, box_h, fill='white', stroke='dark', rx=3)
        svg.text_block(x + col_w / 2, py + 5, col_w - 18,
                       [(pro, 'text'), (con, 'text_light')], size=FS_TINY - 2,
                       min_size=9, line_gap=1.18)

    # Adoption bar chart at bottom
    chart_y = py + box_h + 22
    svg.line(30, chart_y, w - 30, chart_y, color='dark', dash=True)
    svg.text(w / 2, chart_y + 24, "実際の採用状況", size=FS_BODY, bold=True)

    adoptions = [
        ("旧→新", "Claude Code", 0.85, 'dark'),
        ("行番号による位置指定", "IDE 深統合シナリオ", 0.50, 'medium'),
        ("Diff ＋ Apply", "Cursor", 0.40, 'light'),
        ("先頭・末尾マッチ", "一部のカスタムソリューション", 0.30, 'light'),
        ("Vim コマンド", "実験的なソリューション", 0.15, 'code_bg'),
    ]
    bar_x, bar_w_max = 250, 480
    by = chart_y + 48
    for label, products, ratio, fill in adoptions:
        svg.text(bar_x - 10, by + 14, label, size=FS_TINY, anchor='end', bold=True)
        bw = bar_w_max * ratio
        svg.rect(bar_x, by, bw, 28, fill=fill, rx=3)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(bar_x + bw / 2, by + 14, products, size=FS_TINY, fill=tc)
        by += 38

    svg.save(os.path.join(OUT, 'fig5-4.svg'))


# ──────────────────────── fig5-4 ────────────────────────

def fig5_5():
    """PPT generation pipeline (Proposer-Reviewer collaboration + Slidev code)"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "PPT 生成：Proposer-Reviewer 協調機構", size=FS_TITLE, bold=True)

    # Proposer Agent (left)
    svg.rect(20, 60, 350, 280, fill='white', stroke='border', dash=True)
    svg.text(195, 82, "Proposer Agent", size=FS_BODY, bold=True)

    svg.text(40, 110, "入力：論文／コンテンツ", size=FS_SMALL, anchor='start', bold=True)
    svg.rect(30, 125, 330, 24, fill='code_bg', stroke='dark', rx=3)
    svg.mono(38, 137, "paper.pdf → 節／論点／図を抽出", size=11)

    svg.text(40, 168, "出力：Slidev Markdown", size=FS_SMALL, anchor='start', bold=True)
    code_lines = [
        "---",
        "layout: two-cols",
        "---",
        "# Transformer Architecture",
        "::left::",
        "- Self-attention mechanism",
        "- Multi-head attention",
        "::right::",
        "<img src=\"fig3.png\" />",
    ]
    ch = svg.code_block(30, 182, 330, code_lines, font_size=10, line_h=14)

    # Reviewer Agent (right)
    svg.rect(510, 60, 350, 280, fill='white', stroke='border', dash=True)
    svg.text(685, 82, "Reviewer Agent", size=FS_BODY, bold=True)

    svg.text(520, 110, "ステップ1：スクリーンショットをレンダリング", size=FS_SMALL, anchor='start', bold=True)
    svg.rect(520, 125, 330, 50, fill='light')
    svg.text(685, 142, "slidev export --per-slide", size=FS_TINY, fill='text_light')
    svg.text(685, 160, "→ slide-01.png, slide-02.png ...", size=FS_TINY, fill='text_light')

    svg.text(520, 192, "ステップ2：Vision LLM レビュー", size=FS_SMALL, anchor='start', bold=True)
    critique_lines = [
        "レビュー観点:",
        "  ✓ テキストが境界をはみ出していないか",
        "  ✓ レイアウトが窮屈すぎないか",
        "  ✓ 画像サイズが適切か",
        "  ✗ スライド3：テキストが右カラムをはみ出している",
        "  ✗ スライド7：内容が詰め込みすぎ",
    ]
    svg.rect(520, 208, 330, len(critique_lines) * 16 + 12, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(critique_lines):
        svg.mono(528, 222 + j * 16, line, size=10)

    # Arrows: Proposer → Reviewer → Proposer (loop)
    svg.arrow(370, 200, 508, 150, label="Slidev コード")
    svg.arrow(508, 300, 370, 260, label="修正提案", dash=True)

    # Iteration badge
    _pill(svg, 395, 220, 100, 24, "2〜3 ラウンド反復", fill='dark', font_size=11, bold=True)

    # Bottom: why separate agents
    svg.line(30, 365, w - 30, 365, color='dark', dash=True)
    svg.text(w / 2, 388, "なぜ Proposer と Reviewer を分けるのか？", size=FS_BODY, bold=True)

    reasons = [
        ("単一 Agent の問題", [
            "数十ページのレンダリング済みスクリーンショット → コンテキスト肥大化",
            "コード＋スクリーンショットの混在 → アテンションの分散",
        ]),
        ("分離の利点", [
            "Reviewer の独立したコンテキスト → スクリーンショット＋コードのみ",
            "Proposer はコードに集中 → 修正提案のみを受け取る",
        ]),
        ("実際の効果", [
            "コンテキスト使用量を大幅に削減",
            "修正精度が大幅に向上",
        ]),
    ]
    rx = 30
    for title, items in reasons:
        svg.rect(rx, 405, 270, 130, fill='light')
        svg.text(rx + 135, 425, title, size=FS_SMALL, bold=True)
        for j, item in enumerate(items):
            svg.text(rx + 135, 450 + j * 24, item, size=FS_TINY, fill='text_light')
        rx += 290

    svg.save(os.path.join(OUT, 'fig5-5.svg'))


# ──────────────────────── fig5-5 ────────────────────────

def fig5_6():
    """Experiment 5.6+5.7: Paper→PPT→Video end-to-end pipeline"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 5.6+5.7：論文 → PPT → 講義動画", size=FS_TITLE, bold=True)

    # Top pipeline: paper → PPT
    stages_top = [
        ("PDF 入力", 'medium', [
            "paper.pdf",
            "文書構造を解析",
            "図の参照を抽出",
        ]),
        ("コンテンツ設計", 'light', [
            "10〜20 ページの構成",
            "核心的な論点を抽出",
            "図をページに割り当て",
        ]),
        ("Slidev 生成", 'light', [
            "ページごとに生成",
            "layout: two-cols",
            "コード＋画像のレイアウト",
        ]),
        ("レンダリング検査", 'medium', [
            "export --per-slide",
            "Vision LLM レビュー",
            "はみ出し検出",
        ]),
        ("反復修正", 'light', [
            "Reviewer→Proposer",
            "Slidev コードを修正",
            "再レンダリングして検証",
        ]),
    ]

    sw = 155
    sgap = 10
    total = len(stages_top) * sw + (len(stages_top) - 1) * sgap
    sx = (w - total) / 2

    svg.text(w / 2, 60, "フェーズ1：PPT 生成（Proposer-Reviewer）", size=FS_SMALL, bold=True, fill='text_light')
    for i, (title, fill, details) in enumerate(stages_top):
        x = sx + i * (sw + sgap)
        svg.rect(x, 72, sw, 130, fill=fill)
        svg.text(x + sw / 2, 92, title, size=FS_SMALL, bold=True)
        svg.line(x + 8, 104, x + sw - 8, 104, color='dark')
        for j, line in enumerate(details):
            svg.mono(x + 8, 120 + j * 20, line, size=10)
        if i < len(stages_top) - 1:
            svg.arrow(x + sw + 2, 72 + 65, x + sw + sgap - 2, 72 + 65)

    # Arrow down
    svg.arrow(w / 2, 202, w / 2, 240)
    svg.text(w / 2 + 60, 222, "PPT 完成", size=FS_SMALL, fill='text_light')

    # Bottom pipeline: PPT → Video
    svg.text(w / 2, 255, "フェーズ2：動画合成", size=FS_SMALL, bold=True, fill='text_light')

    stages_bot = [
        ("ページごとのスクリーンショット", 'medium', [
            "slide-01.png",
            "slide-02.png",
            "...",
        ]),
        ("スクリプト生成", 'light', [
            "LLM による口語スクリプト",
            "ページごとのナレーション",
            "誘導的な語り",
        ]),
        ("TTS 合成", 'light', [
            "テキスト → 音声",
            "speech-01.mp3",
            "speech-02.mp3",
        ]),
        ("音声・映像の同期", 'medium', [
            "ffmpeg で合成",
            "音声の長さに合わせる",
            "トランジション効果",
        ]),
        ("最終動画", 'dark', [
            "output.mp4",
            "5〜15 分",
            "音声＋映像出力",
        ]),
    ]

    for i, (title, fill, details) in enumerate(stages_bot):
        x = sx + i * (sw + sgap)
        svg.rect(x, 268, sw, 130, fill=fill)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(x + sw / 2, 288, title, size=FS_SMALL, bold=True, fill=tc)
        svg.line(x + 8, 300, x + sw - 8, 300, color='dark')
        for j, line in enumerate(details):
            fc = 'white' if fill in ('dark', 'darker') else 'text'
            svg.mono(x + 8, 316 + j * 20, line, size=10, fill=fc)
        if i < len(stages_bot) - 1:
            svg.arrow(x + sw + 2, 268 + 65, x + sw + sgap - 2, 268 + 65)

    # Bottom: key metrics
    svg.line(30, 420, w - 30, 420, color='dark', dash=True)
    svg.text(w / 2, 440, "受け入れ基準", size=FS_BODY, bold=True)

    criteria = [
        ("PPT", "10〜20 ページ・主要な貢献を網羅・オリジナル図表 3 点以上"),
        ("レンダリング", "テキストのはみ出しゼロ・妥当なレイアウト・テキストと画像の対応"),
        ("動画", "5〜15 分・音声と映像の同期・一貫したナレーション"),
    ]
    cy = 462
    for label, desc in criteria:
        _pill(svg, 180, cy, 92, 26, label, fill='dark', font_size=12, bold=True)
        svg.text(285, cy + 13, desc, size=FS_TINY, fill='text_light', anchor='start')
        cy += 30

    svg.save(os.path.join(OUT, 'fig5-6.svg'))


# ──────────────────────── fig5-7 ────────────────────────

def fig5_8():
    """Dynamic form generation flow (LLM→HTML→JSON→Continue)"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "動的フォーム生成：構造化された意図の明確化", size=FS_TITLE, bold=True)

    # Step 1: User input
    svg.rect(20, 60, 200, 60, fill='medium')
    svg.text(120, 82, "ユーザー入力", size=FS_SMALL, bold=True)
    svg.text(120, 100, "「北京行きの航空券を予約したい」", size=FS_TINY, fill='text_light')

    svg.arrow(220, 90, 260, 90)

    # Step 2: LLM analyzes and generates form
    svg.rect(260, 55, 260, 140, fill='white', stroke='border', dash=True)
    svg.text(390, 75, "LLM が分析 → フォームコードを生成", size=FS_SMALL, bold=True)
    form_code = [
        '<form id="clarify">',
        ' <input type="text"',
        '  name="from" label="出発都市"/>',
        ' <input type="date"',
        '  name="depart" label="出発日"/>',
        ' <select name="type">',
        '  <option>片道</option>',
        '  <option>往復</option>',
        ' </select>',
        '</form>',
    ]
    svg.rect(270, 90, 240, len(form_code) * 13 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(form_code):
        svg.mono(276, 103 + j * 13, line, size=9)

    svg.arrow(520, 130, 560, 130)

    # Step 3: Rendered form (visual representation)
    svg.rect(560, 55, 300, 200, fill='white', stroke='border')
    svg.text(710, 75, "レンダリングされたフォーム画面", size=FS_SMALL, bold=True)

    fields = [
        ("出発都市", "上海", 95),
        ("出発日", "2025-08-15", 135),
        ("旅程タイプ", "往復 ▾", 175),
        ("復路日", "2025-08-22", 215),
    ]
    for label, value, fy in fields:
        svg.text(580, fy, label, size=FS_TINY, anchor='start', bold=True)
        svg.rect(660, fy - 12, 180, 24, fill='code_bg', stroke='dark', rx=3)
        svg.mono(668, fy, value, size=11)

    _pill(svg, 660, 238, 80, 26, "送信", fill='dark', font_size=FS_SMALL, bold=True)

    # Step 4: JSON result
    svg.arrow(710, 268, 710, 300)
    svg.rect(560, 300, 300, 110, fill='white', stroke='border', dash=True)
    svg.text(710, 318, "構造化された JSON レスポンス", size=FS_SMALL, bold=True)
    json_lines = [
        '{"from": "上海",',
        ' "depart": "2025-08-15",',
        ' "type": "往復",',
        ' "return": "2025-08-22"}',
    ]
    svg.rect(570, 330, 280, len(json_lines) * 16 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(json_lines):
        svg.mono(578, 344 + j * 16, line, size=11)

    # Step 5: Agent continues with structured data
    svg.arrow(560, 390, 400, 440)

    svg.rect(100, 430, 500, 50, fill='medium')
    svg.text(350, 448, "Agent が完全なパラメータで実行を継続", size=FS_BODY, bold=True)
    svg.text(350, 468, "search_flights(from='Shanghai', to='Beijing', depart='2025-08-15', ...)", size=FS_TINY, fill='text_light')

    # Comparison: text vs form
    svg.rect(20, 280, 250, 140, fill='light')
    svg.text(145, 300, "比較：プレーンテキスト vs フォーム", size=FS_SMALL, bold=True)
    comp = [
        "テキスト Q&A：10 ラウンドの対話",
        "  Q1: 出発都市は？ A: 上海",
        "  Q2: 日付は？ A: 8月15日",
        "  Q3: 片道か往復か？ ...",
        "",
        "動的フォーム：1 回の送信",
        "  すべての情報を一度に収集",
        "  カスケードロジックを自動処理",
    ]
    for j, line in enumerate(comp):
        svg.mono(30, 318 + j * 13, line, size=10)

    # Bottom annotation
    svg.text(w / 2, 510, "フォームコードは LLM が動的に生成 → カスケードロジック：「往復」を選択すると復路日を自動表示", size=FS_SMALL, fill='darker')

    svg.save(os.path.join(OUT, 'fig5-8.svg'))


# ──────────────────────── fig5-8 ────────────────────────

def fig5_9():
    """SQL Query Agent (artifact mode — data bypasses LLM)"""
    w, h = 880, 580
    svg = SVG(w, h)
    svg.text(w / 2, 30, "SQL クエリ Agent：Artifact モード vs 従来モード", size=FS_TITLE, bold=True)

    # Top: Traditional mode (data through LLM)
    svg.rect(20, 55, w - 40, 200, fill='white', stroke='border', dash=True)
    svg.text(60, 78, "従来モード：データが LLM を経由する（非効率）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 110, 65, 80, 24, "✗ 非効率", fill='dark', font_size=12, bold=True)

    trad_steps = [
        ("ユーザー", 'medium', "「部門ごとの人数は？」"),
        ("LLM", 'light', "SQL を生成"),
        ("DB", 'medium', "クエリを\\n実行"),
        ("LLM", 'light', "5000 行を\\n読み取り"),
        ("ユーザー", 'medium', "テキストで\\n説明"),
    ]
    tsx = 60
    for i, (name, fill, desc) in enumerate(trad_steps):
        svg.rect(tsx, 100, 130, 60, fill=fill)
        svg.text(tsx + 65, 118, name, size=FS_SMALL, bold=True)
        for j, line in enumerate(desc.split('\\n')):
            svg.text(tsx + 65, 138 + j * 16, line, size=FS_TINY, fill='text_light')
        if i < len(trad_steps) - 1:
            svg.arrow(tsx + 130, 130, tsx + 150, 130)
        tsx += 155

    svg.rect(60, 175, w - 120, 30, fill='code_bg', stroke='dark', rx=3)
    svg.mono(70, 190, "問題：LLM によるデータのコピーはエラーが起きやすい・多くのトークンを消費・高レイテンシ", size=12)

    # Separator
    svg.line(30, 265, w - 30, 265, color='dark', dash=True)

    # Bottom: Artifact mode (data bypasses LLM)
    svg.rect(20, 275, w - 40, 280, fill='white', stroke='border', dash=True)
    svg.text(60, 298, "Artifact モード：データが直接フロントエンドへ（効率的）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 110, 285, 80, 24, "✓ 効率的", fill='medium', font_size=12, bold=True)

    # LLM generates code, not data
    svg.rect(40, 315, 250, 120, fill='light')
    svg.text(165, 335, "LLM はコードのみを生成", size=FS_SMALL, bold=True)
    sql_code = [
        "build_artifact(",
        '  type="sql",',
        '  code="SELECT dept,',
        '    COUNT(*) as cnt',
        '    FROM employees',
        '    GROUP BY dept")',
    ]
    svg.rect(50, 345, 230, len(sql_code) * 14 + 8, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(sql_code):
        svg.mono(58, 358 + j * 14, line, size=10)

    svg.arrow(290, 380, 340, 380)

    # Frontend executes directly
    svg.rect(340, 315, 250, 120, fill='medium')
    svg.text(465, 335, "フロントエンドが直接実行", size=FS_SMALL, bold=True)
    svg.rect(350, 348, 230, 75, fill='code_bg', stroke='dark', rx=3)
    table = [
        "┌────────┬──────┐",
        "│ dept   │ cnt  │",
        "├────────┼──────┤",
        "│ R&D Dept │  42  │",
        "│ Marketing Dept │  28  │",
        "└────────┴──────┘",
    ]
    for j, line in enumerate(table):
        svg.mono(358, 360 + j * 12, line, size=9)

    svg.arrow(590, 380, 640, 380)

    # Visualization artifact
    svg.rect(640, 315, 210, 120, fill='light')
    svg.text(745, 335, "可視化 Artifact", size=FS_SMALL, bold=True)
    svg.text(745, 355, "2 つ目の Artifact:", size=FS_TINY, fill='text_light')
    svg.rect(650, 365, 190, 60, fill='code_bg', stroke='dark', rx=3)
    svg.mono(658, 380, "build_artifact(", size=10)
    svg.mono(658, 394, '  type="chart",', size=10)
    svg.mono(658, 408, '  code="bar(data)")', size=10)

    # Data flow annotation
    svg.rect(180, 450, 520, 45, fill='dark')
    svg.text(440, 465, "データフロー：DB → フロントエンド → 可視化（LLM を完全にバイパス）", size=FS_BODY, fill='white', bold=True)
    svg.text(440, 483, "LLM はコード生成のみを担当し、データ転送は担当しない", size=FS_TINY, fill='white')

    # Data flow arrow (bypass)
    svg.arrow_curved(465, 435, 745, 435, curve=25, dash=True, color='dark')

    svg.save(os.path.join(OUT, 'fig5-9.svg'))


# ──────────────────────── fig5-6 ────────────────────────

def fig5_7():
    """Experiment 5.10: Production log intelligent diagnosis pipeline"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 5.10：本番ログのインテリジェント診断", size=FS_TITLE, bold=True)

    # Pipeline: left to right, then down
    # Row 1: ingestion → analysis
    svg.rect(20, 60, 250, 160, fill='white', stroke='border', dash=True)
    svg.text(145, 82, "① ログ収集", size=FS_BODY, bold=True)
    log_lines = [
        "trajectory_001.json:",
        '  {"role":"user","content":',
        '   "注文 #12345 をキャンセル"}',
        '  {"role":"assistant",',
        '   "tool_call":"cancel_order"}',
        '  {"role":"tool","result":',
        '   "ERROR: no insurance"}',
        '  → Agent はユーザーに理由を伝えなかった',
    ]
    svg.rect(30, 98, 230, len(log_lines) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(log_lines):
        svg.mono(38, 112 + j * 14, line, size=9)

    svg.arrow(270, 140, 310, 140)

    svg.rect(310, 60, 260, 160, fill='white', stroke='border', dash=True)
    svg.text(440, 82, "② LLM 分析", size=FS_BODY, bold=True)
    analysis = [
        "入力：トレース + アーキテクチャドキュメント + PRD",
        "",
        "分析の観点:",
        "  - 実行フローが期待どおりか",
        "  - ツール呼び出しが正しいか",
        "  - エラー処理が適切か",
        "  - ユーザー体験が満足できるものか",
        "",
        "→ 逸脱したステップとモジュールを特定",
    ]
    for j, line in enumerate(analysis):
        svg.mono(320, 100 + j * 14, line, size=10)

    svg.arrow(570, 140, 610, 140)

    svg.rect(610, 60, 250, 160, fill='white', stroke='border', dash=True)
    svg.text(735, 82, "③ 構造化レポート", size=FS_BODY, bold=True)
    report = [
        "問題レポート:",
        "  優先度: P1（ユーザー離脱リスク）",
        "  モジュール: cancellation_handler",
        "  説明: キャンセル失敗後、理由と代替案が",
        "    ユーザーに提供されていない",
        "  提案: 失敗理由の説明と",
        "    保険購入の案内を追加",
    ]
    svg.rect(620, 98, 230, len(report) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(report):
        svg.mono(628, 112 + j * 14, line, size=9)

    # Row 2: test case generation → issue creation
    svg.arrow(w / 2, 220, w / 2, 260)

    svg.rect(60, 260, 370, 160, fill='white', stroke='border', dash=True)
    svg.text(245, 282, "④ 回帰テストケース生成", size=FS_BODY, bold=True)
    test_code = [
        "def test_cancel_no_insurance():",
        '  """軌跡 #001、ラウンド 3-5"""',
        "  # リプレイ: ユーザーがエコノミークラスのキャンセルを要求",
        "  resp = agent.run(",
        '    "注文 #12345 をキャンセル")',
        "  # 検証: 理由を説明すべき",
        '  assert "insurance" in resp.text',
        '  assert "alternative" in resp.text',
        "  # 検証: エラーを直接返すべきではない",
        '  assert "ERROR" not in resp.text',
    ]
    svg.rect(70, 298, 350, len(test_code) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(test_code):
        svg.mono(78, 312 + j * 14, line, size=10)

    svg.arrow(430, 340, 470, 340)

    svg.rect(470, 260, 380, 160, fill='white', stroke='border', dash=True)
    svg.text(660, 282, "⑤ GitHub Issue の自動作成", size=FS_BODY, bold=True)
    issue = [
        "gh issue create \\",
        '  --title "P1: キャンセル失敗時に',
        '    ユーザーガイダンスが不足" \\',
        '  --body "**問題**: Agent が cancel_order 失敗後に',
        '    エラーを直接返し、',
        '    理由を説明していない...',
        '    **軌跡**: #001 ラウンド 3-5',
        '    **テスト**: test_cancel_..." \\',
        '  --assignee @backend-team',
    ]
    svg.rect(480, 298, 360, len(issue) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(issue):
        svg.mono(488, 312 + j * 14, line, size=10)

    # Bottom: full pipeline summary
    svg.rect(100, 445, w - 200, 44, fill='dark')
    svg.text(w / 2, 460, "エンドツーエンドの自動化：ログ → 分析 → レポート → テスト → Issue", size=FS_BODY, fill='white', bold=True)
    svg.text(w / 2, 480, "MCP 経由で GitHub と統合・テストフレームワークが自動でリプレイ検証", size=FS_TINY, fill='white')

    svg.text(w / 2, 530, "手動診断のコストを数時間から数分に削減", size=FS_SMALL, fill='darker', bold=True)

    svg.save(os.path.join(OUT, 'fig5-7.svg'))


# ──────────────────────── fig5-9 ────────────────────────

def fig5_10():
    """Agent Bootstrap Loop (Self-replication and Evolution)"""
    w, h = 880, 555
    svg = SVG(w, h)
    svg.text(w / 2, 30, "Agent の自己ブートストラップ：コードから自己複製へ", size=FS_TITLE, bold=True)

    # Evolution timeline at top
    stages = [
        ("塵 → 星", "物理法則"),
        ("星 → 惑星", "重力による集積"),
        ("惑星 → 生命", "DNA の自己複製"),
        ("生命 → Agent", "コードによるブートストラップ"),
    ]
    sx = 60
    for i, (stage, mechanism) in enumerate(stages):
        fill = 'dark' if i == 3 else ('medium' if i == 2 else 'light')
        svg.rect(sx, 55, 180, 50, fill=fill)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(sx + 90, 72, stage, size=FS_SMALL, bold=True, fill=tc)
        svg.text(sx + 90, 92, mechanism, size=FS_TINY, fill='white' if fill == 'dark' else 'text_light')
        if i < len(stages) - 1:
            svg.arrow(sx + 180, 80, sx + 195, 80)
        sx += 200

    # Key distinction
    svg.line(30, 120, w - 30, 120, color='dark', dash=True)

    svg.rect(30, 135, 400, 70, fill='light')
    svg.text(230, 155, "DNA の自己複製：ランダムな突然変異 + 自然選択", size=FS_SMALL, bold=True)
    svg.text(230, 177, "自らを理解しない・方向性を持って改変できない・37 億年の盲目的な試行錯誤", size=FS_TINY, fill='text_light')

    svg.rect(450, 135, 400, 70, fill='dark')
    svg.text(650, 155, "Agent の自己ブートストラップ：コードを理解 + 方向性を持った設計", size=FS_SMALL, bold=True, fill='white')
    svg.text(650, 177, "自らの仕組みを理解・目的を持って創造・ベストプラクティスを継承", size=FS_TINY, fill='white')

    # Bootstrap cycle (main diagram)
    svg.rect(20, 225, 390, 295, fill='white', stroke='border', dash=True)
    svg.text(215, 248, "元の Agent（自身のコード）", size=FS_BODY, bold=True)

    svg.rect(30, 265, 175, 124, fill='light')
    svg.text(118, 285, "システムプロンプト", size=FS_SMALL, bold=True)
    svg.text(40, 308, "あなたは航空会社のカスタマーサービス Agent です", size=12, anchor='start')
    svg.text(40, 326, "キャンセル規則: ...", size=12, anchor='start')
    svg.text(40, 344, "振替規則: ...", size=12, anchor='start')
    svg.text(40, 362, "ツール: cancel_order", size=12, anchor='start')

    svg.rect(215, 265, 185, 124, fill='light')
    svg.text(308, 285, "Agent フレームワークのコード", size=FS_SMALL, bold=True)
    svg.mono(225, 308, "loop:", size=12)
    svg.mono(225, 326, "  msg = llm(ctx)", size=12)
    svg.mono(225, 344, "  if tool_call:", size=12)
    svg.mono(225, 362, "    exec(tool)", size=12)

    svg.rect(30, 400, 370, 54, fill='code_bg', stroke='dark', rx=4)
    svg.text(215, 419, "ツール定義 + MCP 統合 + メッセージ形式", size=FS_SMALL)
    svg.text(215, 438, "検証済みの高品質な実装", size=FS_TINY, fill='text_light')

    # Arrow: self-replication — label placed above dashed box headers
    svg.text(440, 215, "コピー + 改変", size=FS_TINY, fill='text_light', bold=True)
    svg.arrow(410, 375, 470, 375)

    # New Agent
    svg.rect(470, 225, 390, 295, fill='white', stroke='border', dash=True)
    svg.text(665, 248, "新しい Agent（方向性を持った改変後）", size=FS_BODY, bold=True)

    svg.rect(480, 265, 180, 124, fill='medium')
    svg.text(570, 285, "新しいシステムプロンプト", size=FS_SMALL, bold=True)
    svg.text(490, 308, "あなたは EC のカスタマーサービス Agent です", size=12, anchor='start')
    svg.text(490, 326, "返金規則: ...", size=12, anchor='start')
    svg.text(490, 344, "物流の問い合わせ: ...", size=12, anchor='start')
    svg.text(490, 362, "ツール: refund_order", size=12, anchor='start')

    svg.rect(670, 265, 180, 124, fill='light')
    svg.text(760, 285, "継承したフレームワークのコード", size=FS_SMALL, bold=True)
    svg.mono(680, 308, "loop:", size=12)
    svg.mono(680, 326, "  msg = llm(ctx)", size=12)
    svg.mono(680, 344, "  if tool_call:", size=12)
    svg.mono(680, 362, "    exec(tool)", size=12)

    svg.rect(480, 400, 370, 54, fill='code_bg', stroke='dark', rx=4)
    svg.text(665, 419, "新しいツール + 新しいビジネスロジック", size=FS_SMALL)
    svg.text(665, 438, "アーキテクチャフレームワークを完全に継承 → 品質を保証", size=FS_TINY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig5-10.svg'))


# ──────────────────────── fig5-10 ────────────────────────

def fig5_11():
    """Experiment 5.14: Meta-Agent pipeline for creating new Agents"""
    w, h = 880, 610
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 5.14：Agent を作れる Agent", size=FS_TITLE, bold=True)

    # Input: user request
    svg.rect(30, 60, 280, 55, fill='medium')
    svg.text(170, 80, "ユーザー要件", size=FS_SMALL, bold=True)
    svg.text(170, 98, "「EC の返金カスタマーサービス Agent を作成して」", size=FS_TINY, fill='text_light')

    svg.arrow(170, 115, 170, 145)

    # Meta-Agent: the creator
    svg.rect(20, 145, 840, 230, fill='white', stroke='border', dash=True)
    svg.text(440, 168, "メタ Agent（Coding Agent）", size=FS_BODY, bold=True)

    # Step 1: Read reference
    svg.rect(35, 185, 190, 170, fill='light')
    svg.text(130, 205, "① 参照コードを読む", size=FS_SMALL, bold=True)
    svg.mono(45, 228, "read_file:", size=12)
    svg.mono(45, 248, "  agent.py", size=12)
    svg.mono(45, 268, "  tools/*.py", size=12)
    svg.mono(45, 288, "  system_prompt.md", size=12)
    svg.mono(45, 308, "  config.yaml", size=12)
    svg.text(45, 332, "→ アーキテクチャパターンを理解", size=12, anchor='start', fill='text_light')

    svg.arrow(225, 270, 248, 270)

    # Step 2: Copy scaffold
    svg.rect(248, 185, 190, 170, fill='light')
    svg.text(343, 205, "② スキャフォールドをコピー", size=FS_SMALL, bold=True)
    svg.mono(258, 228, "cp -r reference/", size=12)
    svg.mono(258, 248, "  → new_agent/", size=12)
    svg.text(258, 278, "維持:", size=12, anchor='start', fill='text_light')
    svg.text(258, 298, "  Agent のループフレームワーク", size=12, anchor='start', fill='text_light')
    svg.text(258, 318, "  メッセージ形式／KV 最適化", size=12, anchor='start', fill='text_light')

    svg.arrow(438, 270, 461, 270)

    # Step 3: Targeted modification
    svg.rect(461, 185, 190, 170, fill='medium')
    svg.text(556, 205, "③ 対象を絞った修正", size=FS_SMALL, bold=True)
    svg.mono(471, 228, "edit_file:", size=12)
    svg.mono(471, 248, "  system_prompt.md", size=12)
    svg.text(471, 268, "  → EC の返金規則", size=12, anchor='start', fill='text_light')
    svg.mono(471, 290, "  tools/refund.py", size=12)
    svg.text(471, 310, "  → 返金ツールを追加", size=12, anchor='start', fill='text_light')
    svg.mono(471, 332, "  config.yaml", size=12)

    svg.arrow(651, 270, 674, 270)

    # Step 4: Validate
    svg.rect(674, 185, 175, 170, fill='light')
    svg.text(761, 205, "④ 検証テスト", size=FS_SMALL, bold=True)
    svg.mono(684, 228, "bash:", size=12)
    svg.mono(684, 248, "  python agent.py", size=12)
    svg.text(684, 270, "  → 新しい Agent を起動", size=12, anchor='start', fill='text_light')
    svg.text(684, 290, "  → テストメッセージを送信", size=12, anchor='start', fill='text_light')
    svg.text(684, 310, "  → ツール呼び出しを確認", size=12, anchor='start', fill='text_light')
    svg.text(684, 330, "  → 会話フローを検証", size=12, anchor='start', fill='text_light')

    # Output: new agent
    svg.arrow(w / 2, 375, w / 2, 410)

    svg.rect(115, 410, 700, 90, fill='white', stroke='border', dash=True)
    svg.text(465, 432, "生成された新しい Agent", size=FS_BODY, bold=True)

    outputs = [
        ("system_prompt.md", "EC の返金規則"),
        ("tools/refund.py", "返金／照会ツール"),
        ("agent.py", "継承したフレームワークのコード"),
        ("config.yaml", "モデル／パラメータ設定"),
    ]
    ox = 135
    for fname, desc in outputs:
        svg.rect(ox, 448, 170, 42, fill='light')
        svg.mono(ox + 85, 462, fname, size=10, anchor='middle')
        svg.text(ox + 85, 480, desc, size=FS_TINY, fill='text_light')
        ox += 178

    # Bottom: comparison
    svg.line(30, 515, w - 30, 515, color='dark', dash=True)
    svg.rect(60, 530, 350, 54, fill='light')
    svg.text(235, 549, "ゼロから生成：ベストプラクティスが欠如", size=FS_SMALL, bold=True)
    svg.text(235, 571, "場当たり的なコンテキスト管理・非標準的なツール設計・古い API", size=FS_TINY, fill='text_light')

    svg.rect(470, 530, 350, 54, fill='dark')
    svg.text(645, 549, "サンプルから改変：ベストプラクティスを継承", size=FS_SMALL, bold=True, fill='white')
    svg.text(645, 571, "標準的なメッセージ形式・標準的なツール設計・モダンな API", size=FS_TINY, fill='white')

    svg.save(os.path.join(OUT, 'fig5-11.svg'))


# ──────────────────────── main ────────────────────────

def main():
    os.makedirs(OUT, exist_ok=True)
    figs = [
        fig5_1, fig5_2, fig5_3, fig5_4, fig5_5, fig5_6,
        fig5_7, fig5_8, fig5_9, fig5_10, fig5_11,
    ]
    for fn in figs:
        fn()
        print(f"  ✓ {fn.__name__}: {fn.__doc__}")
    print(f"\nGenerated {len(figs)} figures in {OUT}/")


if __name__ == '__main__':
    main()
