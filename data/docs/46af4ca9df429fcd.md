Beta

This feature is in [Beta](/aws/en/release-notes/release-types).

By default, Lakeflow Connect doesn't ingest Salesforce formula fields incrementally. Instead, it takes a snapshot of formula fields on each pipeline run, then joins them with the rest of the table. However, you can enable incremental formula field ingestion, which often significantly improves performance and reduces costs.

## Why formula fields are ingested differently

Salesforce computes formula fields dynamically at read time rather than storing them as static values. A formula such as one that uses `TODAY()` or `NOW()` can produce a different result on every read, even when nothing about the underlying record has changed.

Salesforce cursor columns (like `SystemModstamp` or `LastModifiedDate`) track changes to the record itself, not changes to formula outputs. When a formula result changes, Salesforce doesn't advance the cursor columns. Because incremental ingestion relies on those cursor columns to detect changed rows, formula fields can't be ingested incrementally the same way ordinary fields are: a formula output can change without any cursor column advancing, so a standard incremental read would silently miss it.

To handle this, Lakeflow Connect separates the two kinds of fields and uses a different refresh strategy for each, described in the following section.

## How incremental formula field ingestion works

If you use the default snapshot approach, the end result of a Salesforce ingestion pipeline is a series of streaming tables (one per source table), and formula fields are re-snapshotted and joined on each run.

If you use incremental formula field ingestion instead, the connector splits each table into two parts:

* **Non-formula fields** are ingested incrementally into an intermediary streaming table. The connector applies only the rows that actually changed in Salesforce, using the cursor columns to detect changes (the standard incremental change-data-capture behavior).
* **Formula fields** are recreated as a materialized view that recomputes the formula logic on top of the intermediary streaming table. Because formula outputs can change without a cursor signal, this design keeps formula fields separate from cursor-based incremental ingestion.

The end result is a single materialized view per table that joins the incrementally maintained non-formula fields with the recomputed formula fields. This avoids re-snapshotting the entire table on every run.

note

The intermediary streaming table that holds non-formula fields is named `<destination-table>_without_formula_fields`. Because non-formula fields use cursor-based change detection, this table records a change for a row only when that row's non-formula data actually changes in Salesforce. The final materialized view can still show updated formula values on a run when the intermediary streaming table recorded no change for that row, because formula fields are recomputed independently of the cursor columns. This is expected: an updated formula value in the materialized view does not mean the row's non-formula data changed.

When a non-formula field is deleted in Salesforce, the corresponding column in the destination is marked as inactive but is not deleted. If it reappears in the source, the pipeline fails with a duplicate column error. In contrast, when a formula field is deleted, it's removed from the final materialized view. If the field later reappears in the source, it's ingested into the materialized view with the latest data.

When you create a formula that returns a number in Salesforce, you can specify the scale (the number of digits allowed after the decimal). Salesforce automatically rounds the formula's result to the specified number of decimal places. To avoid cumulative rounding errors, the Databricks connector doesn't reproduce this behavior.

## Limitations

The limitations in this section apply when you create an ingestion pipeline with incremental formula fields.

### General limitations

* You cannot enable this feature on an existing pipeline. You must create a new pipeline.
* This feature is API-only. You cannot configure it using the Databricks UI.
* The final materialized view does not support SCD type 2. However, you can view the history of non-formula fields in the intermediary streaming table.

### Unsupported formula fields and functions

important

If a formula field in one table references a column in another table, both tables must be ingested by the same pipeline.

For example, if `table_A.column_X` is a formula field that references `table_B.column_Y`, you must configure the pipeline to ingest both `table_A` and `table_B`.

* Fields that reference tables or columns that aren't currently ingested in the pipeline are not ingested incrementally.
* The following formula functions are not supported:

  + `GETSESSIONID`
  + `RUNASUSER`
  + `CURRENCYRATE`
  + `ISCLONE`
  + `VLOOKUP`
  + `GETRECORDIDS`
  + `PARENTGROUPVAL`
  + `PREVGROUPVAL`
  + `PRIORVALUE`
  + `ISCHANGED`
  + `ISNEW`
  + `PREDICT`
  + `MLPREDICT`
  + `IMAGEPROXYURL`
  + `JUNCTIONIDLIST`
  + `LINKTO`
  + `LINKGROUPVAL`
  + `REQUIRESCRIPT`
  + `URLFOR`
  + `GEOLOCATION`
  + `DISTANCE`
  + `HTMLENCODE`
  + `JSENCODE`
  + `JSINHTMLENCODE`
  + `URLENCODE`
  + `INCLUDE`
* Rollup summary fields and formulas that reference them are not supported.
* Global entities (for example, `$User`, `$Profile`) are not supported.
* Formulas that use `ROUND(arg1, arg2)` are not supported unless `arg2` is a static integer.
* Formulas with outputs that exceed the precision `decimal(38,18)`, such as a formula that multiplies two decimals of precision `(30,18)`. These cause the pipeline to fail. To exclude them, use the `exclude_columns` configuration. See [Select columns to ingest](/aws/en/ingestion/lakeflow-connect/column-selection).

### Functions with ambiguous results

The following functions might yield different results in Databricks than in Salesforce:

| Function | Behavior difference |
| --- | --- |
| `LEN(TEXT(<decimal_number>))`, such as `LEN("123.45")` | Because Databricks is more precise than Salesforce, this function returns a different value in Databricks than in Salesforce. |
| `CHR(x)` | In Salesforce, this function returns the character with the ASCII code specified by `x`. In Databricks, it returns the character whose ASCII code equals `x` modulo 256. |
| `INITCAP("_mrSmith is _ok")` | In Salesforce, this function capitalizes the first letter of every word, ignoring non-alphabetic characters, yielding `"_MrSmith Is Ok"`. In Databricks, this function capitalizes the first character of every word only if it is a letter, yielding `"_mrSmith Is _ok"`. |
| `FORMAT_DURATION` | In Salesforce, when two date-time inputs are exactly 30 minutes apart, the formula outputs `0:00:29:59` instead of the expected `0:00:30:00`. This limitation doesn't exist in Databricks, so there might be a one-second gap between the source and destination values. |

## Create a pipeline with incremental formula fields

To enable incremental formula field ingestion, you must create a new pipeline with the configuration flag `pipelines.enableSalesforceFormulaFieldsMVComputation: true`. You cannot enable this feature on existing pipelines. For example code, see [Ingest formula fields incrementally](/aws/en/ingestion/lakeflow-connect/salesforce-pipeline#ingest-formula-fields-incrementally).

## Understand the error tracking table

When you enable incremental formula field ingestion, the connector creates an additional table to help with troubleshooting. This table always appears if the incremental formula fields flag is set, even if there are no errors. The error tracking table (named `<pipeline-id>_formula_fields_error_reasons`) has the following columns:

* `<source-object>`: The name of the source object in Salesforce.
* `<formula-field>`: The name of the formula field.
* `error`: Error message that explains why the formula wasn't ingested incrementally.

If a formula field shows `NULL` values in your destination table, query the error tracking table to understand why the field wasn't ingested incrementally. For details, see [Formula field values show as `NULL` (incremental ingestion)](/aws/en/ingestion/lakeflow-connect/salesforce-troubleshoot#null-formula-fields).