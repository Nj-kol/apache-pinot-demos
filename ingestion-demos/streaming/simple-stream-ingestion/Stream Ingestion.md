# Simple Stream Ingestion Example

## Create a schema
* Schema is used to define the columns and data types of the Pinot table
* In the file : `pinot/volumes/examples/streaming/transcript/transcript-realtime-schema.json`

```json
{
  "schemaName": "transcript-realtime",
  "dimensionFieldSpecs": [
    {
      "name": "studentID",
      "dataType": "INT"
    },
    {
      "name": "firstName",
      "dataType": "STRING"
    },
    {
      "name": "lastName",
      "dataType": "STRING"
    },
    {
      "name": "gender",
      "dataType": "STRING"
    },
    {
      "name": "subject",
      "dataType": "STRING"
    }
  ],
  "metricFieldSpecs": [
    {
      "name": "score",
      "dataType": "FLOAT"
    }
  ],
  "dateTimeFieldSpecs": [{
    "name": "timestamp",
    "dataType": "LONG",
    "format" : "1:MILLISECONDS:EPOCH",
    "granularity": "1:MILLISECONDS"
  }]
}
```

## Creating a table config
* Similar to the offline table config, we will create a realtime table config for the sample
* In the file : `pinot/volumes/examples/streaming/transcript/transcript-table-realtime.json`

```json
{
  "tableName": "transcript-realtime",
  "tableType": "REALTIME",
  "segmentsConfig": {
    "timeColumnName": "timestamp",
    "timeType": "MILLISECONDS",
    "schemaName": "transcript-realtime",
    "replicasPerPartition": "1"
  },
  "tenants": {},
  "tableIndexConfig": {
      "bloomFilterColumns":[
         "studentID"
      ],
      "noDictionaryColumns":[
         "firstName",
         "lastName"
      ],
      "invertedIndexColumns":[
         "subject"
      ],
      "sortedColumn":[
         "gender"
      ],
      "loadMode": "MMAP",
  },
  "metadata": {
    "customConfigs": {}
  },
  "ingestionConfig": {
    "streamIngestionConfig": {
        "streamConfigMaps": [
          {
            "realtime.segment.flush.threshold.rows": "0",
            "stream.kafka.decoder.prop.format": "JSON",
            "key.serializer": "org.apache.kafka.common.serialization.ByteArraySerializer",
            "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
            "streamType": "kafka",
            "value.serializer": "org.apache.kafka.common.serialization.ByteArraySerializer",
            "stream.kafka.consumer.type": "LOWLEVEL",
            "realtime.segment.flush.threshold.segment.rows": "50000",
            "stream.kafka.broker.list": "<some_ip>:9092",
            "realtime.segment.flush.threshold.time": "3600000",
            "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
            "stream.kafka.consumer.prop.auto.offset.reset": "smallest",
            "stream.kafka.topic.name": "transcripts"
          }
        ]
      },
      "transformConfigs": [],
      "continueOnError": true,
      "rowTimeValueCheck": true,
      "segmentTimeValueCheck": false
    },
    "isDimTable": false
}
```

## Uploading your schema and table config

* Now that we have our table and schema, let's upload them to the cluster. 
* As soon as the realtime table is created, it will begin ingesting from the Kafka topic
* The command needs to be executed on the controller node

```bash
docker container exec -it pinot-controller \
/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/examples/streaming/transcript/transcript-realtime-schema.json \
-tableConfigFile /opt/examples/streaming/transcript/transcript-table-realtime.json \
-exec

# Drop table
/opt/pinot/bin/pinot-admin.sh ChangeTableState \
-tableName transcript \
-state drop 
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
--topic transcript
```

**Loading sample data into stream**

Push sample JSON into Kafka topic, using the `producer.py` script from `clients` folder in the repo

```shell
python clients/producer.py \
--broker-list "localhost:9092" \
--topic transcript \
--file-path "pinot/volumes/examples/streaming/transcript/data/transcripts.json"
```

## See data

**Pinot**

**Superset**