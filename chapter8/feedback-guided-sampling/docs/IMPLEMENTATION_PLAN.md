# Implementation Plan

## Timeline: 4 Weeks

This document provides a detailed week-by-week implementation plan for the Feedback-Guided DAPO project.

## Week 1: Environment & Data Infrastructure

### Day 1-2: Company Directory & User Profiles

**Goal**: Create realistic company and user data for simulation.

**Tasks**:

1. **Company Database Schema** (Day 1 Morning)
   - Define `Company`, `Department`, `RoutingRule` dataclasses
   - Implement JSON serialization/deserialization
   - Create database loader utility

2. **Generate Companies** (Day 1 Afternoon)
   - Script to generate 100 companies with 2-5 departments each
   - Realistic company names (banks, insurance, telecom, retail)
   - Department types: Customer Service, Billing, Technical Support, Sales, Fraud
   - Assign phone numbers, auth requirements, capabilities

3. **User Profile Generator** (Day 2 Morning)
   - Generate 500 unique user profiles
   - Fields: name, account_number, SSN, DOB, address, phone, credit_card_last4
   - Variations: 80% complete profiles, 15% missing one field, 5% missing multiple
   - Behavior patterns: 70% cooperative, 20% needs clarification, 10% difficult

4. **Task Generator** (Day 2 Afternoon)
   - Level 1: Single department, all info available (100 tasks)
   - Level 2: Single department, must collect 3-4 auth fields (150 tasks)
   - Level 3: Two departments with routing (150 tasks)
   - Level 4: Missing information edge cases (50 tasks)
   - Level 5: Complex 3+ department workflows (50 tasks)
   - Validation: 100 tasks across all levels

**Deliverables**:
- `data/companies.json`: 100 companies
- `data/user_profiles.json`: 500 user profiles
- `data/train_tasks.jsonl`: 500 training tasks
- `data/val_tasks.jsonl`: 100 validation tasks

**Validation**:
```bash
python -m src.environment.validate_data \
    --companies data/companies.json \
    --tasks data/train_tasks.jsonl
```

---

### Day 3-4: Environment Simulators

**Goal**: Implement the three core simulators.

**Tasks**:

1. **User Simulator** (Day 3 Morning)
   ```python
   # src/environment/user_simulator.py
   
   class UserSimulator:
       def respond(self, instance_id: str, question: str) -> str
       def _parse_question_intent(self, question: str) -> Tuple[str, str]
       def _cooperative_response(self, field: str, value: str) -> str
       def _clarification_response(self, field: str) -> str
       def _difficult_response(self, field: str) -> str
   ```
   
   - Implement intent extraction (what field is being asked?)
   - Generate natural language responses
   - Handle multi-turn conversations
   - Support "I don't have that" for missing fields

2. **Company Directory** (Day 3 Afternoon)
   ```python
   # src/environment/company_directory.py
   
   class CompanyDirectory:
       def search(self, company_name: str) -> CompanyInfo
       def lookup_phone(self, phone_number: str) -> Department
       def validate_auth_requirements(self, dept: Department, provided: dict) -> bool
   ```
   
   - Fuzzy company name matching
   - Phone number lookup
   - Auth requirement validation

3. **Phone System Simulator** (Day 4 Full Day)
   ```python
   # src/environment/phone_system.py
   
   class PhoneSystemSimulator:
       def handle_call(self, phone: str, auth_info: dict, context: dict) -> CallResult
       def _authenticate(self, dept: Department, auth_info: dict) -> AuthResult
       def _check_routing(self, dept: Department, call_history: List) -> RoutingResult
       def _provide_service(self, dept: Department, request: str) -> ServiceResult
       def _generate_csr_response(self, stage: str, result: dict) -> str
   ```
   
   - Multi-phase call handling (auth → routing → service)
   - Natural language CSR responses
   - Failure modes with specific error messages
   - Call history tracking for routing validation

**Deliverables**:
- `src/environment/user_simulator.py`
- `src/environment/company_directory.py`
- `src/environment/phone_system.py`

**Testing**:
```bash
# Unit tests
pytest tests/environment/

# Integration test: Can we complete a Level 1 task manually?
python tests/environment/test_full_workflow.py
```

---

### Day 5-7: Custom Tools & Reward Function

