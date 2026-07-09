A *[streaming table](/aws/en/ldp/concepts/streaming-tables)* is a table with support for streaming or incremental data processing. Streaming tables are backed by pipelines. Each time an streaming table is refreshed, data added to the source tables is appended to the streaming table. You can refresh streaming tables manually or on a schedule.

To learn more about how to perform or schedule refreshes, see [Run a pipeline update](/aws/en/ldp/updates).

## Syntax

```
CREATE [OR REFRESH] [PRIVATE] STREAMING TABLE  
  table_name  
  [ table_specification ]  
  [ table_clauses ]  
  [ {flow_clause | AS query} ]  
  
table_specification  
  ( { column_identifier column_type [column_properties] } [, ...]  
    [ column_constraint ] [, ...]  
    [ , table_constraint ] [...] )  
  
   column_properties  
      { NOT NULL | GENERATED ALWAYS AS ( expr ) | GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY [ ( [ START WITH start | INCREMENT BY step ] [ ...] ) ] | DEFAULT default_expression | COMMENT column_comment | column_constraint | MASK clause } [ ... ]  
  
table_clauses  
  { USING DELTA  
    PARTITIONED BY (col [, ...]) |  
    CLUSTER BY clause |  
    LOCATION path |  
    COMMENT view_comment |  
    TBLPROPERTIES clause |  
    WITH { ROW FILTER clause } } [ ... ]  
   } [ ... ]  
  
flow_clause  
  FLOW { { INSERT [ONCE] BY NAME query } |  
  { AUTO CDC auto_cdc_flow_spec } |  
  { REPLACE WHERE predicate BY NAME query } }
```

## Parameters

* **REFRESH**

  If specified, creates the table, or updates an existing table and its content.
* **PRIVATE**

  Creates a private streaming table.

  + They are not added to the catalog and are only accessible within the defining pipeline
  + They can have the same name as an existing object in the catalog. Within the pipeline, if a private streaming table and an object in the catalog have the same name, references to the name resolve to the private streaming table.
  + Private streaming tables are only persisted across the lifetime of the pipeline, not just a single update.

  Private streaming tables were previously created with the `TEMPORARY` parameter.
* **table\_name**

  The name of the newly created table. The fully qualified table name must be unique.
