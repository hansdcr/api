#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         :   2026/2/7
# @Author       :   Gelin
# @Software     :   PyCharm
# @File         :   search.py
from typing import Optional,List

from pydantic import BaseModel,Field

class SearchResultItem(BaseModel):
    """搜索结果条目数据类型"""
    url: str # 搜索条目url链接
    title: str # 搜索条目标题
    snippet: str = "" # 搜索条目摘要信息


class SearchResults(BaseModel):
    """搜索结果数据类型"""
    query: str # 查询query
    date_range: Optional[str] = None # 日期筛选外围
    total_results: int = 0 # 搜索结果条数 (输入一个关键词后，总共有多少条相关结果)
    results: List[SearchResultItem] = Field(default_factory=list) # 搜索结果