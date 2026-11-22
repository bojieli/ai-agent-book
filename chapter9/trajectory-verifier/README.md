# 实验 9-1：客服 Agent 的三层轨迹验证器

用户满意度或一个总分，很难告诉我们 Agent 应该改哪一步。本实验把客服轨迹拆成结果、过程与表达三个层次，学习如何给改进提供可定位的证据。

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

结果层核对环境最终状态，过程层检查规则和承诺是否与动作一致，质量层评价较开放的表达与变通。不同层需要不同验证方式，不能全部交给一个模糊评分。

本实验对应正文的“从运行轨迹中获得学习信号”。它不把用户满意度或一个总分当作学习信号，而是依次核对环境结果、执行过程与语言质量，并在每个失败维度中保留证据轮次。

`verifier.py` 实现三层结构：结果层读取最终订单状态；过程层检查业务规则、隐私、事实依据和承诺—行动一致性；质量层按“表达质量、合规变通”Rubric 评价开放性指标。示例默认使用确定性的 `HeuristicQualityJudge`，所以不需要 API Key；项目也提供遵循同一 `QualityJudge` 接口的真实 LLM 实现，下两层仍坚持使用环境真值和程序规则。

`sample_trajectories.json` 包含正常退款、虚假承诺、违规泄露和过度拒绝四类轨迹，并带有专家标签。`calibration.py` 按维度报告违规识别的精确率、召回率与标签一致率。`demo.py` 还对比了只有一个总分的输出与带证据的多维诊断。

### 代码阅读顺序

- **Run first:** python demo.py (deterministic HeuristicQualityJudge, no API key).
- **Start here:** verifier.py composes the result, process and quality layers.
- **Core behavior:** customer_service_env.py::run_case supplies environment truth; calibration.py compares dimensions with expert labels.
- **State / protocol:** sample_trajectories.json, structured verdict schema and evidence turns.
- **Verifier:** test_verifier.py plus calibration precision/recall; LLM quality judging never replaces the first two code gates.
- **Experiment variable:** single scalar score versus dimensioned verdict with evidence/confidence.
- **Skip on first pass:** provider client and demo formatting.

<a id="learning-1"></a>

## 准备环境与输入

先从本地示例开始。依赖安装可能需要联网，但下面标明的离线路径不需要模型 API Key。若随后切换到真实模型，请再完成相应的服务配置。

<a id="learning-2"></a>

## 按照步骤完成实验

先运行本地演示，对照正常退款、虚假承诺和过度拒绝等样例。找到每个问题对应的轨迹轮次，再阅读验证器怎样得出判断。理解后才把启发式质量评分替换为真实模型裁判。

### 运行离线示例与真实模型

运行方法：

```bash
python demo.py
python -m unittest -v test_verifier.py
```

以上是确定性校准路径。若要真实调用 LLM 评价表达质量与合规变通：

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

cd chapter9/trajectory-verifier

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
export OPENAI_API_KEY=your_api_key_here
python demo.py --judge llm --model gpt-5.6
```

真实模式使用 OpenAI Responses API，并要求模型按相同 schema 返回逐维结论、证据轮次和置信度；环境结果与过程规则两层仍由代码判断。该命令会产生真实 API 费用，输出可能随模型版本变化，应继续用专家标签检查每个维度，而不能只观察总分。

真实系统应扩大专家校准集，并把低置信度或高风险轨迹交给第二个验证器或人工复核。样例中的 `quality_facts` 是离线实验对 LLM 判读结果的显式表示，并不意味着生产系统可以预先获得这些字段。

<a id="learning-3"></a>

## 分析结果与形成判断

默认演示的质量层采用确定性方法，只用于解释结构。检查时既要看问题被识别出来，也要看正常行为是否被误判，并用专家标签校准。

### 检查自己的解释

Agent 说“退款已完成”，但实际只查询了订单，这个问题应该在哪一层被发现？
