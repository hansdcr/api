# 配置文件读取和更新的类调用关系图

## 📊 整体架构调用关系

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Interface Layer (接口层)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼────────┐              ┌──────▼──────┐
            │  GET /llm      │              │ POST /llm   │
            │ get_llm_config │              │update_llm   │
            └───────┬────────┘              └──────┬──────┘
                    │                               │
                    │  Depends(get_app_config_service)
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │    dependencies.py             │
                    │  get_app_config_service()      │
                    │  @lru_cache() - 单例模式       │
                    └───────────────┬────────────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
        ┌───────────▼──────────┐      ┌────────────▼─────────────┐
        │  core/config.py      │      │ FileAppConfigRepository  │
        │  get_settings()      │      │ (Infrastructure Layer)   │
        │  @lru_cache()        │      └────────────┬─────────────┘
        │  ├─ env              │                   │
        │  ├─ log_level        │                   │
        │  └─ app_config_      │                   │
        │     filepath         │                   │
        └──────────────────────┘                   │
                                                   │
┌──────────────────────────────────────────────────┼─────────────────────┐
│                    Application Layer (应用层)     │                     │
└──────────────────────────────────────────────────┼─────────────────────┘
                                                   │
                            ┌──────────────────────▼──────────────────────┐
                            │      AppConfigService                       │
                            │  ┌────────────────────────────────────────┐ │
                            │  │ __init__(app_config_repository)        │ │
                            │  └────────────────────────────────────────┘ │
                            │                                             │
                            │  ┌────────────────────────────────────────┐ │
                            │  │ _load_app_config()                     │ │
                            │  │   └─> repository.load()                │ │
                            │  └────────────────────────────────────────┘ │
                            │                                             │
                            │  ┌────────────────────────────────────────┐ │
                            │  │ get_llm_config()                       │ │
                            │  │   └─> _load_app_config().llm_config   │ │
                            │  └────────────────────────────────────────┘ │
                            │                                             │
                            │  ┌────────────────────────────────────────┐ │
                            │  │ update_llm_config(llm_config)          │ │
                            │  │   1. app_config = _load_app_config()   │ │
                            │  │   2. 检查api_key是否为空               │ │
                            │  │   3. app_config.llm_config = new       │ │
                            │  │   4. repository.save(app_config)       │ │
                            │  └────────────────────────────────────────┘ │
                            └─────────────────┬───────────────────────────┘
                                              │
                                              │ 依赖注入
                                              │
┌─────────────────────────────────────────────┼───────────────────────────┐
│                    Domain Layer (领域层)     │                           │
└─────────────────────────────────────────────┼───────────────────────────┘
                                              │
                    ┌─────────────────────────▼─────────────────────────┐
                    │   AppConfigRepository (Protocol)                  │
                    │   ┌─────────────────────────────────────────────┐ │
                    │   │ load() -> Optional[AppConfig]               │ │
                    │   │ save(app_config: AppConfig) -> None         │ │
                    │   └─────────────────────────────────────────────┘ │
                    └───────────────────────────────────────────────────┘
                                              │
                                              │ 实现协议
                                              │
