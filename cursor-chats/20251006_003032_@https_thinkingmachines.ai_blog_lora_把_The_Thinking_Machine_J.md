# Cursor Chat: ai-agent-book

## Metadata
- **Project**: ai-agent-book
- **Path**: `/Users/boj`
- **Date**: 2025-10-06 00:30:32
- **Session ID**: `55ef0821-e7f0-44e0-92db-8e6b253d5d88`

## Conversation

### 👤 You

@https://thinkingmachines.ai/blog/lora/ 把 The Thinking Machine John Schulmann 这篇文章中的关键技巧和发现总结到文中，并注明出处

---

### 🤖 Cursor Assistant

I'll read the current chapter and then add a summary of the key findings from the Thinking Machines LoRA article.

---

### 🤖 Cursor Assistant

现在我将把 Thinking Machines 文章中的关键发现总结并添加到 LoRA 技巧部分：

---

### 🤖 Cursor Assistant

完成！我已经将 Thinking Machines 的 John Schulman 团队关于 LoRA 的重要研究成果总结并添加到了第七章中。总结内容包括：

### 主要添加的内容：

1. **核心发现**
   - LoRA 何时能达到全量微调的效果（"低遗憾区间"）
   - 关键配置要素（全层应用、rank 选择、学习率调优）
   - 批量大小的敏感性
   - 强化学习中的优势（仅需小 rank）
   - 计算效率优势（约 2/3 FLOPs）
   - 运维优势（多租户服务、内存占用、快速迁移）

2. **容量需求的理论分析**
   - 监督学习：每参数 2 bits，每 token 约 1 bit 损失
   - 强化学习：每 episode 约 1 bit 信息，基于互信息理论分析

3. **实践建议**
   - 6 条具体的应用建议，包括全层应用、rank 选择、学习率调优、RL 场景使用等

4. **引用标注**
   - 使用脚注格式标注了原文出处，包括作者、标题、出版方、时间和 URL

所有内容都已整合到原有章节结构中，并保持了中文写作风格的一致性。

---

### 👤 You

THINKING MACHINES
Tinker
Blog
Join us
LoRA Without Regret
John Schulman in collaboration with others at Thinking Machines
Sep 29, 2025
A
r  k
x
B
d  r
x
ΔW   B  A
=x
x 
γ
d  k
x
Introduction
What matters for LoRA
Methods and results
LoRA rank
Batch size effects
Layers Where LoRA Is Applied
Reinforcement learning
Setting LoRA hyperparameters
Optimal learning rate and rank
Parametrization invariances
Optimal learning rates for LoRA vs. FullFT
Learning rates in short and long runs
Discussion
Why LoRA might be needed on all layers
How much capacity is needed by supervised and reinforcement learning?
Compute efficiency advantage of LoRA
Open questions
Closing thoughts
Acknowledgements
Citation
Today’s leading language models contain upwards of a trillion parameters, pretrained on tens of trillions of tokens. Base model performance keeps improving with scale, as these trillions are necessary for learning and representing all the patterns in written-down human knowledge.

In contrast, post-training involves smaller datasets and generally focuses on narrower domains of knowledge and ranges of behavior. It seems wasteful to use a terabit of weights to represent updates from a gigabit or megabit of training data. This intuition has motivated parameter efficient fine-tuning (PEFT), which adjusts a large network by updating a much smaller set of parameters.

The leading PEFT method is low-rank adaptation, or LoRA. LoRA replaces each weight matrix W from the original model with a modified version 
W
′
=
W
+
γ
B
A
W 
′
 =W+γBA, where B and A are matrices that together have far fewer parameters than W, and 
γ
γ is a constant scaling factor. In effect, LoRA creates a low-dimensional representation of the updates imparted by fine-tuning.

LoRA may offer advantages in the cost and speed of post-training, and there are also a few operational reasons to prefer it to full fine-tuning (henceforth, FullFT):

Multi-tenant serving. Since LoRA trains an adapter (i.e., the A and B matrices) while keeping the original weights unchanged, a single inference server can keep many adapters (different model versions) in memory and sample from them simultaneously in a batched way.Punica: Multi-Tenant LoRA Serving (Chen, Ye, et al, 2023) Modern inference engines such as vLLM and SGLang implement this feature.

Layout size for training. When fine-tuning the whole model, the optimizer state needs to be stored along with the original weights, often at higher precision. As a result, FullFT usually requires an order of magnitude more accelerators than sampling from the same model does, and thus a different layout.For training, besides storing the weights, we typically need to store gradients and optimizer moments for all of the weights; moreover, these variables are often stored in higher precision (float32) than what’s used to store the weights for inference (bfloat16 or lower). Since LoRA trains far fewer weights and uses far less memory, it can be trained on a layout only slightly larger than what is used for sampling. This makes training more accessible, and often more efficient.

Ease of loading and transfer. With fewer weights to store, LoRA adapters are fast and easy to set up or transfer between machines.

These reasons are sufficient to explain the growing popularity of LoRA since the publication of the original LoRA paper in 2021.LoRA: Low-Rank Adaptation of Large Language Models (Hu et al, 2021) However, the literature is unclear on how well LoRA performs relative to FullFT.

