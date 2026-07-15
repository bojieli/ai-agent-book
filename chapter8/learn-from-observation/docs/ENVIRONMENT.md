# Environment Design

## Overview

This document describes the customer service phone call simulation environment used for training and evaluating world model learning. The environment provides rich, structured observations at every step, making it ideal for testing observation-based learning.

## Environment Philosophy

**Design Principle**: The environment should generate **information-rich observations** that contain learnable patterns, not just binary success/failure signals.

**Key Properties**:
1. **Non-deterministic**: Same action in same state can yield different observations (CSR phrasing variations)
2. **Informative**: Observations explicitly state what's needed (not just "error")
3. **Structured**: Consistent format for world model to learn
4. **Realistic**: Mimics real customer service interactions

## Core Components

### 1. User Simulator

**Purpose**: Responds to auth_info_form requests with user authentication data.

**Implementation**:
```python
class UserSimulator:
    """
    Simulates users providing authentication information via form.
    Returns JSON with requested fields.
    """
    
    def __init__(self):
        self.user_profiles = {}  # instance_id -> profile dict
        self.behavior_distribution = {
            "cooperative": 0.7,      # Provides all available info
            "partial_info": 0.2,     # Missing some fields  
            "difficult": 0.1         # Initially provides wrong info
        }
    
    def fill_auth_form(
        self, 
        instance_id: str, 
        requested_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Respond to auth_info_form tool call.
        
        Returns:
            {
                "account_number": "123456789",
                "last_4_ssn": "5678",
                "date_of_birth": "1990-01-01",
                "unavailable": ["last_4_cc"]  # Fields user doesn't have
            }
        """
        profile = self.user_profiles[instance_id]
        behavior = self._sample_behavior()
        
        response = {}
        unavailable = []
        
        for field in requested_fields:
            if field not in profile:
                # User genuinely doesn't have this field
                unavailable.append(field)
            elif behavior == "partial_info" and random.random() < 0.3:
                # User forgets or doesn't have this field
                unavailable.append(field)
            elif behavior == "difficult" and random.random() < 0.2:
                # User provides wrong info (misremembering)
                response[field] = self._generate_wrong_value(field)
            else:
                # Normal case: provide correct value
                response[field] = profile[field]
        
        return {
            **response,
            "unavailable": unavailable
        }
```

**User Profile Schema**:
```python
UserProfile = {
    "name": str,                    # "John Smith"
    "account_number": str,          # "123456789"
    "last_4_ssn": str,             # "5678"
    "date_of_birth": str,          # "1990-01-01"
    "billing_zip": str,            # "94105"
    "last_4_cc": str,              # "4321"  (optional)
    "phone_number": str,           # "415-555-1234"
    "email": str,                  # "john@example.com"
}
```

**Profile Distribution**:
- 80% complete profiles (all fields present)
- 15% missing one field (usually last_4_cc)
- 5% missing multiple fields

**Observation Characteristics**:
- **Format**: JSON dictionary
- **Determinism**: Deterministic given profile + behavior
- **Information content**: Medium
- **World model learning**: Must learn user behavior patterns

### 2. Company Directory

**Purpose**: Provides department contact information (NOT authentication requirements).

**Schema**:
```python
@dataclass
class Department:
    name: str                       # "Customer Service"
    phone: str                      # "800-555-0100"
    description: str                # "General inquiries and account support"
    operating_hours: str            # "Mon-Fri 8am-8pm EST"
    routing_rules: Optional[Dict]   # {"must_call_first": "Customer Service"}
    
@dataclass  
class Company:
    name: str                       # "Acme Bank"
    departments: List[Department]   # 2-5 departments
    industry: str                   # "banking", "insurance", "telecom", etc.
```

**Important Design Decision**: 
The directory does **NOT** include `auth_required` fields. The agent must learn what authentication each department needs through experience (from CSR responses).

**Directory Database**:
- 100 companies total
- Industries: Banking (25), Insurance (25), Telecom (25), Retail (25)
- 2-5 departments per company
- Common departments: Customer Service, Technical Support, Billing, Sales, Fraud

