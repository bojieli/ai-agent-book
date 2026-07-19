# 实验 10-1：根据执行阶段决定系统提示词（Staged System Prompt）

《深入理解 AI Agent》配套实验代码。

## 实验目的

同一个 Coding Agent，在任务的不同**执行阶段**加载**不同的系统提示词 + 不同的工具集**，
从而在同一段对话里扮演不同角色、表现出不同的行为模式；同时让**对话历史与任务状态在阶段间连续共享**。

本实验用一个「Coding Agent」串起三个阶段：

| 阶段 | 角色 | 系统提示词强调 | 配套工具集 | 触发进入下一阶段的工具 |
| --- | --- | --- | --- | --- |
| 1 需求澄清 | 需求分析师 | 只提问确认、**不写代码** | `ask_clarifying_question` / `save_requirement` / `complete_requirements_analysis` | `complete_requirements_analysis` → 阶段2 |
| 2 代码实现 | 软件工程师 | 按已确认需求写高质量 Python | `write_file` / `read_file` / `execute_code` / `submit_for_review` | `submit_for_review` → 阶段3 |
| 3 代码审查 | 代码审查员 | 批判性把关质量 | `run_linter` / `run_tests` / `analyze_complexity` / `request_revision` / `approve_code` | `request_revision` → **回退阶段2**；`approve_code` → 完成 |

## 架构

```
demo.py                入口：一条命令跑通三阶段（任务 = “写一个整理下载文件夹的 Python 脚本”）
agent.py               StagedAgent：阶段状态机 + 工具调用循环 + 跨阶段共享上下文 + 执行日志
tools.py               三套工具的 Schema 与真实实现（虚拟工作区 / 真实执行代码 / linter / 复杂度分析）
simulated_user.py      模拟用户：需求澄清阶段自动回答 Agent 的提问（预设答案），实现无人值守
config.py              从环境变量读取 API Key / base_url / model
```

关键设计：

- **共享上下文**：`StagedAgent.history` 是一条贯穿始终的消息列表，切换阶段时**只替换 system 提示词、只切换传给模型的 tools**，历史消息（需求、代码、审查意见）全部保留。每次请求都是 `[system(当前阶段)] + history`。
- **阶段转换由工具调用触发**：主循环识别到 `complete_requirements_analysis` / `submit_for_review` / `request_revision` / `approve_code` 这些「信号工具」被调用时，注入一条跨阶段「交接」消息并切换阶段。
- **回退机制**：审查阶段发现问题时调用 `request_revision(issues)`，把问题清单退回实现阶段；设有 `max_revisions` 安全阀，避免无限循环烧 token。
- **真实执行**：`execute_code` / `run_tests` 会把代码写入临时目录并用子进程真实运行；`run_linter` / `analyze_complexity` 基于 `ast` 做真实静态分析，不是假返回。

## 如何运行

```bash
pip install -r requirements.txt

# 配置（二选一）
export OPENAI_API_KEY=sk-...           # 方式 A：直接 export
cp env.example .env && vi .env         # 方式 B：写到 .env

python demo.py

# 离线查看三阶段配置（角色 / 系统提示词 / 工具集 / 转换信号），无需 API Key
python demo.py --list-stages

# 查看可选参数（不影响默认行为）
python demo.py --help
```

可选命令行参数（默认值与不加参数完全一致）：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--task` | 整理下载文件夹的任务 | 覆盖交给 Agent 的用户任务 |
| `--start-stage` | `requirements` | 从哪个阶段开始。选 `implementation` 会预置一份等价于需求澄清产物的已确认需求、直接从实现阶段起步，便于单独调试后两个阶段（`review` 依赖实现阶段的代码，不能作为起点） |
| `--interactive` | 关 | 需求澄清阶段改由真人从标准输入回答 Agent 的提问（默认用 `simulated_user.py` 的模拟用户自动回答，可无人值守跑通全流程） |
| `--max-revisions` | `3` | 审查阶段允许的最大回退次数，超过则强制结束演示 |
| `--model` | 环境变量 `OPENAI_MODEL` | 覆盖使用的模型名 |
| `--list-stages` | — | 离线打印三阶段配置后退出，不调用任何 API（适合无 Key 时先看清机制） |

可配环境变量（见 `env.example`）：`OPENAI_API_KEY`、`OPENAI_BASE_URL`（默认官方）、
`OPENAI_MODEL`（默认 `gpt-5.6-luna`，当前便宜旗舰）、`OPENAI_TEMPERATURE`（默认 0.3）。
也可切到兼容 OpenAI 协议的 Kimi / Doubao。

**通用回退**：优先用 `OPENAI_API_KEY` 直连 OpenAI；若未设置该变量但设了
`OPENROUTER_API_KEY`，则自动改走 OpenRouter，并把模型名映射到其命名空间
（`gpt-5.6-luna` → `openai/gpt-5.6-luna`）。提示：`gpt-5.6` 系列直连 OpenAI 需组织验证，
只填 `OPENROUTER_API_KEY`（不填 `OPENAI_API_KEY`）即可强制走 OpenRouter，更省事。

## 演示说明了什么问题

一次真实运行（`gpt-5.6-luna`）会看到：

1. **需求澄清阶段**：Agent 表现为「不断提问」——主动追问处理哪些文件类型、是否递归、是否保留原名、移动还是复制、目标目录怎么定，并逐条 `save_requirement`。它**完全不写代码**。
2. **代码实现阶段**：同一个 Agent 换了提示词后表现为「写代码」——`write_file` 产出 Python 脚本，`execute_code` 自测，然后 `submit_for_review`。
3. **代码审查阶段**：Agent 表现为「批判审查」——依次跑 `run_linter` / `run_tests` / `analyze_complexity`，发现真实问题（如缺少模块 docstring、冒烟测试 `FileNotFoundError`）后 `request_revision` **退回实现阶段**。
4. 实现阶段据问题清单**重写并修复**，再次提交；审查通过后 `approve_code`，任务完成。

也就是说：**提示词 + 工具集随阶段切换，行为模式随之明显不同**，而任务状态（需求、代码、审查意见）在阶段间始终连续共享。运行结束时会打印每个角色的「行为分布」统计，直观对比三个阶段的行为差异。

## 预期输出示例

以下是一次真实运行（`python demo.py`，`gpt-5.6-luna`，经 OpenRouter 路由）的节选，完整展示三阶段的行为切换
（本次运行需求澄清阶段反复追问了大小写规则、触发了 1 次审查回退，最终撞到总步数上限
安全阀结束，也是真实运行中常见的一种结局，详见下方「局限」）：

```
模型：openai/gpt-5.6-luna  | base_url：https://openrouter.ai/api/v1

