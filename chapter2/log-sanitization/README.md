# Log Sanitization / 日志脱敏

本实验演示如何从 Agent 的日志与工具输出中检测并脱敏敏感信息。它提供**两种互补的脱敏引擎**：

1. **离线规则引擎（regex，默认）** —— 纯正则表达式 + 校验算法（Luhn、身份证校验码），
   **无需 Ollama、无需网络、无需外部框架**，结果确定、速度快，适合作为日志落盘前的第一道防线。
   它同时覆盖 Agent 场景中最常泄露的**密钥类**敏感信息（API Key、云厂商令牌、私钥、连接串口令）
   与传统 **PII**（身份证、手机号、信用卡、邮箱等）。
2. **本地 LLM 引擎（llm）** —— 通过 Ollama 调用一个本地小模型（默认 `qwen3:0.6b`）语义识别
   Level 3 PII。呼应本章“小模型也能胜任结构化任务”的论点，同时也暴露小模型的局限
   （例如可能返回带描述前缀的值而非原始字符串，导致回填失败）。

> 想快速看效果，直接运行 `python main.py --demo`（离线，无需任何依赖）即可看到多个代表性样本的
> before/after 对比与脱敏类别汇总。

## 离线规则引擎覆盖的敏感信息类别

`regex_sanitizer.py` 按优先级处理以下类别（重叠时高优先级规则胜出），每类替换为带标签的占位符：

| 类别 | 占位符 | 说明 |
| --- | --- | --- |
| 私钥 / 证书 | `[REDACTED_PRIVATE_KEY]` | PEM 私钥块 |
| JWT | `[REDACTED_JWT]` | `eyJ...` 三段式令牌 |
| 连接串凭据 | `[REDACTED_URL_CRED]` | `scheme://user:PASSWORD@host` |
| AWS 访问密钥 | `[REDACTED_AWS_KEY]` | `AKIA...` |
| GitHub / Slack / Google / OpenAI 密钥 | `[REDACTED_*_TOKEN]` / `[REDACTED_API_KEY]` | `ghp_`、`xoxb-`、`AIza`、`sk-` |
| Bearer 令牌 | `[REDACTED_BEARER_TOKEN]` | `Authorization: Bearer ...` |
| 口令 / 密钥赋值 | `[REDACTED_SECRET]` | `password=...`、`token: ...` 等 |
| 邮箱 | `[REDACTED_EMAIL]` | |
| 信用卡号 | `[REDACTED_CREDIT_CARD]` | 通过 Luhn 校验，降低误报 |
| IBAN | `[REDACTED_IBAN]` | 国际银行账号 |
| 美国社保号 | `[REDACTED_SSN]` | |
| 身份证号 | `[REDACTED_ID_CARD]` | 中国大陆 18 位，含校验码验证 |
| 手机号 | `[REDACTED_PHONE]` | 中国大陆 |
| IP 地址 | `[REDACTED_IP]` | IPv4 |

## Level 3 PII Categories（LLM 引擎）

Based on the privacy protection architecture, Level 3 PII includes highly sensitive information:
- Social Security Numbers (SSN)
- Credit Card Numbers
- Bank Account Numbers
- Medical Record Numbers
- Medical Diagnoses and Treatment Information
- Prescription Information
- Driver's License Numbers
- Passport Numbers
- Financial PINs
- Tax ID Numbers
- Health Insurance IDs
- Biometric Data

## Features

- **Offline Rule Engine**: Regex + Luhn/ID-checksum based sanitizer that needs no model, no network, and covers API keys/secrets in addition to PII
- **Local LLM Processing**: Uses Ollama with a local small model (default `qwen3:0.6b`) for privacy-preserving PII detection
- **Internal Reasoning**: Shows the model's thinking process using `<think>` tags for transparency
- **Streaming Output**: Real-time display of thinking and PII detection progress
- **Performance Metrics**: Measures TTFT (Time to First Token), token counts, and processing speeds
- **Batch Processing**: Can process multiple test cases from user-memory-evaluation framework
- **Detailed Metrics**: Tracks prefill time, output time, tokens per second for both phases

## Installation

### 1. Install Ollama

> **通用回退（OpenRouter）**：本实验默认用本地 Ollama 小模型。若 Ollama 不可用
> （未运行 / 不可达）且设置了 `OPENROUTER_API_KEY`，Agent 会自动改走 OpenRouter
> （默认托管模型 `openai/gpt-5.6-luna`）。想强制走回退做验证，可把 Ollama 指到一个
> 不可达端口：`export OLLAMA_HOST=http://127.0.0.1:1`。

#### macOS:
```bash
brew install ollama
ollama serve  # Run in separate terminal
```

#### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl start ollama
```

#### Windows:
Download from [ollama.com](https://ollama.com/download/windows)

> 说明：以下 Ollama 相关步骤仅在使用 `--mode llm`（本地 LLM 引擎）或运行 LLM 批量评测路径时才需要。
> 离线规则引擎（`--demo`、`--input`）只依赖 Python 标准库，无需安装 Ollama。

### 2. Pull the Qwen3 Model
```bash
ollama pull qwen3:0.6b
```

Note: The 0.6B model requires approximately 500MB of disk space（可按需换用 `qwen3:1.7b`、`qwen3:4b` 提升准确率）。

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Usage

完整参数说明见 `python main.py --help`（中文）。

### 离线规则演示（推荐，无需 Ollama）
对多个内置代表性样本展示 before/after 与脱敏类别汇总：
```bash
python main.py --demo
```

### 脱敏任意日志文件（离线）
```bash
python main.py --input app.log                 # 结果写到 app.log.sanitized
python main.py --input app.log -o cleaned.log  # 指定输出文件
```

也可以直接运行规则引擎模块，仅对内置样本做演示：
```bash
python regex_sanitizer.py
```

### 使用本地 LLM 引擎
上述演示 / 文件脱敏加 `--mode llm` 即改用本地 Ollama 模型：
```bash
python main.py --demo --mode llm
python main.py --input app.log --mode llm --model qwen3:1.7b
```

### Process All Layer 3 Test Cases（LLM 批量评测路径）
Process all complex test cases from user-memory-evaluation（该路径固定使用 LLM，需要 Ollama 与 chapter3 评测框架）：
```bash
python main.py
```

### Process Specific Test Case
```bash
python main.py --test-id layer3_13_emergency_medical_cascade
```

### Limit Number of Test Cases
Process only the first N test cases:
```bash
python main.py --limit 3
```

### 选择模型
```bash
python main.py --demo --mode llm --model qwen3:4b   # 默认 qwen3:0.6b
```

## Output Structure

The sanitized logs and metrics are saved in the `output/` directory:

```
output/
├── <test_id>_sanitized.txt    # Sanitized conversation text
├── <test_id>_summary.json     # Summary of PII found and replaced
├── performance_metrics.json   # Detailed performance metrics
└── performance_summary.json   # Aggregated performance statistics
```

## Performance Metrics

The system tracks the following metrics for each conversation:

### Timing Metrics
- **Prefill Time (TTFT)**: Time to first token in milliseconds
- **Output Time**: Time to generate all output tokens
- **Total Time**: End-to-end processing time

### Token Metrics
- **Input Tokens**: Number of tokens in the prompt
- **Output Tokens**: Number of tokens generated
- **Prefill Speed**: Tokens per second during prefill phase
- **Output Speed**: Tokens per second during generation

### Sanitization Metrics
- **PII Items Found**: Number of Level 3 PII values detected
- **Replacements Made**: Number of replacements with [REDACTED]

## Example Output

```
🚀 Starting Log Sanitization with Local LLM
============================================================
📦 Loading test cases from user-memory-evaluation...
🤖 Initializing Ollama agent...
✅ Using model: qwen3:0.6b

[1/1] Test Case: layer3_13_emergency_medical_cascade
   Title: Emergency Medical Crisis - Multi-System Coordination Response
   Conversations: 8

🔍 Processing conversation: emergency_room_001
   Found 3 PII items
   - 123-45-6789
   - 4532 1234 5678 9012
   - MRN-789456

============================================================
PERFORMANCE SUMMARY
============================================================

📊 Total Conversations Processed: 8

⏱️  Timing Metrics (milliseconds):
   Prefill (TTFT): 125.34 ms (median: 118.50)
   Output Time:    234.67 ms (median: 220.00)
   Total Time:     360.01 ms (median: 338.50)

📝 Token Metrics:
   Average Input Tokens:  450.5
   Average Output Tokens: 25.3
   Total Tokens Processed: 4206

⚡ Speed Metrics (tokens/second):
   Prefill Speed: 3592.8 tok/s
   Output Speed:  107.8 tok/s

🔒 Sanitization Results:
   Total PII Items Found:     24
   Total Replacements Made:   48
   Average PII per Conversation: 3.0
```

## Architecture

The project consists of several modules:

1. **regex_sanitizer.py**: Offline rule-based sanitizer (regex + Luhn/ID checksums), covers keys/secrets and PII
2. **samples.py**: Representative agent-log samples used by the offline demo
3. **config.py**: Configuration for Ollama model and PII categories
4. **test_loader.py**: Loads test cases from user-memory-evaluation framework
5. **agent.py**: Core LLM sanitization logic using Ollama
6. **metrics.py**: Performance metrics collection and reporting
7. **main.py**: Main entry point and orchestration

## How It Works

1. **Test Case Loading**: The system loads conversation histories from the user-memory-evaluation framework
2. **PII Detection**: Each conversation is sent to the local Qwen3 0.6B model with a specialized prompt to detect Level 3 PII
3. **Sanitization**: Detected PII values are replaced with [REDACTED] in the original text
4. **Metrics Collection**: Performance metrics are collected for each operation
5. **Output Generation**: Sanitized logs and performance summaries are saved to the output directory

## Privacy Considerations

- All processing happens locally using Ollama - no data is sent to external APIs
- The Qwen3 0.6B model runs entirely on your local machine
- Sanitized logs replace sensitive information with [REDACTED] placeholders
- Original PII values are logged for verification but should be handled securely

## Troubleshooting

### "Ollama not found"
Make sure Ollama is installed and running:
```bash
ollama serve
```

### "Model qwen3:0.6b not found"
Pull the model:
```bash
ollama pull qwen3:0.6b
```

### "Evaluation framework not found"
Ensure the user-memory-evaluation project exists at:
```
../user-memory-evaluation/
```
