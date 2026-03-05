#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/30
# @Author   : Gelin
# @File     : demo.py

import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import (
    text,
    UUID,
    PrimaryKeyConstraint,
    String,
    Text,
    DateTime,
)

from .base import Base


logger = logging.getLogger(__name__)


class Demo(Base):
    """ Demo模型，用于演示alembic数据库迁移 """
    __tablename__ = "demos" # 在数据库中的表名
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_demos_id"), # 使用id做主键，键的名字pk_demos_id
    )

    """ 
    id: Mapped[uuid.UUID]: 在python类中id的类型： 这里是类型是UUID
        mapped_column(
        UUID, #这里表示在数据库中id字段的类型，这里是UUID
        nullable=False,  #是否允许为空，不允许
        primary_key=True, # 是否是主键： 是
        server_default=text("uuid_generate_v4()") # 如果没有值，使用uuid_generate_v4()这个函数生成uuid
        )
    """
    id: Mapped[uuid.UUID] = mapped_column(
        UUID,nullable=False,
        primary_key=True,
        server_default=text("uuid_generate_v4()")
        )

    """
    mapped_column(
        String(255),  # 在数据库中的类型是String长度是255
        nullable=False, # 不允许为空
        server_default=text("''::character varying") # 默认值是空字符串，character varying字符串是可变长度的
    )
    """
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        server_default=text("''::character varying")
    )

    """
    mapped_column(
        Text,  #在数据库中类型是Text
        nullable=False, # 不允许空
        server_default=text("''::text") # 默认值空，类型是text
    """
    description: Mapped[str] = mapped_column(Text, nullable=False,server_default=text("''::text"))

    """
    mapped_column(
        DateTime, #数据库类型是DateTime
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"), #默认时间是当前时间戳
        onupdate=datetime.now # 如果没有设置，使用系统当前时间进行设置
    )
    """
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        onupdate=datetime.now
    ) # 更新时间

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        onupdate=datetime.now
    ) # 创建时间
    
