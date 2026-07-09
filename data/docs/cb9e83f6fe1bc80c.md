A standalone *streaming table* is a table registered to Unity Catalog with extra support for streaming or incremental data processing, defined outside of Lakeflow Spark Declarative Pipelines. A pipeline is automatically created for each streaming table. You can use streaming tables for incremental data loading from Kafka and cloud object storage.

You can create and refresh standalone streaming tables from a Databricks SQL warehouse, or from a notebook running on serverless general compute. For details on the differences between the two compute options, see [Requirements for standalone pipelines](/aws/en/ldp/dbsql/compute).

To create and refresh standalone streaming tables with Python from a notebook, see [Use Python with standalone pipelines](/aws/en/ldp/dbsql/using-python).

note

To learn how to use Delta Lake tables as streaming sources and sinks, see [Delta Lake table streaming reads and writes](/aws/en/structured-streaming/delta-lake).

## Requirements

For compute options, permissions, and other requirements for creating, refreshing, and querying standalone streaming tables, see [Requirements for standalone pipelines](/aws/en/ldp/dbsql/compute).

## Create streaming tables

A streaming table is defined by a SQL query in Databricks SQL. When you create a streaming table, the data currently in the source tables is used to build the streaming table. After that, you refresh the table, usually on a schedule, to pull in any added data in the source tables to append to the streaming table.

When you create a streaming table, you are considered the owner of the table.

To create a streaming table from an existing table, use the [CREATE STREAMING TABLE statement](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table), as in the following example:

SQL

```
CREATE OR REFRESH STREAMING TABLE sales  
  SCHEDULE EVERY 1 hour  
  AS SELECT product, price FROM STREAM raw_data;
```

In this case, the streaming table `sales` is created from specific columns of the `raw_data` table, with a schedule to refresh every hour. The query used must be a *streaming* query. Use the `STREAM` keyword to use streaming semantics to read from the source.

### Compute used for refresh

When you create a streaming table using the `CREATE OR REFRESH STREAMING TABLE` statement, the initial data refresh and population begin immediately. These operations do not consume Databricks SQL warehouse compute. Instead, streaming tables rely on serverless pipelines for both creation and refresh. A dedicated serverless pipeline is automatically created and managed by the system for each streaming table.

### Load files with Auto Loader

To create a streaming table from files in a volume, you use Auto Loader. Use Auto Loader for most data ingestion tasks from cloud object storage. Auto Loader and pipelines are designed to incrementally and idempotently load ever-growing data as it arrives in cloud storage.

To use Auto Loader in Databricks SQL, use the `read_files` function. The following examples shows using Auto Loader to read a volume of JSON files into a streaming table:

SQL

```
CREATE OR REFRESH STREAMING TABLE sales  
  SCHEDULE EVERY 1 hour  
  AS SELECT * FROM STREAM read_files(  
    "/Volumes/my_catalog/my_schema/my_volume/path/to/data",  
    format => "json"  
  );
```

To read data from cloud storage, you can also use Auto Loader:

SQL

```
CREATE OR REFRESH STREAMING TABLE sales  
  SCHEDULE EVERY 1 hour  
  AS SELECT *  
  FROM STREAM read_files(  
  's3://mybucket/analysis/*/*/*.json',  
    format => "json"  
  );
```

