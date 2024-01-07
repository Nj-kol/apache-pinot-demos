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

1. Zookeeper
2. Kafka 
3. Kafdrop ( UI for kafka )
4. Pinot Components
   - Pinot Controller
   - Pinot Broker
   - Pinot Server

## UI(s)
- Pinot UI   : http://localhost:9210/#/query
- Kafdrop    : http://localhost:9100

## References

https://docs.pinot.apache.org/basics/getting-started/running-pinot-in-docker