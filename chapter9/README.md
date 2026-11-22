# 第 9 章 · Agent 的持续进化

客服助理答应退款，订单却还处于已确认状态。下一次遇到同样的问题，改一条指令就够了吗？本章从这样的办事记录出发，判断该更新知识、指令、程序还是模型参数，再用独立的任务检验改动。读过第七章评估后，可以直接从这里开始。

[返回主目录](../README.md) · [读第九章正文](../book/chapter9.md)

## 从一次失误到下一次验证

1. **先查退款有没有办成。** 打开[实验 9-1 的八份诊断](trajectory-verifier/validation/real_20260729T165247Z/evidence.json)，在 `reports` 中对照 `real-normal-refund-01` 和 `real-false-promise-01`。第一笔订单已退款，记录金额为 480；第二笔应退 610，记录却仍为 0。沿着订单状态、工具调用和客服答复往回查，才能分别判断事情办成了没有、哪一步出了错、怎样向用户解释。
2. **再判一条新指令能否试用。** [实验 9-3](prompt-auto-optimization/README.md)换成航空客服过早转人工的案例。先读乘客要求免掉 200 元改签费的那道题，自己判一次，再看评审为什么接受了退税费的回答。五道旧业务题三个版本都通过了；用来提炼补丁的五道争议题重新跑一遍，评审给旧指令、自动改写和人工改写分别判了 0、2、4 题通过。自动改写达到了小范围试用条件。要知道能否处理新争议，还得另出题。若需要改的是程序，再看[实验 9-6](self-modifying-agent/README.md)怎样验证补丁以及何时回滚。
3. **最后让规则随时间改变。** [实验 9-9](self-evolution-eval/README.md)把行李限额从 20 公斤改为 23 公斤。沿后续任务找出系统第一次采用新限额的时刻，再查它是否又引用了旧限额，以及退款、身份核验这两类任务是否仍能办好。

想复查一次更新为什么获准或被退回，可以从对应实验的运行记录查起，分别找出触发修改的原始轨迹、验证所用的边界题和保留题，以及最后采用的版本。实验 9-7 还演示了怎样让负责发布前检查的程序独立于待审补丁。

## 配套实验

| 编号 | 项目 | 类型 | 一句话说明 |
| :--: | --- | :--: | --- |
| 9-1 | [trajectory-verifier](trajectory-verifier/) | ✅ | 实验 9-1：28 条真实客服调用、8 次 Judge 调用与 8 条专家标注样本已通过验收；[证据](trajectory-verifier/validation/real_20260729T165247Z/evidence.json)同时记录关键违规稳定性主张未复现 |
| 9-2 | [tau2-escalation-experience](tau2-escalation-experience/) | ✅ | 实验 9-2：τ²-bench telecom 上由模型从 19 条失败轨迹提炼转接与工具使用规则；迁移集 114 条通过率 12.3% → 19.3%，零回归；[证据](tau2-escalation-experience/validation/evidence.json)保留提炼回执、三臂策略哈希与行为指标 |
| 9-3 | [prompt-auto-optimization](prompt-auto-optimization/) | ✅ | 实验 9-3：真实任务 Agent、LLM Judge 与 Coding Agent 跑完初始/自动/人工三组完整保留集和边界集；原始回执与发布门槛已保存 |
| 9-4 | 正文对照实验 | 🚧 | 从用户反馈中进化“需求澄清 + Spec 确认”Skill；正文给出三臂 A/B 设计、指标和发布门槛，配套实现待补充 |
| 9-5 | [browser-use-rpa](browser-use-rpa/) | ✅ | 实验 9-5：真实 ARK Agent + Chromium 在可重置本地消息站完成探索、独立验证、参数化回放、假成功对照与页面变化失效 |
| 9-6 | [self-modifying-agent](self-modifying-agent/) | ✅ | 实验 9-6：真实 Coding Agent 从重复故障生成补丁，并与确定性提案、故意过宽的反例通过同一回归/灰度/回滚发布门；[证据](self-modifying-agent/validation/latest.json)保留接受与拒绝历史 |
| 9-7 | [harness-safety-gate](harness-safety-gate/) | ✅ | 实验 9-7：用户纠正/点踩/事后审计触发“高风险调用确认门禁”提案，经 AST 静态检查、未完成任务回放和正常操作回放；确定性提案通过，真实 `gpt-4o-mini` 提案因检查失败被安全拒绝，整体验收通过 |
| 9-8 | [hermes-self-evolution](hermes-self-evolution/) | 📖 | 实验 9-8：把整本书和源码交给 Hermes；它读完后选择一项改进，亲手修改自己，并把每次 Reviewer 的退回变成下一轮学习，直到通过 |
| 9-9 | [self-evolution-eval](self-evolution-eval/) | ✅ | 实验 9-9：static、append-only、evolving 三臂 × 3 seeds × 14 任务共 126 次真实调用；[证据](self-evolution-eval/validation/latest.json)保留迁移、规则替换、保持与配对统计 |

带项目链接的实验都保留无需 API Key 的离线入口和单元测试用于预检。

## 补充案例

| 编号 | 项目 | 关系 |
| :--: | --- | --- |
| 8-8 | [prompt-distillation](../chapter8/prompt-distillation/) | Prompt 蒸馏与参数化学习的跨章项目；训练方法归入第八章 |
| — | [self-evolving-tools](self-evolving-tools/) | Alita 式工具发现、封装与复用，是“将经验写成程序”的补充案例 |
| — | [ai-style-skill](ai-style-skill/) | 写作型 Skill 的补充实验：把“去 AI 味”反馈提炼为可检查规则；正文示例移至第二章，自动更新管道和验收数据保留在项目 README |

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **进行中** | 已有实现，但真实数据、真实环境或纵向验收证据尚未完整 |