There is agreement that LoRA underperforms in settings that resemble pre-training,LoRA Learns Less and Forgets Less (Biderman et al, 2024) namely those with very large datasets that exceed the storage limits of LoRA parameters. But for dataset sizes that are typical in post-training, LoRA has sufficient capacity to store the essential information. However, this fact makes no guarantees regarding sample efficiency and compute efficiency. The question is: can LoRA match the performance of full fine-tuning, and if so, under which conditions?

In our experiments, we find that indeed, when we get a few key details right, LoRA learns with the same sample efficiency as FullFT and achieves the same ultimate performance.

What matters for LoRA#
This article covers a series of supervised fine-tuning and reinforcement learning experiments we conducted to determine the conditions under which LoRA matches FullFT efficiency. To this end, we did a few things differently from previous experiments on LoRA:

We investigated the general relationship between training set size and number of LoRA parameters, rather than focusing on specific datasets and tasks.

In supervised learning, we measured log loss rather than employing sampling-based evals, with the same goal of generality in mind. Log loss measurement gives clean results and scaling laws over ranges of training steps and training parameters.

We find that:

For supervised fine-tuning on small-to-medium-sized instruction-tuning and reasoning datasets, LoRA performs the same as full fine-tuning.

For datasets that exceed LoRA capacity, LoRA underperforms FullFT. Rather than the loss reaching a distinct floor that it can’t go below, LoRA results in worse training efficiency that depends on the relationship between model capacity to dataset size.

In some scenarios, LoRA is less tolerant of large batch sizes than full fine-tuning — it pays a larger penalty in loss as batch size increases beyond some point. This penalty is not mitigated by increasing the LoRA rank; it is a property of the product-of-matrices parametrization, which has different training dynamics than optimizing the original weight matrix.

Even in small data settings, LoRA performs better when applied to all weight matrices, especially MLP and MoE layers. Attention-only LoRA underperforms even when we match the number of trainable parameters by using higher rank for attention-only LoRA.

LoRA performs equivalently to FullFT for reinforcement learning even with small ranks. We find that RL requires very low capacity, a result we anticipated based on information-theoretical arguments.

We also studied the impact of hyperparameters used for LoRA on its learning rate relative to full fine-tuning. We examine some invariances in hyperparameters like init scales and multipliers, and explain why the 1/r prefactor makes the optimal learning rate (LR) approximately independent of rank. We also show experimentally how the optimal LR for LoRA relates to the optimal LR for FullFT.

The outcome of our experiments is the characterization of a “low-regret regime” where LoRA performs similarly to FullFT in terms of dataset size and LoRA parameters. We found this regime covers most post-training scenarios, opening the door to the use of efficient fine-tuning in many applications.

Methods and results#
We designed our experiments to measure in detail the relative performance of LoRA compared to FullFT across a range of conditions. Here are some details of our experimental setup:

We varied the LoRA rank over three orders of magnitude, with rank between 1 and 512, and compared these to full fine-tuning.

To eliminate potential confounds from using a suboptimal learning rate, we swept the LR for each experimental condition. We used constant learning rate schedule (no warmup or cooldown).

Our experiments used Llama 3 series modelsThe Llama 3 Herd of Models (Dubey et al, 2024) and Qwen3 modelsQwen3 Technical Report (Qwen Team, 2025), including a mixture of experts (MoE) model.

The main supervised learning experiments used the Tulu3Tulu 3: Pushing Frontiers in Open Language Model Post-Training (Ivison et al, 2024) and OpenThoughts3OpenThoughts: Data Recipes for Reasoning Models (Guha et al, 2025) datasets, focused on instruction following and reasoning, respectively. The two sets differ significantly in scope, structure, and application, supporting the generality of our results.

Our RL experiments used mathematical reasoning tasks with answer correctness as the reward.

LoRA rank#
We trained for a single epoch on the Tulu3 dataset and a subset of the OpenThoughts3 datasets. For each dataset and model size, we swept over LoRA rank and learning rate. In the plots below, we draw one colored line for each rank, where the line is obtained by taking the pointwise minimum over all learning rates at each training step:

LoRA training curves for various ranks on Tulu3 and OpenThoughts3 datasets. FullFT and high-rank LoRAs have similar learning curves with loss decreasing linearly with the logarithm of steps. Lower-rank LoRAs fall off the minimum-loss curve when the adapter runs out of capacity. In the bottom plots (1B model) high-rank LoRA performs better than FullFT on one dataset and worse on the other. There might be some random variation in how LoRA performs on different datasets, due to differences in training dynamics or generalization behavior.
We see that FullFT and high-rank LoRAs have similar learning curves with loss decreasing linearly with the logarithm of the number of steps. Medium and low-rank LoRAs fall off the minimum-loss learning curves at some threshold of steps that correlates with rank. Intuitively, learning slows down when the adapter runs out of capacity, which in turn is determined by rank.

Next, we plot how loss changes with LR to check that our sweep covers the best learning rate for each rank.

Learning rate versus final loss for various LoRA ranks on Tulu3. Minimum loss is approximately the same for high rank LoRA and FullFT. Optimal LR is 10 times higher for LoRA.
We find that the optimal learning rate for FullFT is lower by a factor of 10 than for high-rank LoRAs.See Biderman et al. (2024), Figure S1, for an experiment with sampling evals, which finds a similar 10x ratio. We’ll return to this in our discussion of LoRA hyperparameters later on.

