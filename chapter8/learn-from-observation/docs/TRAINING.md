# Training Pipeline

## Overview

This document describes the dual-LoRA training algorithm using multi-task learning: simultaneously training the policy to maximize rewards and the world model to predict phone call observations.

## Core Training Algorithm

### Single-Phase Multi-Task Learning

**Key Insight**: Instead of complex alternating updates and intrinsic rewards, simply add world model prediction as an auxiliary loss during standard DAPO training.

```python
For each training step:
  1. Generate rollouts using current policy LoRA
  2. Compute policy loss (DAPO on task rewards)
  3. Compute world model loss (predict phone call responses)
  4. Combined loss = policy_loss + λ * world_model_loss
  5. Single backward pass updates both LoRAs
```

That's it. No phase switching, no intrinsic rewards, no complex scheduling.

### Detailed Training Loop

```python
def train_step(prompts, policy_lora, world_model_lora, optimizer):
    """
    Single training step with multi-task learning.
    """
    # ============= Phase 1: Rollout Generation =============
    # Generate trajectories using current policy
    rollouts = []
    for prompt in prompts:
        for _ in range(n_resp_per_prompt):  # e.g., 8 rollouts
            # Policy LoRA generates actions
            trajectory = generate_trajectory(
                prompt=prompt,
                policy=policy_lora,
                max_turns=16
            )
            # Execute in environment
            executed_trajectory = execute_in_environment(trajectory)
            rollouts.append(executed_trajectory)
    
    # ============= Phase 2: Loss Computation =============
    
    # 2a. Policy Loss (Standard DAPO)
    policy_loss = compute_dapo_loss(
        rollouts=rollouts,
        clip_low=0.2,
        clip_high=0.28
    )
    
    # 2b. World Model Loss (Predict Phone Responses)
    world_model_loss = 0
    num_phone_calls = 0
    
    for trajectory in rollouts:
        for step in trajectory:
            # Only predict phone call responses
            if step.action.tool_name == "make_phone_call":
                # Format input for world model
                wm_input = format_world_model_input(
                    state=step.state,
                    action=step.action
                )
                
                # Get CSR response from observation
                csr_response = step.observation["message"]
                
                # World model predicts response
                with world_model_lora.enabled():
                    predicted_logits = model(wm_input)
                    wm_loss = cross_entropy(predicted_logits, csr_response)
                
                world_model_loss += wm_loss
                num_phone_calls += 1
    
    # Average world model loss
    if num_phone_calls > 0:
        world_model_loss = world_model_loss / num_phone_calls
    else:
        world_model_loss = 0
    
    # ============= Phase 3: Combined Update =============
    
    # Combined loss
    total_loss = policy_loss + λ * world_model_loss
    
    # Single backward pass (updates both LoRAs)
    total_loss.backward()
    
    # Single optimizer step
    optimizer.step()
    optimizer.zero_grad()
    
    return {
        "policy_loss": policy_loss.item(),
        "world_model_loss": world_model_loss.item(),
        "total_loss": total_loss.item()
    }
```

## Input/Output Formatting

### World Model Input Format

**For each phone call**:
```python
Input Template:
<|state|>
Task: {task_description}
Step: {current_step}
Previous Actions:
- {action_1}: {observation_1}
- {action_2}: {observation_2}
Collected Auth: {json.dumps(collected_info)}
<|/state|>

<|action|>
<|tool|>make_phone_call<|args|>
{
  "phone_number": "{phone}",
  "auth_info": {auth_info_dict}
}
<|/tool|>
<|/action|>

<|predict_csr|>
```

**Example**:
```
<|state|>
Task: Check account balance at Acme Bank
Step: 3
Previous Actions:
- search_company("Acme Bank"): Found Customer Service at 800-555-0100
- auth_info_form(["account_number"]): {"account_number": "123456", "unavailable": []}
Collected Auth: {"account_number": "123456"}
<|/state|>

<|action|>
<|tool|>make_phone_call<|args|>{"phone_number": "800-555-0100", "auth_info": {"account_number": "123456"}}<|/tool|>
<|/action|>

<|predict_csr|>
```

