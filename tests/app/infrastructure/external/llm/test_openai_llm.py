#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         : 2026/1/31
# @Author       : Gelin
# @Software     : PyCharm
# @File         : test_openai_llm.py

import pytest
from app.infrastructure.external.llm.openai_llm import OpenAILLM
from app.domain.models.app_config import LLMConfig


class TestOpenAILLM:
    """测试OpenAILLM的invoke方法"""

    @pytest.mark.asyncio
    async def test_invoke(self):
        """测试基本的invoke调用"""
        llm = OpenAILLM(LLMConfig(
            base_url="https://api.deepseek.com",
            api_key="xxx",  # 需要配置真实的API Key
            model_name="deepseek-chat",
        ))

        response = await llm.invoke([{"role": "user", "content": "Hi"}])

        # 验证响应结构
        assert "role" in response
        assert response["role"] == "assistant"
        assert "content" in response
        assert isinstance(response["content"], str)
        assert len(response["content"]) > 0

        print(f"LLM响应: {response}")