* **table\_specification**

  This optional clause defines the list of columns, their types, properties, descriptions, and column constraints.

  + **[column\_identifier](/aws/en/sql/language-manual/sql-ref-names#column-alias)**

    The column names must be unique and map to the output columns of the query.
  + **[column\_type](/aws/en/sql/language-manual/sql-ref-datatypes)**

    Specifies the column's data type. Not all data types supported by Databricks are supported by streaming tables.
  + **column\_comment**

    An optional `STRING` literal describing the column. This option must be specified along with `column_type`. If the column type is not specified, the column comment is skipped.
  + **GENERATED ALWAYS AS ( [expr](/aws/en/sql/language-manual/sql-ref-expression) )**

    When you specify this clause the value of this column is determined by the specified `expr`.

    The `DEFAULT COLLATION` of the table must be `UTF8_BINARY`.

    `expr` may be composed of literals, column identifiers within the table, and deterministic, built-in SQL functions or operators except:

    - [Aggregate functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#aggregate-functions)
    - [Analytic window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#analytic-window-functions)
    - [Ranking window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#ranking-window-functions)
    - Table valued generator functions
    - Columns with a collation other than `UTF8_BINARY`

    Also `expr` must not contain any [subquery](/aws/en/sql/language-manual/sql-ref-syntax-qry-query).
  + **GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY [ ( [ START WITH start ] [ INCREMENT BY step ] ) ]**

    **Applies to:**  Databricks SQL  Databricks Runtime 10.4 LTS and above

    Defines an identity column. When you write to the table, and do not provide values for the identity column, it will be automatically assigned a unique and statistically increasing (or decreasing if `step` is negative) value. This clause is only supported for Delta tables. This clause can only be used for columns with BIGINT data type.

    The automatically assigned values start with `start` and increment by `step`. Assigned values are unique but are not guaranteed to be contiguous. Both parameters are optional, and the default value is 1. `step` cannot be `0`.

    If the automatically assigned values are beyond the range of the identity column type, the query will fail.

    When `ALWAYS` is used, you cannot provide your own values for the identity column.

    The following operations are not supported:

    - `PARTITIONED BY` an identity column
    - `UPDATE` an identity column

    note

    Declaring an identity column on a table disables concurrent transactions. Only use identity columns in use cases where concurrent writes to the target table are not required.
  + **DEFAULT default\_expression**

    **Applies to:**  Databricks SQL  Databricks Runtime 11.3 LTS and above

    Defines a `DEFAULT` value for the column which is used on `INSERT`, `UPDATE`, and `MERGE ... INSERT` when the column is not specified.

    If no default is specified `DEFAULT NULL` is applied for nullable columns.

    `default_expression` may be composed of literals, and built-in SQL functions or operators except:

    - [Aggregate functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#aggregate-functions)
    - [Analytic window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#analytic-window-functions)
    - [Ranking window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#ranking-window-functions)
    - Table valued generator functions

    Also `default_expression` must not contain any [subquery](/aws/en/sql/language-manual/sql-ref-syntax-qry-query).

    `DEFAULT` is supported for `CSV`, `JSON`, `PARQUET`, and `ORC` sources.
  + **[column\_constraint](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint)**

    Adds an informational primary key or informational foreign key constraint to the column in a streaming table.
  + **[MASK clause](/aws/en/sql/language-manual/sql-ref-syntax-ddl-column-mask)**

    Adds a column mask function to anonymize sensitive data.

    See [Row filters and column masks](/aws/en/data-governance/unity-catalog/filters-and-masks/).
  + **CONSTRAINT expectation\_name EXPECT (expectation\_expr) [ ON VIOLATION { FAIL UPDATE | DROP ROW } ]**

    Adds data quality expectations to the streaming table. These data quality expectations can be tracked over time and accessed through the streaming table's [event log](/aws/en/sql/language-manual/functions/event_log). A `FAIL UPDATE` expectation causes the processing to fail when both creating the table as well as refreshing the table. A `DROP ROW` expectation causes the entire row to be dropped if the expectation is not met. See [Manage data quality with pipeline expectations](/aws/en/ldp/expectations).

    `expectation_expr` may be composed of literals, column identifiers within the table, and deterministic, built-in SQL functions or operators except:

    - [Aggregate functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#aggregate-functions)
      * [Analytic window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#analytic-window-functions)
      * [Ranking window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#ranking-window-functions)
      * Table valued generator functions

    Also `expr` must not contain any [subquery](/aws/en/sql/language-manual/sql-ref-syntax-qry-query).
* **table\_constraint**

  When specifying a schema, you can define primary and foreign keys. The constraints are informational and are not enforced. See the [CONSTRAINT clause](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint) in the SQL language reference.

  note

  To define table constraints, your pipeline must be a Unity Catalog-enabled pipeline.
* **table\_clauses**

  Optionally specify partitioning, comments, and user defined properties for the table. Each sub clause may only be specified once.

  + **USING DELTA**

    Specifies the data format. The only option is DELTA.

    This clause is optional, and defaults to DELTA.
  + **PARTITIONED BY**

    An optional list of one or more columns to use for partitioning in the table. Mutually exclusive with `CLUSTER BY`.

    Liquid clustering provides a flexible, optimized solution for clustering. Consider using `CLUSTER BY` instead of `PARTITIONED BY` for pipelines.
  + **CLUSTER BY**

    Enable liquid clustering on the table and define the columns to use as clustering keys. Use automatic liquid clustering with `CLUSTER BY AUTO`, and Databricks intelligently chooses clustering keys to optimize query performance. Mutually exclusive with `PARTITIONED BY`.

    See [Use liquid clustering for tables](/aws/en/tables/clustering).
  + **LOCATION**

    An optional storage location for table data. If not set, the system defaults to the pipeline storage location.
  + **COMMENT**

    An optional `STRING` literal to describe the table.
  + **TBLPROPERTIES**

    An optional list of [table properties](/aws/en/ldp/properties) for the table.
  + **WITH ROW FILTER**

  Adds a row filter function to the table. Future queries for that table receive a subset of the rows for which the function evaluates to TRUE. This is useful for fine-grained access control, because it allows the function to inspect the identity and group memberships of the invoking user to decide whether to filter certain rows.

  See [`ROW FILTER` clause](/aws/en/sql/language-manual/sql-ref-syntax-ddl-row-filter).

  + **FLOW**

    Optionally defines a [flow](/aws/en/ldp/concepts/flows) inline with the table creation. A flow is a stateful query that refreshes the contents of the table. If `FLOW` is not specified, you can use `AS query` instead, or define flows separately with [`CREATE FLOW`](/aws/en/ldp/developer/ldp-sql-ref-create-flow). You can specify one of the following flow types:

    - **INSERT BY NAME**

      Inserts data into the table by column name. If the `ONCE` option is not supplied, the query must be a streaming query. Use the `STREAM` keyword to use streaming semantics to read from the source. If the read encounters a change or deletion to an existing record, an error is thrown. It is safest to read from static or append-only sources.

      note

      `FLOW INSERT BY NAME` is equivalent to using `AS query`. The following two statements have identical behavior:

      SQL

      ```
      CREATE OR REFRESH STREAMING TABLE raw_data  
      AS SELECT * FROM STREAM read_files('abfss://my_path');  
        
      CREATE OR REFRESH STREAMING TABLE raw_data  
      FLOW INSERT BY NAME SELECT * FROM STREAM read_files('abfss://my_path');
      ```
    - **ONCE**

      Optionally defines the flow as a one-time flow, such as a backfill. When `ONCE` is supplied, the query is not a streaming query, and the flow runs one time by default. If the table is refreshed with a full refresh, the `ONCE` flow runs again to recreate the data. `ONCE` only applies to `INSERT BY NAME` flows.
    - **`AUTO CDC`**

      Beta

      Available in Databricks Runtime 17.3 and above and the `PREVIEW` Pipelines channel.

      Defines an `AUTO CDC` flow that processes change data capture (CDC) records from a source into the table. Use `AUTO CDC` when the source data includes CDC semantics. See [The AUTO CDC APIs: Simplify change data capture with pipelines](/aws/en/ldp/cdc).
    - **REPLACE WHERE [predicate](/aws/en/sql/language-manual/sql-ref-expression) BY NAME query**

      Beta

      `FLOW REPLACE WHERE` is in [Beta](/aws/en/release-notes/release-types). Requires using the Pipelines Preview channel — set the `pipelines.channel` table property to `"PREVIEW"`.

      Defines a `REPLACE WHERE` flow that recomputes and overwrites only the rows matching `predicate`, leaving all other rows untouched. Use `REPLACE WHERE` for incremental batch processing of joins and aggregations, late-arriving data, schema evolution, and backfills. `BY NAME` is required. See [Batch processing with REPLACE WHERE flows](/aws/en/ldp/flows-replace-where).
* **[AS query](/aws/en/sql/language-manual/sql-ref-syntax-qry-select)**

  This clause populates the table using the data from `query`. This query must be a **streaming** query. Use the STREAM keyword to use streaming semantics to read from the source. If the read encounters a change or deletion to an existing record, an error is thrown. It is safest to read from static or append-only sources. To ingest data that has change commits, you can add the `skipChangeCommits` read option to handle errors.

  When you specify a `query` and a `table_specification` together, the table schema specified in `table_specification` must contain all the columns returned by the `query`, otherwise you get an error. Any columns specified in `table_specification` but not returned by `query` return `null` values when queried.

  For more information on streaming data, see [Transform data with pipelines](/aws/en/ldp/transform).

  + **Read Options**

    You can specify read options in the query to configure how data is read from the source. For example, you can specify `skipChangeCommits` to skip over any change commits in the source data. Read options are specified as a map in the `WITH` clause of query. For example:

    SQL

    ```
    SELECT * FROM STREAM source_table WITH (SKIPCHANGECOMMITS=TRUE, STARTINGVERSION=X)
    ```

    The `=TRUE` is optional, so you can also specify a boolean option like this:

    SQL

    ```
    SELECT * FROM STREAM source_table WITH (SKIPCHANGECOMMITS)
    ```

    note

    Rea