The optimal LR seems to be similar for all the LoRA runs across different ranks; we give a theoretical explanation for this finding below. However, there does seem to be some rank dependence, with lower optimal LR for rank=1 than for higher-rank LoRAs. The optimal LR changes by a factor of less than 2 between rank=4 and rank=512.

Batch size effects#
We found that in some settings, LoRA is less tolerant of large batch sizes than FullFT. The performance gap grows with larger batch sizes, independent of rank. For this next experiment, we used a small 10,000-example subset of OpenThoughts3.

Batch size effects on LoRA vs FullFT performance. Left: Learning curves for different batch sizes show a persistent gap between LoRA (dashed) and FullFT (solid) at large batch sizes. Right: Final loss as a function of batch size shows LoRA pays a larger penalty for increased batch size.
The left-hand plot in Figure 3 shows a persistent gap between the LoRA (dashed lines) and FullFT (solid line) learning curves at large batch sizes. The gap is smaller and shrinks over time for the smaller batch size of 32.

The right-hand chart plots final loss as a function of batch size. We see the gap in loss for LoRA increasingly diverging from FullFT for larger batch sizes.

The learning gap at large batches doesn’t seem to depend on rank, but rather seems to be a property of LoRA. The likely reason is that the product-of-matrices parametrization (BA) has less favorable optimization dynamics on this dataset than the full matrix (W). However, both LoRA and FullFT achieve their best loss at smaller batch sizes, so this gap may not matter as much in practice.

Layers Where LoRA Is Applied#
We investigated the effects of applying LoRA to different layers in the network. The original paper by Hu et al. recommended applying LoRA only to the attention matrices, and many subsequent papers followed suit, though a recent trend has been to apply it to all layers.Similar to our results, the QLoRA paper also found that LoRA performed worse than MLP or MLP+attention, though they found that MLP+attention > MLP > attention, whereas we found the first two to be roughly equal. Indeed, we achieved far better results when applying LoRA to all layers, in particular, the MLP (including MoE) layers. In fact, applying LoRA to the attention matrices shows no additional benefits beyond applying it to the MLPs only.Biderman et al. (2024) obtained a similar result, with attention-only LoRA providing no additional benefit on top of MLP-only.

Attention-only LoRA significantly underperforms MLP-only LoRA, and does not further improve performance on top of LoRA-on-MLP. This effect holds for a dense model (Llama-3.1-8B) and a sparse MoE (Qwen3-30B-A3B-Base).
The underperformance of attention-only LoRA is not explained by having fewer parameters. In this particular case, attention-only with rank 256 underperforms MLP-only with rank 128, despite them having approximately the same number of parameters. (Compare the bold numbers in the table below.)

LoRA configuration	Params
mlp, rank=256	0.49B
attn, rank=256	0.25B
all, rank=256	0.70B
mlp, rank=128	0.24B
Parameter counts for LoRA on Llama-3.1-8B

For the MoE experiment, we trained a separate LoRA on each expert, with the rank of each equal to the total rank divided by the number of active experts (equal to 8 for Qwen3 MoE). This scaling keeps the ratio of LoRA parameters to FullFT parameters the same for MoE layers as for other layers.

We did similar experiments comparing different LoRA layers in two additional settings: (1) supervised learning on a small subset of the OpenThoughts3 dataset with rank=256, and (2) reinforcement learning on the MATH dataset. We describe our experimental setup in the following section. Attention-only LoRA underperforms MLP-only LoRA (which performs similarly to MLP+attention) in these settings as well.

Learning rate vs final loss or reward, when varying which layers we apply LoRA to.
Reinforcement learning#
A key finding from our experiments is that LoRA fully matches the learning performance of FullFT when running policy gradient algorithms for reinforcement learning, even with ranks as low as 1.

For these experiments, we used a basic policy gradient algorithm with an importance sampling correction; 
objective
=
∑
t
p
learner
p
sampler
A
d
v
t
objective=∑ 
t
​
  
p 
sampler
​
 
p 
learner
​
 
​
 Adv 
t
​
 .See Your Efficient RL Framework Secretly Brings You Off-Policy RL Training We used a GRPO-like centering schemeDeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (Shao et al, 2024) where we sample multiple completions per problem and subtract the mean reward per group.

Figure 6 (below) shows LR sweeps on the MATHMeasuring Mathematical Problem Solving With the MATH Dataset (Hendrycks et al, 2021) and GSMGSM8K: Training Verifiers to Solve Math Word Problems (Cobbe et al, 2021) datasets, using typical hyperparameters for each. We used the Llama-3.1-8B base model as Qwen2.5 and Qwen3 are known to have been pretrained on data that improves their math performance, as described by the Qwen tech reportsQwen2.5 Technical Report (Qwen Team, 2024), which makes it harder to measure what is being learned only during RL.

LoRA shows a wider range of performant learning rates and arrives at the same peak performance as FullFT (black line), at least within the precision limits afforded by the noisiness of RL.

Learning rate vs final reward (accuracy) when doing RL on grade school math (GSM, left) or MATH (right) dataset.
This result is anticipated by an information-theoretic argument. Supervised learning arguably provides O(number of tokens) bits per episode. In contrast, in policy gradient methods, learning is driven by the advantage function which provides only O(1) bits per episode. When each episode contains thousands of tokens, RL absorbs ~1000 times less information per token in training than supervised learning does.