┌─────────────────────────────────────────────┼───────────────────────────┐
│              Infrastructure Layer (基础设施层)│                           │
└─────────────────────────────────────────────┼───────────────────────────┘
                                              │
                    ┌─────────────────────────▼─────────────────────────┐
                    │   FileAppConfigRepository                         │
                    │   implements AppConfigRepository                  │
                    │                                                   │
                    │   ┌─────────────────────────────────────────────┐ │
                    │   │ __init__(config_path: str)                  │ │
                    │   │   - self._config_path = Path(config_path)   │ │
                    │   │   - self._lock_file = path.with_suffix()    │ │
                    │   └─────────────────────────────────────────────┘ │
                    │                                                   │
                    │   ┌─────────────────────────────────────────────┐ │
                    │   │ load() -> Optional[AppConfig]               │ │
                    │   │   1. _create_default_if_not_exists()        │ │
                    │   │   2. open(config_path, "r")                 │ │
                    │   │   3. yaml.safe_load(f)                      │ │
                    │   │   4. AppConfig.model_validate(data)         │ │
                    │   │   5. return AppConfig                       │ │
                    │   └─────────────────────────────────────────────┘ │
                    │                                                   │
                    │   ┌─────────────────────────────────────────────┐ │
                    │   │ save(app_config: AppConfig) -> None         │ │
                    │   │   1. lock = FileLock(lock_file, timeout=5)  │ │
                    │   │   2. with lock:                             │ │
                    │   │   3.   data = app_config.model_dump()       │ │
                    │   │   4.   open(config_path, "w")               │ │
                    │   │   5.   yaml.dump(data, f)                   │ │
                    │   └─────────────────────────────────────────────┘ │
                    │                                                   │
                    │   ┌─────────────────────────────────────────────┐ │
                    │   │ _create_default_app_config_if_not_exists()  │ │
                    │   │   if not exists:                            │ │
                    │   │     default = AppConfig(llm_config=...)     │ │
                    │   │     self.save(default)                      │ │
                    │   └─────────────────────────────────────────────┘ │
                    └───────────────────────┬───────────────────────────┘
                                            │
                                            │ 读写操作
                                            │
                    ┌───────────────────────▼───────────────────────────┐
                    │           File System (文件系统)                   │
                    │                                                   │
                    │   ┌─────────────────────────────────────────────┐ │
                    │   │  config.yaml (YAML配置文件)                  │ │
                    │   │  ├─ llm_config:                             │ │
                    │   │  │   ├─ base_url                            │ │
                    │   │  │   ├─ api_key                             │ │
                    │   │  │   ├─ model_name                          │ │
                    │   │  │   ├─ temperature                         │ │
                    │   │  │   └─ max_tokens                          │ │
                    │   └─────────────────────────────────────────────┘ │
                    │                                                   │
                    │   ┌─────────────────────────────────────────────┐ │
                    │   │  config.lock (文件锁)                        │ │
                    │   │  - 防止并发写入冲突                          │ │
                    │   │  - timeout: 5秒                             │ │
                    │   └─────────────────────────────────────────────┘ │
                    └───────────────────────────────────────────────────┘
```

## 📦 数据模型关系

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Data Models (数据模型)                             │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐         ┌──────────────────────────┐
    │   AppConfig          │         │   LLMConfig              │
    │  ┌────────────────┐  │         │  ┌────────────────────┐  │
    │  │ llm_config     │──┼────────▶│  │ base_url: HttpUrl  │  │
    │  └────────────────┘  │         │  │ api_key: str       │  │
    │                      │         │  │ model_name: str    │  │
    │  (Pydantic Model)    │         │  │ temperature: float │  │
    └──────────────────────┘         │  │ max_tokens: int    │  │
                                     │  └────────────────────┘  │
                                     │                          │
                                     │  (Pydantic Model)        │
                                     └──────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │   Response[T] (泛型响应模型)                              │
    │  ┌────────────────────────────────────────────────────┐  │
    │  │ code: int = 200                                    │  │
    │  │ msg: str = "success"                               │  │
    │  │ data: Optional[T] = {}                             │  │
    │  │                                                    │  │
    │  │ @staticmethod success(msg, data) -> Response[T]    │  │
    │  │ @staticmethod fail(code, msg, data) -> Response[T] │  │
    │  └────────────────────────────────────────────────────┘  │
    └──────────────────────────────────────────────────────────┘
```

