# Cursor Chat: ai-agent-book

## Metadata
- **Project**: ai-agent-book
- **Path**: `/Users/boj`
- **Date**: 2025-10-05 19:11:24
- **Session ID**: `f4b19584-855a-4b03-88ce-842901ee6cc3`

## Conversation

### 👤 You

需要补充完整的 setup 过程，以及项目链接 @https://github.com/PRIME-RL/SimpleVLA-RL/ 

在如下内容基础上做修改：
@@ -27,7 +27,20 @@ pip3 install -e .
 cd ..
 ```

-#### Step 2: Install LIBERO and OpenVLA-OFT
+#### Step 2: Install EGL Libraries for Headless Rendering
+
+**Required for both LIBERO and RoboTwin 2.0 benchmarks.**
+
+Install EGL libraries to enable headless rendering in Docker containers or remote servers without displays:
+
+```bash
+sudo apt-get update
+sudo apt-get install -y libegl1 libegl-dev libegl-mesa0 libegl1-mesa-dev libgles2-mesa-dev
+```
+
+> **Note:** Without these libraries, you may encounter `AttributeError: 'NoneType' object has no attribute 'eglQueryString'` when initializing SAPIEN/robotics environments.
+
+#### Step 3: Install LIBERO and OpenVLA-OFT

 Follow the official [OpenVLA-OFT installation guide](https://github.com/moojink/openvla-oft):

@@ -61,7 +74,11 @@ pip install -r experiments/robot/libero/libero_requirements.txt

 Same as Option 1, Step 1.

-#### Step 2: Install RoboTwin 2.0
+#### Step 2: Install EGL Libraries for Headless Rendering
+
+Same as Option 1, Step 2.
+
+#### Step 3: Install RoboTwin 2.0


# SimpleVLA-RL Installation Guide

This guide provides step-by-step instructions for setting up the SimpleVLA-RL environment. Our project builds upon [veRL](https://github.com/volcengine/verl), and the installation process involves three main components: veRL, simulation benchmarks, and the VLA model (OpenVLA-OFT).

## Installation Options

### Option 1: Running RL on LIBERO Benchmark

#### Step 1: Install veRL

> **Note:** We recommend veRL version 0.2 or 0.3. Latest versions may have library conflicts.

Follow the official [veRL installation guide](https://verl.readthedocs.io/en/v0.3.x/start/install.html):

```bash
# Create and activate conda environment
conda create -n simplevla python==3.10
conda activate simplevla

# Install PyTorch
pip3 install torch==2.4.0 --index-url https://download.pytorch.org/whl/cu124

# Clone veRL (recommended to place at the same level as simplevla-rl, not inside the simplevla-rl folder)
git clone -b v0.2.x https://github.com/volcengine/verl.git
cd verl
pip3 install -e .
cd ..
```

#### Step 2: Install LIBERO and OpenVLA-OFT

Follow the official [OpenVLA-OFT installation guide](https://github.com/moojink/openvla-oft):

```bash
conda activate simplevla
pip3 install torch torchvision

# Clone OpenVLA-OFT (place at the same level as simplevla-rl, not inside the simplevla-rl folder)
git clone https://github.com/moojink/openvla-oft.git
cd openvla-oft
pip install -e .

# Install Flash Attention 2 for training
# If you encounter issues, try `pip cache remove flash_attn` first
pip install packaging ninja
ninja --version; echo $?  # Should return exit code "0"
pip3 install flash-attn --no-build-isolation

cd ..

# Install LIBERO
git clone https://github.com/Lifelong-Robot-Learning/LIBERO.git
pip install -e LIBERO
cd openvla-oft
pip install -r experiments/robot/libero/libero_requirements.txt
```

### Option 2: Running RL on RoboTwin 2.0 Benchmark

#### Step 1: Install veRL

Same as Option 1, Step 1.

#### Step 2: Install RoboTwin 2.0

Follow the official [RoboTwin 2.0 Installation Guide](https://robotwin-platform.github.io/doc/usage/robotwin-install.html#1-dependencies):

```bash
# Install system dependencies
sudo apt install libvulkan1 mesa-vulkan-drivers vulkan-tools