**Department Types and Typical Auth Patterns** (for environment design, not shown to agent):
```python
# These patterns are INTERNAL to environment
# Agent must learn them from CSR responses

TYPICAL_AUTH_REQUIREMENTS = {
    "Customer Service": ["account_number", "last_4_ssn"],
    "Billing": ["account_number", "billing_zip"],
    "Technical Support": ["account_number", "phone_number"],
    "Fraud Department": ["account_number", "last_4_ssn", "last_4_cc"],
    "Sales": [],  # No auth needed
}

# With variation:
# - 70% use typical pattern
# - 20% use additional field
# - 10% use different combination
```

**Routing Rules**:
```python
ROUTING_DEPENDENCIES = {
    "Fraud Department": {"prerequisite": "Customer Service"},
    "Technical Support (Priority)": {"prerequisite": "Technical Support"},
}
```

**Observation Characteristics**:
- **Format**: JSON with departments list
- **Determinism**: Fully deterministic (same for same company)
- **Information content**: Low (no auth requirements listed)
- **World model learning**: Easy to predict, quick convergence

### 3. Phone System Simulator

**Purpose**: Simulates Customer Service Representative (CSR) interactions.

**CSR Behavior Flow**:
```
Call Initiated
    ↓
[Phase 1: Greeting]
    ↓
[Phase 2: Authentication Check]
    ↓
├─ Auth Complete? ──Yes─→ [Phase 3: Service]
│                              ↓
├─ Auth Incomplete? ──→ Request More Info → Return Response
│
├─ Wrong Department? ──→ Redirect → Return Response
│
└─ Routing Violation? ──→ Reject → Return Response
```

**Implementation**:
```python
class PhoneSystemSimulator:
    """
    Simulates CSR interactions with natural language responses.
    This is the PRIMARY source of learning signal for world model.
    """
    
    def handle_call(
        self,
        instance_id: str,
        phone: str,
        auth_info: Dict[str, str],
        call_history: List[str]
    ) -> CallResult:
        """
        Handle a phone call with authentication and routing.
        
        Returns CallResult with:
        - status: success/auth_failed/wrong_dept/routing_violation
        - message: Natural language CSR response
        - step_reward: Partial credit for progress
        - failure_info: Structured error information
        """
        department = self.directory.lookup_phone(phone)
        
        # Phase 1: Check routing prerequisites
        routing_check = self._check_routing_rules(
            department, 
            call_history
        )
        if not routing_check.valid:
            return CallResult(
                status="routing_violation",
                message=self._generate_routing_response(routing_check),
                step_reward=-0.1,
                failure_info={
                    "type": "wrong_order",
                    "prerequisite": routing_check.required_dept
                }
            )
        
        # Phase 2: Check authentication
        auth_check = self._check_authentication(department, auth_info)
        if not auth_check.complete:
            return CallResult(
                status="auth_failed",
                message=self._generate_auth_request_response(auth_check),
                step_reward=0.0 if not auth_check.partial else 0.2,
                failure_info={
                    "type": "missing_auth",
                    "missing_fields": auth_check.missing_fields,
                    "provided_fields": auth_check.provided_fields
                }
            )
        
        # Phase 3: Check department capability
        capability_check = self._check_department_capability(
            department,
            self.task_requests[instance_id]
        )
        if not capability_check.can_handle:
            return CallResult(
                status="wrong_department",
                message=self._generate_redirect_response(capability_check),
                step_reward=0.3,  # Auth was correct, just wrong dept
                failure_info={
                    "type": "wrong_department",
                    "called": department.name,
                    "should_call": capability_check.correct_dept
                }
            )
        
        # Phase 4: Provide service
        service_response = self._handle_service_request(
            department,
            self.task_requests[instance_id]
        )
        return CallResult(
            status="success",
            message=service_response,
            step_reward=1.0,
            failure_info=None
        )
```

