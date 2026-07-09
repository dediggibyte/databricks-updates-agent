This page describes HITRUST compliance controls in Databricks.

## HITRUST overview

HITRUST is a certifiable framework that integrates multiple compliance standards, including HIPAA, to help organizations manage risk and demonstrate security and privacy compliance.

## Key points

* Widely used in the healthcare industry.
* Based on a unified framework combining HIPAA, ISO, NIST, GDPR, and others.
* Offers a certifiable approach to managing risk and ensuring regulatory compliance.

## Enable HITRUST compliance controls

To configure your workspace to support processing of data regulated by the HITRUST standard, the workspace must have the compliance security profile enabled.

Only specific preview features are supported for processing regulated data. For details on the compliance security profile, supported preview features, and supported regions, see [Compliance security profile](/aws/en/security/privacy/security-profile).

You are solely responsible for verifying that sensitive information is never entered in customer-defined input fields, such as workspace names, compute resource names, tags, job names, job run names, network names, credential names, storage account names, and Git repository IDs or URLs. These fields might be stored, processed, or accessed outside the compliance boundary.

To enable HITRUST compliance controls, see [Configure enhanced security and compliance settings](/aws/en/security/privacy/enhanced-security-compliance).

## Regional support for features

This table shows feature availability for the selected compliance standard across all supported Databricks regions. Some features may be listed as available before they are actually released.

| Feature | `ap-northeast-1` | `ap-northeast-2` | `ap-southeast-1` | `ap-southeast-2` | `ap-southeast-3` | `ap-south-1` | `ca-central-1` | `eu-central-1` | `eu-west-1` | `eu-west-2` | `eu-west-3` | `sa-east-1` | `us-east-1` | `us-east-2` | `us-gov-west-1` | `us-west-1` | `us-west-2` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AI Functions - Classification | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| AI Functions - Document Parsing | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| AI Functions - Information Extraction | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| AI Functions - Prep Search |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  |  |  | ✓ |
| AI Runtime Interactive | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Anomaly Detection |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  |  |  | ✓ |
| Classic Compute | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Clean Rooms |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Data Classification |  |  |  |  |  |  |  |  |  |  |  |  | ✓ |  |  |  | ✓ |
| Databricks Apps | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Databricks One | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Default Storage | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Genie Agent Mode |  |  |  |  |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Genie Code | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Genie Code Agent Mode |  |  |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ | ✓ | ✓ | ✓ |
| Genie Code Dashboard Agent |  |  |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ | ✓ | ✓ | ✓ |
| Genie Agents | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Knowledge Assistant |  |  |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ |  | ✓ | ✓ |
| Lakebase Autoscaling |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Lakeflow Connect - Confluence |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - Dynamics 365 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lakeflow Connect - GA4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Lakeflow Connect - Google Ads |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - HubSpot |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - Meta Ads |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - MySQL | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lakeflow Connect - NetSuite |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Lakeflow Connect - PostgreSQL | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lakeflow Connect - SFTP | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lakeflow Connect - Salesforce |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - ServiceNow |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - SharePoint | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lakeflow Connect - TikTok Ads |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - Workday HCM |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - Workday Reports (RaaS) |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - Zendesk Support |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakeflow Connect - Zerobus Ingest | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lakeflow Jobs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lakeflow Pipelines Editor |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Lakehouse Monitoring |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| MLflow on Databricks | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Managed MCP Servers | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Model Serving - AI Gateway (v1) | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Model Serving - AI Guardrail | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Model Serving - AI Playground | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Model Serving - Custom Models | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Model Serving - External Models | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Model Serving - Foundation Models AI Function (ai\_query) | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Model Serving - Foundation Models Pay-Per-Token | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Predictive Optimization |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Serverless Jobs/Workflows/Notebooks |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Serverless Lakeflow Pipelines |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Serverless SQL warehouses |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✓ |
| Serverless Workspace |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  |  |  | ✓ |
| Supervisor Agent |  |  |  |  |  |  |  |  |  |  |  |  | ✓ |  |  |  | ✓ |
| Vector Search (Standard) |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  |  |  | ✓ |
| Vector Search (Storage Optimized) |  |  |  | ✓ |  |  |  |  |  |  |  |  | ✓ |  |  |  | ✓ |