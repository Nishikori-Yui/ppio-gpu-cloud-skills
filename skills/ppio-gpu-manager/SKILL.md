---
name: ppio-gpu-manager
description: Manage PPIO GPU container resources through the official PPIO GPU OpenAPI. Use when Codex needs to inspect PPIO clusters, list GPU products, inspect or create VPC networks, create GPU instances from a checked JSON spec, list instances, inspect instance details, or start, stop, restart, and delete PPIO GPU instances.
---

# PPIO GPU Manager

## Overview

Use only the official PPIO GPU API and official PPIO documentation for this skill.

Default to read-only discovery commands. Treat `create-instance`, `create-vpc`, `start`, `stop`, `restart`, and `delete` as explicit-intent operations that must match clear user intent.

## Quick Start

1. Create `.env` from `.env.example`, or ensure `PPIO_API_KEY` is exported.
2. Use `scripts/ppio_gpu.py` for all API calls.
3. Read `references/ppio-gpu-api.md` when you need request fields, status values, or example payloads.
4. Prefer the generic `request` subcommand only when the wrapped commands do not cover the needed endpoint.

When multiple `.env` files exist, the skill-local `.env` is preferred.

## Workflow

### Discover Capacity

- List clusters first when placement matters:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py clusters
  ```
- List GPU products, optionally filtered by cluster or billing mode:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py gpu-products --cluster-id "<cluster-id>"
  ```
  The command enriches raw upstream prices into readable `CNY/hour` and `CNY/month` fields while preserving the raw values.
- Inspect VPC networks if the workload needs private networking:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py vpcs
  ```

### Create or Update Resources

- Create a VPC from explicit fields:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py create-vpc --cluster-id "<cluster-id>" --name "team-net"
  ```
- Create a GPU instance from a JSON body file:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py create-instance --body-file /absolute/path/create-instance.json
  ```
- Create a GPU instance from inline overrides when the body is small:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py create-instance \
    --set name=trainer-a10 \
    --set productId=prod_xxx \
    --set gpuNum=1 \
    --set rootfsSize=80 \
    --set imageUrl=nvcr.io/nvidia/pytorch:24.02-py3 \
    --set billingMode=onDemand \
    --set kind=gpu
  ```

When building a creation payload, discover `clusterId` and `productId` first instead of guessing. If the user requests a private network, inspect VPC support from cluster data before attempting VPC creation.

### Inspect and Control Instances

- List instances:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances
  ```
- Inspect one instance:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instance --instance-id "<instance-id>"
  ```
- Start, stop, restart, or delete an instance:
  ```bash
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py start --instance-id "<instance-id>"
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py stop --instance-id "<instance-id>"
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py restart --instance-id "<instance-id>"
  python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py delete --instance-id "<instance-id>"
  ```

Before a destructive action, inspect the instance first unless the user has already identified the exact target and action.

## Safety Rules

- Stay read-only unless the user explicitly asks for a mutating action.
- Use `instance` before `delete` when the target looks ambiguous.
- Default output redacts common secret-like fields such as passwords and tokens. Use `--show-secrets` only when the user explicitly needs those values.
- Surface the raw API error body when a request fails; do not paraphrase away the remote error.
- Do not store API keys or passwords in repository files.
- Keep secrets only in the local `.env`, the shell environment, or one-shot flags.
- Keep request specs as temporary local JSON files or inline `--set` overrides.

## Generic Request Fallback

Use `request` when the official docs expose an endpoint that the wrapper does not yet cover:

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py request GET /clusters
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py request POST /gpu/instance/start --body-json '{"instanceId":"abc123"}'
```

Use relative paths under the documented API base by default. Pass an absolute URL only when the upstream API introduces a documented path outside the default base.

## Resources

### `scripts/ppio_gpu.py`

A standard-library Python CLI wrapper for the common PPIO GPU instance and VPC operations.

### `references/ppio-gpu-api.md`

Read this file when you need exact documented endpoint paths, core request fields, status enums, or example commands derived from the official PPIO documentation.
