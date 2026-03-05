#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         :   2026/2/1
# @Author       :   Gelin
# @Software     :   PyCharm
# @File         :   redis_health_checker.py.py

import logging
from app.domain.external.health_checker import HealthChecker
from app.domain.models.health_status import HealthStatus
from app.infrastructure.storage.redis import RedisClient


logger = logging.getLogger(__name__)

class RedisHealthChecker(HealthChecker):
    """Redis健康检查器"""
    def __init__(self, redis_client: RedisClient) -> None:
        self._redis_client = redis_client

    async def check(self) -> HealthStatus:
        try:
            # TODO: 这里有一个bug, pfdd在redis中写入一个key后，redis重启，此时pingtest在redis已经存在，不能再写入
            #       此时健康检查会报错redis ping失败，进而判断健康检查失败
            if self._redis_client.client.pfadd(name="pingtest"):
                return HealthStatus(service="redis",status="ok")
            else:
                return HealthStatus(service="redis",status="error",details="redis服务ping失败")
        except Exception as e:
            logger.error(f"redis健康检查失败: {str(e)}")
            return HealthStatus(
                service="redis",
                status="error",
                details=str(e),
            )