
## HLL Demo

```shell
spark-shell --driver-memory 2G --executor-memory 4G --executor-cores 8
```

```scala
import org.apache.spark.sql.Encoders
import org.apache.spark.sql.functions

val fileLoc = "/home/njkol/Sample_Data/wikipedia_clickstream/2017_01_en_clickstream.tsv"

case class Click(referrer: String, article_name: String, link: String, page_views: Long)

val clickSchema = Encoders.product[Click].schema

var df = spark.read.format("csv")
.option("header", "true")
.option("delimiter", "\t")
.schema(clickSchema)
.load(fileLoc)

val clickDf = df.repartition($"article_name").cache

clickDf.createOrReplaceTempView("clickstream")    

clickDf.show

spark.sql("""
select count( distinct article_name ) as unique_article_name
from clickstream
""").show

+-------------------+
|unique_article_name|
+-------------------+
|            4363200|
+-------------------+

// the 'hll_sketch_agg' aggregate function consumes the values
// and produces a sketch, then the enclosing 'hll_sketch_estimate'
// returns the approximate count.

spark.sql("""
SELECT hll_sketch_estimate(hll_sketch_agg(article_name)) AS unique_article_name
from clickstream
""").show

+-------------------+
|unique_article_name|
+-------------------+
|            4311616|
+-------------------+

spark.sql("""
select distinct link as unique_link
from clickstream
""").show

+-----------+
|unique_link|
+-----------+
|       link|
|      other|
|   external|
|       NULL|
+-----------+

spark.sql("""
SELECT hll_sketch_estimate(hll_sketch_agg(link)) AS unique_article_name
from clickstream
""").show

spark.sql("""
select article_name,count( distinct referrer ) as page_sources
from clickstream
group by article_name
sort by page_sources desc
limit 10
""").show

+-----------------+------------+
|     article_name|page_sources|
+-----------------+------------+
|     Hyphen-minus|      138708|
|           Russia|        1598|
|      World_War_I|        1502|
|           Sweden|         907|
|   Tamil_language|         823|
|      North_Korea|         772|
|         Napoleon|         757|
|             Urdu|         745|
|Holy_Roman_Empire|         719|
|          Playboy|         695|
+-----------------+------------+

// HLL : Less accurate
spark.sql("""
select 
article_name, hll_sketch_estimate(hll_sketch_agg(referrer)) as page_sources
from clickstream
group by  article_name
sort by page_sources desc
limit 10
""").show

+-----------------+------------+
|     article_name|page_sources|
+-----------------+------------+
|     Hyphen-minus|      140917|
|           Russia|        1602|
|      World_War_I|        1497|
|           Sweden|         911|
|   Tamil_language|         803|
|      North_Korea|         782|
|         Napoleon|         772|
|             Urdu|         752|
|Holy_Roman_Empire|         728|
|          Playboy|         696|
+-----------------+------------+

// HLL : More accurate
spark.sql("""
select 
article_name, hll_sketch_estimate(hll_sketch_agg(referrer,20)) as page_sources
from clickstream
group by  article_name
sort by page_sources desc
limit 10
""").show

+-----------------+------------+
|     article_name|page_sources|
+-----------------+------------+
|     Hyphen-minus|      138706|
|           Russia|        1598|
|      World_War_I|        1502|
|           Sweden|         907|
|   Tamil_language|         823|
|      North_Korea|         772|
|         Napoleon|         757|
|             Urdu|         745|
|Holy_Roman_Empire|         719|
|          Playboy|         695|
+-----------------+------------+
```


hll_sketch_agg 

hll_sketch_estimate

hll_union function

hll_union_agg function