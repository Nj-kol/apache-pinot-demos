# Apache Pinot with SuperSet : Wikipedia Clickstream analytics with Star Tree index

## Software Stack setup

**Bring up Ancillary components**

This will bring up S3 and Redis :

```shell
docker-compose -f ancillary/ancillary-components.yml up -d
```

**Bring up Pinot**

Change IP in the following files :

In `pinot/volumes/controller/pinot-controller.conf`, change :

```
pinot.controller.storage.factory.s3.endpoint=http://<YOUR_MACHINE_IP>:9000
```

In `pinot/volumes/server/pinot-server.conf` , change :

```
pinot.server.storage.factory.s3.endpoint=http://<YOUR_MACHINE_IP>:9000
```

Then, bring up the stack :

```shell
docker-compose -f ancillary/ancillary-components.yml up -d
```

This will bring up  :

1. Zookeeper
2. Kafka 
3. Kafdrop ( UI for kafka )
4. Pinot Components
   - Pinot Controller
   - Pinot Broker
   - Pinot Server

**Bring up Superset**

To setup and run SuperSet and connect to pinot, some initial setup has to be done. Please follow the instructions under `superset-pinot/README.md`

### All UIs

**Minio S3**
- URL : http://localhost:9001/browser/
- u/p : minio/minio123

**Redis**
- URL : http://localhost:8001/redis-stack/browser

**Pinot & Kafdrop**
- Pinot UI   : http://localhost:9210/#/query
- Kafdrop    : http://localhost:9100

**Superset**
- UI : http://localhost:30092/login
- u/p: [admin/admin]

## Wikipedia Clickstream Analytics Demo

- Prepare sample data set : `wikipedia-clickstream-analysis/spark/Clickstream_Data_Preparation.md`
- Prepare Redis : `wikipedia-clickstream-analysis/Redis.md`
- Start Spark job : `wikipedia-clickstream-analysis/spark/Spark Pipeline.md`
- Create table & Start Ingestion to Pinot :

![Superset Pinot Dashboard](ingestion-demos/streaming/images/wikipedia-clickstream-dashboard.jpg)

## References

https://docs.pinot.apache.org/basics/getting-started

https://docs.pinot.apache.org/basics/getting-started/pushing-your-data-to-pinot

https://docs.pinot.apache.org/basics/getting-started/pushing-your-streaming-data-to-pinot