
# Batch Ingestion

## Preparing your data

**Host machine**

```bash
mkdir -p ${HOME}/volumes/pinot/server/data/rawdata
```

If you don't have sample data, you can use this sample CSV

( `${HOME}/volumes/pinot/server/data/rawdata/transcript.csv` )

```csv
studentID,firstName,lastName,gender,subject,score,timestampInEpoch
200,Lucy,Smith,Female,Maths,3.8,1570863600000
200,Lucy,Smith,Female,English,3.5,1571036400000
201,Bob,King,Male,Maths,3.2,1571900400000
202,Nick,Young,Male,Physics,3.6,1572418800000
```

## Creating a schema

Schema is used to define the columns and data types of the Pinot table :

`${HOME}/volumes/pinot/samples/transcript/transcript-schema.json`

```json
{
  "schemaName": "transcript",
  "dimensionFieldSpecs": [
    {
      "name": "studentID",
      "dataType": "INT"
    },
    {
      "name": "firstName",
      "dataType": "STRING"
    },
    {
      "name": "lastName",
      "dataType": "STRING"
    },
    {
      "name": "gender",
      "dataType": "STRING"
    },
    {
      "name": "subject",
      "dataType": "STRING"
    }
  ],
  "metricFieldSpecs": [
    {
      "name": "score",
      "dataType": "FLOAT"
    }
  ],
  "dateTimeFieldSpecs": [{
    "name": "timestampInEpoch",
    "dataType": "LONG",
    "format" : "1:MILLISECONDS:EPOCH",
    "granularity": "1:MILLISECONDS"
  }]
}
```

## Creating a table config

* A table config is used to define the config related to the Pinot table. 

Here's the table config for the sample CSV file. You can use this as a reference to build your own table config. Simply edit the `tableName` and `schemaName`

`${HOME}/volumes/pinot/samples/transcript/transcript-table-offline.json`


```json
{
  "tableName": "transcript",
  "segmentsConfig" : {
    "timeColumnName": "timestampInEpoch",
    "timeType": "MILLISECONDS",
    "replication" : "1",
    "schemaName" : "transcript"
  },
  "tableIndexConfig" : {
    "invertedIndexColumns" : [],
    "loadMode"  : "MMAP"
  },
  "tenants": {},
  "tableType":"OFFLINE",
  "metadata": {}
}
```

## Uploading your table config and schema

```bash
docker container exec -it pinot-controller bash

/opt/pinot/bin/pinot-admin.sh AddTable \
-tableConfigFile /opt/pinot/samples/transcript/transcript-table-offline.json \
-schemaFile /opt/pinot/samples/transcript/transcript-schema.json -exec
```

* Response :

```json
{"status":"Table transcript_OFFLINE succesfully added"}
```

## Creating a segment

* A Pinot table's data is stored as Pinot segments.

* ***To generate a segment, we need to first create a job spec yaml file***

* JobSpec yaml file has all the information regarding :
  - data format
  - input data location 
  - and pinot cluster coordinates.

  You can just copy over this job spec file. 

  `${HOME}/volumes/pinot/samples/transcript/batch-job-spec.yml`

```yaml
executionFrameworkSpec:
  name: 'standalone'
  segmentGenerationJobRunnerClassName: 'org.apache.pinot.plugin.ingestion.batch.standalone.SegmentGenerationJobRunner'
  segmentTarPushJobRunnerClassName: 'org.apache.pinot.plugin.ingestion.batch.standalone.SegmentTarPushJobRunner'
  segmentUriPushJobRunnerClassName: 'org.apache.pinot.plugin.ingestion.batch.standalone.SegmentUriPushJobRunner'
jobType: SegmentCreationAndTarPush
inputDirURI: '/opt/pinot/samples/transcript/rawdata/'
includeFileNamePattern: 'glob:**/*.csv'
outputDirURI: '/opt/segments'
overwriteOutput: true
pinotFSSpecs:
  - scheme: file
    className: org.apache.pinot.spi.filesystem.LocalPinotFS
recordReaderSpec:
  dataFormat: 'csv'
  className: 'org.apache.pinot.plugin.inputformat.csv.CSVRecordReader'
  configClassName: 'org.apache.pinot.plugin.inputformat.csv.CSVRecordReaderConfig'
tableSpec:
  tableName: 'transcript'
  schemaURI: 'http://pinot-controller:9000/tables/transcript/schema'
  tableConfigURI: 'http://pinot-controller:9000/tables/transcript'
pinotClusterSpecs:
  - controllerURI: 'http://pinot-controller:9000'
```

Note : The path specified on the job spec are local to the controller (and not the server)

  If you're using your own data, be sure to :

  1) replace `transcript` with your table name 
  2) set the right `recordReaderSpec`

* Use the following command to generate a segment and upload it

```bash
docker container exec -it pinot-controller bash

/opt/pinot/bin/pinot-admin.sh LaunchDataIngestionJob \
-jobSpecFile /opt/pinot/samples/transcript/batch-job-spec.yml 
```

* Response :

```json
{"status":"Successfully uploaded segment: transcript_OFFLINE_1570863600000_1572418800000_0 of table: transcript"}
```

* In this case, the segment has been created on the local file system under : `/tmp/pinot-quick-start/segments/`

  `transcript_OFFLINE_1570863600000_1572418800000_0.tar.gz`

References
==========
https://docs.pinot.apache.org/basics/getting-started/pushing-your-data-to-pinot