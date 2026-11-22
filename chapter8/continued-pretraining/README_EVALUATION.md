# 在相同提示下比较持续预训练与指令微调

持续预训练改变模型对领域文本的适应，指令微调进一步改变它对任务要求的响应。这里使用固定提示比较检查点，学习分别观察语言流畅性、事实内容和指令遵循。少量示例用于理解行为，不是完整能力榜单。

## 确认比较的模型与数据

先完成[训练教程](README.md)，检查 `lora_model_pretrained` 与 `lora_model` 中实际保存的模型。默认评估 `lora_model`，`--pretrained` 则固定选择前一个目录；若使用自定义 `--model_path`，不要同时加 `--pretrained`，否则后者会覆盖路径选择。

评估需要可加载模型的 CUDA 环境。两次运行采用相同提示、上下文长度和输出长度，并记录模型、适配器与量化条件。训练材料与用于判断迁移的评估样本应分离。

## 先做确定性的逐项比较

从本实验目录执行：

```bash
python evaluate_model.py --model_path lora_model_pretrained --max_new_tokens 150
python evaluate_model.py --model_path lora_model --max_new_tokens 150
```

脚本包括韩语、英语的百科式和指令式提示。百科式提示先看主题能否自然延续、事实是否有依据；指令式提示先看是否执行了要求，再看答案内容。保留所有提示的输出，不只展示最流畅的一条。

## 再观察采样带来的变化

```bash
python evaluate_model.py --model_path lora_model --use_sampling --temperature 0.7 --top_p 0.9
```

`--use_sampling` 开启随机采样，`--temperature` 与 `--top_p` 仅在这种模式中使用。重复生成可以观察变化范围；不要把两次不同采样的差异全部归因于训练阶段。

| 参数 | 当前脚本的含义 |
| --- | --- |
| `--model_path` | 自定义模型目录，默认 `lora_model`。 |
| `--pretrained` | 选择 `lora_model_pretrained`。 |
| `--max_seq_length` | 加载的最大序列长度，默认 2048。 |
| `--max_new_tokens` | 生成长度上限，默认 150。 |
| `--load_in_4bit` | 当前实现默认开启，且使用 `store_true`。 |
| `--use_sampling` | 使用采样，默认不启用。 |
| `--temperature` / `--top_p` | 采样参数，默认 0.7 / 0.9。 |

当前 CLI 没有关闭 4-bit 加载的布尔开关：下方早期英文示例中的 `--load_in_4bit False` 与 `store_true` 解析方式不匹配，不应直接照抄。需要全精度对照时，应先调整该参数接口或在代码中明确传入加载设置，再记录改变后的条件。

## 解读输出并排查问题

颜色与流式显示帮助区分提示和输出，本身不属于评价指标。可以按原文的手工评价维度逐项记录语言、相关性、完整性与事实依据，再增加独立样本。韩语表达变好而英语或指令遵循变差时，应同时记录，不能只保留正向结果。

路径不存在时先核对训练是否保存了目标目录。显存不足时检查量化、序列长度和生成上限；输出过短时既要检查长度限制，也要检查模型是否提前生成结束符。更高温度只改变采样分布，不保证更有创造力或更准确。

下面完整保留了原始选项、六组测试说明、逐项比较与输出示例、排错路径和性能记录，便于结合源代码继续学习。

## English

# Korean Mistral Model Evaluation Guide

This guide explains how to use the evaluation script to test your trained Korean Mistral models.

## Overview

After running `continued-pretrain.py`, you'll have two saved models:
- `lora_model_pretrained/` - Model after Korean pretraining (before instruction finetuning)
- `lora_model/` - Final model after instruction finetuning

## Quick Start

### Basic Evaluation (Final Finetuned Model)

```bash
python evaluate_model.py
```

This will:
- Load the final finetuned model from `lora_model/`
- Run 6 test cases (Korean + English, Wikipedia + Instructions)
- Use default parameters (max_new_tokens=150)

### Evaluate Pretrained Model (Before SFT)

```bash
python evaluate_model.py --pretrained
```

This loads the model after Korean pretraining but before instruction finetuning.

## Command Line Options

### Model Selection

```bash
# Evaluate the pretrained model
python evaluate_model.py --pretrained

# Evaluate a custom model path
python evaluate_model.py --model_path path/to/your/model

# Load in full precision (more memory, higher quality)
python evaluate_model.py --load_in_4bit False
```

### Generation Parameters

```bash
# Generate more tokens
python evaluate_model.py --max_new_tokens 300

# Use sampling for more creative outputs
python evaluate_model.py --use_sampling --temperature 0.8 --top_p 0.95
```

### All Available Options

| Option | Default | Description |
|--------|---------|-------------|
| `--model_path` | `lora_model` | Path to saved LoRA model |
| `--pretrained` | `False` | Load pretrained model (before SFT) |
| `--max_seq_length` | `2048` | Maximum sequence length |
| `--load_in_4bit` | `True` | Use 4-bit quantization |
| `--max_new_tokens` | `150` | Maximum tokens to generate |
| `--use_sampling` | `False` | Enable sampling (vs greedy) |
| `--temperature` | `0.7` | Sampling temperature (creativity) |
| `--top_p` | `0.9` | Top-p nucleus sampling |

## Example Use Cases

### Compare Models Side-by-Side

