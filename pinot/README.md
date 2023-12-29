## Pinot with S3 Deep Storage

Here we will be spinning up a Pinot Cluster with S3 as a Deep store

### Spin Up Components 

```bash
## Start all components
docker-compose -f pinot-standalone.yml up -d

## Stop all components
docker-compose -f pinot-standalone.yml down
```

This will bring up the following components :

1. Minio ( S3 compatible file system )
2. Zookeeper
3. Kafka 
4. Kafdrop ( UI for kafka )
5. Pinot Components
   - Pinot Controller
   - Pinot Broker
   - Pinot Server

## UI(s)

- Pinot UI   : http://localhost:9210/#/query
- Minio (S3) : http://localhost:9001
- Kafdrop    : http://localhost:9100

## References

https://docs.pinot.apache.org/basics/getting-started/running-pinot-in-docker