# Upsert example

## Upload your schema and table config

```bash
docker container exec -it pinot-controller \
/opt/pinot/bin/pinot-admin.sh AddTable \
-schemaFile /opt/examples/streaming/upsert/upsertPartialMeetupRsvp_schema.json \
-tableConfigFile /opt/examples/streaming/upsert/upsertPartialMeetupRsvp_realtime_table_config.json \
-exec


# Drop the table if exists
/opt/pinot/bin/pinot-admin.sh ChangeTableState -tableName meetupRsvp \
-state drop 
```

Response from server :

```json
{
    "unrecognizedProperties": {},
    "status": "TableConfigs upsertPartialMeetupRsvp successfully added"
}
```

## Kafka

Now let's create a topic and post some message

### Create a Kafka Topic

```bash
docker container exec -it kafka \
kafka-topics \
--create \
--bootstrap-server localhost:9092 \
--partitions 1 \
--replication-factor 1 \
--topic upsertPartialMeetupRSVPEvents
```

### Push Data

Push sample JSON into Kafka topic, using the Kafka script from the Kafka download

```bash
docker container exec -it kafka \
kafka-console-producer \
--property parse.key=true \
--broker-list localhost:9092 \
--property key.separator=":" \
--topic upsertPartialMeetupRSVPEvents
```

**Sample data**

```json
123:{"event_id":"123","event_name":"Biriyani festival","venue_name":"Acropolis Mall","event_time":1571900400000,"group_city":"Kolkata","group_country":"India","group_id":123,"group_name":"Food festival","group_lat":32.34,"group_lon":128.16,"mtime":1571900400000}
124:{"event_id":"124","event_name":"Block chain event","venue_name":"Taj West end","event_time":1571901400000,"group_city":"Bangalore","group_country":"India","group_id":124,"group_name":"tech festival","group_lat":12.34,"group_lon":148.16,"mtime":1571900400000}
```

**Add updated record with different lattitude and longitude**

```json
123:{"event_id":"123","event_name":"Biriyani festival","venue_name":"Acropolis Mall","event_time":1571900400000,"group_city":"Kolkata","group_country":"India","group_id":123,"group_name":"Food festival","group_lat":31.34,"group_lon":118.16,"mtime":1612151387000}
```

You'll notice that no new record has been added, instead the old record has been updated

```shell
## Old value
123	Biriyani festival	2019-10-24 07:00:00.0	Kolkata	India	123	32.34	128.16	Food festival	804060051eb851eb8540402b851eb851ec	2019-10-24 07:00:00.0	0	Acropolis Mall

## New Value
123	Biriyani festival	2019-10-24 07:00:00.0	Kolkata	India	123	31.34	118.16	Food festival	80405d8a3d70a3d70a403f570a3d70a3d7	2021-02-01 03:49:47.0	0	Acropolis Mall,Acropolis Mall
```

## Disable the upsert during query via query option

To see the difference from the append-only table, you can use a query option `skipUpsert` to skip the upsert effect in the query result.

You'll see all three records :

```sql
select * from upsertPartialMeetupRsvp limit 10 option(skipUpsert=true);

event_id	event_name	event_time	group_city	group_country	group_id	group_lat	group_lon	group_name	location	mtime	rsvp_count	venue_name

123	Biriyani festival	2019-10-24 07:00:00.0	Kolkata	India	123	32.34	128.16	Food festival	804060051eb851eb8540402b851eb851ec	2019-10-24 07:00:00.0	0	Acropolis Mall
124	Block chain event	2019-10-24 07:16:40.0	Bangalore	India	124	12.34	148.16	tech festival	804062851eb851eb854028ae147ae147ae	2019-10-24 07:00:00.0	0	Taj West end
123	Biriyani festival	2019-10-24 07:00:00.0	Kolkata	India	123	31.34	118.16	Food festival	80405d8a3d70a3d70a403f570a3d70a3d7	2021-02-01 03:49:47.0	0	Acropolis Mall,Acropolis Mall
```



