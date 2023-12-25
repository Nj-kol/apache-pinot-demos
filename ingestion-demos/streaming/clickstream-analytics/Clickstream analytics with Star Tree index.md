 
# Clickstream analytics with Star Tree index

## Download and extract data

* You can download the dataset from : https://figshare.com/articles/dataset/Wikipedia_Clickstream/1305770

* Then extract the data locally

```bash
gzip -d 2017_01_en_clickstream.tsv.gz
```

## Prepare data in spark

* The dataset is large, so we will only take a sample of the data and also convert it into JSON so that
  it can be fed to a Kafka topic

```scala
import org.apache.spark.sql.Encoders
import org.apache.spark.sql.functions

val fileLoc = "/Users/nilanjan1.sarkar/Downloads/data/2017_01_en_clickstream.tsv"

case class Click(prev: String, curr: String, link: String, n: Long)

val clickSchema = Encoders.product[Click].schema

var clickDf = spark.read.format("csv").     // Use "csv" regardless of TSV or CSV.
                option("header", "true").  // Does the file have a header line?
                option("delimiter", "\t"). // Set delimiter to tab or comma.
                schema(clickSchema).        // Schema that was built above.
                load(fileLoc)

clickDf.createOrReplaceTempView("clickstream")      

// Do a random sampling on the data
val sampledDf = spark.sql("""
select prev as referrer, curr as article_name,n as page_views
from clickstream
where rand() <= 0.0001
distribute by rand()
sort by rand()
limit 10000
""")  

val randomTimestamp = functions.udf((s: Int) => {
  s + scala.util.Random.nextInt(2000)
})

val sampledWithTimeDf = sampledDf.withColumn("timestampInEpoch", randomTimestamp(lit(1516364153)))

sampledWithTimeDf.show(false)
```

* The output looks like :

```bash
+---------------------------------------------------------+--------------------------------------+----------+----------------+
|referrer                                                 |article_name                          |page_views|timestampInEpoch|
+---------------------------------------------------------+--------------------------------------+----------+----------------+
|2016_BDO_World_Darts_Championship                        |Lisa_Ashton                           |96        |1516365032      |
|other-empty                                              |Baler_(film)                          |334       |1516366019      |
|Brooklyn_Nets                                            |Yankee_Global_Enterprises             |14        |1516364402      |
|other-empty                                              |Forrest_H._Duttlinger_Natural_Area    |38        |1516365742      |
|Ninox                                                    |Sulu_hawk-owl                         |17        |1516365089      |
```

* Convert it into JSON

```json
sampledWithTimeDf.write.json("/Users/nilanjan1.sarkar/Downloads/data/json")
```

* Rename the JSON file generated to something more meaningful

```bash
mv part-00000-3ab21414-8ffe-416d-a78e-edab2ea61b9e-c000.json clickstream.json
```

# Pinot

## Create a schema

Schema is used to define the columns and data types of the Pinot table :

`${HOME}/volumes/pinot/samples/wikipedia/wikipedia-schema.json`

```json
{
  "schemaName": "wikipedia_clickstream",
  "dimensionFieldSpecs": [
    {
      "name": "referrer",
      "dataType": "STRING"
    },
    {
      "name": "article_name",
      "dataType": "STRING"
    }
  ],
  "metricFieldSpecs": [
    {
      "name": "page_views",
      "dataType": "LONG"
    }
  ],
  "dateTimeFieldSpecs": [{
    "name": "timestampInEpoch",
    "dataType": "LONG",
    "format" : "1:MILLISECONDS:EPOCH",
    "granularity": "1:MILLISECONDS"
  }]
}
```

## Creating a table config

* Here's the realtime table config for the `wikipedia-clickstream` table. 

`${HOME}/volumes/pinot/samples/wikipedia/wikipedia-clickstream-table-realtime.json`

```json
{
   "tableName":"wikipedia_clickstream",
   "tableType":"REALTIME",
   "segmentsConfig":{
      "timeColumnName":"timestampInEpoch",
      "timeType":"MILLISECONDS",
      "schemaName":"wikipedia_clickstream",
      "replicasPerPartition":"1"
   },
   "tenants":{
      
   },
   "tableIndexConfig":{
      "starTreeIndexConfigs":[
         {
            "dimensionsSplitOrder":[
               "article_name",           	
               "referrer"
            ],
            "skipStarNodeCreationForDimensions":[
               
            ],
            "functionColumnPairs":[
               "SUM__page_views"
            ],
            "maxLeafRecords":1
         }
      ],
      "loadMode":"MMAP",
      "streamConfigs":{
         "streamType":"kafka",
         "realtime.segment.flush.threshold.size":"0",
         "realtime.segment.flush.threshold.time":"1h",
         "realtime.segment.flush.desired.size":"50M",
         "stream.kafka.consumer.type":"lowlevel",
         "stream.kafka.broker.list":"LM0001680:39092",
         "stream.kafka.topic.name":"wikipedia-clickstream",
         "stream.kafka.decoder.class.name":"org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
         "stream.kafka.consumer.factory.class.name":"org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
         "stream.kafka.consumer.prop.auto.offset.reset":"smallest"
      }
   },
   "metadata":{
      "customConfigs":{
         
      }
   }
}
```

## Uploading your schema and table config

* Now that we have our table and schema, let's upload them to the cluster. 
* As soon as the realtime table is created, it will begin ingesting from the Kafka topic
* The command needs to be executed on the controlled node

```bash
docker container exec -it pinot-controller bash

/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/pinot/samples/wikipedia/wikipedia-schema.json \
-tableConfigFile /opt/pinot/samples/wikipedia/wikipedia-clickstream-table-realtime.json \
-controllerHost pinot-controller \
-controllerPort 9000 \
-exec

# Drop table
/opt/pinot/bin/pinot-admin.sh ChangeTableState \
-tableName wikipedia_clickstream \
-state drop 
```

http://localhost:9000

# Kafka

* Create a new topic to post the clickstream data

```bash
docker container exec -it kafka-standalone bash

# Create a Kafka Topic

kafka-topics.sh \
--create \
--zookeeper zookeeper-standalone:2181 \
--partitions 3 \
--replication-factor 1 \
--topic wikipedia-clickstream
```

* Push data to kafka

```bash
kafka-console-producer.sh \
--broker-list localhost:9092 \
--topic wikipedia-clickstream < /opt/samples/clickstream.json
```

* See data in Kafka

```bash
kafka-console-consumer.sh \
--bootstrap-server localhost:9092 \
--topic wikipedia-clickstream \
--from-beginning
```

* Sample Queries

```sql
SELECT article_name, SUM(page_views) as total_views FROM wikipedia_clickstream 
GROUP BY article_name,referrer

SELECT SUM(page_views) FROM wikipedia_clickstream 
WHERE article_name ='Akkadian_Empire'
GROUP BY referrer
```

## References

https://github.com/IBM/kafka-streaming-click-analysis

https://meta.wikimedia.org/wiki/Research:Wikipedia_clickstream
 
https://figshare.com/articles/dataset/Wikipedia_Clickstream/1305770


### Demo

## Sqllab View

![Superset sqllab](Superset_Sqllab.png)

## Sample Dashboard

![Superset Pinot Dashboard](wikipedia-clickstream-dashboard.jpg)
