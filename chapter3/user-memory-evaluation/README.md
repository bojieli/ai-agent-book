# User Memory Evaluation Framework

A comprehensive evaluation framework for testing AI agents' memory capabilities across three progressive levels of complexity. This framework uses realistic business conversation scenarios to assess whether agents can effectively store, retrieve, and utilize information from user interactions.

## Overview

The framework evaluates agent memory systems through three distinct layers:

### Layer 1: Basic Recall & Direct Retrieval
Tests the agent's ability to accurately store and retrieve explicit, unambiguous information from a single conversation. Examples include account numbers, confirmation codes, and appointment details.

### Layer 2: Contextual Reasoning & Disambiguation  
Evaluates the agent's capability to handle ambiguous requests by retrieving ALL relevant information from multiple conversations and recognizing when clarification is needed. The agent must understand context and avoid making assumptions.

### Layer 3: Cross-Session Synthesis & Proactive Assistance
Assesses whether the agent can synthesize information across multiple conversations over time, identify critical connections, and provide proactive assistance without being explicitly asked.

## Features

- **60 Realistic Test Cases**: 20 test cases per layer, each containing 50+ rounds of authentic business conversations
- **LLM-as-Judge Evaluation**: Uses AI to evaluate semantic understanding rather than exact string matching
- **Comprehensive Scenarios**: Covers banking, insurance, healthcare, travel, retail, and more
- **Flexible Framework**: Supports interactive, batch, and programmatic evaluation modes
- **Detailed Reporting**: Generates comprehensive evaluation reports with scores and insights

## Quickstart: Scored Comparison of Memory Systems (Experiment 3-1)

The headline use of this repo is **comparing memory systems** on the three-layer
suite and reading off a scored table. This runs **fully offline** (no API key)
using the `keyword-recall` metric on the canned fixtures in `fixtures/`:

```bash
python main.py --mode compare --metric keyword-recall
```

Real output (8 annotated test cases, four memory configurations):

```
             Memory System Comparison (Keyword Recall, 0.000-1.000)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Layer                         ┃ full_ctx  ┃ json_card ┃ simple_nt ┃ no_memry ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ Layer 1 · Basic Recall        │  1.000    │  1.000    │  0.417    │  0.000   │
│ Layer 2 · Disambiguation      │  1.000    │  1.000    │  0.333    │  0.000   │
│ Layer 3 · Proactive Synthesis │  1.000    │  1.000    │  0.125    │  0.000   │
│ Overall                       │  1.000    │  1.000    │  0.323    │  0.000   │
└───────────────────────────────┴───────────┴───────────┴───────────┴──────────┘
```

The scores are **computed** from `fixtures/system_responses.example.json` by the
recall metric (not hand-written); they reproduce the book's observation that
*Simple Notes* clears most Layer-1 recall cases but degrades sharply on the
Layer-2/3 cases that need disambiguation and cross-session synthesis, whereas
*Advanced JSON Cards* holds up across all three layers.

- `fixtures/gold_facts.json` — the key facts each answer must recall, transcribed
  verbatim from the `test_cases/*.yaml` conversations (no invented values).
- `fixtures/system_responses.example.json` — illustrative answers from four
  configurations. Replace it with real outputs from your own memory system
  (format: `{system_name: {test_id: answer}}`) to benchmark it against the set.

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure evaluator API (Kimi or OpenAI):
```bash
cp env.example .env
# Edit .env with your API credentials
```

## Usage

The CLI ships with a Chinese `--help`; run `python main.py --help` for the full
list. Key flags:

| Flag | Meaning |
| --- | --- |
| `--mode {interactive,demo,batch,compare}` | Run mode (default `interactive`) |
| `--metric {llm-judge,keyword-recall}` | Scorer: LLM-as-judge (needs API) or offline key-fact recall |
| `--responses PATH` | Answers JSON (`batch`: `{test_id: ans}`; `compare`: `{system: {test_id: ans}}`) |
| `--gold PATH` | Gold-fact annotations for `keyword-recall` (default `fixtures/gold_facts.json`) |
| `--category {layer1,layer2,layer3}` | Restrict to one layer |
| `--test-cases-dir PATH` | Alternate test-case (dataset) directory |
| `--evaluator {kimi,openai}` / `--model NAME` | Judge backend / model override for `llm-judge` |
| `--output PATH` | Report output file |
| `--list` | Offline: list all test cases and exit |

### Compare Mode (cross-system scored table)

```bash
# Offline, deterministic (no API):
python main.py --mode compare --metric keyword-recall --output compare.txt

# Only the hardest layer:
python main.py --mode compare --metric keyword-recall --category layer3

# LLM-as-judge scoring of the same systems (requires API key):
python main.py --mode compare --metric llm-judge --evaluator kimi
```

### Interactive Mode

Run the interactive evaluation interface:

```bash
python main.py --mode interactive
```

This provides a menu-driven interface to:
- Browse and view test cases
- Run individual evaluations
- Submit agent responses manually
- Generate evaluation reports