## 🔄 读取配置文件流程 (GET /api/app-config/llm)

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: HTTP请求到达                                             │
└─────────────────────────────────────────────────────────────────┘
    │
    │ GET /api/app-config/llm
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 路由处理 (app_config_routes.py)                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ @router.get("/llm")                                         │ │
│ │ async def get_llm_config(                                   │ │
│ │     app_config_service = Depends(get_app_config_service)    │ │
│ │ )                                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 触发依赖注入
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 依赖注入 (dependencies.py)                               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ @lru_cache()  # 单例模式，整个应用生命周期只创建一次         │ │
│ │ def get_app_config_service():                               │ │
│ │     settings = get_settings()  # 获取配置文件路径           │ │
│ │     repository = FileAppConfigRepository(                   │ │
│ │         settings.app_config_filepath  # "config.yaml"       │ │
│ │     )                                                       │ │
│ │     return AppConfigService(repository)                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 返回服务实例
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 调用服务层 (AppConfigService)                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ def get_llm_config(self) -> LLMConfig:                      │ │
│ │     return self._load_app_config().llm_config               │ │
│ │                                                             │ │
│ │ def _load_app_config(self) -> AppConfig:                    │ │
│ │     return self.app_config_respository.load()               │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 调用仓储层
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 仓储层读取文件 (FileAppConfigRepository)                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ def load(self) -> Optional[AppConfig]:                      │ │
│ │     # 1. 确保配置文件存在                                    │ │
│ │     self._create_default_app_config_if_not_exists()         │ │
│ │                                                             │ │
│ │     # 2. 读取YAML文件                                        │ │
│ │     with open(self._config_path, "r", encoding="utf-8"):    │ │
│ │         data = yaml.safe_load(f)                            │ │
│ │                                                             │ │
│ │     # 3. 验证并转换为Pydantic模型                            │ │
│ │     return AppConfig.model_validate(data)                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 返回AppConfig对象
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: 提取LLM配置                                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ llm_config = app_config.llm_config                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 返回到路由层
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: 构造响应 (排除敏感信息)                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ return Response.success(                                    │ │
│ │     data=llm_config.model_dump(exclude={"api_key"})         │ │
│ │ )                                                           │ │
│ │                                                             │ │
│ │ # 返回JSON:                                                 │ │
│ │ {                                                           │ │
│ │   "code": 200,                                              │ │
│ │   "msg": "success",                                         │ │
│ │   "data": {                                                 │ │
│ │     "base_url": "https://api.deepseek.com/",               │ │
│ │     "model_name": "deepseek-reasoner",                      │ │
│ │     "temperature": 0.7,                                     │ │
│ │     "max_tokens": 8192                                      │ │
│ │     # api_key被排除，不返回给客户端                          │ │
│ │   }                                                         │ │
│ │ }                                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📝 更新配置文件流程 (POST /api/app-config/llm)

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: HTTP请求到达                                             │
└─────────────────────────────────────────────────────────────────┘
    │
    │ POST /api/app-config/llm
    │ Body: {
    │   "base_url": "https://api.openai.com/v1",
    │   "api_key": "",  # 空字符串表示不更新
    │   "model_name": "gpt-4",
    │   "temperature": 0.8,
    │   "max_tokens": 4096
    │ }
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 路由处理 (app_config_routes.py)                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ @router.post("/llm")                                        │ │
│ │ async def update_llm_config(                                │ │
│ │     new_app_config: LLMConfig,  # 自动验证和解析请求体       │ │
│ │     app_config_service = Depends(get_app_config_service)    │ │
│ │ )                                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 依赖注入 (同读取流程)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 调用服务层 (AppConfigService)                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ def update_llm_config(self, llm_config: LLMConfig):         │ │
│ │                                                             │ │
│ │     # 3.1 加载当前配置                                       │ │
│ │     app_config = self._load_app_config()                    │ │
│ │     # └─> repository.load() 从文件读取                       │ │
│ │                                                             │ │
│ │     # 3.2 API Key保护逻辑                                    │ │
│ │     if not llm_config.api_key.strip():                      │ │
│ │         # 如果新配置的api_key为空，保留原有的api_key          │ │
│ │         llm_config.api_key = app_config.llm_config.api_key  │ │
│ │                                                             │ │
│ │     # 3.3 更新配置                                           │ │
│ │     app_config.llm_config = llm_config                      │ │
│ │                                                             │ │
│ │     # 3.4 保存到文件                                         │ │
│ │     self.app_config_respository.save(app_config)            │ │
│ │                                                             │ │
│ │     # 3.5 返回更新后的配置                                   │ │
│ │     return app_config.llm_config                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 调用仓储层保存
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 仓储层写入文件 (FileAppConfigRepository)                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ def save(self, app_config: AppConfig) -> None:              │ │
│ │                                                             │ │
│ │     # 4.1 创建文件锁（防止并发写入冲突）                      │ │
│ │     lock = FileLock(self._lock_file, timeout=5)             │ │
│ │                                                             │ │
│ │     try:                                                    │ │
│ │         with lock:  # 获取锁                                │ │
│ │             # 4.2 将Pydantic模型转换为字典                   │ │
│ │             data_to_dump = app_config.model_dump(           │ │
│ │                 mode="json"                                 │ │
│ │             )                                               │ │
│ │                                                             │ │
│ │             # 4.3 写入YAML文件                               │ │
│ │             with open(self._config_path, "w",               │ │
│ │                      encoding="utf-8") as f:                │ │
│ │                 yaml.dump(                                  │ │
│ │                     data_to_dump,                           │ │
│ │                     f,                                      │ │
│ │                     allow_unicode=True,  # 支持中文          │ │
│ │                     sort_keys=False      # 保持字段顺序      │ │
│ │                 )                                           │ │
│ │     except TimeoutError:                                    │ │
│ │         # 获取锁超时，静默失败                               │ │
│ │         pass                                                │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
    │
    │ 文件写入完成
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 构造响应                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ return Response.success(                                    │ │
│ │     msg="更新LLM信息配置成功",                               │ │
│ │     data=updated_llm_config.model_dump(exclude={"api_key"}) │ │
│ │ )                                                           │ │
│ │                                                             │ │
│ │ # 返回JSON:                                                 │ │
│ │ {                                                           │ │
│ │   "code": 200,                                              │ │
│ │   "msg": "更新LLM信息配置成功",                              │ │
│ │   "data": {                                                 │ │
│ │     "base_url": "https://api.openai.com/v1",               │ │
│ │     "model_name": "gpt-4",                                  │ │
│ │     "temperature": 0.8,                                     │ │
│ │     "max_tokens": 4096                                      │ │
│ │     # api_key被排除，不返回给客户端                          │ │
│ │   }                                                         │ │
│ │ }                                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔑 核心设计模式和特性

