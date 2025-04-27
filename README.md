# Open Codex

<h1 align="center">Open Codex CLI</h1>
<p align="center">Lightweight coding agent that runs in your terminal</p>
<p align="center"><code>brew tap codingmoh/open-codex && brew install open-codex</code></p>

![Codex demo GIF using: codex "explain this codebase to me"](./.github/demo.gif)

---

**Open Codex** is a fully open-source command-line AI assistant inspired by OpenAI Codex, supporting optimized local language models.

No API key is required for the default model. Everything runs locally.

Supports:
- **One-shot mode**: `open-codex "list all folders"` -> returns shell command
- 🧠 Local-only execution using optimized models:
  - phi-4-mini (default, no auth required)
  - qwen1.5-7b-chat (auth required, enhanced for coding tasks)

---
## ✨ Features

- Natural Language to Shell Command (via local models)
- Works on macOS, Linux, and Windows (Python-based)
- Smart command validation and error handling
- Real-time command output streaming
- Add to clipboard / abort / execute prompt
- One-shot interaction mode (interactive and function-calling coming soon)
- Colored terminal output for better readability

---

## 🧱 Future Plans

- Interactive, context aware mode
- Fancy TUI with `textual` or `rich`
- Add support for additional OSS Models
- Full interactive chat mode
- Function-calling support
- Voice input via Whisper
- Command history and undo
- Plugin system for workflows

---


## 📦 Installation


### 🔹 Option 1: Install via Homebrew (Recommended for MacOS)

```bash
brew tap codingmoh/open-codex
brew install open-codex
```


### 🔹 Option 2: Install via pipx (cross-platform)

```bash
pipx install open-codex
```

### 🔹 Option 3: Clone & Install locally

```bash
git clone https://github.com/codingmoh/open-codex.git
cd open_codex
pip install .
```


Once installed, you can use the `open-codex` CLI globally.

---

## 🚀 Usage

### One-shot mode

Basic usage with default model (phi-4-mini):
```bash
open-codex "list all python files"
```

Using Qwen model for enhanced coding tasks:
```bash
# First, set your Hugging Face token
export HUGGINGFACE_TOKEN=your_token_here

# Then use the Qwen model
open-codex --model qwen-2.5-coder "find python files modified today"

# Or provide token directly
open-codex --model qwen-2.5-coder --hf-token your_token_here "your command"
```

✅ Codex suggests a validated shell command  
✅ Shows real-time command output  
✅ Provides clear error messages  
✅ Asks for confirmation / add to clipboard / abort  
✅ Executes if approved  

### Model Overview

#### phi-4-mini (Default)
- Fast and lightweight
- No authentication required
- Optimized for quick shell commands
- Best for basic file operations and system tasks

#### qwen1.5-7b-chat
- Enhanced for coding tasks
- Requires Hugging Face authentication
- Improved command validation
- Better for complex development tasks

---

## 🛡️ Security Notice

All models run locally. Commands are only executed after explicit approval.

---

## 🧑‍💻 Contributing

PRs welcome! Ideas, issues, improvements — all appreciated.

---

## 📝 License

MIT

---

❤️ Built with love and caffeine by [codingmoh](https://github.com/codingmoh).

