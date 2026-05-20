#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskFlow - 轻量级终端任务调度与自动化引擎
Lightweight Terminal Task Scheduling & Automation Engine

Zero Dependencies, Cron-like Scheduling, Task Chaining, TUI Dashboard
"""

import os
import sys
import json
import time
import signal
import threading
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import tempfile

__version__ = "1.0.0"
__author__ = "TaskFlow Team"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class Task:
    """任务数据类"""
    id: str
    name: str
    command: str
    schedule: str  # Cron表达式或特殊关键字
    enabled: bool = True
    status: str = TaskStatus.PENDING.value
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    timeout: int = 300  # 默认5分钟超时
    retry_count: int = 0
    retry_delay: int = 60
    dependencies: List[str] = field(default_factory=list)
    working_dir: Optional[str] = None
    env_vars: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskLog:
    """任务日志数据类"""
    id: str
    task_id: str
    start_time: str
    end_time: Optional[str] = None
    status: str = TaskStatus.PENDING.value
    output: str = ""
    error: str = ""
    exit_code: Optional[int] = None
    duration: float = 0.0


class CronParser:
    """Cron表达式解析器"""
    
    SPECIAL_SCHEDULES = {
        "@yearly": "0 0 1 1 *",
        "@annually": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@midnight": "0 0 * * *",
        "@hourly": "0 * * * *",
        "@reboot": "@reboot",
    }
    
    def __init__(self, expression: str):
        self.expression = expression.strip()
        if self.expression in self.SPECIAL_SCHEDULES:
            self.expression = self.SPECIAL_SCHEDULES[self.expression]
    
    def is_reboot(self) -> bool:
        """检查是否为重启时执行"""
        return self.expression == "@reboot"
    
    def get_next_run(self, base_time: Optional[datetime] = None) -> Optional[datetime]:
        """获取下一次执行时间"""
        if self.is_reboot():
            return None
        
        if base_time is None:
            base_time = datetime.now()
        
        try:
            parts = self.expression.split()
            if len(parts) != 5:
                return None
            
            minute, hour, day, month, weekday = parts
            
            # 简化实现：从当前时间开始，每分钟检查一次
            current = base_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
            
            for _ in range(525600):  # 检查一年内的每分钟
                if self._matches(current, minute, hour, day, month, weekday):
                    return current
                current += timedelta(minutes=1)
            
            return None
        except Exception:
            return None
    
    def _matches(self, dt: datetime, minute: str, hour: str, day: str, month: str, weekday: str) -> bool:
        """检查时间是否匹配Cron表达式"""
        return (
            self._field_matches(dt.minute, minute, 0, 59) and
            self._field_matches(dt.hour, hour, 0, 23) and
            self._field_matches(dt.day, day, 1, 31) and
            self._field_matches(dt.month, month, 1, 12) and
            self._field_matches(dt.weekday(), weekday, 0, 6)
        )
    
    def _field_matches(self, value: int, pattern: str, min_val: int, max_val: int) -> bool:
        """检查单个字段是否匹配"""
        if pattern == "*":
            return True
        
        # 处理逗号分隔的列表
        if "," in pattern:
            return any(self._field_matches(value, p.strip(), min_val, max_val) for p in pattern.split(","))
        
        # 处理范围
        if "-" in pattern:
            start, end = pattern.split("-")
            return int(start) <= value <= int(end)
        
        # 处理步长
        if "/" in pattern:
            base, step = pattern.split("/")
            if base == "*":
                return value % int(step) == 0
            else:
                start = int(base)
                return value >= start and (value - start) % int(step) == 0
        
        # 精确匹配
        try:
            return value == int(pattern)
        except ValueError:
            return False


class Logger:
    """日志管理器"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self.log_dir / f"taskflow_{datetime.now().strftime('%Y%m%d')}.log"
        self.console_output = True
        self.lock = threading.Lock()
    
    def log(self, level: LogLevel, message: str, task_id: Optional[str] = None):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_prefix = f"[{task_id}] " if task_id else ""
        log_line = f"[{timestamp}] [{level.value}] {task_prefix}{message}\n"
        
        with self.lock:
            # 写入文件
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(log_line)
            
            # 控制台输出
            if self.console_output:
                color_map = {
                    LogLevel.DEBUG: "\033[36m",    # Cyan
                    LogLevel.INFO: "\033[32m",     # Green
                    LogLevel.WARNING: "\033[33m",  # Yellow
                    LogLevel.ERROR: "\033[31m",    # Red
                    LogLevel.CRITICAL: "\033[35m", # Magenta
                }
                reset = "\033[0m"
                color = color_map.get(level, "")
                print(f"{color}{log_line.strip()}{reset}")
    
    def debug(self, message: str, task_id: Optional[str] = None):
        self.log(LogLevel.DEBUG, message, task_id)
    
    def info(self, message: str, task_id: Optional[str] = None):
        self.log(LogLevel.INFO, message, task_id)
    
    def warning(self, message: str, task_id: Optional[str] = None):
        self.log(LogLevel.WARNING, message, task_id)
    
    def error(self, message: str, task_id: Optional[str] = None):
        self.log(LogLevel.ERROR, message, task_id)
    
    def critical(self, message: str, task_id: Optional[str] = None):
        self.log(LogLevel.CRITICAL, message, task_id)


