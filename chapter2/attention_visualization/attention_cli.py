"""
Attention Visualization CLI
===========================

Command-line tool that renders the self-attention heatmap of a real
language model for an arbitrary prompt, letting you pick which layer and
head to inspect. This is the standalone counterpart to the interactive
frontend: instead of saving a trajectory JSON for the React app, it writes
a publication-ready PNG directly.

It reproduces the two patterns discussed in Chapter 2 ("实验 2-2 注意力机制
可视化"):

  * the **attention sink** - the first token soaking up a large,
    disproportionate share of every row's attention, and
  * the **causal triangle** - each token only attending to itself and the
    tokens before it.

Examples
--------
    # Single heatmap for the default prompt (last layer, heads averaged)
    python attention_cli.py

    # Custom prompt, inspect layer 0, head 3, save to a chosen path
    python attention_cli.py --prompt "北京 的 天气 怎么样" \
        --layer 0 --head 3 --output layer0_head3.png

    # Let the model generate a short continuation, then visualize the
    # attention over the whole prompt+generation sequence
    python attention_cli.py --prompt "Explain attention in one sentence." \
        --max-new-tokens 40

    # Compare two layers of the same prompt side by side
    python attention_cli.py --compare-layers 0 -1 --output layer_compare.png

Model weights (Qwen/Qwen3-0.6B, ~1-2 GB) are downloaded on first run.
"""

import argparse
import sys

import numpy as np


DEFAULT_PROMPT = "北京 的 天气 怎么样"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="attention_cli.py",
        description=(
            "Visualize a language model's self-attention as a heatmap. "
            "Pick the layer/head, optionally generate a continuation, and "
            "save the figure. Demonstrates the attention-sink and causal-"
            "triangle patterns from Chapter 2."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python attention_cli.py\n"
            "  python attention_cli.py --prompt '北京 的 天气 怎么样' --layer 0 --head 3\n"
            "  python attention_cli.py --prompt 'Explain attention.' --max-new-tokens 40\n"
            "  python attention_cli.py --compare-layers 0 -1 -o layer_compare.png\n"
        ),
    )

    io_group = parser.add_argument_group("input / output")
    io_group.add_argument(
        "-p", "--prompt", default=DEFAULT_PROMPT,
        help="Text to visualize attention for (default: %(default)r).",
    )
    io_group.add_argument(
        "-o", "--output", default="attention_heatmap.png",
        help="Path to write the heatmap PNG (default: %(default)s).",
    )
    io_group.add_argument(
        "--no-chat-template", action="store_true",
        help="Feed the raw prompt instead of wrapping it in the model's "
             "chat template. Use this to see the plain token stream without "
             "<|im_start|> / <|im_end|> markers.",
    )

    model_group = parser.add_argument_group("model")
    model_group.add_argument(
        "-m", "--model", default="Qwen/Qwen3-0.6B",
        help="Hugging Face model name or local path (default: %(default)s).",
    )
    model_group.add_argument(
        "--device", default=None, choices=["cuda", "mps", "cpu"],
        help="Device to run on (default: auto-detect).",
    )

    attn_group = parser.add_argument_group("attention selection")
    attn_group.add_argument(
        "-l", "--layer", type=int, default=-1,
        help="Transformer layer index to visualize; -1 is the last layer "
             "(default: %(default)s).",
    )
    attn_group.add_argument(
        "--head", type=int, default=-1,
        help="Attention head index to visualize; -1 averages over all heads "
             "(default: %(default)s).",
    )
    attn_group.add_argument(
        "--compare-layers", type=int, nargs="+", metavar="LAYER", default=None,
        help="Instead of a single heatmap, render these layer indices side "
             "by side for the same prompt (e.g. --compare-layers 0 -1).",
    )

    gen_group = parser.add_argument_group("generation")
    gen_group.add_argument(
        "--max-new-tokens", type=int, default=0,
        help="Generate this many tokens before capturing attention over the "
             "full prompt+generation sequence. 0 = visualize the prompt only "
             "(default: %(default)s).",
    )
    gen_group.add_argument(
        "--temperature", type=float, default=0.7,
        help="Sampling temperature when generating (default: %(default)s).",
    )

    viz_group = parser.add_argument_group("visualization")
    viz_group.add_argument(
        "--cmap", default="viridis",
        help="Matplotlib colormap (default: %(default)s).",
    )
    viz_group.add_argument(
        "--no-sink-annotation", action="store_true",
        help="Do not annotate the measured attention-sink share in the title.",
    )

    return parser


def build_input_ids(agent, prompt: str, use_chat_template: bool):
    """Tokenize the prompt, optionally via the model's chat template."""
    if use_chat_template:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ]
        text = agent.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        text = prompt
    inputs = agent.tokenizer(text, return_tensors="pt", truncation=False)
    return {k: v.to(agent.device) for k, v in inputs.items()}


