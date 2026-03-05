#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         :   2026/2/5
# @Author       :   Gelin
# @Software     :   PyCharm
# @File         :   message.py

from pydantic import BaseModel,Field
from typing import Any, Dict, Optional,List

class Message(BaseModel):
    """用户传递的消息"""
    message:str = "" # 用户发送的消息
    attachments:List[str] = Field(default_factory=list) #用户发送的附件
