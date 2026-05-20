#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskFlow 备份自动化示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taskflow import TaskEngine, Task

def main():
    engine = TaskEngine()
    
    # 数据库备份
    db_backup = Task(
        id="db-backup",
        name="数据库备份",
        command="mysqldump -u root -p mydb > backup/db_$(date +%Y%m%d).sql",
        schedule="0 1 * * *",  # 每天凌晨1点
        description="备份MySQL数据库",
        timeout=1800  # 30分钟超时
    )
    engine.add_task(db_backup)
    print(f"✓ 添加任务: {db_backup.name}")
    
    # 文件备份
    files_backup = Task(
        id="files-backup",
        name="文件备份",
        command="tar -czf backup/files_$(date +%Y%m%d).tar.gz /var/www/html",
        schedule="0 2 * * *",  # 每天凌晨2点
        description="备份网站文件",
        timeout=3600  # 1小时超时
    )
    engine.add_task(files_backup)
    print(f"✓ 添加任务: {files_backup.name}")
    
    # 上传到远程存储
    upload_backup = Task(
        id="upload-backup",
        name="上传备份到云存储",
        command="rclone copy backup remote:backups/",
        schedule="0 3 * * *",  # 每天凌晨3点
        description="上传备份到云存储",
        dependencies=["db-backup", "files-backup"],  # 等待两个备份完成
        timeout=7200  # 2小时超时
    )
    engine.add_task(upload_backup)
    print(f"✓ 添加任务: {upload_backup.name}")
    
    # 清理本地旧备份
    cleanup_local = Task(
        id="cleanup-local",
        name="清理本地旧备份",
        command="find backup -name '*.sql' -mtime +7 -delete && find backup -name '*.tar.gz' -mtime +7 -delete",
        schedule="0 4 * * 0",  # 每周日凌晨4点
        description="清理7天前的本地备份",
        dependencies=["upload-backup"]  # 确保上传完成后再清理
    )
    engine.add_task(cleanup_local)
    print(f"✓ 添加任务: {cleanup_local.name}")
    
    # 备份验证
    verify_backup = Task(
        id="verify-backup",
        name="备份完整性验证",
        command="python verify_backup.py",
        schedule="0 5 * * *",  # 每天凌晨5点
        description="验证备份文件完整性",
        dependencies=["upload-backup"]
    )
    engine.add_task(verify_backup)
    print(f"✓ 添加任务: {verify_backup.name}")
    
    print("\n备份自动化任务链已创建:")
    print("  01:00 db-backup ──┐")
    print("  02:00 files-backup ┘")
    print("           ↓")
    print("  03:00 upload-backup")
    print("           ↓")
    print("  04:00 cleanup-local (周日)")
    print("  05:00 verify-backup")

if __name__ == "__main__":
    main()