### 1. **Clean Architecture (整洁架构)**
```
Interface Layer → Application Layer → Domain Layer ← Infrastructure Layer
     (API)           (Service)         (Protocol)      (Implementation)
```

### 2. **依赖注入 (Dependency Injection)**
- 使用 FastAPI 的 `Depends()` 机制
- `@lru_cache()` 实现单例模式
- 松耦合，易于测试和替换实现

### 3. **协议导向设计 (Protocol-Oriented)**
- `AppConfigRepository` 定义接口协议
- `FileAppConfigRepository` 实现具体逻辑
- 易于扩展（如添加数据库存储实现）

### 4. **并发安全 (Concurrency Safety)**
- 使用 `FileLock` 防止并发写入冲突
- 超时机制（5秒）避免死锁

### 5. **数据验证 (Data Validation)**
- Pydantic 模型自动验证
- 类型安全
- 自动生成 OpenAPI 文档

### 6. **安全性 (Security)**
- API Key 保护：
  - GET 请求不返回 `api_key`
  - POST 请求空 `api_key` 不覆盖原值
  - 使用 `exclude={"api_key"}` 排除敏感字段

### 7. **配置管理 (Configuration Management)**
```
优先级：环境变量 > .env文件 > 默认值

Settings (core/config.py)
  ├─ 从 .env 读取环境变量
  ├─ app_config_filepath = "config.yaml"
  └─ @lru_cache() 单例缓存

FileAppConfigRepository
  ├─ 读取 config.yaml
  ├─ 自动创建默认配置
  └─ YAML 格式存储
```

## 📁 文件结构映射

```
app/
├── interfaces/                    # 接口层
│   ├── endpoints/
│   │   └── app_config_routes.py  # API路由定义
│   ├── dependencies.py            # 依赖注入配置
│   └── schemas/
│       └── base.py                # 响应模型
│
├── application/                   # 应用层
│   └── services/
│       └── app_config_service.py  # 业务逻辑服务
│
├── domain/                        # 领域层
│   ├── models/
│   │   └── app_config.py          # 数据模型
│   └── repositories/
│       └── app_config_repository.py  # 仓储协议
│
└── infrastructure/                # 基础设施层
    └── repositories/
        └── file_app_config_repository.py  # 文件存储实现

core/
└── config.py                      # 全局配置

config.yaml                        # 应用配置文件
config.lock                        # 文件锁（自动生成）
```

## 🎯 关键要点总结

1. **读取流程**：HTTP请求 → 路由 → 依赖注入 → 服务层 → 仓储层 → 读取YAML → 返回数据
2. **更新流程**：HTTP请求 → 路由 → 依赖注入 → 服务层 → API Key保护 → 仓储层 → 文件锁 → 写入YAML
3. **单例模式**：`get_app_config_service()` 和 `get_settings()` 使用 `@lru_cache()` 确保全局唯一
4. **并发安全**：使用 `FileLock` 防止多进程/线程同时写入配置文件
5. **安全保护**：API Key 在响应中被排除，空值不覆盖原有配置
6. **自动创建**：配置文件不存在时自动创建默认配置
7. **类型安全**：全程使用 Pydantic 模型进行数据验证和转换

---

# 领域驱动设计（DDD）实用指南

