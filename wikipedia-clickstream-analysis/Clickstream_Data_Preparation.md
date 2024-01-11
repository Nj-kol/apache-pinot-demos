# Prepare Wikipedia Clickstream data

### About the dataset

This project contains data sets containing counts of (referer, resource) pairs extracted from the request logs of Wikipedia.

A referer is an HTTP header field that identifies the address of the webpage that linked to the resource being requested. The data shows how people get to a Wikipedia article and what links they click on. In other words, it gives a weighted network of articles, where each edge weight corresponds to how often people navigate from one page to another. For more information and documentation, see the link in the references section below.

```csv
prev            curr    type    n
Greek_language  Aristotle       link    59
Exaggeration    Aristotle       link    11
Euclid          Aristotle       link    39
Lucid_dream     Aristotle       link    36
Oceanography    Aristotle       link    19
Thespis         Aristotle       link    34
Animal_rights   Aristotle       link    20
History_of_economic_thought     Aristotle       link    33
Greek_words_for_love    Aristotle       link    14
```

A sample data set is already present undein the repo : `ingestion-demos/streaming/clickstream-analytics/data/clickstream.json`

The process used to derive the refined data set is demostrated below.

## Download and extract data

You can download the dataset from : https://figshare.com/articles/dataset/Wikipedia_Clickstream/1305770

Or through CLI :

```shell
wget https://figshare.com/ndownloader/files/7563832
```

Then extract the data locally :

```bash
gzip -d 2017_01_en_clickstream.tsv.gz
```

## Prepare data in Spark

The dataset is large, so we will only take a sample of the data and also convert it into JSON so that it can be fed to a Kafka topic

```shell
spark-shell \
--driver-memory 2G \
--executor-memory 4G \
--executor-cores 4
```

```scala
import org.apache.spark.sql.Encoders
import org.apache.spark.sql.functions

val fileLoc = "/home/njkol/Sample_Data/wikipedia_clickstream/2017_01_en_clickstream.tsv"

case class Click(referrer: String, article_name: String, link_type: String, page_views: Long)

val clickSchema = Encoders.product[Click].schema

var clickDf = spark.read.format("csv")
.option("header", "true")
.option("delimiter", "\t")
.schema(clickSchema)
.load(fileLoc)
.cache

clickDf.createOrReplaceTempView("clickstream")      

val randomTimestamp = functions.udf((s: Long) => s + scala.util.Random.nextInt(20000))

val tsDF = clickDf.withColumn("timestampInEpoch", randomTimestamp(lit(1639137263000L)))

// Convert to JSON
tsDF.repartition(128).write.json("/home/njkol/Sample_Data/wikipedia_clickstream/json3")

tsDF.show(false)
```

* The output looks like :

```sql
+---------------------------------------------+------------+---------+----------+----------------+
|referrer                                     |article_name|link_type|page_views|timestampInEpoch|
+---------------------------------------------+------------+---------+----------+----------------+
|Greek_language                               |Aristotle   |link     |59        |1639137274729   |
|Exaggeration                                 |Aristotle   |link     |11        |1639137272906   |
|Euclid                                       |Aristotle   |link     |39        |1639137276825   |
|Lucid_dream                                  |Aristotle   |link     |36        |1639137279868   |
|Oceanography                                 |Aristotle   |link     |19        |1639137269107   |
|Thespis                                      |Aristotle   |link     |34        |1639137272297   |
|Animal_rights                                |Aristotle   |link     |20        |1639137269315   |
|History_of_economic_thought                  |Aristotle   |link     |33        |1639137270201   |
|Greek_words_for_love                         |Aristotle   |link     |14        |1639137277331   |
|Praxis_(process)                             |Aristotle   |link     |19        |1639137282589   |
|Ibn_al-Haytham                               |Aristotle   |link     |53        |1639137270175   |
|Prima_materia                                |Aristotle   |link     |14        |1639137267531   |
|Foreign_policy                               |Aristotle   |link     |11        |1639137270806   |
|Homer                                        |Aristotle   |link     |42        |1639137265931   |
|Despotism                                    |Aristotle   |link     |25        |1639137277258   |
|Georg_Wilhelm_Friedrich_Hegel                |Aristotle   |link     |67        |1639137282207   |
|Individualism                                |Aristotle   |link     |19        |1639137282788   |
|Hamartia                                     |Aristotle   |link     |16        |1639137267912   |
|Hush_(comics)                                |Aristotle   |link     |28        |1639137275773   |
|List_of_philosophers_born_in_the_centuries_BC|Aristotle   |link     |25        |1639137267395   |
+---------------------------------------------+------------+---------+----------+----------------+
```

Sample JSON data on disk :

```json
{"referrer":"Quartz","article_name":"Shocked_quartz","page_views":277,"timestampInEpoch":1639137264714}
{"referrer":"Ray_Rowe","article_name":"Raymond_Rowe","page_views":43,"timestampInEpoch":1639137264000}
{"referrer":"Leighton_Baines","article_name":"Ashley_Cole","page_views":24,"timestampInEpoch":1639137264153}
{"referrer":"Colleen_Ballinger","article_name":"Cinnamon_challenge","page_views":24,"timestampInEpoch":1639137263647}
{"referrer":"other-empty","article_name":"Peter_Hiscock","page_views":18,"timestampInEpoch":1639137263238}
```