```bash
# First, test the pretrained model
python evaluate_model.py --pretrained > results_pretrained.txt

# Then, test the finetuned model
python evaluate_model.py > results_finetuned.txt

# Compare the outputs
diff results_pretrained.txt results_finetuned.txt
```

### Creative vs Deterministic Generation

```bash
# Deterministic (greedy decoding) - same output every time
python evaluate_model.py

# Creative (sampling) - different output each time
python evaluate_model.py --use_sampling --temperature 0.7

# Very creative (higher temperature)
python evaluate_model.py --use_sampling --temperature 1.0

# More focused (lower temperature)
python evaluate_model.py --use_sampling --temperature 0.3
```

### Long-Form Generation

```bash
# Generate longer responses
python evaluate_model.py --max_new_tokens 500
```

## Test Cases

### Evaluation Script (evaluate_model.py)
Runs 6 test cases on a single model:

1. **Korean Wikipedia Article (Artificial Intelligence)** - Tests encyclopedic writing in Korean
2. **English Wikipedia Article (Artificial Intelligence)** - Ensures English preservation
3. **Korean Instruction (Explain Kimchi)** - Tests instruction-following for cultural topics
4. **English Instruction (Explain Thanksgiving Turkey)** - Tests English instruction-following
5. **Korean Instruction (Introduce Seoul)** - Tests factual knowledge in Korean
6. **Korean Instruction (Explain K-pop)** - Tests modern cultural knowledge

### Comparison Script (compare_models.py)
Runs 5 test cases across 3 models (15 total outputs):

1. **Korean Wikipedia - AI** - Shows Korean capability progression
2. **English Wikipedia - AI** - Validates English preservation (encyclopedic writing)
3. **Korean Instruction - Kimchi** - Shows instruction-following improvement
4. **Korean Instruction - Seoul** - Tests factual accuracy improvement
5. **English Instruction - Thanksgiving** - Validates English preservation (instruction-following)

The comparison script includes both English Wikipedia AND English Instruction tests to comprehensively validate that English capabilities remain strong throughout all training stages.

## Understanding the Output

### Color Coding
- 🔵 **Blue**: Loading and setup information
- 🟡 **Yellow**: Parameters and configuration
- 🟢 **Green**: Successful operations and output
- 🔴 **Red**: Errors
- 🔵 **Cyan**: Prompts and tips

### Evaluation Metrics (Manual)

When evaluating outputs, consider:

1. **Fluency**: Is the Korean grammatically correct?
2. **Factual Accuracy**: Are the facts correct?
3. **Instruction Following**: Does it answer the question?
4. **Coherence**: Does it make logical sense?
5. **Cultural Appropriateness**: Is cultural information accurate?

## Troubleshooting

### "Model path does not exist"
Make sure you've run `continued-pretrain.py` first to train and save the models.

### Out of Memory
Try:
```bash
# Use 4-bit quantization
python evaluate_model.py --load_in_4bit

# Reduce max sequence length
python evaluate_model.py --max_seq_length 1024

# Generate fewer tokens
python evaluate_model.py --max_new_tokens 100
```

### Outputs Too Short
Increase max tokens:
```bash
python evaluate_model.py --max_new_tokens 300
```

### Want Different Outputs Each Time
Enable sampling:
```bash
python evaluate_model.py --use_sampling
```

## Tips for Best Results

1. **Start with defaults**: Run with no arguments first
2. **Compare stages**: Test both `--pretrained` and final model
3. **Use sampling for variety**: Add `--use_sampling` for creative outputs
4. **Monitor GPU memory**: Check the memory stats in output

## Expected Performance

### Baseline Model (No Training)
- ❌ Korean: Poor, repetitive, often nonsensical
- ✅ English: Good, coherent, accurate

### Pretrained Model (After Korean Training)
- ⚠️ Korean: Improved fluency, better vocabulary
- ✅ English: Maintained quality
- ⚠️ Instructions: Better than baseline, but not perfect

### Finetuned Model (After SFT)
- ✅ Korean: Fluent, accurate, follows instructions
- ✅ English: Maintained quality
- ✅ Instructions: Good instruction-following in both languages

## Advanced Usage

### Batch Testing Multiple Configurations

Create a shell script:

```bash
#!/bin/bash
# test_configs.sh

echo "Testing different temperatures..."

for temp in 0.3 0.7 1.0; do
    echo "=== Testing temperature=$temp ==="
    python evaluate_model.py --use_sampling --temperature $temp \
        --max_new_tokens 150 > results_temp_${temp}.txt
done

echo "Testing different token lengths..."

for tokens in 100 200 300; do
    echo "=== Testing max_new_tokens=$tokens ==="
    python evaluate_model.py --max_new_tokens $tokens \
        > results_tokens_${tokens}.txt
done
```

### Custom Test Prompts

Modify the `run_evaluation()` function in `evaluate_model.py` to add your own test cases.

## References

- Main training script: `continued-pretrain.py`
- Unsloth documentation: https://docs.unsloth.ai
- Generation parameters: https://huggingface.co/docs/transformers/main_classes/text_generation

## Support

If you encounter issues:
1. Check that training completed successfully
2. Verify model files exist in `lora_model/` or `lora_model_pretrained/`
3. Ensure you have sufficient GPU memory
4. Try reducing `--max_seq_length` or `--max_new_tokens`

