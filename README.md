# Apache Pinot Demo
# Case Study

* Once an offline segment is pushed to cover a recent time period :
  - the brokers automatically switch to using the offline table for segments for that time period
  - and use realtime table only for data not available in offline table

## Before batch test

200,Lucy,Smith,Female,Maths,3.8,1570863600000 ( offline data )

1570863600000 - Saturday, 12 October 2019 07:00:00
1570863510000 - Saturday, 12 October 2019 06:58:30

**Add a record with past timestamp in kafka**

{"studentID":200,"firstName":"Lucy","lastName":"Smith","gender":"Female","subject":"Maths","score":3.6,"timestampInEpoch":1570863510000}

select * from transcript where studentID=200

You'll notice that only the record in offline table is being shown ( i.e. for 1570863600000 )

## After batch test

200,Lucy,Smith,Female,English,3.5,1571036400000

1571036400000 - Monday, 14 October 2019 07:00:00
1612151387000 - Monday, 1 February 2021 03:49:47

**Add a record with latest timestamp in kafka**

{"studentID":200,"firstName":"Lucy","lastName":"Smith","gender":"Female","subject":"English","score":4.2,"timestampInEpoch":1612151387000}

select * from transcript where studentID=200

You'll notice that a new record is being shown ( i.e. for 1612151387000 )

# Notes

* The tenants section in both the OFFLINE and realtime tables must be same, otherwise HYBRID table
  would not be formed

## References

https://docs.pinot.apache.org/basics/getting-started

https://docs.pinot.apache.org/basics/getting-started/pushing-your-data-to-pinot

https://docs.pinot.apache.org/basics/getting-started/pushing-your-streaming-data-to-pinot