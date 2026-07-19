# 实验代码缺口 · 处置计划（SHIP 优先）

原则（据作者指示）：**默认 SHIP** —— 每个书中实验都应在仓库内提供可参考的实现与架构，方便读者对照。只有存在**具体理由**时才不新写代码：

- **ALREADY** —— 代码其实已存在于仓库某处，只需修正书中/README 的指向。
- **KEEP-EXT** —— 训练类实验，核心代码在外部 fork；仓库内补"薄壳"（钉住上游 commit + `run.sh`/config + 结果表），不重写。
- **SHIP** —— 需要在仓库内新建可运行的参考实现（默认）。

工作量：S（1–2 天）/ M（3–5 天）/ L（1–2 周，通常含 GPU 训练）。

---

## 处置总表

| 实验 | 名称 | 现状 | 处置 | 工作量 | 说明 |
|---|---|---|---|---|---|
| 2-5 | 提示注入攻防 | 无目录 | **SHIP** | S | 最小攻防 demo：3 攻击场景 × 4 防御配置 + 成功率统计 |
| 2-6 | Agent Skills 生成 PPT | 无目录 | **SHIP** | S | 可运行脚本：Claude Code + PPTX Skill 封装 + 示例输入 |
| 3-13 | 结构化知识提取（司法） | 🚧 stub | **SHIP** | L | CAIL2018 抽取管道 + 因子重要性模型 + 对话 Agent |
| 4-5 | 异步 Agent（并行+打断） | 🚧 stub | **SHIP** | M | 设计文档落地：并行工具、中断/取消、状态管理 |
| 5-1 | 代码解数学（AIME） | 无目录 | **SHIP** | M | 代码沙箱 vs 纯 CoT 准确率对比 |
| 5-2 | 逻辑（K&K） | 无目录 | **SHIP** | S | python-constraint 求解器 |
| 5-3 | 小模型代码化（τ-bench） | 无目录 | **SHIP** | M | 三层守卫 + expected_* 校验 |
| 5-4 | 论文→PPT（Slidev） | 无目录 | **SHIP** | M | proposer-reviewer + Vision-LLM 审查环 |
| 5-5 | 论文讲解视频 | 无目录 | **SHIP** | M | TTS + ffmpeg PPT→视频 |
| 5-6 | Blender 智能剪辑 | 无目录 | **SHIP** | M | Blender Python API + 两步场景定位 |
| 5-7 | 自适应日志解析 | 无目录 | **SHIP** | M | 失败检测→生成代码→浏览器测试→热重载 |
| 5-8 | 生产日志智能诊断 | 无目录 | **SHIP** | M | 轨迹分析→报告→回归测试→GitHub issue(MCP) |
| 5-9 | 动态表单意图澄清 | 无目录 | **SHIP** | M | Agent 生成级联 HTML 表单 |
| 5-10 | ERP Agent（NL→SQL） | 无目录 | **SHIP** | M | PostgreSQL schema + 10 查询 |
| 5-11 | 对话式界面定制 | 无目录 | **SHIP** | M | React+FastAPI + HMR |
| 6-5 | TTS 质量评估流水线 | 无目录 | **SHIP** | M | 多 provider 生成 + Gemini 多模态 Rubric 评审 |
| 6-7 | Agent 成本分析 | 无目录 | **SHIP** | S | tracing 成本拆解 + KV-cache/压缩 A/B |
| 6-8 | 多维度模型性能基准 | 无目录 | **SHIP** | M | 吞吐/TTFT/p95/可用性 压测 harness |
| 7-1/7-2 | 寻宝：Q-learning / RL vs LLM | — | **ALREADY** | — | 代码在 `chapter1/learning-from-experience`（已核实） |
| 7-3 | 从头训练 LLM（MiniMind 2） | 📖 fork | **KEEP-EXT** | S | 代码在 fork `bojieli/minimind`（QK-Norm+Muon，产出 README 中 loss 曲线）；钉 commit 8bdc5d9 |
| 7-4 | 自己训练 VLM（投影层从零训） | 📖 fork | **KEEP-EXT** | S | 代码在 fork `bojieli/minimind-v`（CLIP+LLM→从零训 projector→SFT，26M VLM，产出 README 结果）；钉 commit ead791c。注：`SFTvsRL/sft` 是另一类 VLM 实验（微调完整 Llama-3.2-Vision，对应 7-11/7-12） |
| 7-9 | CoT 蒸馏 [扩展] | 无目录 | **SHIP** | M | 规则验证器过滤 + 蒸馏 + 三步验收 |
| 7-10 | AdaptThink | 📖 ext | **KEEP-EXT** | M | 钉 `AdaptThink-original` commit + 结果表 |
| 7-11/7-12 | GeneralPoints / V-IRL | — | **ALREADY** | — | 代码在 `chapter7/SFTvsRL`（含 `gym_virl`） |
| 7-13 | SimpleVLA-RL [扩展] | 📖 ext | **KEEP-EXT** | M | 已有 rollouts；钉上游 + 结果表 |
| 7-14 | RLVP 奖励结果罚路径 [扩展] | 无目录 | **SHIP** | L(GPU) | 最大缺口：书用作者自己论文数字却零代码，须放出训练/评估 |
| 7-15 | ReTool | 📖 ext | **KEEP-EXT** | M | verl fork；钉 commit + run.sh + 结果表 |
| 7-16 | AWorld-train 沙盒 RL | 📖 ext | **KEEP-EXT** | S | 钉 commit 即可（无数字声明） |
| 8-3 | 系统提示词自动优化 | 无目录 | **SHIP** | M | tau-bench 上自动优化 + 对照 |
| 8-4 | 主动工具发现（120+工具） | 无目录 | **SHIP** | M | 第 8 章核心论点 |
| 8-5 | Alita 式网络找工具自进化 | 无目录 | **SHIP** | M | 第 8 章核心论点 |
| 8-6 | 自我进化评估数据集 | 无目录 | **SHIP** | S | 20 任务四层验证 |
| 9-2 | PineClaw 电话 Agent | 无目录 | **SHIP** | M | pine-voice SDK + make_phone_call 工具 ReAct Agent |
| 9-3 | Step-Audio R1 端到端 | 无目录 | **SHIP** | S | 端到端语音思考 demo（表 9-1 数字另补引用脚注） |
| 9-4 | Qwen2-Audio 流式感知 | 无目录 | **SHIP** | S | 分块识别延迟对照 demo |
| 9-5 | Fish Audio 控制标记 TTS | 无目录 | **SHIP** | S | 12 参考语音库 + 控制标记映射 demo |
| 10-1 | 阶段化系统提示 | 无目录 | **SHIP** | S | 需求/实现/审查三阶段角色切换 |
| 10-2 | 多角色 transfer_to_agent | 无目录 | **SHIP** | S | 五角色 + transfer_to_agent 工具 |
| 10-3 | 书籍翻译 Agent | 无目录 | **SHIP** | M | Manager/Glossary/Translation/Proofreading 四 Agent |
| 10-4/10-5 | 电话+电脑双 Agent | 📦 pointer | **KEEP-EXT** | — | 已指向 `19PINE-AI/TalkAct`（完成） |
| 10-6 | 多网站并行搜集 | 无目录 | **SHIP** | M | 10 Agent + 消息总线 + 级联终止 |
| 10-8 | 语音狼人杀 | 无目录 | **SHIP** | L | 法官 + 信息权限控制 + 实时语音多 Agent |

