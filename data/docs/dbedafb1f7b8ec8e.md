Postgres roles control access to your Postgres databases, schemas, tables, and other database objects. Use the Lakebase UI to create and manage roles for your team.

note

Before working with roles, see how to [connect](/aws/en/oltp/projects/connect) to your database and [authenticate](/aws/en/oltp/projects/authentication) using OAuth tokens or native Postgres password authentication.

## Role overview

When you create a project, a Postgres role is automatically created for your Databricks identity (for example, `user@databricks.com`). This role owns the default `databricks_postgres` database and is a member of `databricks_superuser`, giving it broad privileges to manage database objects. You can create additional roles in your project's default branch or in child branches.

note

**Postgres role state is independent between branches.** When you create a branch, it reflects the parent's Postgres roles, databases, role memberships, and grants at the time of branching. After branching, each branch evolves independently — roles and databases created, GRANTs and REVOKEs applied, and role attributes or memberships modified on one branch have no effect on any other branch, including the parent. There is no automatic synchronization of role state between branches.

**Project permissions** (CAN USE, CAN MANAGE) work differently: they apply to the entire project and all of its branches. See [Manage project permissions](/aws/en/oltp/projects/manage-project-permissions).

## Create a role

Use the **Add role** dialog in the Lakebase App to create either an OAuth role for a Databricks identity or a native Postgres password role.

### Create an OAuth role

OAuth roles are linked to a Databricks identity (user, service principal, or group) and authenticate using OAuth tokens, which expire after one hour.

When you create a child branch, it reflects the parent's role and database state at the time of branching. After that, each branch's role state evolves independently. For groups, only workspace-level groups are supported.

