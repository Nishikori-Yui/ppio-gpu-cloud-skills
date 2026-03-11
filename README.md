# PPIO GPU Cloud Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E)](https://opensource.org/licenses/MIT)
[![Stage: Alpha](https://img.shields.io/badge/Stage-Alpha-F59E0B)](https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills)

[简体中文](README.zh-CN.md)

## Overview

This repository provides a Python CLI tool for wrapping the full officially documented PPIO GPU API surface. It can be used directly from the command line or invoked by AI assistants such as Claude Code and Codex.

The repository covers the official GPU API groups under `https://ppio.com/docs/gpus/`:

- base account APIs,
- billing APIs,
- clusters and products,
- jobs,
- networks,
- instances,
- templates,
- images and image prewarming,
- endpoints.

Read-only discovery remains the default operating mode. Mutating actions stay explicit.

## Repository Layout

- `skills/ppio-gpu-manager/`: the skill package, including metadata, references, and automation scripts.
- `skills/ppio-gpu-manager/scripts/ppio_gpu.py`: stable CLI entrypoint for direct shell use and AI-tool integration.
- `skills/ppio-gpu-manager/scripts/ppio_gpu_runtime/`: modular runtime package split by API domain so the full API wrapper does not collapse into one oversized file.

## Runtime Design

The runtime is intentionally modular because the official GPU API surface is broad and still growing.

- Shared request, environment, redaction, and error-handling logic lives in a common runtime module.
- Command registration is centralized in a CLI module.
- Each official API family is defined in its own domain module, such as base, billing, clusters, products, jobs, networks, instances, templates, images, and endpoints.
- The generic `request` command remains available as a documented fallback for future upstream additions.

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
# Query account information
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py base user-info

# List GPU and CPU products
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py products gpu
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py products cpu

# List instances and templates
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances list
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py templates list

# Query image prewarm quota
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py images quota
```

The CLI automatically loads `.env` files from the skill directory or parent directories. If multiple `.env` files exist, the skill-local one takes precedence.

## Command Groups

- `base`: account information
- `billing`: monthly and pay-as-you-go bills
- `clusters`: cluster discovery
- `products`: GPU and CPU products
- `jobs`: task listing and termination
- `networks`: VPC create/list/get/update/delete
- `instances`: create/list/get/edit/start/stop/restart/upgrade/migrate/monitor/renew/billing-policy/delete
- `templates`: create/update/delete/list/get
- `images`: save/list/delete/quota/prewarm/auths
- `endpoints`: limits/create/list/get/update/delete
- `request`: generic fallback for documented endpoints

Legacy flat commands such as `clusters`, `gpu-products`, `vpcs`, `instances`, `instance`, `create-instance`, `start`, `stop`, `restart`, and `delete` remain available for compatibility.

## Resources

- [GPU Container API Reference](https://ppio.com/docs/gpus/reference-start)

## License

This repository is released under the MIT License.
