---
name: ppio-gpu-manager
description: Manage the full official PPIO GPU API through a grouped CLI wrapper. Use when Codex needs to query account or billing information, inspect clusters and products, manage jobs, networks, instances, templates, images, image prewarm tasks, endpoints, or call additional documented GPU endpoints through a generic fallback command.
---

# PPIO GPU Manager

## Overview

Use only the official PPIO GPU API and official PPIO documentation for this skill.

Default to read-only discovery commands. Treat mutating actions across networks, instances, templates, images, image prewarming, and endpoints as explicit-intent operations that must match clear user intent.

## Quick Start

1. Create `.env` from `.env.example`, or ensure `PPIO_API_KEY` is exported.
2. Use `scripts/ppio_gpu.py` for all API calls.
3. Read `references/ppio-gpu-api.md` when you need grouped endpoint mappings or example payload patterns.
4. Prefer the generic `request` subcommand only when the wrapped commands do not cover the needed endpoint.

When multiple `.env` files exist, the skill-local `.env` is preferred.

The runtime behind `scripts/ppio_gpu.py` is modularized by official API family. Keep new endpoint wiring inside the matching domain module instead of growing one monolithic script.

## Workflow

### Discover and Audit State

- Query account data:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py base user-info
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py billing subscription-bills
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py billing payg-bills
  ```
- Discover capacity:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py clusters list
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py products gpu
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py products cpu
  ```
- Inspect jobs, templates, images, and endpoints:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py jobs list
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py templates list
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py images list
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py endpoints list
  ```

### Mutating Workflows

- Create or update resources from explicit request bodies:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py networks create --body-file /absolute/path/create-vpc.json
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances create-gpu --body-file /absolute/path/create-gpu-instance.json
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py templates create --body-file /absolute/path/create-template.json
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py images prewarm-create --body-file /absolute/path/create-prewarm.json
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py endpoints create --body-file /absolute/path/create-endpoint.json
  ```
- For smaller bodies, repeated `--set key=value` flags are supported on body-based commands.

When building creation or edit payloads, discover the target cluster, product, instance, image, or endpoint first instead of guessing.

## Safety Rules

- Stay read-only unless the user explicitly asks for a mutating action.
- Use list or get commands before delete or edit operations when the target looks ambiguous.
- Default output redacts common secret-like fields such as passwords and tokens. Use `--show-secrets` only when the user explicitly needs those values.
- Surface the raw API error body when a request fails; do not paraphrase away the remote error.
- Do not store API keys or passwords in repository files.
- Keep secrets only in the local `.env`, the shell environment, or one-shot flags.
- Keep request specs as temporary local JSON files or inline `--set` overrides.

## Generic Request Fallback

Use `request` when the official docs expose an endpoint variation that the wrapper does not yet cover:

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py request GET /clusters
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py request POST /endpoint/create --body-json '{"name":"example"}'
```

Use relative paths under the selected documented API surface by default. Pass an absolute URL only when the upstream API introduces a documented path outside the default base.

## Resources

### `scripts/ppio_gpu.py`

A stable CLI entrypoint for the modular full-surface PPIO GPU runtime.

### `scripts/ppio_gpu_runtime/`

The modular runtime package. Shared transport logic stays in common modules, while each official API family keeps its own domain-specific command definitions.

### `references/ppio-gpu-api.md`

Read this file when you need exact documented endpoint paths, grouped command mappings, or example commands derived from the official PPIO documentation.
