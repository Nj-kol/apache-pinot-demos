## Architecture for Demo

![](images/architectue_for_demo.png)
### Data flow
- Raw data flows to the first Kafka topic from source system
	- This topic would typically have a longer retention period to aid re-processing
	- There would be periodic jobs writing snapshots of this data to a longer term store like data lake for offline/batch analysis
- The stream processing engine (Spark here)
	- Reads the incoming event data from (  ***Raw layer** )
	- Does a lookup in a fast in-memory store  ( Redis ) to get the rules how to process/filter this event. In this case we have an in-memory bloom filter ( a sketch ) that helps us filter the incoming stream dropping unwanted records
	- Writes the final result to a another Kafka topic ( ***Transformed layer** )
- Finally a pinot real-time job, reads the filtered and modelled data from the ***transformed layer*** and makes data immediately queryable
	- It periodically flushes data to disk
	- It creates specialized indexes ( inverted, startree, bloomfilter etc. ) for columns specified
	- Moves data to a deep store ( S3 ) periodically facilitating Tiered storage