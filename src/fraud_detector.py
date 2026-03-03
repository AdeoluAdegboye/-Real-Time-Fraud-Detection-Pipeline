# src/fraud_detector.py
import os
os.environ['JAVA_HOME'] = '/opt/homebrew/opt/openjdk@17'
os.environ['PATH'] = '/opt/homebrew/opt/openjdk@17/bin:' + os.environ['PATH']
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import *


spark = SparkSession.builder \
    .appName('FraudDetectionPipeline') \
    .config('spark.jars.packages',
            'org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.postgresql:postgresql:42.6.0') \
    .getOrCreate()

spark.sparkContext.setLogLevel('WARN')

schema = StructType([
    StructField('transaction_id', StringType()),
    StructField('user_id', StringType()),
    StructField('amount', DoubleType()),
    StructField('merchant', StringType()),
    StructField('location', StringType()),
    StructField('timestamp', StringType()),
])

# Read from Kafka
raw_stream = spark.readStream \
    .format('kafka') \
    .option('kafka.bootstrap.servers', 'localhost:9092') \
    .option('subscribe', 'transactions') \
    .load()

# Parse JSON
transactions = raw_stream \
    .select(from_json(col('value').cast('string'), schema).alias('data')) \
    .select('data.*')

# Fraud detection rules
flagged = transactions.withColumn(
    'fraud_flag',
    when(col('amount') > 1000000, 'HIGH_AMOUNT')
    .when(col('amount') > 500000, 'SUSPICIOUS_AMOUNT')
    .otherwise('CLEAN')
).filter(col('fraud_flag') != 'CLEAN')

# Write flagged transactions to PostgreSQL
def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format('jdbc') \
        .option('url', 'jdbc:postgresql://localhost:5432/fraud_db') \
        .option('dbtable', 'flagged_transactions') \
        .option('user', 'admin') \
        .option('password', 'admin123') \
        .mode('append') \
        .save()

query = flagged.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode('update') \
    .start()

query.awaitTermination()