To learn about Auto Loader, see [What is Auto Loader?](/aws/en/ingestion/cloud-object-storage/auto-loader/). To learn more about using Auto Loader in SQL, with examples, see [Load data from object storage](/aws/en/ldp/developer/sql-dev#auto-loader-sql).

### Streaming ingestion from other sources

For example of ingestion from other sources, including Kafka, see [Load data in pipelines](/aws/en/ldp/load).

### Apply change data capture (CDC) with Auto CDC flows with Auto CDC flows")

Use the `FLOW AUTO CDC` clause to process change data capture (CDC) records from a source into a streaming table. Previously, the `MERGE INTO` statement was commonly used for processing CDC records on Databricks. However, `MERGE INTO` can produce incorrect results because of out-of-sequence records or requires complex logic to re-order records. See [Change data capture and snapshots](/aws/en/data-engineering/what-is-cdc).

`AUTO CDC` simplifies CDC by automatically handling out-of-order records. You specify keys to identify records, a sequence column for ordering, and whether to store results as SCD type 1 (direct updates) or SCD type 2 (history tracking).

The following example creates a streaming table that applies CDC changes using SCD type 1:

SQL

```
CREATE OR REFRESH STREAMING TABLE target  
  FLOW AUTO CDC  
  FROM stream(cdc_data.users)  
  KEYS (userId)  
  SEQUENCE BY sequenceNum  
  STORED AS SCD TYPE 1;
```

The following example uses SCD type 2 to retain a history of changes:

SQL

```
CREATE OR REFRESH STREAMING TABLE target  
  FLOW AUTO CDC  
  FROM stream(cdc_data.users)  
  KEYS (userId)  
  APPLY AS DELETE WHEN operation = "DELETE"  
  SEQUENCE BY sequenceNum  
  COLUMNS * EXCEPT (operation, sequenceNum)  
  STORED AS SCD TYPE 2;
```

For full details on Auto CDC options and behavior, see [The AUTO CDC APIs: Simplify change data capture with pipelines](/aws/en/ldp/cdc). For the complete syntax reference, see [CREATE STREAMING TABLE](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table).

### Apply selective batch replacement with REPLACE WHERE flows

Beta

This feature is in [Beta](/aws/en/release-notes/release-types). Your streaming table must use the Pipelines Preview channel.

Use the `FLOW REPLACE WHERE` clause to recompute and overwrite a targeted subset of a streaming table without reprocessing your entire table history. `REPLACE WHERE` flows are well-suited for incremental batch processing of joins and aggregations, late-arriving data, upstream reprocessing, schema evolution, and backfills.

For full details on `REPLACE WHERE` flows, including requirements, predicate overrides, and incremental refresh, see [REPLACE WHERE flows for standalone streaming tables](/aws/en/ldp/dbsql/flows-replace-where).

### Ingest new data only

By default, the `read_files` function reads all existing data in the source folder during table creation, and then processes newly arriving records with each refresh.

To avoid ingesting data that already exists in the source folder at the time of table creation, set the `includeExistingFiles` option to `false`. This means that only data that arrives in the folder after table creation is processed. For example:

SQL

```
CREATE OR REFRESH STREAMING TABLE sales  
  SCHEDULE EVERY 1 hour  
  AS SELECT *  
  FROM STREAM read_files(  
    '/path/to/files',  
    includeExistingFiles => false  
  );
```

### Set the runtime channel

Streaming tables created using SQL warehouses are automatically refreshed using a pipeline. Pipelines use the runtime in the `current` channel by default. See [Lakeflow Spark Declarative Pipelines release notes and the release upgrade process](/aws/en/release-notes/dlt/) to learn about the release process.

Databricks recommends using the `current` channel for production workloads. New features are first released to the `preview` channel. You can set a pipeline to the preview channel to test new features by specifying `preview` as a table property using a `CREATE OR REFRESH STREAMING TABLE` statement. To update the channel for an existing streaming table, you must run `CREATE OR REFRESH STREAMING TABLE` with the updated `TBLPROPERTIES`.

The following code example shows how to set the channel to preview:

SQL

```
CREATE OR REFRESH STREAMING TABLE sales  
  TBLPROPERTIES ('pipelines.channel' = 'preview')  
  SCHEDULE EVERY 1 hour  
  AS SELECT *  
  FROM STREAM raw_data;
```

### Hide sensitive data

You can use streaming tables to hide sensitive data from users accessing the table. One approach is to define the query so that it excludes sensitive columns or rows entirely. Alternatively, you can apply column masks or row filters based on the permissions of the querying user. For example, you might hide the `tax_id` column for users who are not in the group `HumanResourcesDept`. To do this, use the `ROW FILTER` and `MASK` syntax during the creation of the streaming table. For more information, see [Row filters and column masks](/aws/en/data-governance/unity-catalog/filters-and-masks/).

## Refresh a streaming table

Streaming tables automatically create and use serverless pipelines to process refresh operations. The refresh is managed by the pipeline and the update is monitored by the Databricks SQL warehouse used to create the streaming table. Streaming tables can be updated using a pipeline that runs on a [schedule](/aws/en/ldp/dbsql/schedule-refreshes).

Even if you have a scheduled refresh, you can call a manual refresh at any time. Refreshes are handled by the same pipeline that was automatically created along with the streaming table.

To refresh a streaming table:

SQL

```
REFRESH STREAMING TABLE sales;
```

You can check the status of the latest refresh with [DESCRIBE TABLE EXTENDED](/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-table).

note

You might need to refresh your streaming table before using [time travel](/aws/en/tables/history#time-travel) queries.

To learn how to schedule a refresh, see [Schedule refreshes](/aws/en/ldp/dbsql/schedule-refreshes). Scheduled refreshes can have update [notifications](/aws/en/ldp/dbsql/schedule-refreshes#notifications), and you can set the [performance mode](/aws/en/ldp/dbsql/schedule-refreshes#performance-mode) for the refresh.

### How refresh works

A streaming table refresh only evaluates new rows that have arrived after the last update, and appends only the new data.

Each refresh uses the current definition of the streaming table to process this new data. Modifying a streaming table definition does not automatically recalculate existing data. If a modification is incompatible with existing data (for example, changing a data type), the next refresh fails with an error.

The following examples explain how changes to a streaming table definition affect refresh behavior:

* Removing a filter does not reprocess previously filtered rows.
* Changing column projections does not affect how existing data was processed.
* Joins with static snapshots use the snapshot state at the time of the initial processing. Late-arriving data that would have matched with the updated snapshot is ignored. This can lead to facts being dropped if dimensions are late.
* Modifying the CAST of an existing column results in an error.

If your data changes in a way that cannot be supported in the existing streaming table, you can perform a full refresh.

### Fully refresh a streaming table

Full refreshes re-process all data available in the source with the latest definition. It is not recommended to call full refreshes on sources that don't keep the entire history of the data or have short retention periods, such as Kafka, because the full refresh truncates the existing data. You might not be able to recover old data if the data is no longer available in the source.

For example:

SQL

```
REFRESH STREAMING TABLE sales FULL;
```

### Schedule and monitor refreshes

You can refresh a streaming table automatically on a schedule or when upstream data changes, and you can configure refresh timeouts, notifications, and performance modes. See [Schedule refreshes](/aws/en/ldp/dbsql/schedule-refreshes).

## Control access to streaming tables

Streaming tables support rich access controls to support data-sharing while avoiding exposing potentially private data. A streaming table owner or a user with the `MANAGE` privilege can grant `SELECT` privileges to other users. Users with `SELECT` access to the streaming table do not require `SELECT` access to the tables referenced by the streaming table. This access control enables data sharing while controlling access to the underlying data.

You can also modify the owner of a streaming table.

### Grant privileges to a streaming table

To grant access to a streaming table, use the [GRANT statement](/aws/en/sql/language-manual/security-grant):

SQL

```
GRANT <privilege_type> ON <st_name> TO <principal>;
```

The `privilege_type` can be:

* `SELECT` - the user can `SELECT` the streaming table.
* `REFRESH` - the user can `REFRESH` the streaming table. Refreshes are run using the owner's permissions.

The following example creates a streaming table and grants select and refresh privileges to users:

SQL

```
CREATE OR REFRESH STREAMING TABLE st_name AS SELECT * FROM source_table;  
  
-- Grant read-only access:  
GRANT SELECT ON st_name TO read_only_user;  
  
-- Grant read and refresh access:  
GRANT SELECT ON st_name TO refresh_user;  
GRANT REFRESH ON st_name TO refresh_user;
```

For more information about granting privileges on Unity Catalog securable objects, see [Unity Catalog privileges reference](/aws/en/data-governance/unity-catalog/access-control/privileges-reference).

### Revoke privileges from a streaming table

To revoke access from a streaming table, use the [REVOKE statement](/aws/en/sql/language-manual/security-revoke):

SQL

```
REVOKE privilege_type ON <st_name> FROM principal;
```

When `SELECT` privileges on a source table are revoked from the streaming table owner or any other user who has been granted `MANAGE` or `SELECT` privileges on the streaming table, or the source table is dropped, the streaming table owner or user granted access is still able to query the streaming table. However, the following behavior occurs:

* The streaming table owner or others who have lost access to a streaming table can no longer `REFRESH` that streaming table, and the streaming table be