We can use more precise numbers based on our experiments. In the MATH example, we trained on ~10,000 problems with 32 samples per problem. Assuming each completion yields a single bit of information, the whole training process only needs to absorb 320,000 bits. Rank-1 LoRA for Llama-3.1-8B already has 3M parametersWe calculated this by adding up rank·
d
i
n
d 
in
​
  (for matrix A) and rank·
d
o
u
t
d 
out
​
  (for B) over all weight matrices in the model., almost 10 times that number. Even at rank-1, LoRA has more than enough capacity to absorb all the information provided during training.

As another point of comparison, DeepSeek-R1-Zero was trained on 5.3M episodesTraining took place for 10,400 steps, each step consisting of 32 unique questions, each question sampled 16 times., corresponding to 5.3M bits of information. This is less than the number of parameters in a low-rank LoRA, and we predict that the results can be replicated with LoRA.

For additional validation of our findings of LoRA’s effectiveness in reasoning RL, we carried out larger-scale experiments with Qwen3-8b-base on the DeepMath datasetDeepMath-103K: A Large-Scale, Challenging, Decontaminated, and Verifiable Mathematical Dataset for Advancing Reasoning (He et al, 2025) as it is much larger than the MATH dataset and in general contains harder problems. To speed up experiments, we restricted the samples to a length of 8192 tokens for training and evaluation. This sample length allows for backtracking and reasoning but limits the performance, relative to longer chain-of-thought.

Experiments on the DeepMath dataset with Qwen3-8b-base. In the left plot, we show the learning curve for different ranks and full fine-tuning. For each of these settings, we show the best learning rate, which results in the highest final performance. On the right, we plot learning rate vs final performance. As in our previous math experiments, LoRA seems to have a wider peak of near-optimal learning rates.
Additional plots from experiments on the DeepMath dataset with Qwen3-8b-Base. The left plot shows the benchmark scores on the AIME test set, which is more challenging than the training set. The right plot shows the chain-of-thought (CoT) length over training steps, which can be seen as a sign of learning to reason.
We observe that when picking the optimal learning rates for each setting, training progresses in an almost identical way for LoRAs with different sizes and full fine-tuning. Moreover, we see similar findings when we evaluate the models on the held-out problems of AIME 2024 and AIME 2025. Furthermore, we observe similar qualitative behavior from the LoRA and full-finetuning runs: both develop advanced reasoning behaviors such as backtracking, self-verification and in-context exploration, which is visible in the lengthening of the model CoTs.

Setting LoRA hyperparameters#
One barrier to LoRA adoption is the necessity to choose optimal hyperparameters, which are different from ones optimized for FullFT. In this section, we show that this problem isn’t as daunting as it appears at first glance and discuss our findings related to hyperparameter choice.

Optimal learning rate and rank#
Following Hu et al., we consider the following parametrization for LoRA:

W
′
=
W
+
α
r
B
A
W 
′
 =W+ 
r
α
​
 BA
Where 
r
r is the LoRA rank, 
α
α is the LoRA scaling factor, and 
A
A, 
B
B are the LoRA weight matrices (of rank 
r
r). We use 
α
=
32
α=32 for the experiments in this article, following standard practice from other implementations.

The 
1
/
r
1/r scaling factor makes the optimal learning rate approximately independent of rank. In fact, a stronger condition holds – the learning curve is exactly the same at the beginning of training, regardless of rank. This effect is striking, and in our experiments the closeness of the learning curves for different ranks had us worried that a bug caused the rank parameter to be ignored. It follows that in a short training regime, the optimal LR is also independent of rank. However, as we showed above in our plots of learning rate vs loss (Figure 2), optimal LR has some rank-dependence in the longer-training regime.

These plots look at the differences in the learning curves, early in training, for different ranks with the same learning rate. On the left, we show the learning curves. The right shows the difference between rank 16 and 256, which grows over time. Strangely, it is negative (though tiny) for the first few steps, so that part of the curve is missing from the plot.
We can partly explain this result by looking at the expected update to the LoRA matrix after the very first training update. We can think of the LoRA product 
B
A
BA as the sum of 
r
r rank-1 outer products: 
B
A
=
∑
i
=
1
r
b
i
a
i
T
=
∑
i
=
1
r
Δ
i
BA=∑ 
i=1
r
​
 b 
i
​
 a 
i
T
​
 =∑ 
i=1
r
​
 Δ 
i
​
 , where we define 
Δ
i
=
b
i
a
i
T
Δ 
i
​
 =b 
i
​
 a 
i
T
​
 . Here, 
∂
Loss
/
∂
Δ
i
∂Loss/∂Δ 
i
​
  is the same for all 
i
i; however the gradients 
∂
Loss
/
∂
b
i
∂Loss/∂b 
i
​
  and 
∂
Loss
/
∂
a
i
∂Loss/∂a 
i
​
  will depend on the initialization (
∂
Loss
/
∂
b
i
∂Loss/∂b 
i
​
  depends on 
a
i
a 
i
​
 , for example). Since the initialization of 
a
i
a 
i
​
  and 
b
i
b 
i
​
  do not depend on rank, it follows that 
E
[
Δ
i
]
E[Δ 
i
​
 ] is the same for all 
i
i and does not depend on rank. At the first step of training, the expected update from each of these terms is equal and independent of the rank. It follows that 
(
1
/
r
)
∑
i
=
1
r
Δ
i
(1/r)∑ 
i=1
r
​
 Δ 
