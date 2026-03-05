#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/28
# @Author   : Gelin
# @File     : base.py

from typing import TypeVar, Generic, Optional
from pydantic import BaseModel,Field

# 定义一个泛型类
T = TypeVar('T')

class Response(BaseModel,Generic[T]):
    """ 基础API响应结构，继承BaseModel类，并使用TypeVar定义一个泛型类型T"""
    code:int = 200 # 业务状态码，和http状态码一致
    msg:str = "success" # 响应消息提示
    data:Optional[T] = Field(default_factory=dict) # 响应数据，默认值为空字典

    @staticmethod
    def success(msg:str="success",data:Optional[T]=None) -> "Response[T]":
        """ 成功消息，code固定为200，msg默认success """
        return Response(code=200,msg=msg,data=data if data else {})
    
    @staticmethod
    def fail(code:int,msg:str,data:Optional[T]=None) -> "Response[T]":
        """ 失败消息提示"""
        return Response(code=code,msg=msg,data=data if data else {})
    
    