#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskFlow 基础使用示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taskflow import TaskEngine, Task, TaskStatus

def main():
    # 创建引擎实例
    engine = TaskEngine()
    
    # 示例1: 添加一个简单的定时任务
    task1 = Task(
        id="hello-world",
        name="Hello World",
        command="echo 'Hello, TaskFlow!'",
        schedule="*/1 * * * *",  # 每分钟执行一次
        description="简单的问候任务"
    )
    engine.add_task(task1)
    print(f"✓ 添加任务: {task1.name}")
    
    # 示例2: 添加一个备份任务
    task2 = Task(
        id="backup-files",
        name="文件备份",
        command="tar -czf backup.tar.gz ~/Documents",
        schedule="0 2 * * *",  # 每天凌晨2点
        description="每日文件备份",
        timeout=3600  # 1小时超时
    )
    engine.add_task(task2)
    print(f"✓ 添加任务: {task2.name}")
    
    # 示例3: 添加一个系统监控任务
    task3 = Task(
        id="system-monitor",
        name="系统监控",
        command="df -h && free -h",
        schedule="@hourly",  # 每小时
        description="监控系统磁盘和内存使用情况"
    )
    engine.add_task(task3)
    print(f"✓ 添加任务: {task3.name}")
    
    # 示例4: 添加一个带依赖的任务
    task4 = Task(
        id="send-report",
        name="发送报告",
        command="python send_email.py",
        schedule="0 9 * * 1",  # 每周一上午9点
        description="发送周报",
        dependencies=["backup-files"]  # 依赖备份任务
    )
    engine.add_task(task4)
    print(f"✓ 添加任务: {task4.name} (依赖: backup-files)")
    
    # 列出所有任务
    print("\n任务列表:")
    print("-" * 80)
    for task in engine.list_tasks():
        print(f"  • {task.name} ({task.id})")
        print(f"    调度: {task.schedule}")
        print(f"    命令: {task.command}")
        print()
    
    # 获取统计信息
    stats = engine.get_stats()
    print("统计信息:")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  已启用: {stats['enabled_tasks']}")
    
    print("\n提示: 使用 'taskflow --tui' 启动交互式界面")

if __name__ == "__main__":
    main()
