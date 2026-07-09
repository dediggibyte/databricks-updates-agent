This page introduces the SAP Business Data Cloud (BDC) Connector for Databricks, which allows you to share data from [SAP BDC](https://help.sap.com/docs/business-data-cloud) to Databricks and from Databricks to SAP BDC using [OpenSharing](/aws/en/opensharing/).

note

If you elect to use the SAP BDC Connector to share SAP BDC data to Databricks, Databricks may disclose certain usage and operations information to SAP relating to your use of that data, including identifying your organization in connection with such information. See [Usage data shared with SAP](#shared-data) for more details.

## What is the SAP BDC Connector for Databricks?

The SAP BDC Connector for Databricks enables seamless and secure data sharing between SAP BDC and the Databricks Data Intelligence Platform. With this connector, organizations can access and analyze SAP BDC data directly from their Databricks workspace that is enabled for Unity Catalog, eliminating data silos and reducing the complexity and cost of traditional data extraction.

The connector is integrated with Databricks and utilizes OpenSharing for live, zero-copy access to SAP BDC data products. OpenSharing is a secure data sharing platform that allows you to share data and AI assets.

Using OpenSharing, data remains in place and is not moved or replicated. This allows users to combine multiple data sources while maintaining full governance and auditing through Unity Catalog. Security protocols such as mutual Transport Layer Security (mTLS) and OpenID Connect (OIDC) are implemented for safe data exchanges.

## How do you share data between Databricks and SAP BDC?

To share data between Databricks and SAP BDC, a Databricks workspace admin with `CREATE PROVIDER` and `CREATE RECIPIENT` privileges and an SAP BDC admin must first establish a connection:

1. Ensure you have a workspace that is enabled for Unity Catalog. See [Get started with Unity Catalog](/aws/en/data-governance/unity-catalog/get-started).
2. Ensure you have OpenSharing set up in your workspace. See [Set up OpenSharing for your account (for providers)](/aws/en/opensharing/set-up).
3. A Databricks admin creates a connection by sending their connection identifier information to an SAP BDC admin. See [Step 1: Obtain a connection identifier for an SAP BDC admin](/aws/en/opensharing/sap-bdc/create-connection#connection-identifier).
4. The SAP BDC admin uses the connection identifier to set up a Third Party Connection and sends the invitation link back to the Databricks admin. See [the SAP BDC documentation](https://help.sap.com/docs/business-data-cloud/administering-sap-business-data-cloud/provision-sap-business-data-cloud-connector-for-supported-external-systems).
5. The Databricks admin finishes setting up the SAP BDC connection using the invitation link from the SAP BDC admin. See [Step 2: Create an SAP BDC connection](/aws/en/opensharing/sap-bdc/create-connection#create-connection).
6. Use OpenSharing to share and receive data between Databricks and SAP BDC.
   * [Create a catalog from a share](/aws/en/opensharing/read-data-databricks#create-catalog)
   * [Grant SAP Business Data Cloud (BDC) recipients access to OpenSharing data shares](/aws/en/opensharing/sap-bdc/share-to-sap).

## SAP BDC semantic metadata

When you mount SAP BDC shares to Unity Catalog catalogs on Databricks, semantic metadata such as table and column comments, primary keys, foreign keys, and governance tags syncs automatically into Unity Catalog, making SAP data more understandable and discoverable. You can use this metadata across Databricks, including in Catalog Explorer, SQL queries, Genie Agents, and governance policies.

See [SAP BDC semantic metadata](/aws/en/opensharing/sap-bdc/semantic-metadata).

## Usage data shared with SAP

Databricks may disclose to SAP certain usage and operations information relating to initial workloads on Databricks that include SAP BDC data shared by customers through the SAP BDC Connector, on an unaggregated and unanonymized, per-workload basis, for billing and administrative purposes. This information may include the volume of SAP BDC data and its ratio to non-SAP BDC data in those workloads, the date and time of those workloads, and your organization’s effective price for Databricks consumption represented by those workloads.