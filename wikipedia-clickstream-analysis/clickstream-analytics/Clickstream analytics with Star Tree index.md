 
# Clickstream analytics with Star Tree index

## Create a schema

Schema is used to define the columns and data types of the Pinot table : `pinot/volumes/examples/streaming/wikipedia-clickstream/wikipedia-schema.json`

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
    "dataType": "TIMESTAMP",
    "format" : "1:MILLISECONDS:EPOCH",
    "granularity": "1:MILLISECONDS"
  }]
}
```

## Creating a table config

Here's the realtime table config for the `wikipedia-clickstream` table : `pinot/volumes/examples/streaming/wikipedia-clickstream/wikipedia-clickstream-table-realtime.json`

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
             "aggregationConfigs": [
                {
                  "columnName": "page_views",
                  "aggregationFunction": "SUM",
                  "compressionCodec": "LZ4"
                }
              ],
             "maxLeafRecords": 100
          }
       ],
       "loadMode":"MMAP",
       "streamConfigs":{
          "streamType":"kafka",
          "realtime.segment.flush.threshold.size":"0",
          "realtime.segment.flush.threshold.time":"1h",
          "realtime.segment.flush.desired.size":"50M",
          "stream.kafka.consumer.type":"lowlevel",
          "stream.kafka.hlc.zk.connect.string": "pinot-zookeeper:2181/kafka",
          "stream.kafka.zk.broker.url": "pinot-zookeeper:2181/kafka",
          "stream.kafka.broker.list": "kafka:19092",
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
docker container exec -it pinot-controller \
/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/examples/streaming/wikipedia-clickstream/wikipedia-clickstream-schema.json \
-tableConfigFile /opt/examples/streaming/wikipedia-clickstream/wikipedia-clickstream-table-realtime.json \
-exec
```

Clean up :

```shell
# Drop table
docker container exec -it pinot-controller \
/opt/pinot/bin/pinot-admin.sh ChangeTableState \
-tableName wikipedia_clickstream \
-state drop 

# Drop schema
docker container exec -it pinot-controller \
/opt/pinot/bin/pinot-admin.sh DeleteSchema \
-schemaName=wikipedia_clickstream \
-exec
```

## Insert data into Kafka

**Create a Kafka Topic**

```bash
docker container exec -it kafka \
kafka-topics \
--create \
--bootstrap-server localhost:9092 \
--partitions 1 \
--replication-factor 1 \
--topic wikipedia-clickstream
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

### Sample Queries

```sql
SELECT referrer,SUM(page_views) 
FROM wikipedia_clickstream 
WHERE article_name ='Aristotle'
GROUP BY referrer;

SELECT distinct(link_type)
FROM wikipedia_clickstream
WHERE article_name ='Aristotle';

-- Sketch
-- HLL Demo
SELECT count(distinct referrer) AS num_referrers
FROM wikipedia_clickstream 
WHERE article_name ='Aristotle';

SELECT distinctcounthll(referrer) AS num_referrers
FROM wikipedia_clickstream
WHERE article_name ='Aristotle';

-- Theta Sketch demo

SELECT distinct(referrer)
FROM wikipedia_clickstream
WHERE article_name ='Aristotle';


SELECT *
FROM wikipedia_clickstream
WHERE article_name ='Aristotle'
AND referrer='Lucid_dream';


-- 998753
SELECT count(referrer) AS num_referrers
FROM wikipedia_clickstream
WHERE link_type= 'link';

-- 34195
SELECT count(referrer) AS num_referrers
FROM wikipedia_clickstream
WHERE link_type= 'other';

-- How many referrers came from link type of `link` and not `other`
-- 433760
SELECT distinctCountThetaSketch(
referrer,
'nominalEntries=262144',
'link_type= ''link'' ',
'link_type= ''other'' ',
'SET_DIFF($1,$2)'
) 
FROM wikipedia_clickstream
WHERE link_type IN ('link','other');


-- For articles on Aristottle, how many referrers came from link type of `link` and not `other`
SELECT distinctCountThetaSketch(
referrer,
'nominalEntries=262144',
'link_type= ''link'' ',
'link_type= ''other'' ',
'SET_DIFF($1,$2)'
) 
FROM wikipedia_clickstream
WHERE article_name ='Aristotle'
AND link_type IN ('link','other');
```


### Demo

## Sqllab View

![Superset](../images/Superset_Sqllab.png)

## Sample Dashboard

![Superset Pinot Dashboard](../images/wikipedia-clickstream-dashboard.jpg)

## References

https://github.com/IBM/kafka-streaming-click-analysis

https://meta.wikimedia.org/wiki/Research:Wikipedia_clickstream
 
https://figshare.com/articles/dataset/Wikipedia_Clickstream/1305770

