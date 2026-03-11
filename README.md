# PPIO GPU Cloud Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E)](https://opensource.org/licenses/MIT)
[![Stage: Alpha](https://img.shields.io/badge/Stage-Alpha-F59E0B)](https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills)

[简体中文](README.zh-CN.md)

## Overview

This repository provides a Python CLI tool for managing PPIO GPU container instances through the official PPIO GPU OpenAPI. It can be used directly from the command line or invoked by AI assistants such as Claude Code and Codex.

The repository is designed around a compact operational workflow:

- discover clusters and GPU products,
- inspect VPC networks,
- inspect existing instances,
- create or control instances only when intent is explicit.

## Repository Layout

- `skills/ppio-gpu-manager/`: the skill package, including metadata, references, and automation scripts.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills.git
cd ppio-gpu-cloud-skills
```

### 2. Configure API Key

Create `.env` from the example file:

```bash
cp .env.example .env
```

Edit `.env` and set your API key, or export it directly:

```bash
export PPIO_API_KEY="your-api-key"
```

### 3. Run Commands

```bash
# List available clusters
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py clusters

# List GPU products
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py gpu-products

# List instances
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances

# Inspect a specific instance
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instance --instance-id "<instance-id>"
```

The CLI automatically loads `.env` files from the skill directory or parent directories. If multiple `.env` files exist, the skill-local one takes precedence.

## Resources

- [GPU Container API Reference](https://ppio.com/docs/gpus/reference-start)

## License

This repository is released under the MIT License.
