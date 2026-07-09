To authenticate to the Databricks [REST API](https://docs.databricks.com/api/workspace), a user can create a personal access token (PAT) and use it in their REST API request. A user can also create a service principal and use it with a personal access token to call Databricks REST APIs in their CI/CD tools and automation. This article explains how Databricks admins can manage personal access tokens in their workspace. To create a personal access token, see [Authenticate with Databricks personal access tokens (legacy)](/aws/en/dev-tools/auth/pat).

## Use OAuth instead of personal access tokens

Databricks recommends you use OAuth access tokens instead of PATs for greater security and convenience. Databricks continues to support PATs, but due to their greater security risk, it is suggested that you audit your account's current PAT usage, and migrate your users and service principals to OAuth access tokens. To create an OAuth access token (instead of a PAT) to use with a service principal in automation, see [Authorize service principal access to Databricks with OAuth](/aws/en/dev-tools/auth/oauth-m2m).

Databricks recommends you minimize your personal access token exposure with the following steps:

1. Set a short lifetime for all new tokens created in your workspaces. The lifetime should be less than 90 days. By default, the maximum lifetime for all new tokens is 730 days (two years).
2. Work with your Databricks workspace administrators and users to switch to those tokens with shorter lifetimes.
3. Revoke all long-lived tokens to reduce the risk of these older tokens getting misused over time. Databricks automatically revokes all PATs for your Databricks workspaces when the token hasn't been used in 90 or more days.

## Requirements

You must be an admin to manage personal access tokens.

Databricks account admins can monitor and revoke personal access tokens across the account.

Databricks workspace admins can do the following:

* Disable personal access tokens for a workspace.
* Control which non-admin users can create tokens and use tokens.
* Set a maximum lifetime for new tokens.
* Monitor and revoke tokens in their workspace.

Managing personal access tokens in your workspace requires the [Premium plan or above](https://databricks.com/product/pricing/platform-addons).

## Monitor and revoke personal access tokens in the account

Account admins can monitor and revoke personal access tokens from the account console. The queries to monitor tokens run only when an account admin uses the token report page.

1. As an account admin, log in to the [account console](https://accounts.cloud.databricks.com).
2. In the sidebar, click **Security** and **Token report**.

   You can filter by the token owner, workspace, created date, expiration date, and date the token was last used. Use the buttons on the top of the report to filter for access tokens for inactive principals or access tokens with no expiration date.
3. To export a report to a CSV, click **Export**.
4. To revoke a token, select a token and click **Revoke**.

## Enable or disable personal access token authentication for the workspace

Personal access token authentication is enabled by default for all Databricks workspaces. You can change this setting in the workspace settings page.

When personal access tokens are disabled for a workspace, personal access tokens cannot be used to authenticate to Databricks and workspace users and service principals cannot create new tokens. No tokens are deleted when you disable personal access token authentication for a workspace. If tokens are re-enabled later, any non-expired tokens are available for use.

If you want to disable token access for a subset of users, you can keep personal access token authentication enabled for the workspace and set fine-grained permissions for users and groups. See [Control who can create and use personal access tokens](#permissions).

warning

[Partner Connect](/aws/en/partner-connect/), [partner integrations](/aws/en/integrations/), and [service principals](/aws/en/admin/users-groups/service-principals) require personal access tokens to be enabled on a workspace.

To disable the ability to create and use personal access tokens for the workspace:

1. Go to the [settings page](/aws/en/admin/admin-concepts#admin-settings).
2. Click the **Advanced** tab.
3. Click the **Personal Access Tokens** toggle.
4. Click **Confirm**.

   This change may take a few seconds to take effect.

You can also use the [Workspace configuration API](https://docs.databricks.com/api/workspace/workspaceconf) to disable personal access tokens for the workspace.

## Control who can create and use personal access tokens

Workspace admins can set permissions on personal access tokens to control which users, service principals, and groups can create and use tokens. For details on how to configure personal access token permissions, see [Manage personal access token permissions](/aws/en/security/auth/api-access-permissions).

## Set the maximum lifetime of new personal access tokens

By default, the maximum lifetime of new tokens is 730 days (two years). Set a shorter maximum token lifetime in your workspace using the [Databricks CLI](/aws/en/dev-tools/cli/) or the [Workspace configuration API](https://docs.databricks.com/api/workspace/workspaceconf). This limit applies only to new tokens.

Set `maxTokenLifetimeDays` to the maximum lifetime (in days) for new tokens, as an integer. For example:

* Databricks CLI
* Workspace configuration API
* Terraform

Bash

```
databricks workspace-conf set-status --json '{  
  "maxTokenLifetimeDays": "90"  
}'
```

Bash

```
curl -n -X PATCH "https://<databricks-instance>/api/2.0/workspace-conf" \  
  -d '{  
  "maxTokenLifetimeDays": "90"  
  }'
```

To use the Databricks Terraform provider to manage the maximum lifetime for new tokens in a workspace, see [databricks\_workspace\_conf Resource](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/workspace_conf).

Setting `maxTokenLifetimeDays` to `"0"` removes any custom lifetime limit and reverts to the system default of 730 days (two years). Use this setting to disable a previously configured custom limit.

### Personal access token expiration notifications

Databricks sends email notifications to workspace users approximately seven days before their personal access tokens expire. Users must have email-based usernames to receive these notifications. Databricks groups all expiring tokens within the same workspace together in a single email.

#### Service principal token expiration notifications

Beta

This feature is in [Beta](/aws/en/release-notes/release-types).

For service principal tokens, Databricks sends expiration notifications to workspace admins. Notifications are only sent for service principal tokens with a lifetime greater than seven days that have been used at least once.

## Monitor and revoke tokens in your workspace

This section describes how workspace admins can use the [Databricks CLI](/aws/en/dev-tools/cli/) to manage existing tokens in the workspace. You can also use the [Token Management API](https://docs.databricks.com/api/workspace/tokenmanagement). Databricks automatically revokes personal access tokens that haven't been used in 90 or more days.

### Get tokens for the workspace

To get the workspace's tokens:

* Python
* Bash

Python

```
from databricks.sdk import WorkspaceClient  
  
w = WorkspaceClient()  
  
spark.createDataFrame([token.as_dict() for token in w.token_management.list()]).createOrReplaceTempView('tokens')  
  
display(spark.sql('select * from tokens order by creation_time'))
```

Bash

```
# Filter results by a user by using the `created-by-id` (to filter by the user ID) or `created-by-username` flags.  
databricks token-management list
```

### Delete (revoke) a token a token")

To delete a token, replace TOKEN\_ID with the id of the token to delete:

Bash

```
databricks token-management delete TOKEN_ID
```

## Review token auto-scoping status

You can review a token's auto-scoping status, inferred scopes, and applied scopes using either the workspace UI or the Token API. For an overview of how auto-scoping works, see [Auto-scoping for personal access tokens](/aws/en/dev-tools/auth/pat#autoscoping).

For new tokens, you can view proposed scopes in the workspace UI. For existing tokens with all-APIs access, proposed scopes are available only through the API.

* Workspace UI
* API

1. In your Databricks workspace, click your username in the upper-right corner.
2. Click **Settings**.
3. In the left navigation pane, click **Developer**.
4. Click **Access Tokens** > **Manage**.
5. Review each token's auto-scoping status and its historical or applied scopes.

Use `GET /api/2.0/token/list` to review inferred scopes and auto-scoping state.

**New tokens**: The response includes `inferred_scopes` showing the current inferred scopes and `autoscope_state` showing the current auto-scoping state.

JSON

```
{  
  "token_infos": [  
    {  
      "token_id": "<token-id>",  
      "comment": "example autoscoping completed PAT",  
      "scopes": ["authentication"],  
      "autoscope_state": "AUTOSCOPE_STATE_COMPLETED",  
      "inferred_scopes": ["authentication"]  
    }  
  ]  
}
```

**Existing tokens**: The response includes a `backfill_scopes` field showing scopes inferred from historical API usage.

JSON

```
{  
  "token_infos": [  
    {  
      "token_id": "<token-id>",  
      "comment": "example existing all-apis PAT",  
      "backfill_scopes": ["authentication"]  
    }  
  ]  
}
```