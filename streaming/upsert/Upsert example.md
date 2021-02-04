# Upsert example

## Upload your schema and table config

```bash
docker container exec -it pinot-controller bash

/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/pinot/samples/meetupRsvp/upsert_meetupRsvp_schema.json \
-tableConfigFile /opt/pinot/samples/meetupRsvp/upsert_meetupRsvp_realtime_table_config.json  \
-controllerHost pinot-controller \
-controllerPort 9000 \
-exec

# Drop the table
/opt/pinot/bin/pinot-admin.sh ChangeTableState -tableName meetupRsvp \
-state drop 
```

# Kafka

Now let's create a topic and post some message

**Create a Kafka Topic**

```bash
docker container exec -it kafka-standalone bash

kafka-topics.sh \
--create \
--zookeeper zookeeper-standalone:2181 \
--partitions 3 \
--replication-factor 1 \
--topic meetupRSVPEvents
```

Push sample JSON into Kafka topic, using the Kafka script from the Kafka download

```bash
docker container exec -it kafka-standalone bash

kafka-console-producer.sh \
--property parse.key=true \
--broker-list localhost:9092 \
--property key.separator=":" \
--topic meetupRSVPEvents
```


**Sample data**

```json
123:{"event_id":"123","event_name":"Biriyani festival","venue_name":"Acropolis Mall","event_time":1571900400000,"group_city":"Kolkata","group_country":"India","group_id":123,"group_name":"Food festival","group_lat":32.34,"group_lon":128.16,"mtime":1571900400000}
124:{"event_id":"124","event_name":"Block chain event","venue_name":"Taj West end","event_time":1571901400000,"group_city":"Bangalore","group_country":"India","group_id":124,"group_name":"tech festival","group_lat":12.34,"group_lon":148.16,"mtime":1571900400000}
```

**Add updated record**

```json
123:{"event_id":"123","event_name":"Biriyani festival","venue_name":"Acropolis Mall","event_time":1571900400000,"group_city":"Kolkata","group_country":"India","group_id":123,"group_name":"Food festival","group_lat":31.34,"group_lon":118.16,"mtime":1612151387000}
```

You'll notice that no new record has been added, instead the old record has been updated

## Disable the upsert during query via query option

To see the difference from the append-only table, you can use a query option `skipUpsert` to skip the upsert effect in the query result.

`select * from meetupRsvp option(skipUpsert=true) limit 10`
