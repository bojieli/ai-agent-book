# 实验 8-19：特殊字符串的精确复述 SFT

代码编辑工具通常接收一段待替换的原文 `old_string`。假如文件中有一个换行，而模型输出了反斜杠和字母 `n`，工具就可能找不到这一段。该改训练数据，还是该改传递参数的程序？先跟着一条已有样本找出差异，再看监督微调（SFT）究竟改善了哪一步。

<a id="learning-0"></a>

## 先看一次失败：复制对了，为什么仍得零分？

从仓库根目录运行下面的命令。这里只读取两份随书保存的结果，装有 Python 3 就能完成。

```bash
cd chapter8/exact-copy-sft
python - <<'PY'
import json
from pathlib import Path

for model in ("base", "adapted"):
    report = json.loads(Path(f"validation/eval_{model}_eval.json").read_text(encoding="utf-8"))
    row = next(r for r in report["rows"] if r["id"] == "eval-000")
    actual, expected = map(json.loads, (row["prediction"], row["target"]))
    print(model, list(actual), actual["old_string"] == expected["old_string"], row["exact"])
PY
```

基座模型这一行会显示 `['path', 'old_string', 'other'] True 0`。原文在工具观察里和文件路径一起出现，任务只要求交回含有 `old_string` 的紧凑 JSON。基座把原文字段复制对了，却把另外两个字段也交了回来。加载适配器后，同一道题显示 `['old_string'] True 1`。这一次提高的是遵循输出格式的能力。评分器比较整段答案的 UTF-8 字节，实际编辑工具是否接受多余字段，还取决于它的参数协议。

<a id="learning-1"></a>

## 找到字符串第一次改变的位置

另一条样本 `eval-004` 更难用肉眼判断。打开微调后的留出集结果，这条记录中预测值和目标值都以形似 é 的字符结尾。沿用上面的实验目录，打印它们结尾的 UTF-8 编码：

```bash
python - <<'PY'
import json
from pathlib import Path

rows = json.loads(Path("validation/eval_adapted_eval.json").read_text(encoding="utf-8"))["rows"]
row = next(r for r in rows if r["id"] == "eval-004")
offset = row["first_diff_byte"]
for field in ("prediction", "target"):
    print(field, offset, row[field].encode("utf-8")[offset:].hex(" "))
PY
```

差异从偏移量 49 开始。预测以 `c3 a9` 结尾，这是一个预组合字符；目标以 `65 cc 81` 结尾，这是字母 e 加组合重音。查看分词器审计，Qwen3 的失败样本中也有 `eval-004`。这给出了可以验证的线索：取出数据行的 `source`，单独做一次编码再解码，逐字节比较往返前后的差异。这个步骤完全绕开了模型生成。[分词器审计记录](validation/tokenizer_audit.json)

面对真实工具故障，也可以这样逐段缩小范围。先比较文件原文与工具读取结果，再比较传给模型的内容、模型解码后的输出、解析后的 `old_string` 和工具最终收到的值。直接复述成功而工具匹配失败时，应先检查 Harness 的序列化、参数解析和工具的匹配规则。差异首次出现在模型生成处的样本，才适合拿来教模型精确复制。

<a id="learning-2"></a>

## 用三种任务训练，再在新字符串上评估

三种训练题分别要求直接复述 `source`（`verbatim`）、从等长的干扰项中复制标为 TARGET 的字符串（`decoy_copy`）、把原文装入指定 JSON（`tool_json`）。生成器组合不同长度、字符模式、10 种语言上下文及 8 种文章体裁；三个数据集使用不同随机种子，原始字符串互不重复。三组都使用相同的任务生成规则，因此边界集考察的是新字符串，不能据此推断对全新任务类型的效果。[分层人工抽查记录](validation/manual_audit.md)

