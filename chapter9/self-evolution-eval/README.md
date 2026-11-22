# 实验 9-9：评估 Agent 是否在持续进化

真正的持续进化不只是同一道题第二次做对。系统还应把规律用于新任务，适应规则变化，并保留没有过时的能力。本实验通过顺序任务流分别观察这些阶段。

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4)。

<a id="learning-0"></a>

## 理解问题与方法

学习阶段提供经验，迁移阶段改变表述或环境，规则变化阶段要求更新，保持阶段检查旧能力。按顺序运行才能看到状态积累的影响；把每题独立重置会改变研究对象。

本实验把评估对象从“单次任务是否成功”扩展到一条长期任务流。任务不会简单重复，而是依次经历四个阶段：学习阶段暴露可共享规律，迁移阶段更换表述和环境，规则变化阶段要求修订旧能力，保持阶段重新测试未变化能力与当前有效规则。

<a id="learning-1"></a>

## 准备环境与输入

先从本地示例开始。依赖安装可能需要联网，但下面标明的离线路径不需要模型 API Key。若随后切换到真实模型，请再完成相应的服务配置。

### 数据与对照条件

`dataset.json` 包含退款、身份核验和行李政策三个任务族。行李规则在第三阶段从 20kg 改为 23kg，因此只会追加知识、不会淘汰旧规则的 Agent 会在变化阶段和保持阶段持续失败。参考 Agent 路径完全离线；真实验收路径需要 API Key，而且每个臂的每一道题都由真实模型决策。

三个真实模型臂共享同一模型、任务顺序、Seed 调度和提示协议，唯一差别是模型外记忆生命周期：

```bash
# 从仓库根目录开始：使用共享的第 9 章环境
uv sync --locked --python 3.12 --extra ch9
# Apple Silicon macOS 需要 macOS 14+（锁文件中的 bitsandbytes wheel 要求）；
# 更早的 macOS 请使用下方单项目兼容路径。

# 切换目录前先激活环境：
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch9]"

cd chapter9/self-evolution-eval

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

export OPENAI_API_KEY=your_api_key_here
python demo.py --profile llm --model gpt-5.6 --output output/llm-report.json
```

- `static` 从不持久化反馈；
- `append_only` 保存每条观察和冲突，但始终激活第一版规则；
- `evolving` 保存版本及来源，以更高版本替换旧规则并保留 `superseded` 审计记录。

Harness 在模型返回并记录当前动作之后才暴露学习信号；发往模型的请求只含任务输入和此前已激活的记忆，不含 `expected_action` 或 `learning_signal`。原始请求/响应、响应 ID、Seed、时间戳、Token、延迟和哈希全部写入 `validation/<run>/evidence.json`，`validation/latest.json` 是最近一次规范证据。凭据值从不写入证据。

`demo.py` 提供三个可控参考 Agent，用于校验指标方向：

- `evolving` 能保存经验，也能用更高版本替换旧规则；
- `append_only` 能学习第一版规则，却不能更新或淘汰它；
- `static` 不持久化任何生产反馈。

它们不是被宣称为真实模型，而是用于检查评估框架是否能区分三种长期行为。你可以用自己的 Agent 替换 `ReferenceAgent`，只需实现 `act(task)`、`observe(task)`、`profile` 和 `storage_bytes`。

<a id="learning-2"></a>

## 按照步骤完成实验

先运行参考策略演示，阅读任务流中的阶段划分。找出某条规则何时出现、何时失效。理解评价逻辑后，再按下文运行真实模型比较。

### 运行参考策略与真实模型

```bash
# 参考 Agent 只校验 Harness，不算真实实验验收
python -m pytest -q test_longitudinal.py test_campaign_statistics.py
python demo.py --profile all --output output/reference-report.json

# 真实验收：3 个真实模型臂 × 3 个种子 × 14 个顺序任务 = 126 次 API 调用
python run_experiment_9_9.py \
  --provider ark --model doubao-seed-1-6-250615 \
  --seeds 8601,8602,8603 --workers 6
```

<a id="learning-3"></a>

## 分析结果与形成判断

参考策略分数用于检查评估框架，不代表真实模型能力。汇总时应分别报告学会、迁移、忘记旧规则与保留有效规则的表现。

### 真实重复实验结果

仓库内的规范运行使用 Ark `doubao-seed-1-6-250615` 和种子 8601、8602、8603。三次重复的核心比例完全一致：

| 臂 | 迁移准确率 | 适应恢复分 | 规则替换准确率 | 废止规则引用率 | 保持率 | 未变化能力保持率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `static` | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| `append_only` | 1.000 | 0.000 | 0.000 | 1.000 | 0.667 | 1.000 |
| `evolving` | 1.000 | 0.500 | 1.000 | 0.000 | 1.000 | 1.000 |

`evolving` 在收到第一条 23kg 新规则之后的下一题恢复正确，并在保持阶段继续使用 23kg；`append_only` 的迁移很好，却在后续所有替换检查中继续引用 20kg。这正是本实验需要区分的“记得住”和“会演化”。126 次调用合计 48,318 输入 Token、35,222 输出/推理 Token、83,540 总 Token。供应商没有返回金额字段，因此证据只报告 Token、延迟和存储实测值，不猜测美元成本。

### 报告指标

`LongitudinalEvaluator` 输出每阶段准确率、学习曲线、迁移准确率、规则变化后的恢复速度、规则替换准确率、废止规则引用率、未变化能力保持率、当前规则保持率、负迁移率、安全 Rubric 通过率，以及 Token、时间和存储成本。还分别报告修改提案有效率、产物激活率和记忆遵循率。重复实验对每个指标给出均值、样本标准差和 95% t 区间，并按相同 Seed 报告 `evolving-static` 与 `evolving-append_only` 配对差。

其中“规则变化后的恢复速度”以收到第一条新规则信号后，还需要多少个任务恢复正确为准；“负迁移”统计 Agent 调用了已有经验却因此答错的情况；保持率只按最后阶段的当前有效规则计算，避免把继续执行已经废止的旧政策误当成记忆良好。

这个实验刻意避免把全部指标压成一个总分。一个 Agent 可能迁移很好，却无法更新旧知识；也可能保持率高，却靠违反规则的捷径完成任务。持续进化只有在适应性、保持性、效率和安全性同时可见时才有可解释的意义。

### 检查自己的解释

一个系统在新规则上进步，却忘掉仍有效的旧规则，应该怎样描述它的变化？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 文件说明

| 文件 | 作用 |
| --- | --- |
| `dataset.json` | 四阶段顺序任务流与环境反馈 |
| `agent.py` | 三种参考行为与 static / append-only / evolving 三种真实模型臂 |
| `harness.py` | 长期运行、分阶段统计、成本与安全评估 |
| `demo.py` | 命令行对照实验 |
| `run_experiment_9_9.py` | 重复、带 Seed 的三臂真实模型实验与统计/证据生成 |
| `test_longitudinal.py` | 迁移、规则更新、保持和四阶段完整性测试 |
| `test_campaign_statistics.py` | 重复运行均值、样本标准差与 t 区间测试 |

旧版“发现、创造并复用工具”的四层评估已不再作为本章主实验；这类工具创造仍可作为持续进化闭环中的一个更新载体，但不能单独证明 Agent 能在长期运行中适应变化并避免遗忘。
