# revctl

> Local AI code reviewer — no data ever leaves your machine.

`revctl` is a terminal tool that runs a full code review on your git changes using a local AI model via [Ollama](https://ollama.com). No API keys, no subscriptions, no data sent to external servers.

```
$ revctl diff --focus security

╭─────────────────── revctl ────────────────────╮
│ Reviewing: staged changes                     │
│ Model:     qwen2.5-coder:7b  (local · no data sent) │
╰───────────────────────────────────────────────╯

## Summary
This change replaces a raw SQL string with a parameterized query.

## Issues
No critical issues found.

## Security
✓ SQL injection risk eliminated by using parameterized query.

## Verdict
APPROVE — Clean fix, no concerns.
```

---

## Why revctl?

- **Private by design** — your code runs through a model on your own CPU/GPU
- **Works offline** — no internet required after setup
- **Fast feedback loop** — review staged changes before committing
- **Three review modes** — diff, commit, branch (like a local PR)

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- At least one code model pulled (see [Recommended Models](#recommended-models))

---

## Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/revctl.git
cd revctl

# Install (creates the `revctl` command globally)
pip install -e .
```

---

## Setup

**1. Install Ollama**

Download from [ollama.com/download](https://ollama.com/download) and run the installer.

**2. Pull a code model**

```bash
ollama pull qwen2.5-coder:7b
```

**3. Confirm everything works**

```bash
revctl models
```

You should see `qwen2.5-coder:7b` listed as available.

---

## Usage

### Review current changes

Reviews staged files. Falls back to unstaged if nothing is staged.

```bash
revctl diff
```

### Review a specific commit

```bash
revctl commit <hash>

# Example
revctl commit a3f9c12
```

### Review a branch (local PR)

Compares a feature branch against a base branch — same as a GitHub PR review, but local.

```bash
revctl branch <head> [base]

# Examples
revctl branch feature/login main
revctl branch feat/payment dev
```

### List available models

```bash
revctl models
```

---

## Options

All review commands accept the same optional flags:

| Flag | Short | Values | Description |
|------|-------|--------|-------------|
| `--model` | `-m` | any Ollama model name | Override the default model |
| `--focus` | `-f` | `security` \| `performance` \| `style` | Direct the AI to focus on a specific concern |

**Examples:**

```bash
# Focus on security issues only
revctl diff --focus security

# Use a different model
revctl diff --model codellama:7b

# Review a branch with a performance lens
revctl branch feat/db-query main --focus performance
```

---

## Recommended Models

| Model | Size | Best for |
|-------|------|----------|
| `qwen2.5-coder:7b` | ~4.7 GB | General code review *(default)* |
| `qwen2.5-coder:14b` | ~9 GB | Higher quality, needs more RAM |
| `codellama:7b` | ~3.8 GB | Lighter option, less context |
| `deepseek-coder:6.7b` | ~3.8 GB | Good alternative to codellama |

Pull any model with:
```bash
ollama pull <model-name>
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Project Structure

```
revctl/
├── cli_review/
│   ├── main.py      # CLI commands (typer)
│   ├── git.py       # git diff/commit/branch parsing
│   ├── ollama.py    # Ollama API client (streaming)
│   ├── prompt.py    # Review prompt templates
│   └── output.py    # Terminal formatting (rich)
├── tests/
│   ├── test_cli.py
│   ├── test_git.py
│   ├── test_ollama.py
│   └── test_prompt.py
└── pyproject.toml
```

---

## License

MIT
