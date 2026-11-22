# 生成一个专用 Agent 需要交付什么

让 Agent“再创建一个 Agent”，不是只写一段系统提示词。本实验从需求出发生成专用程序，并与复用已有框架的路径比较，学习如何判断生成结果是否真的可用。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4)。

<a id="learning-0"></a>

## 理解问题与方法

专用 Agent 需要明确任务、可用工具、控制流程和完成条件。复用框架可以减少基础设施工作，从零实现则更自由；两者都必须经过行为检查，不能只比较生成文件的数量。

### 比较从零生成与模板改造

实验 5-13 要求同一个真实模型构造两个专用 Agent。第一条路线从零生成 Agent 循环、工具协议、领域工具、命令行入口和测试；第二条路线复制 `reference_agent`，保留已有的消息与工具循环，只修改领域提示、工具定义、实现、文档和测试。

这样设计是为了区分两个问题：模型能否写出领域逻辑，以及它能否同时正确组织通用的 Agent 协议。模板路线减少了后一个问题的生成负担，但仍需证明新增的领域行为符合要求。

<a id="learning-1"></a>

## 准备环境与输入

下面会用到模型服务。先按配置说明选择一个提供商，准备对应的模型名称、服务地址和 API Key，再运行小规模例子。一次完整运行的费用取决于模型、输入长度和调用次数。

### 安装依赖并配置创建者模型

从仓库根目录执行下面的安装步骤，在 `.env` 中填写所选服务的凭据。`demo.py` 会调用真实模型生成两个版本，并进一步运行生成的 Agent；缺少凭据或真实运行失败时，默认命令会报错，不会自动用模拟结果替代。

```bash
cd chapter5/agent-creator
pip install -r requirements.txt
cp env.example .env
python demo.py --output runs/release-agent
```

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读默认需求与验证器，写出专用 Agent 应完成的一个正常任务和一个边界情形。配置模型后运行生成流程，再检查产物结构、依赖与验证结果。最后改变需求中的一项，观察哪些部分需要重新生成。

### 先做一个小规模观察

以下命令从本实验目录执行。先完成前面的环境准备，再观察这条路径的输入和输出。

```bash
python demo.py --output runs/release-agent
```

### 为自己的任务生成一个 Agent

先读默认产物，再替换需求。例如，下面把目标改为检查服务健康并起草升级处理建议。保持其他配置不变，才能比较两种创建路线如何处理同一需求。

```bash
python demo.py \
  --requirements "Create an incident triage Agent that queries service health and drafts an evidence-backed escalation" \
  --output runs/incident-triage
```

`--no-live` 用于确定性的单元测试，可以学习生成与验证流程；它跳过真实运行，因此不能回答“生成的 Agent 是否能在真实模型下完成任务”。

<a id="learning-3"></a>

## 分析结果与形成判断

生成脚本成功结束不等于产物可以独立运行。还应确认工具调用、错误处理和输出证据与需求一致。验证器覆盖不到的行为需要单独说明。

### 从文件可用走到任务完成

两条路线依次经过相同的检查：必需文件与凭据扫描、Python AST/编译、`assistant.tool_calls → role=tool` 消息协议、循环次数限制、生成的 pytest 测试，以及生成 Agent 自身样例任务的真实 API 运行。前面几项通过只说明结构可用，最后一项才开始检验实际协作行为。

`comparison.json` 同时记录生成耗时、token 用量、每项检查、真实轨迹与策略比较结果。先定位失败发生在哪一层，再解释哪种路线更合适。

### 检查自己的解释

哪些职责应该由生成的 Agent 自己完成，哪些基础能力适合从已有框架继承？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 沿创建、验证和执行三个入口阅读

`creator.py` 组织两条生成路线；`reference_agent/` 是模板来源；`validator.py` 实现共同的结构、测试和运行检查；`demo.py` 连接完整流程；`test_creator.py` 检查创建者的编排与边界。生成路径有允许范围，凭据不应进入提示或产物，真实执行发生在结构和测试检查之后。生成工具最终仍会执行本地代码，因此先在独立实验目录审阅和试运行，再用于其他项目。

## English

# Experiment 5-13: An Agent That Creates Agents

This is the runnable companion for Chapter 5, Experiment 5-13. It implements the
book's complete comparison rather than merely pointing at `coding-agent` as a
possible starting point.

The experiment asks the same real model to create two specialized Agents:

1. **From scratch**: generate the Agent loop, tool protocol, domain tools, CLI,
   and tests with no reference implementation.
2. **Template adaptation**: copy the proven `reference_agent`, preserve its
   standard message/tool loop, and generate only the domain-specific prompt,
   tool schemas, implementations, documentation, and tests.

Both outputs pass the same gates:

- required-file and secret scan;
- Python AST/compile validation;
- standard `assistant.tool_calls → role=tool` protocol audit;
- bounded-loop audit;
- generated pytest suite;
- a real API run of the generated Agent on its own sample task.

The resulting `comparison.json` records generation time and token use, every
validation gate, the live Agent trace, and the winning strategy. There is no
mock fallback in the default experiment: missing credentials or a failed live
Agent run fails the command.

## Run

```bash
cd chapter5/agent-creator
pip install -r requirements.txt
cp env.example .env
python demo.py --output runs/release-agent
```

Use a custom target:

```bash
python demo.py \
  --requirements "Create an incident triage Agent that queries service health and drafts an evidence-backed escalation" \
  --output runs/incident-triage
```

`--no-live` exists only for deterministic CI/unit testing. It is not considered
a completed experiment run.

## Files

- `creator.py`: real-model creator and the two controlled comparison arms.
- `reference_agent/`: the known-good Agent that template mode copies.
- `validator.py`: common structural, test, and live-runtime gates.
- `demo.py`: one-command end-to-end comparison.
- `test_creator.py`: creator safety and orchestration tests.

## Security boundary

Generated paths are allowlisted, credentials are never placed in prompts or
generated files, and live execution occurs only after structural and test gates.
Generated domain tools still execute local code, so review them before using the
output outside an isolated experiment directory.
