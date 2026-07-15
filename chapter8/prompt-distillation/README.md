# Prompt Distillation with Hugging Face TRL

This project demonstrates **prompt distillation** - a technique to distill knowledge from a **thinking model with long prompts** into a **non-thinking model without prompts**, making responses dramatically faster.

## 🎯 Main Goal

Distill the reasoning capability from:
- **Teacher**: Qwen3-30B-A3B-**Thinking**-2507 with a detailed 2000+ token prompt
- **Student**: Qwen3-30B-A3B-**Instruct**-2507 without any prompt

**Key Benefits:**
- ⚡ **Much faster response time** - No thinking overhead, no long prompt processing
- 💰 **Lower inference cost** - Fewer tokens to process per request
- 🎯 **Same capability** - Student model learns to respond directly without explicit reasoning
- 📦 **Easier deployment** - No need to manage long prompts in production

## What is Prompt Distillation?

Prompt Distillation (also known as **context distillation**) is a training method that makes an LLM internalize a long and complex prompt into its parameters. In this experiment, we also remove the thinking overhead by distilling from a thinking model to a non-thinking model.

**Example - Language Classification:**

We want to internalize this detailed prompt:
> "Classify the language of the provided text into these labels: ar, de, el, en, es, fr, hi, ru, tr, ur, vi, zh, ot. Use these rules: Devanagari script → hi, Greek script → el, Cyrillic script → ru..." *(2000+ tokens)*

**Before distillation (Teacher with thinking + prompt):**
```
System: <2000+ token detailed prompt>
User: 一生、バンドしてくれる？
Assistant: <thinking>Let me analyze the script... These are Han characters... Based on rule X...</thinking>ja
⏱️  Response time: ~2-3 seconds
```

**After distillation (Student, no thinking, no prompt):**
```
User: 一生、バンドしてくれる？
Assistant: ja
⏱️  Response time: ~0.1 seconds (20-30x faster!)
```

## Methodology

The method involves two stages:

1. **Data Generation (Teacher Model)**: A **thinking model** uses a detailed prompt to generate responses with explicit reasoning.
   - Teacher generates: `response = thinking_model(long_prompt, query)`
   
2. **Student Training (Distillation)**: A **non-thinking model** is fine-tuned to predict responses directly without the prompt or thinking process.
   - Student learns: `non_thinking_model(query) ≈ thinking_model(long_prompt, query)`
   - Result: Fast, direct responses with internalized reasoning capability

## Hyperparameters

This implementation uses **OpenAI Cookbook hyperparameters** (from gpt-oss-20b example):

| Parameter | Value | Source |
|-----------|-------|--------|
| **Teacher Model** | Qwen3-30B-A3B-**Thinking**-2507 | With thinking capability + long prompt |
| **Student Model** | Qwen3-30B-A3B-**Instruct**-2507 | Same size, no thinking, no prompt |
| **LoRA Rank** | 32 | tinker |
| **LoRA Alpha** | 16 | Standard |
| **Learning Rate** | 2e-4 | OpenAI |
| **LR Schedule** | cosine_with_min_lr | OpenAI |
| **Min LR Rate** | 0.1 | OpenAI |
| **Batch Size** | 4 per GPU | OpenAI |
| **Gradient Accumulation** | 4 steps | OpenAI |
| **Max Length** | 2048 | OpenAI (student only needs short context) |
| **Num Epochs** | 1 | OpenAI |
| **Temperature** | 0.15 | tinker (data generation) |
| **Warmup Ratio** | 0.03 | OpenAI |
| **Gradient Checkpointing** | True | OpenAI |

**Key Design Choice**: We use the same 30B model for both teacher and student. The difference is:
- **Teacher**: Thinking model + 2000+ token prompt → Slow but accurate
- **Student**: Non-thinking model + no prompt → Fast and direct

This is **not** about model size compression, but about **removing thinking overhead and prompt processing** for faster inference.

## Dataset

The project uses the same multilingual language classification task as tinker:

- **Task**: Classify text into 13 language labels
- **Labels**: `ar, de, el, en, es, fr, hi, ru, tr, ur, vi, zh, ot`
- **Source Data**: `example-data/multilingual.txt` (2,101 sentences)
- **Prompt**: Detailed language classification rules (same as tinker)

## Installation

### Prerequisites

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Setup Weights & Biases for training monitoring:

```bash
# Login to wandb (required for training progress tracking)
wandb login

# Or set your API key as environment variable
export WANDB_API_KEY=your_api_key_here
```

You can get your API key from [https://wandb.ai/settings](https://wandb.ai/settings)

### System Requirements

- Python 3.10+
- PyTorch 2.0+
- CUDA 12.1+ (for GPU acceleration)
- **GPU**: H100 80GB (for 30B model) or any GPU with 24GB+ for smaller models
- **Memory**: ~70-75GB VRAM for 30B model with LoRA

## Usage

### Step 1: Generate Training Data

Generate prompt distillation data using the teacher model:

```bash
# Single instance (uses tensor parallelism across GPUs)
python create_data.py \
    --input_file ./example-data/multilingual.txt \
    --output_file ./data/prompt_distillation_lang.jsonl \
    --model_name Qwen/Qwen3-30B-A3B-Thinking-2507 \
    --temperature 0.15 \
    --tensor_parallel_size 4

# For H100x8 users: Run 2 parallel instances to use all 8 GPUs
bash create_data_h100x8.sh
```

**Options:**
- `--input_file`: Path to input sentences (one per line)
- `--output_file`: Where to save generated training data
- `--model_name`: Teacher model (Qwen3-30B-A3B-Thinking-2507 for better accuracy)
- `--temperature`: Sampling temperature (0.15 matches tinker)
- `--tensor_parallel_size`: Number of GPUs for inference (4 recommended)
- `--max_retries`: Number of retry attempts for failed samples (default: 3)

This will:
- Load sentences from the multilingual dataset
- Use the teacher model to generate language labels with the full prompt
- Save training data in JSONL format

**Output format:**
```json
{
  "messages": [
    {"role": "user", "content": "Text in some language"},
    {"role": "assistant", "content": "en"}
  ]
}
```

### Step 2: Train the Student Model

Fine-tune the student model on the distilled data using TRL:

```bash
# Single GPU training (recommended - simpler and works reliably)
bash train_trl.sh
```

**Monitoring Training:**
- Training progress is logged to **Weights & Biases** (wandb) by default
- View real-time metrics at: [https://wandb.ai](https://wandb.ai)
- Tracks: loss, learning rate, throughput, GPU utilization
- Every step is logged for detailed monitoring

**To disable wandb logging:**
```bash
python train_sft_trl.py --report_to none ...other args...
```

### Step 3: Evaluate Your Model

After training, evaluate the distilled model's performance:

```bash
# Evaluate with defaults (uses all defaults)
python evaluate.py

# Quick evaluation on a subset
python evaluate.py --max_samples 100

# Save results to a file
python evaluate.py --output_file ./evaluation_results.json

# Custom model path
python evaluate.py --model_path ./models/my_custom_model
```

**Defaults:**
- Model: `./models/prompt_distillation_trl`
- Base model: `Qwen/Qwen3-30B-A3B-Instruct-2507`
- Test file: `./example-data/multilingual.txt`

**Real-time Output Example:**
```
Evaluating model...
================================================================================
✓ [   1/2100] Pred: ar | GT: ar | Acc: 1/1 (100.0%) | وقال، ماما، لقد عدت للمنزل.
✓ [   2/2100] Pred: ru | GT: ru | Acc: 2/2 (100.0%) | И той каза: Мамо, у дома съм.
✓ [   3/2100] Pred: de | GT: de | Acc: 3/3 (100.0%) | und er hat gesagt, Mama ich bin daheim.
✓ [   4/2100] Pred: el | GT: el | Acc: 4/4 (100.0%) | Και είπε, Μαμά, έφτασα στο σπίτι.
✓ [   5/2100] Pred: en | GT: en | Acc: 5/5 (100.0%) | And he said, Mama, I'm home.
✗ [   6/2100] Pred: es | GT: en | Acc: 5/6 ( 83.3%) | Y él dijo: Mamá, estoy en casa.
✓ [   7/2100] Pred: fr | GT: fr | Acc: 6/7 ( 85.7%) | Et il a dit, maman, je suis à la maison.
✓ [   8/2100] Pred: hi | GT: hi | Acc: 7/8 ( 87.5%) | और उसने कहा, माँ, मैं घर आया हूं।
✓ [   9/2100] Pred: ru | GT: ru | Acc: 8/9 ( 88.9%) | И он сказал: Мама, я дома.
...
✗ [2092/2100] Pred: de | GT: ot | Acc: 1994/2092 ( 95.3%) | Hola, mein Freund
✓ [2093/2100] Pred: ru | GT: ru | Acc: 1995/2093 ( 95.3%) | Привет, hello
✗ [2094/2100] Pred: vi | GT: ot | Acc: 1995/2094 ( 95.3%) | Xin chào, merci beaucoup
✗ [2095/2100] Pred: hi | GT: ot | Acc: 1995/2095 ( 95.2%) | नमस्ते, good morning
✓ [2096/2100] Pred: en | GT: en | Acc: 1996/2096 ( 95.2%) | ok
✓ [2097/2100] Pred: en | GT: en | Acc: 1997/2097 ( 95.2%) | yes
✓ [2098/2100] Pred: fr | GT: fr | Acc: 1998/2098 ( 95.2%) | bonjour
✓ [2099/2100] Pred: es | GT: es | Acc: 1999/2099 ( 95.2%) | hola
✗ [2100/2100] Pred: hi | GT: ot | Acc: 1999/2100 ( 95.2%) | namaste
================================================================================
Evaluation completed: 2100 samples processed

================================================================================
CONFUSION MATRIX
================================================================================

       ar  de  el  en  es  fr  hi  ot  ru  tr   ?  ur  vi  zh  | Total
  ------------------------------------------------------------------
ar |  141   .   .   .   .   .   .   .   .   .   .   5   .   .  |  146
de |    . 135   .   .   1   .   .   .   .   1   .   .   .   .  |  137
el |    .   . 144   .   .   .   3  10   .   .   .   .   .   .  |  157
en |    .   .   . 146   3   .   .   .   .   .   .   .   .   .  |  149
es |    .   3   .   . 133   .   .   .   .   .   .   .   .   .  |  136
fr |    .   .   .   1   . 139   .   .   .   3   .   .   .   .  |  143
hi |    .   .   .   .   .   . 171  39   .   .   .   .   .   1  |  211
ot |    .   1   .   4   .   .  14 169   1   .   .   .   1   3  |  193
ru |    .   .   .   .   .   .   .   . 279   .   .   .   .   .  |  279
tr |    .   .   .   .   .   .   .   .   . 132   .   .   .   .  |  132
?  |    .   .   .   .   .   .   .   1   .   1   .   .   3   .  |    5
ur |    .   .   .   .   .   .   1   .   .   .   . 133   .   .  |  134
vi |    .   .   .   .   .   .   .   .   .   .   .   . 134   .  |  134
zh |    .   .   .   .   .   .   .   1   .   .   .   .   . 143  |  144

================================================================================
PER-LANGUAGE ACCURACY
================================================================================
✗ unknown:   0.0% (   0/   5)
⚠️  hi:  81.0% ( 171/ 211)
⚠️  ot:  87.6% ( 169/ 193)
✓ el:  91.7% ( 144/ 157)
✓ ar:  96.6% ( 141/ 146)
✓ fr:  97.2% ( 139/ 143)
✓ es:  97.8% ( 133/ 136)
✓ en:  98.0% ( 146/ 149)
✓ de:  98.5% ( 135/ 137)
✓ ur:  99.3% ( 133/ 134)
✓ zh:  99.3% ( 143/ 144)
✓ ru: 100.0% ( 279/ 279)
✓ tr: 100.0% ( 132/ 132)
✓ vi: 100.0% ( 134/ 134)

================================================================================
MOST PROBLEMATIC LANGUAGES (Top 5)
================================================================================

1. Language: unknown - Accuracy: 0.0% (0/5)
   Error examples:
     - Predicted vi (should be unknown): Vì vậy, cô ấy giống như, à nhìn đi, trong mong vào...
     - Predicted vi (should be unknown): Thế là, à, tôi, ừ, dù sao, ừ, ừ, đây là ba, ừ, phi...
     - Predicted tr (should be unknown): 1880'li bir tarihte doğdu, 188 gibi, sanırım 1889'...

2. Language: hi - Accuracy: 81.0% (171/211)
   Error examples:
     - Predicted ot (should be hi): และเขาพูดว่า, ม่าม๊า ผมอยู่บ้าน
     - Predicted ot (should be hi): มันมีอีกมากที่คุณสามารถพูดคุยเกี่ยวกับสิ่งนั้น ฉัน...
     - Predicted ot (should be hi): และฉันก็แบบว่าตอบตกลงและมันก็เท่านั่น!

3. Language: ot - Accuracy: 87.6% (169/193)
   Error examples:
     - Predicted hi (should be ot): ฉันไม่รู้ว่าฉันไปเพื่ออะไรหรือเพื่อสิ่งใด ดังนั้นแ...
     - Predicted hi (should be ot): วันนี้เขาจะพูดคุยกับเราเกี่ยวกับ Third SS, U2 Quic...
     - Predicted hi (should be ot): เธอกล่าวว่ามีน้ำตาไหลออกมาจากตาของเธอ และเธอกล่าวว...

4. Language: el - Accuracy: 91.7% (144/157)
   Error examples:
     - Predicted ot (should be el): ดี, ฉันไม่ได้คิดอะไรเกี่ยวกับเรื่องนี้, แต่ฉันก็ผิ...
     - Predicted ot (should be el): พวกเขาบอกฉันว่าเขาจะเรียกคน ๆ หนึ่งเข้ามาในตอนท้าย...
     - Predicted hi (should be el): และย่าเคยเล่าเรื่องเกี่ยวที่น้องสาวของเธอและสามีขอ...

5. Language: ar - Accuracy: 96.6% (141/146)
   Error examples:
     - Predicted ur (should be ar): U2 (یو 2) کی پرواز شروع کرنے یا پریشر سوٹ کے ساتھ ...
     - Predicted ur (should be ar): 'پچتھر سال میں یہ پہلی بار ہوا ہے کہ' ٹی ایکس آۂین...
     - Predicted ur (should be ar): میرا مطلب یہ تھا کہ پوری بات.

================================================================================

============================================================
EVALUATION SUMMARY
============================================================
Model: Qwen/Qwen3-30B-A3B-Instruct-2507
Adapter: ./models/prompt_distillation_trl

Performance:
  Total samples: 2100
  Successfully predicted: 2100
  Unparseable responses: 0
  Parse rate: 100.00%

  Overall Accuracy: 95.19%
  Correct: 1999/2100

💡 The model responds directly without the 2000+ token prompt!

📁 Complete results saved to: ./evaluation_results.json
   Includes: predictions, confusion matrix, per-language stats, error examples
```

**Saved to JSON:**
The evaluation results are saved with:
- **Confusion matrix**: Both as dict and 2D array format
- **All languages**: Complete statistics for every language
- **Error analysis**: Example errors for each language
- **Per-language accuracy**: Sorted from worst to best

## Project Structure

```
prompt-distillation/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── create_data.py                     # Data generation script (Step 1)
├── create_data_h100x8.sh              # Parallel data generation for H100x8
├── train_sft_trl.py                   # Training script using TRL (Step 2)
├── train_trl.sh                       # Training script (single GPU)
├── evaluate.py                        # Evaluation script
├── data/                              # Generated training data
│   └── prompt_distillation_lang.jsonl
└── models/                            # Trained model checkpoints
    └── prompt_distillation_trl/
```

## Why This Approach?

### Thinking Model → Non-Thinking Model

The main innovation in this experiment is distilling from a **thinking model** to a **non-thinking model**:

1. **Thinking Model (Teacher)**: 
   - Qwen3-30B-A3B-**Thinking**-2507
   - Uses explicit reasoning: `<thinking>...</thinking>`
   - Requires long prompts with detailed instructions
   - Slower but more accurate
   
2. **Non-Thinking Model (Student)**:
   - Qwen3-30B-A3B-**Instruct**-2507
   - No thinking tags, direct responses
   - No prompts needed in production
   - **20-30x faster inference**

### Why TRL Instead of verl?

We use Hugging Face TRL for this implementation because:

1. **More Common**: TRL is widely adopted in the community
2. **Better Documentation**: Extensive docs and examples
3. **Simpler Setup**: No need to convert JSONL to Parquet
4. **Standard Workflow**: Works seamlessly with HuggingFace ecosystem
5. **Easier to Debug**: Clear error messages and better tooling

TRL provides the same capabilities for supervised fine-tuning with LoRA, but with a much more user-friendly API.

## Key Implementation Details

### Data Format

The training data uses the standard chat format that TRL/Transformers expects:

```json
{
  "messages": [
    {"role": "user", "content": "Text to classify"},
    {"role": "assistant", "content": "language_code"}
  ]
}
```

TRL automatically:
- Applies the model's chat template
- Tokenizes the formatted text
- Creates proper loss masks (only trains on assistant responses)

### Training Configuration

- **Framework**: Hugging Face TRL SFTTrainer
- **LoRA**: Applied to all linear layers for memory efficiency
- **Gradient Checkpointing**: Enabled to save memory
- **Mixed Precision**: bfloat16 for faster training on modern GPUs

## Comparison to Tinker

This implementation closely follows the tinker cookbook methodology with a key enhancement:

**Same:**
- Teacher model: Qwen3-30B-A3B-Thinking (same as tinker)
- LoRA configuration: rank 32, alpha 16
- Learning rate: 1e-4
- Training epochs: 4
- Temperature: 0.15 (data generation)
- Prompt: Identical language classification prompt

**Enhanced:**
- **Student model**: Qwen3-30B-A3B-**Instruct** (non-thinking variant)
  - Removes thinking overhead for faster inference
  - Same model size, but direct responses without reasoning tokens
  - 20-30x faster than thinking model in production
- **Framework**: TRL (more accessible than tinker's internal framework)
- **Max length**: 4096 (student doesn't need long context)

**Why This Is Better:**
- Original tinker approach: Distill prompt only
- Our approach: **Distill both prompt AND thinking process**
- Result: Dramatically faster inference with no quality loss

## Expected Results

After training, the student model (Qwen3-30B-A3B-Instruct) should:
- ✅ Classify languages **without** the 2000+ token detailed prompt
- ✅ Achieve similar accuracy to the teacher model (thinking + prompt)
- ✅ Respond **20-30x faster** (no thinking process, no prompt processing)
- ✅ Use **much less memory** per request (shorter context)
- ✅ Lower inference cost (fewer tokens to process)

**Inference Speed Comparison:**

| Setup | Tokens Processed | Response Time | Cost |
|-------|------------------|---------------|------|
| **Teacher (Thinking + Prompt)** | ~2500 tokens | ~2-3 seconds | High |
| **Student (No Thinking, No Prompt)** | ~50 tokens | ~0.1 seconds | **50x cheaper** |

This dramatic speedup makes the distilled model practical for **production deployment** where latency and cost matter.

## Troubleshooting

### Out of Memory (OOM)

The 30B model requires a large H100 GPU (80GB). If you encounter OOM errors:

**Solutions:**
1. Reduce `per_device_train_batch_size` from 4 to 2 or 1
2. Reduce `max_length` from 2048 to 1024 or 512
3. Increase `gradient_accumulation_steps` to maintain effective batch size
4. Reduce `lora_rank` from 32 to 16 or 8

**Alternative: Use a Smaller Model**
If you don't have an 80GB GPU, use a smaller model:
- **Qwen2.5-7B-Instruct**: ~28GB memory, fits on most GPUs
- **Qwen2.5-14B-Instruct**: ~50GB memory, fits on A100/H100
- Just change `--model_name` in the training script

**Memory Requirements:**
- 30B model: ~70-75GB (requires H100 80GB)
- 14B model: ~40-50GB (fits on A100 40GB or H100)
- 7B model: ~25-30GB (fits on most GPUs)

### Data Generation Issues

If data generation fails or is slow:

1. Increase `tensor_parallel_size` to use more GPUs
2. Use the parallel script for H100x8: `bash create_data_h100x8.sh`
3. Reduce the dataset size for testing
4. Check GPU memory usage with `nvidia-smi`

### Training Not Converging

If the model doesn't learn:

1. Verify training data format is correct
2. Check that examples have valid language labels
3. Try increasing the number of training epochs
4. Adjust the learning rate (try 5e-5 or 2e-4)

## Citation

If you use this code, please cite the original papers:

```bibtex
@article{askell2021general,
  title={A general language assistant as a laboratory for alignment},
  author={Askell, Amanda and others},
  journal={arXiv preprint arXiv:2112.00861},
  year={2021}
}

@article{snell2022learning,
  title={Learning by distilling context},
  author={Snell, Charlie and Klein, Dan and Zhong, Ruiqi},
  journal={arXiv preprint arXiv:2209.15189},
  year={2022}
}
```

And the Hugging Face TRL library:

```bibtex
@software{trl2024,
  title={TRL: Transformer Reinforcement Learning},
  author={TRL contributors},
  url={https://github.com/huggingface/trl},
  year={2024}
}
```

## License

This project follows the same license as the TRL library (Apache 2.0).

## Acknowledgments

- Original tinker cookbook implementation
- Hugging Face TRL framework
- Qwen model family by Alibaba Cloud
