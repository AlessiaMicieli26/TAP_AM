from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, ArrayType, IntegerType
from pyspark.sql.functions import col, from_json, explode, expr, split, substring, to_date, lit

def format_df(df):
    schema = StructType([
        StructField("event", StructType([
            StructField("original", StringType(), True)
        ])),
        StructField("@timestamp", StringType(), True),
        StructField("log", StructType([
            StructField("file", StructType([
                StructField("path", StringType(), True)
            ]))
        ])),
        StructField("host", StructType([
            StructField("name", StringType(), True)
        ])),
        StructField("@version", StringType(), True)
    ])

    return df \
        .withColumn("value_str", df["value"].cast(StringType())) \
        .withColumn("json", from_json(col("value_str"), schema)) \
        .select(
            col("json.event.original").alias("message"),
            col("json.@timestamp").alias("@timestamp"),
            col("json.log.file.path").alias("log_path"),
            col("json.host.name").alias("host_name"),
            col("json.@version").alias("@version")
        ) \
        .withColumn("split_message", split(col("message"), ",")) \
        .select(
            col("split_message")[0].alias("id_player"),
            col("split_message")[1].alias("room"),
            col("split_message")[2].alias("name_room"),
            substring(col("split_message")[5], 1, 10).alias("timestamp"),  # Estrae i primi 10 caratteri
            col("split_message")[7].alias("sign"),
            split(col("split_message")[8], ",").alias("user_signs"),
            col("split_message")[12].alias("rock_num"),
            col("split_message")[13].alias("scissor_num"),
            col("split_message")[14].alias("paper_num"),
            col("log_path"),
            col("host_name"),
            col("@version")
        ) \
        .withColumn("timestamp", to_date("timestamp", "yyyy-MM-dd"))