**CSR Response Generation**:
```python
def _generate_auth_request_response(
    self, 
    auth_check: AuthCheckResult
) -> str:
    """
    Generate natural language CSR response requesting authentication.
    
    Key: These responses are INFORMATION-RICH for world model learning.
    They explicitly state what's needed.
    """
    missing = auth_check.missing_fields
    
    # Template with variations
    templates = [
        # Style 1: Formal
        f"For security purposes, I need to verify your identity. "
        f"Could you please provide your {format_field_list(missing)}?",
        
        # Style 2: Conversational
        f"I'll need a few pieces of information to pull up your account. "
        f"Can you give me your {format_field_list(missing)}?",
        
        # Style 3: Direct
        f"I need your {format_field_list(missing)} to continue.",
        
        # Style 4: Apologetic
        f"I apologize, but I need to verify some information first. "
        f"May I have your {format_field_list(missing)}?",
    ]
    
    # Choose template based on department style
    return random.choice(templates)

def format_field_list(fields: List[str]) -> str:
    """
    Convert field names to natural language.
    
    Examples:
    - ["account_number"] → "account number"
    - ["account_number", "last_4_ssn"] → "account number and the last 4 digits of your Social Security Number"
    """
    field_names = {
        "account_number": "account number",
        "last_4_ssn": "the last 4 digits of your Social Security Number",
        "last_4_cc": "the last 4 digits of your credit card",
        "date_of_birth": "date of birth",
        "billing_zip": "billing ZIP code",
        "phone_number": "phone number on file",
    }
    
    natural_fields = [field_names.get(f, f) for f in fields]
    
    if len(natural_fields) == 1:
        return natural_fields[0]
    elif len(natural_fields) == 2:
        return f"{natural_fields[0]} and {natural_fields[1]}"
    else:
        return ", ".join(natural_fields[:-1]) + f", and {natural_fields[-1]}"
```

**Observation Characteristics**:
- **Format**: Natural language string
- **Determinism**: Non-deterministic (multiple phrasings for same meaning)
- **Information content**: HIGH - explicitly states requirements
- **World model learning**: Most valuable signal, requires many examples

### 4. Tool Definitions

**Tool 1: auth_info_form**
```yaml
name: auth_info_form
description: |
  Collect authentication information from the user.
  Call this ONCE with ALL required fields.
  Do not call multiple times.
  
parameters:
  fields:
    type: array
    items: string
    description: List of authentication fields to collect
    examples:
      - ["account_number", "last_4_ssn"]
      - ["account_number", "billing_zip", "date_of_birth"]
    
returns:
  type: object
  properties:
    # Provided field values
    account_number: string
    last_4_ssn: string
    # ... other requested fields ...
    unavailable:
      type: array
      items: string
      description: Fields user doesn't have

observation_characteristics:
  format: JSON
  determinism: Deterministic given user profile
  information_content: Medium
  typical_tokens: 50-100
```

**Tool 2: search_company**
```yaml
name: search_company
description: |
  Search for company departments and phone numbers.
  Returns department names, phones, and descriptions.
  Does NOT include authentication requirements - learn those from experience.
  
parameters:
  company_name:
    type: string
    description: Name of company to search
    examples: ["Acme Bank", "SafeGuard Insurance"]
    
returns:
  type: object
  properties:
    departments:
      type: array
      items:
        name: string
        phone: string
        description: string
        operating_hours: string

observation_characteristics:
  format: JSON
  determinism: Fully deterministic
  information_content: Low (no auth requirements)
  typical_tokens: 200-400
```

**Tool 3: make_phone_call**
```yaml
name: make_phone_call
description: |
  Make a phone call to a department with authentication.
  
parameters:
  phone_number:
    type: string
    description: Department phone number
  auth_info:
    type: object
    description: Authentication information (e.g., {"account_number": "123456"})
    
returns:
  type: object
  properties:
    status: 
      enum: [success, auth_failed, wrong_department, routing_violation]
    message: 
      type: string
      description: Natural language CSR response
      
observation_characteristics:
  format: JSON with natural language message
  determinism: Non-deterministic (CSR phrasing varies)
  information_content: HIGH
  typical_tokens: 50-200
```

### 5. Task Specification

**Task Format**:
```python
@dataclass
class Task:
    company: str                    # "Acme Bank"
    user_profile: UserProfile       # Authentication data
    goal: str                       # "Check account balance and dispute charge"
    success_criteria: Dict          # What constitutes success
    difficulty_level: int           # 1-5
    optimal_steps: int              # Minimum steps to complete
```

**Difficulty Levels**:

**Level 1: Single Call, Simple Auth** (100 tasks)
```python
Example:
- Company: Acme Bank
- Goal: Check account balance
- Required: Call Customer Service with account_number, last_4_ssn
- Optimal steps: 3
  1. search_company("Acme Bank")
  2. auth_info_form(["account_number", "last_4_ssn"])
  3. make_phone_call("800-555-0100", {account_number, last_4_ssn})

Learning challenge:
- Agent must learn Customer Service needs these 2 fields
- No routing complexity
```

