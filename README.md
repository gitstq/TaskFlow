<div align="center">

# 🚀 TaskFlow

**轻量级终端任务调度与自动化引擎**

*Lightweight Terminal Task Scheduling & Automation Engine*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

TaskFlow 是一个**零依赖**的轻量级终端任务调度与自动化引擎，专为开发者和系统管理员设计。它提供了类似 Cron 的任务调度能力，同时增加了任务依赖管理、超时控制、重试机制等高级功能，全部通过优雅的 TUI（终端用户界面）和 CLI 进行操作。

### ✨ 核心亮点

- 🎯 **零依赖设计** - 仅使用 Python 标准库，无需安装任何第三方包
- ⏰ **灵活的调度** - 支持标准 Cron 表达式和特殊关键字（@hourly, @daily, @reboot）
- 🔗 **任务依赖** - 支持任务链式依赖，确保任务按正确顺序执行
- 🛡️ **健壮性** - 内置超时控制、失败重试、错误日志记录
- 🖥️ **TUI 界面** - 美观的终端交互界面，操作简单直观
- 📝 **完整日志** - 详细的执行日志，便于排查问题
- 🌍 **跨平台** - 支持 Linux、macOS、Windows

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🕐 **Cron 表达式** | 支持标准 5 字段 Cron 表达式（分 时 日 月 星期） |
| 🔄 **特殊调度** | @hourly、@daily、@weekly、@monthly、@reboot |
| 🔗 **任务依赖** | 支持多任务依赖，自动处理执行顺序 |
| ⏱️ **超时控制** | 可为每个任务设置超时时间 |
| 🔄 **失败重试** | 支持失败重试，可设置重试次数和间隔 |
| 📊 **统计信息** - 任务执行统计，成功率分析 |
| 🖥️ **TUI 界面** | 彩色终端界面，支持任务管理 |
| 📝 **日志记录** | 详细的执行日志，支持按任务筛选 |
| 🌍 **跨平台** | 支持 Linux、macOS、Windows |

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Linux / macOS / Windows

### 安装

#### 方式一：直接下载使用

```bash
# 克隆仓库
git clone https://github.com/gitstq/TaskFlow.git
cd TaskFlow

# 直接使用
python taskflow.py --help
```

#### 方式二：安装为系统命令

```bash
# 安装
pip install -e .

# 使用
taskflow --help
tf --help
```

---

## 📖 详细使用指南

### 1. TUI 交互模式（推荐）

启动美观的终端界面：

```bash
taskflow --tui
```

界面功能：
- 📋 查看任务列表
- ➕ 添加新任务
- ✏️ 编辑任务
- 🗑️ 删除任务
- ▶️ 立即运行任务
- 📜 查看执行日志
- 📊 查看统计信息

### 2. CLI 命令模式

#### 添加任务

```bash
# 基本任务
taskflow add \
  --id backup \
  --name "每日备份" \
  --command "bash backup.sh" \
  --schedule "0 2 * * *" \
  --description "每天凌晨2点执行备份"

# 带重试的任务
taskflow add \
  --id web-scraper \
  --name "数据抓取" \
  --command "python scraper.py" \
  --schedule "0 * * * *" \
  --description "每小时抓取数据"
```

#### 列出所有任务

```bash
taskflow list
```

#### 立即运行任务

```bash
taskflow run backup
```

#### 删除任务

```bash
taskflow remove backup
```

#### 查看日志

```bash
# 查看所有日志
taskflow logs

# 查看特定任务的日志
taskflow logs --task backup --limit 50
```

#### 查看统计

```bash
taskflow stats
```

#### 后台运行调度器

```bash
taskflow --daemon
```

### 3. Cron 表达式指南

| 表达式 | 说明 |
|--------|------|
| `*/5 * * * *` | 每 5 分钟 |
| `0 * * * *` | 每小时 |
| `0 2 * * *` | 每天凌晨 2 点 |
| `0 0 * * 0` | 每周日 |
| `0 0 1 * *` | 每月 1 号 |
| `@hourly` | 每小时 |
| `@daily` | 每天 |
| `@weekly` | 每周 |
| `@reboot` | 启动时执行 |