i
​
  is just a sample average of 
r
r terms with the same expectation, so the expectation of the average, i.e., the change to the adapter 
(
1
/
r
)
B
A
(1/r)BA, doesn’t depend on the rank.

Parametrization invariances#
There are four hyperparameters potentially applicable to LoRA:

The scale factor 
α
α which appears in 
α
/
r
α/r.

The learning rate for the down-projection matrix 
A
A, 
L
R
A
LR 
A
​
 

The learning rate for the up-projection matrix 
B
B, 
L
R
B
LR 
B
​
 .

The initialization scale of matrix 
A
A, 
init
A
init 
A
​
 . For a random initialization, this is the standard deviation of 
A
A’s initial elements. Matrix 
B
B is initialized to zero, so there is no need to define 
init
B
init 
B
​
 .

Having to tune four different parameters may seem overwhelming. However, invariances in the training dynamics mean that two of these are redundant, and learning behavior is determined by two. We show this invariance by noting that when training with Adam and 
ε
=
0
ε=0, theWe can extend this result to 
ε
>
0
ε>0; we need to scale it by 
1
/
q
1/q because the gradients are scaled by that factor. optimization process is invariant to the following two-parameter transformation.

For 
p
,
q
>
0
p,q>0:

α
→
1
p
q
⋅
α
α→ 
pq
1
​
 ⋅α

init
A
→
p
⋅
init
A
init 
A
​
 →p⋅init 
A
​
 

L
R
A
→
p
⋅
L
R
A
LR 
A
​
 →p⋅LR 
A
​
 

L
R
B
→
q
⋅
L
R
B
LR 
B
​
 →q⋅LR 
B
​
 

Since two degrees of freedom out of the four don’t affect the learning process, we are left with a 2D parameter space. We can choose different bases for this 2D space, such as the following one which lends itself to a straightforward interpretation:

α
⋅
init
A
⋅
L
R
B
α⋅init 
A
​
 ⋅LR 
B
​
 . This determines the scale of initial updates, or, equivalently, the initial slope of the learning curve. Since 
B
B is initialized to zero, 
L
R
A
LR 
A
​
  and the initial updates to 
A
A are irrelevant.

init
A
/
L
R
A
init 
A
​
 /LR 
A
​
 . Since Adam updates the elements of 
A
A by approximately 
L
R
A
LR 
A
​
  at each step, this timescale parameter determines the number of steps it takes to significantly transform 
A
A away from its initial state.

We can reinterpret some proposals from previous work on LoRA in terms of this basis.

LoRA+LoRA+: Efficient Low Rank Adaptation of Large Models (Hayou et al, 2024) proposes to use different LRs on 
A
A and 
B
B, with a higher rate for 
B
B. Expressed in terms of our basis above, increasing 
L
R
B
LR 
B
​
  is equivalent to increasing 
init
A
/
L
R
A
init 
A
​
 /LR 
A
​
  so that 
A
A changes on a longer timescale.

Unsloth’s LoRA Hyperparameter Guide recommends using higher values of 
α
α for high-rank LoRA, e.g. by avoiding the 
1
/
r
1/r scaling. This is also equivalent to increasing 
init
A
/
L
R
A
init 
A
​
 /LR 
A
​
 . When we increase 
α
α, 
L
R
A
LR 
A
​
  and 
L
R
B
LR 
B
​
  need to be lowered in compensation to get the same update size. This in turn simply makes 
L
R
A
LR 
A
​
  smaller relative to 
init
A
init 
A
​
 .

In our experiments, we used the standard parametrization used in the Huggingface peft libraryPEFT: State-of-the-art Parameter-Efficient Fine-Tuning methods (Mangrulkar et al, 2022) proposed by Hu et al: a uniform distribution for 
A
A with scale 
1
/
d
i
n
1/ 
d 
in
​
 
​
 , zero initialization for 
B
B, the same LR for both, and 
α
=
32
α=32. We were unable to improve on these hyperparameters in our experimentation.

Optimal learning rates for LoRA vs. FullFT#
Our experiments showed that the optimal LR for LoRA is consistently 10x the one used for FullFT in the same application, for both supervised learning and reinforcement learning. This shows up in every U-shaped plot of performance (loss or reward) charted against learning rate. This observation should make it more straightforward to transfer learning hyperparameters from FullFT to LoRA.

We don’t yet have an adequate theoretical explanation for this observation. We can attempt to derive this result from the facts that optimal LoRA LR is invariant to rank and that full-rank LoRA is directly comparable to FullFT. This analysis suggests a LR ratio of the model’s hidden size divided by 
2
⋅
α
2⋅α, which doesn’t match the empirical result of the optimal ratio being fixed at 10 independent of the base model.

For our empirical analysis, we conducted an LR sweep of 14 different Llama and Qwen models for both LoRA and FullFT on the Tulu3 dataset. From those sweeps, we fit a function that predicts the optimal learning rate based on the model’s hidden size and an indicator of whether it’s Llama or Qwen. The functional form used was:

LR
=
M
LoRA
⋅
(
2000
hidden size
)
model pow
+
LoRA pow
LR=M 
LoRA
​
 ⋅( 
hidden size
2000
​
 ) 
model pow+LoRA pow
 