**Goal**: Implement the three agent tools and reward computation.

**Tasks**:

1. **AuthInfoFormTool** (Day 5 Morning)
   ```python
   # src/tools/auth_info_form_tool.py
   
   class AuthInfoFormTool(BaseTool):
       async def create(self, instance_id, user_profile, **kwargs)
       async def execute(self, instance_id, parameters, **kwargs)
       async def calc_reward(self, instance_id, **kwargs)
       async def release(self, instance_id, **kwargs)
   ```
   
   - Tool schema: `{"fields": ["account_number", "last_4_ssn", ...]}`
   - Returns JSON with all requested field values
   - Should only be called ONCE per task
   - Agent must identify ALL required fields before calling
   - Penalty if called multiple times

2. **CompanyDirectoryTool** (Day 5 Afternoon)
   ```python
   # src/tools/company_directory_tool.py
   
   class CompanyDirectoryTool(BaseTool):
       async def execute(self, instance_id, parameters, **kwargs)
   ```
   
   - Tool schema: `{"company_name": "string"}`
   - Returns JSON with department names, phone numbers, and descriptions
   - Does NOT include authentication requirements (agent must learn those)
   - No reward

3. **PhoneCallTool** (Day 6 Morning)
   ```python
   # src/tools/phone_call_tool.py
   
   class PhoneCallTool(BaseTool):
       async def execute(self, instance_id, parameters, **kwargs)
       async def calc_reward(self, instance_id, **kwargs)
   ```
   
   - Tool schema: `{"phone_number": "string", "auth_info": "object"}`
   - Calls PhoneSystemSimulator
   - Returns step reward (partial credit for correct auth)
   - Final reward computed in calc_reward

4. **Tool Configuration** (Day 6 Afternoon)
   ```yaml
   # configs/tool_config.yaml
   
   tools:
     - class_name: "src.tools.auth_info_form_tool.AuthInfoFormTool"
       tool_schema:
         type: "function"
         function:
           name: "auth_info_form"
           description: "Collect authentication information from the user. Call this ONCE with ALL required fields."
           parameters:
             type: "object"
             properties:
               fields:
                 type: "array"
                 items:
                   type: "string"
                 description: "List of authentication fields to collect (e.g., ['account_number', 'last_4_ssn'])"
             required: ["fields"]
     
     - class_name: "src.tools.company_directory_tool.CompanyDirectoryTool"
       tool_schema:
         type: "function"
         function:
           name: "search_company"
           description: "Search for company departments and phone numbers. Returns department names, phone numbers, and descriptions. Does NOT include authentication requirements - you must learn those from experience."
           parameters:
             type: "object"
             properties:
               company_name:
                 type: "string"
                 description: "Name of the company to search for"
             required: ["company_name"]
     
     - class_name: "src.tools.phone_call_tool.PhoneCallTool"
       tool_schema:
         type: "function"
         function:
           name: "make_phone_call"
           description: "Make a phone call to a department with authentication information"
           parameters:
             type: "object"
             properties:
               phone_number:
                 type: "string"
                 description: "Phone number to call"
               auth_info:
                 type: "object"
                 description: "Authentication information (e.g., {'account_number': '123456', 'last_4_ssn': '5678'})"
             required: ["phone_number", "auth_info"]
   ```

5. **Reward Function** (Day 7)
   ```python
   # src/training/reward.py
   
   def compute_score_with_feedback(
       data_source: str,
       solution_str: str,
       ground_truth: dict,
       extra_info: dict
   ) -> dict:
       """
       Compute reward AND generate feedback.
       
       Returns:
           {
               "score": float (0.0 to 1.0),
               "pred": str,
               "feedback": Optional[str],
               "partial_scores": dict
           }
       """
       pass
   
   def generate_failure_feedback(
       trajectory: List[Turn],
       ground_truth: dict,
       failure_info: FailureInfo
   ) -> str:
       """Generate actionable feedback from failure."""
       pass
   ```
   
   - Implement reward computation logic
   - Partial credit system:
     - 0.0: No progress
     - 0.2: Collected some auth info
     - 0.3: Collected all auth info
     - 0.5: Successfully authenticated
     - 0.7: Reached correct department
     - 1.0: Task completed
   
   - Implement feedback generation:
     - Rule-based templates for common failures
     - LLM enhancement (optional for Week 1)

