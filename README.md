# Apache Pinot with SuperSet : Wikipedia Clickstream analytics with Star Tree index

## Bring up Ancillary components

This will bring up S3 and Redis :

```shell
W
```

Login to Minio and create a bucket called `pinot`

- URL : http://localhost:9001/browser/
- u/p : minio/minio123


**Setup Redis CLI**

Login to Redis Shell

```shell
docker exec -it redis-stack redis-cli
```

Create a Bloom filter and add elements :

```shell
## Create a new bloom filter
BF.RESERVE whitelisted_linktypes 0.001 100

## Add allowed link types
BF.MADD whitelisted_linktypes link external

## Check for existence
BF.EXISTS whitelisted_linktypes link
BF.EXISTS whitelisted_linktypes external

quit
```

### Bring up Pinot

**Setup config**

Change IP in the following files :

In `pinot/volumes/controller/pinot-controller.conf`, change :

```
pinot.controller.storage.factory.s3.endpoint=http://<YOUR_MACHINE_IP>:9000
```

In `pinot/volumes/server/pinot-server.conf` , change :

```
pinot.server.storage.factory.s3.endpoint=http://<YOUR_MACHINE_IP>:9000
```

Then, bring up the stack :

```shell
docker-compose -f pinot/pinot-standalone.yml up -d
```

This will bring up  :

1. Zookeeper
2. Kafka 
3. Kafdrop ( UI for kafka )
4. Pinot Components
   - Pinot Controller
   - Pinot Broker
   - Pinot Server

### Bring up Superset

To setup and run SuperSet and connect to pinot, some initial setup has to be done. Please follow the instructions under `superset-pinot/README.md`


### All UIs

**Minio S3**
- URL : http://localhost:9001/browser/
- u/p : minio/minio123

**Redis**
- URL : http://localhost:8001/redis-stack/browser

**Pinot & Kafdrop**
- Pinot UI   : http://localhost:9210/#/query
- Kafdrop    : http://localhost:9100

**Superset**
- UI : http://localhost:30092/login
- u/p: [admin/admin]

## Wikipedia Clickstream Analytics Demo

**Prepare sample data set**

Follow steps in : `wikipedia-clickstream-analysis/spark/Clickstream_Data_Preparation.md`

**Create Kafka Topic(s)**

```bash
docker container exec -it kafka \
kafka-topics \
--create \
--bootstrap-server localhost:9092 \
--partitions 1 \
--replication-factor 1 \
--topic clickstream-raw

docker container exec -it kafka \
kafka-topics \
--create \
--bootstrap-server localhost:9092 \
--partitions 1 \
--replication-factor 1 \
--topic clickstream-transformed
```

**Create REALTIME table in Pinot**

```shell
docker container exec -it pinot-controller \
/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/examples/streaming/wikipedia-clickstream/wikipedia-clickstream-schema.json \
-tableConfigFile /opt/examples/streaming/wikipedia-clickstream/wikipedia-clickstream-table-realtime.json \
-exec
```

**Start Spark pre-processing job**

The pipeline will read data from kafka, do a lookup in Redis to filter out undesired inputs and write the fileterd data to another kafka topic

```shell
spark-shell \
--driver-memory 2G \
--executor-memory 4G \
--executor-cores 8 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,redis.clients:jedis:5.0.2
```

## Code

```scala
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._
import spark.implicits._
import redis.clients.jedis.Jedis

val checkPointLocation = "/home/njkol/tmp/spark-redis-1"

val redisHost = "localhost"
val redisPort = 6379
val bloomFilterName = "whitelisted_linktypes"
val kafkaServer = "localhost:9092"
val kafkaSourceTopic = "clickstream-raw"
val kafkaDestinationTopic = "clickstream-transformed"

@transient lazy val jedis = new Jedis(redisHost, redisPort)

def bloomFilterLookup(json: Map[String,String]): Long = {
 val script = "return redis.call('BF.EXISTS', KEYS[1], ARGV[1])"
 jedis.eval(script, 1, bloomFilterName, json("link_type")).asInstanceOf[Long]
}

val bloomFilterLookupFunction = udf[Long,Map[String,String]](bloomFilterLookup)

val inputStream = spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", kafkaServer)
  .option("subscribe", kafkaSourceTopic)
  .option("startingOffsets", "latest")
  .load()

// Filter data stream by reading External context
val finalDf = inputStream
.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
.withColumn("deser",from_json(col("value"),MapType(StringType,StringType)))
.withColumn("computed",bloomFilterLookupFunction(col("deser")))
.filter(col("computed") > 0 )
.drop("deser")
.drop("computed")

// Write filtered data to Kafka for further downstream processing
val query = finalDf.writeStream
.format("kafka")
.option("kafka.bootstrap.servers", kafkaServer)
.option("topic", kafkaDestinationTopic)
.option("failOnDataLoss", "false")
.option("checkpointLocation", checkPointLocation) 
.start()
    
query.awaitTermination()
```

**Send data to Kakfa**

```shell
SAMPLE_DATA_FILE="/home/njkol/Sample_Data/wikipedia_clickstream/json2/part-00000-1e492adb-bb07-4845-a518-999f5665e0a6-c000.json"

## Copy sample data file to kafka docker
docker cp $SAMPLE_DATA_FILE kafka:/home/appuser

## Ingest some records
docker container exec -it kafka bash

kafka-console-producer \
--broker-list localhost:9092 \
--topic clickstream-raw < /home/appuser/part-00000-1e492adb-bb07-4845-a518-999f5665e0a6-c000.json
```

**Loading sample data into stream**

Push sample JSON into Kafka topic, using the `producer.py` script from `clients` folder in the repo

```shell


python clients/producer.py \
--broker-list "localhost:9092" \
--topic wikipedia-clickstream \
--file-path "ingestion-demos/streaming/clickstream-analytics/data/clickstream.json"
```

* See data in Kafka : http://localhost:9100/

### Final Superset Dashboard

![Superset Pinot Dashboard](ingestion-demos/streaming/images/wikipedia-clickstream-dashboard.jpg)

## References

https://docs.pinot.apache.org/basics/getting-started

https://docs.pinot.apache.org/basics/getting-started/pushing-your-data-to-pinot

https://docs.pinot.apache.org/basics/getting-started/pushing-your-streaming-data-to-pinot