### 4. Python API 使用

```python
from taskflow import TaskEngine, Task

# 创建引擎
engine = TaskEngine()

# 添加任务
task = Task(
    id="my-task",
    name="我的任务",
    command="echo 'Hello World'",
    schedule="*/5 * * * *",
    timeout=300,
    retry_count=3
)
engine.add_task(task)

# 启动调度器
engine.start()
```

---

## 💡 设计思路与迭代规划

### 设计理念

TaskFlow 的设计遵循以下原则：

1. **简洁至上** - 零依赖，开箱即用
2. **功能完整** - 覆盖任务调度的核心需求
3. **易于扩展** - 模块化设计，便于二次开发
4. **用户友好** - TUI 界面降低使用门槛

### 技术选型

- **纯标准库** - 不依赖任何第三方包，降低维护成本
- **线程调度** - 使用 Python threading 实现轻量级并发
- **JSON 存储** - 任务数据使用 JSON 格式存储，便于查看和备份

### 后续迭代计划

- [ ] Web 管理界面
- [ ] 任务执行历史图表
- [ ] 邮件/Slack 通知
- [ ] 任务模板市场
- [ ] 分布式任务调度
- [ ] REST API 接口

---

## 📦 打包与部署

### 打包为可执行文件

使用 PyInstaller 打包：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --name taskflow taskflow.py

# 可执行文件在 dist/ 目录
```

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY taskflow.py .

ENTRYPOINT ["python", "taskflow.py"]
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细规范。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<a name="繁體中文"></a>
## 🎉 專案介紹（繁體中文）

TaskFlow 是一個**零依賴**的輕量級終端任務調度與自動化引擎，專為開發者和系統管理員設計。它提供了類似 Cron 的任務調度能力，同時增加了任務依賴管理、超時控制、重試機制等高級功能。

### ✨ 核心特性

- 🎯 **零依賴設計** - 僅使用 Python 標準庫
- ⏰ **靈活的調度** - 支援標準 Cron 表達式和特殊關鍵字
- 🔗 **任務依賴** - 支援任務鏈式依賴
- 🛡️ **健壯性** - 內置超時控制、失敗重試
- 🖥️ **TUI 界面** - 美觀的終端交互界面

### 🚀 快速開始

```bash
# 克隆倉庫
git clone https://github.com/gitstq/TaskFlow.git
cd TaskFlow

# 啟動 TUI 界面
python taskflow.py --tui
```

---

<a name="english"></a>
## 🎉 Project Introduction (English)

TaskFlow is a **zero-dependency** lightweight terminal task scheduling and automation engine designed for developers and system administrators. It provides Cron-like task scheduling capabilities with advanced features like task dependency management, timeout control, and retry mechanisms.

### ✨ Key Features

- 🎯 **Zero Dependencies** - Uses only Python standard library
- ⏰ **Flexible Scheduling** - Supports standard Cron expressions and special keywords
- 🔗 **Task Dependencies** - Chain tasks with dependency management
- 🛡️ **Robustness** - Built-in timeout control and retry mechanisms
- 🖥️ **TUI Interface** - Beautiful terminal user interface
- 📝 **Complete Logging** - Detailed execution logs
- 🌍 **Cross-Platform** - Linux, macOS, Windows support

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/gitstq/TaskFlow.git
cd TaskFlow

# Start TUI interface
python taskflow.py --tui

# Or use CLI
python taskflow.py add --id backup --name "Daily Backup" --command "bash backup.sh" --schedule "0 2 * * *"
```

### 📖 Usage

#### Add Task

```bash
taskflow add \
  --id my-task \
  --name "My Task" \
  --command "echo 'Hello'" \
  --schedule "*/5 * * * *"
```

#### List Tasks

```bash
taskflow list
```

#### Run Task Immediately

```bash
taskflow run my-task
```

#### View Logs

```bash
taskflow logs --task my-task
```

### 📄 License

[MIT License](LICENSE)

---

<div align="center">

**Made with ❤️ by TaskFlow Team**

⭐ Star us on GitHub — it motivates us a lot!

</div>