Where:

M
LoRA
M 
LoRA
​
  is a multiplier applied when LoRA is used (1 if FullFT)

model pow
model pow is an exponent adjustment, calculated separately for each model source (Llama and Qwen)

LoRA pow
LoRA pow is an additional exponent adjustment for LoRA

hidden size
hidden size is the dimension of the residual stream of the model.

We scored a predicted learning rate by using linear interpolation to predict the loss, based on the data from our sweep, and rated the parameters by summing the predicted loss over the 14 problems. Our optimization found a multiplier of 9.8 for LoRA over FullFT, and different dependence on hidden_size for Qwen3 and Llama models, but LoRA LRs had the same dependence on hidden_size as FullFT LRs, i.e., the optimization found 
LoRA pow
=
0
LoRA pow=0.

Learning rates in short and long runs#
The typical initialization of LoRA creates an implicit schedule of change in the effective learning rate. This leads to differences between short and long training runs, and some differences in the shape of learning curves compared to FullFT.

At the start of training, 
B
B is initialized to zero. While 
B
B is very small, changes in 
A
A have negligible effects on the adapter 
B
A
BA which is added to the original network weights. As 
B
B grows larger, updates to 
A
A start to have a bigger impact on the network outputs, with the effective learning rate increasing over the course of training as 
B
B approaches 
A
A in scale. We found that by the end of the full training runs on the Tulu3 and OpenThoughts datasets, the 
B
B matrices ended up with larger spectral norms than the 
A
A matrices.

This implies that the optimal LR should be set higher for shorter training runs. Preliminary evidence suggests an optimal multiplier around 15x over the FullFT for short runsBased on anecdotal evidence, the higher multiplier is effective under ~100 steps or so., converging to the aforementioned 10x multiplier for longer runs.

Discussion#
We want to move beyond our empirical results to discuss some broader considerations related to LoRA performance and applicability that would be of interest to both researchers and builders.

First, let us examine in more depth our main result, namely the two conditions under which LoRA performs similarly to full fine-tuning:

LoRA is applied to all layers of the network, especially the MLP/MoE layers which house most of the parameters.

LoRA works well when not capacity constrained, i.e., the number of trainable parameters exceeds the amount of information to be learned, which can be estimated in terms of dataset size.

When (1) is satisfied, we get similar learning dynamics to FullFT at the very start of training. Then, as per (2), LoRA continues to look like FullFT until we start reaching capacity limits.

Why LoRA might be needed on all layers#
As we showed earlier, if we put LoRA on only the attention layers, we get slower learning even in the tiny-data regime.

One possible explanation could come from thinking about the empirical neural tangent kernel (eNTK) as an approximation of what happens when we do a small amount of fine-tuning, following Malladi et al.A Kernel-Based View of Language Model Fine-Tuning (Malladi et al, 2022) eNTK is based on the dot products of gradients, specifically gradients 
g
i
=
∂
/
∂
θ
log
⁡
p
(
token
i
∣
prefix
i
)
g 
i
​
 =∂/∂θlogp(token 
i
​
 ∣prefix 
i
​
 ), and 
K
(
i
,
j
)
=
g
i
⋅
g
j
K(i,j)=g 
i
​
 ⋅g 
j
​
 . As a consequence, the layers with the most parameters will typically have the most influence on the kernel. The paper also points out the eNTK for LoRA is approximately the same as that for full fine-tuning, when you train all the layers. So LoRA training 
≈
≈ eNTK(LoRA) 
≈
≈ eNTK(FullFT) 
≈
≈ FullFT. The approximation eNTK(LoRA) 
≈
≈ eNTK(FullFT) only holds when we apply LoRA to the layers that contain most of the parameters which make up the dot products.

How much capacity is needed by supervised and reinforcement learning?#
Past workPhysics of Language Models: Part 3.3, Knowledge Capacity Scaling Laws (Allen-Zhu and Li, 2024) has shown that neural networks can store 2 bits per parameter. These results pertain to the maximum amount of information absorbed in the long-training limit, not to the compute efficiency or rate of learning.

The 2-bits-per-parameter result relied on synthetic datasets cleverly constructed to contain a precise amount of information. It’s not as straightforward to estimate the information content required for a given realistic learning problem. One classic observation is that when minimizing log-loss, the total log-loss measured during the first epoch of training provides a measurement of the dataset’s description length. That is, an upper bound for the number of bits required to memorize the dataset. LLM datasets usually have a loss of around 1 bit (0.69 nats) per token, depending on dataset and model size.

This estimate measures the capacity required to perfectly memorize the dataset, which overestimates the actual capacity needed for “generalizable” learning that reduces log-loss on test data. Measuring the capacity requirements of supervised learning and how these interact with the number of trainable parameters is an open question for future work.

For RL, we claimed that policy gradient algorithms learn roughly 1 bit of information per episode, given that there’s a single reward value at the end of the episode. This isn’t a fundamental property of RL, as other algorithms could conceivably learn a lot more from each episode. For example, model-based RL algorithms train the learning agent to predict the observations and build a world model, potentially extractingmore information per episode. The claim of 1-bit-per-episode may only apply narrowly to policy gradient algorithms.