Optionally grant `databricks_superuser` (inherits `pg_read_all_data`, `pg_write_all_data`, and `pg_monitor`) or standard Postgres attributes (`CREATEDB`, `CREATEROLE`, `BYPASSRLS`). See [Role attributes](https://www.postgresql.org/docs/current/role-attributes.html) in the PostgreSQL documentation.

To create an OAuth role, navigate to **Roles & Databases** > **Add role** > **OAuth** tab, select an identity from the **Principal** dropdown, configure permissions, and click **Add**.

note

You can also create OAuth roles using the `databricks_auth` extension with SQL or the REST API. See [Create Postgres roles](/aws/en/oltp/projects/postgres-roles#oauth-role).

### Create a password role

Password roles use a static Postgres password and are not linked to a Databricks identity. They are useful for applications or tools that require traditional database credentials.

The Lakebase App generates a secure password automatically. Copy it immediately after creation — it is not shown again. If you need a custom password, set it later using SQL. The same optional permissions from the OAuth role apply (`databricks_superuser`, `CREATEDB`, `CREATEROLE`, `BYPASSRLS`). Role names must be valid Postgres identifiers and cannot exceed 63 characters.

To create a password role, navigate to **Roles & Databases** > **Add role** > **Password** tab, enter a role name, configure permissions, click **Add**, and copy the generated password.

## View roles

To view all roles in a branch, navigate to your branch's **Roles & Databases** tab in the Lakebase App.

## Manage password connections

Password connections are disabled by default for new Lakebase Autoscaling projects. Existing projects are not affected by this default.

To enable password connections, navigate to your project **Settings** > **Database connections** and check **Password (Native Postgres roles)**.

To disable password connections, navigate to your project **Settings** > **Database connections** and uncheck **Password (Native Postgres roles)**. Existing password roles are not deleted but cannot authenticate while password connections are disabled.

You can also control this per compute endpoint. In your branch's compute settings, select **Edit** > **Database connections** and check or uncheck **Password (Postgres roles)**.

important

This is a behavior change. If you have automation scripts or CI pipelines that create new Lakebase Autoscaling projects and rely on native Postgres password connections, you must now explicitly enable password connections after project creation.

To enable or disable password connections programmatically:

* CLI
* Python SDK
* curl

Bash

```
# Enable password connections  
databricks postgres update-project projects/<project-id> spec.enable_pg_native_login \  
  --json '{"spec": {"enable_pg_native_login": true}}'  
  
# Disable password connections  
databricks postgres update-project projects/<project-id> spec.enable_pg_native_login \  
  --json '{"spec": {"enable_pg_native_login": false}}'
```

Python

```
from databricks.sdk import WorkspaceClient  
from databricks.sdk.service.postgres import FieldMask, Project, ProjectSpec  
  
w = WorkspaceClient()  
  
# Enable password connections  
w.postgres.update_project(  
    name="projects/<project-id>",  
    project=Project(spec=ProjectSpec(enable_pg_native_login=True)),  
    update_mask=FieldMask(field_mask=["spec.enable_pg_native_login"]),  
).wait()  
  
# Disable password connections  
w.postgres.update_project(  
    name="projects/<project-id>",  
    project=Project(spec=ProjectSpec(enable_pg_native_login=False)),  
    update_mask=FieldMask(field_mask=["spec.enable_pg_native_login"]),  
).wait()
```

Bash

```
# Enable password connections  
curl -X PATCH "https://${DATABRICKS_HOST}/api/2.0/postgres/projects/<project-id>?update_mask=spec.enable_pg_native_login" \  
  -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \  
  -H "Content-Type: application/json" \  
  -d '{"spec": {"enable_pg_native_login": true}}' | jq  
  
# Disable password connections  
curl -X PATCH "https://${DATABRICKS_HOST}/api/2.0/postgres/projects/<project-id>?update_mask=spec.enable_pg_native_login" \  
  -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \  
  -H "Content-Type: application/json" \  
  -d '{"spec": {"enable_pg_native_login": false}}' | jq
```

For authentication, see [About authentication](/aws/en/oltp/projects/authentication).

## Reset a password

You can reset the password for native Postgres password roles. OAuth roles use OAuth tokens for authentication and don't have passwords to reset.

To reset a role's password:

1. Navigate to your branch's **Roles & Databases** tab in the Lakebase App.
2. Select **Reset password** from the role menu and click **Reset**.
3. Copy the new generated password.

note

Resetting a password in the Lakebase App resets the password to a generated value with 60-bit entropy. To set your own password value, you can reset the password using the [SQL editor](/aws/en/oltp/projects/sql-editor) or an SQL client like psql with the following syntax:

SQL

```
ALTER USER user_name WITH PASSWORD 'new_password';
```

The password should have at least 12 characters with a mix of lowercase, uppercase, number, and symbol characters. User-defined passwords are validated at creation time to ensure 60-bit entropy.

### Get a new OAuth token

If you're using OAuth authentication and need a new OAuth token (tokens expire after one hour), you can get one from the Connect modal:

1. Navigate to your project in the Lakebase App.
2. Click **Connect** to open the database connection modal.
3. Select your OAuth role from the **Roles** dropdown.
4. Click **Copy OAuth Token** to copy a new token.

Learn more: [Connect with an OAuth role](/aws/en/oltp/projects/connect-overview#connect-oauth) | [About authentication](/aws/en/oltp/projects/authentication)

## Delete a role

important

Deleting a role is a permanent action that cannot be undone, and you cannot delete a role that owns a database. The database must be deleted before deleting the role that owns the database.

To delete a role:

1. Navigate to your branch's **Roles & Databases** tab in the Lakebase App.
2. Select **Delete role** from the role menu and confirm the deletion.

note

Managing database roles requires the **CAN MANAGE** or **CAN USE** [project permission](/aws/en/oltp/projects/manage-project-permissions). If you don't have the required permission, you will see a "Permissions required" message when attempting a role-related action. Contact a workspace admin to request access. For more information, see [Manage project permissions](/aws/en/oltp/projects/manage-project-permissions).