**Deliverables**:
- `src/tools/auth_info_form_tool.py`
- `src/tools/company_directory_tool.py`
- `src/tools/phone_call_tool.py`
- `configs/tool_config.yaml`
- `src/training/reward.py`

**Testing**:
```bash
# Test each tool individually
pytest tests/tools/

# Test auth_info_form with single vs. multiple calls
python tests/tools/test_auth_info_form.py

# Test full agent workflow with tools
python tests/tools/test_tool_integration.py

# Manually verify reward computation
python tests/training/test_reward_function.py --visualize
```

---

## Week 2: Baseline DAPO Training

### Day 8-9: Dataset & DAPO Setup

**Goal**: Prepare data and configure baseline DAPO.

**Tasks**:

1. **Custom Dataset Class** (Day 8 Morning)
   ```python
   # src/training/dataset.py
   
   class CustomerServiceDataset(RLHFDataset):
       def _read_files_and_tokenize(self)
       def map_fn(self, row: dict) -> dict
   ```
   
   - Convert task data to verl format
   - Include all necessary metadata for reward computation
   - Validate data loading

2. **Ray Cluster Setup** (Day 8 Afternoon)
   - Install Ray
   - Configure single-node 8-GPU cluster
   - Test basic Ray operations
   - Set up WandB logging

3. **verl Installation & Configuration** (Day 9 Morning)
   ```bash
   cd projects/week7/verl
   pip install -e .
   
   # Install dependencies
   pip install vllm==0.8.3 flash-attn transformers datasets
   ```

4. **Baseline Config Script** (Day 9 Afternoon)
   ```bash
   # configs/run_baseline_dapo.sh
   
   # Key settings for baseline:
   # - enable_feedback_guidance=False  # No feedback in baseline
   # - train_batch_size=8
   # - n_resp_per_prompt=8
   # - Standard DAPO hyperparameters
   ```

**Deliverables**:
- `src/training/dataset.py`
- `configs/run_baseline_dapo.sh`
- Ray cluster operational
- verl installed and tested

---

### Day 10-14: Baseline Training Run

**Goal**: Train baseline DAPO and establish performance benchmarks.

**Tasks**:

1. **Launch Baseline Training** (Day 10)
   ```bash
   export RAY_ADDRESS="http://localhost:8265"
   bash configs/run_baseline_dapo.sh
   ```
   
   - Monitor GPU utilization
   - Verify memory usage stays under 24GB
   - Check training starts correctly

2. **Monitor Training** (Day 11-13)
   - Daily checkpoints
   - Log metrics to WandB:
     - Training loss
     - Validation success rate
     - Tool usage statistics
     - GPU memory peaks
   - Adjust batch sizes if OOM occurs

3. **Baseline Analysis** (Day 14)
   - Generate learning curves
   - Compute sample efficiency metrics
   - Analyze failure modes (what % of each error type?)
   - Identify which difficulty levels are hardest
   
   Expected baseline results:
   - Level 1: ~70% success
   - Level 2: ~25% success
   - Level 3: ~10% success
   - Overall: ~35% success

**Deliverables**:
- Trained baseline model checkpoint
- WandB training logs
- `experiments/baseline/analysis.md` with results
- Baseline metrics for comparison

---

## Week 3: Feedback-Guided Implementation

### Day 15-16: Feedback Generator

**Goal**: Implement high-quality feedback generation.

**Tasks**:

1. **Rule-Based Feedback Templates** (Day 15 Morning)
   ```python
   # src/training/feedback_generator.py
   
   FEEDBACK_TEMPLATES = {
       "missing_auth": """The phone call failed because you didn't provide required authentication.
   
   Required fields: {missing_fields}
   
   Next steps:
   1. Use ask_user to collect: {missing_fields}
   2. Then retry the call with complete auth info""",
       
       "wrong_department": """You called {called_dept} but they cannot handle "{request}".
   
   Correct department: {correct_dept} at {correct_phone}""",
       
       "wrong_order": """You must call {prerequisite} before accessing {target}.
   
   Correct sequence:
   1. Call {prerequisite}
   2. Complete that interaction
   3. Then call {target}""",
   }
   
   def generate_rule_based_feedback(failure_info: FailureInfo) -> str:
       template = FEEDBACK_TEMPLATES[failure_info.type]
       return template.format(**failure_info.details)
   ```

