# Orpheus TTS - Text-to-Speech Fine-tuning with Unsloth

This project demonstrates how to fine-tune the Orpheus 3B text-to-speech model using Unsloth for efficient training and inference.

## Overview

Orpheus is a text-to-speech (TTS) model that converts text into natural-sounding speech. This implementation uses:
- **Unsloth** for efficient LoRA fine-tuning (30% less VRAM, 2x larger batch sizes)
- **SNAC** (Stochastic Neural Audio Codec) for audio tokenization at 24kHz
- **Hugging Face Transformers** for model training and inference

## Features

- ✅ Fine-tune Orpheus 3B model with minimal GPU memory
- ✅ Support for single-speaker and multi-speaker TTS
- ✅ **Expressive speech with emotion tags** (laugh, sigh, gasp, etc.)
- ✅ Audio generation with customizable parameters
- ✅ Automatic WAV file export of generated speech
- ✅ LoRA adapter training for efficient fine-tuning

## Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended: 16GB+ VRAM)
- CUDA toolkit installed

### Install Dependencies

**IMPORTANT**: The `datasets` package version must be between 3.4.1 and 4.0.0 for compatibility.

```bash
pip install sentencepiece protobuf "datasets>=3.4.1,<4.0.0" "huggingface_hub>=0.34.0" hf_transfer
pip install -r requirements.txt
```

For Colab or specific environments, you may need:
```bash
pip install --no-deps bitsandbytes accelerate xformers peft trl triton cut_cross_entropy unsloth_zoo
pip install --no-deps unsloth
```

## Project Structure

```
orpheus/
├── orpheus_sft_unsloth.py    # Full training + inference script
├── inference.py               # Standalone inference script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── lora_model/               # Saved LoRA adapters (after training)
└── generated_audio/          # Generated audio outputs
```

## Usage

### Training

Fine-tune the model on your dataset:

```bash
python orpheus_sft_unsloth.py
```

The training script will:
1. Load the pre-trained Orpheus 3B model
2. Apply LoRA adapters for efficient fine-tuning
3. Train on the MrDragonFox/Elise dataset (or your custom dataset)
4. Save the fine-tuned LoRA adapters to `lora_model/`

**Training Parameters:**
- Batch size: 1 per device
- Gradient accumulation: 4 steps
- Learning rate: 2e-4
- Training steps: 60 (configurable)
- LoRA rank: 64

### Inference

Generate speech from text using the fine-tuned model:

```bash
python inference.py
```

Or use it as a module:

```python
from inference import OrpheusInference

# Initialize the model
tts = OrpheusInference(
    model_path="unsloth/orpheus-3b-0.1-ft",
    lora_path="lora_model"  # Optional: load fine-tuned adapters
)

# Generate speech with emotion tags
prompts = [
    "Hey there my name is Elise, <giggles> and I'm a speech generation model.",
    "I missed you <laugh> so much! It's been way too long.",
    "This is absolutely amazing <gasp> I can't believe it worked!"
]

audio_files = tts.generate(
    prompts=prompts,
    output_dir="generated_audio",
    temperature=0.6,
    top_p=0.95,
    max_new_tokens=1200
)

print(f"Generated {len(audio_files)} audio files")
```

### Emotion Tags (Expressive Speech)

Orpheus supports special emotion/expression tags to create more expressive and natural-sounding speech:

**Supported Tags:**
- **Laughter**: `<laugh>`, `<giggles>`, `<chuckle>`
- **Emotions**: `<sigh>`, `<gasp>`
- **Physical sounds**: `<yawn>`, `<cough>`, `<sniffle>`, `<groan>`

**Usage:**
```python
prompts = [
    "Hey there <giggles> welcome to my channel!",
    "I missed you <laugh> so much!",
    "That's so beautiful <sigh> it brings back memories.",
    "I'm so tired <yawn> after working all day.",
    "This is incredible <gasp> I can't believe my eyes!"
]

audio_files = tts.generate(prompts=prompts)
```

