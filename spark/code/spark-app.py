from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.conf import SparkConf
from schema import format_df
#from es_daily_query import daily_problems, notify_tomorrow_problems
#from Predictor import EmurPredictor
from datetime import timedelta

sparkConf = SparkConf().set("es.nodes", "elasticsearch") \
    .set("es.port", "9200")

spark = SparkSession.builder.appName("spokelizard").config(conf=sparkConf).getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "10.0.100.23:9092") \
    .option("subscribe", "tap") \
    .load()

df = format_df(df)

# Write to Elasticsearch
es_stream = df.writeStream \
    .option("checkpointLocation", "/tmp/") \
    .format("es") \
    .start("index")

# Write to console (for debugging)
console_stream = df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

es_stream.awaitTermination()
