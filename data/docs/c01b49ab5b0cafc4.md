Public Preview

Converting an external table to a managed table is generally available.

Converting a foreign table to a managed table is in [Public Preview](/aws/en/release-notes/release-types). Only foreign tables federated using [Hive metastore and Glue Federation](/aws/en/query-federation/hms-federation-concepts) are supported.

To convert an external or foreign Delta Lake table to a Unity Catalog managed table in Databricks, use the `ALTER TABLE ... SET MANAGED` command or, for external tables, Catalog Explorer. The conversion retains table configurations, including name, settings, permissions, and views, and retains table history.

For external table conversions, `SET MANAGED` also:

* Minimizes reader and writer downtime.
* Handles concurrent writes during conversion.
* Allows you to roll back a converted managed table to an external table.
* Redirects path-based reads and writes to allow legacy code to function after conversion.

Although you can also use `CREATE TABLE AS SELECT` (CTAS) to convert an external table, Databricks recommends `SET MANAGED` for these benefits.

For foreign table conversions, Databricks sets predictive optimization on the converted table to `INHERIT` rather than automatically enabling it. See [Foreign tables using SQL](#convert-foreign-sql).

To convert foreign tables to external tables, see [Convert a foreign table to an external Unity Catalog table](/aws/en/tables/convert-foreign-external).

## Prerequisites

### External tables

Converting external tables to managed tables has the following prerequisites:

* **Format**: The table must use the Delta Lake format.
* **Runtime**: You must use Databricks Runtime 17.3 LTS or above or Serverless compute to use `SET MANAGED`, `UNSET MANAGED`, or `TRUNCATE UNIFORM HISTORY`.
* **Readers and writers**: Databricks readers and writers for your source tables must use Databricks Runtime 15.4 LTS or above. If your readers or writers use 14.3 LTS or below, see [Legacy readers and writers](#legacy-readers-writers).
* **External clients**: External (non-Databricks) clients must support reads to Unity Catalog managed tables. See [Access tables with Delta clients](/aws/en/external-access/#delta-clients).
  + Use the [Access Insights](https://github.com/databrickslabs/access-insights) dashboard to see whether readers and writers accessing your tables are Databricks Runtime or external non-Databricks.
* **Feature compatibility**: If your table has `minReaderVersion=2`, `minWriterVersion=7`, and `tableFeatures={..., columnMapping}`, the `SET MANAGED` command fails with a `DELTA_TRUNCATED_TRANSACTION_LOG` error. Verify if your table has these properties using `DESCRIBE DETAIL`. See [Delta Lake feature compatibility and protocols](/aws/en/tables/features/feature-compatibility).

After conversion, path-based reads and writes are automatically redirected to the new managed location with slight performance overhead. Databricks recommends migrating all path-based access to name-based access to avoid the performance overhead. See [Path-based redirect](#path-redirect).

important

To avoid conflicts, cancel any existing `OPTIMIZE` command jobs (liquid clustering, compaction, `ZORDER`) operating on your external table, and do not schedule any jobs while you convert your external tables to managed tables.

### Foreign tables

Public Preview

Converting a foreign table to a managed table is in [Public Preview](/aws/en/release-notes/release-types).

Converting foreign tables to managed tables has the following prerequisites:

* **Data format**: The foreign table must use the Delta Lake format. To perform a one-time conversion for Parquet, see [Convert to Delta Lake](/aws/en/ingestion/data-migration/convert-to-delta).
* **Runtime**: Databricks Runtime 17.3 or above.
* **Table type**: The Hive metastore (HMS) table type must be an external HMS table. The command fails if the table is a managed HMS table.
* **Permissions**: `OWNER` or `MANAGE` permissions on the table and `CREATE` permission on the `EXTERNAL LOCATION`.

## Downtime and data copy times

The `SET MANAGED` command minimizes or eliminates downtime compared to alternative approaches, such as [`DEEP CLONE`](/aws/en/sql/language-manual/delta-clone).

### External tables

The conversion process for external tables uses a two-step approach:

1. **Initial data copy (no downtime):** The command copies table data and Delta transaction log from the external location to the managed location. Active readers and writers to the external table run without interruption.
2. **Switch to managed location (brief downtime):** Commits made to the external location during the first step are moved to the managed location, and the table metadata is updated to register the new managed location. During this step, all writes to the external location are temporarily blocked, resulting in writer downtime. Readers on Databricks Runtime 16.4 LTS or above experience no downtime, but readers on Databricks Runtime 15.4 LTS and below might experience downtime.

The following table shows estimated downtime based on the size of the source table and an estimated throughput rate of 0.5-2 GB/CPU core/minute:

| Table size | Recommended cluster size | Estimated data copy time | Estimated reader and writer downtime |
| --- | --- | --- | --- |
| 100 GB or less | 32-core / X-Large SQL warehouse | ~6 min or less | ~1-2 min or less |
| 1 TB | 64-core / 2X-Large SQL warehouse | ~30 min | ~1-2 min |
| 10 TB | 256-core / 4X-Large SQL warehouse | ~1.5 hrs | ~1-5 min |

note

Downtime might vary based on factors such as file size, number of files, and number of commits.

### Foreign tables

Foreign table conversion downtime depends on whether you use `MOVE` or `COPY`:

* For `MOVE`, downtime might occur as described for external tables. See [External tables](#ext-downtime).
* For `COPY`, you are responsible for managing downtime because the conversion process copies the source table to the managed storage location, creating two separate copies of the data. You are responsible for disabling reads and writes to the source table in the external catalog, and migrating workloads to use the new managed table.

## Convert to a managed table

Convert an external table using Catalog Explorer or SQL, or convert a foreign table using SQL.

### External tables using the Catalog Explorer (Beta)

Beta

Converting external to managed tables using Catalog Explorer is in [Beta](/aws/en/release-notes/release-types).

Using Catalog Explorer, you can convert one or more external tables in a schema at a time.

1. Go to the table or schema you want to convert in Catalog Explorer.
2. Under **About this table** (table detail page) or **About this schema** (schema detail page), click **Explore optimizations**.
3. In the **Why migrate to Unity Catalog managed tables?** dialog, click **Continue**.
4. Select the external tables you want to convert. If you opened the dialog from a table detail page, Catalog Explorer pre-selects your table. Use the search bar to find additional tables. Managed tables are not selectable.
5. Click **Create conversion notebook**.
6. Optionally, enter a name for the notebook. By default, this saves the notebook to your home folder. Click **Browse** to save it to a different location.
7. In the notebook, review the best practices and verify that you meet all [prerequisites](#prerequisites).
8. Run the **SET MANAGED Queries** cell.

After the cell runs, the table type displays as **MANAGED** instead of **EXTERNAL** in Catalog Explorer. Refresh the page if the status doesn't update immediately.

### External tables using SQL

Depending on whether your external table has Apache Iceberg reads ([UniForm](/aws/en/delta/uniform)) enabled, run one of the following commands. To verify if your table has Iceberg reads enabled, see [Verify that Iceberg reads are enabled](/aws/en/delta/uniform#verify).

* For Unity Catalog external tables without Iceberg reads enabled, run the following command:

  SQL

  ```
  ALTER TABLE catalog.schema.my_external_table SET MANAGED;
  ```

  After conversion, you can enable Iceberg reads on your managed table without compatibility concerns.
* For Unity Catalog external tables with Iceberg reads already enabled, run the following command:

  SQL

  ```
  ALTER TABLE catalog.schema.my_external_table SET MANAGED TRUNCATE UNIFORM HISTORY;
  ```

  Include `TRUNCATE UNIFORM HISTORY` to maintain optimal table performance and compatibility. `TRUNCATE UNIFORM HISTORY` truncates UniForm Iceberg history only and doesn't remove Delta history. This command results in a short read and write downtime for Iceberg after the truncation.

After table conversion, existing read and write streams fail. Restart streams with the same configurations to automatically use path-based redirect. Verify that your readers and writers work with the managed table. See [Streaming behavior](#redirect-streams).

Predictive optimization is automatically enabled after conversion unless you manually turned it off. See [Verify whether predictive optimization is enabled](/aws/en/optimizations/predictive-optimization#check-po-enabled).

Databricks retains the data in your Unity Catalog external location for 14 days to allow rollback. See [Roll back a managed table conversion](#rollback). After 14 days, with predictive optimization enabled, Databricks automatically deletes this data to reclaim storage and save costs. If you turn off predictive optimization, run `VACUUM` (requires Databricks Runtime 17.3 LTS or above or Serverless compute) on the newly converted managed table after 14 days to reclaim the storage yourself.

SQL

```
VACUUM my_converted_table
```

note

Even with predictive optimization enabled, data in your Unity Catalog external location might not be deleted after 14 days. For example, this can occur when the managed table is infrequently used or small. If the previous data remains, run `VACUUM` manually to remove it.

Databricks deletes only the data in the external location. The Delta transaction log and reference to the table in Unity Catalog are kept.

### Foreign tables using SQL

Public Preview

Converting a foreign table to a managed table is in [Public Preview](/aws/en/release-notes/release-types).

To convert your Unity Catalog foreign table to be Unity Catalog managed, run the following command:

SQL

```
ALTER TABLE source_table SET MANAGED {MOVE | COPY}
```

* **source\_table**

  An existing foreign table federated in Unity Catalog.
* **`MOVE`**

  Converts the table to managed and disables access to the source table in the external catalog.

  + Access through the external catalog or path-based access fails after you convert the table. All readers and writers to the table must use the Unity Catalog namespace for access. For example:

    SQL

    ```
    SELECT * FROM catalog_name.schema_name.table_name;
    ```
  + Path-based access is not supported and fails after you convert the table. For example:

    SQL

    ```
    SELECT * FROM delta.`protocol://path/to/table`;
    ```
  + The reader/writer version and client-compatibility requirements are the same as described in [Prerequisites](#prerequisites) and [Legacy readers and writers](#legacy-readers-writers).
  + Predictive optimization is set to `INHERIT` unless you manually configured it. To check whether predictive optimization is enabled, see [Verify whether predictive optimization is enabled](/aws/en/optimizations/predictive-optimization#check-po-enabled).
* **`COPY`**

  Converts the table to managed without modifying or disabling access to the source table in the external catalog.

  + During conversion to managed, the conversion process copies data from the source table into the managed storage location defined for the foreign table, creating two separate copies: the new managed table and the source table in the external catalog.
  + Unlike `MOVE` where reads and writes fail, when using `COPY`, you are responsible for properly disabling reads and writes to the source table in the external catalog and ensuring that workloads have migrated to the new catalog.

After table conversion, you must restart any streaming jobs (read or write) using the foreign table and verify that your readers and writers work with the managed table.

Before conversion, if you drop the source table in the external catalog, Unity Catalog also drops the foreign table. After you convert the table to managed, dropping the source table in the external catalog does not affect the Unity Catalog managed table.

If the command is interrupted while copying data, restart it. The command resumes from where it left off.

warning

Databricks recommends that you avoid running multiple `SET MANAGED` commands concurrently on the same table, which can lead to an inconsistent table state.

#### Video walkthrough

This video demonstrates how to [federate an AWS Glue metastore](/aws/en/query-federation/hms-federation-glue) and then convert foreign tables to managed tables (10 minutes). The foreign-to-managed table conversion begins at 5:30.

### Verify conversion

To verify that your table converted to a managed table successfully, check whether the table `Type` is `MANAGED`. You can do either of the following:

* Open a new tab and go to the Catalog Explorer. In the **Details** tab, under **About this table**, the table **Type** displays as **Managed**.
* Check the table `Type` by running the following SQL command:

  SQL

  ```
  DESCRIBE EXTENDED catalog_name.schema_name.table_name
  ```

  To check multiple tables at once or script the check, query `information_schema.tables` instead:

  SQL

  ```
  SELECT table_type FROM system.information_schema.tables  
  WHERE table_catalog = 'catalog_name' AND table_schema = 'schema_name' AND table_name = 'table_name';
  ```

### Legacy readers and writers

Databricks recommends upgrading all readers and writers to Databricks Runtime 15.4 LTS or above to use the full capabilities of `SET MANAGED`, incl