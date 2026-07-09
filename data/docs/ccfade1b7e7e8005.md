Add Lakebase databases as Databricks Apps resources to persist data across deployments. These PostgreSQL-backed resources let your app create and manage schemas and tables that retain state.

The following types of Lakebase database resources are available:

* **Lakebase Autoscaling**: Organizes resources as [projects](/aws/en/oltp/projects/) containing branches and databases.

* **Lakebase Provisioned**: Organizes resources as [database instances](/aws/en/oltp/instances/).

Both types use the same PostgreSQL connection model and provide the same environment variables to your app.

## Add a database resource

Before you add a Lakebase database as a resource, review the [app resource prerequisites](/aws/en/dev-tools/databricks-apps/resources#resources-prereqs).

note

You can't create new Provisioned databases after March 12, 2026, but you can add existing ones as app resources. See [Upgrade to Autoscaling](/aws/en/oltp/upgrade-to-autoscaling).

1. In the **App resources** section when you create or edit an app, click **+ Add resource** > **Database**.
2. Choose a database. For Lakebase Autoscaling, select a project, branch, and database. For Lakebase Provisioned, select a database instance and a database within that instance.
3. Select the appropriate permission level for your app. Currently, the only available permission is **Can connect and create**.
4. (Optional) Specify a custom resource key, which is how you reference the database in your app configuration. The default key is `postgres` for Lakebase Autoscaling and `database` for Lakebase Provisioned.

You must have `CAN MANAGE` permission on the Lakebase project to add it as an app resource.

When you add a database resource:

* Databricks creates a PostgreSQL role in the selected database. The role name matches the [service principal's](/aws/en/dev-tools/databricks-apps/auth#app-authorization) client ID. If the role already exists, Databricks reuses it.
* Databricks grants the service principal `CONNECT` and `CREATE` privileges on the selected database. These privileges let the app create schemas and tables in the database.
* For Lakebase Autoscaling, the user adding the resource must have `CAN MANAGE` permission on the project.

## Environment variables

When you deploy an app with a database resource, Databricks sets the following environment variables for the first database resource.

If your app uses multiple PostgreSQL databases, these variables only reflect the first one. Use `valueFrom` with the resource key to retrieve the connection details for the database. See [Use environment variables to access resources](/aws/en/dev-tools/databricks-apps/environment-variables#access-resources).

| Variable | Description |
| --- | --- |
| `PGAPPNAME` | App name |
| `PGDATABASE` | Name of the database |
| `PGHOST` | Host name of the PostgreSQL server |
| `PGPORT` | Port for the PostgreSQL server |
| `PGSSLMODE` | SSL mode for the connection |
| `PGUSER` | Service principal's client ID and role name |

## Remove a database resource

If you remove database resources from an app, the app attempts to reassign all objects owned by the service principal to the user removing the resource.

The logic that the app uses primarily depends on whether you have a role in the database:

| Your permissions | Role in database? | Result |
| --- | --- | --- |
| `CAN MANAGE` | Yes | Databricks reassigns all objects owned by the service principal to you and deletes the service principal's role. |
| `CAN MANAGE` | No | Databricks creates a role for you, reassigns all objects owned by the service principal's role to you, and deletes the service principal's role. |
| *No `CAN MANAGE`* | N/A | Databricks removes the resource, but does not delete the role or reassign ownership. A warning appears in the UI, and you must manually clean up the role and owned objects later. |

## Notes

Consider the following when you add databases as app resources:

* If you revoke `CONNECT` and `CREATE` from one database and grant them on another in the same update, Databricks updates the privileges but doesn't recreate the service principal's role.
* Databases persist state. Any schemas or tables created by an app remain even after you re-deploy or stop the app.

* If you have an existing app that uses a Lakebase Provisioned `database` resource, it continues to work after [upgrading to Autoscaling](/aws/en/oltp/upgrade-to-autoscaling). Connection details, environment variables, and Postgres roles are unchanged. For new apps, [add a Lakebase Autoscaling database resource](#lakebase-add).

  important

  Do not change a `database` resource to `postgres` in an existing app configuration. The `database` and `postgres` resource types create separate Postgres roles. Changing the type creates a new role and breaks your app's access to existing data.