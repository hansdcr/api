from typing import Optional

from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """ 后端中控配置信息，从.env 或者环境变量中加载信息 """

    # 项目基础配置
    env:str = "development"
    log_level:str = "INFO"
    app_config_filepath:str = "config.yaml"

    # 数据库相关配置
    sqlalchemy_database_uri:str = "postgresql+asyncpg://postgres:postgres@localhost:5432/manus"

    # Redis相关配置
    redis_host:str = "localhost"
    redis_port:int = 6379
    redis_db:int = 0
    redis_password:str | None = None

    # COS对象存储相关配置
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_region: str = ""
    cos_scheme: str = "https"
    cos_bucket: str = ""
    cos_domain: str = ""


    # Sandbox配置
    sandbox_address: Optional[str] = None
    sandbox_image: Optional[str] = None
    sandbox_name_prefix: Optional[str] = None
    sandbox_ttl_minutes: Optional[int] = 60
    sandbox_network: Optional[str] = None
    sandbox_chrome_args: Optional[str] = ""
    sandbox_https_proxy: Optional[str] = None
    sandbox_http_proxy: Optional[str] = None
    sandbox_no_proxy: Optional[str] = None

    #使用pydantic v2写法来完成环境变量的告知
    model_config = SettingsConfigDict(
        env_file=".env", #读取.env文件
        env_file_encoding="utf-8", 
        extra="ignore" #如果类中没有声明的字段在env有，那么忽略env中的这个字段配置
    )

@lru_cache()
def get_settings()-> Settings:
    """ 获取当前项目配置信息，并进行缓存，避免重复读取。在整个APP周期Settings只会被读取1次"""
    settings = Settings()
    return settings