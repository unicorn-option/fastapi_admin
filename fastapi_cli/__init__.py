"""
FastAPI Project Scaffold CLI Tool

一个用于快速创建 FastAPI 项目脚手架的命令行工具。
"""

__version__ = "0.1.0"
__author__ = "unicorn"
__email__ = "unicorn_0618@foxmail.com"

from .cli import ProjectCreator, main

__all__ = (
    'ProjectCreator',
    'main',
)