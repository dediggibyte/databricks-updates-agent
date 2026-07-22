There are a variety of sample datasets provided by Databricks and made available by third parties that you can use in your Databricks [workspace](/aws/en/admin/workspace/).

## Unity Catalog datasets

[Unity Catalog](/aws/en/data-governance/unity-catalog/) provides access to a number of sample datasets in the `samples` catalog. You can review these datasets in the [Catalog Explorer UI](/aws/en/catalog-explorer/) and reference them directly in a [notebook](/aws/en/notebooks/) or in the [SQL editor](/aws/en/sql/user/sql-editor/) by using the `<catalog-name>.<schema-name>.<table-name>` pattern.

The following table lists the available schemas in the `samples` catalog:

| Dataset | Description |
| --- | --- |
| [`databricks`](/aws/en/discover/databricks-datasets#databricks) | File-based sample datasets for building data pipelines, in the `datasets` volume. |
| [`nyctaxi`](/aws/en/discover/databricks-datasets#nyctaxi) | Taxi trip records for New York City. |
| [`tpcds_sf1`](/aws/en/discover/databricks-datasets#tpcds) | Small-scale dataset (approximately 1 GB) from the [TPC-DS benchmark](https://www.tpc.org/tpcds/). |
| [`tpch`](/aws/en/discover/databricks-datasets#tpch) | Large-scale dataset (approximately 1 TB) from the [TPC-H Benchmark](https://www.tpc.org/tpch/). |
| [`wanderbricks`](/aws/en/discover/wanderbricks-dataset) | A simulated travel booking platform with users, properties, bookings, reviews, and more. |

←✕

| Dataset | Description |
| --- | --- |
| [`databricks`](/aws/en/discover/databricks-datasets#databricks) | File-based sample datasets for building data pipelines, in the `datasets` volume. |
| [`nyctaxi`](/aws/en/discover/databricks-datasets#nyctaxi) | Taxi trip records for New York City. |
| [`tpcds_sf1`](/aws/en/discover/databricks-datasets#tpcds) | Small-scale dataset (approximately 1 GB) from the [TPC-DS benchmark](https://www.tpc.org/tpcds/). |
| [`tpch`](/aws/en/discover/databricks-datasets#tpch) | Large-scale dataset (approximately 1 TB) from the [TPC-H Benchmark](https://www.tpc.org/tpch/). |
| [`wanderbricks`](/aws/en/discover/wanderbricks-dataset) | A simulated travel booking platform with users, properties, bookings, reviews, and more. |

### databricks

The `databricks` schema contains the `datasets` volume, which hosts a collection of Databricks-provided file datasets that you can use to build and test data pipelines. To list the available datasets, run:

* SQL
* Python

SQL

```
LIST '/Volumes/samples/databricks/datasets/'
```

Python

```
display(dbutils.fs.ls("/Volumes/samples/databricks/datasets/"))
```

### nyctaxi

The `nyctaxi` schema contains the table `trips`, which has details about taxi rides in New York City. The following example returns the first 10 records in this table:

* SQL
* Python

SQL

```
SELECT * FROM samples.nyctaxi.trips LIMIT 10
```

Python

```
display(spark.read.table("samples.nyctaxi.trips").limit(10))
```

### tpcds\_sf1

The `tpcds_sf1` schema contains data from the [TPC-DS benchmark](https://www.tpc.org/tpcds/). To list the tables in this schema, run:

* SQL
* Python

SQL

```
SHOW TABLES IN samples.tpcds_sf1;
```

Python

```
display(spark.sql("SHOW TABLES IN samples.tpcds_sf1"))
```

For more guidance on how to use this dataset to evaluate system performance, see [Use the TPC-DS sample dataset to evaluate system performance](/aws/en/sql/tpcds-eval).

### tpch

The `tpch` schema contains data from the [TPC-H Benchmark](https://www.tpc.org/tpch/). To list the tables in this schema, run:

* SQL
* Python

SQL

```
SHOW TABLES IN samples.tpch
```

Python

```
display(spark.sql("SHOW TABLES IN samples.tpch"))
```

### wanderbricks

The `wanderbricks` schema contains a simulated travel booking platform dataset. For details about the `wanderbricks` dataset tables, see [Wanderbricks dataset](/aws/en/discover/wanderbricks-dataset).

## Third-party sample datasets in CSV format

Databricks has built-in tools to quickly upload third-party sample datasets as comma-separated values (CSV) files into Databricks workspaces. Some popular third-party sample datasets available in CSV format:

| Sample dataset | To download the sample dataset as a CSV file… |
| --- | --- |
| [The Squirrel Census](https://www.thesquirrelcensus.com/data) | On the **Data** webpage, click **Park Data**, **Squirrel Data**, or **Stories**. |
| [OWID Dataset Collection](https://github.com/owid/owid-datasets) | In the GitHub repository, click the **datasets** folder. Click the subfolder that contains the target dataset, and then click the dataset's CSV file. |
| [Data.gov CSV datasets](https://catalog.data.gov/dataset/?res_format=CSV) | On the search results webpage, click the target search result, and next to the **CSV** icon, click **Download**. |
| [Diamonds](https://www.kaggle.com/datasets/shivam2503/diamonds) (Requires a [Kaggle](https://www.kaggle.com/account/login) account) | On the dataset's webpage, on the **Data** tab, on the **Data** tab, next to **diamonds.csv**, click the **Download** icon. |
| [NYC Taxi Trip Duration](https://www.kaggle.com/c/nyc-taxi-trip-duration) (Requires a [Kaggle](https://www.kaggle.com/account/login) account) | On the dataset's webpage, on the **Data** tab, next to **sample\_submission.zip**, click the **Download** icon. To find the dataset's CSV files, extracts the contents of the downloaded ZIP file. |

←✕

| Sample dataset | To download the sample dataset as a CSV file… |
| --- | --- |
| [The Squirrel Census](https://www.thesquirrelcensus.com/data) | On the **Data** webpage, click **Park Data**, **Squirrel Data**, or **Stories**. |
| [OWID Dataset Collection](https://github.com/owid/owid-datasets) | In the GitHub repository, click the **datasets** folder. Click the subfolder that contains the target dataset, and then click the dataset's CSV file. |
| [Data.gov CSV datasets](https://catalog.data.gov/dataset/?res_format=CSV) | On the search results webpage, click the target search result, and next to the **CSV** icon, click **Download**. |
| [Diamonds](https://www.kaggle.com/datasets/shivam2503/diamonds) (Requires a [Kaggle](https://www.kaggle.com/account/login) account) | On the dataset's webpage, on the **Data** tab, on the **Data** tab, next to **diamonds.csv**, click the **Download** icon. |
| [NYC Taxi Trip Duration](https://www.kaggle.com/c/nyc-taxi-trip-duration) (Requires a [Kaggle](https://www.kaggle.com/account/login) account) | On the dataset's webpage, on the **Data** tab, next to **sample\_submission.zip**, click the **Download** icon. To find the dataset's CSV files, extracts the contents of the downloaded ZIP file. |

To use third-party sample datasets in your Databricks workspace, do the following:

1. Follow the third-party's instructions to download the dataset as a CSV file to your local machine.
2. [Upload the CSV file](/aws/en/ingestion/create-or-modify-table) from your local machine into your Databricks workspace.
3. To work with the imported data, use Databricks SQL to [query the data](/aws/en/sql/user/sql-editor/write-queries#create-a-query). Or you can use a [notebook](/aws/en/notebooks/) to [load the data as a DataFrame](/aws/en/delta/tutorial#read).

## Third-party sample datasets within libraries

Some third parties include sample datasets within [libraries](/aws/en/libraries/), such as [Python Package Index (PyPI)](https://pypi.org/) packages or [Comprehensive R Archive Network (CRAN)](https://cran.r-project.org/) packages. For more information, see the library provider's documentation.

* To install a library on a Databricks [cluster](/aws/en/compute/) by using the cluster user interface, see [Compute-scoped libraries](/aws/en/libraries/cluster-libraries).
* To install a Python library by using a Databricks [notebook](/aws/en/notebooks/), see [Notebook-scoped Python libraries](/aws/en/libraries/notebooks-python-libraries).
* To install an R library by using a Databricks notebook, see [Notebook-scoped R libraries](/aws/en/libraries/notebooks-r-libraries).

## Databricks datasets (databricks-datasets) mounted to DBFS

Databricks recommends against using DBFS and mounted cloud object storage for most use cases in Unity Catalog-enabled Databricks workspaces. Some sample datasets mounted to [DBFS](/aws/en/dbfs/) are available in Databricks

note

The availability and location of Databricks datasets are subject to change without notice.

### Browse DBFS mounted Databricks datasets

To browse these files from a Python, Scala, or R [notebook](/aws/en/notebooks/), you can use [Databricks Utilities (`dbutils`) reference](/aws/en/dev-tools/databricks-utils). The following code lists all of the available Databricks datasets.

* Python
* Scala
* R

Python

```
display(dbutils.fs.ls('/databricks-datasets'))
```

Scala

```
display(dbutils.fs.ls("/databricks-datasets"))
```

R

```
%fs ls "/databricks-datasets"
```