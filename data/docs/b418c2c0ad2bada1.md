This page describes how to configure Auto Loader streams to use file notification mode to incrementally discover and ingest cloud data.

In file notification mode, Auto Loader automatically sets up a notification service and queue service that subscribes to file events from the input directory. You can use file notifications to scale Auto Loader to ingest millions of files an hour. When compared to directory listing mode, file notification mode is faster and more scalable. Also, you can switch between file notifications and directory listing at any time and still maintain exactly-once data processing guarantees.

For a complete reference of all Auto Loader configuration settings, including file notification options and cloud-specific authentication options, see [Auto Loader](/aws/en/spark/api-options#stream-reader-al).

note

Although file notification mode with file events improves cost and scalability, it does not guarantee the order in which files are discovered or processed. Design your pipelines to handle out-of-order file arrivals. For guidance, see [Handle out-of-order data](/aws/en/ingestion/cloud-object-storage/auto-loader/#handle-out-of-order-data).

## File notification mode with and without file events enabled on external locations

There are two ways to configure Auto Loader to use file notification mode:

* [(Recommended) File events](#file-events): You use a single file notification queue for all streams that process files from a given [external location](/aws/en/connect/unity-catalog/cloud-storage/#external-locations). This approach has the following advantages over the classic file notification mode:
  + Databricks can set up subscriptions and file events in your cloud storage account for you without requiring that you supply additional credentials to Auto Loader using a service credential or other cloud-specific authentication options. See  [Set up file events for an external location](/aws/en/connect/unity-catalog/cloud-storage/manage-external-locations#file-events).
  + You have fewer IAM role policies to create in your cloud storage account.
  + Because you no longer need to create a queue for each Auto Loader stream, it's easier to avoid hitting the cloud provider notification limits listed in [Cloud resources used in classic Auto Loader file notification mode](#file-notification).
  + Databricks automatically manages the tuning of resource requirements, so you don't need to tune parameters such as `cloudFiles.fetchParallelism`.
  + Cleanup functionality means that you don't need to worry as much about the lifecycle of notifications that are created in the cloud, such as when a stream is deleted or fully refreshed.
* [Classic file notification mode](#classic): You manage file notification queues for each Auto Loader stream separately. Auto Loader automatically sets up a notification service and queue service that subscribes to file events from the input directory. This is the classic approach.

If you use Auto Loader in directory listing mode, Databricks recommends migrating to file notification mode with file events. Auto Loader with file events offers significant performance improvements. Start by [enabling file events](/aws/en/connect/unity-catalog/cloud-storage/manage-external-locations#file-events) for your external location, then set `cloudFiles.useManagedFileEvents` in your Auto Loader stream configuration.

## Use file notification mode with file events

This section describes how to create and update Auto Loader streams to use file events. Databricks strongly recommends the following when using file notification mode:

* Use Unity Catalog volumes: Create a separate [external volume](/aws/en/files/volumes) for each path or subdirectory that Auto Loader loads data from. Supply volume paths (for example, `/Volumes/catalog/schema/volume`) to Auto Loader instead of cloud storage URLs (for example, `s3://bucket/path`). This improves file discovery performance because the file events service can scope file discovery to only the relevant objects, rather than iterating over all objects in the external location.
* Use a separate volume for each subpath: If you have multiple Auto Loader streams reading from different subpaths under the same external location, create a dedicated volume for each subpath instead of sharing a single volume. This avoids unnecessary file discovery overhead and helps prevent rate limiting.

### Before you begin

Setting up file events requires:

* A Databricks workspace that is enabled for Unity Catalog.
* Permission to create storage credential and external location objects in Unity Catalog.

Auto Loader streams with file events require:

* Compute on Databricks Runtime 14.3 LTS or above.

### Configuration instructions

The following instructions apply whether you are creating new Auto Loader streams or migrating existing streams to use the upgraded file notification mode with file events:

1. Create a [storage credential](/aws/en/connect/unity-catalog/cloud-storage/#storage-credentials) and [external location](/aws/en/connect/unity-catalog/cloud-storage/#external-locations) in Unity Catalog that grant access to the source location in cloud storage for your Auto Loader streams.
2. Enable file events for the external location. See  [Set up file events for an external location](/aws/en/connect/unity-catalog/cloud-storage/manage-external-locations#file-events).
3. When you create a new Auto Loader stream or edit an existing one to work with the external location:
   * If you have existing [notifications-based Auto Loader streams](#classic) that consume data from the external location, switch them off and delete the associated notification resources.
   * Ensure that `pathRewrites` is not set (this is not a common option).
   * Review the [list of settings](#settings) that Auto Loader ignores when it manages file notifications using file events. Avoid them in new Auto Loader streams and remove them from existing streams that you are migrating to this mode.
   * Set the option `cloudFiles.useManagedFileEvents` to `true` in your Auto Loader code.

For example:

Python

```
autoLoaderStream = (spark.readStream  
  .format("cloudFiles")  
  ...  
  .options("cloudFiles.useManagedFileEvents", True)  
  ...)
```

If you're using Lakeflow Spark Declarative Pipelines and you already have a pipeline with a streaming table, update it to include the `useManagedFileEvents` option:

SQL

```
CREATE OR REFRESH STREAMING LIVE TABLE <table-name>  
AS SELECT <select clause expressions>  
  FROM STREAM read_files('abfss://path/to/external/location/or/volume',  
                   format => '<format>',  
                   useManagedFileEvents => 'True'  
                   ...  
                   );
```

### Unsupported Auto Loader settings

The following Auto Loader settings are unsupported when streams use file events:

| Setting | Change |
| --- | --- |
| `useIncremental` | You no longer need to decide between the efficiency of file notifications and the simplicity of directory listing. Auto Loader with file events comes in one mode. |
| `useNotifications` | There is only one queue and storage event subscription per external location. |
| `cloudFiles.fetchParallelism` | Auto Loader with file events does not offer a manual parallelism optimization. |
| `cloudFiles.backfillInterval` | Databricks handles backfill automatically for external locations that are enabled for file events. |
| `cloudFiles.pathRewrites` | This option applies only when you mount external data locations to the DBFS, which is deprecated. |
| `resourceTags` | You should set resource tags using the cloud console. |

For managed file events best practices, see [Best practices for Auto Loader with file events](/aws/en/ingestion/cloud-object-storage/auto-loader/file-events-explained#best-practices).

### Limitations on Auto Loader with file events

The file events service optimizes file discovery by caching the most recently created files. If Auto Loader runs infrequently, this cache can expire, and Auto Loader falls back to directory listing to discover files and update the cache. To avoid this scenario, invoke Auto Loader at least once every seven days.

For a general list of limitations on file events, see  [File events limitations](/aws/en/connect/unity-catalog/cloud-storage/manage-external-locations#file-event-limitations).

## Manage file notification queues for each Auto Loader stream separately (classic)

In classic file notification mode, Auto Loader automatically sets up a dedicated notification service and queue for each stream. This approach requires you to manage notification queues per stream and supply authentication credentials for cloud resource creation. Databricks recommends file notification mode for new workloads.

note

Auto Loader consumes messages from the notification queue as it processes files, deleting each message from the queue after the corresponding file is read. This is normal operation and is the reason that Auto Loader requires `sqs:DeleteMessage` (Amazon S3), `Microsoft.Storage/storageAccounts/queueServices/queues/messages/delete` (Azure), and equivalent message-delete permissions on the queue. You don't need to drain or manage the queue manually.

important

You need elevated permissions to automatically configure cloud infrastructure for file notification mode. Contact your cloud administrator or workspace admin. See:

* [Required permissions for configuring file notification for Azure Data Lake Storage and Azure Blob Storage](#permissions-azure)
* [Required permissions for configuring file notification for Amazon S3](#permissions-s3)
* [Required permissions for configuring file notification for GCS](#permissions-gcs)

In classic file notification mode, Auto Loader automatically sets up a notification service and queue service for each stream that subscribes to file events from the input directory. You manage the notification queues for each Auto Loader stream separately.

warning

Auto Loader does not support [changing the source path](/aws/en/ingestion/cloud-object-storage/auto-loader/directory-listing-mode#change-location) in classic file notification mode. If you change the path, you might fail to ingest files that are already present in the new location at the time of the path update.

### Cloud resources used in classic Auto Loader file notification mode

Auto Loader can set up file notifications for you automatically when you set the option `cloudFiles.useNotifications` to `true` and provide the necessary permissions to create cloud resources. In addition, you might need to provide [additional options](/aws/en/spark/api-options#al-file-notification) to grant Auto Loader authorization to create these resources.

The following table lists the resources that Auto Loader creates for each cloud provider.

| Cloud Storage | Subscription Service | Queue Service | Prefix \* | Limit \*\* |
| --- | --- | --- | --- | --- |
| Amazon S3 | AWS SNS | AWS SQS | databricks-auto-ingest | 100 per S3 bucket |
| ADLS | Azure Event Grid | Azure Queue Storage | databricks | 500 per storage account |
| GCS | Google Pub/Sub | Google Pub/Sub | databricks-auto-ingest | 100 per GCS bucket |
| Azure Blob Storage | Azure Event Grid | Azure Queue Storage | databricks | 500 per storage account |

\* Auto Loader names the resources with this prefix.

\*\* How many concurrent file notification pipelines can be launched

If you must run more file-notification-based Auto Loader streams than allowed by these limits, you can use [file events](#file-events) or a service such as AWS Lambda, Azure Functions, or Google Cloud Functions to fan out notifications from a single queue that listens to an entire container or bucket into directory-specific queues.

### Classic file notification events

Amazon S3 provides an `ObjectCreated` event when a file is uploaded to an S3 bucket regardless of whether it was uploaded by a put or multi-part upload.

Azure Data Lake Storage provides different event notifications for files that appear in your storage container.

* Auto Loader listens for the `FlushWithClose` event for processing a file.
* Auto Loader streams support the `RenameFile` action for discovering files. `RenameFile` actions require an API request to the storage system to get the size of the renamed file.
* Auto Loader streams created with Databricks Runtime 9.0 and after support the `RenameDirectory` action for discovering files. `RenameDirectory` actions require API requests to the storage system to list the contents of the renamed directory.

Google Cloud Storage provides an `OBJECT_FINALIZE` event when a file is uploaded, which includes overwrites and file copies. Failed uploads do not generate this event.

note

Cloud providers do not guarantee 100% delivery of all file events under very rare conditions and do not provide strict SLAs on the latency of the file events. Databricks recommends that you trigger regular backfills with Auto Loader by using the `cloudFiles.backfillInterval` option to guarantee that all files are discovered within a given SLA if data completeness is a requirement. Triggering regular backfills does not cause duplicates.

### Required permissions for configuring file notification for Azure Data Lake Storage and Azure Blob Storage

You must have read permissions for the input directory. See [Azure Blob Storage](/aws/en/connect/storage/azure-storage).

To use file notification mode, you must provide authentication credentials for setting up and accessing the event notification services. You can authenticate using one of the following methods:

* In Databricks Runtime 16.1 and above, use a Databricks service credential: [Create service credentials](/aws/en/connect/unity-catalog/cloud-services/service-credentials) using a managed identity and a Databricks access connector.
* Create a [Microsoft Entra ID (formerly Azure Active Directory) app and service principal](https://learn.microsoft.com/azure/active-dire