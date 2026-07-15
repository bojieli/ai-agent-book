# verl Framework Integration

## Overview

This document provides technical details on integrating dual-LoRA world model learning into the verl framework, building on the existing DAPO implementation from the retool recipe.

## verl LoRA Support

Based on verl documentation and code analysis, verl supports LoRA through:

- **Backend**: Huggingface PEFT library
- **Training strategies**: FSDP and FSDP2
- **Rollout backend**: vLLM (SGLang support coming)
- **Algorithms**: PPO, GRPO, DAPO, and others

### Standard LoRA Configuration

**Existing verl LoRA parameters**:
```yaml
actor_rollout_ref:
  model:
    lora_rank: 16              # LoRA rank (r)
    lora_alpha: 32             # Scaling factor
    target_modules: "all-linear"  # Which layers to adapt
    use_shm: True              # Preload model to /dev/shm
  
  rollout:
    load_format: "safetensors"  # Required for vLLM
    layered_summon: True        # Reduces memory for large models
```

## Extending to Dual-LoRA

### Challenge: verl Expects Single LoRA

**Current verl assumption**:
- One LoRA adapter per model
- Adapter synchronized to vLLM for rollouts
- Adapter updated during training

**Our requirement**:
- Two LoRA adapters (policy and world_model)
- Only policy adapter synchronized to vLLM
- Both adapters updated during training

### Solution: PEFT Multi-Adapter Support

**Huggingface PEFT supports multiple adapters**:

```python
from peft import get_peft_model, LoraConfig

# Create base model
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B-Base")

# Add first adapter (policy)
policy_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "o_proj"],
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, policy_config, adapter_name="policy")

# Add second adapter (world_model)
world_model_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "o_proj"],
    task_type="CAUSAL_LM"
)
model.add_adapter("world_model", world_model_config)

# Switch between adapters
model.set_adapter("policy")        # For policy forward pass
model.set_adapter("world_model")   # For world model forward pass
model.set_adapter(["policy", "world_model"])  # For joint backward
```

### How Dual-LoRA Works with PEFT

**PEFT Multi-Adapter Support**:

PEFT (Parameter-Efficient Fine-Tuning) library supports multiple adapters on the same base model. The custom trainer leverages this to create and manage both LoRA adapters:

```python
# In custom trainer's model initialization

# Create base model
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B-Base")

# Add policy adapter
policy_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "o_proj"],
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, policy_config, adapter_name="policy")

# Add world model adapter (same config, separate parameters)
model.add_adapter("world_model", policy_config)

# Set default adapter for rollouts
model.set_adapter("policy")
```

**Adapter Switching During Training**:
```python
# For policy loss computation
model.set_adapter("policy")
policy_logits = model(state)
policy_loss = compute_dapo_loss(policy_logits, ...)

# For world model loss computation
model.set_adapter("world_model")
wm_logits = model(state + action)
wm_loss = cross_entropy(wm_logits, csr_response)

# Combined backward updates both
total_loss = policy_loss + λ * wm_loss
total_loss.backward()  # Gradients for both LoRAs
optimizer.step()  # Updates both LoRAs
```

## Custom Trainer Implementation

### DualLoRADAPOTrainer Class

**File**: `src/training/dual_lora_trainer.py`

