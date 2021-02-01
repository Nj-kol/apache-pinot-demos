
# Stream Ingestion Example

## Create a schema

Schema is used to define the columns and data types of the Pinot table :

`${HOME}/volumes/pinot/samples/transcript/transcript-schema.json`

```json
{
  "schemaName": "transcript",
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
    "name": "timestampInEpoch",
    "dataType": "LONG",
    "format" : "1:MILLISECONDS:EPOCH",
    "granularity": "1:MILLISECONDS"
  }]
}
```

## Creating a table config

* Similar to the offline table config, we will create a realtime table config for the sample.

* Here's the realtime table config for the transcript table. 

`${HOME}/volumes/pinot/samples/transcript/transcript-table-realtime.json`

```json
{
  "tableName": "transcript",
  "tableType": "REALTIME",
  "segmentsConfig": {
    "timeColumnName": "timestampInEpoch",
    "timeType": "MILLISECONDS",
    "schemaName": "transcript",
    "replicasPerPartition": "1"
  },
  "tenants": {},
  "tableIndexConfig": {
    "loadMode": "MMAP",
    "streamConfigs": {
      "streamType": "kafka",
      "realtime.segment.flush.threshold.size": "0",
      "realtime.segment.flush.threshold.time": "1h",
      "realtime.segment.flush.desired.size": "50M",
      "stream.kafka.consumer.type": "lowlevel",
      "stream.kafka.broker.list": "LM0001680:39092",
      "stream.kafka.topic.name": "transcript-realtime",
      "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
      "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
      "stream.kafka.consumer.prop.auto.offset.reset": "smallest"
    }
  },
  "metadata": {
    "customConfigs": {}
  }
}
```

## Insert data into Kafka

```bash
docker container exec -it kafka-standalone bash

# Create a Kafka Topic

kafka-topics.sh \
--create \
--zookeeper zookeeper-standalone:2181 \
--partitions 3 \
--replication-factor 1 \
--topic transcript-realtime
```

**Loading sample data into stream***

```json
{"studentID":205,"firstName":"Natalie","lastName":"Jones","gender":"Female","subject":"Maths","score":3.8,"timestampInEpoch":1571900400000}
{"studentID":205,"firstName":"Natalie","lastName":"Jones","gender":"Female","subject":"History","score":3.5,"timestampInEpoch":1571900400000}
{"studentID":207,"firstName":"Bob","lastName":"Lewis","gender":"Male","subject":"Maths","score":3.2,"timestampInEpoch":1571900400000}
{"studentID":207,"firstName":"Bob","lastName":"Lewis","gender":"Male","subject":"Chemistry","score":3.6,"timestampInEpoch":1572418800000}
{"studentID":209,"firstName":"Jane","lastName":"Doe","gender":"Female","subject":"Geography","score":3.8,"timestampInEpoch":1572505200000}
{"studentID":209,"firstName":"Jane","lastName":"Doe","gender":"Female","subject":"English","score":3.5,"timestampInEpoch":1572505200000}
{"studentID":209,"firstName":"Jane","lastName":"Doe","gender":"Female","subject":"Maths","score":3.2,"timestampInEpoch":1572678000000}
{"studentID":209,"firstName":"Jane","lastName":"Doe","gender":"Female","subject":"Physics","score":3.6,"timestampInEpoch":1572678000000}
{"studentID":211,"firstName":"John","lastName":"Doe","gender":"Male","subject":"Maths","score":3.8,"timestampInEpoch":1572678000000}
{"studentID":211,"firstName":"John","lastName":"Doe","gender":"Male","subject":"English","score":3.5,"timestampInEpoch":1572678000000}
{"studentID":211,"firstName":"John","lastName":"Doe","gender":"Male","subject":"History","score":3.2,"timestampInEpoch":1572854400000}
{"studentID":212,"firstName":"Nick","lastName":"Young","gender":"Male","subject":"History","score":3.6,"timestampInEpoch":1572854400000}
```

Push sample JSON into Kafka topic, using the Kafka script from the Kafka download

```bash
docker container exec -it kafka-standalone bash

mkdir /tmp/data

cd /tmp/data

vi transcript.json # copy & paste the above data 

kafka-console-producer.sh \
--broker-list localhost:9092 \
--topic transcript-realtime < /tmp/data/transcript.json
```

## Uploading your schema and table config

* Now that we have our table and schema, let's upload them to the cluster. 
* As soon as the realtime table is created, it will begin ingesting from the Kafka topic
* The command needs to be executed on the controlled node

```bash
docker container exec -it pinot-controller bash

/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/pinot/samples/transcript/transcript-schema.json \
-tableConfigFile /opt/pinot/samples/transcript/transcript-table-realtime.json \
-controllerHost pinot-controller \
-controllerPort 9000 \
-exec

# Drop table
/opt/pinot/bin/pinot-admin.sh ChangeTableState \
-tableName transcript \
-state drop 
```