### Demo Mode

See example evaluations with sample responses:

```bash
python main.py --mode demo
```

### Batch Mode

Evaluate multiple test cases programmatically:

```bash
python main.py --mode batch --responses agent_responses.json
```

The JSON file should map test IDs to agent responses:
```json
{
  "layer1_01_bank_account": "Your checking account number is 4429853327.",
  "layer1_02_insurance_claim": "Your claim number is CLM-2024-894327..."
}
```

### Programmatic Usage

```python
from framework import UserMemoryEvaluationFramework

# Initialize framework
framework = UserMemoryEvaluationFramework()

# List test cases
test_cases = framework.list_test_cases(category="layer1")

# Get conversation histories for a test
histories = framework.get_conversation_histories("layer1_01_bank_account")

# Get user question
question = framework.get_user_question("layer1_01_bank_account")

# Submit agent response for evaluation
result = framework.submit_and_evaluate(
    test_id="layer1_01_bank_account",
    agent_response="Your checking account number is 4429853327.",
    extracted_memory=None  # Optional
)

# Check results
print(f"Reward: {result.reward:.3f}")  # Continuous score from 0.0 to 1.0
print(f"Passed: {result.reward >= 0.6}")  # Pass if reward >= 0.6
print(f"Reasoning: {result.reasoning}")
```

## Test Case Structure

Each test case contains:

- **test_id**: Unique identifier
- **category**: layer1, layer2, or layer3
- **title**: Descriptive title
- **conversation_histories**: One or more realistic conversations (50+ rounds each)
- **user_question**: The question posed to the agent
- **evaluation_criteria**: What the agent should retrieve/understand
- **expected_behavior**: Ideal agent response

### Example Test Case Scenarios

**Layer 1 Examples:**
- Bank account setup with account numbers
- Insurance claim with confirmation details  
- Medical appointment scheduling
- Airline reservations with seat assignments
- Internet service installation

**Layer 2 Examples:**
- Multiple vehicles requiring disambiguation
- Several credit cards with different benefits
- Multiple properties or insurance policies
- Family members with separate accounts

**Layer 3 Examples:**
- Passport expiring before booked international travel
- Insurance coverage for planned medical procedure
- Tax documents needed from various past conversations
- Home warranty coverage for reported issue

## Evaluation Metrics

Two interchangeable scorers produce a continuous reward in `[0.0, 1.0]`:

### 1. `keyword-recall` (offline, deterministic)

Key-fact recall: `reward = (# gold facts found in the answer) / (# gold facts)`,
using normalized substring matching (case/whitespace-insensitive; a fact may list
several acceptable surface forms). Requires no API key, so it powers the offline
comparison table. Gold facts live in `fixtures/gold_facts.json`.

### 2. `llm-judge` (LLM-as-judge, needs API)

Uses a judge LLM (Kimi or OpenAI) to score semantic quality against the test
case's `evaluation_criteria` and `expected_behavior`, considering:

1. **Information Retrieval**: Did the agent find the required information?
2. **Completeness**: For ambiguous queries, did it retrieve ALL relevant information?
3. **Accuracy**: Is the retrieved information correct?
4. **Context Understanding**: Does the agent understand the situation?
5. **Proactive Assistance**: Does it identify unstated but relevant connections?

## Configuration

Edit `config.py` or `.env` file:

```python
# Evaluator LLM Settings
KIMI_API_KEY=your_key_here
DEFAULT_EVALUATOR=kimi  # or openai
MAX_RETRIES=3
REQUEST_TIMEOUT=60
```

## Extending the Framework

### Adding New Test Cases

Create YAML files in the appropriate category folder:

```yaml
test_id: layer1_new_case
category: layer1
title: New Test Case Title
conversation_histories:
  - conversation_id: conv_001
    timestamp: "2024-11-20 10:00:00"
    messages:
      - role: user
        content: "User message"
      - role: assistant
        content: "Assistant response"
      # ... 50+ rounds
user_question: "What information should I retrieve?"
evaluation_criteria:
  description: "What to evaluate"
  required_information:
    - "Key piece of information"
  success_indicators:
    - "Signs of success"
expected_behavior: "Ideal response"
```

### Custom Evaluators

Extend the `LLMEvaluator` class:

```python
class CustomEvaluator(LLMEvaluator):
    def evaluate(self, test_case, agent_response, extracted_memory=None):
        # Custom evaluation logic
        return EvaluationResult(...)
```

## Requirements

- Python 3.8+
- API key for Kimi or OpenAI
- 8GB+ RAM for loading conversation histories

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Areas for improvement:
- Additional test cases for specific industries
- Support for more evaluator LLMs
- Multi-language test cases
- Performance optimizations for large-scale evaluations

## Citation

If you use this framework in your research, please cite:

```
User Memory Evaluation Framework
A comprehensive testing suite for AI agent memory systems
https://github.com/your-repo/user-memory-evaluation
```


## OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment now supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.
