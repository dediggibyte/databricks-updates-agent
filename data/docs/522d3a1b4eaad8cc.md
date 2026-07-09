Public Preview

This feature is in [Public Preview](/aws/en/release-notes/release-types). This feature only supports converting foreign tables federated using [HMS and Glue Federation](/aws/en/query-federation/hms-federation-concepts).

This page describes how to use `SET EXTERNAL` to convert a foreign table to an external table.

* For details on converting a foreign table to a managed table, see [Foreign tables using SQL](/aws/en/tables/convert-to-managed#convert-foreign-sql)
* For details on converting an external table to a managed table, see [Convert external or foreign Delta Lake tables to Unity Catalog managed tables](/aws/en/tables/convert-to-managed)

## `SET EXTERNAL` overview

Use the `SET EXTERNAL` feature to convert a foreign table to a Unity Catalog `EXTERNAL` table in Databricks. `SET EXTERNAL` offers the following benefits:

* Retaining table history
* Keeping the same table configurations, including the same name, settings, permissions, and views.

## Prerequisites

* **Data format**: The foreign table's data format must be one of the following:
  + Delta
  + Parquet
  + ORC
  + Avro
  + JSON
  + CSV
  + TEXT
* **Table type**: The HMS table type must be an external HMS table. The command fails if the table is a managed HMS table.
* **Runtime**: Databricks Runtime 17.3 or above
* **Permissions**: `OWNER` or `MANAGE` permissions on the table and `CREATE` permission on the `EXTERNAL LOCATION`

warning

Concurrent writes to the source table and from Unity Catalog are not supported. You are responsible for disabling reads and writes to the source table in the external catalog and ensuring that workloads have migrated to the new catalog before performing the conversion.

## Syntax

To convert your Unity Catalog foreign table to be Unity Catalog external, run the following command:

SQL

```
ALTER TABLE source_table SET EXTERNAL [DRY RUN]
```

## Parameters

* **source\_table**

  An existing foreign table in Unity Catalog. Foreign tables contain data and metadata managed by an external catalog. Before conversion, if you drop the source table in the external catalog, the foreign table is also dropped in Unity Catalog. After the table is converted to external, dropping the source table in the external catalog does not affect the Unity Catalog external table.
* **`DRY RUN`**

  When specified, checks whether the source table can be upgraded without upgrading the target tables. The command returns `DRY_RUN_SUCCESS` if a table can be upgraded.

## Rollback

To roll back the table migration, drop the table and it is then re-federated as foreign in the next catalog sync.

SQL

```
DROP TABLE catalog.schema.my_external_table;
```

## Check conversion

You can confirm that your foreign table has been converted to an external table by checking in Catalog Explorer. Before conversion, the table shows as **Foreign**, and after conversion it shows as **External**.

note

Running `DESCRIBE EXTENDED` shows the table type as `EXTERNAL` both before and after conversion. This is due to how Federation works, as it mimics the behavior of running this command on the `hive_metastore` catalog. To accurately verify conversion, use Catalog Explorer.

## FAQ

### Can I create tables as well as convert tables in a foreign catalog?

Yes, you can create external or managed tables in a foreign catalog. The behavior depends on the schema configuration:

* **For Glue or eHMS schemas**, or **for schemas with a managed location set in Unity Catalog**: If you run `CREATE TABLE foreign_catalog.schema.table`, this creates a Unity Catalog managed or external table. The table is not pushed or synced to the external catalog.
* **For schemas from internal Hive metastore connections**: If you try to create a table in a foreign schema, it still creates a foreign table and also creates a table in `hive_metastore`.
* **For legacy workspace Hive metastore**: Since it is read and write federation, if you create a table in the foreign catalog, it also creates a table in the internal Hive metastore.

### What if my foreign tables are in SerDe format?

For Parquet SerDe tables in AWS Glue, you must modify the table metadata before converting to an external table. The following Python script uses the AWS boto3 library to update the necessary properties:

Python

```
import boto3  
import json  
  
# Initialize boto3 Glue client with your AWS region  
glue_client = boto3.client('glue', region_name='<your-aws-region>')  # Example: 'us-west-2'  
  
# Configure your table details  
DATABASE_NAME = '<your-database-name>'  # Example: 'my_database'  
TABLE_NAME = '<your-table-name>'  # Example: 'my_parquet_table'  
SPARK_PROVIDER = 'PARQUET'  
SPARK_PARTITION_PROVIDER = 'filesystem'  
  
# Step 1: Get the current table definition  
print(f"Retrieving current table definition for {DATABASE_NAME}.{TABLE_NAME}...")  
response = glue_client.get_table(DatabaseName=DATABASE_NAME, Name=TABLE_NAME)  
  
# Extract the table's current definition  
table_definition = response['Table']  
  
# Step 2: Verify if the table is a Parquet SerDe  
serde_library = table_definition['StorageDescriptor']['SerdeInfo'].get('SerializationLibrary', '')  
is_parquet_serde = serde_library == "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"  
  
if not is_parquet_serde:  
    print(f"The table {TABLE_NAME} does not use a Parquet SerDe. Found: {serde_library}")  
else:  
    print(f"Table {TABLE_NAME} is using a Parquet SerDe.")  
  
    # Step 3: Extract the S3 path dynamically from the Location field  
    s3_path = table_definition['StorageDescriptor']['Location']  
    print(f"S3 Path found: {s3_path}")  
  
    # Step 4: Modify the SerDe and table properties  
    # Modify SerDe parameters  
    if 'SerdeInfo' in table_definition['StorageDescriptor']:  
        if 'Parameters' not in table_definition['StorageDescriptor']['SerdeInfo']:  
            table_definition['StorageDescriptor']['SerdeInfo']['Parameters'] = {}  
        table_definition['StorageDescriptor']['SerdeInfo']['Parameters']['path'] = s3_path  
  
    # Modify table properties  
    if 'Parameters' not in table_definition:  
        table_definition['Parameters'] = {}  
  
    # Set both spark.sql.sources.provider and spark.sql.partitionProvider  
    table_definition['Parameters']['spark.sql.sources.provider'] = SPARK_PROVIDER  
    table_definition['Parameters']['spark.sql.partitionProvider'] = SPARK_PARTITION_PROVIDER  
  
    # Remove metadata fields that are not accepted by update_table API  
    table_definition.pop('CreateTime', None)  
    table_definition.pop('UpdateTime', None)  
    table_definition.pop('LastAccessTime', None)  
    table_definition.pop('Retention', None)  
    table_definition.pop("DatabaseName", None)  
    table_definition.pop('CreatedBy', None)  
    table_definition.pop('IsRegisteredWithLakeFormation', None)  
    table_definition.pop('CatalogId', None)  
    table_definition.pop('VersionId', None)  
  
    # Step 5: Update the table with the modified properties  
    print(f"Updating the table {TABLE_NAME} in Glue...")  
    response = glue_client.update_table(  
        DatabaseName=DATABASE_NAME,  # Correct use of DatabaseName  
        TableInput=table_definition,  
    )  
  
    print(f"Table {TABLE_NAME} updated successfully!")
```

### What if my foreign tables are DBFS-backed?

When converting a DBFS-backed table, we store the current mapping of the DBFS path to cloud path as the external table's cloud path location.

### Can I convert at the schema or catalog level?

You can iterate through your tables in your schemas to convert individually, or utilize the discoverx labs project to convert entire schemas or catalogs at once:

Python

```
df = (dx.from_tables("prod.*.*")  
.with_sql("ALTER TABLE {full_table_name} SET EXTERNAL;")  
.apply())  # dry run with .explain()
```