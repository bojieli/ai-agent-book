# 实验 5-4：基于论文的 PPT 自动生成（提议者-审核者机制）

配套《深入理解 AI Agent》第 5 章。把"做 PPT"重构为**代码生成**问题：用
[Slidev](https://sli.dev)（Markdown + HTML 定义幻灯片）框架，让 Agent 从一篇论文
自动生成演示文稿，并用**提议者-审核者（Proposer-Reviewer）**机制做视觉质量控制。

## 一句话结论

Proposer 只写 Slidev 代码、Reviewer 真正把每页**渲染成 PNG** 再用 **Vision LLM 看图**
挑毛病（文字溢出 / 内容拥挤 / 图片尺寸），Proposer 据结构化反馈迭代修订。相比"单 Agent
自审"（把历次渲染图片都堆在同一上下文里），双 Agent 分工的**上下文峰值显著更小**——
因为 Proposer 全程不看图片、Reviewer 每轮只看最新一版截图。

## 为什么需要"渲染出来再看"

Agent 写完 Slidev 代码时**并不知道实际渲染效果**：内容会不会太挤、文字会不会溢出、
图片尺寸是否合适——这些只有真正渲染成像素才看得出来。所以 Reviewer 接触到的是
Proposer 看不到的**新信息**（渲染结果），这正是本机制的价值所在。

## 提议者-审核者分工

| 角色 | 职责 | 上下文里有什么 |
|---|---|---|
| **Proposer**（`gpt-4o`，纯文本） | 读论文 → 规划页面 → 生成/修订 `slides.md` | 论文正文 + **累积的结构化文字反馈**（永不含图片） |
| **Reviewer**（`gpt-4o`，Vision） | 看最新一版每页 PNG，输出结构化建议 JSON | **每轮全新调用**，只含最新一版截图 |

Reviewer 的建议是结构化、可执行的，而非模糊的"不好看"，包含字段：
`page`（页码）、`issue_type`（`text_overflow`/`overcrowded`/`image_size`/`readability`/`layout`）、
`severity`（high/medium/low）、`suggestion`（具体修改建议）、以及整份的 `overall_score` 与 `pass`。

Proposer 收到反馈 → 理解意图 → 修订代码 → 再次提交 Reviewer，循环直到 `pass` 或达最大轮数。

## 对照实验：单 Agent 自审 vs 双 Agent 分工

`demo.py` 同时跑两种方案，并用**同一位独立 Vision 评委**给两者的最终 PPT 打分（保证质量可比）：

- **方案 A 双 Agent**：如上。Proposer 上下文只增文本；Reviewer 每轮重置、只看最新截图。
- **方案 B 单 Agent 自审**：一个 Agent 在**同一段对话**里生成 → 看自己的渲染截图自审 → 修订。
  历次渲染的图片会**一直留在上下文里**，随迭代快速膨胀（书中所述"上下文迅速超限"）。

脚本打印每次调用的 prompt token 序列、总量、以及**上下文峰值**（单次 prompt token，
决定是否撑爆上下文窗口）。页数越多、迭代越多，方案 B 的峰值相对方案 A 越夸张。

## 运行

```bash
# 1) Python 依赖
pip install -r requirements.txt

# 2) Slidev + 渲染依赖（Node）。首次约 1-2 分钟：
npm install
#   - @slidev/cli：Slidev 命令行
#   - playwright-chromium：slidev export --format png 的底层浏览器
#   - typescript：Slidev 的 twoslash 代码高亮所需（否则 export 会 ERR_MODULE_NOT_FOUND）
#   若 npm install 没有自动装好 chromium 浏览器二进制，运行：
#     npx playwright install chromium

# 3) 配置 Key
cp env.example .env    # 填入 OPENAI_API_KEY

# 4) 跑完整流程（生成 → 渲染 → Vision 审查 → 迭代 → 对比）
python demo.py
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `demo.py` | 主流程：跑两种方案、独立评委打分、打印 token 对比 |
| `agents.py` | `Proposer` / `Reviewer` / `SelfReviewAgent` 三个 Agent + `TokenMeter` 计量 |
| `renderer.py` | 调 `slidev export --format png` 把 `slides.md` 渲染成逐页 PNG |
| `make_figures.py` | 用 matplotlib 从论文数字复现 2 张图表，放进 Slidev `public/` |
| `paper/sample_paper.md` | 精简论文（FlashAttention，含标题/章节/表格/结果） |
| `package.json` | Slidev 与渲染依赖 |
| `output/` | 运行产物：各轮 `slides.md`、`review.json`、`comparison_summary.json` |
| `slidev_workspace/exports/` | 各轮渲染出的 PNG（`dual_round1/`、`single_round1/` …） |

## 关于"第一版故意写得很挤"

为了**稳定复现**"渲染 → 发现问题 → 修订"的闭环，`agents.py` 里让 Proposer/单 Agent 的
**首版**先把整篇论文塞进约 4 页、成段贴原文（一种常见的"先把内容倒进去"的初稿写法）。
这会产生**真实的**文字溢出与图表被裁切（见 `slidev_workspace/exports/dual_round1/2.png`：
段落太长、图表底部超出页面）。Reviewer 的问题都是 gpt-4o **看真实像素**得出的，修订也是
真实的——不是预设脚本。若把首版指令改成"直接生成 8-12 页精简版"，gpt-4o 往往一版就过关，
反而看不到迭代过程。一次真实运行的结果（会有随机波动）：

```
双 Agent：round1 score=85 pass=False（4 个 medium：p2/p3/p4 overcrowded、p2 image_size）
          → Proposer 拆页精简 → round2 score=95 pass=True（+10 改善）
上下文峰值：双 Agent = 9308 tok，单 Agent 自审 = 14179 tok（单 Agent 图片累积：1640→8069→14179）
```

## 局限

- **审美主观**：Reviewer 的偏好未必等于目标用户的偏好，反馈循环可能收敛到 Reviewer
  认可但用户嫌挤的局部最优（见书末思考题：如何让用户偏好也进入循环）。
- **图表来源**：本实验不解析真实 PDF，图表由 `make_figures.py` 从论文数字程序化复现，
  作为"论文原始图表"的替身；接入真实 PDF 需另加图片抽取。
- **成本/时长**：每轮 Reviewer 要把约 10 张截图发给 gpt-4o Vision，单次运行需数十次
  API 调用；已把截图统一缩放到 1280px 宽以控制 token。
- **确定性**：LLM 与 Vision 判定有随机性，具体分数/建议每次略有不同；`temperature`
  已调低，但迭代是否恰好"1 轮达标"取决于首版质量。
- **渲染依赖**：`slidev export` 依赖 playwright-chromium；无网络/无法装 chromium 的
  环境需先解决浏览器二进制问题（见"运行"第 2 步）。
