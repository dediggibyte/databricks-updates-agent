Beta

This feature is in [Beta](/aws/en/release-notes/release-types). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](/aws/en/admin/workspace-settings/manage-previews).

The managed TikTok Ads connector in Lakeflow Connect allows you to ingest data from TikTok Ads into Databricks.

## Feature availability

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Not supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Supported  With exceptions when your table doesn't support incremental ingestion. See [Tables that support incremental updates](/aws/en/ingestion/lakeflow-connect/tiktok-ads-reference#incremental-tables). |
| Unity Catalog governance | Supported |
| Orchestration using Databricks Workflows | Supported |
| SCD type 2 | Supported |
| API-based column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported  Requires a full refresh. |
| Automated schema evolution: New tables | Supported  If you ingest the entire schema. See the limitations on the number of tables per pipeline. |
| Maximum number of tables per pipeline | 250 |

## Authentication methods

| Authentication method | Availability |
| --- | --- |
| OAuth U2M | Supported |
| OAuth M2M | Not supported |
| OAuth (manual refresh token) | Not supported |
| Basic authentication (username/password) | Not supported |
| Basic authentication (API key) | Not supported |
| Basic authentication (service account JSON key) | Not supported |

## What to know before you start

| Topic | Why it matters |
| --- | --- |
| [Databricks user persona](/aws/en/connect/managed-ingestion) | The workflow depends on your Databricks user persona:   * Single-user: An admin user creates a Unity Catalog connection and an ingestion pipeline. * Multi-user: An admin user creates a connection for non-admin users to create pipelines with. |
| [Authentication method](#authentication-methods) | The steps to create a connection depend on the authentication method you choose. |
| [Interface](/aws/en/ingestion/lakeflow-connect/faq) | The steps to create a pipeline depend on the interface. |
| [Ingestion frequency](/aws/en/ldp/pipeline-mode) | The pipeline schedule depends on your latency and cost requirements. |
| [Common patterns](/aws/en/ingestion/lakeflow-connect/common-patterns) | Depending on your ingestion needs, the pipeline might use configurations like history tracking, column selection, and row filtering. Supported configurations vary by connector. See [Feature availability](#feature-availability). |

## Start ingesting from TikTok Ads

The following table provides an overview of the end-to-end TikTok Ads ingestion flow, based on user type:

| User | Steps |
| --- | --- |
| Admin | 1. Configure TikTok Ads to enable authentication from Databricks. See [Configure TikTok Ads for managed ingestion](/aws/en/ingestion/lakeflow-connect/tiktok-ads-source-setup). 2. Use Catalog Explorer to create a connection to TikTok Ads so that non-admins can create pipelines. See [Create a TikTok Ads connection](/aws/en/ingestion/lakeflow-connect/tiktok-ads-connection). |
| Non-admin | Use any supported interface to create a pipeline from an existing connection. See [Ingest data from TikTok Ads](/aws/en/ingestion/lakeflow-connect/tiktok-ads-pipeline). |