2. **LLM-Enhanced Feedback** (Day 15 Afternoon - Day 16)
   ```python
   def generate_llm_enhanced_feedback(
       trajectory: List[Turn],
       failure_info: FailureInfo,
       rule_based_feedback: str
   ) -> str:
       """Use Qwen3-8B to enhance feedback with context."""
       
       judge_prompt = f"""You are helping an AI agent learn.

Agent's task: {trajectory.task}

What the agent did:
{format_trajectory(trajectory, max_turns=5)}

What went wrong: {failure_info.summary}

Basic feedback: {rule_based_feedback}

Provide enhanced feedback that:
1. References specific actions the agent took
2. Explains WHY it failed
3. Gives concrete next steps
4. Stays under 100 tokens

Enhanced feedback:"""
       
       # Call Qwen synchronously (small batch)
       enhanced = call_qwen_for_feedback(judge_prompt)
       
       return enhanced
   ```
   
   - Implement Qwen inference for feedback generation
   - Add caching for common failure patterns
   - Quality control: validate feedback is actionable

**Deliverables**:
- `src/training/feedback_generator.py`
- Unit tests for each failure type
- Manual review of 50 generated feedbacks for quality

---

### Day 17-18: Feedback-Guided Trainer

**Goal**: Implement the core innovation - feedback-guided rollout generation.

**Tasks**:

1. **Custom Trainer Class** (Day 17)
   ```python
   # src/training/feedback_trainer.py
   
   class FeedbackGuidedDAPOTrainer(RayDAPOTrainer):
       def __init__(self, config):
           super().__init__(config)
           self.feedback_generator = FeedbackGenerator(config)
           self.feedback_config = config.algorithm.feedback_guidance
       
       def generate_training_batch(self, prompts):
           """Override to implement feedback guidance."""
           return self._generate_feedback_guided_batch(prompts)
       
       def _generate_feedback_guided_batch(self, prompts):
           all_rollouts = []
           
           for prompt_data in prompts:
               group_rollouts = self._generate_group_with_feedback(
                   prompt_data,
                   n=self.config.actor_rollout_ref.rollout.n
               )
               all_rollouts.extend(group_rollouts)
           
           return all_rollouts
       
       def _generate_group_with_feedback(self, prompt_data, n):
           rollouts = []
           critiques = []
           
           for i in range(n):
               # Construct prompt (original or with feedback)
               if i < self.feedback_config.start_rollout or not critiques:
                   current_prompt = prompt_data.original_prompt
               else:
                   current_prompt = self._augment_prompt_with_feedback(
                       prompt_data.original_prompt,
                       critiques
                   )
               
               # Generate and execute
               response = self.rollout_worker.generate(current_prompt)
               result = self.execute_tools(response, prompt_data)
               
               # Store rollout
               rollouts.append({
                   "prompt": current_prompt,
                   "response": response,
                   "reward": result.reward,
                   "extra_info": result.extra_info
               })
               
               # Extract feedback if failed
               if result.reward < 1.0 and result.feedback:
                   critiques.append({
                       "attempt": i + 1,
                       "feedback": result.feedback,
                       "score": result.reward
                   })
           
           return rollouts
   ```

2. **Prompt Augmentation** (Day 18 Morning)
   ```python
   def _augment_prompt_with_feedback(
       self, 
       original_prompt: str,
       critiques: List[dict]
   ) -> str:
       """Format feedback for inclusion in prompt."""
       
       feedback_section = "\n<previous_attempts>\n"
       for critique in critiques:
           feedback_section += f"""
Attempt {critique['attempt']} (Score: {critique['score']:.1f}):
{critique['feedback']}
"""
       feedback_section += "\n</previous_attempts>\n"
       
       augmented = f"""{original_prompt}

{feedback_section}

Learn from the previous attempts and complete the task correctly."""
       
       return augmented
   ```

3. **Config Extension** (Day 18 Afternoon)
   ```yaml
   # Add to config
   algorithm:
     feedback_guidance:
       enable: True
       start_rollout: 2  # Start adding feedback from rollout 2
       accumulation_mode: "all"  # all | last | summary
       max_feedback_tokens: 500
       use_llm_enhancement: True
   ```

