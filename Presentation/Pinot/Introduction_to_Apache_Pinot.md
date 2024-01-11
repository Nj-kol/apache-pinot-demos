### What is it

Apache Pinot Realtime distributed OLAP datastore, designed to answer OLAP queries with low latency.

Pinot was first developed by LinkedIn in 2014 as an internal analytics infrastructure.  It originated from the demands to scale out OLAP systems to support low-latency real-time queries  on huge volume data. It was later open-sourced in 2015 and ***entered Apache Incubator in 2018***
### Who Uses it

![](who_uses_pinot.jpg)
### Architecture

![](pinot_architecture.jpg)
### Features
* A column-oriented database with various compression schemes such as Run Length, Fixed Bit Length
* Pluggable indexing technologies - Sorted Index, Bitmap Index, Inverted Index, Star-Tree Index
* Ability to optimize query/execution plan based on query and segment metadata
* Near real time ingestion from Kafka and batch ingestion from Hadoop
* SQL like language that supports selection, aggregation, filtering, group by, order by, distinct queries on fact data
* Support for multivalued fields
* Horizontally scalable and fault tolerant

![](pinot_feature_overview.jpg)

#### Hybrid Tables

Pinot supports the following types of tables:

|Type|Description|
|---|---|
|**Offline**|Offline tables ingest pre-built Pinot segments from external data stores and are generally used for batch ingestion.|
|**Real-time**|Real-time tables ingest data from streams (such as Kafka) and build segments from the consumed data.|
|**Hybrid**|Hybrid Pinot tables have both real-time as well as offline tables under the hood. By default, all tables in Pinot are hybrid.|

The user querying the database does not need to know the type of the table. They only need to specify the table name in the query.

e.g. regardless of whether we have an offline table `myTable_OFFLINE`, a real-time table `myTable_REALTIME`, or a hybrid table containing both of these, the query will be:

```sql
select count(*)
from myTable
```
#### Rich Indexing Support

![](pinot_index_1.jpg)

![](pinot_index_2.jpg)
##### Star-Tree Index

Unlike other index techniques which work on a single column, the star-tree index is built on multiple columns and utilizes pre-aggregated results to significantly reduce the number of values to be processed, resulting in improved query performance.

Use the **star-tree** index to utilize pre-aggregated documents to achieve both low query latencies and efficient use of storage space for aggregation and group-by queries.

![](pinot_index_3.jpg)
#### Support for Upserts

Pinot provides native support of upserts during real-time ingestion. There are scenarios where records need modifications, such as correcting a ride fare or updating a delivery status.

Partial upserts are convenient as you only need to specify the columns where values change, and you ignore the rest.

![](pinot_upsert.jpg)
#### Tiered Storage

Tiered storage allows you to split your server storage into multiple tiers. ***All the tiers can use different filesystem to hold the data***. Tiered storage can be used to optimise the cost to latency tradeoff in production Pinot systems.

![](pinot_tiered_storage_1.jpg)

![](pinot_tiered_storage_2.jpg)
#### Multistage Query Engine

Before Pinot 1.0, it did not support join. So, to do joins Presto/Trino had to be used.

The new multi-stage query engine (a.k.a V2 query engine) is designed to support more complex SQL semantics such as `JOIN`, `OVER` window, `MATCH_RECOGNIZE` and eventually, make Pinot support closer to full ANSI SQL semantics.

![](pinot_multi_stage_query_engine.jpg)

## References

https://www.youtube.com/watch?v=2_leJs8VzpQ

https://docs.pinot.apache.org/basics/indexing/star-tree-index

https://docs.pinot.apache.org/basics/architecture
