#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/29
# @Author   : Gelin
# @File     : base.py

from sqlalchemy.orm import declarative_base



# 定义基础ORM类，让所有模型都继承这个类
Base = declarative_base()

