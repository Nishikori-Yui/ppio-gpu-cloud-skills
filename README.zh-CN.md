# PPIO GPU 云技能

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E)](https://opensource.org/licenses/MIT)
[![Stage: Alpha](https://img.shields.io/badge/Stage-Alpha-F59E0B)](https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills)

[English](README.md)

## 概览

这个子仓库提供了一个 Python CLI 工具，用于通过 PPIO 官方 GPU OpenAPI 管理 GPU 容器实例。它可以由 AI 助手（如 Claude Code、Codex）直接调用或从命令行使用。

仓库围绕一条尽量收敛的操作路径设计：

- 查询集群和 GPU 产品
- 查询 VPC 网络
- 查询现有实例
- 仅在用户明确要求时创建或控制实例

## 仓库结构

- `skills/ppio-gpu-manager/`：skill 本体，包含元数据、参考资料和脚本

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills.git
cd ppio-gpu-cloud-skills
```

### 2. 配置 API Key

从示例文件创建 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 设置 API key，或直接导出环境变量：

```bash
export PPIO_API_KEY="your-api-key"
```

### 3. 运行命令

```bash
# 查询可用集群
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py clusters

# 查询 GPU 产品
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py gpu-products

# 查询实例列表
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances

# 查询指定实例详情
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instance --instance-id "<instance-id>"
```

CLI 会自动加载 skill 目录或父目录中的 `.env` 文件。如果存在多个 `.env`，skill 目录附近的文件优先。

## 参考资料

- [GPU 容器 API 手册](https://ppio.com/docs/gpus/reference-start)

## 许可证

本仓库采用 MIT License。