```python
from verl.trainer.ppo.ray_trainer import RayPPOTrainer
import torch
import torch.nn.functional as F

class DualLoRADAPOTrainer(RayPPOTrainer):
    """
    Extends verl's standard PPO/DAPO trainer with world model auxiliary loss.
    
    Key changes:
    1. Initialize dual-LoRA adapters in setup_model()
    2. Add world model loss in compute_actor_loss()
    3. Track world model metrics in evaluate()
    """
    
    def __init__(self, config):
        super().__init__(config)
        
        # World model configuration from config
        self.wm_config = config.algorithm.get("world_model", None)
        if self.wm_config and self.wm_config.get("enable", False):
            self.use_world_model = True
            self.wm_loss_weight = self.wm_config.get("loss_weight", 0.5)
            self.wm_predict_tool = self.wm_config.get("predict_tool", "make_phone_call")
        else:
            self.use_world_model = False
    
    def setup_model(self):
        """
        Override to initialize dual-LoRA instead of single LoRA.
        """
        # Call parent to load base model
        super().setup_model()
        
        if self.use_world_model:
            # Base model already has policy LoRA from parent
            # Add world model LoRA
            lora_config = LoraConfig(
                r=self.config.actor_rollout_ref.model.lora_rank,
                lora_alpha=self.config.actor_rollout_ref.model.lora_alpha,
                target_modules=self.config.actor_rollout_ref.model.target_modules,
                task_type="CAUSAL_LM"
            )
            self.actor_module.add_adapter("world_model", lora_config)
            print("Added world_model LoRA adapter")
    
    def compute_actor_loss(self, data):
        """
        Override to add world model loss.
        
        Called by verl's training loop during actor update phase.
        """
        # Standard policy loss (DAPO/GRPO)
        policy_loss = super().compute_actor_loss(data)
        
        if not self.use_world_model:
            return policy_loss
        
        # Add world model auxiliary loss
        world_model_loss = self.compute_world_model_loss(data)
        
        # Combined loss
        total_loss = policy_loss + self.wm_loss_weight * world_model_loss
        
        # Log both components
        self.log_dict({
            "train/policy_loss": policy_loss.item(),
            "train/world_model_loss": world_model_loss.item(),
            "train/total_loss": total_loss.item(),
            "train/wm_contribution": (self.wm_loss_weight * world_model_loss / total_loss).item()
        })
        
        return total_loss
    
    def compute_world_model_loss(self, data):
        """
        Compute world model auxiliary loss on CSR response prediction.
        
        Only predicts CSR responses from make_phone_call tool.
        Other tools (search_company, auth_info_form) are deterministic.
        """
        # Extract phone call observations from trajectories
        wm_tuples = self.extract_phone_call_tuples(data)
        
        if len(wm_tuples) == 0:
            # No phone calls in this batch
            return torch.tensor(0.0, device=data.batch["input_ids"].device)
        
        # Switch to world model adapter
        self.actor_module.set_adapter("world_model")
        
        # Compute predictions and losses for each phone call
        wm_losses = []
        for state, action, csr_response in wm_tuples:
            # Format input for world model prediction
            input_ids, attention_mask = self.format_wm_input(state, action)
            
            # Format target (CSR response to predict)
            csr_token_ids = self.tokenizer.encode(
                f"<|csr|>{csr_response}<|/csr|>",
                return_tensors="pt"
            ).to(input_ids.device)
            
            # Concatenate for teacher forcing
            full_input_ids = torch.cat([input_ids, csr_token_ids], dim=1)
            
            # Create labels (mask input portion, predict CSR portion)
            labels = torch.cat([
                torch.full_like(input_ids, -100),  # Ignore input tokens
                csr_token_ids  # Predict CSR tokens
            ], dim=1)
            
            # Forward pass (world model LoRA active)
            outputs = self.actor_module(
                input_ids=full_input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            # Loss computed by model (only on CSR tokens)
            wm_losses.append(outputs.loss)
        
        # Switch back to policy adapter
        self.actor_module.set_adapter("policy")
        
        # Average world model loss across all phone calls
        return torch.stack(wm_losses).mean()
    
    def extract_phone_call_tuples(self, data):
        """
        Extract (state, action, CSR_response) tuples from trajectories.
        
        Parses multi-turn tool conversations to find make_phone_call actions
        and their corresponding CSR responses.
        """
        tuples = []
        
        # Parse batch data (format depends on verl's data structure)
        for trajectory in self.parse_trajectories(data):
            # Build state incrementally as we walk through trajectory
            state_context = self.build_state_context(trajectory)
            
            for turn_idx, turn in enumerate(trajectory.turns):
                if turn.tool_name == self.wm_predict_tool:
                    # Extract state before this phone call
                    state_str = self.format_state(state_context, turn_idx)
                    
                    # Extract action (phone call parameters)
                    action_str = self.format_action(turn.tool_call)
                    
                    # Extract observation (CSR response message)
                    csr_response = turn.tool_response.get("message", "")
                    
                    if csr_response:  # Only include if CSR responded
                        tuples.append((state_str, action_str, csr_response))
                
                # Update state for next turn
                state_context = self.update_state(state_context, turn)
        
        return tuples
    
    def format_wm_input(self, state, action):
        """
        Format state and action for world model prediction input.
        """
        prompt = f"""<|state|>
{state}
<|/state|>
<|action|>
{action}
<|/action|>
<|predict_csr|>"""
        
        return self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=False,
            truncation=False
        ).to(self.device)
    
    def evaluate(self):
        """
        Override to add world model evaluation metrics.
        """
        # Standard policy evaluation
        policy_metrics = super().evaluate()
        
        if self.use_world_model:
            # Evaluate world model prediction quality
            wm_metrics = self.evaluate_world_model()
            policy_metrics.update(wm_metrics)
        
        return policy_metrics
    
    def evaluate_world_model(self):
        """
        Evaluate world model prediction accuracy on validation set.
        """
        self.actor_module.set_adapter("world_model")
        self.actor_module.eval()
        
        total_accuracy = 0
        num_predictions = 0
        
        # Generate validation rollouts and check predictions
        for val_trajectory in self.validation_trajectories:
            for turn in val_trajectory.turns:
                if turn.tool_name == self.wm_predict_tool:
                    predicted = self.predict_csr(turn.state, turn.action)
                    actual = turn.observation.message
                    
                    accuracy = self.compute_semantic_match(predicted, actual)
                    total_accuracy += accuracy
                    num_predictions += 1
        
        self.actor_module.set_adapter("policy")
        
        if num_predictions == 0:
            return {}
        
        return {
            "val/wm_accuracy": total_accuracy / num_predictions,
            "val/wm_num_predictions": num_predictions
        }
```

