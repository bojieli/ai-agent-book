# FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness

**Authors**: Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, Christopher Ré (Stanford University)

**Venue**: NeurIPS 2022

## Abstract

Transformers are slow and memory-hungry on long sequences, since the time and
memory complexity of self-attention are quadratic in sequence length. We argue
that a missing principle is making attention algorithms *IO-aware* — accounting
for reads and writes between levels of GPU memory. We propose **FlashAttention**,
an IO-aware exact attention algorithm that uses tiling to reduce the number of
memory reads/writes between GPU high-bandwidth memory (HBM) and on-chip SRAM.
FlashAttention trains Transformers faster than existing baselines: 15% end-to-end
speedup on BERT-large, 3x speedup on GPT-2, and enables longer context, yielding
higher quality models (0.7 better perplexity on GPT-2) and entirely new
capabilities (the first Transformers to achieve better-than-chance performance
on Path-X with 16K sequence length).

## 1. Introduction

Transformer models have grown larger and deeper, but equipping them with longer
context remains difficult, because the self-attention module at their heart has
time and memory complexity **quadratic** in sequence length. A key question is
whether making attention faster and more memory-efficient can help Transformer
models address their runtime and memory challenges for long sequences.

Many approximate attention methods (sparse, low-rank) aim to reduce the compute
and memory requirements. Although these methods reduce the FLOP count, they often
do not achieve wall-clock speedup, mainly because they focus on FLOP reduction
and ignore overheads from **memory access (IO)**.

Our main observation is that the principal missing ingredient is making attention
algorithms **IO-aware** — carefully accounting for reads and writes to different
levels of fast and slow memory (e.g., between fast on-chip SRAM and relatively
slow HBM on a GPU).

## 2. Background: GPU Memory Hierarchy

A GPU has a memory hierarchy with different bandwidth/size trade-offs:

| Memory level | Size (A100) | Bandwidth |
|--------------|-------------|-----------|
| SRAM (on-chip) | 20 MB | 19 TB/s |
| HBM (main GPU) | 40-80 GB | 1.5-2.0 TB/s |
| CPU DRAM | > 1 TB | 12.8 GB/s |

Standard attention implementations materialize the large N x N attention matrix S
and P to HBM, incurring O(N^2) HBM accesses. Since HBM is much slower than SRAM,
this memory traffic dominates the runtime for long sequences.

## 3. Method: FlashAttention

FlashAttention computes exact attention with far fewer HBM accesses via two
classical techniques adapted to attention:

- **Tiling**: split the inputs Q, K, V into blocks, load them from slow HBM to
  fast SRAM, compute attention per block, and accumulate the output. We never
  materialize the full N x N attention matrix in HBM.
- **Softmax rescaling / recomputation**: the softmax normalization is computed
  incrementally across blocks using online softmax; in the backward pass, the
  attention matrix is recomputed on-chip from stored statistics rather than
  read from HBM.

The result is an algorithm with **O(N^2 d)** FLOPs but only **O(N^2 d^2 / M)**
HBM accesses, where M is the SRAM size and d is the head dimension. For typical
values, this is many times fewer HBM accesses than standard attention.

## 4. Experiments and Results

FlashAttention delivers strong end-to-end and micro-benchmark results:

- **BERT-large** (seq. 512): 15% faster training than the MLPerf 1.1 record.
- **GPT-2** (seq. 1K): up to **3x** end-to-end speedup over HuggingFace and
  Megatron-LM implementations, with identical model quality.
- **Long-range Arena** (1K-4K): 2.4x speedup vs standard attention.
- **Long context quality**: enabling 4K context on GPT-2 gives **0.7 better
  perplexity**; a Path-X task with 16K sequence becomes solvable for the first
  time (61.4% accuracy), and block-sparse FlashAttention solves Path-256 (63.1%).

Memory usage scales **linearly** in sequence length (versus quadratic for
standard attention), up to 20x memory savings at long sequence lengths.

## 5. Conclusion

By treating attention as an IO-bound problem and minimizing HBM accesses through
tiling and recomputation, FlashAttention computes exact attention faster and with
a smaller memory footprint than approximate methods, while remaining numerically
exact. IO-awareness is a broadly useful principle: we hope FlashAttention
inspires IO-aware implementations of more deep learning primitives.