### World Model Target Format

**CSR response to predict**:
```python
Target:
<|csr|>For security purposes, I need your account number and the last 4 digits of your Social Security Number.<|/csr|>
```

**Loss Computation**:
```python
# Only compute loss on CSR response tokens
Input tokens:  [state] [action] <|predict_csr|> <|csr|> [CSR response] <|/csr|>
Loss mask:     [  0  ] [   0  ] [      0      ] [  1  ] [      1      ] [   1  ]

loss = masked_cross_entropy(logits, target, mask)
```

## Why This Simplified Approach Works

### 1. Focus on Valuable Signal

**Phone call responses contain the learning signal**:
- CSR explicitly states: "I need account_number and last_4_ssn"
- This is actionable information the agent must learn
- Other tool outputs are either deterministic or less informative

**Not worth predicting**:
- `search_company`: Always returns same result for same company (deterministic)
- `auth_info_form`: Returns user profile data (deterministic given profile)

**Worth predicting**:
- `make_phone_call`: CSR responses vary and contain crucial information about requirements

### 2. Multi-Task Learning is Powerful

**The policy LoRA and world model LoRA share the base model**:
- When world model learns "Customer Service responses typically mention account_number and SSN"
- These patterns affect the shared base model representations
- Policy LoRA benefits implicitly when making decisions
- No need for explicit intrinsic rewards

**Example**:
```
Step 100: World model has learned common CSR patterns
- Can predict with 70% accuracy: "Customer Service asks for account + SSN"

Policy at step 100:
- Hasn't explicitly learned to collect auth first
- But when deciding what to do, base model representations are influenced by world model knowledge
- More likely to call auth_info_form before phone calls
- Learns faster because underlying representations already encode CSR patterns
```

### 3. No Need for Intrinsic Rewards

**Exploration still happens via**:
- DAPO's sampling with temperature=1.0
- Natural exploration from imperfect policy
- Gradient signal from world model loss itself

**The world model loss provides implicit exploration**:
- When world model prediction error is high → larger gradients
- These gradients flow through shared base model
- Policy is influenced to explore situations that reduce world model uncertainty
- No need to explicitly compute surprise and add to rewards

## Training Configuration

### Hyperparameters

**Primary Hyperparameter**:
```python
λ (world_model_loss_weight): 0.5

Range: 0.0 to 2.0
Default: 0.5

Effect:
- λ=0.0: Pure DAPO (baseline)
- λ=0.5: Balanced multi-task learning (recommended)
- λ=1.0: Equal weight to both objectives
- λ=2.0: World model dominates

Tuning:
- Start with 0.5
- If world model accuracy < 50% after 100 steps: increase to 1.0
- If task success rate drops: decrease to 0.3
- Monitor: both losses should be comparable in magnitude
```

**Standard DAPO Parameters** (unchanged):
```python
Clipping:
- ε_low: 0.2
- ε_high: 0.28

Batch size:
- train_batch_size: 8 prompts
- n_resp_per_prompt: 8 rollouts
- ppo_mini_batch_size: 2

Optimization:
- Learning rate: 1e-6 (same for both LoRAs)
- Gradient clipping: 1.0
- Weight decay: 0.1
- Warmup steps: 10
```

**LoRA Configuration** (unchanged):
```python
Policy LoRA:
- Rank: 16
- Alpha: 32
- Target modules: ["q_proj", "v_proj", "o_proj"]
- Dropout: 0.05

World Model LoRA:
- Rank: 16
- Alpha: 32
- Target modules: ["q_proj", "v_proj", "o_proj"]  # Same as policy
- Dropout: 0.05
```

### Implementation in verl

