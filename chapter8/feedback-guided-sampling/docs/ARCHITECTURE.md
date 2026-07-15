# System Architecture

## Overview

This document describes the architecture of the Feedback-Guided DAPO system for sample-efficient reinforcement learning in multi-turn tool-use scenarios.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Training Controller                      │
│                    (Ray Task Runner)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   Rollout    │ │  Actor   │ │  Reference   │
│   Worker     │ │  Worker  │ │   Worker     │
│   (vLLM)     │ │  (FSDP)  │ │   (FSDP)     │
└──────┬───────┘ └────┬─────┘ └──────┬───────┘
       │              │               │
       ▼              ▼               ▼
┌──────────────────────────────────────────┐
│        Simulation Environment            │
│  ┌────────┐ ┌──────────┐ ┌───────────┐ │
│  │  User  │ │ Company  │ │   Phone   │ │
│  │Simulate│ │ Directory│ │  System   │ │
│  └────────┘ └──────────┘ └───────────┘ │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│       Feedback Generation System         │
│  ┌──────────────┐   ┌─────────────────┐ │
│  │ Rule-based   │   │  LLM-based      │ │
│  │ Feedback     │ + │  Critique       │ │
│  └──────────────┘   └─────────────────┘ │
└──────────────────────────────────────────┘
```

## Component Details

### 1. Training Controller (Ray Task Runner)

**Responsibility**: Orchestrates the entire training loop.

**Key Functions**:
- Initialize worker groups (rollout, actor, reference)
- Manage data loading and batching
- Coordinate feedback-guided rollout generation
- Trigger GRPO updates
- Handle checkpointing and logging

**Implementation**: Extends `RayDAPOTrainer` from verl.

### 2. Rollout Worker (vLLM-based)

**Responsibility**: Generate model responses using vLLM for fast inference.

**Configuration**:
- Tensor Parallel: 2 GPUs
- Max sequence length: 10K tokens (prompt + response)
- Supports multi-turn tool calling
- Async execution for throughput

**Key Features**:
- Function calling format (Hermes or similar)
- Tool schema injection
- Multi-turn conversation management

### 3. Actor Worker (FSDP Training)

**Responsibility**: The main policy model being trained.

**Configuration**:
- FSDP with 6-8 GPUs
- Sequence Parallel: 2-way
- Gradient Checkpointing: Enabled
- Optimizer Offloading: Enabled (critical for 24GB GPUs)

**Training Details**:
- Learning rate: 1e-6
- Gradient clipping: 1.0
- Loss aggregation: Token-mean (DAPO's token-level loss)
- Clip ratios: ε_low=0.2, ε_high=0.28

### 4. Reference Worker (FSDP Frozen)

**Responsibility**: Compute reference log probabilities for KL penalty (optional in DAPO).

**Configuration**:
- Same sharding as Actor
- Frozen weights (no training)
- Parameter offloading: Enabled

### 5. Simulation Environment

Three interconnected simulators that provide realistic task execution.

#### 5.1 User Simulator

**Purpose**: Simulates user providing authentication information via form submission.

**Implementation**:
```python
class UserSimulator:
    def __init__(self):
        self.user_profiles = {}  # Maps instance_id -> profile
        self.behavior_types = {
            "cooperative": 0.7,      # Provides all info clearly
            "partial_info": 0.2,     # Missing some fields
            "difficult": 0.1         # Provides wrong info first
        }
    
    def fill_auth_form(self, instance_id: str, requested_fields: List[str]) -> dict:
        """
        Respond to auth_info_form request with JSON containing all requested fields.
        
        Args:
            instance_id: User instance ID
            requested_fields: List of field names requested (e.g., ["account_number", "last_4_ssn"])
        
        Returns:
            JSON dict with field values and unavailable list
        """
        profile = self.user_profiles[instance_id]
        behavior = self._sample_behavior()
        
        response = {}
        unavailable = []
        
        for field in requested_fields:
            if field not in profile or behavior == "partial_info" and random.random() < 0.3:
                # User doesn't have this field
                unavailable.append(field)
            elif behavior == "difficult" and random.random() < 0.2:
                # Provide wrong info initially (realistic - user misremembering)
                response[field] = self._generate_wrong_value(field)
            else:
                # Normal case: provide correct value
                response[field] = profile[field]
        
        return {
            **response,
            "unavailable": unavailable
        }
```

**Data**:
- 500+ user profiles with complete auth information
- Variations: 80% complete profiles, 15% missing one field, 5% missing multiple
- Realistic field names: account_number, last_4_ssn, date_of_birth, last_4_cc, billing_zip, etc.

#### 5.2 Company Directory

**Purpose**: Provides department information and requirements.

**Schema**:
```python
@dataclass
class Department:
    name: str
    phone: str
    description: str  # e.g., "Customer Service - Account inquiries and general support"
    routing_rules: Optional[Dict[str, str]]  # Prerequisites or transfers (e.g., "must_call_first": "Customer Service")