======================================================================
进入阶段：requirements  |  角色：需求分析师  |  可用工具：['ask_clarifying_question', 'save_requirement', 'complete_requirements_analysis']
======================================================================
[需求分析师] 提问: 你希望脚本整理哪些文件类型？例如按扩展名整理所有常见文件，还是只处理图片、文档、视频等指定类型？
[需求分析师] 模拟用户回答: 按文件类型分类：图片(jpg/png/gif)、文档(pdf/doc/txt)、音频(mp3/wav)、视频(mp4/mov)、压缩包(zip/rar)，其余归到 Others。
[需求分析师] 记录需求: file_categories = 按文件类型分类：图片 jpg/png/gif；文档 pdf/doc/txt；音频 mp3/wav；视频 mp4/mov；压缩包 zip/rar；其他扩展名归入 Others。
[需求分析师] 提问: 整理时是否需要递归处理下载文件夹的子目录，还是只处理下载文件夹根目录中的文件？
[需求分析师] 记录需求: recursive = 不递归处理子目录，只整理下载文件夹当前层级的文件，忽略已有子文件夹。
[需求分析师] 记录需求: operation = 移动文件（move），不保留原位置的文件。
[需求分析师] 记录需求: name_conflicts = 保留原文件名；目标目录存在同名文件时，在扩展名前添加 _1、_2 等序号，避免覆盖。
...（模拟用户对「扩展名是否区分大小写」只会给出兜底回答，Agent 因此反复追问同一点，共提问 19 次）
[需求分析师] 完成需求分析 -> 转交实现: 已确认：脚本按指定扩展名分类并将其他文件归入 Others；仅处理下载目录当前层级；默认路径为 ~/Downloads、也可通过命令行参数指定；移动文件而非复制；扩展名不区分大小写；保留原文件名，冲突时追加 _1、_2 等避免覆盖。

======================================================================
进入阶段：implementation  |  角色：软件工程师  |  可用工具：['write_file', 'read_file', 'execute_code', 'submit_for_review']
======================================================================
[软件工程师] 写文件: 已写入文件 organize_downloads.py（4312 字符，135 行）
[软件工程师] 执行代码自测: from pathlib import Path from tempfile import TemporaryDirectory import organize ...
[软件工程师] 提交审查 -> 转交审查: organize_downloads.py

======================================================================
进入阶段：review  |  角色：代码审查员  |  可用工具：['run_linter', 'run_tests', 'analyze_complexity', 'request_revision', 'approve_code']
======================================================================
[代码审查员] run_linter: [linter] 通过：未发现问题。
[代码审查员] run_tests: [tests] 冒烟测试结果：FAIL
[代码审查员] analyze_complexity: [complexity] 函数数量=6，分支/循环语句=16，最大嵌套深度=3
[代码审查员] 审查不通过 -> 回退实现: 第1次退回：['冒烟测试失败：`from __future__ import annotations` 不在文件开头触发 SyntaxError，请移除该 future import 或改用兼容写法。']

======================================================================
进入阶段：implementation  |  角色：软件工程师  |  可用工具：['write_file', 'read_file', 'execute_code', 'submit_for_review']
======================================================================
[软件工程师] 写文件: 已写入文件 organize_downloads.py（4218 字符，133 行）
[软件工程师] 提交审查 -> 转交审查: organize_downloads.py