**Configuration File**:
```bash
# configs/run_dual_lora_dapo.sh

# Standard DAPO parameters
adv_estimator=grpo
clip_ratio_low=0.2
clip_ratio_high=0.28
train_batch_size=8
n_resp_per_prompt=8

# LoRA configuration
lora_rank=16
lora_alpha=32
target_modules="all-linear"

# NEW: World model configuration
enable_world_model=True
world_model_loss_weight=0.5
world_model_predict_tool="make_phone_call"  # Only predict this tool's responses

python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=$adv_estimator \
    actor_rollout_ref.actor.clip_ratio_low=$clip_ratio_low \
    actor_rollout_ref.actor.clip_ratio_high=$clip_ratio_high \
    actor_rollout_ref.model.lora_rank=$lora_rank \
    actor_rollout_ref.model.lora_alpha=$lora_alpha \
    actor_rollout_ref.model.target_modules=$target_modules \
    +algorithm.world_model.enable=$enable_world_model \
    +algorithm.world_model.loss_weight=$world_model_loss_weight \
    +algorithm.world_model.predict_tool=$world_model_predict_tool \
    # ... other standard parameters
```

## Loss Details

### Policy Loss (Standard DAPO)

**Computation** (unchanged from baseline):
```python
For each trajectory:
  1. Compute final reward (extrinsic only, no intrinsic)
  2. Group rollouts (N rollouts per prompt)
  3. Compute group-relative advantages
  4. Compute clipped policy gradient loss
  5. Aggregate: token-mean across all tokens

policy_loss = mean(max(L_1, L_2))
where:
  L_1 = -advantage * ratio
  L_2 = -advantage * clip(ratio, 1-ε_low, 1+ε_high)
```

### World Model Loss (New)

**Computation**:
```python
For each phone call in all trajectories:
  1. Extract state before phone call
  2. Extract phone call action (phone number + auth provided)
  3. Extract CSR response (the observation to predict)
  4. Format as prediction task
  5. Compute cross-entropy loss

world_model_loss = mean(cross_entropy(predicted_csr, actual_csr))

Where:
- predicted_csr: Generated by world model LoRA
- actual_csr: Actual CSR response from environment
- mean: Average across all phone calls in batch
```

**Prediction Quality Metrics**:
```python
Track during training:
- Token-level accuracy: % of CSR response tokens predicted correctly
- Semantic accuracy: % where predicted meaning matches actual
- BLEU score: Similarity of predicted vs. actual response
- Perplexity: How confident is world model?

Expected progression:
Steps 1-50: 
  - Token accuracy: 10% → 40%
  - Semantic accuracy: 5% → 25%
  
Steps 50-200:
  - Token accuracy: 40% → 60%
  - Semantic accuracy: 25% → 50%
  
Steps 200-500:
  - Token accuracy: 60% → 75%
  - Semantic accuracy: 50% → 70%
```

## Training Dynamics

### How Both LoRAs Learn Together

**Gradient Flow**:
```
total_loss = policy_loss + λ * world_model_loss
            ↓
        backward()
            ↓
    ┌───────────────┐
    ↓               ↓
Policy LoRA    World Model LoRA
gradients      gradients
    ↓               ↓
Both share gradients through base model
    ↓               ↓
Single optimizer.step() updates both
```

**Shared Representations**:
- Base model embeddings used by both LoRAs
- Attention patterns modified by both LoRAs
- World model learning influences policy's understanding
- Policy learning keeps world model grounded in task success

**Implicit Knowledge Transfer**:
```
World model learns (from CSR responses):
"Customer Service departments typically request account_number and last_4_ssn"

↓ (shared base model representations)

Policy benefits:
When deciding whether to collect auth before calling, 
the base model's representations encode the pattern
that Customer Service needs these fields.
Policy LoRA learns faster because it's building on
world model's learned patterns.
```

### Expected Learning Progression

**Steps 1-50: Both Learning Basics**
```
Policy:
- Success rate: 5% → 25%
- Learning: Basic tool syntax, simple sequences

World Model:
- Prediction accuracy: 10% → 40%
- Learning: Common CSR response patterns

Observation:
- Both losses high
- Both decreasing steadily
- Policy benefits minimal (world model not accurate yet)
```

