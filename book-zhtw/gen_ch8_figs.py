#!/usr/bin/env python3
"""Chapter 8 figures — Agent 的自我進化.

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


def fig8_1():  # 外部化學習迴圈
    _pipeline([("完成任務", "產生原始經驗"), ("提煉經驗", "總結·壓縮·結構化"),
               ("存入外部系統", "知識庫/工具，可檢索"), ("檢索複用", "下次任務呼叫")],
              'fig8-1', feedback="經驗持續沉澱，跨會話複用")


def fig8_2():  # GAIA 經驗學習系統
    _pipeline([("成功軌跡", "完成任務的過程"), ("策略總結", "提煉為知識摘要"),
               ("知識摘要庫", "建立語義索引"), ("檢索注入", "Agent 決策時取用")],
              'fig8-2', feedback="相似任務複用歷史經驗")


def fig8_3():  # 層次化工具匹配（伺服器級→工具級）
    W, H = 620, 354
    s = SVG(W, H)
    cx = W / 2
    s.box(cx - 150, 46, 300, 52, "使用者查詢", sublabel="“Debug 這個檔案”", bold=True, fill='light')
    s.arrow(cx, 100, cx, 120)
    s.box(cx - 220, 122, 440, 62, "第一層：伺服器級語義搜尋",
          sublabel="數百個 MCP 伺服器 → 召回 Top-K 相關伺服器", bold=True, fill='light')
    s.arrow(cx, 186, cx, 208)
    s.box(cx - 220, 210, 440, 62, "第二層：工具級語義搜尋",
          sublabel="僅在 Top-K 伺服器的工具內匹配 → Top-N 工具", bold=True, fill='light')
    s.arrow(cx, 274, cx, 296)
    s.box(cx - 150, 298, 300, 46, "選定工具",
          sublabel="大幅縮小候選範圍，降低選擇成本", bold=True, fill='light')
    s.save(os.path.join(OUT, 'fig8-3.svg'))


def fig8_4():  # 工具動態載入的 KV Cache 最佳化（樸素 vs 最佳化）
    W, H = 860, 244
    s = SVG(W, H)
    s.text(220, 46, "樸素做法：工具定義混入系統提示", size=FS_SMALL, bold=True, fill='darker')
    s.rect(30, 62, 380, 70, fill='#f0d8d8')
    s.text(220, 84, "系統提示 + 全部工具定義", size=FS_SMALL, bold=True)
    s.text(220, 108, "工具增刪 → 字首改變 → KV Cache 全部失效", size=FS_TINY, fill='text_light')
    s.rect(30, 140, 380, 46, fill='light')
    s.text(220, 163, "每輪重算，成本高", size=FS_SMALL)

    s.text(640, 46, "最佳化做法：工具定義動態載入", size=FS_SMALL, bold=True, fill='darker')
    s.rect(450, 62, 380, 40, fill='#d8e8d8')
    s.text(640, 82, "穩定系統提示（快取命中字首）", size=FS_SMALL, bold=True)
    s.rect(450, 106, 380, 40, fill='light')
    s.text(640, 126, "按需追加的工具定義（變化部分）", size=FS_SMALL)
    s.rect(450, 150, 380, 40, fill='light')
    s.text(640, 170, "對話軌跡", size=FS_SMALL)
    s.text(640, 206, "穩定字首不變 → KV Cache 持續複用", size=FS_TINY, fill='text_light')
    s.line(430, 54, 430, 220, dash=True)
    s.save(os.path.join(OUT, 'fig8-4.svg'))


def fig8_5():  # Agent 自我進化流水線（需求識別→工具搜尋→程式碼封裝→工具註冊）
    _pipeline([("① 需求識別", "現有工具不足"), ("② 工具搜尋", "開放世界查詢"),
               ("③ 程式碼封裝", "生成並封裝"), ("④ 工具註冊", "納入庫可複用")],
              'fig8-5', feedback="新工具註冊後可被後續任務複用，持續擴充套件能力邊界")


def fig8_6():  # Voyager 持續學習架構（課程生成器 + 技能庫 + 迭代提示）
    _pipeline([("課程生成器", "提出漸進式新任務"), ("迭代提示機制", "生成並除錯技能程式碼"),
               ("技能庫", "儲存可複用技能")],
              'fig8-6', W=760, feedback="技能積累後解鎖更難的任務（開放世界探索）")


def fig8_7():  # 實驗 8-5 自我進化流水線（搜尋→評估→測試→封裝→複用）
    _pipeline([("① 搜尋", "開放網路找工具"), ("② 評估", "判斷是否合適"), ("③ 測試", "驗證可用性"),
               ("④ 封裝", "包成標準工具"), ("⑤ 複用", "納入工具庫")],
              'fig8-7', W=940, feedback="新工具沉澱後供後續任務複用")


if __name__ == '__main__':
    for fn in (fig8_1, fig8_2, fig8_3, fig8_4, fig8_5, fig8_6, fig8_7):
        fn()
        print('saved', fn.__name__)