## 🎯 领域驱动设计（DDD）简单理解

**核心思想**：按照业务逻辑（领域）来组织代码，而不是按照技术实现来组织。

想象你在经营一家餐厅：
- **领域层（Domain）**：菜单、菜品规则（不能点已售罄的菜）
- **应用层（Application）**：点餐流程、结账流程
- **基础设施层（Infrastructure）**：厨房设备、收银系统
- **接口层（Interface）**：服务员、外卖平台

## 📁 四层架构详解（结合你的项目）

### 1️⃣ **Domain Layer（领域层）** - `app/domain/`
**作用**：定义业务核心概念和规则，不依赖任何外部技术

**放什么文件？**
```python
app/domain/
├── models/              # 业务数据模型
│   ├── app_config.py   # ✅ 应用配置模型（LLMConfig, AppConfig）
│   ├── agent.py        # ✅ Agent实体模型
│   └── task.py         # ✅ 任务实体模型
│
├── repositories/        # 仓储接口（Protocol）
│   ├── app_config_repository.py  # ✅ 配置仓储协议
│   └── agent_repository.py       # ✅ Agent仓储协议
│
└── external/           # 外部服务接口（Protocol）
    ├── llm.py         # ✅ LLM接口协议
    └── mcp.py         # ✅ MCP服务接口协议
```

**判断标准**：
- ✅ 是业务概念吗？（Agent、Task、LLM配置）
- ✅ 是接口定义吗？（Protocol、抽象类）
- ✅ 不依赖具体技术吗？（不依赖FastAPI、SQLAlchemy、Redis等）
- ❌ 不包含具体实现（没有数据库操作、API调用）

**例子**：
```python
# ✅ 正确：领域模型
class LLMConfig(BaseModel):
    base_url: HttpUrl
    api_key: str
    model_name: str
    temperature: float
    max_tokens: int

# ✅ 正确：接口协议
class LLM(Protocol):
    async def invoke(self, messages: List[Dict]) -> Dict:
        ...
```

---

### 2️⃣ **Application Layer（应用层）** - `app/application/`
**作用**：编排业务流程，协调领域对象完成用例

**放什么文件？**
```python
app/application/
├── services/           # 业务服务（用例）
│   ├── app_config_service.py    # ✅ 配置管理服务
│   ├── agent_service.py         # ✅ Agent管理服务
│   └── task_execution_service.py # ✅ 任务执行服务
│
└── errors/            # 业务异常
    └── exceptions.py  # ✅ 自定义异常（BadRequestError等）
```

**判断标准**：
- ✅ 是业务流程吗？（创建Agent、执行任务、更新配置）
- ✅ 需要协调多个对象吗？（调用repository、调用LLM）
- ✅ 包含业务逻辑吗？（验证、转换、编排）
- ❌ 不直接处理HTTP请求
- ❌ 不直接操作数据库

**例子**：
```python
# ✅ 正确：应用服务
class AppConfigService:
    def __init__(self, repository: AppConfigRepository):
        self.repository = repository
    
    def update_llm_config(self, llm_config: LLMConfig) -> LLMConfig:
        # 1. 加载当前配置
        app_config = self.repository.load()
        
        # 2. 业务逻辑：保护API Key
        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key
        
        # 3. 保存配置
        app_config.llm_config = llm_config
        self.repository.save(app_config)
        
        return app_config.llm_config
```

---

### 3️⃣ **Infrastructure Layer（基础设施层）** - `app/infrastructure/`
**作用**：提供技术实现，连接外部系统

**放什么文件？**
```python
app/infrastructure/
├── repositories/       # 仓储实现
│   ├── file_app_config_repository.py  # ✅ 文件存储实现
│   └── db_agent_repository.py         # ✅ 数据库存储实现
│
├── external/          # 外部服务实现
│   ├── llm/
│   │   ├── openai_llm.py    # ✅ OpenAI LLM实现
│   │   └── claude_llm.py    # ✅ Claude LLM实现
│   └── mcp/
│       └── mcp_client.py    # ✅ MCP客户端实现
│
├── storage/           # 存储系统
│   ├── postgres.py    # ✅ PostgreSQL连接
│   ├── redis.py       # ✅ Redis连接
│   └── cos.py         # ✅ 对象存储
│
├── models/            # ORM模型
│   └── demo.py        # ✅ SQLAlchemy模型
│
└── logging/           # 日志系统
    └── logging.py     # ✅ 日志配置
```

