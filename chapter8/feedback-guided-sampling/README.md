# Feedback-Guided DAPO for Sample-Efficient Reinforcement Learning

> **Novel RL Training Method**: Using critique feedback from failed rollouts to guide subsequent rollouts within the same training batch, dramatically improving sample efficiency.

## Overview

This project implements a novel extension to DAPO (Decoupled Clip and Dynamic Sampling Policy Optimization) that incorporates **within-group feedback guidance** to achieve significantly better sample efficiency in reinforcement learning for language models.

### The Core Innovation

Standard GRPO/DAPO generates N rollouts per prompt uniformly from the current policy. Our method introduces **sequential feedback conditioning**:

1. **Rollout 1**: Generate from original prompt → Execute → Get reward + feedback
2. **Rollout 2**: Generate from **original prompt + Rollout 1's feedback** → Execute → Get reward + feedback
3. **Rollout 3-N**: Continue with accumulated feedback from all previous failed attempts
4. **GRPO Update**: Train on all N rollouts with their actual rewards

This leverages the model's in-context learning capability to explore more intelligently within each training batch, while still using gradient descent to improve the base policy.

**Why This Matters for Our Task**: Since authentication requirements aren't provided in the directory, the agent MUST learn from CSR feedback. When a CSR says "I need account_number and last_4_ssn", this becomes crucial training signal. Feedback-guided rollouts allow later attempts in the same batch to immediately use this information, dramatically improving sample efficiency compared to waiting for random exploration to discover the right authentication combination.

## Key Features

- **No SFT Required**: Trains directly from base model using DAPO
- **Single Model**: Uses Qwen3-8B for both policy and critique generation
- **Multi-turn Tool Use**: Supports complex agent workflows with tool interactions
- **Sample Efficiency**: Expected 5-10x improvement over standard GRPO on structured tasks
- **Hardware Efficient**: Runs on 8x RTX 4090 (24GB) with memory optimizations

## Validation Scenario: Customer Service Phone Calls

We validate the approach on a realistic customer service scenario where an agent must:

1. **Search company directory** to find department contact information
2. **Infer or learn** what authentication each department requires (not provided in directory)
3. **Collect authentication information** from the user (in a single form submission)
4. **Make phone calls** with complete authentication to complete user requests

This scenario provides:
- **Clear success/failure criteria**: Task succeeds when all required calls are completed
- **Actionable feedback**: CSR explicitly states what authentication is missing
- **Multiple difficulty levels**: 1-5 departments with various routing dependencies
- **Key learning challenges**:
  - Agent must INFER what authentication each department needs (not listed in directory)
  - Must collect ALL required fields in ONE call to auth_info_form (no iterative collection)
  - Must learn optimal strategies through experience and feedback
- **Realistic complexity**: Similar to real-world API composition where requirements aren't documented

## Project Structure

```
feedback-guided-sampling/
├── README.md                          # This file
├── docs/
│   ├── ARCHITECTURE.md               # System architecture
│   ├── IMPLEMENTATION_PLAN.md        # Detailed implementation steps
│   ├── HARDWARE_REQUIREMENTS.md      # GPU memory analysis
│   └── API_SPECIFICATION.md          # Tool and interface specs
├── src/
│   ├── environment/                  # Simulation environment
│   │   ├── user_simulator.py
│   │   ├── company_directory.py
│   │   ├── phone_system.py
│   │   └── task_generator.py
│   ├── tools/                        # Custom agent tools
│   │   ├── auth_info_form_tool.py
│   │   ├── company_directory_tool.py
│   │   └── phone_call_tool.py
│   ├── training/                     # Training infrastructure
│   │   ├── dataset.py
│   │   ├── reward.py
│   │   ├── feedback_trainer.py
│   │   └── feedback_generator.py
│   └── evaluation/                   # Evaluation scripts
│       ├── metrics.py
│       └── analysis.py
├── configs/
│   ├── tool_config.yaml
│   └── training_config.sh
├── data/                             # Generated datasets
│   ├── companies/
│   └── tasks/
└── experiments/                      # Experiment logs and results
    └── baselines/
```

## Quick Start

### Prerequisites

- Python 3.10+
- PyTorch 2.0+
- 8x GPU (24GB+ VRAM each)
- Ray cluster setup
- verl framework

### Installation

```bash
# Clone the repository
cd projects/week7/feedback-guided-sampling

# Install dependencies
pip install -r requirements.txt

# Install verl
cd ../verl && pip install -e .
```

### Generate Data

```bash
# Generate company directory and tasks
python src/environment/task_generator.py \
    --num_companies 100 \
    --num_train_tasks 500 \
    --num_val_tasks 100 \
    --output_dir ./data
```

### Run Baseline (Standard DAPO)

```bash
bash configs/run_baseline_dapo.sh
```

### Run Feedback-Guided DAPO

```bash
bash configs/run_feedback_guided_dapo.sh
```

## Key Results (Expected)

| Method | Success@70% (tasks) | First-try Success | With-feedback Success | Training Time |
|--------|---------------------|-------------------|----------------------|---------------|
| Standard DAPO | ~2500 | 45% | - | 5 days |
| Feedback-Guided DAPO | **~500** | 60% | 82% | 7 days |
| Improvement | **5x** | **+15%** | - | 1.4x slower |

## Research Questions

This project investigates:

1. **Sample Efficiency**: Can within-group feedback achieve 5-10x sample efficiency improvement?
2. **Base Policy Learning**: Does the base policy internalize behaviors, or only learn to follow feedback?
3. **Feedback Quality**: How does critique quality (rule-based vs. LLM-generated) affect improvement?
4. **Generalization**: Does the method transfer to unseen companies and task variations?
5. **Scalability**: Does the approach work across different difficulty levels?

## Related Work

- **DAPO** (ByteDance-Tsinghua, 2025): Our base algorithm
- **ReTool** (ByteDance, 2025): Tool-use RL framework we build upon
- **Text2Grad** (2025): Converts textual feedback to gradients (different approach)
- **Constitutional AI** (Anthropic, 2022): Uses critique for data generation (offline)
- **Reflexion** (Shinn et al., 2023): Uses memory between episodes (not within batch)

**Key Difference**: We use feedback **within the same training batch** to guide rollout generation, enabling immediate sample efficiency gains during online RL training.
