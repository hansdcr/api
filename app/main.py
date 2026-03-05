#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/28
# @Author   : Gelin
# @File     : main.py

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from core.config import get_settings
from app.infrastructure.logging import setup_logging
from contextlib import asynccontextmanager
from app.interfaces.endpoints.routes import router
from app.interfaces.errors.exception_handlers import register_exception_handlers
from app.infrastructure.storage.redis import get_redis
from app.infrastructure.storage.postgres import get_postgres
from app.infrastructure.storage.cos import get_cos

# 1、加载配置信息
settings = get_settings()

# 2、初始化日志系统
setup_logging()
logger = logging.getLogger()

# 3、定义FastAPI路由tags标签
openai_tags = [
    {
        "name": "状态模块",
        "description": "包含 **状态检测** 等API接口，用于检测系统的运行状态",
    }
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ 创建FastAPI应用程序生命周期上下文管理器 """
    # 1、打印日志表示程序开始了
    logger.info("App正在初始化....")

    # 2、初始化redis缓存客户端
    redis = get_redis()
    await redis.init()

    # 3、初始化postgres客户端
    postgres = get_postgres()
    await postgres.init()

    # 4、初始化腾讯云cos对象存储客户端
    cos = get_cos()
    await cos.init()

    try:
        #lifespan节点/分界。（yield之前可以放些例如数据库初始化内容，finally中可以放关闭数据库连接内容）
        yield
    finally:
        await redis.shutdown()
        await postgres.shutdown()
        await cos.shutdown()
        logger.info("App正在关闭...")

# 4、创建项目应用实例app
app = FastAPI(
    title = "通用智能体",
    description="通用的AI Agent系统，可以完全私有化部署，使用A2A+MCP连接agent/tools,同时支持沙箱操作",
    lifespan=lifespan,
    openai_tags=openai_tags,
    version="1.0.0",
)

# 5、配置CORS中间件，解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 6、注册错误处理器
register_exception_handlers(app)


# 7、继承路由
app.include_router(router, prefix="/api")