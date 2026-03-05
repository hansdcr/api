#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/28
# @Author   : Gelin
# @File     : logging.py

import logging
import sys

from core.config import get_settings


def setup_logging():
    """配置项目的日志系统，包括日志等级，输出格式，输出渠道等 """
    # 1、读取配置文件，获取日志配置
    settings = get_settings()

    # 2、获取根日志处理器
    root_logger = logging.getLogger()

    # 3、设置根日志处理器等级
    log_level = getattr(logging, settings.log_level)
    root_logger.setLevel(log_level)

    # 4、日志输出格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 5、创建控制台日志输出处理器，将日志输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)  # 设置控制器使用的日志格式
    console_handler.setLevel(log_level) # 设置控制器使用的日志级别（这里保持和根处理器的格式一样）

    # 6、将控制台处理器添加到根处理器中
    root_logger.addHandler(console_handler)


    root_logger.info("日志系统初始化完成")
    