### Using the Custom Trainer

**Main training script**: `src/training/main_dual_lora.py`

```python
import hydra
from omegaconf import DictConfig
from src.training.dual_lora_trainer import DualLoRADAPOTrainer

@hydra.main(config_path="../../configs", config_name="dual_lora_config")
def main(config: DictConfig):
    """
    Entry point for dual-LoRA DAPO training.
    """
    # Create custom trainer
    trainer = DualLoRADAPOTrainer(config)
    
    # Run training
    trainer.fit()

if __name__ == "__main__":
    main()
```

**Launch training**:
```bash
# Instead of python3 -m verl.trainer.main_ppo
# Use custom entry point:
python3 -m src.training.main_dual_lora \
    # ... all config parameters same as before
```

### Custom Configuration Schema

**File**: `configs/dual_lora_config.yaml`

```yaml
# Extend standard DAPO configuration
defaults:
  - dapo_trainer  # Inherit from verl's DAPO config

# NEW: World model configuration
algorithm:
  adv_estimator: grpo
  
  world_model:
    enable: true
    loss_weight: 0.5
    predict_tool: "make_phone_call"
    log_predictions: true
    log_frequency: 10

# LoRA configuration
actor_rollout_ref:
  model:
    # Dual-LoRA specific
    use_dual_lora: true
    adapter_names: ["policy", "world_model"]
    
    # Standard LoRA settings
    lora_rank: 16
    lora_alpha: 32
    target_modules: "all-linear"
    
    # Model path
    path: "Qwen/Qwen3-8B-Base"
    
    # Memory optimizations
    enable_gradient_checkpointing: true
    use_remove_padding: true
    
  actor:
    # DAPO settings
    clip_ratio_low: 0.2
    clip_ratio_high: 0.28
    
    # Optimization
    optim:
      lr: 1.0e-6
      weight_decay: 0.1
      warmup_steps: 10
    
    # Memory management
    fsdp_config:
      param_offload: true
      optimizer_offload: true
    
    # Batch sizes
    ppo_mini_batch_size: 2
    use_dynamic_bsz: true
  
  rollout:
    # vLLM configuration
    name: vllm
    mode: async
    tensor_model_parallel_size: 2
    
    # Rollout settings
    n: 8
    temperature: 1.0
    top_p: 1.0
    
    # Multi-turn tool calling
    multi_turn:
      enable: true
      max_user_turns: 16
      max_assistant_turns: 16
      tool_config_path: configs/tool_config.yaml

# Data configuration
data:
  train_files: "data/customer_service_train.parquet"
  val_files: "data/customer_service_val.parquet"
  train_batch_size: 8
  max_prompt_length: 2048
  max_response_length: 8192

# Trainer settings
trainer:
  project_name: "dual-lora-world-model"
  experiment_name: "qwen3-8b-customer-service"
  n_gpus_per_node: 8
  nnodes: 1
  total_epochs: 1
  total_training_steps: 500
  val_before_train: false
  test_freq: 10
  save_freq: 20
```

## Training Script

**File**: `configs/run_dual_lora_dapo.sh`

