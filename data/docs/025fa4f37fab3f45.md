note

The `lakeflow` schema was previously known as `workflow`. The content of both schemas is identical.

This article is a reference for the `lakeflow` system tables, which record job activity in your account. These tables include records from all workspaces in your account deployed in the same cloud region. To see records from another region, you must view the tables from a workspace deployed in that region.

## Requirements

* To access these system tables, users must either:
  + Be both a metastore admin and an account admin, or
  + Have `USE` and `SELECT` permissions on the system schemas. See [Grant access to system tables](/aws/en/admin/system-tables/#grant-access).

## Available jobs tables

All job-related system tables live in the `system.lakeflow` schema. Currently, the schema hosts six tables:

| Table | Description | Supports streaming | Free retention period | Includes global or regional data |
| --- | --- | --- | --- | --- |
| [jobs](#jobs) | Tracks all jobs created in the account | Yes | 365 days | Regional |
| [job\_tasks](#job-tasks) | Tracks all job tasks that run in the account | Yes | 365 days | Regional |
| [job\_run\_timeline](#runs) | Tracks the job runs and related metadata | Yes | 365 days | Regional |
| [job\_task\_run\_timeline](#task-timeline) | Tracks job task runs and related metadata | Yes | 365 days | Regional |
| [pipelines](#pipelines) (Public Preview) | Tracks all pipelines created in the account | Yes | 365 days | Regional |
| [pipeline\_update\_timeline](#pipeline-update-timeline) (Public Preview) | Tracks the pipeline updates and related metadata | Yes | 365 days | Regional |

note

In addition to the 365-day retention window, Databricks retains the most recent record for each entity in the slowly changing dimension (SCD2) tables (`jobs`, `job_tasks`, and `pipelines`). This means the latest historical entry for each `job_id`, `job_task`, or `pipeline_id` is always available, even if it is older than 365 days. Records beyond the 365-day window other than the latest entry per entity are removed.

## Detailed schema reference

The following sections provide schema references for each of the jobs-related system tables.

### Jobs table schema

The `jobs` table is a slowly changing dimension table (SCD2). When a row changes, a new row is emitted, logically replacing the previous one.

**Table path**: `system.lakeflow.jobs`

| Column name | Data type | Description | Notes |
| --- | --- | --- | --- |
| `account_id` | string | The ID of the account this job belongs to |  |
| `workspace_id` | string | The ID of the workspace this job belongs to |  |
| `job_id` | string | The ID of the job | Only unique within a single workspace |
| `name` | string | The user-supplied name of the job |  |
| `description` | string | The user-supplied description of the job | This field is empty if you have [customer-managed keys](https://docs.databricks.com/en/security/keys/customer-managed-keys.html) configured. |
| `creator_id` | string | The ID of the principal who created the job |  |
| `tags` | map | The user-supplied custom tags associated with this job |  |
| `change_time` | timestamp | The time when the job was last modified | Timezone recorded as +00:00 (UTC) |
| `delete_time` | timestamp | The time when the job was deleted by the user | Timezone recorded as +00:00 (UTC) |
| `run_as` | string | The ID of the user or service principal whose permissions are used for the pipeline update |  |
| `trigger` | struct | The trigger configuration for the job | Not populated for rows emitted before early December 2025 |
| `trigger_type` | string | The type of trigger for the job | Not populated for rows emitted before early December 2025 |
| `run_as_user_name` | string | The email of the user, the ID of the service principal, or group name whose permissions are used for the job run | Not populated for rows emitted before early December 2025 |
| `creator_user_name` | string | The email of the user, the ID of the service principal, or group name who created the job | Not populated for rows emitted before early December 2025 |
| `paused` | boolean | Indicates whether the job is paused | Not populated for rows emitted before early December 2025 |
| `timeout_seconds` | long | The timeout duration for the job in seconds | Not populated for rows emitted before early December 2025 |
| `health_rules` | array | Set of health rules defined for this job | Not populated for rows emitted before early December 2025 |
| `deployment` | struct | Deployment information for jobs managed by external sources | Not populated for rows emitted before early December 2025 |
| `create_time` | timestamp | The time at which this job was created. Timezone recorded as +00:00 (UTC). | Not populated for rows emitted before early December 2025 |

#### Example query

SQL

```
-- Get the most recent version of a job  
SELECT  
  *,  
  ROW_NUMBER() OVER(PARTITION BY workspace_id, job_id ORDER BY change_time DESC) as rn  
FROM  
  system.lakeflow.jobs QUALIFY rn=1
```

### Job task table schema

The job tasks table is a slowly changing dimension table (SCD2). When a row changes, a new row is emitted, logically replacing the previous one.

**Table path**: `system.lakeflow.job_tasks`

| Column name | Data type | Description | Notes |
| --- | --- | --- | --- |
| `account_id` | string | The ID of the account this job belongs to |  |
| `workspace_id` | string | The ID of the workspace this job belongs to |  |
| `job_id` | string | The ID of the job | Only unique within a single workspace |
| `task_key` | string | The reference key for a task in a job | Only unique within a single job |
| `depends_on_keys` | array | The task keys of all upstream dependencies of this task |  |
| `change_time` | timestamp | The time when the task was last modified | Timezone recorded as +00:00 (UTC) |
| `delete_time` | timestamp | The time when a task was deleted by the user | Timezone recorded as +00:00 (UTC) |
| `timeout_seconds` | long | The timeout duration for the task in seconds | Not populated for rows emitted before early December 2025 |
| `health_rules` | array | Set of health rules defined for this job task | Not populated for rows emitted before early December 2025 |

#### Example query

SQL

```
-- Get the most recent version of a job task  
SELECT  
  *,  
  ROW_NUMBER() OVER(PARTITION BY workspace_id, job_id ORDER BY change_time DESC) as rn  
FROM  
  system.lakeflow.job_tasks QUALIFY rn=1
```

### Job run timeline table schema

The job run timeline table is immutable and complete at the time it is produced.

**Table path**: `system.lakeflow.job_run_timeline`

| Column name | Data type | Description | Notes |
| --- | --- | --- | --- |
| `account_id` | string | The ID of the account this job belongs to |  |
| `workspace_id` | string | The ID of the workspace this job belongs to |  |
| `job_id` | string | The ID of the job | This key is only unique within a single workspace |
| `run_id` | string | The ID of the job run |  |
| `period_start_time` | timestamp | The start time for the run or for the time period | Timezone information is recorded at the end of the value with `+00:00` representing UTC. For details on how Databricks slices long runs into hourly intervals, see [timeline slicing logic](#run-timeline-slicing-logic). |
| `period_end_time` | timestamp | The end time for the run or for the time period | Timezone information is recorded at the end of the value with `+00:00` representing UTC. For details on how Databricks slices long runs into hourly intervals, see [timeline slicing logic](#run-timeline-slicing-logic). |
| `trigger_type` | string | The type of trigger that can fire a run | For possible values, see [Trigger type values](#trigger) |
| `run_type` | string | The type of job run | For possible values, see [Run type values](#run-type) |
| `run_name` | string | The user-supplied run name associated with this job run |  |
| `compute_ids` | array | Array containing the job compute IDs for the parent job run | Use for identifying the job cluster used by `WORKFLOW_RUN` run types. For other compute information, refer to the `job_task_run_timeline` table. |
| `result_state` | string | The outcome of the job run | For runs longer than one hour that are split across multiple rows, this column is populated only in the row that represents the end of the run. For possible values, see [Result state values](#result). |
| `termination_code` | string | The termination code of the job run | For runs longer than one hour that are split across multiple rows, this column is populated only in the row that represents the end of the run. For possible values, see [Termination code values](#termination). |
| `job_parameters` | map | The job-level parameters used in the job run | Contains only the values from [job\_parameters](https://docs.databricks.com/api/workspace/jobs/runnow#job_parameters). Deprecated parameter fields (`notebook_params`, `python_params`, `python_named_params`, `spark_submit_params`, and `sql_params`) are not included. |
| `source_task_run_id` | string | The ID of the source task run. Use this column to identify which task run triggered this job run. | Not populated for rows emitted before early December 2025 |
| `root_task_run_id` | string | The ID of the root task run. Use this column to identify which task run triggered this job run. | Not populated for rows emitted before early December 2025 |
| `compute` | array | Details about the compute resources used in the job run | Not populated for rows emitted before early December 2025 |
| `termination_type` | string | The type of termination for the job run | Not populated for rows emitted before early December 2025 |
| `setup_duration_seconds` | long | The duration of the setup phase for the job run in seconds | Not populated for rows emitted before early December 2025 |
| `queue_duration_seconds` | long | The duration spent in the queue for the job run in seconds | Not populated for rows emitted before early December 2025 |
| `run_duration_seconds` | long | The total duration of the job run in seconds | Not populated for rows emitted before early December 2025 |
| `cleanup_duration_seconds` | long | The duration of the cleanup phase for the job run in seconds | Not populated for rows emitted before early December 2025 |
| `execution_duration_seconds` | long | The duration of the execution phase for the job run in seconds | Not populated for rows emitted before early December 2025 |

#### Example query

SQL

```
-- This query gets the daily job count for a workspace for the last 7 days:  
SELECT  
  workspace_id,  
  COUNT(DISTINCT run_id) as job_count,  
  to_date(period_start_time) as date  
FROM system.lakeflow.job_run_timeline  
WHERE  
  period_start_time > CURRENT_TIMESTAMP() - INTERVAL 7 DAYS  
GROUP BY ALL  
  
-- This query returns the daily job count for a workspace for the last 7 days, distributed by the outcome of the job run.  
SELECT  
  workspace_id,  
  COUNT(DISTINCT run_id) as job_count,  
  result_state,  
  to_date(period_start_time) as date  
FROM system.lakeflow.job_run_timeline  
WHERE  
  period_start_time > CURRENT_TIMESTAMP() - INTERVAL 7 DAYS  
  AND result_state IS NOT NULL  
GROUP BY ALL  
  
-- This query returns the average time of job runs, measured in seconds. The records are organized by job. A top 90 and a 95 percentile column show the average lengths of the job's longest runs.  
with job_run_duration as (  
    SELECT  
        workspace_id,  
        job_id,  
        run_id,  
        CAST(SUM(period_end_time - period_start_time) AS LONG) as duration  
    FROM  
        system.lakeflow.job_run_timeline  
    WHERE  
      period_start_time > CURRENT_TIMESTAMP() - INTERVAL 7 DAYS  
    GROUP BY ALL  
)  
SELECT  
    t1.workspace_id,  
    t1.job_id,  
    COUNT(DISTINCT t1.run_id) as runs,  
    MEAN(t1.duration) as mean_seconds,  
    AVG(t1.duration) as avg_seconds,  
    PERCENTILE(t1.duration, 0.9) as p90_seconds,  
    PERCENTILE(t1.duration, 0.95) as p95_seconds  
FROM  
    job_run_duration t1  
GROUP BY ALL  
ORDER BY mean_seconds DESC  
LIMIT 100  
  
-- This query provides a historical runtime for a specific job based on the `run_name` parameter. For the query to work, you must set the `run_name`.  
SELECT  
  workspace_id,  
  run_id,  
  SUM(period_end_time - period_start_time) as run_time  
FROM system.lakeflow.job_run_timeline  
WHERE  
  run_type="SUBMIT_RUN"  
  AND run_name = :run_name  
  AND period_start_time > CURRENT_TIMESTAMP() - INTERVAL 60 DAYS  
GROUP BY ALL  
  
-- This query collects a list of retried job runs with the number of retries for each run.  
with repaired_runs as (  
    SELECT  
    workspace_id, job_id, run_id, COUNT(*) - 1 as retries_count  
    FROM system.lakeflow.job_run_timeline  
    WHERE result_state IS NOT NULL  
    GROUP BY ALL  
    HAVING retries_count > 0  
    )  
SELECT  
    *  
FROM repaired_runs  
ORDER BY retries_count DESC  
    LIMIT 10;
```

### Job task run timeline table schema

The job task run timeline table is immutable and complete at the time it is produced.

**Table path**: `system.lakeflow.job_task_run_timeline`

| Column name | Data type | Description | Notes |
| --- | --- | --- | --- |
| `account_id` | string | The ID of the account this job belongs to |  |
| `workspace_id` | string | The ID of the workspace this job belongs to |  |
| `job_id` | string | The ID of the job | Only unique within a single workspace |
| `run_id` | string | The ID of the task run |  |
| `job_run_id` | string | The ID of the job run |  |
| `parent_run_id` | string | The ID of the parent run |  |
| `period_start_time` | timestamp | The start time for the task or for the time period | Timezone information is recorded at the end of the value with `+00:00` representing UTC. For details on how Databricks slices long runs into hourly intervals, see [timeline slicing logic](#run-timeline-slicing-logic). |
| `period_end_time` | times