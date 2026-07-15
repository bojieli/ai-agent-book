# Learning from Observation: Dual-LoRA World Model for Agent Training

> **Core Innovation**: Train agents to learn from environmental observations (not just sparse rewards) by maintaining separate LoRA adapters for policy and world model, achieving 5-10x sample efficiency improvement.

## Overview

This project implements a dual-LoRA architecture that enables language model agents to learn from environmental observations through simple multi-task learning. Unlike standard model-free RL methods (PPO, GRPO, DAPO) that only learn from sparse final rewards, our approach adds an auxiliary task: predicting CSR responses from phone calls. This provides 10-15x more learning signal per trajectory while adding only one hyperparameter (λ) to standard DAPO.

## The Core Problem

**Current Model-Free RL**:
```
Agent makes 10 tool calls → Task fails → Gets reward = 0

Learning signal: 1 scalar (the final reward)
Wasted information: 9 intermediate observations
```

**With World Model Learning**:
```
Agent makes 10 tool calls → Task fails → Gets reward = 0
But world model learns from ALL 10 (state, action, observation) tuples

Learning signal: 10 prediction errors + 1 scalar = 11x more signal per trajectory
```

## Key Innovation: Dual-LoRA Multi-Task Learning

**Two separate LoRA adapters on the same base model**:

1. **Policy LoRA**: Learns what actions to take (π(a|s))
   - Objective: Maximize task rewards (DAPO)
   - Target modules: attention layers
   - Rank: 16

2. **World Model LoRA**: Learns to predict CSR responses (P(obs|s,a))
   - Objective: Minimize prediction error (cross-entropy)
   - Target modules: same attention layers as policy
   - Rank: 16

**Training**: Simple multi-task learning
```
total_loss = policy_loss + λ * world_model_loss
```

**Key Insight**: Both LoRAs share the base model's representations. When world model learns "Customer Service typically requests account_number and SSN", this knowledge implicitly helps the policy learn to collect authentication before calling. No complex intrinsic rewards or phase switching needed—just clean multi-task learning.

## Validation Scenario: Customer Service Phone Calls

Same environment as the feedback-guided sampling project:

1. Search company directory for department information
2. Infer required authentication (not provided in directory)
3. Collect authentication via single form submission
4. Make phone calls with complete authentication

**Why This Tests World Model Learning**:
- CSR responses are non-deterministic and information-rich
- Authentication requirements must be learned from CSR feedback
- World model must learn: "If I call Customer Service without account_number, CSR will say 'I need your account number'"
- This knowledge should transfer to new companies

## Key Features

- **Observation-Based Learning**: Learn from CSR responses at every phone call (not just final rewards)
- **Simple Multi-Task Learning**: Single loss function, single backward pass, one hyperparameter (λ)
- **Zero-Shot Transfer**: World model learns general patterns that transfer to new companies
- **Parameter Efficient**: Only train lightweight LoRA adapters (~20MB each)
- **Compatible with DAPO**: Minimal changes to existing verl/DAPO infrastructure
- **Hardware Efficient**: Runs on 8x RTX 4090 (24GB each) with 12GB headroom
- **No SFT Required**: Trains directly from Qwen3-8B base model

## Expected Results

**Sample Efficiency**:
- Baseline DAPO: ~2500 tasks to reach 70% success
- Dual-LoRA DAPO: ~250-500 tasks to reach 70% success
- **Improvement: 5-10x fewer training samples**

**Transfer Learning**:
- Train on 50 companies → Test on 50 new companies
- World model predictions transfer across companies
- Policy benefits from world model's general knowledge

**Per-Step Learning**:
- Standard RL: 1 learning signal per trajectory (final reward)
- Dual-LoRA: 10-15 learning signals per trajectory (all observations)

## Project Structure

```
learn-from-observation/
├── README.md                          # This file
├── docs/
│   ├── ARCHITECTURE.md                # System architecture and dual-LoRA design
│   ├── ENVIRONMENT.md                 # Environment and tool specifications
│   ├── TRAINING.md                    # Training pipeline and algorithms
│   └── VERL_INTEGRATION.md           # verl-specific implementation details
├── configs/
│   ├── tool_config.yaml
│   ├── dual_lora_config.yaml
│   └── training_config.sh
└── data/
    ├── companies/
    └── tasks/
```

## Technical Highlights

### World Model Architecture

**State Representation**:
- Conversation history compressed to 512 tokens
- Task goal, tools called, information collected
- Current step number and department context

**Action Representation**:
- Structured tool calls with parameters
- Format: `<|tool|>make_phone_call<|args|>{"phone": "800-555-0100", "auth_info": {...}}<|end|>`

**Observation Prediction**:
- Predict next observation token-by-token
- Loss: Standard next-token prediction (cross-entropy)
- Target: `<|obs_start|>CSR: "I need your account number"<|obs_end|>`

### Training Pipeline

**Online RL with Alternating Updates**:

1. **Generate Rollouts** (Policy LoRA active)
   - Generate N trajectories from current policy
   - Execute in environment
   - Collect (state, action, observation, reward) tuples

2. **World Model Update** (World Model LoRA active, Policy frozen)
   - For each (s_t, a_t, o_{t+1}):
     - Predict o_{t+1} given s_t and a_t
     - Compute prediction loss
   - Update world model LoRA

