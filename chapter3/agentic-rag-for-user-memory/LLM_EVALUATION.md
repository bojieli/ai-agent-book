# LLM Evaluation Integration

This project now includes automatic LLM-based evaluation of agent responses, similar to the week2/user-memory project. When an agent generates a response, it is automatically evaluated for accuracy and completeness.

## 🎯 Overview

The LLM evaluation system automatically:
1. Evaluates agent responses after generation
2. Assigns a continuous reward score (0.0 to 1.0)
3. Determines pass/fail based on threshold (>= 0.6)
4. Provides detailed reasoning for the evaluation
5. Checks if required information was found

## 📋 Features

### Automatic Evaluation
- **Triggered automatically** after agent generates response
- **No manual intervention** required
- **Integrated into** the existing evaluation pipeline

### Evaluation Metrics
- **Reward Score**: Continuous score from 0.0 to 1.0
  - 0.0-0.2: Complete failure
  - 0.2-0.4: Poor performance
  - 0.4-0.6: Partial success
  - 0.6-0.8: Good performance
  - 0.8-1.0: Excellent performance
- **Pass/Fail**: Determined by reward >= 0.6
- **Reasoning**: Detailed explanation of the score
- **Required Information**: Verification of key facts

### Console Output
When evaluation runs, you'll see:
```
============================================================
Running LLM Evaluation...
------------------------------------------------------------
LLM Evaluation Reward: 0.850/1.000
Passed: Yes
Reasoning: The agent correctly recalled the account number from the conversation history.
Required Information Found:
  ✓ account number: 123456789
  ✓ routing number: 071000013
  ✗ pin number: not found
============================================================
```

## 🔧 Implementation

### Integration Points

1. **evaluator.py**
   - Imports LLMEvaluator from week2/user-memory-evaluation
   - Initializes evaluator if available
   - Runs evaluation after agent response
   - Adds results to EvaluationResult

2. **main.py**
   - Displays LLM evaluation results in UI
   - Shows reward score and pass/fail status
   - Lists required information checks

3. **Report Generation**
   - Includes LLM evaluation metrics
   - Shows average reward scores
   - Tracks evaluation success rates

### Code Changes

The key changes include:

```python
# In evaluator.py - Automatic evaluation after agent response
if self.llm_evaluator and agent_answer:
    llm_result = self.llm_evaluator.evaluate(
        test_case=eval_test_case,
        agent_response=agent_answer,
        extracted_memory=None
    )
    
    # Process and log results
    logger.info(f"LLM Evaluation Reward: {llm_result.reward:.3f}/1.000")
    logger.info(f"Passed: {'Yes' if llm_result.passed else 'No'}")
```

## 📊 Evaluation Flow

```
User Question
    ↓
Agent Processing (RAG)
    ↓
Agent Response Generated
    ↓
[AUTOMATIC LLM EVALUATION]
    ├─ Send response to LLM
    ├─ Get reward score
    ├─ Check required info
    └─ Generate reasoning
    ↓
Display Results
    ├─ Agent answer
    ├─ LLM evaluation score
    ├─ Pass/fail status
    └─ Required info checks
```

## 🚀 Usage

### Running with Evaluation

1. **Single Test Case**:
   ```bash
   python main.py
   # Select option 4: Evaluate Single Test Case
   # LLM evaluation runs automatically
   ```

2. **Batch Evaluation**:
   ```bash
   python main.py --mode batch --category layer1
   # All test cases evaluated with LLM
   ```

3. **Check Integration**:
   ```bash
   python test_llm_evaluation.py
   ```

### Viewing Results

Results include LLM evaluation details:
- In console output during evaluation
- In generated reports
- In saved result files

## 📈 Benefits

1. **Objective Assessment**: Consistent evaluation criteria
2. **Detailed Feedback**: Reasoning for each score
3. **Automatic Verification**: Checks required information
4. **Performance Tracking**: Monitor improvement over time
5. **No Manual Review**: Reduces human evaluation burden

## ⚙️ Configuration

### Requirements
- Access to week2/user-memory-evaluation module
- Valid API keys for LLM evaluation
- OpenAI-compatible API endpoint

### Environment Variables
```bash
# For LLM evaluation (if using OpenAI)
OPENAI_API_KEY=your_key

# Or configure evaluator in week2/user-memory-evaluation/config.py
```

### Disabling Evaluation
If LLM evaluation is not available:
- System continues to work normally
- Only RAG metrics are shown
- Manual evaluation still possible

## 📝 Example Output

### Successful Evaluation
```
Test: layer1_01_bank_account
Agent Answer: Your checking account number is 4429853327.

LLM Evaluation:
  Passed: Yes ✓
  Reward Score: 0.920/1.000
  Reasoning: The agent correctly extracted and provided the exact account number from the conversation. The response is accurate and directly addresses the user's question.
  
Required Information:
  ✓ checking account number
  ✓ account number format
```

### Failed Evaluation
```
Test: layer2_01_multiple_vehicles
Agent Answer: You have a Honda Accord.

LLM Evaluation:
  Passed: No ✗
  Reward Score: 0.450/1.000
  Reasoning: The agent only mentioned one vehicle when the user has multiple vehicles. Missing information about the Tesla Model 3 and service scheduling details.
  
Required Information:
  ✓ Honda Accord mentioned
  ✗ Tesla Model 3 not mentioned
  ✗ Service scheduling information missing
```

## 🔍 Troubleshooting

### LLM Evaluator Not Available
- Check week2/user-memory-evaluation exists
- Verify evaluator.py is present
- Ensure API keys are configured

### Evaluation Errors
- Check API key validity
- Verify network connectivity
- Review error logs for details

### Inconsistent Scores
- LLM evaluation is probabilistic
- Use temperature=0 for consistency
- Review evaluation criteria

## 📚 Related Documentation
- [README.md](README.md) - Main project documentation
- [RETRIEVAL_PIPELINE_INTEGRATION.md](RETRIEVAL_PIPELINE_INTEGRATION.md) - RAG pipeline details
- week2/user-memory-evaluation - Original evaluation framework