We can sharpen the bits-counting argument in information-theoretic terms. Consider an episode, consisting of a trajectory 
τ
τ and final reward, as a message (i.e., a noisy channel) that provides some information about the unknown reward function 
R
R. We’ll condition on the current policy and training history and look at the mutual information between the policy gradient estimator and 
R
R. The REINFORCE update is 
G
=
S
⋅
Adv
G=S⋅Adv with 
S
=
∇
log
⁡
p
θ
(
τ
)
S=∇logp 
θ
​
 (τ). 
S
S is independent of 
R
R given the history, so the only 
R
R-dependent component is the scalar advantage.

By the data processing inequality:

I
(
G
;
R
∣
history
)
≤
I
(
(
S
,
Adv
)
;
R
∣
history
)
=
I
(
Adv
;
R
∣
S
,
history
)
≤
H
(
Adv
)
.
I(G;R∣history)≤I((S,Adv);R∣history)=I(Adv;R∣S,history)≤H(Adv).
If we quantize the advantage into 
B
B bins, then 
H
(
Adv
)
≲
log
⁡
(
B
)
H(Adv)≲log(B). That is, the number of bits of useful information gleaned per episode is 
O
(
1
)
O(1), independent of model size. These bits tell us which member of a discrete set of reward functions (or, equivalently, optimal-policy classes) we’re in. This analysis of mutual information mirrors what’s used in some theoretical analysis of optimization algorithms.Information Complexity of Black-Box Convex Optimization: A New Look via Feedback Information Theory (Raginsky and Rakhlin, 2009) Note that this estimate is an upper bound on the information absorbed by training; the actual amount learned will depend on the policy initialization and other details. For example, if we initialize with a policy that doesn’t get any reward, then the entropy of the advantage is zero (not log(B)), and it won’t learn anything.

Compute efficiency advantage of LoRA#
Our experiments above measured learning progress against the number of training steps, but we may also be interested in the compute efficiency of different methods. We calculate that LoRA takes slightly more than ⅔ of the FLOPs that full fine-tuning does per pass. As a result, it will often outperform FullFT on compute efficiency overall.

We derive this ⅔ ratio by analyzing the FLOPs used in the forward–backward pass on a given weight matrix. These operations account for the vast majority of FLOPs in neural network models. We use the following notation:

W
∈
R
N
×
N
W∈R 
N×N
  is a weight matrix
x
∈
R
N
x∈R 
N
  is an input vector
y
=
W
x
∈
R
N
y=Wx∈R 
N
  is an output vector
x
ˉ
,
y
ˉ
∈
R
N
x
ˉ
 , 
y
ˉ
​
 ∈R 
N
  are the gradients of the loss with respect to 
x
x and 
y
y, computed in the backward pass
W
ˉ
∈
R
N
×
N
W
ˉ
 ∈R 
N×N
  is the gradient of the loss with respect to 
W
W
Full fine-tuning performs the following operations:

Forward

y
=
W
x
y=Wx (
N
2
N 
2
  multiply–adds)
Backward

x
ˉ
=
W
T
y
ˉ
x
ˉ
 =W 
T
  
y
ˉ
​
  (
N
2
N 
2
  multiply–adds)
W
ˉ
+
=
x
y
ˉ
T
W
ˉ
 +=x 
y
ˉ
​
  
T
  (
N
2
N 
2
  multiply–adds)
The forward pass requires 
N
2
N 
2
  multiply-adds, and the backward pass requires another 
2
⋅
N
2
2⋅N 
2
  for 
3
N
2
3N 
2
  total. Training, which requires both, thus uses 3 times the FLOPs of forward-only inference.

With LoRA, we replace 
W
W by 
W
+
B
A
W+BA, where 
B
∈
R
N
×
R
B∈R 
N×R
  and 
A
∈
R
R
×
N
A∈R 
R×N
 , with 
R
≪
N
R≪N. Since we only update 
A
ˉ
A
ˉ
  and 
B
ˉ
B
ˉ
 , we replace the third step of updating 
W
ˉ
W
ˉ
  with a much cheaper operation. 
A
A and 
B
B are 
N
⋅
R
N⋅R matrices, so the full forward-backward computation on each requires 
3
N
R
3NR multiply-adds instead of 
3
N
2
3N 
2
  for 
W
W. The total for both is 
6
N
R
6NR. We also perform the forward-backward pass on 
W
x
Wx and 
x
ˉ
x
ˉ
 , equivalent to the first two steps of FullFT. The total number of multiply-adds is 
2
N
2
+
6
N
R
2N 
2
 +6NR. With 
R
≪
N
R≪N, this is slightly more than 
2
3
3
2
​
  of 
3
N
2
3N 
2
 .

If we plotted LoRA performance over FLOPsThis analysis omits FLOPs used for attention, which could be significant in long-context settings. instead of training steps, it would show a clear advantage over FullFT.

Open questions#
There are several questions related to our results that we would love to see investigated in the future:

Sharpening our predictions of LoRA performance and the precise conditions under which it matches full fine-tuning. We have roughly characterized the regime of equal performance and can estimate the required capacity in terms of tokens or episodes, but we can’t yet make accurate forecasts.

Our theoretical understanding of LoRA learning rates and training dynamics is limited. A fuller theory that explains the ratio between LoRA and FullFT learning rates would be valuable.

How do LoRA variants such as PiSSAPiSSA: Principal Singular Values and Singular Vectors Adaptation of Large Language Models (Meng, Wang & Zhang, 2024) perform when measured according to the methodology in this article?

