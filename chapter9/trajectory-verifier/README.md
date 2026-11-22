# 实验 9-1：客服 Agent 的三层轨迹验证器

客服在第 2 轮对用户说：“已经为您完成退款。”打开[离线样例](sample_trajectories.json)，找到 `cs-false-promise`。订单仍是 `confirmed`，工具调用列表也是空的。只读客服最后一句、只查订单状态、把对话与调用记录放在一起看，这三种读法各能回答什么问题？

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

先问钱退了没有。结果层核对环境里的订单状态和金额；正常退款样例中，预期与实测都是已退款 480。再问客服当时凭什么说已经退了。过程层沿时间顺序查找工具回执，还要核对业务规则、隐私边界，以及客服承诺的动作是否执行过。最后才评措辞：答复是否说清楚了结果，原方案办不成时，有没有提出合规的替代办法？

三层共用[验证器入口](verifier.py)。结果和过程由程序核验；表达与变通按评分标准评价。默认示例使用确定性的 `HeuristicQualityJudge`，离线就能对照每项结论与依据。要尝试真实模型评审，可以替换实现同一个 `QualityJudge` 接口的质量评判器。

`sample_trajectories.json` 包含正常退款、虚假承诺、违规泄露和过度拒绝四类轨迹，并带有专家标签。`calibration.py` 按维度报告违规识别的精确率、召回率与标签一致率。`demo.py` 还对比了只有一个总分的输出与带证据的多维诊断。

退款与改签的事实依据必须来自陈述之前的成功工具调用；陈述中的数字金额、沙盒订单号和 ISO 日期还需与该调用的参数/结果一致。同名工具成功不能为错误金额提供依据。缺少值或无法解析值时返回 `uncertain`，明确失配返回 `fail`；这两种情况都进入人工复核，不作为自动学习信号。解析范围限于本实验的金额、订单和日期格式，复杂自然语言仍需人工复核。

### 代码阅读顺序

在本目录运行 `python demo.py`。输出里有两条轨迹都得了 0.571，先记下它们的编号。接着打开 [verifier.py](verifier.py) 看每条轨迹在哪些维度失分，再用 [calibration.py](calibration.py) 对照专家标签。四条样例对应同一套判定格式；想改进其中一层，可以重跑样例，检查其他层的结论是否也发生变化。

<a id="learning-1"></a>

## 准备环境与输入

先运行 `python demo.py`，找一条出现退款承诺的对话，再对照工具记录检查款项状态。核对事实后才评价措辞，这样可以分清任务结果与沟通质量。

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

为什么两条轨迹都是 0.571？七个维度里，它们都通过了四项。看 `cs-false-promise`，订单本该退款却仍有效，助手也拿不出支持“已退款”的工具回执。看 `cs-policy-and-privacy`，订单本该保持有效却被退了款，而且发生了规则违规和隐私泄露。一次少做了，一次做过了。两者都要复核，应该改的环节却不同。

可以在本目录用 Python 标准库把结论追到原始证据：

```bash
python3 - <<'PYTHON'
import json
from pathlib import Path
from verifier import TrajectoryVerifier

cases = json.loads(Path("sample_trajectories.json").read_text(encoding="utf-8"))
verifier = TrajectoryVerifier()
for case in cases:
    if case["id"] in ("cs-false-promise", "cs-policy-and-privacy"):
        report = verifier.evaluate(case)
        print(case["id"], case["expected_outcome"], case["final_state"])
        for item in report["dimensions"]:
            if item["verdict"] == "fail":
                print(item["dimension"], item["evidence"])
PYTHON
```

结果层的依据可以直接是一对期望值与实测值。检查虚假承诺时，还要回到客服说这句话的那一轮，核对当时已有的调用记录。四条样例上的校准只说明程序在这些例子里与专家判断是否一致。

### 检查自己的解释

Agent 说“退款已完成”，但实际只查询了订单，这个问题应该在哪一层被发现？
