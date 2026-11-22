# 实验 8-16：结果做对了，该怎样给出过程反馈？

假设 Agent 要改一项配置。它直接覆盖了文件，碰巧写出了正确结果。只按最终状态给分，这条轨迹和“先读原配置，再改指定项”会得到相同奖励。作者团队提出的 RLVP 给训练增加了一条信号：先检查哪一步违反了可验证的规则，再决定哪些动作应承担这次扣分。[第八章正文](../../book/chapter8.md) · [English](#english)

## 先确定哪一步违规

看上游的[文件操作测试](https://github.com/19PINE-AI/rlvp/blob/1ad30bc7e338911fb733739393d92c420f4d8bee/tests/test_rules.py)。同样调用 `write_file`，直接写已有配置文件会触发 `blind_write`；先读同一文件再写，检查通过。创建一个新文件也通过，因为这时没有旧内容可读。这三个例子划出了规则的适用范围。

## 再算这一步该扣多少分

[奖励分配测试](https://github.com/19PINE-AI/rlvp/blob/1ad30bc7e338911fb733739393d92c420f4d8bee/tests/test_credit.py)构造了两条轨迹。第一条完成任务，但第二轮动作违规；另一条任务失败，全程合规。两条的结果奖励分别为 1 和 0，减去组均值 0.5，得到 +0.5 和 −0.5。

如果把所有违规扣分并入最终奖励，再减组均值（代码中的 `c1`），第一条轨迹的每轮动作都会受到这次违规的影响。换成 `c2`，两条轨迹仍保留各自的结果信号；在这个算例中，另外的 −0.3 只加在第一条轨迹的第二轮动作上。两项信号怎样共同影响参数更新，还要看它们各自分摊到多少个 token 上。

沿这个测试读[参数更新函数](https://github.com/19PINE-AI/rlvp/blob/1ad30bc7e338911fb733739393d92c420f4d8bee/rlvp/grpo.py)。两条轨迹各有两轮动作，每轮 10 个动作 token。结果信号按全部 40 个动作 token 归一化，违规信号按收到扣分的 10 个 token 归一化。成功轨迹的第一轮没有违规，每个动作 token 的权重是 0.5 ÷ 40 = 0.0125。第二轮既完成了这条成功轨迹中的动作，又触发了违规，因此权重是 0.5 ÷ 40 − 0.3 ÷ 10 = −0.0175。在这批样本里，完成任务可以得到奖励，导致违规的那一步仍会受到抑制。

如果两条轨迹都失败，结果奖励都为零，减去组均值后这一项也为零。只要规则还能定位到违规动作，那一轮仍有路径信号；若两条轨迹都合规，单靠这条规则也分不出谁更接近成功。

## 在本地核对规则和分数

从本书仓库根目录取得论文仓库的固定版本：

```bash
git clone https://github.com/19PINE-AI/rlvp.git chapter8/RLVP/rlvp
git -C chapter8/RLVP/rlvp fetch origin 1ad30bc7e338911fb733739393d92c420f4d8bee
git -C chapter8/RLVP/rlvp checkout --detach 1ad30bc7e338911fb733739393d92c420f4d8bee
git -C chapter8/RLVP/rlvp rev-parse HEAD
test "$(git -C chapter8/RLVP/rlvp rev-parse HEAD)" = "1ad30bc7e338911fb733739393d92c420f4d8bee"
```

进入上游目录后，先运行这两组测试。第一组使用 Python 标准库；第二组需要 PyTorch，可以在 CPU 上运行。

```bash
cd chapter8/RLVP/rlvp
python3 tests/test_rules.py
python3 tests/test_credit.py
```

两组测试分别检查规则触发和奖励分配。要判断训练后违规是否减少、任务成功率是否保持，还需要实际更新策略并在留出的任务上评估。上游训练流程从 `python3 scripts/phase0_baseline.py` 建立基线，经 `bash scripts/run_all.sh` 运行训练，再用 `python3 scripts/eval_checkpoint.py results/run_c3/final c3_norules` 评估检查点。完整训练需要 CUDA；正文中的违规率、miniF2F 和全败组统计来自作者团队的研究。与 AdaptThink、ReTool 和 AWorld 一样，本目录给出外部实现的复现入口。[实验记录](../EXPERIMENT_LEDGER.md)

## English

# Experiment 8-16: RLVP —— Reward the Outcome, Penalize the Path

> 📖 **The complete training/evaluation code corresponding to this experiment is in the standalone paper repository: [`github.com/19PINE-AI/rlvp`](https://github.com/19PINE-AI/rlvp)**
>
> RLVP (Reward the Outcome, Penalize the Path) is a post-training study by the author team. All results reported in Chapter 8, Experiment 8-16 of the book (violation rate, miniF2F, full-loss group proportion, etc.) come from experiments in that repository. Since training depends on GPU clusters and the code is continuously updated alongside the paper, the main book repository no longer duplicates it. Please go directly to the upstream repository for the latest code, configuration, and reproduction instructions:

```bash
# Use the pinned clone/fetch/detached-checkout/SHA-verification block above.
```

## Relationship with Other Training Experiments in This Chapter

This directory, like `chapter8/AdaptThink`, `chapter8/retool`, and `chapter8/AWorld-train`, belongs to the **reproduction guide (KEEP-EXT)**: the core training code resides in an external repository; simply follow its README to reproduce. For an explanation of the method and conclusions, see the corresponding section on "Model Post-Training" in Chapter 8 of the book.

---