**How it works:**
- Tags are enclosed in angle brackets: `<tag>`
- During training, the model learns to associate these tags with audio patterns
- The Elise dataset contains 336 occurrences of "laughs", 156 of "sighs", etc.
- If your custom dataset lacks these tags, you can manually annotate transcripts where the audio contains those expressions

### Multi-Speaker Support

For multi-speaker models, specify the voice name:

```python
tts.generate(
    prompts=["This is a test <laugh> with emotion."],
    voice="speaker_name"  # Specify the speaker
)
```

## Dataset Format

The training script expects datasets with the following structure:

**Single-speaker:**
- `text`: The text to be spoken
- `audio`: Audio file with `array` and `sampling_rate` fields

**Multi-speaker:**
- `source`: Speaker identifier
- `text`: The text to be spoken
- `audio`: Audio file with `array` and `sampling_rate` fields

Example dataset: [MrDragonFox/Elise](https://huggingface.co/datasets/MrDragonFox/Elise)

## Model Architecture

### Audio Tokenization (SNAC)
- Sample rate: 24kHz
- Multi-layer hierarchical codec (3 layers)
- 7 tokens per frame (1 + 2 + 4 from the three layers)
- Duplicate frame removal for efficiency

### Special Tokens
- Start of human: 128259
- End of human: 128260
- Start of AI: 128261
- End of AI: 128262
- Start of speech: 128257
- End of speech: 128258
- Pad token: 128263

## Output

Generated audio files are saved as WAV files in the `generated_audio/` directory:
- Format: WAV (PCM)
- Sample rate: 24kHz
- Naming: `output_0.wav`, `output_1.wav`, etc.

## Memory Usage

Typical memory requirements:
- Training: ~12-16GB VRAM (with LoRA and 4-bit quantization)
- Inference: ~8-10GB VRAM
- CPU RAM: ~16GB recommended

## Troubleshooting

### Common Issues

**1. Dataset version error:**
```
Ensure datasets>=3.4.1,<4.0.0 is installed
pip install "datasets>=3.4.1,<4.0.0" --force-reinstall
```

**2. CUDA out of memory:**
- Reduce `max_new_tokens` during inference
- Use `load_in_4bit=True` when loading the model
- Reduce batch size or enable gradient checkpointing

**3. Multi-GPU issues:**
- Set `CUDA_VISIBLE_DEVICES=0` to use only one GPU
- `per_device_train_batch_size >1` may cause errors on multi-GPU setups

## Performance Tips

1. **Faster Inference**: Use `FastLanguageModel.for_inference(model)` before generation
2. **Memory Optimization**: Enable 4-bit quantization with `load_in_4bit=True`
3. **Better Quality**: Adjust `temperature` (0.4-0.8) and `top_p` (0.9-0.95) parameters
4. **Longer Audio**: Increase `max_new_tokens` (each ~7 tokens = 1 audio frame)

## Resources

- [Unsloth Documentation](https://docs.unsloth.ai/)
- [Unsloth TTS Guide](https://docs.unsloth.ai/basics/text-to-speech-tts-fine-tuning)
- [SNAC Model](https://huggingface.co/hubertsiuzdak/snac_24khz)
- [Orpheus Model](https://huggingface.co/unsloth/orpheus-3b-0.1-ft)
- [Discord Support](https://discord.gg/unsloth)

## License

This project uses models and libraries with their respective licenses:
- Unsloth: Apache 2.0
- Transformers: Apache 2.0
- Orpheus model: Check model card on Hugging Face

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{orpheus-tts-unsloth,
  title={Orpheus TTS Fine-tuning with Unsloth},
  author={Unsloth AI Team},
  year={2024},
  url={https://github.com/unslothai/unsloth}
}
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- Thanks to [Etherl](https://huggingface.co/Etherll) for creating the original notebook
- Unsloth AI team for the efficient training framework
- Hugging Face for hosting models and datasets

