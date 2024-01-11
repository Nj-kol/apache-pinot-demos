# Kafka Python

### Setup

```shell
brew install librdkafka

pip install confluent-kafka
```

## Producer 

### Batch Mode

Push sample JSON into Kafka topic, using the `producer.py` script from `clients` folder in the repo

```shell
python clients/producer.py \
--broker-list "192.168.0.152:9092" \
--topic transcripts \
--file-path "pinot/volumes/examples/streaming/transcript/data/transcripts.json"
```

### Interactive Mode

```shell
python clients/producer.py \
--broker-list "192.168.0.152:9092" \
--topic transcripts \
--interactive
```

## Client

```shell
python clients/consumer.py \
--bootstrap-server "192.168.0.152:9092" \
--topic transcripts \
--offset earliest
```



