#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         :   2026/2/13
# @Author       :   Gelin
# @Software     :   PyCharm
# @File         :   app_config.py


from pydantic import BaseModel,Field
from typing import List

from app.domain.models.app_config import MCPTransport


class ListMCPServerItem(BaseModel):
    """MCP服务列表条目选项"""
    server_name: str = "" #服务名字
    enabled: bool = True #启用状态
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP # 传输协议
    tools: List[str] = Field(default_factory=list) #工具名字列表


class ListMCPServerResponse(BaseModel):
    """获取MCP服务列表响应结构"""
    mcp_servers: List[ListMCPServerItem] = Field(default_factory=list) #MCP服务列表
