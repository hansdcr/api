#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/28
# @Author   : Gelin
# @File     : status_routes.py

import logging
from typing import List
from fastapi import APIRouter
from fastapi.params import Depends

from app.application.services.status_service import StatusService
from app.interfaces.schemas import Response
from app.domain.models.health_status import HealthStatus
from app.interfaces.service_dependencies import get_status_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status",tags=["状态模块"])


@router.get(
    path="", # 空代表/status
    response_model=Response[List[HealthStatus]],
    summary="系统健康检查",
    description="检查系统postgres redis fastapi等组件的健康信息"
)
async def get_status(
        status_service: StatusService = Depends(get_status_service)
)->Response:
    """ 检查系统postgres redis fastapi等组件的健康信息 """
    # todo: 等待postgres redis cos等接入后补全代码
    status = await status_service.check_all()
    if any(item.status == "error" for item in status):
        return Response.fail(503,"系统存在服务异常",status)
    return Response.success("系统健康检查成功",status)


