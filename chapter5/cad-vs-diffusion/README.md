# 实验 5-9：同一个零件的两种生成路线——代码与生成模型

一个有精确孔径的法兰盘，与一盆形态自然的绿植，对三维生成提出了不同要求。本实验比较参数化 CAD 代码与直接生成形状的路线，学习任务约束怎样影响技术选择。

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

CAD 用尺寸和几何关系表达结构，适合可测量的约束与局部修改。生成模型更便于产生外观形态，但未必准确满足每个机械尺寸。比较时需要把几何合规与视觉自然程度分开。

> 《AI Agent 深入》第 5 章配套实验。同一份自然语言规格，分别走「Agent 写 CAD 代码」与「3D 生成模型」两条路线，程序化测量产物尺寸，再用一次变更请求比较两条路线的修改成本；对照组「生成一盆绿植」展示两条路线适用边界的反转。

← [返回第 5 章目录](../README.md)

### 实验目标

主线任务规格：**法兰盘，外径 80mm，厚度 10mm，4 个均布 M5 安装孔（孔径 5.5mm），孔位圆直径 60mm**。

- **路线 A（代码生成）**：Agent（Kimi `kimi-k2.5`）编写 CadQuery 代码构造零件，本地真实执行，导出 STEP 与 STL。
- **路线 B（生成模型）**：同一规格走 text-to-3D。混元 Hunyuan3D-2.1 官方 Hugging Face Space 只暴露 image-to-3D 端点，故按业界标准两段式：Gemini（`gemini-2.5-flash-image`）由规格文本生成零件产品图 → Hunyuan3D-2.1 公共 Space（`gradio_client` 调 `/shape_generation`，无需密钥）图生 3D，得到 GLB 三角网格。
- **程序化验证**：trimesh 测量两条路线产物的外径、厚度、孔数、孔径、孔位圆直径与安装面平整度，与规格逐项比对。
- **变更请求**：「安装孔从 M5 改为 M6（孔径 6.5mm）」。路线 A 程序化修补 `PARAMS.hole_diameter` 一个参数（0 次 LLM 调用）重新执行；路线 B 只能改提示词整体重新生成，复测其余尺寸是否漂移。
- **对照组**：「一盆绿植」——matplotlib 程序化渲染 vs Gemini 文生图，Kimi 视觉模型（`moonshot-v1-8k-vision-preview`）评审自然度，展示适用边界反转。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

### 配置与运行

```bash
cd chapter5/cad-vs-diffusion
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env   # 填入密钥（见下），并 export 到环境变量
python run_experiment.py
```

环境变量（只从环境读取，代码与 manifest 均不落密钥）：

- `KIMI_API_KEY`（必填）：路线 A 代码生成 + 对照组视觉评审。
- `GEMINI_API_KEY`（必填）：路线 B 的规格→零件图、对照组文生图。
- `DASHSCOPE_API_KEY` / `SILICONFLOW_API_KEY`（可选备选）：本次正式运行中前者返回 401（key 无效）、后者返回 402（余额不足），均未使用，留证见下文。

离线测试（不打外部 API）：

```bash
python -m pytest test_offline.py -q
```

<a id="learning-2"></a>

## 按照步骤完成实验

先读法兰盘规格，列出外径、厚度、孔径和孔位等检查项。按下文准备两条路线后生成同一对象，用测量程序检查结果。再提出一次单独的尺寸修改，观察两条路线如何保留其他约束。

<a id="learning-3"></a>

## 分析结果与形成判断

渲染图看起来相似，不等于模型尺寸相同；测量前应核对单位。反过来，几何尺寸准确也不足以说明自然物体外观好。结论应与具体任务类型绑定。

### 已有运行结果与对照分析

> 正式 run：`exp5-7-cad-vs-diffusion-20260821-015734-v1`，完整数据见
> `validation/runs/exp5-7-cad-vs-diffusion-20260821-015734-v1/manifest.json`
> （SHA-256 前 16 位 `ae7c5fdf685562e5`，全文哈希见 `validation/latest.json`）。
> 10/10 门禁全部通过，9 次外部调用全部留证成功。

清单的 `artifacts` 列出了本次运行的 13 个文件及其 SHA-256。可以在作者工作区的 `output/` 找到对应原件，逐项计算的哈希均与清单一致。普通 Git 检出只包含清单和测量记录。自行重跑时，先核对本次生成了哪些文件，再比较测量结果。外部模型重新生成的网格可能有变化。

#### 主线任务：怎样检查法兰盘的尺寸和安装孔？

先确认模型怎么摆放。`measure.py` 假定法兰平放在 XY 平面，用 X、Y 两个方向跨度的较大值估算外径，用 Z 方向的跨度估算厚度。路线 A 按这个约定建模，长度单位为毫米。路线 B 输出的网格还没有按零件规格校准尺度和朝向，读数用原始网格单位表示。

| 检查项（规格） | 路线 A：CadQuery 代码 | 路线 B：Hunyuan3D-2.1 网格 |
|---|---|---|
| 外径（80 mm） | 80.0 mm | XY 最大跨度 0.519 |
| 厚度（10 mm） | 10.0 mm | Z 跨度 1.989 |
| 孔数（4） | 中截面检出 4 个孔 | 中截面检出 0 个孔 |
| 孔径（5.5 mm） | 5.499 mm（偏差 −0.001 mm） | 无可测内环 |
| 孔位圆直径（60 mm） | 60.0 mm | 无可测内环 |
| 安装面平整度 RMS | 0.0 mm（理想平面） | 0.030（网格单位） |
| 网格 | 水密，2532 面 | 水密，144580 面 |

