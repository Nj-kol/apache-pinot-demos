# Superset
 
```bash
# Pull the latest image
 
docker pull amancevice/superset:1.0.0
 
# Spin up a container
 
docker container run -d -p 30092:8088  \
--network sandbox \
--name superset \
amancevice/superset:1.0.0
 
# Create an admin account ( one time activity )
 
docker exec -it superset superset-init
```

## UI

http://localhost:30092

## Pinot URL for Database creation with presto

```
presto://presto-standalone:8080/pinot/default
```