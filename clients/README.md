**Loading sample data into stream**

Push sample JSON into Kafka topic, using the `producer.py` script from `clients` folder in the repo

```shell
python clients/producer.py \
--broker-list "localhost:9092" \
--topic wikipedia-clickstream \
--file-path "ingestion-demos/streaming/clickstream-analytics/data/clickstream.json"
```