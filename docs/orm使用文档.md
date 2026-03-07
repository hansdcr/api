* 创建sessions表
```angular2html
#步骤1:生成迁移脚本
alembic revision --autogenerate -m "create sessions table"

#步骤2: 提交正式写入postgres数据库
alembic upgrade head
```
