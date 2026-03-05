* app应用启动命令
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --lifespan on
```