**Deliverables**:
- `src/training/feedback_trainer.py`
- Modified config files
- Integration tests for feedback loop

---

### Day 19-21: Feedback-Guided Training Run

**Goal**: Train with feedback guidance and monitor improvement.

**Tasks**:

1. **Launch Feedback-Guided Training** (Day 19)
   ```bash
   bash configs/run_feedback_guided_dapo.sh
   ```
   
   - Start from same initialization as baseline (for fair comparison)
   - Monitor within-group improvement
   - Track feedback generation time

2. **Real-Time Monitoring** (Day 20-21)
   - Compare learning curves to baseline
   - Monitor key metrics:
     - Success rate by rollout position (1-8)
     - First-try success vs. with-feedback success
     - Sample efficiency (tasks to 70%)
   
   - Log feedback examples to WandB for qualitative review

3. **Early Analysis** (Day 21 Evening)
   - After ~100 training steps, preliminary analysis
   - Is within-group improvement visible?
   - Are later rollouts succeeding more?
   - Is base policy improving?

**Deliverables**:
- Training in progress (will complete during Week 4)
- Real-time metrics dashboard
- Preliminary results

---

## Week 4: Analysis & Iteration

### Day 22-23: Comprehensive Evaluation

**Goal**: Thorough evaluation on held-out test set.

**Tasks**:

1. **Test Set Evaluation** (Day 22)
   ```bash
   # Baseline model
   python src/evaluation/evaluate.py \
       --checkpoint experiments/baseline/final \
       --test_data data/test_tasks.jsonl \
       --output experiments/baseline/test_results.json
   
   # Feedback-guided model
   python src/evaluation/evaluate.py \
       --checkpoint experiments/feedback_guided/final \
       --test_data data/test_tasks.jsonl \
       --output experiments/feedback_guided/test_results.json
   ```
   
   - Evaluate both models on same 500 test tasks
   - Test in two modes:
     - **Cold start**: No feedback, base policy only
     - **With feedback**: Allow one failure + feedback

2. **Metrics Computation** (Day 22 Evening)
   ```python
   # src/evaluation/metrics.py
   
   def compute_all_metrics(results):
       return {
           "sample_efficiency": {
               "tasks_to_70": ...,
               "tasks_to_90": ...,
               "success@N": ...
           },
           "learning_quality": {
               "base_policy_success": ...,
               "with_feedback_success": ...,
               "improvement_from_feedback": ...
           },
           "behavioral": {
               "info_gathering_completeness": ...,
               "call_order_correctness": ...,
               "tool_call_efficiency": ...
           }
       }
   ```

3. **Failure Analysis** (Day 23)
   - Categorize all failures by type
   - Identify which types benefit most from feedback
   - Find failure modes that feedback doesn't help
   - Compare failure distributions between baseline and feedback-guided

**Deliverables**:
- `experiments/baseline/test_results.json`
- `experiments/feedback_guided/test_results.json`
- `experiments/analysis/failure_analysis.md`

---

### Day 24-25: Ablation Studies

**Goal**: Understand what components contribute to improvement.

**Ablations**:

1. **Feedback Timing**
   - Start feedback from rollout 1 vs. 2 vs. 4
   - Which is optimal?

2. **Feedback Quality**
   - Rule-based only
   - Rule-based + LLM enhancement
   - Full LLM generation
   - Compare quality and efficiency

3. **Feedback Accumulation**
   - Show all previous feedback
   - Show only last feedback
   - Show summary of feedback
   - Which works best?

4. **Training Mix**
   - 100% feedback-guided groups
   - 80% feedback, 20% clean
   - 50/50 mix
   - Effect on base policy learning

**Implementation**:
```bash
# Run each ablation (can parallelize on different GPU sets)
for config in feedback_timing_*.sh; do
    bash configs/ablations/$config
done
```

**Deliverables**:
- Results for each ablation
- `experiments/ablations/analysis.md`

---

### Day 26-28: Paper Preparation & Documentation

**Goal**: Document results and prepare for publication.

**Tasks**:

1. **Generate All Plots** (Day 26)
   - Learning curves (baseline vs. feedback-guided)
   - Sample efficiency comparison
   - Within-group improvement (rollout 1 vs. 8)
   - Success rate by difficulty level
   - Failure mode distributions
   - Ablation results