**判断标准**：
- ✅ 实现了Domain层的接口吗？
- ✅ 依赖具体技术吗？（SQLAlchemy、OpenAI SDK、Redis）
- ✅ 连接外部系统吗？（数据库、API、文件系统）
- ✅ 可以被替换吗？（换成MySQL、换成其他LLM）

**例子**：
```python
# ✅ 正确：基础设施实现
class FileAppConfigRepository(AppConfigRepository):
    def __init__(self, config_path: str):
        self._config_path = Path(config_path)
        self._lock_file = self._config_path.with_suffix(".lock")
    
    def load(self) -> AppConfig:
        with open(self._config_path, "r") as f:
            data = yaml.safe_load(f)
            return AppConfig.model_validate(data)
    
    def save(self, app_config: AppConfig) -> None:
        lock = FileLock(self._lock_file, timeout=5)
        with lock:
            with open(self._config_path, "w") as f:
                yaml.dump(app_config.model_dump(), f)
```

---

### 4️⃣ **Interface Layer（接口层）** - `app/interfaces/`
**作用**：对外提供访问入口（API、CLI等）

**放什么文件？**
```python
app/interfaces/
├── endpoints/         # API路由
│   ├── status_routes.py       # ✅ 健康检查
│   ├── app_config_routes.py   # ✅ 配置管理API
│   └── agent_routes.py        # ✅ Agent管理API
│
├── schemas/           # 请求/响应模型
│   ├── base.py        # ✅ 通用响应模型
│   └── agent_schema.py # ✅ Agent相关Schema
│
├── dependencies.py    # ✅ 依赖注入
│
└── errors/           # HTTP错误处理
    └── exception_handlers.py  # ✅ 异常处理器
```

**判断标准**：
- ✅ 处理HTTP请求吗？
- ✅ 定义API路由吗？
- ✅ 处理请求/响应格式吗？
- ✅ 依赖注入配置吗？

**例子**：
```python
# ✅ 正确：API路由
@router.get("/llm", response_model=Response[LLMConfig])
async def get_llm_config(
    service: AppConfigService = Depends(get_app_config_service)
) -> Response[LLMConfig]:
    llm_config = service.get_llm_config()
    return Response.success(data=llm_config.model_dump(exclude={"api_key"}))

@router.post("/llm", response_model=Response[LLMConfig])
async def update_llm_config(
    new_config: LLMConfig,
    service: AppConfigService = Depends(get_app_config_service)
) -> Response[LLMConfig]:
    updated = service.update_llm_config(new_config)
    return Response.success(msg="更新成功", data=updated.model_dump(exclude={"api_key"}))
```

---

## 🎓 实用判断法则

### 问自己3个问题：

#### 1. **这个文件是"什么"？** → Domain Layer
```python
# 定义业务概念
class Agent(BaseModel):
    id: UUID
    name: str
    status: AgentStatus
```

#### 2. **这个文件"做什么"？** → Application Layer
```python
# 编排业务流程
class AgentService:
    def create_agent(self, name: str) -> Agent:
        # 验证、创建、保存
```

#### 3. **这个文件"怎么做"？** → Infrastructure Layer
```python
# 具体技术实现
class PostgresAgentRepository:
    async def save(self, agent: Agent):
        # 使用SQLAlchemy保存到数据库
```

#### 4. **这个文件"对外提供"？** → Interface Layer
```python
# HTTP API
@router.post("/agents")
async def create_agent(request: CreateAgentRequest):
    # 处理HTTP请求
```

---

## 📊 依赖方向规则（重要！）

```
Interface Layer
      ↓ 依赖
Application Layer
      ↓ 依赖
Domain Layer ← Infrastructure Layer
   (核心)        (实现)
```

**规则**：
- ✅ 外层可以依赖内层
- ✅ Infrastructure实现Domain的接口
- ❌ Domain不能依赖Infrastructure
- ❌ 内层不能依赖外层

---

## 🔍 常见文件分类示例

### ✅ Domain Layer
```python
# 业务模型
class Task(BaseModel):
    id: UUID
    title: str
    status: TaskStatus

# 接口协议
class TaskRepository(Protocol):
    def save(self, task: Task) -> None: ...
    def find_by_id(self, id: UUID) -> Task: ...
```