def extract_layer_matrix(attentions, layer: int, head: int) -> np.ndarray:
    """
    Extract a [seq, seq] matrix from a HF `attentions` tuple.

    attentions: tuple(len = num_layers) of tensors [batch, heads, seq, seq].
    head < 0 averages over heads; otherwise selects one head.
    """
    num_layers = len(attentions)
    if not -num_layers <= layer < num_layers:
        raise ValueError(
            f"Layer index {layer} out of range for a {num_layers}-layer model "
            f"(valid: {-num_layers}..{num_layers - 1})."
        )
    layer_attn = attentions[layer][0]  # [heads, seq, seq]
    num_heads = layer_attn.shape[0]
    if head < 0:
        matrix = layer_attn.mean(dim=0)
    else:
        if not 0 <= head < num_heads:
            raise ValueError(
                f"Head index {head} out of range for {num_heads} heads "
                f"(valid: 0..{num_heads - 1})."
            )
        matrix = layer_attn[head]
    return matrix.float().cpu().numpy()


def run(args) -> int:
    # Heavy imports deferred so that --help and argument parsing stay fast
    # and work even without torch / a downloaded model.
    import torch
    from agent import AttentionVisualizationAgent
    from visualization import (
        create_attention_comparison,
        create_layer_attention_heatmap,
        attention_sink_stats,
    )

    agent = AttentionVisualizationAgent(
        model_name=args.model,
        device=args.device,
        attention_layer_index=args.layer,
        verbose=True,
    )

    use_chat_template = not args.no_chat_template
    inputs = build_input_ids(agent, args.prompt, use_chat_template)
    context_length = inputs["input_ids"].shape[1]

    # Optionally extend the sequence with a real generation so the heatmap
    # covers prompt + model output.
    if args.max_new_tokens > 0:
        print(f"Generating up to {args.max_new_tokens} tokens...")
        with torch.no_grad():
            gen = agent.model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=args.temperature > 0,
                temperature=max(args.temperature, 1e-5),
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=agent.tokenizer.pad_token_id,
            )
        full_ids = gen[0].unsqueeze(0)
    else:
        full_ids = inputs["input_ids"]

    token_ids = full_ids[0].tolist()
    tokens = [agent.tokenizer.decode([tid], skip_special_tokens=False)
              for tid in token_ids]
    print(f"Sequence length: {len(tokens)} tokens "
          f"(prompt: {context_length}, generated: {len(tokens) - context_length})")

    # Single forward pass over the full sequence to get attention weights.
    with torch.no_grad():
        outputs = agent.model(
            input_ids=full_ids,
            output_attentions=True,
            return_dict=True,
        )
    attentions = outputs.attentions
    if not attentions:
        print("ERROR: model returned no attention weights. Ensure the model "
              "is loaded with attn_implementation='eager'.", file=sys.stderr)
        return 1
    print(f"Captured attention: {len(attentions)} layers, "
          f"{attentions[0].shape[1]} heads each.")

    head_desc = "avg heads" if args.head < 0 else f"head {args.head}"

    if args.compare_layers:
        matrices, titles, tokens_list = [], [], []
        for layer in args.compare_layers:
            matrix = extract_layer_matrix(attentions, layer, args.head)
            matrices.append(matrix)
            tokens_list.append(tokens)
            titles.append(f"Layer {layer} ({head_desc})")
        fig = create_attention_comparison(
            matrices, tokens_list, titles,
            save_path=args.output, cmap=args.cmap,
            suptitle=f"Attention comparison - '{args.prompt[:40]}'",
        )
        for layer, matrix in zip(args.compare_layers, matrices):
            stats = attention_sink_stats(matrix)
            print(f"  layer {layer:>3}: attention sink mean "
                  f"{stats['mean_sink_share'] * 100:.1f}%  "
                  f"max {stats['max_sink_share'] * 100:.1f}%")
    else:
        matrix = extract_layer_matrix(attentions, args.layer, args.head)
        stats = attention_sink_stats(matrix)
        print(f"Attention sink (token 0): mean "
              f"{stats['mean_sink_share'] * 100:.1f}%  "
              f"max {stats['max_sink_share'] * 100:.1f}% of each row.")
        fig = create_layer_attention_heatmap(
            matrix, tokens,
            title=f"Layer {args.layer} ({head_desc}) - '{args.prompt[:40]}'",
            save_path=args.output, cmap=args.cmap,
            context_boundary=context_length if args.max_new_tokens > 0 else None,
            annotate_sink=not args.no_sink_annotation,
        )

    print(f"Saved heatmap to {args.output}")

    try:
        import matplotlib.pyplot as plt
        plt.close(fig)
    except Exception:
        pass
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.head < -1:
        parser.error("--head must be -1 (average) or a non-negative head index.")
    if args.max_new_tokens < 0:
        parser.error("--max-new-tokens must be >= 0.")

    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