2. **Write Results Summary** (Day 27)
   ```markdown
   # experiments/RESULTS.md
   
   ## Main Results
   
   - Sample efficiency: 5.2x improvement (baseline needs 2400 tasks for 70%, 
     feedback-guided needs 460 tasks)
   - Base policy improvement: +18% absolute (45% → 63%)
   - Within-group improvement: Rollout 8 is 42% more successful than Rollout 1
   
   ## Key Findings
   
   1. Feedback helps most on Level 2-3 tasks (complex auth, multiple departments)
   2. Rule-based feedback is 85% as effective as LLM-enhanced (but 10x faster)
   3. Starting feedback from rollout 2 is optimal (allows exploration first)
   4. 80/20 feedback/clean mix is best for base policy learning
   
   ## Limitations
   
   - Doesn't help much on Level 5 tasks (too complex for single feedback cycle)
   - Requires good simulation environment (unrealistic feedback hurts)
   - 40% slower training due to feedback generation overhead
   ```

3. **Update Documentation** (Day 28)
   - Final README with results
   - Complete implementation guide
   - Known issues and future work
   - Usage examples

**Deliverables**:
- All plots and figures
- `experiments/RESULTS.md`
- Updated documentation
- Draft paper outline (if pursuing publication)

---

## Risk Mitigation

### If 8x RTX 4090 is Insufficient

**Symptoms**:
- OOM errors during training
- Unable to train with n=8 rollouts

**Solutions** (in order of preference):
1. Reduce `n_resp_per_prompt` to 6 or 4
2. Reduce `max_response_length` to 6144
3. Disable LLM feedback enhancement (use rule-based only)
4. Reduce training batch size to 4-6
5. **Fallback**: Rent cloud GPUs (H100 or A100 80GB)

### If Baseline Performance is Too Low

**Symptoms**:
- Baseline never reaches >40% success
- Model not learning tool use

**Solutions**:
1. Add small amount of SFT (100 expert demonstrations)
2. Adjust reward shaping (increase partial credit)
3. Simplify Level 1 tasks for initial learning
4. Increase training steps

### If Feedback Doesn't Help

**Symptoms**:
- No within-group improvement
- Feedback-guided model performs same as baseline

**Debugging**:
1. Manually inspect feedback quality (is it actionable?)
2. Verify feedback reaches later rollouts (logging)
3. Check if model can parse feedback format
4. Try more explicit feedback formatting

**Solutions**:
1. Improve feedback templates
2. Use more explicit formatting (numbered lists)
3. Add examples to feedback
4. Simplify feedback language

### If Training is Too Slow

**Symptoms**:
- <100 samples/hour
- Will take >2 weeks to complete

**Solutions**:
1. Disable LLM feedback enhancement
2. Reduce validation frequency
3. Optimize tool execution (caching, batching)
4. Parallelize feedback generation
5. Use faster GPUs (cloud rental)

---

## Success Criteria

By end of Week 4, we should have:

**Minimum Success**:
- ✅ 2x sample efficiency improvement over baseline
- ✅ Visible within-group improvement (rollout 8 > rollout 1)
- ✅ Base policy improves (not just feedback-following)

**Target Success**:
- ✅ 5x sample efficiency improvement
- ✅ Works across multiple difficulty levels (1-4)
- ✅ Generalizes to held-out companies

**Stretch Success**:
- ✅ 10x sample efficiency improvement
- ✅ Works on Level 5 tasks
- ✅ Faster training than baseline (despite feedback overhead)
- ✅ Transferable to other tool-use domains

---

## Post-Week 4: Future Work

1. **Week 5**: Transfer to real API composition benchmarks (ToolBench, API-Bank)
2. **Week 6**: Integrate human feedback during training
3. **Week 7**: Scale to larger models (Qwen3-14B, 32B)
4. **Week 8**: Write full paper for submission to ICML/NeurIPS

---

## Daily Checkpoints

At end of each day:
- [ ] Code committed to git
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Blockers identified and escalated

At end of each week:
- [ ] Weekly retrospective
- [ ] Adjust plan if needed
- [ ] Demo progress
- [ ] Plan next week in detail