### ✅ Application Layer
```python
# 业务服务
class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository
    
    def create_task(self, title: str) -> Task:
        task = Task(id=uuid4(), title=title, status=TaskStatus.PENDING)
        self.repository.save(task)
        return task
    
    def complete_task(self, task_id: UUID) -> Task:
        task = self.repository.find_by_id(task_id)
        task.status = TaskStatus.COMPLETED
        self.repository.save(task)
        return task
```

### ✅ Infrastructure Layer
```python
# 数据库实现
class PostgresTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, task: Task) -> None:
        db_task = TaskModel(**task.model_dump())
        self.session.add(db_task)
        await self.session.commit()
    
    async def find_by_id(self, id: UUID) -> Task:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == id)
        )
        db_task = result.scalar_one()
        return Task.model_validate(db_task)
```

### ✅ Interface Layer
```python
# API路由
@router.post("/tasks", response_model=Response[Task])
async def create_task(
    request: CreateTaskRequest,
    service: TaskService = Depends(get_task_service)
) -> Response[Task]:
    task = service.create_task(request.title)
    return Response.success(data=task)

@router.put("/tasks/{task_id}/complete", response_model=Response[Task])
async def complete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service)
) -> Response[Task]:
    task = service.complete_task(task_id)
    return Response.success(data=task)
```

---

## 🎯 快速决策树

```
新建一个Python文件，应该放在哪里？

1. 是Pydantic模型且表示业务概念？
   → app/domain/models/

2. 是Protocol/抽象类定义接口？
   → app/domain/repositories/ 或 app/domain/external/

3. 包含业务流程编排逻辑？
   → app/application/services/

4. 使用了具体技术（SQLAlchemy、OpenAI SDK、Redis等）？
   → app/infrastructure/

5. 处理HTTP请求/响应？
   → app/interfaces/endpoints/

6. 定义API请求/响应Schema？
   → app/interfaces/schemas/

7. 是SQLAlchemy ORM模型？
   → app/infrastructure/models/

8. 是依赖注入配置？
   → app/interfaces/dependencies.py
```

---

## 💡 实战建议

### 开发新功能时的步骤：

1. **先设计Domain层**（业务模型和接口）
2. **再实现Application层**（业务逻辑）
3. **然后实现Infrastructure层**（技术实现）
4. **最后实现Interface层**（API暴露）

### 例子：添加"Agent执行任务"功能

```python
# Step 1: Domain Layer - 定义概念
# app/domain/models/agent.py
class Agent(BaseModel):
    id: UUID
    name: str
    llm_config: LLMConfig

# app/domain/external/executor.py
class TaskExecutor(Protocol):
    async def execute(self, task: Task, agent: Agent) -> TaskResult: ...

# Step 2: Application Layer - 业务流程
# app/application/services/agent_service.py
class AgentService:
    def __init__(self, executor: TaskExecutor):
        self.executor = executor
    
    async def run_task(self, agent_id: UUID, task: Task) -> TaskResult:
        agent = self.agent_repo.find_by_id(agent_id)
        result = await self.executor.execute(task, agent)
        return result

# Step 3: Infrastructure Layer - 技术实现
# app/infrastructure/external/llm_executor.py
class LLMTaskExecutor(TaskExecutor):
    def __init__(self, llm: LLM):
        self.llm = llm
    
    async def execute(self, task: Task, agent: Agent) -> TaskResult:
        response = await self.llm.invoke([
            {"role": "user", "content": task.description}
        ])
        return TaskResult(output=response["content"])

# Step 4: Interface Layer - API暴露
# app/interfaces/endpoints/agent_routes.py
@router.post("/agents/{agent_id}/tasks")
async def execute_task(
    agent_id: UUID,
    task: TaskRequest,
    service: AgentService = Depends(get_agent_service)
):
    result = await service.run_task(agent_id, task)
    return Response.success(data=result)
```

---

## 📝 总结

| 层级 | 放什么 | 不放什么 | 关键词 |
|------|--------|----------|--------|
| **Domain** | 业务模型、接口协议 | 具体实现、技术细节 | Protocol, BaseModel, 业务规则 |
| **Application** | 业务流程、用例服务 | HTTP处理、数据库操作 | Service, 编排, 协调 |
| **Infrastructure** | 技术实现、外部集成 | 业务逻辑 | SQLAlchemy, OpenAI, Redis |
| **Interface** | API路由、请求响应 | 业务逻辑 | FastAPI, @router, Depends |

**记住**：Domain是核心，其他层都是为它服务的！