**Steps 50-200: Synergy Emerges**
```
Policy:
- Success rate: 25% → 60%
- Learning: Complex sequences, auth patterns
- ACCELERATED by world model knowledge

World Model:
- Prediction accuracy: 40% → 65%
- Learning: Department-specific patterns, auth requirements

Observation:
- World model loss decreasing
- Policy learning FASTER than baseline (world model helping)
- Success rate improvement accelerates
```

**Steps 200-500: Refinement**
```
Policy:
- Success rate: 60% → 80%
- Learning: Edge cases, transfer to new companies

World Model:
- Prediction accuracy: 65% → 75%
- Learning: Rare responses, edge cases

Observation:
- Both losses plateauing
- Policy maintains advantage over baseline
- World model accuracy stabilizes
```

## Memory Requirements

### GPU Memory Breakdown (8x RTX 4090)

**Per Training GPU** (6 GPUs with FSDP):
```
Base Model (Qwen3-8B):
- Sharded weights: 16GB / 8 = 2GB
- No gradients (frozen)

Policy LoRA:
- Weights: 10MB
- Gradients: 10MB

World Model LoRA:
- Weights: 10MB
- Gradients: 10MB

Activations (with gradient checkpointing):
- Forward pass activations: ~8GB
- Backward pass recomputation: minimal

FSDP Overhead:
- Communication buffers: 2GB

Optimizer States (offloaded to CPU):
- Adam states: 0GB on GPU

Total per GPU: 2GB + 0.04GB + 8GB + 2GB = ~12GB
```

**Verdict**: ✅ **Fits comfortably on 24GB GPUs with 12GB headroom**

**Per Rollout GPU** (2 GPUs with vLLM TP=2):
```
Base Model:
- Sharded weights: 16GB / 2 = 8GB

Policy LoRA (for inference):
- Weights: 10MB
- No world model LoRA needed for rollouts

KV Cache:
- Per batch: 6-8GB

vLLM Overhead:
- Buffers: 2GB

Total per GPU: 8GB + 10MB + 8GB + 2GB = ~18GB
```

**Verdict**: ✅ **Fits in 24GB**

### CPU Memory

```
Optimizer States (both LoRAs):
- Policy Adam states: 20MB × 2 = 40MB
- World Model Adam states: 20MB × 2 = 40MB
- Total: 80MB (negligible)

Other:
- Data loading: 8GB
- Environment state: 4GB
- Total CPU: ~16GB (very manageable)
```

## Training Time Estimation

### Computational Overhead

**Additional Computation from World Model**:
```
Per training step:

Baseline DAPO:
- Rollout generation: 10 seconds
- Policy forward+backward: 5 seconds
- Parameter sync: 1 second
- Total: 16 seconds/step

Dual-LoRA DAPO:
- Rollout generation: 10 seconds (unchanged)
- Policy forward+backward: 5 seconds (unchanged)
- World model loss computation: +2 seconds (additional forward pass)
- Combined backward pass: +0.5 seconds (two LoRAs)
- Parameter sync: 1 second (unchanged)
- Total: 18.5 seconds/step

Overhead: +15% per step
```

### End-to-End Training Time

**Baseline DAPO**:
```
Configuration:
- 500 training steps
- 16 seconds per step
- Total: ~2.2 hours of training

To reach 70% success:
- Needs ~2500 training tasks
- At 8 tasks/step = 312 steps
- Time: ~83 minutes
```

**Dual-LoRA DAPO**:
```
Configuration:
- 500 training steps
- 18.5 seconds per step
- Total: ~2.6 hours of training (+18% time)

To reach 70% success:
- Needs ~500 training tasks (5x more efficient)
- At 8 tasks/step = 62 steps
- Time: ~19 minutes

Net speedup: 83 / 19 = 4.4x faster to reach same performance
```

