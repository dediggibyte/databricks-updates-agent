info

For new use cases, Databricks recommends deploying agents on Databricks Apps for full control over agent code, server configuration, and deployment workflow. See [Author an AI agent and deploy it on Databricks Apps](/aws/en/agents/agent-framework/author-agent). To migrate an existing agent, see [Migrate an agent from Model Serving to Databricks Apps](/aws/en/agents/agent-framework/migrate-agent-to-apps).

important

**Deprecation notice**: As of December 4, 2025, Databricks no longer automatically populates the `payload_request_logs` and `payload_assessment_logs` tables. These tables have been [deprecated](/aws/en/release-notes/runtime/databricks-runtime-ver).

* Newly deployed agents via [agents.deploy()](/aws/en/agents/agent-framework/deploy-agent) will no longer generate request\_logs or assessment\_logs tables.
* Legacy request\_logs and assessment\_logs tables are no longer populated. You can create your own replacement table using materialized views. See [alternative solutions for MLflow 2](#mlflow2-alternatives).
* The legacy [experimental API](/aws/en/agents/agent-framework/feedback-model) for logging feedback will no longer be supported for agents deployed with the latest version of databricks-agents. Use the MLflow 3 [Assessments API](/aws/en/mlflow3/genai/human-feedback/dev-annotations) instead.

**Action required**:

* **Recommended**: [Upgrade to MLflow 3](#migrate-mlflow-3) to use real-time tracing, which provides unified logging with better performance.
* **Alternative**: If you must continue using MLflow 2, see [alternative solutions](#mlflow2-alternatives) to maintain access to your data.

When you deploy an AI agent, Databricks creates three inference tables that automatically capture requests and responses to and from your agent. These tables help you monitor performance, debug issues, and analyze user feedback.

| Inference table | Example Databricks table name | Table contents |
| --- | --- | --- |
| Payload | `{catalog_name}.{schema_name}.{model_name}_payload` | Raw JSON request and response payloads |
| Payload request logs | `{catalog_name}.{schema_name}.{model_name}_payload_request_logs` | Formatted request and responses. MLflow traces.  Derived from raw payload table. |
| Payload assessment logs | `{catalog_name}.{schema_name}.{model_name}_payload_assessment_logs` | Formatted feedback, as provided in the Review App, for each request  Derived from raw payload table. |

* Raw JSON data enters the payload table within one hour after your agent receives a request.
* The request logs and assessment logs tables process and format data from the payload table. This takes additional time.
* You can manually extract and process data from the payload table if needed.
* Changes to the payload table (deletions or updates) don't automatically sync to the derived tables.

## What's changing?

Databricks no longer automatically populates the `payload_request_logs` and `payload_assessment_logs` tables.

**What still works**: The raw `payload` table continues to receive data from new requests.

## Migrate to MLflow 3 and use real-time tracing to unify agent logs

Databricks strongly recommends migrating agent endpoints to use MLflow 3. MLflow 3 real-time tracing eliminates the need for separate `request_logs` and `assessment_logs` tables by unifying all of your agent logs in one trace location.

|  | **Legacy Observability** | **MLflow 3 Observability** |
| --- | --- | --- |
| **Data collection latency** | 1+ hours | <10s |
| **Data Organization** | Traces and user feedback (assessments) are extracted into separate Unity Catalog tables (`request_logs` and `assessment_logs`). | All your observability-related data, such as traces, feedback, and assessments, can easily be accessed in the same experiment. |
| **Feedback Collection** | Not well-supported. Uses the experimental feedback API, which puts data in the payload inference table. | MLflow 3 provides simplified APIs for running evaluation, human labeling, and managing evaluation datasets. |
| **Monitoring** | Not well-supported. Support is limited to now-deprecated legacy monitoring, which was limited to legacy built-in judges and guidelines judge, and has no custom metric support.  Legacy monitoring runs on top of payload request logs, meaning that your agent responses will take 1+ hours to be evaluated. | Monitoring is natively integrated with MLflow 3, supporting any Scorer:   * Built-in scorers * Custom code scorer * Custom judges   Includes metric backfill capabilities to retroactively apply new metrics to historical traces.  Traces are read from MLflow for evaluation, decreasing the latency of monitoring to 15–30 minutes. |

MLflow 3 attaches assessments to traces, then logs the traces to the MLflow tracing server together with all the payload, response, and intermediate-step logs. See [Label during development](/aws/en/mlflow3/genai/human-feedback/dev-annotations) and [Concepts & data model](/aws/en/mlflow3/genai/concepts/).

### Migration steps

1. **Upgrade to MLflow 3**: Ensure your agent uses MLflow 3.1.3 or above. Tracing will be automatically enabled when you deploy agents with MLflow 3.

Python

```
# Install prerequisites  
%pip install mlflow>=3.1.3  
  
# Restart Python to make sure the new packages are picked up  
dbutils.library.restartPython()
```

2. **Log your agent**: Log the agent as you normally would, making sure that it requires MLflow 3.1.3 or above. Then, register the model to UC.

Python

```
# Log your agent  
with mlflow.start_run():  
    logged_agent_info = mlflow.pyfunc.log_model(  
        name="my_agent",  
        pip_requirements=[  
            "mlflow>=3.1.3",  
        ],  
        ...  
    )  
  
# Register your model to UC  
uc_registered_model_info = mlflow.register_model(  
    model_uri=logged_agent_info.model_uri, name=UC_MODEL_NAME  
)
```

3. **Deploy your agent:** Deploy the agent like you normally would. Optionally, set your MLflow experiment before deployment to control where traces are logged. If you don't do this, traces will be logged to the currently active MLflow experiment.

Python

```
import mlflow  
from databricks import agents  
  
# Set experiment for trace logging  
mlflow.set_experiment("/path/to/your/experiment")  
  
# Deploy with automatic tracing  
deployment = agents.deploy(uc_model_name, uc_model_info.version)  
  
# Retrieve the query endpoint URL for making API requests  
deployment.query_endpoint
```

note

MLflow 3 currently supports up to 100,000 traces per serving endpoint. If you anticipate needing higher limits, contact your Databricks account team.

See [Trace agents deployed on Databricks](/aws/en/mlflow3/genai/tracing/prod-tracing) for more information.

## Alternative options to continue using MLflow 2

important

MLflow 2 alternative methods don't support endpoints with agent monitoring enabled. If you use monitoring, you must migrate to MLflow 3 and recreate your monitors as [MLflow 3 scorers](/aws/en/mlflow3/genai/eval-monitor/concepts/scorers#built-in-judges).

If you can't upgrade to MLflow 3, Databricks continues to populate the raw `payload` table. However, Databricks no longer processes this data into the `payload_requests_logs` and `payload_assessment_logs` tables.

Instead, Databricks generates views over your payload tables that provide the same formatted data. You have two options to access this data. Use the provided views or create materialized views.

### Option 1: Use the provided views

The simplest method is to use the generated views `payload_request_logs_view` and `payload_assessment_logs_view` in place of the deprecated tables.

These views query the payload table to provide the same formatted data, and they work immediately with no setup required.

Optionally, rename the views to match your original table names to minimize code changes.

### Option 2: Create materialized views

The provided views (`payload_request_logs_view` and `payload_assessment_logs_view`) compute data in real-time by querying the payload table. For scenarios that require physical Delta tables, like real time monitoring, create materialized views instead.

Run the following notebook to convert your views into materialized views:

#### Create materialized views for agent inference logs

[Open notebook in new tab](https://docs.databricks.com/aws/en/notebooks/source/generative-ai/materialized-views-agent-inference-logs.html)[Open in Databricks](https://login.databricks.com/signin?destination_url=%2Fopen%3Fp%3DeyJhY3Rpb24iOiJpbXBvcnRub3RlYm9vayIsInBheWxvYWQiOnsidXJsIjoiaHR0cHM6Ly9kb2NzLmRhdGFicmlja3MuY29tL2F3cy9lbi9ub3RlYm9va3Mvc291cmNlL2dlbmVyYXRpdmUtYWkvbWF0ZXJpYWxpemVkLXZpZXdzLWFnZW50LWluZmVyZW5jZS1sb2dzLmh0bWwifX0%253D&utm_source=open-in-databricks&utm_medium=docs&utm_campaign=docs%2Fagents%2Fagent-framework%2Frequest-assessment-logs&utm_content=https%3A%2F%2Fdocs.databricks.com%2Faws%2Fen%2Fnotebooks%2Fsource%2Fgenerative-ai%2Fmaterialized-views-agent-inference-logs.html)

Expand notebook

## Frequently asked questions

### What happens to the data in my existing request logs and assessment logs?

Existing data in your inference tables will continue to be accessible. However, after December 4, 2025, no new data will be populated into `request_logs` and `assessment_logs` tables.

### Does my agent deployment break?

No, your old agent deployments continue to work, and your payload inference tables continue to be populated. However, after the deprecation dates, you won't receive data in the `request_logs` and `assessment_logs` tables. Use the provided views or migrate to MLflow 3 to maintain equivalent functionality.

If you need assistance with migration, contact your Databricks support team.

## Additional resources

* [Deploy your agent with tracing using MLflow 3](/aws/en/mlflow3/genai/tracing/prod-tracing)
* [Learn about MLflow 3 assessment APIs](/aws/en/mlflow3/genai/human-feedback/dev-annotations)
* [Set up production monitoring for Gen AI](/aws/en/mlflow3/genai/eval-monitor/production-monitoring)