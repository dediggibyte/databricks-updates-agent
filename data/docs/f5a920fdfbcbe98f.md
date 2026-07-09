Each Databricks app runs on compute resources that determine its processing power and memory. Choose an instance size when you create or edit an app to match your workload requirements.

To run an app across multiple instances for higher availability and concurrency, see [Horizontal scaling for Databricks apps](/aws/en/dev-tools/databricks-apps/horizontal-scaling) ([Beta](/aws/en/release-notes/release-types)).

## Available instance sizes

The following instance sizes are available for Databricks apps:

| Size | CPU | Memory | Cost per hour | When to use |
| --- | --- | --- | --- | --- |
| `Medium` | Up to 2 vCPUs | 6 GB | 0.5 DBU | Standard apps with moderate resource needs, such as dashboards, simple data visualizations, and forms. Most apps work well with this size. |
| `Large` | Up to 4 vCPUs | 12 GB | 1 DBU | Apps that process large datasets in memory, handle high concurrency, or perform more intensive computations. |

If you don't specify an instance size, Databricks assigns the `Medium` size by default.

## Configure instance size

Configure the instance size when you create or edit an app.

* Create app
* Edit app

To set the instance size when you create a new app:

1. In your Databricks workspace, click the  app switcher and select **Databricks Apps**.
2. Click **+ Create app**.
3. In the **Configure** step, select an **Instance size** from the drop-down menu.
4. Complete the remaining configuration steps and click **Create app**.

To change the instance size for an existing app:

1. In your Databricks workspace, click the  app switcher and select **Databricks Apps**.
2. Click the app name.
3. Click the **Settings** tab.
4. Under **Compute**, select a different **Instance size** from the drop-down menu.
5. Click **Save**.

After you change the instance size, the app continues to run on the previous instance size until the update to the new instance size finishes. After the update finishes, the app switches over to the new size.

## Best practices for instance sizing

When you choose an instance size for your app, consider the following best practices:

* Most apps work well with the default `Medium` size. Only choose `Large` if you encounter performance issues or know your app has high resource requirements.
* Test your app with the selected instance size in a development or staging workspace before you deploy it to production.
* Consider cost implications. The `Large` instance size costs more per hour.