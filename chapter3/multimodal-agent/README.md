# Multimodal Agent with Multiple Extraction Techniques

An educational agent framework that compares different multimodal content extraction techniques across multiple AI providers (Gemini, OpenAI, Doubao).

## Features

### Three Extraction Modes

1. **Native Multimodality**: Direct processing using model's built-in multimodal capabilities
   - Gemini 2.5 Pro: Documents (PDF), Images, Audio
   - GPT-5/GPT-4o: Images (OpenAI multimodal format)
   - Doubao 1.6: Images (OpenAI multimodal format)

2. **Extract to Text**: Convert multimodal content to text first, then process
   - PDF: OCR using Gemini or GPT-5
   - Image: Generate descriptions using GPT-5 or Doubao 1.6
   - Audio: Transcription using Whisper API or Gemini

3. **Multimodal Analysis Tools**: Additive functionality for follow-up questions
   - Image analysis tool (GPT-5/Doubao 1.6)
   - Audio analysis tool (Gemini 2.5 Pro)
   - PDF analysis tool (Gemini 2.5 Pro)

## Architecture

The agent follows a modular architecture with clear separation of concerns:

```
MultimodalAgent
├── Configuration (config.py)
│   ├── Model configurations
│   ├── API key management
│   └── Extraction mode settings
├── Agent Core (agent.py)
│   ├── Message handling (OpenAI format)
│   ├── Conversation history
│   ├── Mode-specific processing
│   └── Streaming responses
└── Multimodal Tools
    ├── Image analysis
    ├── Audio analysis
    └── PDF analysis
```

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd projects/week3/multimodal-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
```bash
cp env.example .env
# Edit .env with your API keys
```

4. Load environment variables:
```bash
export $(cat .env | xargs)
```

## Usage

### Interactive Chat Mode

Start an interactive session with the agent:

```bash
python main.py --interactive
```

Available commands in interactive mode:
- `/file <path>` - Load a multimodal file
- `/mode <native|extract_to_text>` - Switch extraction mode
- `/model <model_name>` - Switch model
- `/tools <on|off>` - Enable/disable multimodal tools
- `/history` - Show conversation history
- `/clear` - Clear conversation history
- `/quit` - Exit

### Process Single File

Process a file with a specific query:

```bash
# Native mode (default)
python main.py --file document.pdf --query "What is the main topic?"

# Extract to text mode
python main.py --mode extract_to_text --file image.jpg --query "Describe this image"

# With multimodal tools enabled
python main.py --tools --mode extract_to_text --file audio.mp3 --query "What's the content?"
```

### Programmatic Usage

```python
import asyncio
from agent import MultimodalAgent, MultimodalContent
from config import ExtractionMode

async def example():
    # Initialize agent
    agent = MultimodalAgent(
        model="gemini-2.5-pro",
        mode=ExtractionMode.NATIVE,
        enable_tools=True
    )
    
    # Process a PDF
    content = MultimodalContent(
        type="pdf",
        path="document.pdf"
    )
    
    result = await agent.process_multimodal_content(
        content,
        "Summarize this document"
    )
    print(result)
    
    # Chat with streaming
    async for chunk in agent.chat("Tell me more about the key points", stream=True):
        print(chunk, end="", flush=True)

asyncio.run(example())
```

## Comparing Extraction Techniques

### Demo Script

Run the comprehensive comparison demo:

```bash
# Compare extraction modes for a specific file
python demo.py document.pdf "What are the key findings?"

# This will run:
# 1. Native multimodal mode
# 2. Extract to text mode
# 3. Extract to text with tools
# 4. Comparison across different models
```

### Mode Comparison

| Mode | Advantages | Disadvantages | Best For |
|------|------------|---------------|----------|
| **Native** | - Preserves full context<br>- Better visual understanding<br>- Direct processing | - Limited model support<br>- Higher token usage | Complex documents with mixed content |
| **Extract to Text** | - Works with all models<br>- Lower token usage<br>- Can cache extractions | - Loses visual context<br>- Two-step process | Text-heavy documents, cost optimization |
| **With Tools** | - Best of both worlds<br>- Follow-up questions<br>- Selective deep analysis | - More complex setup<br>- Multiple API calls | Interactive sessions, detailed Q&A |

## Supported File Types

### Documents
- PDF files (up to 1000 pages)
- Best with Gemini 2.5 Pro native mode

### Images
- JPEG, PNG, GIF, BMP, WebP
- Supported by all models