3. **Compute Intrinsic Rewards**
   - Prediction error → intrinsic reward (exploration bonus)
   - High surprise = novel situation = more reward

4. **Policy Update** (Policy LoRA active, World Model frozen)
   - Combined reward = extrinsic (task) + intrinsic (surprise)
   - Update policy LoRA with DAPO

### verl Integration

**LoRA Support in verl**:
- Uses huggingface peft for LoRA adapters
- Compatible with FSDP/FSDP2 training strategy
- Works with vLLM for fast rollout generation
- Supports adapter switching and weight updates

**Dual-LoRA Implementation**:
- Load two named adapters: "policy" and "world_model"
- Switch active adapter during training phases
- Synchronize policy adapter to vLLM for rollouts
- Keep world model adapter on training workers only

## Hardware Requirements

### Memory Analysis for 8x RTX 4090 (24GB)

**Base Model (Qwen3-8B)**:
- Model weights: 16GB (bf16) / 8 GPUs = 2GB per GPU

**Policy LoRA**:
- Weights: 20MB
- Gradients: 20MB

**World Model LoRA**:
- Weights: 20MB
- Gradients: 20MB

**Activations** (with gradient checkpointing):
- Batch size: 4 per GPU
- Sequence length: 2560 (state + observation)
- Activations: ~10GB per GPU

**Total per GPU**: 2GB + 0.08GB + 10GB = **~12GB**

**Verdict**: ✅ Fits comfortably on 8x RTX 4090 with headroom

### Training Time

- World model updates add ~30% overhead
- Total training time: ~1.5x baseline DAPO
- But achieves same performance with 5-10x fewer samples
- **Net speedup: 3-7x faster to convergence**

## Advantages Over Baseline DAPO

| Aspect | Baseline DAPO | Dual-LoRA DAPO |
|--------|---------------|----------------|
| Learning Signal | Final rewards only | All observations + rewards |
| Exploration | Random or entropy-based | Surprise-driven (principled) |
| Transfer Learning | Limited | Generalizes via world model |
| Sample Efficiency | 1x | 5-10x |
| Training Time | 1x | 1.5x |
| Time to Convergence | 1x | 0.15-0.3x (3-7x faster) |

## Design Philosophy: Simplicity

**Original complex design** (discarded):
- 4 training phases (rollout, WM update, intrinsic reward, policy update)
- Intrinsic rewards from surprise
- Separate optimizers for each LoRA
- Complex scheduling and phase coordination

**Current simple design**:
- 1 training loop (generate → compute losses → update)
- Multi-task learning (policy + WM loss)
- Single optimizer, single backward pass
- One hyperparameter: λ

**Result**: Same benefits (observation-based learning), 10x simpler implementation.

## Complementary to Feedback-Guided Sampling

These two approaches are **orthogonal and composable**:

- **Feedback-Guided**: Within-batch in-context learning (fast adaptation per batch)
- **Dual-LoRA**: Cross-batch observation-based learning (accumulates knowledge over training)
- **Combined**: Potential for 25-100x sample efficiency (multiplicative effect)

Both can be implemented independently and combined later.

## Getting Started

### Prerequisites

- Python 3.10+
- PyTorch 2.0+
- 8x GPU with 24GB+ VRAM each
- verl framework
- Ray cluster setup

### Installation

```bash
cd projects/week7/learn-from-observation

# Install dependencies (same as feedback-guided)
pip install -r requirements.txt

# Install verl
cd ../verl && pip install -e .
```

### Generate Environment Data

```bash
python scripts/generate_environment.py \
    --num_companies 100 \
    --num_train_tasks 500 \
    --num_val_tasks 100 \
    --output_dir ./data
```

### Training

```bash
# Run baseline DAPO for comparison
bash configs/run_baseline_dapo.sh

# Run dual-LoRA DAPO
bash configs/run_dual_lora_dapo.sh
```

## Research Questions

1. **Does world model auxiliary loss improve sample efficiency?**
   - Hypothesis: Yes, 5-10x improvement over baseline DAPO
   - Measure: Tasks needed to reach 70% success

2. **Do world model predictions transfer across companies?**
   - Hypothesis: Yes, learns "Customer Service typically needs account + SSN"
   - Measure: Zero-shot success rate on 50 held-out companies

3. **What's the optimal world model loss weight (λ)?**
   - Hypothesis: λ=0.5 to 1.0 works best
   - Measure: Ablation study on λ ∈ [0.0, 0.1, 0.3, 0.5, 1.0, 2.0]

4. **Does world model quality correlate with policy improvement?**
   - Hypothesis: Yes, better CSR prediction → faster policy learning
   - Measure: Correlation between WM accuracy and policy success rate

5. **Is prediction only on phone calls sufficient?**
   - Hypothesis: Yes, other tools are deterministic (not worth predicting)
   - Measure: Compare predicting all tools vs. phone calls only

## References

- **DAPO**: Decoupled Clip and Dynamic Sampling Policy Optimization
- **verl**: Volcano Engine Reinforcement Learning framework
- **Customer Service Task**: Same as feedback-guided sampling project
- **Blog Post**: https://01.me/2025/10/agent-continual-learning/

## License

Apache 2.0 (following verl framework)

