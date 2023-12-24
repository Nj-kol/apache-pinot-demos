# Setup Components for Demo

## Install Pinot with Docker Compose

### Setup

```shell
mkdir -p ${HOME}/Compose/pinot

vim pinot-original.yml

docker-compose -f pinot-original.yml up -d

## Stop
docker-compose -f pinot-original.yml down
```

```shell
# Create local directories for mounting volumes
mkdir -p ${HOME}/Compose/pinot/volumes/zookeeper
mkdir -p ${HOME}/Compose/pinot/volumes/controller
mkdir -p ${HOME}/Compose/pinot/volumes/broker
mkdir -p ${HOME}/Compose/pinot/volumes/server

docker cp pinot-controller:/opt/pinot/plugins/ \
${HOME}/Compose/pinot/volumes/controller/plugins

docker cp pinot-server:/opt/pinot/plugins/ \
${HOME}/Compose/pinot/volumes/server/plugins

docker cp pinot-broker:/opt/pinot/plugins/ \
${HOME}/Compose/pinot/volumes/broker/plugins
```

vim pinot-controller.conf

```shell


controller.port=9000
controller.vip.host=pinot-controller
controller.vip.port=9000
controller.data.dir=/var/pinot/controller/data
controller.zk.str=pinot-zookeeper:2181
pinot.set.instance.id.to.hostname=true


pinot.service.role=CONTROLLER
pinot.cluster.name=real-time-analytics
pinot.zk.server=pinot-zookeeper:2181
controller.port=9000
controller.vip.host=pinot-controller
controller.vip.port=9000

controller.data.dir=s3://pinot/controller-data
controller.local.temp.dir=/tmp/pinot-tmp-data

pinot.controller.storage.factory.class.s3=org.apache.pinot.plugin.filesystem.S3PinotFS
pinot.controller.storage.factory.s3.endpoint=http://192.168.0.152:9000
pinot.controller.storage.factory.s3.region=us-west-2
pinot.controller.storage.factory.s3.accessKey=minio
pinot.controller.storage.factory.s3.secretKey=minio123

pinot.controller.segment.fetcher.protocols=file,http,s3
pinot.controller.segment.fetcher.s3.class=org.apache.pinot.common.utils.fetcher.PinotFSSegmentFetcher
```

vim pinot-broker.conf

```
pinot.service.role=BROKER
pinot.cluster.name=real-time-analytics
pinot.zk.server=pinot-zookeeper:2181
pinot.broker.client.queryPort=8099
pinot.broker.routing.table.builder.class=random
```

vim pinot-server.conf

```shell
pinot.service.role=SERVER
pinot.cluster.name=real-time-analytics
pinot.zk.server=pinot-zookeeper:2181
pinot.set.instance.id.to.hostname=true
pinot.server.netty.port=8098
pinot.server.adminapi.port=8097
pinot.server.instance.dataDir=/tmp/pinot/data/server/index
pinot.server.instance.segmentTarDir=/tmp/pinot/data/server/segmentTar

pinot.server.storage.factory.class.s3=org.apache.pinot.plugin.filesystem.S3PinotFS
pinot.server.storage.factory.s3.endpoint=http://192.168.0.152:9000
pinot.server.storage.factory.s3.region=us-west-2
pinot.server.storage.factory.s3.accessKey=minio
pinot.server.storage.factory.s3.secretKey=minio123
pinot.server.segment.fetcher.protocols=file,http,s3
pinot.server.segment.fetcher.s3.class=org.apache.pinot.common.utils.fetcher.PinotFSSegmentFetcher
```


## Spin Up Pinot 

```bash
## Start
docker-compose -f pinot-standalone.yml up -d

## Stop
docker-compose -f pinot-standalone.yml down
```

**Housekeeping**

```bash
docker logs pinot-controller

docker exec -it pinot-controller bash

docker logs pinot-broker

docker exec -it pinot-broker bash

docker logs pinot-server

docker exec -it pinot-server bash
```

http://localhost:9210/#/query

### Kafka

```bash
mkdir -p ${HOME}/Compose/kafka

docker-compose -f kafka.yml up -d
```

## Housekeeping

docker container logs zookeeper-standalone

docker container start zookeeper-standalone

docker container stop zookeeper-standalone

docker container rm zookeeper-standalone

docker container exec -it zookeeper-standalone bash

bin/zkCli.sh

## Housekeeping

docker container start kafka-standalone

docker container stop kafka-standalone

docker container rm kafka-standalone

docker container logs kafka-standalone -f 

docker container exec -it kafka-standalone bash
```

## References

https://docs.pinot.apache.org/basics/getting-started/running-pinot-in-docker