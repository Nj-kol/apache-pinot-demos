
# Stream Ingestion with Upsert

* Pinot provides native support of upsert during the real-time ingestion (v0.6.0+).

* There are scenarios that the records need modifications, such as :
   - correcting a ride fare 
   - updating a delivery status

* To enable upsert on a Pinot table, there are a couple of configurations to make on :
   - the table configurations 
   - as well as on the input stream.

## Define the primary key in the schema

* To update a record, a primary key is needed to uniquely identify the record.

* To define a primary key, add the field `primaryKeyColumns` to the schema definition.

upsert_meetupRsvp_schema.json

```json
{
    "primaryKeyColumns": ["event_id"]
}
```

* Note this field expects a list of columns, as ***the primary key can be composite***

* When two records of the same primary key are ingested, the record with the greater event time
  (as defined by the time column) is used.

## Partition the input stream by the primary key

* An important requirement for the Pinot upsert table is to partition the input stream by the primary key. 

  For Kafka messages, this means ***the producer shall set the key in the send API***

  If the original stream is not partitioned, then a streaming processing job (e.g. Flink)
  is needd to shuffle and repartition the input stream into a partitioned one for Pinot's ingestion.

# Enable upsert in the table configurations

There are a few configurations needed in the table configurations to enable upsert.

## Upsert mode

* For append-only tables, the upsert mode defaults to NONE. 

* To enable the upsert, set the mode to FULL for the full update. In the future, Pinot plans to add 
  the partial update support. For example:

```json
{
  "upsertConfig": {
    "mode": "FULL"
  }
}
```

## Use strictReplicaGroup for routing

* The upsert Pinot table can use only the low-level consumer for the input streams. 

* As a result, it uses the partitioned replica-group assignment for the segments.

* Moreover,upsert poses the additional requirement that ***all segments of the same partition must be served 
  from the same server to ensure the data consistency across the segments.***

* Accordingly, it requires to use `strictReplicaGroup` as the routing strategy.
  To use that, configure `instanceSelectorType` in Routing as the following

```json
{
  "routing": {
    "instanceSelectorType": "strictReplicaGroup"
  }
}
```

**Example**

```json
{
  "tableName": "meetupRsvp",
  "tableType": "REALTIME",
  "segmentsConfig": {
    "timeColumnName": "mtime",
    "timeType": "MILLISECONDS",
    "retentionTimeUnit": "DAYS",
    "retentionTimeValue": "1",
    "segmentPushType": "APPEND",
    "segmentAssignmentStrategy": "BalanceNumSegmentAssignmentStrategy",
    "schemaName": "meetupRsvp",
    "replicasPerPartition": "1"
  },
  "tenants": {},
  "tableIndexConfig": {
    "loadMode": "MMAP",
    "streamConfigs": {
      "streamType": "kafka",
      "stream.kafka.consumer.type": "lowLevel",
      "stream.kafka.topic.name": "meetupRSVPEvents",
      "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
      "stream.kafka.hlc.zk.connect.string": "localhost:2191/kafka",
      "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
      "stream.kafka.zk.broker.url": "localhost:2191/kafka",
      "stream.kafka.broker.list": "localhost:19092",
      "realtime.segment.flush.threshold.size": 30,
      "realtime.segment.flush.threshold.rows": 30
    }
  },
  "metadata": {
    "customConfigs": {}
  },
  "routing": {
    "instanceSelectorType": "strictReplicaGroup"
  },
  "upsertConfig": {
    "mode": "FULL"
  }
}
```

## Disable the upsert during query via query option

To see the difference from the append-only table, you can use a query option `skipUpsert` to skip the upsert effect in the query result.

`select * from meetupRsvp option(skipUpsert=true) limit 10`


# Limitations

There are some limitations for the upsert Pinot tables.

* First, the high-level consumer is not allowed for the input stream ingestion, which means 
  `stream.kafka.consumer.type` must be `lowLevel`

* Second, the ***star-tree index cannot be used for indexing***, as the star-tree index performs pre-aggregation 
  during the ingestion

References
==========
https://docs.pinot.apache.org/basics/data-import/upsert#example