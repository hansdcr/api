#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/31
# @Author   : Gelin
# @File     : app_config.py

import logging
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl, Field,model_validator
from typing import Dict, Optional, Any,List

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """ 语言模型配置 """
    base_url: HttpUrl = "https://api.deepseek.com"  # 基础URL地址
    api_key: str = ""  # API密钥
    model_name: str = "deepseek-reasoner"  # 推理模型如果传递了tools底层会自动切换deepseek-chat
    temperature: float = Field(default=0.7)  # 温度
    max_tokens: int = Field(8192, ge=0)  # 最大输出token数, 值要大于等于0

class AgentConfig(BaseModel):
    """Agent通用配置"""
    max_iterations: int = Field(default=100,gt=0,lt=1000) #最大迭代次数
    max_retries: int = Field(default=3,gt=1,lt=10) # LLM/工具的最大重试次数
    max_search_results: int = Field(default=10,gt=1,lt=30) #最大搜索结果返回数据条目


class MCPTransport(str, Enum):
    """MCP传输类型枚举"""
    STDIO = "stdio" #本地输入输出
    SSE = "sse" # 流式事件类型
    STREAMABLE_HTTP = "streamable_http" # 可流式HTTP


class MCPServerConfig(BaseModel):
    """MCP单条服务配置"""
    # 通用字段配置
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP # 传输协议
    enabled: bool = True # 是否开启
    description: Optional[str] = None #MCP的描述
    env: Optional[Dict[str,Any]] = None #环境变量

    # stdio配置
    command: Optional[str] = None #启动命令
    args: Optional[List[str]] = None #名命令参数

    #streamable_http和sse配置
    url: Optional[str] = None #MCP服务器url地址
    headers: Optional[Dict[str, Any]] = None #headers请求头

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_mcp_server_config(self):
        """校验mcp_server_config的相关信息，包含url+command"""
        # 1. 判断tansport是否为sse/streamable_http
        if self.transport in [MCPTransport.SSE, MCPTransport.STREAMABLE_HTTP]:
            # 2. 这两种传输方式需要判断url是否传递
            if not self.url:
                raise ValueError("在sse或streamable_http传输协议模式下必须传递url")

        # 3. 判断transport 是否是stdio类型
        if self.transport == MCPTransport.STDIO:
            # 4. 判断 command 也就是启动命令是否传递
            if not self.command:
                raise ValueError("在stdio模式下必须传递command")
        return self

class MCPConfig(BaseModel):
    """应用MCP配置"""
    mcpServers: Dict[str,MCPServerConfig] = Field(default_factory=dict) # mcp服务
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True) # 允许额外的属性被定义


class AppConfig(BaseModel):
    """ 应用配置信息，包含Agent配置、LLM提供商、A2A网络、MCP服务配置等"""
    llm_config: LLMConfig  # 语言模型配置
    agent_config: AgentConfig # agent通用配置
    mcp_config: MCPConfig

    # Pydantic配置，允许传递额外字段初始化
    model_config = ConfigDict(extra="allow")
