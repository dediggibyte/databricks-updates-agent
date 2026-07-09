Preview

The MySQL connector is in Public Preview. Contact your Databricks account team to request access.

Learn how to configure MySQL for ingestion into Databricks using Lakeflow Connect. The MySQL connector uses binary log (binlog) replication to capture changes from your MySQL database and incrementally syncs them to Databricks.

## Requirements

Before you configure MySQL for ingestion, verify that your environment meets the following requirements:

* **Supported database versions**:
  + Amazon RDS: 5.7.44 and later (both standalone and HA deployments)
  + Amazon Aurora: 5.7.mysql\_aurora.2.12.2 and later (for HA setups, support is only from primary instance)
  + Amazon Aurora Serverless: Supported
  + Azure Database for MySQL Flexible Servers: 5.7.44 and later (both standalone and HA deployments)
  + MySQL on EC2: 5.7.44 and later
  + GCP Cloud SQL: 5.7.44 and later
* **Binary logging configuration**: The following server configurations are required:
  + Enable binary logging.
  + Set the binlog format to `ROW`.
  + Set the binlog row image to `FULL`.
* Access to create a MySQL user with replication privileges.
* Network connectivity from Databricks to your MySQL instance.

## Overview of source setup tasks

Complete the following tasks to configure MySQL for ingestion:

1. **Configure MySQL server parameters** to enable binary logging and set the correct format.

   The configuration steps vary by deployment type:

   * [AWS RDS and Aurora MySQL](/aws/en/ingestion/lakeflow-connect/mysql-aws-rds-config)
   * [Azure Database for MySQL](/aws/en/ingestion/lakeflow-connect/mysql-azure-config)
   * [MySQL on EC2](/aws/en/ingestion/lakeflow-connect/mysql-ec2-config)
   * [Google Cloud SQL for MySQL](/aws/en/ingestion/lakeflow-connect/mysql-gcp-config)
2. **Create a MySQL user** with the required privileges for replication. See [Grant MySQL user privileges](/aws/en/ingestion/lakeflow-connect/mysql-privileges).
3. **Configure networking** to allow Databricks to connect to your MySQL instance. This might include configuring firewall rules, security groups, or network peering.

   See [Configure firewall settings for AWS SQL Database](/aws/en/ingestion/lakeflow-connect/aws-sql-db-firewall) for information about IP addresses to allowlist.

## Read replica support

The MySQL connector supports ingesting from read replicas for the following deployment types:

* Amazon RDS for MySQL
* Azure Database for MySQL
* MySQL on EC2

warning

The connector does **not** support ingesting from Amazon Aurora MySQL read replicas. You must connect to the primary instance for Aurora deployments.

Using a read replica can reduce load on your primary database. However, there might be a replication lag between the primary database and replica, which can affect data freshness.