---

## 汇总

- **SHIP（约 28）**：新写参考实现。其中：
  - 轻量 S（约 10）：2-5、2-6、5-2、6-7、8-6、9-3、9-4、9-5、10-1、10-2 —— 建议先做（快速见效）。
  - 中等 M（约 16）：5-1、5-3~5-11、6-5、6-8、7-9、8-3、8-4、8-5、9-2、10-3、10-6、4-5。
  - 重 L/GPU（2）：3-13、7-14、10-8。
- **KEEP-EXT（8）**：7-3（`bojieli/minimind`）、7-4（`bojieli/minimind-v`）、7-10、7-13、7-15、7-16、10-4、10-5 —— 钉 commit + 结果表，不重写。
- **ALREADY（2 组）**：7-1/7-2（`chapter1/learning-from-experience`）、7-11/7-12（`chapter7/SFTvsRL`）—— 仅修正指向与命名。

## 建议 build order（分批）

1. **Batch 1 · 多 Agent 自包含（S/M，无外部依赖，教学价值高）**：10-1、10-2、10-3、10-6、4-5。
2. **Batch 2 · 第 8 章核心自我进化**：8-4、8-5、8-3、8-6。
3. **Batch 3 · 第 5 章 Coding Agent 应用**：5-1、5-3 先行，其余 5-2/5-4~5-11 跟进。
4. **Batch 4 · 第 6/9 章评估与语音 demo**：6-5、6-7、6-8、9-2~9-5。
5. **Batch 5 · 训练类**：KEEP-EXT 薄壳（7-10/13/15/16）→ GPU 训练（7-3、7-14）→ 3-13、10-8。

## 待决策（需作者拍板）

1. ~~7-4 VLM~~ **已解决**：投影层从零训的代码是 fork `bojieli/minimind-v`（26M VLM），与 7-3 的 `bojieli/minimind` 同源。按 KEEP-EXT 补 clone 指引即可。
2. **7-14 RLVP**：RLVP 是 github.com/19PINE-AI/rlvp 论文，直接 README reference 就行了。
3. **孤儿 stub 目录**：`chapter8/feedback-guided-sampling`、`learn-from-observation` 删除。