conda activate simplevla

# Clone and install RoboTwin
git clone https://github.com/RoboTwin-Platform/RoboTwin.git
cd RoboTwin
bash script/_install.sh

# Download RoboTwin assets
bash script/_download_assets.sh
cd ..
```

#### Step 3: Install OpenVLA-OFT

```bash
conda activate simplevla
pip3 install torch torchvision

# Clone OpenVLA-OFT (place at the same level as simplevla-rl, not inside the simplevla-rl folder)
git clone https://github.com/moojink/openvla-oft.git
cd openvla-oft
pip install -e .

# Install Flash Attention 2
pip install packaging ninja
ninja --version; echo $?  # Should return exit code "0"
pip3 install flash-attn --no-build-isolation
cd ..
```

#### Step 4: Configure RoboTwin for SimpleVLA-RL

Apply necessary modifications to RoboTwin:

```bash
git clone https://github.com/PRIME-RL/SimpleVLA-RL.git
cd SimpleVLA-RL

# Apply RoboTwin modifications
bash copy_overwrite_robotwin2.sh <your_robotwin_path> <your_simplevlarl_path>
# Example: bash copy_overwrite_robotwin2.sh /mnt/petrelfs/SimpleVLA-RL /mnt/petrelfs/RoboTwin
```

## Troubleshooting

- If you encounter issues with RoboTwin 2.0 installation, refer to the [RoboTwin documentation](https://robotwin-platform.github.io/doc/) or check their GitHub issues
- All repositories (veRL, OpenVLA-OFT, RoboTwin) are recommended to clone at the same directory level as SimpleVLA-RL

## Directory Structure

After installation, your directory structure should look like:
```
your_workspace/
├── SimpleVLA-RL/
├── verl/
├── openvla-oft/
├── LIBERO/          (for Option 1)
└── RoboTwin/        (for Option 2)
```


## Supporting Additional Tasks in RoboTwin 2.0 (Optional) 

### Step 1: Collect Feasible Seeds

RoboTwin 2.0 tasks may have infeasible seeds (e.g., objects beyond arm reach). To optimize RL training, we pre-collect feasible seeds to avoid repeated validation during training epochs.

**Collection Process:**

1. Update `DATASET_NAME` in `pre_collect_robotwin2_seed.sh` with your target task name
2. Run the collection script:
   ```bash
   sh pre_collect_robotwin2_seed.sh
   ```
3. This generates `robotwin2_train_seeds.json` in the SimpleVLA-RL directory
4. Add the JSON content to:
   ```
   SimpleVLA-RL/verl/utils/envs/robotwin2/seeds/robotwin2_train_seeds.json
   ```

### Step 2: Register New Tasks

1. Add task name in `SimpleVLA-RL/verl/utils/dataset/rob_dataset.py`
2. Add task name and corresponding max steps in `SimpleVLA-RL/verl/workers/rollout/rob_rollout.py`

### Step 3: Implement Task-Specific Functions

Add a `get_info()` function in the corresponding task file under `SimpleVLA-RL/verl/utils/envs/robotwin2/envs/task_name.py`. 

For implementation reference, see:
```
SimpleVLA-RL/modified_codes/robotwin2/envs/handover_block.py
```

---

### 🤖 Cursor Assistant

我来帮你补充完整 SimpleVLA-RL 项目的 SETUP.md 文件，添加 EGL Libraries 安装步骤和项目链接。

---

### 🤖 Cursor Assistant

我发现 SETUP.md 文件不存在，我将根据你提供的内容创建一个完整的 SETUP.md 文件，其中已经包含了 EGL Libraries 安装步骤。

---

### 🤖 Cursor Assistant

已完成！我创建了完整的 `SETUP.md` 文件，包含以下改进：

## 主要更新内容：

### ✅ 添加的内容：
1. **项目链接** - 在文件顶部添加了 GitHub 仓库链接
2. **EGL Libraries 安装步骤** - 在两个安装选项中都添加为 Step 2：
   - 用于无头渲染（headless rendering）
   - 解决 SAPIEN/机器人环境初始化时的 `eglQueryString` 错误
3. **增强的故障排除部分** - 添加了 EGL 相关错误的说明
4. **验证步骤** - 添加了安装完成后的验证命令
5. **更清晰的结构** - 重新编号了步骤以适应新的 EGL 安装步骤

## 文件结构：

```
SimpleVLA-RL Installation Guide
├── Option 1: LIBERO Benchmark
│   ├── Step 1: Install veRL
│   ├── Step 2: Install EGL Libraries ⭐ (新增)
│   └── Step 3: Install LIBERO and OpenVLA-OFT
└── Option 2: RoboTwin 2.0 Benchmark
    ├── Step 1: Install veRL
    ├── Step 2: Install EGL Libraries ⭐ (新增)
    ├── Step 3: Install RoboTwin 2.0
    ├── Step 4: Install OpenVLA-OFT
    └── Step 5: Configure RoboTwin for SimpleVLA-RL
