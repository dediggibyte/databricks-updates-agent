The managed HubSpot connector in Lakeflow Connect allows you to ingest data from HubSpot Marketing Hub into Databricks.

## Feature availability

| Feature | Availability |
| --- | --- |
| UI-based pipeline authoring | Supported |
| API-based pipeline authoring | Supported |
| Declarative Automation Bundles | Supported |
| Incremental ingestion | Partially supported  Some tables support incremental ingestion. Other tables require a full refresh. See [HubSpot connector reference](/aws/en/ingestion/lakeflow-connect/hubspot-reference). |
| Unity Catalog governance | Supported |
| Lakeflow Jobs | Supported |
| SCD type 2 | Supported |
| Column selection and deselection | Supported |
| API-based row filtering | Not supported |
| Automated schema evolution: New and deleted columns | Not supported |
| Automated schema evolution: Data type changes | Not supported |
| Automated schema evolution: Column renames | Not supported |
| Automated schema evolution: New tables | Supported |
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

## Start ingesting from HubSpot

The following table provides an overview of the end-to-end HubSpot ingestion flow, based on user type:

| User | Steps |
| --- | --- |
| Admin | 1. Configure HubSpot to enable authentication from Databricks. See [Configure OAuth for HubSpot ingestion](/aws/en/ingestion/lakeflow-connect/hubspot-source-setup). 2. Either:    * Use Catalog Explorer to create a connection to HubSpot so that non-admins can create pipelines. See [Create a HubSpot connection](/aws/en/ingestion/lakeflow-connect/hubspot-connection).    * Use the data ingestion UI to create a connection and a pipeline at the same time. See [Ingest data from HubSpot](/aws/en/ingestion/lakeflow-connect/hubspot-pipeline). |
| Non-admin | Use any supported interface to create a pipeline from an existing connection. See [Ingest data from HubSpot](/aws/en/ingestion/lakeflow-connect/hubspot-pipeline). |