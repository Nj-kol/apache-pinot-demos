## Supporting Components

This will bring up the following components :

1. Minio ( S3 compatible file system )
2. Zookeeper
3. Kafka 
4. Kafdrop ( UI for kafka )

## Usage

```shell
## Bring up components
docker-compose -f supporting.yaml up -d

## Teardown components
docker-compose -f supporting.yaml down
```

#### With Amazon CLI

```shell
export AWS_ACCESS_KEY_ID=minio
export AWS_SECRET_ACCESS_KEY=minio123

## Create a new bucket for Pinot
aws s3 mb \
s3://pinot \
--endpoint-url http://<your_ip>:9000

aws s3 ls \
--endpoint-url http://<your_ip>:9000
```

### Kafka Client

```shell
brew install librdkafka

pip install confluent-kafka
```

Produce some data 

```shell
## Producer
```


## UI(s)

- Minio (S3) : http://localhost:9001
- Kafdrop    : http://localhost:9100