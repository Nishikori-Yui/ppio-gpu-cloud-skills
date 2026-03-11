# PPIO GPU Cloud Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E)](https://opensource.org/licenses/MIT)
[![Stage: Alpha](https://img.shields.io/badge/Stage-Alpha-F59E0B)](https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills)

[简体中文](README.zh-CN.md)

## Overview

This repository packages a Codex skill for managing PPIO GPU container instances through the official PPIO GPU OpenAPI.

The repository is designed around a compact operational workflow:

- discover clusters and GPU products,
- inspect VPC networks,
- inspect existing instances,
- create or control instances only when intent is explicit.

## Repository Layout

- `skills/ppio-gpu-manager/`: the skill package, including metadata, references, and automation scripts.

## Quick Start

1. Create a local environment file from the sample:

```bash
cp .env.example .env
```

2. Fill in your API key in `.env`, or export it directly:

```bash
export PPIO_API_KEY="your-api-key"
```

3. Inspect clusters:

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py clusters
```

4. Inspect GPU products:

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py gpu-products
```

5. List instances:

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances
```

The CLI loads a local `.env` file automatically when present and does not require a manual `source` step. If multiple `.env` files exist, the skill-local `.env` is preferred before walking upward from the current working directory.

## Resources

- [PPIO GPU Cloud Reference](https://ppio.com/docs/gpus/reference-start)

## License

This repository is released under the MIT License.
