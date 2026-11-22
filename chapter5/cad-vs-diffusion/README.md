# 实验 5-9：同一个零件的两种生成路线——代码与生成模型

工厂要把法兰盘上的四个 M5 安装孔改成 M6。孔要扩大，外径、盘厚和孔的位置都得保留。假如手上只有一张看起来正确的效果图，你能判断新零件装不装得上吗？

<a id="learning-0"></a>

## 理解问题与方法

先用两种方法制作同一只法兰盘。一种让 Agent 写出构造零件的程序，另一种先画产品图，再从图重建三维网格。第一次交付要按图纸逐项量尺寸。第二次只改孔径，再量一遍，看看谁能把其他尺寸原样保留下来。最后把任务换成画一盆绿植，看看换了验收要求以后，你还会不会选同一种方法。

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

仓库附有一个 M5 法兰盘的 STL 样件。第一次做实验，可以先用它练习测量，再用已有运行记录比较两条路线。希望从头生成零件和图片时，再配置下列服务。

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

在实验目录中打开 [规格文件](flange_spec.py)，把 M5 和 M6 两次交付各自应有的孔数、孔径和孔位圆直径写下来。装好依赖后，用下面的命令量一量[随仓库提供的 M5 样件](tests/fixtures/flange_m5.stl)。这一步在本地完成。

```bash
python - <<'PYTHON'
from flange_spec import SPEC_M5
from measure import load_mesh, measure_flange

mesh = load_mesh("tests/fixtures/flange_m5.stl")
result = measure_flange(mesh, SPEC_M5)
print("中截面的孔数", result["hole_count_detected"])
print("平均孔径（mm）", round(result["hole_diameter_mm"], 3))
PYTHON
```

接着打开[两条路线的运行清单](validation/runs/exp5-7-cad-vs-diffusion-20260821-015734-v1/manifest.json)。书中编号是 5-9，归档时用的是旧编号 5-7，清单里的 `experiment` 字段和目录名都沿用旧编号。先在 `route_a` 下对照 `initial.measurement` 和 `after_change.measurement`，找出改动的尺寸，再用同样的方法读 `route_b`。如果某个孔径读数为空，先查截面上找到了几个孔，再决定能从这个读数推出什么。

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

法兰盘要和别的零件装配。把孔径单列为参数，这次变更就能复用原来的外圆、厚度和孔位。绿植要让人觉得枝叶自然，这次评审更喜欢生成图里的叶片细节和光影。3 分和 8 分来自一个模型对两张图的评判；换一种植物或绘图方法，还可以沿用这个比较办法，再看结果。

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
