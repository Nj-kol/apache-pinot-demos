# Apache Pinot Demo

* Create an external network to bind all the components together

```bash
docker network create sandbox
```

## Spin Up Pinot 

```bash
# Create local directories for mounting volumes
mkdir -p ${HOME}/volumes/pinot/zookeeper/data
mkdir -p ${HOME}/volumes/pinot/zookeeper/datalog
mkdir -p ${HOME}/volumes/pinot/controller
mkdir -p ${HOME}/volumes/pinot/server

mkdir -p ${HOME}/volumes/pinot/samples

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

http://localhost:9000/#/query

# Kafka on Docker

```bash
# Set up Zookeeper
mkdir -p ${HOME}/volumes/zookeeper

docker pull zookeeper:3.6.1

ZK_HOME=${HOME}/volumes/zookeeper

docker container run \
-p 30181:2181 \
--network=sandbox \
--name zookeeper-standalone \
--restart always \
-e ZOO_LOG4J_PROP="INFO,ROLLINGFILE" \
-v ${ZK_HOME}/datalog:/datalog \
-v ${ZK_HOME}/data:/data \
-v ${ZK_HOME}/logs:/logs \
-d zookeeper:3.6.1

## Housekeeping

docker container logs zookeeper-standalone

docker container start zookeeper-standalone

docker container stop zookeeper-standalone

docker container rm zookeeper-standalone

docker container exec -it zookeeper-standalone bash

bin/zkCli.sh

## Setup Kafka

mkdir -p ${HOME}/volumes/kafka/data
mkdir -p ${HOME}/volumes/kafka/samples

docker pull wurstmeister/kafka

docker container run -d \
-p 39092:9092 \
--name kafka-standalone \
--network sandbox \
-e KAFKA_ADVERTISED_HOST_NAME=LM0001680 \
-e KAFKA_ADVERTISED_PORT=39092 \
-e KAFKA_BROKER_ID=1 \
-e KAFKA_ZOOKEEPER_CONNECT=zookeeper-standalone:2181 \
-e ZK=zk \
-v ${HOME}/volumes/kafka/data:/kafka \
-v ${HOME}/volumes/kafka/samples:/opt/samples \
-t wurstmeister/kafka

## Housekeeping

docker container start kafka-standalone

docker container stop kafka-standalone

docker container rm kafka-standalone

docker container logs kafka-standalone -f 

docker container exec -it kafka-standalone bash
```

# Case Study

* Once an offline segment is pushed to cover a recent time period :
  - the brokers automatically switch to using the offline table for segments for that time period
  - and use realtime table only for data not available in offline table

## Before batch test

200,Lucy,Smith,Female,Maths,3.8,1570863600000 ( offline data )

1570863600000 - Saturday, 12 October 2019 07:00:00
1570863510000 - Saturday, 12 October 2019 06:58:30

**Add a record with past timestamp in kafka**

{"studentID":200,"firstName":"Lucy","lastName":"Smith","gender":"Female","subject":"Maths","score":3.6,"timestampInEpoch":1570863510000}

select * from transcript where studentID=200

You'll notice that only the record in offline table is being shown ( i.e. for 1570863600000 )

## After batch test

200,Lucy,Smith,Female,English,3.5,1571036400000

1571036400000 - Monday, 14 October 2019 07:00:00
1612151387000 - Monday, 1 February 2021 03:49:47

**Add a record with latest timestamp in kafka**

{"studentID":200,"firstName":"Lucy","lastName":"Smith","gender":"Female","subject":"English","score":4.2,"timestampInEpoch":1612151387000}

select * from transcript where studentID=200

You'll notice that a new record is being shown ( i.e. for 1612151387000 )

# Notes

* The tenants section in both the OFFLINE and realtime tables must be same, otherwise HYBRID table
  would not be formed

References
==========
https://docs.pinot.apache.org/basics/getting-started

https://docs.pinot.apache.org/basics/getting-started/pushing-your-data-to-pinot

https://docs.pinot.apache.org/basics/getting-started/pushing-your-streaming-data-to-pinot