### Audio
- MP3, WAV, M4A, FLAC, AAC, OGG
- Transcription via Whisper or Gemini

## Model Capabilities

| Model | Native PDF | Native Image | Native Audio | Extract to Text | Tools Support |
|-------|------------|--------------|--------------|-----------------|---------------|
| Gemini 2.5 Pro | ✅ | ✅ | ✅ | ✅ | ✅ |
| GPT-5/GPT-4o | ❌ | ✅ | ❌ | ✅ | ✅ |
| Doubao 1.6 | ❌ | ✅ | ❌ | ✅ | ✅ |

## API Configuration

### Required API Keys

1. **Google Gemini**: Required for PDF/Audio native processing
   - Get key at: https://makersuite.google.com/app/apikey
   - Set: `GOOGLE_API_KEY`

2. **OpenAI**: Required for GPT models and Whisper
   - Get key at: https://platform.openai.com/api-keys
   - Set: `OPENAI_API_KEY`

3. **Doubao**: Required for Doubao model
   - Get key at: https://console.volcengine.com/
   - Set: `DOUBAO_API_KEY`

### File Size Limits
- PDF: 20MB
- Images: 20MB
- Audio: 25MB

## Testing

Run the test suite:

```bash
python test_multimodal.py
```

## Examples

### Example 1: Analyzing a Research Paper

```python
# Native mode for best understanding
agent = MultimodalAgent(
    model="gemini-2.5-pro",
    mode=ExtractionMode.NATIVE
)

content = MultimodalContent(type="pdf", path="research_paper.pdf")
summary = await agent.process_multimodal_content(
    content,
    "What are the main contributions and findings?"
)
```

### Example 2: Processing Images with Follow-up

```python
# Extract to text with tools for follow-up questions
agent = MultimodalAgent(
    model="gpt-4o",
    mode=ExtractionMode.EXTRACT_TO_TEXT,
    enable_tools=True
)

# Initial processing
await agent.chat("I have an image at photo.jpg", MultimodalContent(type="image", path="photo.jpg"))

# Follow-up using tools
await agent.chat("What objects are in the background?")
await agent.chat("What's the color scheme?")
```

### Example 3: Audio Transcription and Analysis

```python
# Using Whisper for transcription
agent = MultimodalAgent(
    model="gpt-4o",
    mode=ExtractionMode.EXTRACT_TO_TEXT
)

content = MultimodalContent(type="audio", path="interview.mp3")
transcript = await agent._extract_audio_to_text(content)
print(f"Transcript: {transcript}")

# Analyze the transcript
analysis = await agent._answer_with_context(
    transcript,
    "What are the key points discussed?"
)
```

## Best Practices

1. **Mode Selection**:
   - Use Native mode when visual/audio understanding is crucial
   - Use Extract to Text for cost optimization and caching
   - Enable tools for interactive sessions with follow-ups

2. **Model Selection**:
   - Gemini 2.5 Pro: Best for PDFs and audio
   - GPT-4o/GPT-5: Best for complex image understanding
   - Doubao 1.6: Alternative for image processing

3. **Performance Optimization**:
   - Cache extracted text for repeated queries
   - Use streaming for better user experience
   - Process files under size limits

4. **Error Handling**:
   - Always validate file existence and type
   - Check API key configuration before processing
   - Handle rate limits and API errors gracefully

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure all required API keys are set in .env
   - Check API key validity and quota

2. **File Processing Errors**:
   - Verify file format is supported
   - Check file size is within limits
   - Ensure file path is correct

3. **Model Compatibility**:
   - Not all models support all content types natively
   - Use Extract to Text mode for unsupported combinations

## Architecture Details

### Message Format

The agent uses OpenAI-compatible message format:

```python
{
    "role": "user" | "assistant" | "system" | "tool",
    "content": "message text" | [{"type": "text", "text": "..."}, ...],
    "tool_calls": [...],  # Optional
    "tool_call_id": "...",  # For tool responses
}
```

### Tool Calling Format

Tools follow OpenAI function calling specification:

```python
{
    "type": "function",
    "function": {
        "name": "analyze_image",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

### Streaming Implementation

The agent supports streaming responses for better UX:
- Gemini: Native streaming API
- OpenAI/Doubao: Stream via chat completions API
- Tool results are streamed as they complete

## Contributing

This is an educational project demonstrating multimodal AI capabilities. Contributions should focus on:
- Adding new extraction techniques
- Improving model comparisons
- Enhancing documentation
- Adding more test cases

## License

MIT License - See LICENSE file for details
