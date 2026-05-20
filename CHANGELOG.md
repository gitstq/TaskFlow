# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-20

### 🎉 Initial Release

#### Added
- ✨ Zero-dependency design using only Python standard library
- ⏰ Full Cron expression support (minute hour day month weekday)
- 🔄 Special schedule keywords (@hourly, @daily, @weekly, @monthly, @reboot)
- 🔗 Task dependency management with automatic execution ordering
- ⏱️ Configurable timeout control for each task
- 🔄 Retry mechanism with configurable count and delay
- 🖥️ Beautiful TUI (Terminal User Interface) for interactive management
- 📝 Comprehensive logging system with task-specific filtering
- 📊 Statistics dashboard showing execution metrics
- 🌍 Cross-platform support (Linux, macOS, Windows)
- 📚 Multi-language documentation (简体中文, 繁體中文, English)
- 🔧 CLI commands: add, list, remove, run, logs, stats
- 📦 Easy installation via pip or direct download
- 🧪 Example scripts for common use cases

#### Features
- **Task Scheduling**: Schedule tasks using familiar Cron syntax
- **Task Dependencies**: Chain tasks together for complex workflows
- **Error Handling**: Automatic retry on failure with exponential backoff
- **Logging**: Detailed execution logs for debugging
- **Statistics**: Track success rates and execution counts
- **Interactive UI**: Colorful terminal interface for easy management

---

## Release Notes

### v1.0.0 - TaskFlow Initial Release

**TaskFlow** is a lightweight, zero-dependency terminal task scheduling and automation engine.

**Key Highlights:**
- 🎯 **Zero Dependencies**: Pure Python standard library implementation
- ⚡ **Lightweight**: Single file, minimal resource usage
- 🎨 **Beautiful TUI**: Interactive terminal interface
- 🔧 **Powerful CLI**: Complete command-line interface
- 📖 **Well Documented**: Multi-language README and examples

**Installation:**
```bash
pip install -e .
# or
python taskflow.py --tui
```

**Quick Start:**
```bash
# Add a task
taskflow add --id backup --name "Daily Backup" --command "bash backup.sh" --schedule "0 2 * * *"

# Start TUI
taskflow --tui

# Run daemon
taskflow --daemon
```

---

**Full Changelog**: https://github.com/gitstq/TaskFlow/commits/v1.0.0
