#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2026/01/30
# @Author   : Gelin
# @File     : conftest.py

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """ 
    创建一个可供所有测试用例使用的TestClient客户端 
    scope="session" 表示这个fixture在整个测试用例只会实例一次，这样可以提高效率
    """
    with TestClient(app) as c:
        yield c
    
