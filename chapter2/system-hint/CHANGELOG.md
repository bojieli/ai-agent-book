# System-Hint Agent Changelog

## 2025-09-30 - Trajectory Logging Enhancement

### Changes Made

#### 1. Full LLM Messages in Trajectory
Added tracking of the complete messages list sent to the LLM, including system hints:

- **Added field**: `last_llm_messages` to `SystemHintAgent` class
  - Stores the full messages array sent to the LLM, including the system hint appended as a user message
  - This differs from `conversation_history` which only stores the base conversation without the dynamic system hints

- **Modified methods**:
  - `__init__`: Initialize `last_llm_messages = None`
  - `execute_task`: Capture `messages_to_send` before LLM call and store as `self.last_llm_messages`
  - `_save_trajectory`: Include `last_llm_messages` in the trajectory JSON output
  - `reset`: Reset `last_llm_messages` to `None`

#### 2. Real System Time (No Mock Time)
Verified and ensured real system time is used throughout:

- **Default configuration**: `simulate_time_delay = False` (line 68 in agent.py)
  - When `False`, uses `datetime.now()` for all timestamps
  - When `True` (only for demos), uses simulated time

- **Timestamp sources**:
  - `_get_timestamp()`: Uses `datetime.now()` when `simulate_time_delay=False`
  - `trajectory_data['timestamp']`: Always uses `datetime.now().isoformat()`
  - Tool call timestamps: Always use `datetime.now().isoformat()`
  - TODO item timestamps: Always use `datetime.now().isoformat()`

### Benefits

1. **Complete LLM Context**: The `last_llm_messages` field in trajectory.json now shows exactly what was sent to the LLM, including dynamic system hints about current state, TODO list, timestamps, etc.

2. **Debugging**: Easier to debug agent behavior by seeing the complete context the LLM received, not just the conversation history

3. **Accurate Timestamps**: All timestamps reflect real system time for accurate trajectory analysis and debugging

### Example Trajectory Structure

```json
{
  "timestamp": "2025-09-30T20:26:32.057323",
  "iteration": 1,
  "provider": "kimi",
  "model": "kimi-k2-0905-preview",
  "conversation_history": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "[2025-09-30 20:26:00] Task..."},
    {"role": "assistant", "content": "..."}
  ],
  "last_llm_messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "[2025-09-30 20:26:00] Task..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "=== SYSTEM STATE ===\nCurrent Time: 2025-09-30 20:26:32\n..."}
  ],
  "tool_calls": [...],
  "todo_list": [...],
  "current_directory": "/path/to/dir",
  "final_answer": null,
  "config": {
    "enable_timestamps": true,
    "enable_tool_counter": true,
    "enable_todo_list": true,
    "enable_detailed_errors": true,
    "enable_system_state": true,
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
    "simulate_time_delay": false
  }
}
```

### Differences: conversation_history vs last_llm_messages

- **conversation_history**: Permanent record of the conversation between user and assistant
  - System prompt
  - User messages (with timestamps if enabled)
  - Assistant responses
  - Tool call messages and results

- **last_llm_messages**: Complete snapshot of what was sent to LLM in the last call
  - Everything from conversation_history
  - PLUS: Dynamic system hint appended as final user message
  - Shows current system state, TODO list, directory, time
  - This is what the LLM actually sees when making decisions

### Testing

All changes have been tested and verified:
- ✅ `last_llm_messages` correctly captured and saved
- ✅ Real system timestamps used (not simulated time)
- ✅ Trajectory JSON format validated
- ✅ No linter errors
- ✅ Backward compatible with existing code