## Hyperparameter Tuning

### Primary Hyperparameter: λ (World Model Loss Weight)

**Tuning Strategy**:
```python
1. Start with λ=0.5

2. After 50 steps, check:
   - World model prediction accuracy on CSR responses
   - Task success rate
   
3. Adjust based on observations:

If world_model_accuracy < 30%:
    λ = 1.0  # World model not learning, increase weight
    
If world_model_accuracy > 80% but success_rate < baseline:
    λ = 0.3  # World model dominating, reduce weight
    
If 30% < world_model_accuracy < 80% and success_rate > baseline:
    λ = 0.5  # Keep current setting
```

**Loss Balance Monitoring**:
```python
Ideal ratio:
policy_loss : world_model_loss ≈ 1 : 1 to 2 : 1

If world_model_loss >> policy_loss:
- World model too easy (predicting deterministic responses?)
- Increase λ or filter easier predictions

If policy_loss >> world_model_loss:
- World model converged faster than policy
- Can decrease λ or stop world model training
```

### Secondary Hyperparameters

**LoRA Rank**:
```python
Default: 16

Ablation values to test:
- Rank 8: Faster, less capacity
- Rank 16: Balanced (recommended)
- Rank 32: More capacity, slower

Decision criteria:
- If world model underfitting (accuracy <50%): increase rank
- If overfitting (train accuracy >> val accuracy): decrease rank
```

**World Model Learning Rate** (if using separate optimizers):
```python
Default: 1e-6 (same as policy)

Can be tuned separately:
- Higher (5e-6): Faster world model convergence
- Lower (5e-7): More stable

Generally not necessary - use same LR as policy
```

## Evaluation Metrics

### During Training (Every 10 Steps)

**World Model Metrics**:
```python
1. Prediction Accuracy:
   - Token-level accuracy (exact match)
   - Semantic accuracy (correct meaning)
   - By observation category:
     - Auth failure responses
     - Success responses
     - Routing violation responses

2. Prediction Examples (log to WandB):
   - Show 5 examples per checkpoint:
     - State + Action
     - Predicted CSR response
     - Actual CSR response
     - Comparison
```

**Policy Metrics**:
```python
1. Task Success Rate:
   - Overall validation success
   - By difficulty level (1-5)

2. Learning Efficiency:
   - Tasks seen vs. success rate
   - Compare to baseline DAPO

3. Behavioral Analysis:
   - % tasks where auth collected before calling
   - % tasks with correct department sequence
   - Average phone calls per task (efficiency)
```

**Combined Metrics**:
```python
1. Sample Efficiency:
   - Training tasks to reach 50%, 70%, 90% success
   - Comparison: Baseline vs. Dual-LoRA
   - Expected: 5-10x improvement

2. Loss Correlation:
   - Does lower world model loss → faster policy learning?
   - Scatter plot: WM accuracy vs. policy success rate
```

## Ablation Studies

### Ablation 1: World Model Loss Weight (λ)

**Test values**: [0.0, 0.1, 0.3, 0.5, 1.0, 2.0]

**Metrics**:
- Sample efficiency (primary)
- Final performance
- World model accuracy

**Expected**: λ=0.5 to 1.0 performs best

### Ablation 2: What to Predict

**Variants**:
1. **Phone calls only** (proposed): Predict CSR responses
2. **All tools**: Predict all tool outputs
3. **Phone + form**: Predict phone and auth_info_form outputs
4. **None**: Baseline DAPO (λ=0)

**Hypothesis**: Phone calls only is most efficient (best signal-to-noise ratio)

### Ablation 3: LoRA Rank

**Test values**: [8, 16, 32, 64]

**Metrics**:
- World model accuracy
- Policy success rate
- Training speed
- Memory usage

**Expected**: Rank 16 is optimal (balance capacity and efficiency)

### Ablation 4: Training Schedule

