# Prepare Wikipedia Clickstream data

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

```scala
import org.apache.spark.sql.Encoders
import org.apache.spark.sql.functions

val fileLoc = "/home/njkol/Sample_Data/wikipedia_clickstream/2017_01_en_clickstream.tsv"

case class Click(prev: String, curr: String, link: String, n: Long)

val clickSchema = Encoders.product[Click].schema

var clickDf = spark.read.format("csv")
.option("header", "true")
.option("delimiter", "\t")
.schema(clickSchema)
.load(fileLoc)

clickDf.createOrReplaceTempView("clickstream")      

// Do a random sampling on the data
val sampledDf = spark.sql("""
select prev as referrer, curr as article_name,n as page_views
from clickstream
where rand() <= 0.0001
distribute by rand()
sort by rand()
limit 10000
""")  

val randomTimestamp = functions.udf((s: Long) => s + scala.util.Random.nextInt(2000))

val sampledWithTimeDf = sampledDf.withColumn("timestampInEpoch", randomTimestamp(lit(1639137263000L)))

sampledWithTimeDf.show(false)
```

* The output looks like :

```sql
+----------------------------------------------+-----------------------------------------------+----------+----------------+
|referrer                                      |article_name                                   |page_views|timestampInEpoch|
+----------------------------------------------+-----------------------------------------------+----------+----------------+
|Quartz                                        |Shocked_quartz                                 |277       |1639137263279   |
|Ray_Rowe                                      |Raymond_Rowe                                   |43        |1639137264788   |
|Leighton_Baines                               |Ashley_Cole                                    |24        |1639137263412   |
|Colleen_Ballinger                             |Cinnamon_challenge                             |24        |1639137263435   |
|other-empty                                   |Peter_Hiscock                                  |18        |1639137263801   |
|other-empty                                   |Segmental_medullary_artery                     |158       |1639137263294   |
|List_of_House_episodes                        |Family_(House)                                 |120       |1639137263260   |
|other-empty                                   |Earl_Humphrey                                  |16        |1639137263580   |
|Inuit_culture                                 |Kudlik                                         |14        |1639137263316   |
|other-internal                                |Tamarama,_New_South_Wales                      |11        |1639137263983   |
|Texas_Outlaws_(football)                      |Eric_Bassey                                    |17        |1639137264370   |
|List_of_colleges_and_universities_in_Minnesota|Minnesota_State_Community_and_Technical_College|20        |1639137264560   |
|other-empty                                   |Marsaskala_F.C.                                |26        |1639137263549   |
|List_of_Louisiana_state_symbols               |Crayfish                                       |16        |1639137263674   |
|Sega_Channel                                  |Primal_Rage                                    |16        |1639137264529   |
|Tibouchina                                    |Tibouchina_oroensis                            |15        |1639137264706   |
|Chris_Harris_(journalist)                     |Clifton_College                                |107       |1639137263988   |
|Micronesian_Games                             |Palau                                          |11        |1639137263180   |
|La_Calavera_Catrina                           |Zinc                                           |22        |1639137263370   |
|House_Un-American_Activities_Committee        |William_Z._Foster                              |19        |1639137264992   |
+----------------------------------------------+-----------------------------------------------+----------+----------------+
```

Convert it into JSON :

```scala
sampledWithTimeDf.write.json("/home/njkol/Sample_Data/wikipedia_clickstream/json")
```

Rename the JSON file generated to something more meaningful

```bash
mv part-00000-11c0facc-8bae-411d-b366-aaf08fc43112-c000.json clickstream.json
```

Sample JSON data :

```json
{"referrer":"Quartz","article_name":"Shocked_quartz","page_views":277,"timestampInEpoch":1639137264714}
{"referrer":"Ray_Rowe","article_name":"Raymond_Rowe","page_views":43,"timestampInEpoch":1639137264000}
{"referrer":"Leighton_Baines","article_name":"Ashley_Cole","page_views":24,"timestampInEpoch":1639137264153}
{"referrer":"Colleen_Ballinger","article_name":"Cinnamon_challenge","page_views":24,"timestampInEpoch":1639137263647}
{"referrer":"other-empty","article_name":"Peter_Hiscock","page_views":18,"timestampInEpoch":1639137263238}
```