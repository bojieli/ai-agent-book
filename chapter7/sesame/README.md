# Sesame CSM (1B) TTS - Text-to-Speech Fine-tuning

This directory contains scripts for fine-tuning and running inference with the Sesame CSM text-to-speech model using Unsloth.

## Files

- `sesame_csm_sft_unsloth.py` - Training script for fine-tuning the model with LoRA
- `inference.py` - Single inference script for generating speech from text
- `batch_inference.py` - Batch inference script for processing multiple texts
- `example_inputs.json` - Example input file for batch inference
- `requirements.txt` - Python dependencies

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For Conda users, install ffmpeg
conda install -c conda-forge "ffmpeg>=6.0" -y
conda install -c conda-forge libiconv -y
```

## Training

To train a model with your own dataset:

```bash
python sesame_csm_sft_unsloth.py
```

This will:
1. Load the base model `unsloth/csm-1b`
2. Add LoRA adapters
3. Fine-tune on your dataset
4. Save the LoRA adapters to `lora_model/`

## Inference

### Single Text Inference

Generate speech from a single text:

```bash
# Without context (simple generation)
python inference.py \
    --lora-path lora_model \
    --text "We just finished fine tuning a text to speech model... and it's pretty good!" \
    --output example_without_context_1.wav

# With voice context (for voice consistency) using dataset index 3
python inference.py \
    --lora-path lora_model \
    --text "Sesame is a super cool TTS model which can be fine tuned with Unsloth." \
    --dataset-context-idx 3 \
    --output example_with_context_1.wav

# Using base model only (without LoRA)
python inference.py \
    --text "Hello world, this is a test of the text to speech system."

# With custom speaker ID and longer generation
python inference.py \
    --lora-path lora_model \
    --text "This is a longer sentence that needs more tokens." \
    --speaker-id 0 \
    --max-tokens 250 \
    --output long_speech.wav

# With 4-bit quantization (lower memory)
python inference.py \
    --lora-path lora_model \
    --text "Memory efficient inference." \
    --load-in-4bit
```

### Batch Inference

Process multiple texts at once:

```bash
# From JSON file
python batch_inference.py \
    --lora-path lora_model \
    --input-file example_inputs.json \
    --output-dir batch_outputs

# From plain text file (one text per line)
python batch_inference.py \
    --lora-path lora_model \
    --input-file texts.txt \
    --output-dir batch_outputs
```

#### Input File Formats

**JSON format** (`example_inputs.json`):

Without context:
```json
[
    {
        "text": "We just finished fine tuning a text to speech model... and it's pretty good!",
        "speaker_id": 0,
        "output": "example_without_context_1.wav"
    },
    {
        "text": "Sesame is a super cool TTS model which can be fine tuned with Unsloth.",
        "speaker_id": 0,
        "output": "example_without_context_2.wav"
    }
]
```

With context (for voice consistency using dataset indices):
```json
[
    {
        "text": "Sesame is a super cool TTS model which can be fine tuned with Unsloth.",
        "speaker_id": 0,
        "dataset_context_idx": 3,
        "output": "example_with_context_1.wav"
    },
    {
        "text": "We just finished fine tuning a text to speech model... and it's pretty good!",
        "speaker_id": 0,
        "dataset_context_idx": 4,
        "output": "example_with_context_2.wav"
    }
]
```

**Note**: `dataset_context_idx` refers to the index in the training dataset (e.g., `MrDragonFox/Elise`). Indices 3 and 4 are used in the training script examples.

**Plain text format** (one sentence per line, no context support):
```
Hello world, this is the first sentence.
This is the second sentence.
This is the third sentence.
```

## Parameters

### Common Parameters

- `--base-model`: Base model name or path (default: `unsloth/csm-1b`)
- `--lora-path`: Path to saved LoRA adapters (optional)
- `--load-in-4bit`: Load model in 4-bit quantization to reduce memory usage

### Inference Parameters

- `--text`: Text to convert to speech
- `--speaker-id`: Speaker ID for multi-speaker models (default: 0)
- `--output`: Output audio file path (default: `output.wav`)
- `--max-tokens`: Maximum tokens to generate (125 ≈ 10 seconds of audio)
- `--dataset-context-idx`: Dataset index to use for voice consistency (e.g., 3 or 4 from training examples)
- `--dataset-name`: Dataset name to load context from (default: `MrDragonFox/Elise`)

### Batch Inference Parameters

- `--input-file`: Input file (JSON or plain text)
- `--output-dir`: Output directory for audio files (default: `outputs`)

## Model Information

- **Base Model**: Sesame CSM (1B) - A compact text-to-speech model
- **Output Format**: 24kHz WAV audio
- **Token-to-Time Ratio**: Approximately 125 tokens = 10 seconds of audio
- **Multi-speaker**: Supports multiple speakers via speaker IDs

## Advanced Usage

### Voice Consistency with Context

For better voice consistency, you can provide audio context from the dataset (see `sesame_csm_sft_unsloth.py` lines 320-390 for examples):

```python
from inference import load_model, generate_speech

model, processor = load_model("unsloth/csm-1b", "lora_model")

# Use dataset index 3 for voice consistency (same as training script)
generate_speech(
    model=model,
    processor=processor,
    text="Sesame is a super cool TTS model which can be fine tuned with Unsloth.",
    dataset_context_idx=3,
    dataset_name="MrDragonFox/Elise",
    output_path="output_with_context.wav"
)
```

The inference scripts automatically load the audio and text from the specified dataset index, ensuring consistency with the training approach.

## Memory Requirements

- **Base model**: ~4-6GB VRAM
- **Base model + LoRA training**: ~8-12GB VRAM
- **With 4-bit quantization**: ~2-3GB VRAM
- **Inference only**: ~2-4GB VRAM

Use `--load-in-4bit` flag if you have limited GPU memory.

## Troubleshooting

### AssertionError during generation

If you encounter `AssertionError` during `model.generate()`, ensure you're passing tensors correctly:

```python
# ❌ Wrong
audio_values = model.generate(**inputs, max_new_tokens=125)

# ✅ Correct
audio_values = model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs.get("attention_mask"),
    max_new_tokens=125,
    output_audio=True
)
```

### Out of memory

- Use `--load-in-4bit` flag
- Reduce `max_new_tokens`
- Process texts one at a time instead of batching
- Use a smaller batch size during training

## Resources

- [Unsloth Documentation](https://docs.unsloth.ai/)
- [Unsloth TTS Guide](https://docs.unsloth.ai/basics/text-to-speech-tts-fine-tuning)
- [Unsloth Discord](https://discord.gg/unsloth)
- [Unsloth GitHub](https://github.com/unslothai/unsloth)

## License

This project uses the Unsloth library and Sesame CSM model. Please refer to their respective licenses.

