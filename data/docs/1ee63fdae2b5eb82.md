Beta

Cross-engine ABAC is in [Beta](/aws/en/release-notes/release-types).

External engines can read Unity Catalog tables with fine-grained access controls enforced. This includes both [attribute-based access controls (ABAC)](/aws/en/data-governance/unity-catalog/abac/) policies and standalone [row filters and column masks](/aws/en/data-governance/unity-catalog/filters-and-masks/), all dynamically enforced even when querying from outside Databricks.

When an external engine queries a table with ABAC policies, row filters, or column masks attached, Databricks uses a specialized serverless compute layer to filter and return sanitized data to the external engine.

## Requirements

To enforce fine-grained access controls on tables queried from external engines, you must complete the following:

* Enable [external data access](/aws/en/external-access/admin) on your Unity Catalog metastore.
* Grant the querying principal the [`EXTERNAL USE SCHEMA`](/aws/en/external-access/admin#external-schema) privilege.
* Use a [managed table](/aws/en/tables/managed) with [catalog commits](/aws/en/tables/features/catalog-commits).
* Authenticate using [OAuth machine-to-machine (M2M)](/aws/en/dev-tools/auth/oauth-m2m) or a [personal access token (PAT)](/aws/en/dev-tools/auth/pat).

## Create a managed Delta table with catalog commits

To create a new managed Delta table with catalog commits (requires Databricks Runtime 16.4 and above):

SQL

```
CREATE TABLE <catalog>.<schema>.<table> (id INT, name STRING)  
TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported') USING delta;
```

To upgrade an existing managed table (requires Databricks Runtime 18.0 and above):

SQL

```
ALTER TABLE <catalog>.<schema>.<table>  
SET TBLPROPERTIES ('delta.feature.catalogManaged' = 'supported');
```

After you create the table, you can apply ABAC policies, row filters, or column masks.

See [Create a policy](/aws/en/data-governance/unity-catalog/abac/policies#create-policy) or [Manually apply row filters and column masks](/aws/en/data-governance/unity-catalog/filters-and-masks/manually-apply).

## Read tables with Apache Spark (Delta)

Configure Apache Spark with [Delta-Spark 4.1 or above](https://mvnrepository.com/artifact/io.delta/delta-spark_2.13) and [Unity Catalog Spark connector 0.4 or above](https://mvnrepository.com/artifact/io.unitycatalog/unitycatalog-spark_2.13/0.4.0).

ini

```
"spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",  
"spark.sql.catalog.spark_catalog": "io.unitycatalog.spark.UCSingleCatalog",  
"spark.sql.catalog.<uc-catalog-name>": "io.unitycatalog.spark.UCSingleCatalog",  
"spark.sql.catalog.<uc-catalog-name>.uri": "<workspace-url>",  
"spark.sql.catalog.<uc-catalog-name>.auth.type": "oauth",  
"spark.sql.catalog.<uc-catalog-name>.auth.oauth.uri": "<oauth-token-endpoint>",  
"spark.sql.catalog.<uc-catalog-name>.auth.oauth.clientId": "<oauth-client-id>",  
"spark.sql.catalog.<uc-catalog-name>.auth.oauth.clientSecret": "<oauth-client-secret>",  
"spark.sql.catalog.<uc-catalog-name>.ServerSidePlanning.enabled": "true",  
"spark.sql.defaultCatalog": "<uc-catalog-name>",  
"spark.hadoop.fs.s3.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",  
"spark.jars.packages": "io.delta:delta-spark_4.0_2.13:4.1.0,io.delta:delta-iceberg_2.13:4.1.0,io.unitycatalog:unitycatalog-spark_2.13:0.4.0,org.apache.hadoop:hadoop-aws:3.4.1"
```

note

Set `ServerSidePlanning.enabled` to `true` to enable fine-grained access control enforcement from external engines.

Substitute the following variables:

* `<uc-catalog-name>`: The name of the catalog in Unity Catalog that contains your tables.
* `<workspace-url>`: The Databricks [workspace URL](/aws/en/workspace/workspace-details#workspace-url), including the workspace ID.
* `<oauth-token-endpoint>`: OAuth token endpoint URL. See [Authorize service principal access to Databricks with OAuth](/aws/en/dev-tools/auth/oauth-m2m).
* `<oauth-client-id>`: OAuth client ID for the authenticating principal.
* `<oauth-client-secret>`: OAuth client secret for the authenticating principal.

## Read tables with Apache Spark (Iceberg)

Configure Apache Spark with [Iceberg-Spark 1.11 or above](https://iceberg.apache.org/releases/) and Apache Spark 4.0 or above.

ini

```
"spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",  
"spark.sql.catalog.<uc-catalog-name>": "org.apache.iceberg.spark.SparkCatalog",  
"spark.sql.catalog.<uc-catalog-name>.type": "rest",  
"spark.sql.catalog.<uc-catalog-name>.uri": "<workspace-url>/api/2.1/unity-catalog/iceberg-rest/",  
"spark.sql.catalog.<uc-catalog-name>.credential": "<oauth-client-id>:<oauth-client-secret>",  
"spark.sql.catalog.<uc-catalog-name>.oauth2-server-uri": "<oauth-token-endpoint>",  
"spark.sql.catalog.<uc-catalog-name>.warehouse": "<uc-catalog-name>",  
"spark.sql.catalog.<uc-catalog-name>.cache-enabled": "false",  
"spark.sql.defaultCatalog": "<uc-catalog-name>"
```

Substitute the following variables:

* `<uc-catalog-name>`: The name of the catalog in Unity Catalog that contains your tables.
* `<workspace-url>`: The Databricks [workspace URL](/aws/en/workspace/workspace-details#workspace-url), including the workspace ID.
* `<oauth-token-endpoint>`: OAuth token endpoint URL. See [Authorize service principal access to Databricks with OAuth](/aws/en/dev-tools/auth/oauth-m2m).
* `<oauth-client-id>`: OAuth client ID for the authenticating principal.
* `<oauth-client-secret>`: OAuth client secret for the authenticating principal.

## Query data

You can query the table using Apache Spark SQL or DataFrame APIs. Databricks enforces fine-grained access policies behind the scenes.

SQL

```
SELECT * FROM <uc-catalog-name>.<schema>.<table>;
```

warning

Concurrent writes during query planning can cause the same table to be read from different table snapshots in self-join and multi-scan queries, potentially resulting in incorrect results.

## Serverless compute costs

Cross-engine ABAC uses serverless compute resources to enforce fine-grained access policies server-side. Customers are charged for these resources. For pricing information, see [Beta product pricing](https://www.databricks.com/product/pricing/beta-products).

Users with access to the billing system table can query `system.billing.usage` to see how much they've been charged. For example, the following query breaks down compute costs by user:

SQL

```
SELECT usage_date,  
sku_name,  
 identity_metadata.run_as,  
SUM(usage_quantity) AS `DBUs consumed by cross-engine ABAC`  
FROM system.billing.usage  
WHERE usage_date BETWEEN '2026-06-01' AND '2026-07-01'  
 AND billing_origin_product = 'EXTERNAL_COMPATIBILITY'  
GROUP BY 1, 2, 3 ORDER BY 1;
```

## Limitations

* Only reads are supported from external engines when fine-grained access controls (FGAC) are enforced. To write, you must exempt the writing principal from the ABAC policy.
* Dynamic views are not supported.
* Projecting `VARIANT` columns is not supported.
* Filtering on `BINARY` columns is not supported.
* Column-masking functions whose return type differs from the original column type are not supported.
* Large aggregations might experience performance degradation.