路线 B 的 M5 网格在 X、Y、Z 三轴的跨度依次为 0.496、0.519、1.989。沿 Z 看，它的高度约为横向跨度的四倍。对照规格，直径 80 mm、厚度 10 mm 的圆盘应当有两个长轴和一个短轴。这说明，即使先放下单位问题，重建的外形也值得检查。清单把原始读数直接与 80 和 10 相减，给出 −99.4% 和 −80.1%。只有先建立网格单位与毫米的对应关系，这种百分比才有尺寸误差的含义。

再检查孔。输入产品图 `output/route_b/flange_m5_input.png` 上能看到四个安装孔。测量程序沿 Z 轴在网格中部切一刀，在截面轮廓里寻找内环。路线 A 找到四个，路线 B 一个也没找到。要判断孔是否真正贯穿，还应沿实际安装面的法向检查多个深度的截面。可以对照两张点云渲染 `output/render_route_a_m5.png` 和 `output/render_route_b_m5.png`，再决定怎样放置切面。

路线 A 一次成功：Kimi 生成的 17 行 CadQuery 代码（`output/route_a/flange_m5.py`）全部尺寸在 0.05mm 公差内，唯一的 −0.001mm 孔径偏差来自 STL 三角离散的弦差，STEP 文件则是精确 B-rep。

#### 变更请求：M5 → M6（孔径 5.5 → 6.5）

| | 路线 A | 路线 B |
|---|---|---|
| 修改方式 | 程序化修补 `PARAMS.hole_diameter` 一行 | 改提示词，文生图 + 图生 3D 整体重跑 |
| LLM/模型调用 | **0 次**（本地执行 2.1s） | **2 次外部生成**（6.9s + 24.6s） |
| 变更后孔径 | 6.499（偏差 −0.001mm） | Z 向中截面仍无可测内环 |
| 其余尺寸漂移 | 外径 0.0、厚度 0.0、孔位 0.0、孔数不变 | XY 最大跨度 0.519→1.988（+283%），Z 跨度变化 −0.0015（网格单位） |

为什么 XY 读数涨了 283%，却不能据此断定零件外径也涨了 283%？打开路线 B 的 M6 网格，三轴跨度变成了 1.988、0.248、1.988，最短的方向是 Y。看渲染图 `output/render_route_b_m6.png` 时，可以试着让薄面朝上，再重新测量。两次生成的外形和摆放都发生了变化，要判断外径是否保持，先得认出两件零件上相对应的面，并取得可比的尺度。

#### 对照组：一盆绿植（适用边界反转）

任务：`一盆绿植（带花盆的室内观叶植物），写实风格`。

| | 程序化渲染（matplotlib） | 文生图（Gemini） |
|---|---|---|
| 产物 | `output/control/plant_procedural.png` | `output/control/plant_generative.png` |
| 视觉评审自然度（1-10） | **3**（过于简化，缺乏细节和真实感） | **8**（细节丰富，光影效果逼真） |

评审模型（Kimi `moonshot-v1-8k-vision-preview`）结论：文生图「更接近真实世界的一盆绿植」。原文见 manifest `control_group.vision_review`。

**结论**：精确工程对象（法兰盘）——代码生成碾压生成模型（尺寸精确、可参数化修改）；开放性自然内容（绿植）——生成模型碾压代码渲染。两条路线的适用边界正好反转。

### 检查自己的解释

用户同时要求自然外观和可制造接口时，能否把两条路线组合起来？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 目录结构

```
cad-vs-diffusion/
├── flange_spec.py        # 规格与变更请求的唯一事实来源
├── measure.py            # trimesh 网格测量（外径/厚度/孔/平整度）
├── llm.py                # Kimi 聊天/视觉调用（带留证）
├── gemini_image.py       # Gemini 原生文生图（带留证）
├── route_a_codegen.py    # 路线 A：LLM 写 CadQuery → 子进程真实执行 → STEP/STL
├── route_b_gen3d.py      # 路线 B：HF 公共 Space Hunyuan3D-2.1 图生 3D
├── control_plant.py      # 对照组：程序化绿植 + Vision 评审
├── receipts.py           # 外部调用留证（参数/响应/时间戳/耗时，绝不含密钥）
├── validate_manifest.py  # manifest 模式校验
├── run_experiment.py     # 主流程
├── test_offline.py       # pytest 离线测试（不打外部 API）
├── tests/fixtures/       # CadQuery 本地生成的法兰 fixture 网格
├── output/               # 产物：源码、STEP/STL/GLB、图片
└── validation/runs/<run_id>/
    ├── manifest.json     # 正式运行清单（哈希、测量、门禁）
    └── receipts/         # 每次外部调用的留证 JSON
```

<a id="learning-5"></a>

## 排查问题与查阅资料

### 结果的适用范围

- 路线 B 的网格由真实外部服务（Hugging Face 公共 Space）生成，原始 GLB 原样保存、原样测量；表中的跨度和截面检孔结果均取自生成时的坐标系。
- 若公共 Space 排队/限流导致路线 B 失败，manifest 中会标 `status: incomplete` 并附原因，不会用 mock 网格冒充。
- `DASHSCOPE_API_KEY`（401 invalid_api_key）与 `SILICONFLOW_API_KEY`（402 余额不足）在本次运行中不可用，相关探测记录如实保留；视觉评审与文生图改走 Kimi / Gemini。
