## Spark Filter Pipeline

The pipeline will read data from kafka, do a lookup in Redis to filter out undesired inputs and write
the fileterd data to another kafka topic

### Launch Spark shell

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

val checkPointLocation = "/home/njkol/tmp/spark-redis"

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
.option("checkpointLocation", checkPointLocation) 
.start()
    
query.awaitTermination()
```