@dataclass
class Company:
    name: str
    departments: List[Department]
    operating_hours: str
```

**Key Design Decision**: The directory does **NOT** include `auth_required` fields. The agent must:
- Learn from CSR responses what authentication each department needs
- Build implicit knowledge through training (e.g., "Customer Service usually needs account_number and last_4_ssn")
- Use feedback from failed attempts to succeed on retry

**Database**:
- 100 companies
- 2-5 departments per company
- Realistic routing dependencies (e.g., must go through CS first)

#### 5.3 Phone System Simulator

**Purpose**: Simulates CSR (Customer Service Representative) interactions.

**Workflow**:
```python
class PhoneSystemSimulator:
    def handle_call(self, phone: str, auth_info: dict) -> CallResult:
        dept = self.directory.lookup(phone)
        
        # Phase 1: Authentication
        auth_result = self._authenticate(dept, auth_info)
        if not auth_result.success:
            return CallResult(
                status="auth_failed",
                message=auth_result.error_message,
                step_reward=-0.2,
                feedback=self._generate_auth_feedback(auth_result)
            )
        
        # Phase 2: Routing Check
        routing_result = self._check_routing(dept, call_history)
        if not routing_result.valid:
            return CallResult(
                status="wrong_routing",
                message=routing_result.message,
                step_reward=-0.1,
                feedback=self._generate_routing_feedback(routing_result)
            )
        
        # Phase 3: Service
        service_result = self._handle_service(dept, request)
        return CallResult(
            status="success",
            message=service_result.message,
            step_reward=1.0,
            feedback=None
        )
```

**Realism Features**:
- Natural language CSR responses
- Varied phrasing for same authentication requests
- Hold times (simulated delays)
- Transfer scenarios

### 6. Feedback Generation System

**Purpose**: Convert failures into actionable critiques for next rollouts.

**Two-Stage Architecture**:

#### Stage 1: Rule-Based Feedback (Fast, Deterministic)

```python
def generate_rule_based_feedback(failure_info: FailureInfo) -> str:
    """Generate feedback using templates and rules."""
    
    if failure_info.type == "missing_auth":
        missing_fields = failure_info.missing_fields
        return f"""The phone call to {failure_info.department} failed because the CSR said they need: {', '.join(missing_fields)}.

To fix this:
1. Use auth_info_form(fields={missing_fields}) to collect the required authentication
2. Then retry the call with complete authentication

IMPORTANT: auth_info_form should only be called ONCE. Make sure to request ALL fields needed.

NOTE: Company directories don't list auth requirements. You must learn what each 
department needs from CSR responses or prior experience."""
    
    elif failure_info.type == "wrong_department":
        return f"""You called {failure_info.called_dept} but they can't handle "{failure_info.request}".

According to the directory, you should call {failure_info.correct_dept} at {failure_info.correct_phone}."""
    
    elif failure_info.type == "wrong_order":
        return f"""You must call {failure_info.prerequisite_dept} first before accessing {failure_info.target_dept}.

Correct sequence:
1. Call {failure_info.prerequisite_dept}
2. Then call {failure_info.target_dept}"""
    
    elif failure_info.type == "incomplete_form":
        missing = failure_info.fields_not_requested
        return f"""You called auth_info_form but didn't request all required fields.

You requested: {failure_info.fields_requested}
But the department requires: {failure_info.fields_required}
Missing: {missing}

Call auth_info_form again with ALL required fields: {failure_info.fields_required}"""
    
    elif failure_info.type == "multiple_form_calls":
        return f"""ERROR: You called auth_info_form {failure_info.call_count} times.

auth_info_form should only be called ONCE per task.
Identify ALL required authentication fields from search_company results,
then call auth_info_form with the complete list of fields.

Penalty: -{failure_info.penalty} points for multiple calls."""
    
    # Add more templates...
```

#### Stage 2: LLM-Enhanced Feedback (Context-Aware, Natural)

```python
def generate_llm_feedback(trajectory: List[Turn], failure_info: FailureInfo) -> str:
    """Use Qwen3-8B to generate nuanced feedback."""
    
    # Start with rule-based feedback
    base_feedback = generate_rule_based_feedback(failure_info)
    
    # Enhance with LLM for context
    prompt = f"""You are helping an AI agent learn customer service phone calls.

Task: {trajectory.task_description}

Agent's actions:
{format_trajectory(trajectory)}

Failure: {failure_info.summary}

Base feedback: {base_feedback}

Enhance this feedback to be more specific and helpful based on what the agent actually did. Keep it under 100 tokens and actionable.

Enhanced feedback:"""
    
    # Call Qwen3-8B for enhancement
    enhanced = call_qwen_sync(prompt, max_tokens=100)
    
    return enhanced
