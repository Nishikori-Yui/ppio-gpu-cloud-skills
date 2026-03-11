# PPIO GPU 云技能

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E)](https://opensource.org/licenses/MIT)
[![Stage: Alpha](https://img.shields.io/badge/Stage-Alpha-F59E0B)](https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills)

[English](README.md)

## 概览

这个子仓库封装了一个 Codex skill，用于通过 PPIO 官方 GPU OpenAPI 管理 GPU 容器实例。

仓库围绕一条尽量收敛的操作路径设计：

- 查询集群和 GPU 产品
- 查询 VPC 网络
- 查询现有实例
- 仅在用户明确要求时创建或控制实例

## 仓库结构

- `skills/ppio-gpu-manager/`：skill 本体，包含元数据、参考资料和脚本

## 快速开始

1. 从示例创建本地环境文件：

```bash
cp .env.example .env
```

2. 在 `.env` 中填入 API Key，或直接导出环境变量：

```bash
export PPIO_API_KEY="your-api-key"
```

3. 查询集群：

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py clusters
```

4. 查询 GPU 产品：

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py gpu-products
```

5. 查询实例：

```bash
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances
```

CLI 会自动加载就近的 `.env` 文件，不需要手工 `source`。如果存在多个 `.env`，会优先使用 skill 目录附近的 `.env`，然后再向上查找。

## 参考资料

- [PPIO GPU 云参考](https://ppio.com/docs/gpus/reference-start)

## 许可证

本仓库采用 MIT License。
