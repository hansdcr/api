#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/31
# @Author   : Gelin
# @File     : app_config_service.py

import logging
from typing import List

from app.domain.models.app_config import AppConfig, LLMConfig, AgentConfig, MCPConfig
from app.domain.repositories.app_config_repository import AppConfigRepository
from app.application.errors.exceptions import NotFoundError
from app.domain.services.tools.base import tool
from app.domain.services.tools.mcp import MCPClientManager
from app.interfaces.schemas.app_config import ListMCPServerItem

logger = logging.getLogger(__name__)


class AppConfigService:
    """ 应用配置服务 """
    def __init__(self,app_config_respository: AppConfigRepository) -> None:
        """构造函数，完成应用配置服务的初始化 """
        self.app_config_respository = app_config_respository
    
    async def _load_app_config(self) -> AppConfig:
        """加载获取所有的应用配置"""
        return self.app_config_respository.load()

    async def get_llm_config(self) -> LLMConfig:
        """加载获取LLM提供商配置"""
        app_config = await self._load_app_config()
        return app_config.llm_config
    
    async def update_llm_config(self,llm_config:LLMConfig) -> LLMConfig:
        """根据传递的llm_config更新语言模型提供商配置"""
        # 1、获取应用配置
        app_config = await self._load_app_config()
        # 2、判断api_key是否为空
        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key
        # 3、调用函数更新app_config
        app_config.llm_config = llm_config
        self.app_config_respository.save(app_config)
    
        return app_config.llm_config




    async def get_agent_config(self) -> AgentConfig:
        """加载获取agent配置"""
        app_config = await self._load_app_config()
        return app_config.agent_config

    async def update_agent_config(self, agent_config: AgentConfig) -> AgentConfig:
        """根据传递的agent_config更新配置"""
        # 1、获取应用配置
        app_config = await self._load_app_config()
        # 2.
        app_config.agent_config = agent_config
        self.app_config_respository.save(app_config)

        return app_config.agent_config


    async def get_mcp_servers(self) -> List[ListMCPServerItem]:
        """获取MCP服务器列表"""
        #1.获取的当前应用配置
        app_config = await self._load_app_config()
        #2.创建mcp客户端管理器，对配置信息不进行过滤
        mcp_servers = []
        mcp_client_manager = MCPClientManager(mcp_config=app_config.mcp_config)
        try:
            #3.初始化mcp客户端管理器
            await mcp_client_manager.initialize()
            #4.获取mcp客户端管理器的工具列表
            tools = mcp_client_manager.tools
            #5.循环组装响应的工具格式
            for server_name,server_config in app_config.mcp_config.mcpServers.items():
                mcp_servers.append(ListMCPServerItem(
                    server_name=server_name,
                    enabled=server_config.enabled,
                    transport=server_config.transport,
                    tools=[tool.name for tool in tools.get(server_name,[])]
                ))
        except Exception as e:
            pass
        finally:
            #6.清除MCP管理器客户端的相关资源
            await mcp_client_manager.cleanup()
        return mcp_servers

    async def update_and_create_mcp_servers(self,mcp_config: MCPConfig) -> MCPConfig:
        """根据传递的数据新增或更新MCP配置"""
        #1.获取应用配置
        app_config = await self._load_app_config()
        #2.使用新的mcp_config更新原始的配置
        app_config.mcp_config.mcpServers.update(mcp_config.mcpServers)
        #3.调用数据仓库完成存储or更新
        self.app_config_respository.save(app_config)
        return app_config.mcp_config

    async def delete_mcp_servers(self,server_name:str) -> MCPConfig:
        """根据服务名字删除mcp服务"""
        #1.获取应用配置
        app_config = await self._load_app_config()
        #2.查询对应服务的名字是否存在
        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"该MCP服务[{server_name}]不存在，请核实后重试")
        #3.如果存在则删除字典中对应的服务
        del app_config.mcp_config.mcpServers[server_name]
        self.app_config_respository.save(app_config)
        return app_config.mcp_config

    async def set_mcp_server_enabled(self,server_name:str,enabled: bool) -> MCPConfig:
        """更新mcp服务的启用状态"""
        #1. 获取应用配置
        app_config = await self._load_app_config()
        #2.查询对应的服务名字是否存在
        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"该MCP服务[{server_name}]不存在，请核实后重试")
        #3.如果存在则变更mcp服务状态
        app_config.mcp_config.mcpServers[server_name].enabled = enabled
        self.app_config_respository.save(app_config)
        return app_config.mcp_config

