这是一个为你精心编写的 **GitHub README.md** 项目介绍。它采用了中英双语对照格式，涵盖了从“全龄启迪”的设计理念到“Python 3.14 内存防御”的硬核技术实现。

---

# AI Prompt Matrix Engine | AI 绘画提示词矩阵生成器

[English] | [中文]

An industrial-grade, fully offline AI art prompt generator and "imagination enlightenment" tool. Designed to empower creators of all ages—from children to the elderly—by bridging the gap between imagination and professional AI art syntax.

一款工业级、全离线运行的 AI 绘画提示词生成器与“想象力启迪”工具。旨在打破技术门槛，通过“积木式”点击，帮助从儿童到老人的全年龄段用户将脑海中的画面转化为专业的 AI 绘画指令。

---

## ✨ Highlights | 核心亮点

### 1. **Formulaic Prompt Construction | 公式化主体构建**
*   **Logical Matrix**: Prompts are broken down into **Noun, Action, Location, Time, Environment, and Result**.
*   **Atomic Building Blocks**: Users can pick "Lego-like" words (e.g., *Old man, Smiling, Victorian study*) instead of rigid long sentences.
*   **逻辑矩阵**：将提示词拆解为**名词、动作、地点、时间、环境、结果**六大维度。
*   **原子化积木**：用户可以像拼乐高一样自由组合词汇（如：*老人、微笑、维多利亚书房*），而非死板的长句。

### 2. **Data-Logic Decoupling | 数据与逻辑彻底解耦**
*   **JSON Driven**: All categories and vocabularies are stored in an external `lexicon.json`.
*   **Zero-Code Customization**: Users can expand the library by simply editing the JSON file without touching the Python core.
*   **数据驱动**：所有分类与词库均存储在外部 `lexicon.json` 中。
*   **零代码自定义**：用户只需编辑 JSON 文件即可扩容词库，无需修改 Python 源代码。

### 3. **High-Fidelity Offline TTS | 电影级离线语音**
*   **ChatTTS Integration**: Powered by the **ChatTTS** engine, providing natural, human-like voice synthesis with "breathing" and "pauses".
*   **No API Needed**: 100% local operation with zero Token cost and full privacy protection.
*   **电影级语音**：集成 **ChatTTS** 引擎，提供带有“呼吸感”和“自然停顿”的拟人化语音反馈。
*   **无需 API**：100% 本地运行，零 Token 消耗，完美保护用户创作隐私。

### 4. **Python 3.14 Extreme Compatibility | 极客级环境兼容**
*   **Memory Defense System**: Includes a custom **Module Mocking** layer to bypass `pybase16384` compilation issues on Python 3.14.
*   **Adaptive Loading**: Uses `strict=False` state-dict loading to ensure cross-version model stability.
*   **内存防御系统**：内置自定义**动态拦截器**，完美绕过 Python 3.14 环境下的 `pybase16384` 编译天坑。
*   **自适应加载**：通过 `strict=False` 宽松加载模式，确保跨版本模型的稳定性。

---

## 🚀 Installation | 安装指南

### Prerequisites | 环境要求
*   **Python 3.14+** (Optimized for cutting-edge environments)
*   **CUDA Enabled GPU** (Optional but recommended for ChatTTS speed)

### Step 1: Install Dependencies | 安装依赖
```bash
pip install torch numpy sounddevice ChatTTS OmegaConf requests scipy
```
*[Note: `torch` is essential for the AI brain, while `sounddevice` handles the audio output.]*

### Step 2: Deploy Assets | 部署资源
Ensure `lexicon.json` is placed in the same directory as the script.

---

## 🛠️ Technical Breakdown | 核心架构

| Component | Function |
| :--- | :--- |
| **Logic Layer** | `UltimateDecoupledMatrixV65` - Python/Tkinter engine. |
| **Data Layer** | `lexicon.json` - High-density human civilization visual map. |
| **Audio Layer** | **ChatTTS** + **sounddevice** for real-time auditory feedback. |
| **Hack Layer** | **400-byte Memory Alignment** to fix NumPy/PyTorch mismatches. |

---

## 📂 Project Structure | 项目结构

```text
.
├── main.py              # The "Engine" (Logic Layer)
├── lexicon.json         # The "Fuel" (Data Layer: Nouns, Actions, Styles...)
├── saved_prompts.txt    # Local asset storage with timestamps
└── stored_audio/        # Generated .wav files for persistence
```

---

## 💡 Why This Project? | 为什么发起这个项目？

This tool was created to help a **70-year-old grandmother** learn to paint with AI and to inspire **children** to explore their imagination. By turning complex English prompts into intuitive Chinese "building blocks," we aim to democratize AI technology for everyone.

这个工具是为了帮助 **70 岁的老奶奶** 学习 AI 绘画，并启发 **孩子们** 的想象力而创造。 通过将复杂的英文提示词转化为直观的中文“积木”，我们致力于让 AI 技术普惠每一个人。

---

## 📜 License | 许可证
**MIT License** - Feel free to hack, modify, and share. [Conversational Remark]
