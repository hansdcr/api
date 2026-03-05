#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         :   2026/2/8
# @Author       :   Gelin
# @Software     :   PyCharm
# @File         :   search.py

from typing import Protocol, Optional

from app.domain.models.search import SearchResults
from app.domain.models.tool_result import ToolResult


class SearchEngine(Protocol):
    """搜索引擎API接口协议"""

    async def invoke(self, query: str, date_range:Optional[str] =None) -> ToolResult[SearchResults]:
        """根据传递的query+date_range(时间筛选)调用搜索引擎获取工具"""
        ...

