# Live Voice Chat Demo

A real-time voice chat demo featuring speech-to-text, AI conversation, and text-to-speech capabilities. The application supports multiple AI service providers and provides a seamless conversational experience with minimal latency.

## Features

- 🎤 Real-time voice input with Voice Activity Detection (VAD)
- 🤖 AI-powered conversations with **multiple provider support**
- 🔊 Text-to-speech synthesis
- ⚡ Low-latency audio streaming
- 📊 Real-time latency monitoring and logging
- 🎯 WebSocket-based communication
- 🔧 **Flexible provider selection** for ASR, LLM, and TTS services

## Supported AI Providers

### ASR (Automatic Speech Recognition)
- **OpenAI Whisper**: High accuracy, excellent language support
- **SenseVoice** (via Siliconflow): Low latency, cost-effective, auto language detection

### LLM (Large Language Model)
- **OpenAI GPT-4o**: Excellent reasoning, balanced performance
- **OpenRouter GPT-4o**: No geographic restrictions, unified interface
- **OpenRouter Gemini**: Fast response, optimized for real-time chat
- **ARK Doubao**: Low latency in China, optimized for Chinese language

### TTS (Text-to-Speech)
- **Fish Audio** (via Siliconflow): Natural voice synthesis, multiple voices

## Architecture Overview

The system consists of a frontend-backend architecture with real-time audio processing and **pluggable provider architecture**:

### Frontend (Next.js)
- **Audio Capture**: Uses Web Audio API to capture microphone input
- **Audio Processing**: Client-side audio processing and streaming to backend
- **WebSocket Communication**: Sends audio stream to backend and receives responses
- **Audio Playback**: Plays back TTS audio responses from the backend

### Backend (Node.js)
- **WebSocket Server**: Handles real-time audio streaming and client connections
- **Voice Activity Detection**: Server-side Silero VAD processing to detect speech boundaries with high accuracy
- **Multi-Provider Support**: Flexible ASR, LLM, and TTS provider integration
- **Provider Factories**: Dynamic provider creation and switching capabilities

### Data Flow
```
User Speech → WebSocket → Backend VAD → Multi-Provider STT → Multi-Provider LLM → TTS → Audio Response
```

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- **FFmpeg** - Required for audio processing and format conversion
- **Google Chrome** (recommended) - Best performance and compatibility for real-time audio
  - Not recommended: Safari, Edge, or other browsers due to WebAudio API limitations
- **API keys** from the supported providers (see Configuration section)

### Installing FFmpeg

#### macOS (using Homebrew)
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows
- Download from https://ffmpeg.org/download.html
- Or use Chocolatey: `choco install ffmpeg`
- Make sure `ffmpeg` is in your PATH

## Project Structure

```
/backend
- server.js: Main WebSocket server with provider integration
- config.js: Multi-provider configuration settings
- utils/
  - providers/
    - asrProviders.js: ASR provider implementations (OpenAI, Siliconflow)
    - llmProviders.js: LLM provider implementations (OpenAI, OpenRouter, ARK)
  - vad.js: Voice Activity Detection implementation
  - speechToText.js: Provider-aware STT service
  - textProcessor.js: Text preprocessing utilities
- tests/
  - provider-tests.js: Comprehensive provider testing
- run-tests.js: Test runner with environment validation
- PROVIDER_GUIDE.md: Detailed provider configuration guide
- package.json: Backend dependencies and scripts
```

```
/frontend
- pages/: Next.js pages
  - index.tsx: Main application interface
- components/: Reusable UI components
- public/: Static assets
  - audioWorklet.js: Audio processing and VAD implementation
- next.config.js: Next.js configuration
- tailwind.config.js: Tailwind CSS settings
- package.json: Frontend dependencies and scripts
```

## Installation

1. Clone the repository
2. Install backend dependencies: 
   ```bash
   cd backend && npm install
   ```
3. Install frontend dependencies: 
   ```bash
   cd frontend && npm install
   ```
4. Download the Silero VAD model:
   ```bash
   cd backend/models
   wget https://huggingface.co/deepghs/silero-vad-onnx/resolve/main/silero_vad.onnx
   ```

## Configuration

### Provider-Based Configuration

The system now supports **multiple AI service providers** for maximum flexibility. You can mix and match different providers for ASR, LLM, and TTS services.

### 1. Environment Variables Setup

Set up your API keys as environment variables:

```bash
# Required for OpenAI services
export OPENAI_API_KEY="your-openai-api-key"

# Required for OpenRouter services  
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Required for ARK (Doubao) services
export ARK_API_KEY="your-ark-api-key"

# Required for Siliconflow services (ASR and TTS)
export SILICONFLOW_API_KEY="your-siliconflow-api-key"

# For future use
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 2. Provider Selection

1. Copy the example configuration file:
   ```bash
   cp backend/config.js.example backend/config.js
   ```

2. Edit `backend/config.js` to select your preferred providers:
   ```javascript
   const config = {
     // Provider Selection - Choose your preferred providers
     ASR_PROVIDER: 'siliconflow',      // 'openai' or 'siliconflow'
     LLM_PROVIDER: 'ark',              // 'openai', 'openrouter-gpt4o', 'openrouter-gemini', 'ark'
     TTS_PROVIDER: 'siliconflow',      // 'siliconflow' (Fish Audio)
     
     // API Keys (loaded from environment variables)
     OPENAI_API_KEY: process.env.OPENAI_API_KEY,
     OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY,
     ARK_API_KEY: process.env.ARK_API_KEY,
     SILICONFLOW_API_KEY: process.env.SILICONFLOW_API_KEY,
     
     // ... other configuration options
   };
   ```

### 3. Recommended Provider Combinations

#### For Real-time Performance (Low Latency in China)
```javascript
ASR_PROVIDER: 'siliconflow',      // 'openai' or 'siliconflow'
LLM_PROVIDER: 'ark',              // 'openai', 'openrouter-gpt4o', 'openrouter-gemini', 'ark'
TTS_PROVIDER: 'siliconflow',      // 'siliconflow' (Fish Audio)
```

#### For Real-time Performance (Low Latency in US)
```javascript
ASR_PROVIDER: 'openai',            // 'openai' or 'siliconflow'
LLM_PROVIDER: 'openrouter-gemini', // 'openai', 'openrouter-gpt4o', 'openrouter-gemini', 'ark'
TTS_PROVIDER: 'siliconflow',       // 'siliconflow' (Fish Audio)
```

#### For Best Accuracy
```javascript
ASR_PROVIDER: 'openai',           // Accurate Whisper
LLM_PROVIDER: 'openrouter-gpt4o', // High-quality GPT-4o
TTS_PROVIDER: 'siliconflow'       // Fish Audio
```

### 4. API Key Requirements

You only need the API keys for the providers you plan to use:

| Provider | ASR | LLM | TTS | Required API Key |
|----------|-----|-----|-----|------------------|
| OpenAI | ✅ Whisper | ✅ GPT-4o | ❌ | `OPENAI_API_KEY` |
| OpenRouter | ❌ | ✅ GPT-4o, Gemini | ❌ | `OPENROUTER_API_KEY` |
| ARK (Doubao) | ❌ | ✅ Doubao | ❌ | `ARK_API_KEY` |
| Siliconflow | ✅ SenseVoice | ❌ | ✅ Fish Audio | `SILICONFLOW_API_KEY` |

### 5. Configuration Validation

The system includes comprehensive validation and testing tools:

```bash
# Test all configured providers
npm run test:providers

# Run the full test suite with environment validation
node run-tests.js
```

### Legacy Configuration Support

The system maintains backward compatibility with the previous hardcoded configuration format, but using the new provider selection is strongly recommended for better flexibility.

## Usage

1. **Set up your API keys** (see Configuration section)

2. **Configure your preferred providers** in `backend/config.js`

3. Start the backend server: 
   ```bash
   cd backend && npm start
   ```

4. Start the frontend development server: 
   ```bash
   cd frontend && npm run dev
   ```

5. Open http://localhost:3000 in your browser

6. Click "Start Recording" to begin a conversation

## Testing

### Provider Testing

Test individual providers and all combinations:

```bash
cd backend

# Test all providers with your API keys
node run-tests.js

# Test specific providers only
npm run test:providers

# Install test dependencies if needed
npm install
```

The test suite will automatically skip providers for which you don't have API keys configured.

### Test Coverage

- ✅ ASR provider functionality (OpenAI Whisper, SenseVoice)
- ✅ LLM provider functionality (OpenAI, OpenRouter GPT-4o, OpenRouter Gemini, ARK Doubao)  
- ✅ TTS provider functionality (Fish Audio via Siliconflow)
- ✅ All provider combinations (8 ASR+LLM combinations)
- ✅ Dynamic provider switching
- ✅ Error handling and fallback mechanisms

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure required environment variables are set
2. **FFmpeg Not Found**: Ensure FFmpeg is installed and available in your system PATH
   - Test with: `ffmpeg -version`
   - If not found, refer to the FFmpeg installation instructions above
3. **Network Issues**: Check connectivity to API endpoints
4. **Rate Limiting**: Consider switching providers or implementing retry logic
5. **Geographic Restrictions**: Use OpenRouter for global access
6. **ONNX Runtime Issues**: The backend uses ONNX Runtime for voice activity detection
   - Usually resolved by the `onnxruntime-node` package automatically
   - On some systems, you may need additional system libraries

### Performance Optimization

- **Low Latency**: Use Siliconflow ASR + OpenRouter Gemini
- **High Accuracy**: Use OpenAI ASR + OpenAI LLM
- **China Deployment**: Use Siliconflow ASR + ARK LLM

For detailed troubleshooting and configuration guidance, see [PROVIDER_GUIDE.md](backend/PROVIDER_GUIDE.md).

## License

MIT