```

文件已保存至：`/Users/boj/ai-agent-book/projects/week7/SimpleVLA-RL/SETUP.md`

这个安装指南现在提供了完整的、可操作的设置流程，特别强调了 EGL 库对于无头服务器环境的重要性。

---

### 👤 You

不是，是要把完整的 setup 过程用中文，补充到 README 里面

---

### 🤖 Cursor Assistant

明白了！你是要把完整的 setup 过程用中文补充到 README.md 里面。让我先查看现有的 README.md 内容。

---

### 🤖 Cursor Assistant

明白了！我需要把完整的 setup 过程用中文补充到 README.md 的"快速开始"部分。让我修改 README.md 中的环境配置部分。

---

### 🤖 Cursor Assistant

现在让我删除之前创建的单独的 SETUP.md 文件，因为完整的 setup 过程已经用中文集成到 README.md 中了：

---

### 🤖 Cursor Assistant

完成！我已经成功完成以下更新：

## ✅ 已完成的修改

### 1. **添加项目链接**
在 README.md 顶部添加了 GitHub 仓库链接：
```markdown
**项目地址**: [https://github.com/PRIME-RL/SimpleVLA-RL/](https://github.com/PRIME-RL/SimpleVLA-RL/)
```

### 2. **用完整的中文 Setup 过程替换了简短说明**
将"第一步:环境配置"部分从简短的依赖列表扩展为完整的安装指南，包括：

#### 选项 1: LIBERO 基准测试
- **步骤 1.1**: 安装 veRL
- **步骤 1.2**: 安装 EGL 库以支持无头渲染 ⭐ (新增)
- **步骤 1.3**: 安装 LIBERO 和 OpenVLA-OFT

#### 选项 2: RoboTwin 2.0 基准测试
- **步骤 2.1**: 安装 veRL
- **步骤 2.2**: 安装 EGL 库以支持无头渲染 ⭐ (新增)
- **步骤 2.3**: 安装 RoboTwin 2.0
- **步骤 2.4**: 安装 OpenVLA-OFT
- **步骤 2.5**: 为 SimpleVLA-RL 配置 RoboTwin

### 3. **添加的重要部分**
- ✅ 故障排除指南
- ✅ 目录结构说明
- ✅ 验证安装命令
- ✅ RoboTwin 2.0 额外任务配置（可选）
  - 收集可行的种子
  - 注册新任务
  - 实现任务特定函数

### 4. **清理**
删除了之前误创建的单独 SETUP.md 文件，所有内容现在都在 README.md 中。

现在 README.md 包含了完整的、可操作的中文 setup 指南，特别强调了 EGL 库对于无头服务器环境的重要性，用户可以直接按照步骤进行安装配置！

---


*Exported from [Cursor View](https://github.com/saharmor/cursor-view)*