## Pinot with S3 Deep Storage

Here we will be spiining up a Pinot Cluster with S3 as a Deep store

### Setup

```shell
vim pinot/volumes/controller/pinot-controller.conf
```

Change the following to point to your S3 :

```shell
controller.data.dir=s3://pinot/controller-data
pinot.controller.storage.factory.s3.endpoint=http://192.168.0.152:9000
pinot.controller.storage.factory.s3.region=us-west-2
pinot.controller.storage.factory.s3.accessKey=minio
pinot.controller.storage.factory.s3.secretKey=minio123
```

```shell
vim pinot/volumes/server/pinot-server.conf
```

Change the following to point to your S3 :

```shell
controller.data.dir=s3://pinot/controller-data
pinot.controller.storage.factory.s3.endpoint=http://192.168.0.152:9000
pinot.controller.storage.factory.s3.region=us-west-2
pinot.controller.storage.factory.s3.accessKey=minio
pinot.controller.storage.factory.s3.secretKey=minio123
```

### Spin Up Pinot 

```bash
## Start
docker-compose -f pinot-standalone.yml up -d

docker-compose -f pinot-compose.yml up -d

## Stop
docker-compose -f pinot-standalone.yml down

docker-compose -f pinot-compose.yml down
```

UI : http://localhost:9210/#/query

**Housekeeping**

```bash
docker logs pinot-controller

docker exec -it pinot-controller bash
```

## References

https://docs.pinot.apache.org/basics/getting-started/running-pinot-in-docker