```bash
#!/bin/bash
set -x

# Project configuration
project_name='dual-lora-world-model'
exp_name='qwen3-8b-customer-service'

# Paths
MODEL_PATH=${MODEL_PATH:-"Qwen/Qwen3-8B-Base"}
TRAIN_FILE="data/customer_service_train.parquet"
VAL_FILE="data/customer_service_val.parquet"
TOOL_CONFIG="configs/tool_config.yaml"
CKPT_DIR="checkpoints/${exp_name}"

# DAPO algorithm settings
adv_estimator=grpo
clip_ratio_low=0.2
clip_ratio_high=0.28

# Batch configuration
train_batch_size=8
n_resp_per_prompt=8
ppo_mini_batch_size=2

# Sequence lengths
max_prompt_length=2048
max_response_length=8192

# LoRA configuration
lora_rank=16
lora_alpha=32
target_modules="all-linear"

# NEW: Dual-LoRA and world model settings
use_dual_lora=True
world_model_enable=True
world_model_loss_weight=0.5
world_model_predict_tool="make_phone_call"

# Performance settings
infer_tp=2                # vLLM tensor parallel
train_sp=2                # Sequence parallel for training
offload=True              # Critical for 24GB GPUs

# Launch training
python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=$adv_estimator \
    +algorithm.world_model.enable=$world_model_enable \
    +algorithm.world_model.loss_weight=$world_model_loss_weight \
    +algorithm.world_model.predict_tool=$world_model_predict_tool \
    data.train_files=$TRAIN_FILE \
    data.val_files=$VAL_FILE \
    data.train_batch_size=$train_batch_size \
    data.max_prompt_length=$max_prompt_length \
    data.max_response_length=$max_response_length \
    data.custom_cls.path=src/training/dataset.py \
    data.custom_cls.name=CustomerServiceDataset \
    custom_reward_function.path=src/training/reward.py \
    custom_reward_function.name=compute_score \
    actor_rollout_ref.model.path=$MODEL_PATH \
    +actor_rollout_ref.model.use_dual_lora=$use_dual_lora \
    actor_rollout_ref.model.lora_rank=$lora_rank \
    actor_rollout_ref.model.lora_alpha=$lora_alpha \
    actor_rollout_ref.model.target_modules=$target_modules \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.clip_ratio_low=$clip_ratio_low \
    actor_rollout_ref.actor.clip_ratio_high=$clip_ratio_high \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=$ppo_mini_batch_size \
    actor_rollout_ref.actor.fsdp_config.param_offload=$offload \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=$offload \
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=$train_sp \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.mode=async \
    actor_rollout_ref.rollout.tensor_model_parallel_size=$infer_tp \
    actor_rollout_ref.rollout.n=$n_resp_per_prompt \
    actor_rollout_ref.rollout.temperature=1.0 \
    actor_rollout_ref.rollout.multi_turn.enable=True \
    actor_rollout_ref.rollout.multi_turn.max_user_turns=16 \
    actor_rollout_ref.rollout.multi_turn.max_assistant_turns=16 \
    actor_rollout_ref.rollout.multi_turn.tool_config_path=$TOOL_CONFIG \
    trainer.project_name=$project_name \
    trainer.experiment_name=$exp_name \
    trainer.n_gpus_per_node=8 \
    trainer.nnodes=1 \
    trainer.total_training_steps=500 \
    trainer.test_freq=10 \
    trainer.save_freq=20 \
    trainer.default_local_dir=$CKPT_DIR
```

## Implementation Strategy: Custom Trainer Class

**Create**: `src/training/dual_lora_trainer.py`

**Inherit from**: `verl.trainer.ppo.ray_trainer.RayPPOTrainer`

**Override key methods**:
- `setup_model()`: Initialize dual-LoRA adapters
- `compute_actor_loss()`: Add world model auxiliary loss
- `evaluate()`: Add world model prediction metrics

**Advantages**:
- ✅ Clean separation from verl core code
- ✅ Easy to customize and extend
- ✅ Works with verl updates (no core modifications)
- ✅ Better for experimentation and debugging
- ✅ Can be released as standalone extension

## Custom Components Required

### Component 1: Dataset Preprocessor

**File**: `src/training/dataset.py`

**Purpose**: Convert customer service tasks to verl format

```python
from verl.utils.dataset import RLHFDataset
import datasets

class CustomerServiceDataset(RLHFDataset):
    """
    Load customer service tasks and format for verl.
    """
    
    def map_fn(self, row):
        """
        Convert task to verl format.
        """
        return {
            "prompt": [{
                "role": "user",
                "content": self.format_task_prompt(row)
            }],
            "data_source": "customer_service",
            "ability": "TOOL_USE",
            "reward_model": {
                "company": row["company"],
                "user_profile": row["user_profile"],
                "task": row["task"],
                "success_criteria": row["success_criteria"]
            },
            "agent_name": "tool_agent"
        }
    
    def format_task_prompt(self, row):
        return f"""You need to help with: {row['task']}

Company: {row['company']}

You have these tools:
1. search_company: Find departments and phone numbers
2. auth_info_form: Collect authentication (call ONCE with all fields)
3. make_phone_call: Call a department with authentication

Complete the task efficiently."""
```

