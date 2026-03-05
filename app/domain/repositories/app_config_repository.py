#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/31
# @Author   : Gelin
# @File     : app_config_repository.py

import logging
from typing import Protocol,Optional
from app.domain.models.app_config import AppConfig


logger = logging.getLogger(__name__)


class AppConfigRepository(Protocol):
    """ 应用配置仓库 """
    def load(self) -> Optional[AppConfig]:
        """ 加载获取应用配置 """
        ...
    
    def save(self,app_config:AppConfig) -> None:
        """ 存储更新的应用配置 """
        ...
    