**Variants**:
1. **Joint** (proposed): Update both LoRAs every step
2. **Alternating**: Update world model, then policy (separate steps)
3. **World model first**: Pre-train world model for 50 steps, then joint
4. **Hierarchical**: Update world model every 5 steps, policy every step

**Hypothesis**: Joint training works best (simpler, no tuning of update ratios)

## Training from Scratch

### No Pre-Training Needed

**Start directly from Qwen3-8B base model**:
```python
Step 0:
- Load Qwen3-8B-Base (no instruction tuning, no SFT)
- Initialize two random LoRA adapters
- Both LoRAs start with random weights

Step 1:
- Policy generates (mostly) random trajectories
- Execute in environment → get observations
- Compute both losses on first batch
- Update both LoRAs

No need for:
❌ SFT phase
❌ Pre-collected trajectories
❌ Warm-start from instruction-tuned model
```

### Why This Works

**Random trajectories still provide signal**:
- Even random tool calls generate CSR responses
- World model can learn from these (e.g., "calling without auth → rejection")
- As policy improves, world model sees better data
- They co-evolve from random initialization

**Early training dynamics**:
```
Steps 1-10 (random policy):
- Policy: Generates random tool sequences
- Observations: Mostly failures, but informative failures
- World model: Learns "no auth → CSR asks for auth"
- Policy gradient: Weak (most rewards are 0)
- World model gradient: Strong (clear patterns even in failures)

Steps 10-50 (emerging patterns):
- Policy: Learns basic tool usage
- Observations: Mix of failures and partial successes
- World model: Learns department-specific patterns
- Both: Learning accelerates

Steps 50+:
- Normal training dynamics (described above)
```

## Optimization Details

### Optimizer Configuration

**Single Optimizer for Both LoRAs**:
```python
# Collect parameters from both adapters
policy_params = model.get_adapter_params("policy")
world_model_params = model.get_adapter_params("world_model")
all_params = list(policy_params) + list(world_model_params)

# Single optimizer
optimizer = torch.optim.AdamW(
    all_params,
    lr=1e-6,
    betas=(0.9, 0.95),
    weight_decay=0.1
)

# Single learning rate scheduler
scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=10,
    num_training_steps=500
)
```

**Advantages**:
- Simpler: One optimizer to manage
- Synchronized: Both LoRAs update together
- Memory efficient: Single optimizer state

**Alternative** (if needed):
```python
# Separate optimizers with different learning rates
optimizer_policy = AdamW(policy_params, lr=1e-6)
optimizer_wm = AdamW(world_model_params, lr=5e-6)  # Can be higher

# Update both in same step
total_loss.backward()
optimizer_policy.step()
optimizer_wm.step()
```

### Gradient Management

**Gradient Clipping**:
```python
# Clip gradients for both LoRAs together
torch.nn.utils.clip_grad_norm_(all_params, max_norm=1.0)
```

**Gradient Monitoring**:
```python
Track per step:
- Policy LoRA gradient norm
- World Model LoRA gradient norm
- Ratio: Should be roughly balanced (1:1 to 3:1)

Warning signs:
- If policy_grad_norm >> wm_grad_norm (>10x):
  - World model saturated or λ too small
  
- If wm_grad_norm >> policy_grad_norm (>10x):
  - λ too large, world model dominating
```

## Expected Results

### Sample Efficiency

**Primary Metric: Tasks to 70% Success**:
```
Baseline DAPO: ~2500 tasks
Dual-LoRA DAPO: ~500 tasks
Improvement: 5x
```

**Learning Curve Comparison**:
```
Tasks Seen    | Baseline Success | Dual-LoRA Success
---------------------------------------------------------
100           | 15%             | 35%
500           | 35%             | 70%  ← Target reached
1000          | 50%             | 80%
2500          | 70%  ← Target  | 85%
```

### World Model Contribution

**Correlation Analysis**:
```
Hypothesis: Better world model → faster policy learning

Measure:
- At step N, compute world model accuracy
- Measure policy learning rate (Δ success / Δ tasks) for next 50 steps
- Plot correlation

Expected: Strong positive correlation (r > 0.7)
```

