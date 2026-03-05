#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         :   2026/1/31
# @Author       :   Gelin
# @Software     :   PyCharm
# @File         :   openai_llm.py
from typing import List, Dict, Any

import logging

from app.application.errors.exceptions import ServerRequestError
from app.domain.external.llm import  LLM
from app.domain.models.app_config import LLMConfig
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class OpenAILLM(LLM):
    """ 基于OpenAI SDK/兼容OpenAI格式的LLM调用类"""
    def __init__(self, llm_config: LLMConfig,**kwargs) -> None:
        """构造函数，完成异步OpenAI客户端的创建和参数初始化"""

        # 1. 初始化异步客户端
        self._client = AsyncOpenAI(
            base_url=str(llm_config.base_url),
            api_key=llm_config.api_key,
            **kwargs,
        )

        # 2.完成其他参数的存储
        self._model_name = llm_config.model_name
        self._temperature = llm_config.temperature
        self._max_tokens = llm_config.max_tokens
        self._timeout = 3600

    # 实现LLM协议中方法model_name  temperature  max_tokens invoke
    @property
    def model_name(self) -> str:
        return self._model_name
    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    async def invoke(self,
                 messages: List[Dict[str, Any]],
                 tools: List[Dict[str, Any]] = None,
                 response_format:Dict[str,Any] = None,
                 tool_choice:str = None,
                 ) -> Dict[str, Any]:
        """使用异步OpenAI客户端发起响应（该步骤可以切换成流式响应）"""
        try:
            # 1. 检测是否传递了工具列表
            if tools:
                logger.info(f"调用OpenAI客户端向LLM发起请求并携带工具信息: {self._model_name}")
                response = await self._client.chat_completions.create(
                    model =self._model_name,
                    temperature = self._temperature,
                    max_tokens = self._max_tokens,
                    messages = messages,
                    response_format=response_format,
                    tools = tools,
                    tool_choice = tool_choice,
                    parallel_tool_calls=False, # 关闭并行工具调用(deepseek没有这个参数)
                    timeout = self._timeout,
                )
            else:
                # 2. 未传递工具则去掉tools/tool_choice等参数
                logger.info(f"调用OpenAI客户端向LLM发起请求不携带工具信息: {self._model_name}")
                response = await self._client.chat.completions.create(
                    model=self._model_name,
                    temperature = self._temperature,
                    max_tokens = self._max_tokens,
                    messages = messages,
                    response_format=response_format,
                    timeout = self._timeout,
                )
            # 3.处理响应数据并返回
            logger.info(f"OpenAI客户端返回内容： {response.model_dump()}")
            return response.choices[0].message.model_dump()
        except Exception as e:
            logger.error(f"调用OpenAI客户端发生错误: {str(e)}")
            raise ServerRequestError("调用OpenAI客户端向LLM发起请求出错")