有支持 bf16 的本地 CUDA GPU 时，可以继续复现训练。仓库根目录的 `uv sync --locked --extra train` 安装训练依赖；激活生成的虚拟环境后回到本实验目录。首次运行需要获取 Qwen3-8B 权重和分词器，分词审计还会获取另外两个模型的分词器。随书训练回执记录的设备是 NVIDIA RTX PRO 6000。[训练回执](validation/train_20260808T035121Z/training_receipt.json)

```bash
python generate_data.py
python tokenizer_audit.py
python evaluate.py --model Qwen/Qwen3-8B --label my_base --split eval
python train_sft.py --model Qwen/Qwen3-8B
python evaluate.py --model Qwen/Qwen3-8B --adapter output/adapter --label my_adapted --split eval
python evaluate.py --model Qwen/Qwen3-8B --adapter output/adapter --label my_adapted --split boundary
```

第一步重建 1,024 条训练样本、256 条留出样本和 256 条边界样本；第二步重写 `validation/tokenizer_audit.json`。先测基座，是为了让训练前后都回答同一批留出题。训练脚本使用 bf16、LoRA 适配器和 2 个 epoch，提示部分不计入损失，模型学习生成目标字符串或目标 JSON。新适配器写入 `output/adapter`。评估命令的标签会写入文件名，例如 `validation/eval_my_adapted_eval.json`，便于与随书结果并排比较。[数据文件校验值与运行清单](validation/manifest.json)

<a id="learning-3"></a>

## 读懂成绩：提升来自哪里？

| 模型与题集 | 整段答案字节一致 | 平均首次分歧位置（字节） |
|---|---:|---:|
| 基座，同一留出集 | 96 / 256（37.5%） | 29.0 |
| 加载适配器，同一留出集 | 202 / 256（78.9%） | 54.0 |
| 加载适配器，独立边界集 | 205 / 256（80.1%） | 54.2 |

首次分歧位置从零开始；整段相同的答案会计入答案的完整字节数，因此这个平均值也受正确答案的数量和长度影响。另一个评分细节是脚本先对模型解码结果调用 `.strip()`，再与目标比较，因此这里的分数不能用于判断模型是否原样保留了答案首尾的空白。[评分实现](evaluate.py) · [基座留出集](validation/eval_base_eval.json) · [微调留出集](validation/eval_adapted_eval.json) · [微调边界集](validation/eval_adapted_boundary.json)

把两份留出集成绩按题号配对，还能查到总分里看不见的退步。在实验目录运行：

```bash
python - <<'PY'
import json
from collections import Counter
from pathlib import Path

def answers(model):
    report = Path(f"validation/eval_{model}_eval.json")
    return {r["id"]: r for r in json.loads(report.read_text(encoding="utf-8"))["rows"]}

base, adapted = answers("base"), answers("adapted")
assert base.keys() == adapted.keys()
changes = Counter()
for sample, before in base.items():
    after = adapted[sample]
    assert before["target"] == after["target"]
    changes[before["exact"], after["exact"]] += 1
    if before["exact"] > after["exact"]:
        print(sample, repr(before["target"]), repr(after["prediction"]))
print(sorted(changes.items()))
PY
```

有 95 题两次都对，53 题两次都错，107 题由错变对，1 题由对变错。唯一退步的 `eval-095` 中，目标末尾是 `…Zq\nhZq`（这里用 `\n` 表示一个换行符），微调后的答案末尾却是 `…ZqhZq`。换行在字符串中间，因此评分脚本清理首尾空白的操作不会影响这道题。复测下一版模型时，可以把这道题与第一题一起保留，分别检查多行复制和 JSON 输出格式。

最后回到开头的两个案例。512 条留出和边界探针中，Qwen3 与 Qwen2.5 分词器的编码—解码往返率均为 80.1%，Mistral 为 100%。这里测的是 `source` 经过分词器后能否还原；表中的 80.1% 测的是模型在 256 道边界题上生成的整段答案。试着找一条模型答错的题，像检查 `eval-000` 那样先比字段，再像检查 `eval-004` 那样比字节。同一个零分，可能对应不同的修复方法。