### Component 2: Reward Function

**File**: `src/training/reward.py`

**Purpose**: Compute rewards from task execution

```python
def compute_score(data_source, solution_str, ground_truth, extra_info):
    """
    Compute task success reward.
    
    Note: This is only for policy learning (extrinsic reward).
    World model has separate loss (CSR prediction).
    """
    trajectory = extra_info.get("trajectory", [])
    
    # Check if task completed successfully
    task_success = check_completion(trajectory, ground_truth)
    
    if task_success:
        score = 1.0
    else:
        # Partial credit
        score = compute_partial_reward(trajectory, ground_truth)
    
    return {
        "score": score,
        "pred": extract_result(solution_str),
        "num_turns": len(trajectory),
        # Store trajectory for world model extraction
        "trajectory": trajectory
    }

def compute_partial_reward(trajectory, ground_truth):
    """
    Partial credit based on progress.
    """
    score = 0.0
    
    # Collected authentication
    if has_collected_auth(trajectory):
        score += 0.3
    
    # Successfully authenticated
    if has_authenticated(trajectory):
        score += 0.2  # Total 0.5
    
    # Reached correct department
    if reached_correct_dept(trajectory):
        score += 0.2  # Total 0.7
    
    # Penalties
    if called_auth_form_multiple_times(trajectory):
        score -= 0.1
    
    return max(0.0, score)
```

### Component 3: World Model Loss Function

**File**: `src/training/world_model_loss.py`

**Purpose**: Extract phone call tuples and compute prediction loss

```python
import torch
import torch.nn.functional as F

def extract_phone_call_sao_tuples(batch_data):
    """
    Extract (state, action, observation) tuples for phone calls.
    
    Args:
        batch_data: Batch from verl rollout
        
    Returns:
        List of (state_str, action_str, csr_response_str) tuples
    """
    sao_tuples = []
    
    for trajectory in batch_data.trajectories:
        # Build state context incrementally
        state_context = {
            "task": trajectory.task,
            "step": 0,
            "history": []
        }
        
        for turn in trajectory.turns:
            if turn.tool_name == "make_phone_call":
                # Extract state before this call
                state_str = format_state(state_context)
                
                # Extract action (phone call parameters)
                action_str = format_action(turn.tool_call)
                
                # Extract observation (CSR response)
                csr_response = turn.tool_response.get("message", "")
                
                sao_tuples.append((state_str, action_str, csr_response))
            
            # Update state for next turn
            state_context["step"] += 1
            state_context["history"].append({
                "tool": turn.tool_name,
                "result": summarize_result(turn.tool_response)
            })
    
    return sao_tuples

def compute_world_model_loss_from_tuples(
    model,
    tokenizer,
    sao_tuples,
    device
):
    """
    Compute cross-entropy loss for CSR response prediction.
    """
    if len(sao_tuples) == 0:
        return torch.tensor(0.0, device=device)
    
    losses = []
    
    for state, action, csr_response in sao_tuples:
        # Format input
        input_text = f"{state}\n{action}\n<|predict_csr|>"
        target_text = f"<|csr|>{csr_response}<|/csr|>"
        
        # Tokenize
        input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)
        target_ids = tokenizer.encode(target_text, return_tensors="pt").to(device)
        
        # Concatenate for teacher forcing
        full_input_ids = torch.cat([input_ids, target_ids], dim=-1)
        
        # Forward pass
        outputs = model(full_input_ids)
        logits = outputs.logits
        
        # Compute loss only on target tokens
        shift_logits = logits[:, input_ids.size(1)-1:-1, :]
        shift_labels = target_ids[:, 1:]
        
        loss = F.cross_entropy(
            shift_logits.reshape(-1, shift_logits.size(-1)),
            shift_labels.reshape(-1),
            reduction='mean'
        )
        
        losses.append(loss)
    
    return torch.stack(losses).mean()
```

## Rollout Worker Considerations

### vLLM LoRA Loading

**Challenge**: vLLM needs policy LoRA for inference, but not world model LoRA

**Solution**: Only synchronize policy adapter

```python
# In ActorRolloutRefWorker.update_rollout_weights()

def update_rollout_weights(self):
    """
    Synchronize policy LoRA (not world model) to vLLM.
    """
    # Get only policy adapter weights
    policy_lora_state_dict = get_adapter_state_dict(
        self.actor_module, 
        adapter_name="policy"
    )
    
    # Synchronize to vLLM rollout workers
    self.rollout_worker.update_weights(
        weights=policy_lora_state_dict.items(),
        peft_config=self.policy_lora_config,
        base_sync_done=True  # Base model already loaded
    )
```

