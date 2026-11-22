# 第 5 章 · Coding Agent 与代码生成

用户要把法兰盘的安装孔从 M5 改为 M6。程序跑通了，屏幕上的零件看起来也对，怎样知道这次改动合格？沿孔的中截面量一次直径，得到的答案比看一张效果图更直接。代码能创造新工具，也让我们有机会把需求写成可以反复执行的检查。这条思路贯穿本章的求解器、编码助理和内容制作实验。

[返回主目录](../README.md) · [读第五章正文](../book/chapter5.md)

## 第一次做实验

1. **先检查条件有没有写对。** 在[逻辑求解实验](code-for-logic/README.md)里，把自然语言线索写成约束，再检查求解器返回的赋值。若出现多个解，回到原题查有没有遗漏线索；若找不到解，也要逐条核对是否把条件写反。读[编码助理的主循环](coding-agent/agent.py)时可以用同样的办法，先跟踪一次只读任务，再看修改文件后程序怎样运行检查、把失败信息交回模型。
2. **再选一个自己能验收的成品。** 用户要移动界面按钮，就在[对话式界面实验](conversational-ui/README.md)里对照修改后的页面；用户要改安装孔，就在[法兰盘实验](cad-vs-diffusion/README.md)里检查截面。CadQuery 样件的实测孔径从 5.499 毫米增至 6.499 毫米。另一种方法生成的网格在所测截面上没有可测的内环，单凭外观给不出同样的尺寸结论。若规则由服务端执行，可接着读[小模型与代码化规则](small-model-codified-rules/README.md)，核对模型答复和实际业务状态。
3. **最后看成品如何交给下一道工序。** [论文转幻灯片](paper-to-ppt/README.md)用同一篇论文比较自审和独立审核，两份 20 页成稿都得了 95 分。接下来的[讲解视频实验](paper-to-video/README.md)取材于更早的 22 页稿：视频的第 12 段用的是源稿第 21 页。读者可以先按选页表找到原图，再听这一段讲解是否说对了图中的内容。逐页时长记录能帮助定位音画交界，讲解说得对不对还要对照原页。

## 配套项目

| 编号 | 项目 | 类型 | 一句话说明 |
| :--: | --- | :--: | --- |
| 5-1 | [provider-failover](provider-failover/) | ✅ | 六种厂商组合 × 三种做法的真实接管：中立格式 6/6 切换成功并算对总额，原样直传 3/6、剥离思考 4/6，其余五次首个请求均返回 HTTP 400。对照 Anthropic → Gemini 的两次请求，观察删除凭证后发生了什么 |
| 5-2 | [provider-failover](provider-failover/) | ✅ | 流式输出在思考／正文／参数三处被切断后的恢复对照：正文断点上续写省 15%~66% 输出 token，参数断点上却会拼出「合法但写错」的参数，元指令在每个单元上都比整轮重发更贵 |
| 5-3 | [code-for-math](code-for-math/) | ✅ | 30 道 AIME 2024 同模型真实对照：代码臂全部调用沙箱（含 sympy/numpy/scipy），53.3% vs 纯 CoT 36.7%，但差异未达显著（p=0.125）；正式负结论与原始收据均保留 |
| 5-4 | [code-for-logic](code-for-logic/) | ✅ | 固定版本 K&K 数据集 84 题真实对照：代码臂 100% 调用 `python-constraint`，实测 39.3% vs 纯思考 75.0%，未达到正文预期的 90%；完整负结论如实保留 |
| 5-5 | [small-model-codified-rules](small-model-codified-rules/) | ✅ | 本地 Qwen3-4B 的 60×2 配对 τ-bench 风格活动：代码化规则臂 91.7% vs 控制组 95.0%（p=0.6875），未显著提升；服务端真值、checklist 和完整 120 条轨迹均已验证 |
| 5-6 | [paper-to-ppt](paper-to-ppt/) | ✅ | 固定真实论文 PDF 的 20 页双臂正式对照：三张原图均带页码/裁剪/变换/哈希来源；两组独立 Vision 均以 95 分通过，质量持平，但双 Agent 峰值上下文 24,186 vs 单 Agent 92,601（低 3.83×） |
| 5-7 | [paper-to-video](paper-to-video/) | ✅ | 从实验 5-6 的 22 页旧稿选取 12 页，用 Kimi K3 写讲稿、Qwen-VL-Max 对照页面审核、Fish Audio S1 合成旁白。用 ffprobe 检查 513.010 秒的成片，再逐页比较原音频和视频片段时长，最大差值为 0.024 秒 |
| 5-8 | [video-edit](video-edit/) | ✅ | 一段多场景视频 + 一句自然语言需求，两步 Vision 定位剪出片段，Reviewer 抽帧核对不合格则迭代 |
| 5-9 | [cad-vs-diffusion](cad-vs-diffusion/) | ✅ | 按同一规格生成法兰盘，再把安装孔从 M5 改为 M6。CadQuery 改一个参数后，实测孔径从 5.499 mm 增至 6.499 mm；混元 3D 重新生成网格后，需要先对齐尺度和朝向才能比较尺寸。最后用两张盆栽图比较外观自然度 |
| 5-10 | [adaptive-log-parser](adaptive-log-parser/) | ✅ | 遇到无法解析的新格式时不报错，交给代码 Agent 生成 `parse` 函数，测试通过后热更新进引擎，全程无人介入 |
| 5-11 | [log-diagnosis](log-diagnosis/) | ✅ | 诊断 Agent 读真实 HTTP 轨迹/架构文档/PRD，定位根因、生成回归测试并在修复前后重放；正式活动通过官方 GitHub MCP 创建了真实 Issue（保留脱敏收据） |
| 5-12 | [dynamic-form](dynamic-form/) | ✅ | 信息不全时动态生成含级联逻辑的 HTML 表单让用户一次性补全，汇总 JSON 交回 Agent |
| 5-13 | [erp-agent](erp-agent/) | ✅ | 中文自然语言转 SQL 由 DB 执行，artifact 模式让 LLM 只生成 SQL 制品不搬运数据，省 token 又防错 |
| 5-14 | [conversational-ui](conversational-ui/) | ✅ | 自然语言提 UI 定制需求（颜色/字体/文案/布局），Agent 改 React 源码借 Vite HMR 即时生效 |
| 5-15 | [permission-embedded-data-objects](permission-embedded-data-objects/) | ✅ | 在 PostgreSQL 之上的权限内嵌对象存储：应用层代码可以动态生成，但每次读写仍由数据层强制执行权限、校验、引用完整性和受控后果反应 |
| 5-16 | [agent-creator](agent-creator/) | ✅ | 用模板生成和从零生成的两个 Agent 在同一套质量检查中都得了 39/39 分。模板路线创建时用了 1,181 个 token，从零路线用了 381,814 个；生成后的任务运行开销另计。[查看检查步骤和两组结果](agent-creator/README.md#learning-3) |

## 正式实验验收

逐项正文契约、正式运行状态、负结果与证据哈希统一记录在
[EXPERIMENT_LEDGER.md](EXPERIMENT_LEDGER.md)。机制演示、离线占位音频和 mock 外部写入
均不能替代正式证据。

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **进行中** | 已有实现，但实验范围或验收证据尚未满足正文全部要求 |