**Level 2: Single Call, Multiple Fields** (150 tasks)
```python
Example:
- Company: SafeGuard Insurance  
- Goal: Update billing information
- Required: Call Billing with account_number, billing_zip, date_of_birth
- Optimal steps: 3
  1. search_company("SafeGuard Insurance")
  2. auth_info_form(["account_number", "billing_zip", "date_of_birth"])
  3. make_phone_call("800-555-0200", {account_number, billing_zip, date_of_birth})

Learning challenge:
- Agent must learn Billing dept needs 3 specific fields
- Must request ALL fields in one auth_info_form call
```

**Level 3: Two Calls, Sequential** (150 tasks)
```python
Example:
- Company: Acme Bank
- Goal: Dispute fraudulent charge
- Required: 
  1. Call Customer Service first (prerequisite)
  2. Then call Fraud Department
- Optimal steps: 5
  1. search_company("Acme Bank")
  2. auth_info_form(["account_number", "last_4_ssn"])
  3. make_phone_call(CS, {account_number, last_4_ssn})
  4. auth_info_form(["last_4_cc"])  # Need additional field
  5. make_phone_call(Fraud, {account_number, last_4_ssn, last_4_cc})

Learning challenge:
- Must learn routing rules (CS before Fraud)
- Fraud needs additional authentication
- Sequential dependency
```

**Level 4: Missing Information** (50 tasks)
```python
Example:
- Company: TechCorp
- Goal: Get technical support
- User profile: MISSING phone_number field
- Required: Handle missing information gracefully
- Optimal steps: Variable

Learning challenge:
- User doesn't have required field
- Must learn to handle "unavailable" in auth_info_form response
- May need to use alternative authentication
```

**Level 5: Complex Multi-Department** (50 tasks)
```python
Example:
- Company: MegaCorp
- Goal: "Transfer service, update billing, schedule technician"
- Required: 3-4 department calls with various auth
- Optimal steps: 8-12

Learning challenge:
- Multiple departments with different auth requirements
- Complex routing (some prerequisites)
- Information from first call needed for later calls
```

### 6. Reward Structure

**Reward Components**:

**Extrinsic Rewards** (from environment):
```python
Reward Levels:
- 0.0: No progress (failed before authentication)
- 0.2: Partial authentication provided (some fields correct)
- 0.3: Full authentication collected
- 0.5: Successfully authenticated with CSR
- 0.7: Reached correct department and authenticated
- 1.0: Task completed successfully

Penalties:
- -0.1: Called auth_info_form multiple times
- -0.1: Violated routing rules
- -0.05: Called wrong department (but authenticated)
```

**Intrinsic Rewards** (from world model - computed during training):
```python
For each step t:
  intrinsic_reward_t = β * surprise_t
  surprise_t = -log P(o_{t+1} | s_t, a_t; world_model)
  β = 0.1  # intrinsic reward coefficient

Where:
- High surprise (world model uncertain) = high intrinsic reward
- Low surprise (world model confident) = low intrinsic reward

Example values:
- search_company result (deterministic): surprise ≈ 0.1, intrinsic ≈ 0.01
- Common CSR response (seen 100x): surprise ≈ 1.0, intrinsic ≈ 0.10
- Novel CSR response (rare case): surprise ≈ 5.0, intrinsic ≈ 0.50
```

**Total Reward**:
```python
total_reward = extrinsic_reward + intrinsic_reward

This combines:
- Task success signal (extrinsic)
- Exploration bonus (intrinsic)
```

### 7. Observation Format for World Model

**State-Action-Observation Tuple Format**:
```python
SAO_Tuple = {
    "state": {
        "task": "Check account balance at Acme Bank",
        "step": 2,
        "history_compressed": "Searched Acme Bank directory, got dept list",
        "info_collected": {},
        "tools_called": ["search_company"]
    },
    "action": {
        "tool": "make_phone_call",
        "parameters": {
            "phone": "800-555-0100",
            "auth_info": {}
        }
    },
    "observation": {
        "tool": "make_phone_call",
        "output": {
            "status": "auth_failed",
            "message": "For security purposes, I need your account number and the last 4 digits of your Social Security Number."
        }
    },
    "reward": 0.0,
    "metadata": {
        "observation_type": "csr_response",
        "department": "Customer Service",
        "company": "Acme Bank"
    }
}
```