**Benefits**:
- World model LoRA stays on training workers only
- Reduces memory on vLLM workers
- Faster synchronization (only one adapter)

## Monitoring and Logging

### WandB Integration

**Metrics to Log**:

```python
Per training step:
  # Loss components
  - train/policy_loss
  - train/world_model_loss
  - train/total_loss
  - train/wm_weight_contribution  # λ * wm_loss / total_loss
  
  # World model quality
  - train/wm_prediction_accuracy
  - train/wm_perplexity
  
  # Policy performance
  - train/average_reward
  - train/success_rate (if deterministic tasks)

Every 10 steps (validation):
  # Policy evaluation
  - val/success_rate
  - val/success_by_level (for each difficulty)
  
  # World model evaluation  
  - val/wm_accuracy
  - val/wm_bleu_score
  
  # Sample efficiency
  - efficiency/tasks_seen
  - efficiency/success_at_N_tasks
```

**Example Prediction Logging**:

```python
Every 50 steps, log examples to WandB:

for i in range(5):  # 5 examples
    state, action, actual_csr, predicted_csr = get_prediction_example(i)
    
    wandb.log({
        f"predictions/example_{i}": wandb.Html(f"""
        <h3>State:</h3>
        <pre>{state}</pre>
        
        <h3>Action:</h3>
        <pre>{action}</pre>
        
        <h3>Actual CSR:</h3>
        <pre style="color: green">{actual_csr}</pre>
        
        <h3>Predicted CSR:</h3>
        <pre style="color: blue">{predicted_csr}</pre>
        
        <h3>Match:</h3>
        <pre>{compare_semantic_match(actual_csr, predicted_csr)}</pre>
        """)
    })
```

## Checkpointing

### What to Save

**Checkpoint Contents**:
```python
checkpoint = {
    # Base model (same across all checkpoints, can be skipped)
    "base_model_path": "Qwen/Qwen3-8B-Base",
    
    # Policy LoRA (needed for inference and continuation)
    "policy_lora_state_dict": model.get_adapter_state_dict("policy"),
    
    # World model LoRA (needed for continuation, not inference)
    "world_model_lora_state_dict": model.get_adapter_state_dict("world_model"),
    
    # Optimizer (both LoRAs)
    "optimizer_state_dict": optimizer.state_dict(),
    
    # Training state
    "step": current_step,
    "config": config,
    "metrics": latest_metrics
}
```

### Loading for Inference

**For deployment** (only need policy):

```python
# Load base model
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B-Base")

# Load only policy adapter
policy_config = LoraConfig(...)
model = get_peft_model(model, policy_config, adapter_name="policy")
model.load_adapter_weights(checkpoint["policy_lora_state_dict"])

# World model LoRA not needed for inference
```

### Loading for Training Continuation

**Resume training**:

```python
# Load base model
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B-Base")

# Load both adapters
model = get_peft_model(model, policy_config, adapter_name="policy")
model.add_adapter("world_model", world_model_config)

# Load adapter weights
model.load_adapter_weights(checkpoint["policy_lora_state_dict"], "policy")
model.load_adapter_weights(checkpoint["world_model_lora_state_dict"], "world_model")

# Load optimizer
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

# Resume from step
start_step = checkpoint["step"] + 1
```

## Ray Cluster Configuration

### Single Node Setup (8 GPUs)

**Requirements**:
- Ray 2.0+
- CUDA 12.1+
- PyTorch 2.0+

**Start Ray Cluster**:
```bash
# Start Ray head
ray start --head --port=8265

# Verify cluster
ray status
```

**Environment Variables**:
```bash
export RAY_ADDRESS="http://localhost:8265"
export VLLM_USE_V1=1
export TOKENIZERS_PARALLELISM=true
export NCCL_DEBUG=WARN
```

### Multi-Node Setup (if scaling beyond 8 GPUs)

**Not needed for initial experiments**, but for reference:

```bash
# Head node
ray start --head --port=8265 --num-gpus=8

# Worker nodes
ray start --address=<head_ip>:8265 --num-gpus=8
```

## Debugging Tools

### LoRA Adapter Inspection

**Verify both adapters loaded**:
```python
# In training script or notebook
print("Active adapter:", model.active_adapter)
print("Available adapters:", model.peft_config.keys())

# Should output:
# Active adapter: policy
# Available adapters: dict_keys(['policy', 'world_model'])
```

