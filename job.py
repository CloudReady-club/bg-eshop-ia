import sys
from pyspark.context import SparkContext
from pyspark.sql.functions import lit, current_timestamp
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Arguments passed to Glue job
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# =========================
# Source and Target Paths
# =========================
source_path = "s3://your-source-bucket/input/data.csv"
target_path = "s3://your-target-bucket/output/"

# =========================
# Load CSV from S3
# =========================
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(source_path)

# =========================
# Add 3 new columns
# =========================
df_with_cols = (
    df
    .withColumn("col_A", lit("static_value"))
    .withColumn("col_B", current_timestamp())
    .withColumn("col_C", lit(123))
)

# =========================
# Reorder columns → new cols first
# =========================
new_column_order = ["col_A", "col_B", "col_C"] + df.columns
df_final = df_with_cols.select(new_column_order)

# =========================
# Write to target S3
# =========================
df_final.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(target_path)

job.commit()
