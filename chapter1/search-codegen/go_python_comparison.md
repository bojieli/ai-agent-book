# Go vs Python Implementation Comparison

This document shows how the Python implementation exactly matches the Go implementation for GPT-5 OpenRouter API calls.

## Request Structure Comparison

### Go Implementation
```go
// From the provided Go code
webSearchTool := GPT5OpenRouterWebSearchTool{
    Type:              "web_search",
    SearchContextSize: "medium",
    UserLocation: map[string]interface{}{
        "type":    "approximate",
        "country": "US",
    },
}

request := GPT5OpenRouterRequest{
    Model:             c.model,
    Messages:          messages,
    Tools:             []GPT5OpenRouterWebSearchTool{webSearchTool},
    ToolChoice:        "auto",
    ParallelToolCalls: true,
    Reasoning: &GPT5OpenRouterReasoning{
        Effort:          reasoningEffort,
        GenerateSummary: false,
    },
    Background: false,
    Stream:     false,
}
```

### Python Implementation
```python
# From agent.py
web_search_tool = {
    "type": "web_search",
    "search_context_size": "medium",
    "user_location": {
        "type": "approximate",
        "country": "US"
    }
}

request_body = {
    "model": self.model,
    "messages": messages,
    "tools": [web_search_tool],
    "tool_choice": "auto",
    "parallel_tool_calls": True,
    "reasoning": {
        "effort": reasoning_effort,
        "generate_summary": False
    },
    "background": False,
    "stream": False
}
```

## Key Matching Points

1. **Tool Structure**: Both implementations use the same tool structure with `type: "web_search"` and additional configuration fields.

2. **Request Parameters**: Identical parameters including:
   - `model`
   - `messages`
   - `tools` (array of web_search tools)
   - `tool_choice: "auto"`
   - `parallel_tool_calls: true/True`
   - `reasoning` with effort and generate_summary
   - `background: false/False`
   - `stream: false/False`

3. **Headers**: Both use simple headers:
   ```go
   // Go
   req.Header.Set("Content-Type", "application/json")
   req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.apiKey))
   ```
   
   ```python
   # Python
   headers = {
       "Content-Type": "application/json",
       "Authorization": f"Bearer {self.api_key}"
   }
   ```

4. **Model Default**: Both default to `openai/gpt-5-2025-08-07`

5. **Reasoning Levels**: Both support "low", "medium", and "high" reasoning effort

## Usage Comparison

### Go
```go
client := NewGPT5OpenRouterClientAdapter(apiKey, baseURL, model)
response, err := client.CallGPT5(ctx, systemPrompt, userPrompt, "medium")
```

### Python
```python
agent = GPT5NativeAgent(api_key, base_url, model)
result = agent.process_request(user_request, use_tools=True, reasoning_effort="medium")
```

## Response Handling

Both implementations:
- Handle streaming and non-streaming responses
- Log token usage including cached and reasoning tokens
- Extract content from the response choices
- Handle errors with appropriate status codes

The Python implementation is a direct port of the Go implementation, ensuring complete compatibility with the OpenRouter GPT-5 API.