...（审查阶段再次检查，如此循环，直到 approve_code 或达到步数/回退上限）

======================================================================
执行小结
======================================================================
[需求分析师] 行为分布：提问×19, 模拟用户回答×19, 记录需求×7, 完成需求分析 -> 转交实现×1
[软件工程师] 行为分布：写文件×2, 执行代码自测×4, 读文件×1, 提交审查 -> 转交审查×2
[代码审查员] 行为分布：run_linter×1, run_tests×1, analyze_complexity×1, 审查不通过 -> 回退实现×1

已确认需求条数：7
产出文件：['organize_downloads.py']
审查回退次数：1
```

三段「行为分布」清楚对照出同一个 Agent 在三种提示词下的不同行为模式：需求分析师只问不写，
软件工程师只写不审，代码审查员只查不写。

## 更强的模型会让这套「阶段脚手架」变得多余吗？

一个常见直觉是：脚手架（这里指「按阶段切换系统提示词 + 工具集」的状态机）只是给弱模型用的拐杖，
换上更强的模型，它自然会「先澄清、再实现、后审查」地自我组织，脚手架随之失效。
用同一套代码、同一个任务、同一个模拟用户，本地各**真实**跑一次 `gpt-4o-mini` 与 `gpt-5.6-luna` 对照，
结论是否定的：

| 观察项 | `gpt-4o-mini`（较弱） | `gpt-5.6-luna`（较强推理模型） |
| --- | --- | --- |
| 需求澄清提问次数 | 5（一问一点，问完即走） | **21**（反复纠缠「大写扩展名 / 无扩展名文件如何归类」这一个边角情形） |
| 是否跑完三阶段拿到 `approve_code` | **是**（1 次回退后审查通过、任务完成） | **否**（撞到 40 步总步数安全阀被强制结束） |
| 审查回退次数 | 1 | 1 |

（运行命令：`MODEL=gpt-4o-mini python demo.py --model gpt-4o-mini`；`python demo.py --model gpt-5.6-luna`。
后者经 OpenRouter 路由为 `openai/gpt-5.6-luna`。）

要点有两个：

1. **这套脚手架不是「可以关掉的拐杖」，而是结构性约束。** 每个阶段只把本阶段的工具暴露给模型
   （需求阶段根本没有 `write_file`，实现阶段根本没有 `approve_code`），角色分离是被**工具门控**强制出来的，
   对强弱模型一视同仁——没有哪个模型能「自我组织」跳过或合并阶段。也正因如此，本实验里**并不存在**
   一个「关掉脚手架、让强模型自由发挥」的基线可供严格对照。
2. **换上更强的模型并没有让脚手架变多余，反而更依赖它的安全阀。** `gpt-5.6-luna` 更「较真」，
   坚持把一个模拟用户答不上来的边角规则问到底，而且聪明到每次都换一种问法，
   恰好绕开了 `SimulatedUser`「同一问题问两次就催它进入下一阶段」的防重复机制，
   于是在需求阶段空转了二十多步、把 40 步预算烧光——最后是 `max_total_steps` 这个脚手架安全阀替它兜的底；
   较弱的 `gpt-4o-mini` 反而因为「问几个大方向就收手」顺利跑完了全程。

**诚实的边界**：`gpt-5.6-luna` 这次没跑完，很大程度上是被预设答案的 `SimulatedUser`（见「局限」）拖累的——
它答不上强模型追问的边角问题，才诱发了空转；换真人回答（`--interactive`）或更聪明的模拟用户，
强模型大概率能更快收敛。所以这组数据**不能**推出「强模型在这个任务上更差」，
只能支持一个更窄、但对读者更有用的结论：**阶段化提示词 + 工具门控是一种结构性脚手架，
它带来的角色分离与安全阀对强弱模型同样生效，不会因为模型变强就自动失效或变得多余。**

## 局限

- **依赖所选模型的能力**：默认用便宜旗舰 `gpt-5.6-luna` 控制演示成本。注意「更强的模型 = 更快收敛」
  并不总成立：越较真的推理模型越容易在需求澄清阶段追问预设 `SimulatedUser` 答不上的边角问题而空转
  （见上一节的真实对照），此时更依赖 `max_total_steps` / `max_revisions` 这两个脚手架安全阀兜底。
- **单一固定任务**：内置演示任务是「整理下载文件夹」，虽然新增了 `--task` 参数可覆盖，
  但 `simulated_user.py` 的预设问答是围绕这个任务场景设计的，换成差异很大的任务时模拟用户可能答不上点子上。
- **模拟用户是预设答案**：`SimulatedUser` 按关键词匹配预设回答，不是真正理解语义的用户，
  遇到 Agent 提出预设脚本之外的问题时会退化为兜底回答或催促进入下一阶段。
- **真实 LLM 有随机性**：即使 `temperature=0.3`，不同次运行的提问顺序、代码实现细节、
  审查是否通过、回退次数都可能不同；也可能像上面这次示例一样撞到 `max_revisions` 安全阀
  强制结束，而不是拿到 `approve_code`。