**Check adapter parameters**:
```python
policy_params = sum(p.numel() for p in model.get_adapter_params("policy"))
wm_params = sum(p.numel() for p in model.get_adapter_params("world_model"))

print(f"Policy LoRA parameters: {policy_params:,}")
print(f"World Model LoRA parameters: {wm_params:,}")

# Should output around 10M each
```

**Verify gradient flow**:
```python
# After backward pass
policy_grad_norm = 0
wm_grad_norm = 0

for name, param in model.named_parameters():
    if param.grad is not None:
        if "policy" in name:
            policy_grad_norm += param.grad.norm().item() ** 2
        elif "world_model" in name:
            wm_grad_norm += param.grad.norm().item() ** 2

policy_grad_norm = policy_grad_norm ** 0.5
wm_grad_norm = wm_grad_norm ** 0.5

print(f"Policy gradient norm: {policy_grad_norm:.4f}")
print(f"World model gradient norm: {wm_grad_norm:.4f}")
print(f"Ratio: {policy_grad_norm / wm_grad_norm:.2f}")

# Should see both have gradients
# Ratio should be 0.3-3.0 (similar magnitude)
```

### Trajectory Inspection

**Save sample trajectories**:
```python
# Every 50 steps, save 10 trajectories
if step % 50 == 0:
    save_trajectories(
        trajectories=batch.trajectories[:10],
        path=f"diagnostics/step_{step}/trajectories.pkl"
    )
```

**Inspect world model predictions**:
```python
# Load trajectory
trajectory = load_trajectory("diagnostics/step_100/traj_0.pkl")

# For each phone call
for turn in trajectory:
    if turn.tool == "make_phone_call":
        # Get world model prediction
        predicted = world_model.predict(turn.state, turn.action)
        actual = turn.observation.message
        
        print(f"\n=== Phone Call ===")
        print(f"State: {turn.state}")
        print(f"Action: {turn.action}")
        print(f"\nPredicted CSR: {predicted}")
        print(f"Actual CSR: {actual}")
        print(f"Match: {compute_similarity(predicted, actual)}")
```

## Performance Optimization

### Memory Optimization

**Already configured in training script**:
```bash
# Essential for 24GB GPUs
param_offload=True           # Offload parameters during optimizer step
optimizer_offload=True       # Offload optimizer states to CPU
enable_gradient_checkpointing=True  # Recompute activations
use_remove_padding=True      # Remove padding for efficiency
```

**If still OOM**:
```bash
# Reduce batch sizes
train_batch_size=6           # Down from 8
n_resp_per_prompt=6          # Down from 8

# Reduce sequence length
max_response_length=6144     # Down from 8192

# Increase sequence parallelism
train_sp=4                   # Up from 2 (if model supports)
```

### Speed Optimization

**Faster training**:
```bash
# Use flash attention
# (Usually enabled by default in recent transformers)

# Disable unnecessary logging
trainer.log_val_generations=0

# Reduce validation frequency
trainer.test_freq=20          # Down from 10

# Enable async rollout
actor_rollout_ref.rollout.mode=async
```

**Faster rollout generation**:
```bash
# Increase tensor parallelism if memory allows
infer_tp=4                    # Up from 2 (uses 4 GPUs for vLLM)

# Enable continuous batching (vLLM V1)
export VLLM_USE_V1=1

# Optimize GPU memory utilization
actor_rollout_ref.rollout.gpu_memory_utilization=0.95
```

## Testing Strategy

### Unit Tests

**Test dual-LoRA initialization**:
```bash
pytest tests/test_dual_lora_init.py
```

**Test world model loss computation**:
```bash
pytest tests/test_world_model_loss.py
```

**Test combined training step**:
```bash
pytest tests/test_training_step.py
```

### Integration Tests

**Test with small model (Qwen-0.5B)**:
```bash
# Quick test with tiny model
bash configs/test_dual_lora_qwen0.5b.sh

# Should complete in 10 minutes
# Verify both LoRAs update
# Verify no OOM
```

**Test with full environment**:
```bash
# Generate small test dataset (10 tasks)
python scripts/generate_test_data.py --num_tasks 10

# Run 10 training steps
bash configs/test_dual_lora_10steps.sh

# Verify:
# - Both losses decrease
# - World model makes reasonable predictions
# - Policy generates valid tool calls
```

## Baseline Comparison Script

**File**: `scripts/compare_to_baseline.sh`

```bash
#!/bin/bash

# Run baseline DAPO
echo "Running baseline DAPO..."
bash configs/run_baseline_dapo.sh > logs/baseline.log 2>&1

# Run dual-LoRA DAPO
echo "Running dual-LoRA DAPO..."
bash configs/run_dual_lora_dapo.sh > logs/dual_lora.log 2>&1

# Compare results
python scripts/compare_results.py \
    --baseline logs/baseline.log \
    --dual_lora logs/dual_lora.log \
    --output analysis/comparison.md
```

