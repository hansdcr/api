#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/30
# @Author   : Gelin
# @File     : cos.py

import logging
from typing import Optional
from functools import lru_cache

from qcloud_cos import CosS3Client,CosConfig

from core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Cos:
    """ 腾讯云cos对象存储 """
    def __init__(self):
        """ 构造函数，完成配置获取+Cos客户端初始化赋值 """
        self._settings: Settings = get_settings()
        self._client: Optional[CosS3Client] = None

    async def init(self) -> None:
        """ 完成cos腾讯云对象存储客户端的创建 """
        if self._client is not None:
            logger.warning("Cos腾讯云对象存储已经初始化，无需重复操作")
            return
        try:
            config = CosConfig(
                Region=self._settings.cos_region,
                SecretId=self._settings.cos_secret_id,
                SecretKey=self._settings.cos_secret_key,
                Token=None,
                Scheme=self._settings.cos_scheme,
            )
            self._client = CosS3Client(config)
            logger.info("Cos腾讯云对象存储初始化成功")
        except Exception as e:
            logger.error(f"Cos腾讯云对象存储初始化失败: {str(e)}")
            raise


    async def shutdown(self) -> None:
        """ 关闭cos腾讯对象存储 """
        if self._client is not None:
            self._client = None
            logger.info("关闭Cos腾讯对象存储成功")
        get_cos.cache_clear()

    @property
    def client(self) -> CosS3Client:
        """ 只读属性,返回Cos腾讯云对象存储客户端 """
        if self._client is None:
            raise RuntimeError("Cos腾讯云对象存储客户端未初始化")
        return self._client

@lru_cache()
def get_cos() -> Cos:
    """ 使用单例模式获取腾讯云cos对象存储客户端"""
    return Cos()