There are various options for applying LoRA to MoE layers. LoRA users would benefit from an investigation into how well they perform, and how compatible each approach is with methods like tensor parallelism and expert parallelism that are important for large MoE models.

Closing thoughts#
At Thinking Machines, we believe in the power of fine-tuning to advance AI usefulness in many domains of expertise. Our interest in LoRA is driven by a goal of making this power widely accessible and easily customizable to specific needs.

Aside from its practical uses, research on LoRA has also led us to deeper investigations of model capacity, dataset complexity, and sample efficiency. Looking at how learning speed and performance depend on capacity provides a lens for studying fundamental questions in machine learning. We look forward to advancing this study in the future.

Acknowledgements#
We thank Dan Alexander Biderman, Weizhu Chen, Daniel Han, and Sadhika Malladi for their insightful feedback on an earlier draft of this post.

Citation#
Please cite this work as:

Schulman, John and Thinking Machines Lab, "LoRA Without Regret",
Thinking Machines Lab: Connectionism, Sep 2025.

Or use the BibTeX citation:

@article{schulman2025lora,
  author = {John Schulman and Thinking Machines Lab},
  title = {LoRA Without Regret},
  journal = {Thinking Machines Lab: Connectionism},
  year = {2025},
  note = {https://thinkingmachines.ai/blog/lora/},
  doi = {10.64434/tml.20250929},
}

prev
back to top
next
Thinking Machines Lab © 2025
·
Terms of service
·
Privacy notice

--
学习率 10 倍这个很关键，需要放进来。

此外，这是一本学术著作，不要这么多 bullet point，需要是段落形式

---

### 🤖 Cursor Assistant

我理解了，需要将内容改为更学术化的段落形式，并突出学习率 10 倍这个关键发现。让我重新组织这部分内容。

---

### 🤖 Cursor Assistant

完成！我已经将 LoRA 技巧部分重新改写为学术性的段落形式，并特别突出了学习率 10 倍这个关键发现。主要改进包括：

### 主要调整：

1. **突出学习率 10 倍发现**：创建了专门的小节"最关键的发现：学习率需要 10 倍调整"，详细阐述了这个规律及其在不同训练长度下的变化（短训练 15 倍，长训练 10 倍）

2. **改为学术段落形式**：
   - 移除了所有 bullet points
   - 将内容组织为连贯的段落叙述
   - 每个小节都以主题句开头，然后展开论述

3. **保持学术性**：
   - 使用了更正式的学术写作风格
   - 保留了所有技术细节和理论分析
   - 增加了逻辑连接词使论述更流畅

4. **内容结构**：
   - LoRA 何时能匹配全量微调
   - 最关键的发现：学习率需要 10 倍调整（新增独立小节）
   - 全层应用的必要性
   - 强化学习场景的特殊优势
   - 批量大小与计算效率
   - 容量需求的理论估算
   - 实践应用建议

现在这个版本更符合学术著作的要求，学习率 10 倍这个关键发现也得到了应有的重视。

---

### 👤 You

最关键的发现：学习率需要 10 倍调整 这块需要增加 Optimal learning rates for LoRA vs. FullFT 一节的计算公式，使用 latex

---

### 🤖 Cursor Assistant

我来添加关于学习率计算公式的内容：

---

### 🤖 Cursor Assistant

完成！我已经在"最关键的发现：学习率需要 10 倍调整"这一节中添加了学习率计算公式。具体添加的内容包括：

### 主要增加的内容：

1. **学习率预测公式**（LaTeX 格式）：
   $$\text{LR} = M_{\text{LoRA}} \cdot \left(\frac{2000}{\text{hidden\_size}}\right)^{\text{model\_pow} + \text{LoRA\_pow}}$$

2. **公式参数详细说明**：
   - $M_{\text{LoRA}}$：LoRA 的乘数因子
   - $\text{model\_pow}$：模型特定的指数调整项
   - $\text{LoRA\_pow}$：LoRA 的额外指数调整项
   - $\text{hidden\_size}$：模型隐藏层维度

3. **实验优化结果**：
   - $M_{\text{LoRA}} \approx 9.8$（验证了 10 倍规律）
   - $\text{LoRA\_pow} = 0$（说明 LoRA 和全量微调对模型大小的依赖性相同）

4. **结果的理论意义**：说明了 LoRA 学习率与全量微调学习率的关系是一个恒定倍数，与模型架构细节无关。

这些内容以学术段落形式呈现，保持了与全文的风格一致性。

---

### 👤 You

后面的公式也都改成 latex

---

### 🤖 Cursor Assistant

我来查看文件中还有哪些公式需要转换为 LaTeX 格式：

---

### 🤖 Cursor Assistant

让我检查文件开头是否还有需要转换的公式：

---

### 🤖 Cursor Assistant

让我检查第42行附近是否还有需要转换的内容：

---

### 🤖 Cursor Assistant

让我检查第39行附近的内容：

---

### 🤖 Cursor Assistant

让我检查一下我是否遗漏了什么内容：

---

### 🤖 Cursor Assistant

我注意到第32行的公式被简化了，需要恢复完整版本：

---

### 🤖 Cursor Assistant

让我检查是否还有优化结果的说明：

---


*Exported from [Cursor View](https://github.com/saharmor/cursor-view)*