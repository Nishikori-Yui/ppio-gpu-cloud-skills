# PPIO GPU 云技能

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E)](https://opensource.org/licenses/MIT)
[![Stage: Alpha](https://img.shields.io/badge/Stage-Alpha-F59E0B)](https://github.com/Nishikori-Yui/ppio-gpu-cloud-skills)

[English](README.md)

## 概览

这个子仓库提供了一个 Python CLI 工具，用于封装 PPIO 官方文档中完整的 GPU API。它可以由 AI 助手（如 Claude Code、Codex）直接调用或从命令行使用。

当前目标覆盖 `https://ppio.com/docs/gpus/` 下的官方 GPU API 分组：

- 基础账户接口
- 账单接口
- 集群和产品接口
- 任务接口
- 网络接口
- 实例接口
- 模板接口
- 镜像和镜像预热接口
- Endpoint 接口

默认仍然优先只读查询，所有变更类操作都要求明确意图。

## 仓库结构

- `skills/ppio-gpu-manager/`：skill 本体，包含元数据、参考资料和脚本
- `skills/ppio-gpu-manager/scripts/ppio_gpu.py`：稳定 CLI 入口，保留给命令行与 AI 工具直接调用
- `skills/ppio-gpu-manager/scripts/ppio_gpu_runtime/`：按 API 领域拆分的运行时包，避免把完整官方接口包装继续堆在单个超长文件中

## 运行时设计

之所以采用模块化设计，是因为官方 GPU API 面较大，而且后续还可能继续扩展。

- 公共请求、环境加载、输出脱敏、错误处理放在共享运行时模块。
- 命令树注册集中在 CLI 模块。
- 每个官方 API 分组分别放在独立领域模块，例如 base、billing、clusters、products、jobs、networks、instances、templates、images、endpoints。
- `request` 仍然保留为文档覆盖之外的官方接口兜底命令。

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
# 查询账户信息
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py base user-info

# 查询 GPU 和 CPU 产品
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py products gpu
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py products cpu

# 查询实例和模板列表
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances list
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py templates list

# 查询镜像预热配额
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py images quota
```

CLI 会自动加载 skill 目录或父目录中的 `.env` 文件。如果存在多个 `.env`，skill 目录附近的文件优先。

## 命令分组

- `base`：账户信息
- `billing`：包年包月与按量账单
- `clusters`：集群查询
- `products`：GPU / CPU 产品
- `jobs`：任务查询与中断
- `networks`：VPC 创建、查询、修改、删除
- `instances`：实例创建、查询、编辑、启停、升级、迁移、监控、续费、计费切换、删除
- `templates`：模板创建、更新、删除、列表、详情
- `images`：镜像保存、查询、删除、预热、镜像认证信息
- `endpoints`：限制范围、创建、查询、更新、删除
- `request`：官方文档接口的通用兜底

为兼容现有用法，`clusters`、`gpu-products`、`vpcs`、`instances`、`instance`、`create-instance`、`start`、`stop`、`restart`、`delete` 这些旧扁平命令仍会保留。

## 参考资料

- [GPU 容器 API 手册](https://ppio.com/docs/gpus/reference-start)

## 许可证

本仓库采用 MIT License。
