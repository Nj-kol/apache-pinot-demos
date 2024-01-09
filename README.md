# Apache Pinot with SuperSet : Wikipedia Clickstream analytics with Star Tree index

## Bring up Ancillary components

This will bring up S3 and Redis :

```shell
docker-compose -f ancillary/ancillary-components.yml up -d
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
BF.EXISTS whitelisted_linktypes others

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

## Demo: Wikipedia Clickstream Analytics

Once the superset container has been described in : `superset-pinot/README.md`, start the container before for warmup

```shell
docker start custom-superset
```

**Step 1 : Prepare sample data set**

Follow steps in : `wikipedia-clickstream-analysis/spark/Clickstream_Data_Preparation.md`

**Step 2 : Create Kafka Topic(s)**

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

**Step 3 : Create REALTIME table in Pinot**

```shell
docker container exec -it pinot-controller \
/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/examples/streaming/wikipedia-clickstream/wikipedia-clickstream-schema.json \
-tableConfigFile /opt/examples/streaming/wikipedia-clickstream/wikipedia-clickstream-table-realtime.json \
-exec
```

**Step 4 : Start Spark pre-processing job**

The pipeline will read data from kafka, do a lookup in Redis to filter out undesired inputs and write the fileterd data to another kafka topic

Start a Spark shell :

```shell
spark-shell \
--driver-memory 2G \
--executor-memory 4G \
--executor-cores 8 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,redis.clients:jedis:5.0.2
```

Paste the code in Spark shell :

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

**Step 5 : Send data to Kakfa**

From another shell, start sending data to kakfa :

```shell
## Copy sample data file to kafka docker
docker cp /home/njkol/Sample_Data/wikipedia_clickstream/json3/part-00001-0a72d7ce-c897-4b8d-85a4-d33a61109df6-c000.json kafka:/home/appuser

## Ingest some records
docker container exec -it kafka bash

kafka-console-producer \
--broker-list localhost:9092 \
--topic clickstream-raw < /home/appuser/part-00000-0a72d7ce-c897-4b8d-85a4-d33a61109df6-c000.json
```

* See data in Kafka : http://localhost:9100/

### Sample Pinot queries

```sql
-- Regular queries
select distinct(link_type) 
from wikipedia_clickstream;

-- Queries utilising Star-tree index
SELECT article_name,SUM(page_views) 
FROM wikipedia_clickstream 
WHERE article_name = 'Aristotle' 
GROUP BY article_name;

SELECT article_name,referrer,SUM(page_views) 
FROM wikipedia_clickstream 
WHERE article_name = 'Aristotle' 
GROUP BY article_name,referrer;

SELECT article_name,referrer,SUM(page_views) 
FROM wikipedia_clickstream 
WHERE article_name = 'Aristotle'
AND referrer = 'Ruhollah_Khomeini'
GROUP BY article_name,referrer;

-- Sketch queries

--HyperLogLog (HLL Demo)

SELECT 
count(distinct(referrer)) AS num_referrer
FROM wikipedia_clickstream;

SELECT 
distinctcounthll(referrer) AS num_referrer
FROM wikipedia_clickstream;

-- 178631
SELECT 
distinctcounthll(article_name, 'nominalEntries=8192')  AS num_distinct_article_name
FROM wikipedia_clickstream;

-- Theta Sketch Demo

-- Count distinct
SELECT 
distinctCountThetaSketch(referrer) AS num_referrer
FROM wikipedia_clickstream;

SELECT
distinctCountThetaSketch(referrer, 'nominalEntries=8192') AS num_referrer
FROM wikipedia_clickstream;

-- Set operations : Difference in count of referrers of articles on Aristotle based on link type
SELECT 
count(distinct(referrer)) AS num_internal_referrers
FROM wikipedia_clickstream 
WHERE
article_name = 'Aristotle' AND link_type='link';

SELECT 
count(distinct(referrer)) AS num_external_referrers
FROM wikipedia_clickstream 
WHERE article_name = 'Aristotle' AND link_type='external';

SELECT distinctCountThetaSketch(
  referrer, 
  'nominalEntries=4096', 
  'link_type = ''link'' AND article_name = ''Aristotle'' ',
  'link_type = ''external'' AND article_name = ''Aristotle''',
  'SET_DIFF($1, $2)'
) AS value
FROM wikipedia_clickstream 
WHERE link_type IN ('link','external');
```

### Final Superset Dashboard

![Superset Pinot Dashboard](ingestion-demos/streaming/images/wikipedia-clickstream-dashboard.jpg)

## Teardown

```shell
docker-compose -f pinot/pinot-standalone.yml down

docker-compose -f ancillary/ancillary-components.yml down
```

## References

https://docs.pinot.apache.org/basics/getting-started

https://docs.pinot.apache.org/basics/getting-started/pushing-your-data-to-pinot

https://docs.pinot.apache.org/basics/getting-started/pushing-your-streaming-data-to-pinot