## Implementation Checklist

### Files to Create

**Training Infrastructure**:
```
src/training/
├── dual_lora_trainer.py       # Custom trainer class (extends RayPPOTrainer)
├── main_dual_lora.py          # Training entry point
├── dataset.py                 # CustomerServiceDataset
├── reward.py                  # compute_score function
└── world_model_utils.py       # Helper functions for WM loss
```

**Environment & Tools**:
```
src/environment/
├── user_simulator.py          # User form responses
├── company_directory.py       # Department database
├── phone_system.py            # CSR simulator
└── task_generator.py          # Generate training tasks

src/tools/
├── auth_info_form_tool.py     # Tool 1
├── company_directory_tool.py  # Tool 2
└── phone_call_tool.py         # Tool 3
```

**Configuration**:
```
configs/
├── dual_lora_config.yaml      # Hydra config
├── tool_config.yaml           # Tool schemas
└── run_dual_lora_dapo.sh      # Launch script
```

### Implementation Steps

**Step 1: Environment Setup** (Day 1-2)
```bash
# Generate data
python src/environment/task_generator.py

# Test environment
python tests/test_environment.py

# Verify tools work
python tests/test_tools.py
```

**Step 2: Custom Trainer** (Day 3-4)
```bash
# Implement DualLoRADAPOTrainer
# - setup_model() for dual-LoRA
# - compute_actor_loss() for combined loss
# - Helper methods for SAO extraction

# Test trainer initialization
python tests/test_trainer_init.py
```

**Step 3: Integration Test** (Day 5)
```bash
# Small scale test (10 tasks, 10 steps)
python -m src.training.main_dual_lora \
    data.train_files=data/test_10tasks.parquet \
    trainer.total_training_steps=10

# Verify:
# - Both LoRAs initialized
# - Both losses computed
# - No crashes, no OOM
```

**Step 4: Full Training** (Day 6-7)
```bash
# Launch full training run
bash configs/run_dual_lora_dapo.sh

# Monitor via WandB
# Wait for completion (~2.5 hours)
```

**Step 5: Evaluation** (Day 8)
```bash
# Run evaluation on test set
python scripts/evaluate.py \
    --checkpoint checkpoints/final \
    --test_data data/test_tasks.parquet

# Compare to baseline
python scripts/compare_to_baseline.py
```

### Key Integration Points with verl

**1. Custom Trainer Entry Point**:
- Replace `python3 -m verl.trainer.main_ppo`
- With `python3 -m src.training.main_dual_lora`
- Inherits all verl functionality + adds world model loss

**2. LoRA Adapter Management**:
- verl loads single LoRA via PEFT
- Custom trainer adds second LoRA in `setup_model()`
- Both managed through PEFT's multi-adapter API

**3. Loss Computation Hook**:
- verl calls `compute_actor_loss()` during training
- Custom trainer overrides to add world model loss
- Returns combined loss for backward pass

**4. Rollout Synchronization**:
- verl syncs LoRA weights to vLLM
- Works automatically (vLLM sees "policy" adapter)
- World model adapter stays on training workers

### No verl Core Modifications Needed

**What you DON'T need to change**:
- ❌ verl/workers/*.py (no modifications)
- ❌ verl/trainer/*.py (no modifications)
- ❌ verl/models/*.py (no modifications)

**What you DO need to create**:
- ✅ Custom trainer class (inherits from verl)
- ✅ Custom training entry point
- ✅ Standard dataset and reward functions
- ✅ Environment and tools (domain-specific)

## Summary

The verl integration for dual-LoRA world model learning is **clean and non-invasive**:

**Architecture**:
- Custom trainer class extends `RayPPOTrainer`
- Adds world model LoRA via PEFT multi-adapter
- Computes combined loss (policy + world model)
- Single backward pass updates both LoRAs

**Implementation Effort**:
- Main file: `dual_lora_trainer.py` (~300 lines)
- Helper utilities: ~200 lines
- Configuration: ~100 lines YAML
- Total: ~600 lines of new code

**Benefits**:
- ✅ No verl core modifications required
- ✅ Works with future verl updates
- ✅ Easy to maintain and extend
- ✅ Can be released as standalone plugin
- ✅ Simple to disable (set `world_model.enable=False`)

The custom trainer approach provides maximum flexibility while maintaining compatibility with verl's infrastructure.

