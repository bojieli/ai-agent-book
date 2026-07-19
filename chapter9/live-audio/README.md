# Live Voice Chat Demo

A real-time voice chat demo featuring speech-to-text, AI conversation, and text-to-speech capabilities. The application supports multiple AI service providers and provides a seamless conversational experience with minimal latency.

> This is the companion code for **实验 9-1「构建传统语音 Agent」** in 《深入理解 AI Agent》第 9 章. It implements the **cascaded** voice pipeline (VAD → ASR → LLM → TTS) discussed there: the frontend captures the microphone and streams audio over a WebSocket; the backend runs Silero VAD to detect end-of-speech (~500 ms of silence), then routes the utterance through pluggable ASR, LLM, and TTS providers and streams synthesized audio back for playback.

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
- **CosyVoice2** (via Siliconflow): Natural voice synthesis, multiple system voices

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

### Ports

| Component | Port | Notes |
|-----------|------|-------|
| Backend (WebSocket server) | **8848** | Set by `LISTEN_PORT` in `backend/config.js`. The frontend connects to `ws://localhost:8848`. |
| Frontend (Next.js dev server) | **3000** | Open http://localhost:3000 in the browser. |

The frontend learns the backend port from the `WEBSOCKET_PORT` environment variable (see `frontend/.env.example`). It must match the backend's `LISTEN_PORT`.

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
- utils/providers/: Provider configuration (ASR / LLM / TTS)
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
4. Download the Silero VAD model (already included in this repo at `backend/models/silero_vad.onnx`; only needed if missing):
   ```bash
   cd backend/models
   wget https://huggingface.co/deepghs/silero-vad-onnx/resolve/main/silero_vad.onnx
   ```
5. Configure the frontend's WebSocket port (defaults to 8848 if omitted):
   ```bash
   cd frontend && cp .env.example .env   # sets WEBSOCKET_PORT=8848 to match the backend
   ```

After installing, verify your environment (Node version, FFmpeg, VAD model, provider keys) without needing a microphone or browser:

```bash
cd backend && npm run check    # or: node check-setup.js
```

This prints which prerequisites are satisfied and which selected providers have their API keys set. It exits non-zero only if a hard prerequisite (Node < 16, missing FFmpeg, or missing VAD model) is absent.

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

1. This repo already ships a ready-to-edit `backend/config.js`. If it is missing (e.g. a fresh checkout that ignores it), copy the example first:
   ```bash
   cp backend/config.js.example backend/config.js
   ```

2. Edit `backend/config.js` to select your preferred providers:
   ```javascript
   const config = {
     // Provider Selection - Choose your preferred providers
     ASR_PROVIDER: 'siliconflow',      // 'openai' (whisper-1) or 'siliconflow' (SenseVoice)
     LLM_PROVIDER: 'openrouter',       // 'openrouter' (gpt-5.6-luna, default), 'openai', 'openrouter-gemini', 'ark'
     TTS_PROVIDER: 'siliconflow',      // 'siliconflow' (CosyVoice2)
     
     // API Keys (loaded from environment variables)
     OPENAI_API_KEY: process.env.OPENAI_API_KEY,
     OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY,
     ARK_API_KEY: process.env.ARK_API_KEY,
     SILICONFLOW_API_KEY: process.env.SILICONFLOW_API_KEY,
     
     // ... other configuration options
   };
   ```

### 3. Recommended Provider Combinations

#### Default / Recommended (works anywhere with an OpenRouter key)
```javascript
ASR_PROVIDER: 'siliconflow',      // SenseVoice
LLM_PROVIDER: 'openrouter',       // openai/gpt-5.6-luna via OpenRouter (avoids gpt-5.6* org verification)
TTS_PROVIDER: 'siliconflow',      // CosyVoice2
```

#### For Real-time Performance (Low Latency in China)
```javascript
ASR_PROVIDER: 'siliconflow',      // SenseVoice
LLM_PROVIDER: 'ark',              // Doubao (fast in China); or 'openrouter' for gpt-5.6-luna
TTS_PROVIDER: 'siliconflow',      // CosyVoice2
```

#### For Best Accuracy
```javascript
ASR_PROVIDER: 'openai',           // Accurate Whisper
LLM_PROVIDER: 'openrouter',       // openai/gpt-5.6-luna via OpenRouter
TTS_PROVIDER: 'siliconflow'       // CosyVoice2
```

### 4. API Key Requirements

You only need the API keys for the providers you plan to use:

| Provider | ASR | LLM | TTS | Required API Key |
|----------|-----|-----|-----|------------------|
| OpenAI | ✅ Whisper | ✅ gpt-5.6-luna | ❌ | `OPENAI_API_KEY` |
| OpenRouter | ❌ | ✅ gpt-5.6-luna, Gemini | ❌ | `OPENROUTER_API_KEY` |
| ARK (Doubao) | ❌ | ✅ Doubao | ❌ | `ARK_API_KEY` |
| Siliconflow | ✅ SenseVoice | ❌ | ✅ CosyVoice2 | `SILICONFLOW_API_KEY` |

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

3. (Optional) **Verify your setup**: `cd backend && npm run check`

4. Start the backend server (WebSocket server on port **8848**): 
   ```bash
   cd backend && npm start
   ```
   You should see `Server is running on 0.0.0.0:8848`.

5. Start the frontend development server (on port **3000**): 
   ```bash
   cd frontend && npm run dev
   ```

6. Open http://localhost:3000 in your browser (Chrome recommended)

7. Click "Start Recording" and grant microphone permission to begin a conversation

**Expected behavior**: after you finish speaking, the backend detects ~500 ms of silence (VAD), transcribes your speech (ASR), streams an LLM reply, and synthesizes it back as audio (TTS) that plays automatically. The on-screen log panel shows per-stage latency (WebSocket RTT, transcription, LLM, TTS). If you start speaking again while the assistant is talking, playback is interrupted.

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
- ✅ TTS provider functionality (CosyVoice2 via Siliconflow)
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

For provider configuration, see [`backend/config.js.example`](backend/config.js.example) and the provider implementations under [`backend/utils/providers/`](backend/utils/providers).

## License

MIT