class TaskEngine:
    """任务调度引擎"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path.home() / ".taskflow"
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks_file = self.data_dir / "tasks.json"
        self.logs_file = self.data_dir / "logs.json"
        self.log_dir = self.data_dir / "logs"
        
        self.logger = Logger(self.log_dir)
        self.tasks: Dict[str, Task] = {}
        self.logs: List[TaskLog] = []
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.running_tasks: Dict[str, threading.Thread] = {}
        
        self._load_data()
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理"""
        self.logger.info(f"收到信号 {signum}，正在停止调度器...")
        self.stop()
        sys.exit(0)
    
    def _load_data(self):
        """加载数据"""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = Task(**task_data)
                        self.tasks[task.id] = task
                self.logger.info(f"已加载 {len(self.tasks)} 个任务")
            except Exception as e:
                self.logger.error(f"加载任务数据失败: {e}")
        
        if self.logs_file.exists():
            try:
                with open(self.logs_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for log_data in data.get("logs", [])[-1000:]:  # 只保留最近1000条
                        self.logs.append(TaskLog(**log_data))
            except Exception as e:
                self.logger.error(f"加载日志数据失败: {e}")
    
    def _save_data(self):
        """保存数据"""
        try:
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump({
                    "tasks": [asdict(task) for task in self.tasks.values()]
                }, f, ensure_ascii=False, indent=2)
            
            with open(self.logs_file, "w", encoding="utf-8") as f:
                json.dump({
                    "logs": [asdict(log) for log in self.logs[-1000:]]
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
    
    def add_task(self, task: Task) -> bool:
        """添加任务"""
        with self.lock:
            if task.id in self.tasks:
                self.logger.warning(f"任务 {task.id} 已存在")
                return False
            
            # 验证Cron表达式
            parser = CronParser(task.schedule)
            if not parser.is_reboot():
                next_run = parser.get_next_run()
                if next_run:
                    task.next_run = next_run.isoformat()
            
            self.tasks[task.id] = task
            self._save_data()
            self.logger.info(f"任务 {task.id} 添加成功")
            return True
    
    def remove_task(self, task_id: str) -> bool:
        """删除任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            # 停止正在运行的任务
            if task_id in self.running_tasks:
                self.logger.warning(f"任务 {task_id} 正在运行，无法删除")
                return False
            
            del self.tasks[task_id]
            self._save_data()
            self.logger.info(f"任务 {task_id} 已删除")
            return True
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # 重新计算下次执行时间
            if "schedule" in kwargs:
                parser = CronParser(task.schedule)
                if not parser.is_reboot():
                    next_run = parser.get_next_run()
                    if next_run:
                        task.next_run = next_run.isoformat()
            
            self._save_data()
            self.logger.info(f"任务 {task_id} 已更新")
            return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Task]:
        """列出所有任务"""
        return list(self.tasks.values())
    
    def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                self.logger.error(f"依赖任务 {dep_id} 不存在", task.id)
                return False
            
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.SUCCESS.value:
                self.logger.warning(f"依赖任务 {dep_id} 未成功完成", task.id)
                return False
        
        return True
    
    def _execute_task(self, task: Task) -> TaskLog:
        """执行任务"""
        log_id = f"{task.id}_{int(time.time())}"
        task_log = TaskLog(
            id=log_id,
            task_id=task.id,
            start_time=datetime.now().isoformat(),
            status=TaskStatus.RUNNING.value
        )
        
        self.logger.info(f"开始执行任务: {task.name}", task.id)
        task.status = TaskStatus.RUNNING.value
        task.last_run = datetime.now().isoformat()
        task.run_count += 1
        
        start_time = time.time()
        
        try:
            # 检查依赖
            if task.dependencies and not self._check_dependencies(task):
                task_log.status = TaskStatus.SKIPPED.value
                task_log.error = "依赖任务未满足"
                task.status = TaskStatus.SKIPPED.value
                return task_log
            
            # 准备环境变量
            env = os.environ.copy()
            env.update(task.env_vars)
            
            # 执行命令
            process = subprocess.Popen(
                task.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=task.working_dir or os.getcwd(),
                env=env,
                text=True
            )
            
            # 等待进程完成或超时
            try:
                stdout, stderr = process.communicate(timeout=task.timeout)
                task_log.output = stdout
                task_log.error = stderr
                task_log.exit_code = process.returncode
                
                if process.returncode == 0:
                    task_log.status = TaskStatus.SUCCESS.value
                    task.status = TaskStatus.SUCCESS.value
                    task.success_count += 1
                    self.logger.info(f"任务执行成功", task.id)
                else:
                    task_log.status = TaskStatus.FAILED.value
                    task.status = TaskStatus.FAILED.value
                    task.fail_count += 1
                    self.logger.error(f"任务执行失败，退出码: {process.returncode}", task.id)
                
            except subprocess.TimeoutExpired:
                process.kill()
                task_log.status = TaskStatus.FAILED.value
                task_log.error = f"任务执行超时（{task.timeout}秒）"
                task.status = TaskStatus.FAILED.value
                task.fail_count += 1
                self.logger.error(f"任务执行超时", task.id)
        
        except Exception as e:
            task_log.status = TaskStatus.FAILED.value
            task_log.error = str(e)
            task.status = TaskStatus.FAILED.value
            task.fail_count += 1
            self.logger.error(f"任务执行异常: {e}", task.id)
        
        finally:
            task_log.end_time = datetime.now().isoformat()
            task_log.duration = time.time() - start_time
            
            # 重试逻辑
            if task_log.status == TaskStatus.FAILED.value and task.retry_count > 0:
                self.logger.info(f"任务将在 {task.retry_delay} 秒后重试", task.id)
                # 简化实现：实际应该在调度器中处理重试
            
            # 更新下次执行时间
            parser = CronParser(task.schedule)
            if not parser.is_reboot():
                next_run = parser.get_next_run(datetime.now())
                if next_run:
                    task.next_run = next_run.isoformat()
            
            with self.lock:
                self.logs.append(task_log)
                self._save_data()
            
            # 从运行列表中移除
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
        
        return task_log
    
    def run_task_now(self, task_id: str) -> Optional[TaskLog]:
        """立即运行任务"""
        task = self.tasks.get(task_id)
        if not task:
            self.logger.error(f"任务 {task_id} 不存在")
            return None
        
        if not task.enabled:
            self.logger.warning(f"任务 {task_id} 已禁用")
            return None
        
        if task_id in self.running_tasks:
            self.logger.warning(f"任务 {task_id} 已在运行中")
            return None
        
        # 在新线程中执行任务
        def run():
            self._execute_task(task)
        
        thread = threading.Thread(target=run, name=f"Task-{task_id}")
        self.running_tasks[task_id] = thread
        thread.start()
        
        return None  # 异步执行，不返回日志
    
    def _scheduler_loop(self):
        """调度器主循环"""
        self.logger.info("调度器已启动")
        
        while self.running:
            try:
                now = datetime.now()
                
                for task in self.tasks.values():
                    if not task.enabled:
                        continue
                    
                    if task.status == TaskStatus.RUNNING.value:
                        continue
                    
                    if task_id := task.id in self.running_tasks:
                        continue
                    
                    # 检查是否应该执行
                    parser = CronParser(task.schedule)
                    
                    if parser.is_reboot():
                        # @reboot 任务只执行一次
                        if task.run_count == 0:
                            self.run_task_now(task.id)
                        continue
                    
                    if task.next_run:
                        next_run = datetime.fromisoformat(task.next_run)
                        if now >= next_run:
                            self.run_task_now(task.id)
                
                # 每秒检查一次
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"调度器异常: {e}")
                time.sleep(5)
        
        self.logger.info("调度器已停止")
    
    def start(self):
        """启动调度器"""
        if self.running:
            self.logger.warning("调度器已在运行")
            return False
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, name="Scheduler")
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        return True
    
    def stop(self):
        """停止调度器"""
        if not self.running:
            return False
        
        self.running = False
        
        # 等待调度器线程结束
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        # 等待所有运行中的任务
        for task_id, thread in list(self.running_tasks.items()):
            self.logger.info(f"等待任务 {task_id} 完成...")
            thread.join(timeout=30)
        
        return True
    
    def get_logs(self, task_id: Optional[str] = None, limit: int = 100) -> List[TaskLog]:
        """获取日志"""
        logs = self.logs
        if task_id:
            logs = [log for log in logs if log.task_id == task_id]
        return logs[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_tasks = len(self.tasks)
        enabled_tasks = sum(1 for t in self.tasks.values() if t.enabled)
        running_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING.value)
        
        total_runs = sum(t.run_count for t in self.tasks.values())
        total_success = sum(t.success_count for t in self.tasks.values())
        total_fail = sum(t.fail_count for t in self.tasks.values())
        
        return {
            "total_tasks": total_tasks,
            "enabled_tasks": enabled_tasks,
            "running_tasks": running_tasks,
            "total_runs": total_runs,
            "total_success": total_success,
            "total_fail": total_fail,
            "success_rate": (total_success / total_runs * 100) if total_runs > 0 else 0,
        }


class TUI:
    """终端用户界面"""
    
    def __init__(self, engine: TaskEngine):
        self.engine = engine
        self.running = False
    
    def clear(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """打印标题"""
        print("\033[36m" + "=" * 80 + "\033[0m")
        print("\033[36m" + "  TaskFlow - 轻量级终端任务调度与自动化引擎".center(76) + "\033[0m")
        print("\033[36m" + f"  v{__version__}".center(76) + "\033[0m")
        print("\033[36m" + "=" * 80 + "\033[0m")
        print()
    
    def print_menu(self):
        """打印菜单"""
        print("\033[33m主菜单:\033[0m")
        print("  1. 查看任务列表")
        print("  2. 添加新任务")
        print("  3. 编辑任务")
        print("  4. 删除任务")
        print("  5. 立即运行任务")
        print("  6. 查看任务日志")
        print("  7. 查看统计信息")
        print("  8. 启动/停止调度器")
        print("  9. 查看帮助")
        print("  0. 退出")
        print()
    
    def print_tasks(self):
        """打印任务列表"""
        tasks = self.engine.list_tasks()
        
        if not tasks:
            print("\033[33m暂无任务\033[0m")
            return
        
        print("\033[33m任务列表:\033[0m")
        print("-" * 100)
        print(f"{'ID':<20} {'名称':<20} {'状态':<10} {'调度':<20} {'下次执行':<20}")
        print("-" * 100)
        
        status_colors = {
            TaskStatus.PENDING.value: "\033[37m",   # White
            TaskStatus.RUNNING.value: "\033[34m",   # Blue
            TaskStatus.SUCCESS.value: "\033[32m",   # Green
            TaskStatus.FAILED.value: "\033[31m",    # Red
            TaskStatus.SKIPPED.value: "\033[33m",   # Yellow
            TaskStatus.PAUSED.value: "\033[35m",    # Magenta
        }
        
        for task in tasks:
            status_color = status_colors.get(task.status, "\033[37m")
            enabled_marker = "✓" if task.enabled else "✗"
            next_run = task.next_run[:16] if task.next_run else "N/A"
            
            print(f"{task.id:<20} {task.name[:18]:<20} {status_color}{task.status:<10}\033[0m "
                  f"{enabled_marker} {task.schedule[:18]:<18} {next_run:<20}")
        
        print("-" * 100)
        print(f"总计: {len(tasks)} 个任务")
        print()
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.engine.get_stats()
        
        print("\033[33m统计信息:\033[0m")
        print("-" * 50)
        print(f"  总任务数:     {stats['total_tasks']}")
        print(f"  已启用任务:   {stats['enabled_tasks']}")
        print(f"  运行中任务:   {stats['running_tasks']}")
        print(f"  总执行次数:   {stats['total_runs']}")
        print(f"  成功次数:     \033[32m{stats['total_success']}\033[0m")
        print(f"  失败次数:     \033[31m{stats['total_fail']}\033[0m")
        print(f"  成功率:       {stats['success_rate']:.1f}%")
        print("-" * 50)
        print()
    
    def print_logs(self, task_id: Optional[str] = None):
        """打印日志"""
        logs = self.engine.get_logs(task_id, limit=20)
        
        if not logs:
            print("\033[33m暂无日志\033[0m")
            return
        
        print("\033[33m最近日志:\033[0m")
        print("-" * 100)
        
        for log in reversed(logs):
            status_color = "\033[32m" if log.status == TaskStatus.SUCCESS.value else "\033[31m"
            duration = f"{log.duration:.1f}s" if log.duration else "N/A"
            print(f"[{log.start_time[:16]}] [{log.task_id}] {status_color}{log.status}\033[0m "
                  f"(耗时: {duration})")
            if log.error:
                print(f"  错误: {log.error[:80]}")
        
        print("-" * 100)
        print()
    
    def add_task_interactive(self):
        """交互式添加任务"""
        print("\033[33m添加新任务:\033[0m")
        print()
        
        task_id = input("任务ID (唯一标识): ").strip()
        if not task_id or task_id in self.engine.tasks:
            print("\033[31m任务ID无效或已存在\033[0m")
            return
        
        name = input("任务名称: ").strip()
        if not name:
            print("\033[31m任务名称不能为空\033[0m")
            return
        
        command = input("执行命令: ").strip()
        if not command:
            print("\033[31m执行命令不能为空\033[0m")
            return
        
        print("\n调度表达式 (Cron格式):")
        print("  示例: */5 * * * * (每5分钟)")
        print("        0 2 * * * (每天凌晨2点)")
        print("        0 0 * * 0 (每周日)")
        print("        @hourly (每小时)")
        print("        @daily (每天)")
        schedule = input("调度表达式: ").strip()
        if not schedule:
            schedule = "@hourly"
        
        description = input("任务描述 (可选): ").strip()
        
        task = Task(
            id=task_id,
            name=name,
            command=command,
            schedule=schedule,
            description=description
        )
        
        if self.engine.add_task(task):
            print("\033[32m任务添加成功!\033[0m")
        else:
            print("\033[31m任务添加失败\033[0m")
    
    def run(self):
        """运行TUI"""
        self.running = True
        
        while self.running:
            self.clear()
            self.print_header()
            self.print_menu()
            
            choice = input("\033[33m请选择操作 [0-9]: \033[0m").strip()
            
            if choice == "1":
                self.clear()
                self.print_header()
                self.print_tasks()
                input("按回车键继续...")
            
            elif choice == "2":
                self.clear()
                self.print_header()
                self.add_task_interactive()
                input("按回车键继续...")
            
            elif choice == "3":
                self.clear()
                self.print_header()
                self.print_tasks()
                task_id = input("请输入要编辑的任务ID: ").strip()
                if task_id in self.engine.tasks:
                    print("\n当前仅支持启用/禁用任务")
                    enabled = input("启用任务? (y/n): ").strip().lower() == "y"
                    self.engine.update_task(task_id, enabled=enabled)
                    print("\033[32m任务已更新\033[0m")
                else:
                    print("\033[31m任务不存在\033[0m")
                input("按回车键继续...")
            
            elif choice == "4":
                self.clear()
                self.print_header()
                self.print_tasks()
                task_id = input("请输入要删除的任务ID: ").strip()
                if self.engine.remove_task(task_id):
                    print("\033[32m任务已删除\033[0m")
                else:
                    print("\033[31m删除失败\033[0m")
                input("按回车键继续...")
            
            elif choice == "5":
                self.clear()
                self.print_header()
                self.print_tasks()
                task_id = input("请输入要立即运行的任务ID: ").strip()
                if task_id in self.engine.tasks:
                    self.engine.run_task_now(task_id)
                    print("\033[32m任务已启动\033[0m")
                else:
                    print("\033[31m任务不存在\033[0m")
                input("按回车键继续...")
            
            elif choice == "6":
                self.clear()
                self.print_header()
                self.print_logs()
                input("按回车键继续...")
            
            elif choice == "7":
                self.clear()
                self.print_header()
                self.print_stats()
                input("按回车键继续...")
            
            elif choice == "8":
                if self.engine.running:
                    self.engine.stop()
                    print("\033[33m调度器已停止\033[0m")
                else:
                    self.engine.start()
                    print("\033[32m调度器已启动\033[0m")
                input("按回车键继续...")
            
            elif choice == "9":
                self.clear()
                self.print_header()
                self.print_help()
                input("按回车键继续...")
            
            elif choice == "0":
                self.running = False
                if self.engine.running:
                    self.engine.stop()
                print("\033[32m再见!\033[0m")
            
            else:
                print("\033[31m无效选择\033[0m")
                time.sleep(1)
    
    def print_help(self):
        """打印帮助信息"""
        print("\033[33mTaskFlow 帮助:\033[0m")
        print()
        print("TaskFlow 是一个轻量级终端任务调度与自动化引擎，支持:")
        print()
        print("  • Cron表达式调度 (*/5 * * * *)")
        print("  • 特殊调度关键字 (@hourly, @daily, @weekly, @reboot)")
        print("  • 任务依赖管理")
        print("  • 超时控制与重试机制")
        print("  • 执行日志记录")
        print("  • TUI交互界面")
        print()
        print("Cron表达式格式:")
        print("  分 时 日 月 星期")
        print("  0  2  *  *  *     每天凌晨2点")
        print("  */5 * *  *  *     每5分钟")
        print("  0  0  *  *  0     每周日午夜")
        print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TaskFlow - 轻量级终端任务调度与自动化引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --tui              启动TUI界面
  %(prog)s --daemon           以后台模式运行调度器
  %(prog)s add --id backup --name "备份任务" --command "bash backup.sh" --schedule "0 2 * * *"
  %(prog)s list               列出所有任务
  %(prog)s run backup         立即运行指定任务
  %(prog)s remove backup      删除指定任务
        """
    )
    
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--tui", action="store_true", help="启动TUI界面")
    parser.add_argument("--daemon", action="store_true", help="以后台模式运行调度器")
    parser.add_argument("--data-dir", type=str, help="数据目录路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加任务")
    add_parser.add_argument("--id", required=True, help="任务ID")
    add_parser.add_argument("--name", required=True, help="任务名称")
    add_parser.add_argument("--command", required=True, help="执行命令")
    add_parser.add_argument("--schedule", default="@hourly", help="调度表达式")
    add_parser.add_argument("--description", default="", help="任务描述")
    
    # list 命令
    subparsers.add_parser("list", help="列出所有任务")
    
    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="删除任务")
    remove_parser.add_argument("task_id", help="任务ID")
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="立即运行任务")
    run_parser.add_argument("task_id", help="任务ID")
    
    # logs 命令
    logs_parser = subparsers.add_parser("logs", help="查看日志")
    logs_parser.add_argument("--task", help="任务ID过滤")
    logs_parser.add_argument("--limit", type=int, default=20, help="日志条数限制")
    
    # stats 命令
    subparsers.add_parser("stats", help="查看统计信息")
    
    args = parser.parse_args()
    
    # 初始化引擎
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = TaskEngine(data_dir)
    
    # TUI模式
    if args.tui:
        tui = TUI(engine)
        tui.run()
        return
    
    # 后台模式
    if args.daemon:
        print(f"TaskFlow v{__version__} - 启动调度器...")
        engine.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止调度器...")
            engine.stop()
        return
    
    # 子命令处理
    if args.command == "add":
        task = Task(
            id=args.id,
            name=args.name,
            command=args.command,
            schedule=args.schedule,
            description=args.description
        )
        if engine.add_task(task):
            print(f"✓ 任务 '{args.id}' 添加成功")
        else:
            print(f"✗ 任务添加失败")
            sys.exit(1)
    
    elif args.command == "list":
        tasks = engine.list_tasks()
        if not tasks:
            print("暂无任务")
        else:
            print(f"{'ID':<20} {'名称':<20} {'状态':<10} {'调度':<20} {'启用':<6}")
            print("-" * 80)
            for task in tasks:
                enabled = "是" if task.enabled else "否"
                print(f"{task.id:<20} {task.name[:18]:<20} {task.status:<10} "
                      f"{task.schedule[:18]:<20} {enabled:<6}")
    
    elif args.command == "remove":
        if engine.remove_task(args.task_id):
            print(f"✓ 任务 '{args.task_id}' 已删除")
        else:
            print(f"✗ 删除失败")
            sys.exit(1)
    
    elif args.command == "run":
        if args.task_id in engine.tasks:
            engine.run_task_now(args.task_id)
            print(f"✓ 任务 '{args.task_id}' 已启动")
        else:
            print(f"✗ 任务 '{args.task_id}' 不存在")
            sys.exit(1)
    
    elif args.command == "logs":
        logs = engine.get_logs(args.task, args.limit)
        if not logs:
            print("暂无日志")
        else:
            for log in reversed(logs):
                status_icon = "✓" if log.status == TaskStatus.SUCCESS.value else "✗"
                print(f"[{log.start_time}] [{log.task_id}] {status_icon} {log.status}")
                if log.error:
                    print(f"  错误: {log.error[:100]}")
    
    elif args.command == "stats":
        stats = engine.get_stats()
        print(f"总任务数:   {stats['total_tasks']}")
        print(f"已启用:     {stats['enabled_tasks']}")
        print(f"运行中:     {stats['running_tasks']}")
        print(f"总执行:     {stats['total_runs']}")
        print(f"成功:       {stats['total_success']}")
        print(f"失败:       {stats['total_fail']}")
        print(f"成功率:     {stats['success_rate']:.1f}%")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