### Transfer Learning

**Zero-Shot Transfer to New Companies**:
```
Training: 50 companies (banking, insurance, telecom)
Testing: 50 new companies (same industries)

Baseline DAPO:
- Zero-shot success: ~15% (random exploration)

Dual-LoRA DAPO:
- Zero-shot success: ~45% (world model predicts patterns)
- 3x improvement

Interpretation:
World model learned: "Customer Service typically needs account + SSN"
This transfers to new companies even without training on them
```

## Debugging and Troubleshooting

### Common Issues

**Issue 1: World Model Not Learning (Accuracy <30% After 100 Steps)**

Potential causes:
- λ too small (world model loss dominated by policy loss)
- Observation formatting issues (model can't parse)
- Batch size too small (insufficient examples)

Solutions:
- Increase λ to 1.0 or 2.0
- Verify observation format consistency
- Increase batch size or use observation replay buffer

**Issue 2: Policy Performance Decreases**

Potential causes:
- λ too large (world model dominating)
- World model learning incorrect patterns
- Gradient conflict between two objectives

Solutions:
- Decrease λ to 0.3 or 0.1
- Check world model predictions manually (are they reasonable?)
- Try alternating updates instead of joint

**Issue 3: Both Losses Not Decreasing**

Potential causes:
- Learning rate too low/high
- LoRA rank too small (underfitting)
- Environment too noisy

Solutions:
- Adjust learning rate (try 5e-6 or 2e-6)
- Increase LoRA rank to 32
- Validate environment (manually check if CSR responses are consistent)

**Issue 4: OOM (Out of Memory)**

Potential causes:
- Batch size too large
- Sequence lengths too long
- Gradient accumulation not enabled

Solutions:
- Reduce n_resp_per_prompt from 8 to 6
- Reduce max_response_length from 8192 to 6144
- Enable gradient accumulation (split mini-batches)
- Ensure optimizer offload is enabled

### Diagnostic Tools

**Trajectory Inspection**:
```bash
# Save sample trajectories every 50 steps
python scripts/save_trajectories.py \
    --checkpoint checkpoint_step_50 \
    --num_samples 10 \
    --output diagnostics/step_50/

# Inspect world model predictions
python scripts/inspect_world_model.py \
    --checkpoint checkpoint_step_50 \
    --trajectory diagnostics/step_50/traj_0.json
```

**World Model Probing**:
```python
# Test world model predictions on synthetic inputs
test_cases = [
    {
        "state": "Task: Check balance. Step: 2. Collected: {}",
        "action": "make_phone_call('800-555-0100', {})",
        "expected_pattern": "CSR should request authentication"
    },
    {
        "state": "Task: Check balance. Collected: {account_number, last_4_ssn}",
        "action": "make_phone_call('800-555-0100', {account_number, last_4_ssn})",
        "expected_pattern": "CSR should provide service"
    }
]

for test in test_cases:
    predicted = world_model.predict(test.state, test.action)
    print(f"Predicted: {predicted}")
    print(f"Expected pattern: {test.expected_pattern}")
```

## Summary

The simplified dual-LoRA training approach:

**What changed from original design**:
- ❌ Removed: Alternating phase updates
- ❌ Removed: Intrinsic reward computation
- ❌ Removed: Surprise-based exploration
- ❌ Removed: Complex scheduling
- ✅ Added: Simple multi-task learning (one loss function)
- ✅ Added: Single optimizer, single backward pass
- ✅ Added: Only predict phone call responses

**Benefits**:
- Simpler to implement (standard multi-task learning)
- Easier to debug (fewer moving parts)
- Faster training (no phase overhead)
- One hyperparameter to tune (λ instead of many)
- More stable (no alternating dynamics)

**Core insight**: The world model helps policy learning through shared representations, not through explicit intrinsic rewards. Multi-task learning is sufficient.
