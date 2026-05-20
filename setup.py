#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskFlow - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="taskflow-cli",
    version="1.0.0",
    description="轻量级终端任务调度与自动化引擎 | Lightweight Terminal Task Scheduling & Automation Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TaskFlow Team",
    author_email="taskflow@example.com",
    url="https://github.com/gitstq/TaskFlow",
    py_modules=["taskflow"],
    entry_points={
        "console_scripts": [
            "taskflow=taskflow:main",
            "tf=taskflow:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="task scheduler cron automation cli terminal python",
    python_requires=">=3.8",
    license="MIT",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/TaskFlow/issues",
        "Source": "https://github.com/gitstq/TaskFlow",
        "Documentation": "https://github.com/gitstq/TaskFlow#readme",
    },
)
