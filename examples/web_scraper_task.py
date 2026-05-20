#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskFlow Web爬虫定时任务示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taskflow import TaskEngine, Task

def main():
    engine = TaskEngine()
    
    # 爬虫任务 - 每小时抓取一次数据
    scraper_task = Task(
        id="web-scraper",
        name="网站数据抓取",
        command="python -c \"import urllib.request; print('Fetching data...')\"",
        schedule="0 * * * *",  # 每小时执行
        description="定时抓取网站数据",
        timeout=300,  # 5分钟超时
        retry_count=3,  # 失败重试3次
        retry_delay=300  # 5分钟后重试
    )
    engine.add_task(scraper_task)
    print(f"✓ 添加爬虫任务: {scraper_task.name}")
    
    # 数据清理任务 - 每天清理一次
    cleanup_task = Task(
        id="cleanup-old-data",
        name="清理旧数据",
        command="find /tmp/scraper_data -mtime +7 -delete",
        schedule="0 3 * * *",  # 每天凌晨3点
        description="清理7天前的旧数据",
        dependencies=["web-scraper"]  # 确保爬虫任务完成后才清理
    )
    engine.add_task(cleanup_task)
    print(f"✓ 添加清理任务: {cleanup_task.name}")
    
    # 报告生成任务 - 每天早上发送报告
    report_task = Task(
        id="daily-report",
        name="生成日报",
        command="python generate_report.py",
        schedule="0 8 * * *",  # 每天早上8点
        description="生成并发送数据报告",
        dependencies=["web-scraper"]
    )
    engine.add_task(report_task)
    print(f"✓ 添加报告任务: {report_task.name}")
    
    print("\nWeb爬虫任务链已创建:")
    print("  web-scraper → cleanup-old-data")
    print("  web-scraper → daily-report")

if __name__ == "__main__":
    main()
