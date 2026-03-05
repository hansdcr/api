# Postgres
* 运行postgres
```
(base) gelin@MacBookPro manus_postgres_data % docker run -d \
--name manus-postgres \
-p 5432:5432 \
-e POSTGRES_USER=postgres \
-e POSTGRES_PASSWORD=postgres \
-e POSTGRES_DB=manus \
-v manus_postgres_data:/var/lib/postgresql \     
postgres:latest
```

* 运行redis
```
docker run -d \
--name manus-redis \
-p 6379:6379 \
-v manus_redis_data:/data \
redis:latest
```