**Observation Type Taxonomy**:
```python
Observation Types:
1. "directory_result": search_company output
   - Deterministic
   - Low information content for world model
   - Example: {"departments": [...]}

2. "form_response": auth_info_form output
   - Semi-deterministic (depends on user profile)
   - Medium information content
   - Example: {"account_number": "123456", "unavailable": []}

3. "csr_response": make_phone_call output
   - Non-deterministic (phrasing varies)
   - HIGH information content
   - Example: "I need your account number and last 4 SSN"
   - This is the MOST VALUABLE for world model learning
```

### 8. Data Generation Strategy

**Training Set** (500 tasks):
```python
Distribution:
- Level 1: 100 tasks (20%)
- Level 2: 150 tasks (30%)
- Level 3: 150 tasks (30%)
- Level 4: 50 tasks (10%)
- Level 5: 50 tasks (10%)

Company Distribution:
- 50 companies used in training
- Each company appears 10 times with different tasks
- Mix of industries

User Profile Distribution:
- 80% complete profiles
- 15% missing one field
- 5% missing multiple fields
```

**Validation Set** (100 tasks):
```python
- Same 50 companies as training
- Different task types
- Used for monitoring during training
```

**Test Set** (100 tasks):
```python
- 50 NEW companies (never seen in training)
- Tests generalization and transfer
- Same difficulty distribution as training
```

### 9. Key Design Rationale

**Why This Environment is Good for World Model Learning**:

1. **Rich Observations**: CSR responses contain explicit information about requirements
2. **Patterns to Learn**: Auth requirements follow patterns (e.g., Customer Service usually needs account + SSN)
3. **Transfer Opportunity**: Patterns generalize across companies
4. **Non-Determinism**: Multiple valid phrasings for same meaning
5. **Clear Structure**: JSON + natural language mix
6. **Measurable Progress**: Can track world model prediction accuracy

**What Makes This Different from Standard RL Benchmarks**:

| Aspect | Standard RL (e.g., Atari) | Our Environment |
|--------|---------------------------|-----------------|
| Observations | Pixels, low-level | Language, high-level |
| Information density | Low per frame | High per step |
| Patterns | Implicit | Explicit (CSR states requirements) |
| Transfer | Limited | Strong (across companies) |
| Determinism | Mostly deterministic | Mix of deterministic and non-deterministic |

### 10. Environment Validation

**Sanity Checks**:
```python
1. Determinism check:
   - Same company → same directory result (100% match)
   
2. Auth pattern consistency:
   - Customer Service at different companies should have similar auth patterns
   - 70% should require [account_number, last_4_ssn]
   
3. CSR response quality:
   - All auth failures should explicitly state missing fields
   - No vague error messages
   
4. Routing rules:
   - All prerequisites must be enforced
   - Correct redirects provided
   
5. User profile coverage:
   - All required fields for all tasks must exist in some user profiles
   - Some profiles should be missing optional fields
```

**World Model Learnability Test**:
```python
Simple test: Can a supervised model learn to predict observations?

1. Collect 1000 SAO tuples from random policy
2. Train small language model (Qwen-1.5B) to predict observations
3. Measure prediction accuracy

Expected results:
- Directory results: >95% accuracy (deterministic)
- Form responses: >80% accuracy (semi-deterministic)
- CSR responses: >60% accuracy (non-deterministic but structured)

If prediction accuracy is too low (<40% on CSR), environment may be too noisy.
If accuracy is too high (>95% on everything), environment may be too simple.
```

## Implementation Notes

1. **Use LLM for CSR Simulation**: Use a small LLM (GPT-4o-mini or Qwen-2.5-7B) to generate CSR responses with templates, ensuring natural variation while maintaining information content.

2. **Cache Deterministic Results**: Cache directory lookups to ensure perfect determinism and faster execution.

3. **Log All Observations**: Save all SAO tuples for offline analysis and world model quality evaluation.

4. **Observation Statistics**: Track observation type distributions to ensure balanced learning signal.

5. **Validation Scripts**: Include scripts to verify environment properties (determinism, information content, etc.)

## Summary

This environment is specifically designed to test world model learning by providing:
- **Rich observations** at every step
- **Learnable patterns** that generalize
- **Varying information density** across observation types
- **Realistic complexity** without being overwhelming

The key innovation is that CSR responses explicitly state requirements, making them excellent training signal for world models while still requiring the agent to learn and generalize patterns.