```

**Quality Control**:
- Feedback must be specific (names exact fields/phones)
- Feedback must be actionable (tells what to do differently)
- Feedback must be concise (<100 tokens to fit in context)

### 7. Feedback-Guided Rollout Generation

**The Core Innovation**: Modified rollout loop that uses feedback from earlier rollouts.

```python
def generate_feedback_guided_batch(
    prompts: List[PromptData],
    n: int = 8
) -> List[RolloutData]:
    """
    Generate n rollouts per prompt with feedback guidance.
    
    Key: Later rollouts within same group see feedback from earlier failures.
    """
    all_rollouts = []
    
    for prompt_data in prompts:
        group_critiques = []  # Accumulate feedback for this prompt
        
        for rollout_idx in range(n):
            # Construct prompt for this rollout
            if rollout_idx == 0 or not group_critiques:
                # First rollout or no failures yet: use original prompt
                current_prompt = prompt_data.original_prompt
            else:
                # Subsequent rollout with failures: add feedback
                feedback_context = format_feedback_for_prompt(group_critiques)
                current_prompt = {
                    "role": "user",
                    "content": f"""{prompt_data.original_prompt}

<previous_attempts>
{feedback_context}
</previous_attempts>

Learn from the above mistakes and complete the task."""
                }
            
            # Generate response (multi-turn with tools)
            response, tools_used = await rollout_worker.generate(
                current_prompt,
                max_turns=16
            )
            
            # Execute in environment and get reward + feedback
            result = await environment.execute(
                response, 
                tools_used,
                prompt_data.ground_truth
            )
            
            # Store rollout data for training
            all_rollouts.append(RolloutData(
                prompt=current_prompt,
                response=response,
                reward=result.reward,
                tools_used=tools_used,
                extra_info=result.extra_info
            ))
            
            # If failed, extract feedback for next rollout in this group
            if result.reward < 1.0 and result.feedback:
                group_critiques.append({
                    "attempt": rollout_idx + 1,
                    "actions_taken": summarize_actions(tools_used),
                    "what_went_wrong": result.feedback,
                    "score": result.reward
                })
    
    return all_rollouts
```

**Prompt Formatting Example**:

```
Original Prompt:
"You need to check your account balance at Acme Bank. Use the tools to complete this task."

After Rollout 1 Fails:
"You need to check your account balance at Acme Bank. Use the tools to complete this task.

<previous_attempts>
Attempt 1 (Score: 0.0):
- You searched the company directory
- You called Customer Service (800-555-0100) without authentication
- The call failed: Missing authentication fields: account_number, last_4_ssn

Feedback: You must collect ALL required authentication information BEFORE calling.
Use auth_info_form to request: ["account_number", "last_4_ssn"] in a single call.
Do not call the phone until you have collected all required fields.
</previous_attempts>

Learn from the above mistake and complete the task."
```

## Data Flow

### Training Step Flow

```
1. Sample batch of prompts (e.g., 8 prompts)
   ↓
2. For each prompt, generate N rollouts (e.g., 8) with feedback guidance
   ↓
3. Batch has 8×8=64 rollouts total
   ↓
4. Compute advantages using GRPO (group-relative)
   ↓
5. Update actor with PPO loss (token-mean aggregation)
   ↓
6. Validation: Test base policy on held-out tasks (no feedback)
   ↓
7. Log metrics, save checkpoint
   ↓
8. Repeat
```

### Within-Group Rollout Flow

```
Prompt P
  │
  ├─→ Rollout 1: Generate(P) → Execute → R₁=0.0, F₁="missing auth"
  │
  ├─→ Rollout 2: Generate(P + F₁) → Execute → R₂=0.3, F₂="wrong dept"
  │
  ├─→ Rollout 3: Generate(P + F₁ + F₂) → Execute → R₃=1.0, F₃=None
  │
  ├─→ Rollout 4: Generate(P + F₁ + F₂) → Execute → R₄=1.0
  │
  └─→ ... (4 more rollouts)

GRPO Update: Uses all 8 rollouts
- Advantage: Compare within this group of 8
- Policy gradient pushes toward high-reward rollouts (3,4)
- Importantly: R₃ and R₄ were conditioned on feedback, but grad update improves base policy
```

## Memory Management

Critical for running on 8x RTX 4090 (24GB each).

### GPU Allocation

```
GPU 0-1: Rollout Worker (vLLM, TP=2)
  - Model shards: 8GB each
  - KV cache: 4GB each
  - Total: ~12GB per GPU ✓

GPU 2-7: Actor + Reference (FSDP, sharded)
  - Model shards: 2GB per GPU
  - Gradients: 2GB per GPU
  - Activations (with checkpointing): 8-10GB per GPU
  - FSDP overhead: 2-3GB per GPU
  - Optimizer states: OFFLOADED to CPU RAM
  - Total: ~15-17GB per GPU ✓

