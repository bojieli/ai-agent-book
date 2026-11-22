# 《AI Agent》配套 Skills

本书 10 章内容蒸馏为 22 个开发 skill。每个 skill 是一个按需触发的操作知识包：当你的开发任务匹配其触发条件时会被自动加载，提供该领域的决策框架、实践模式与书中实验代码的入口。

## 安装

```bash
# 方式一：拷贝到用户级 skill 目录（全局生效，任何项目可用）
cp -R skills/*/ ~/.claude/skills/

# 方式二：软链（跟随仓库更新，推荐）
for d in skills/*/; do ln -sfn "$(pwd)/${d%/}" ~/.claude/skills/"$(basename $d)"; done
```

## 第一部分：如何构建 Agent

| Skill | 触发场景 | 对应章节 | 配套代码 |
|---|---|---|---|
| `context-engineering` | 设计系统提示词、上下文结构、按需加载的 Skill | ch2 | `chapter1/context/`、`chapter2/prompt-engineering/` |
| `kv-cache-design` | 优化推理延迟与成本、诊断缓存命中率下降 | ch2 | `chapter2/kv-cache/` |
| `context-compression` | 上下文膨胀、决策质量随轮次下降 | ch2 | `chapter2/context-compression/` |
| `agent-state-bar` | Agent 无限循环、遗忘 TODO、思考 token 膨胀 | ch2 | `chapter2/system-hint/` |
| `memory-system` | 设计/实现/评估用户记忆系统 | ch3 | `chapter3/user-memory/`、`mem0/`、`memobase/` |
| `rag-pipeline` | 搭建或调优 RAG 检索管道 | ch3 | `chapter3/retrieval-pipeline/`、`dense-embedding/` |
| `knowledge-org` | 组织超越扁平文本块的知识（RAPTOR/GraphRAG） | ch3 | `chapter3/structured-index/`、`agentic-rag/` |
| `tool-design` | 设计 Agent 工具、判断能力形态 | ch4 | `chapter4/perception-tools/`、`execution-tools/` |
| `tool-discovery` | 工具数量变多、上下文被工具定义占满 | ch4 | `chapter4/active-tool-discovery/` |
| `mcp-skill-hub` | 接入第三方能力，MCP 还是 Skill Hub | ch4 | `chapter4/DOCKER_DEPLOYMENT.md` |
| `coding-agent-harness` | 搭建 Coding Agent、设计护栏 | ch5 + ch1 | `chapter5/coding-agent/` |
| `error-recovery` | 故障恢复、流式中断、跨厂商接管 | ch5 | `chapter5/provider-failover/` |
| `async-event-agent` | 异步/事件驱动 Agent、外部事件响应 | ch6 | `chapter6/async-agent/` |
| `computer-use` | GUI 自动化 Agent、视觉定位 | ch6 | `chapter6/claude-computer-use-native/` |

## 第二部分：如何提升 Agent 能力

| Skill | 触发场景 | 对应章节 | 配套代码 |
|---|---|---|---|
| `agent-evaluation` | 建立评估体系、设计指标与环境 | ch7 | `chapter7/tau2-bench-eval/`、`model-benchmark/` |
| `eval-dataset-design` | 设计评估数据集、解剖评估任务 | ch7 | `chapter7/tau2-bench-eval/`、`android-world/` |
| `post-training-strategy` | 选择 Mid-training / SFT / RL 路线 | ch8 | `chapter8/continued-pretraining/`、`retool/` |
| `reward-design` | 设计奖励函数、排查奖励黑客 | ch8 | `chapter8/RLVP/`、`retool/` |
| `bad-case-to-dpo` | 把生产 bad case 转成训练数据 | ch8 + ch9 | `chapter8/premature-completion-dpo/` |
| `agent-evolution` | 从运行经验持续学习、自进化闭环 | ch9 | `chapter9/self-evolution-eval/`、`self-evolving-tools/` |
| `multi-agent-design` | 单 Agent 还是多 Agent、协作拓扑 | ch10 | `chapter10/generative-agents/`、`parallel-web-research/` |
| `loop-engineering` | Agent 过早宣称完成、设计验证器 | ch10 | `chapter5/paper-to-ppt/`、`video-edit/` |

## 约定

- 每个 skill 是单文件 `SKILL.md`，自包含，可独立使用
- skill 内所有路径相对仓库根（如 `chapter4/active-tool-discovery/`、`book/chapter4.md`），方便回到原书与实验代码深入
- 内容为书中知识的蒸馏（判断规则、步骤、关键数字），非书段摘抄
- 修改 skill 后同步到 `~/.claude/skills/`（软链方式自动生效）