CPU RAM: ~64GB
  - Optimizer states: ~32GB
  - Data loading: ~8GB
  - Environment state: ~4GB
  - Buffers: ~20GB
```

### Memory Optimizations

1. **Gradient Checkpointing**: Recompute activations during backward pass
2. **Optimizer Offload**: Keep Adam states in CPU RAM
3. **Sequence Parallel**: Split long sequences across 2 GPUs
4. **Dynamic Batching**: Adjust batch size to fit available memory
5. **Selective Tool Execution**: Only load environment state when needed

## Evaluation System

### Metrics Tracked

**Sample Efficiency**:
- Success@N: % tasks solved within N training samples
- Tasks-to-70%: Number of training tasks to reach 70% success
- Tasks-to-90%: Number of training tasks to reach 90% success

**Learning Quality**:
- Base policy success: Success rate without any feedback (cold start)
- With-feedback success: Success rate after one failure + feedback
- First-rollout success: Success rate of rollout #1 in each group
- Last-rollout success: Success rate of rollout #8 in each group

**Behavioral**:
- Information gathering completeness: % tasks where all auth collected upfront
- Call order correctness: % multi-call tasks with correct sequence
- Tool call efficiency: Average number of tool calls per task
- Failure recovery: % of tasks that succeed after feedback vs. without

**System**:
- Training throughput: samples/hour
- GPU memory peak: max VRAM used
- Wall-clock time per epoch

### Evaluation Protocol

**Training Evaluation** (every 10 steps):
- 100 validation tasks
- No feedback (base policy only)
- Report success rate and average reward

**Held-out Evaluation** (end of training):
- 500 test tasks (unseen companies)
- Multiple conditions:
  - No feedback (base policy)
  - With feedback (one failure allowed)
  - Oracle (unlimited retries)

## Configuration Management

### Key Hyperparameters

**Algorithm**:
- `clip_ratio_low`: 0.2
- `clip_ratio_high`: 0.28
- `loss_agg_mode`: "token-mean"
- `enable_feedback_guidance`: True
- `feedback_start_rollout`: 2

**Batch Sizes**:
- `train_batch_size`: 8 prompts
- `n_resp_per_prompt`: 8 rollouts
- `ppo_mini_batch_size`: 2

**Model**:
- `model_path`: "Qwen/Qwen3-8B-Base"
- `max_prompt_length`: 2048
- `max_response_length`: 8192
- `enable_gradient_checkpointing`: True

**Performance**:
- `infer_tp`: 2
- `train_sp`: 2
- `offload`: True

## Extensibility

### Adding New Tools

Implement `BaseTool` interface:

```python
class MyCustomTool(BaseTool):
    async def execute(self, instance_id, parameters, **kwargs):
        # Your tool logic
        result = do_something(parameters)
        step_reward = compute_step_reward(result)
        metrics = extract_metrics(result)
        return ToolResponse(text=result), step_reward, metrics
```

### Adding New Task Types

Extend `RLHFDataset`:

```python
class MyTaskDataset(RLHFDataset):
    def map_fn(self, row):
        return {
            "prompt": format_task(row),
            "reward_model": {
                "ground_truth": row["answer"],
                "custom_field": row["metadata"]
            },
            "agent_name": "tool_agent"
        }
```

### Custom Feedback Generators

Implement feedback generation function:

```python
def my_feedback_generator(trajectory, failure_info, **kwargs):
    # Analyze failure
    # Generate specific feedback
    return feedback_text
```

## Monitoring & Debugging

### WandB Integration

Logs:
- Learning curves (success rate, reward)
- Within-group improvement (rollout 1 vs 8)
- Sample efficiency curves
- Tool usage statistics
- Feedback quality metrics

### Debug Mode

Enable with `DEBUG=True`:
- Save all trajectories
- Log feedback generation process
- Detailed environment state dumps
- Rollout-by-rollout breakdown

### Common Issues

**OOM during training**:
- Reduce `n_resp_per_prompt`
- Enable more aggressive gradient checkpointing
- Reduce `max_response_length`

**Poor feedback quality**:
- Check rule-based templates first
- Validate LLM feedback with human review
- Adjust feedback prompts

**No within-group improvement**:
- Check if feedback is reaching later rollouts
- Verify prompt formatting
- Ensure model can parse feedback context

## Future Extensions

1. **Hierarchical Feedback**: Task-level vs. tool-level critiques
2. **Meta-Learning**: Learn feedback generation policy
3. **Multi-Agent**: Multiple policies with different feedback strategies
4. **Transfer Learning**: Pre-train on simple tasks, transfer to complex ones
5. **Human-in-the-Loop**: Incorporate human feedback during training

