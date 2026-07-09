This page describes how to configure Git integration for Databricks Git folders, including credentials, network connectivity, and security features. To create a Git folder and start working with Git operations, see [Create and manage Git folders](/aws/en/repos/git-operations-with-repos).

important

Use Git folders for interactive development. For CI/CD and production deployments, use Declarative Automation Bundles with versioned artifacts and workload identity federation. See [CI/CD with Databricks Git folders](/aws/en/repos/ci-cd) and [What are Declarative Automation Bundles?](/aws/en/dev-tools/bundles/).

## Prerequisites

Before you begin, confirm the following:

* Git folders are enabled in your workspace (enabled by default). See [Enable or disable Databricks Git folders](/aws/en/repos/enable-disable-repos-with-api).
* You have a Git provider account (GitHub, GitLab, Azure DevOps, Bitbucket, or AWS CodeCommit).
* For private repositories or write operations, you have a personal access token (PAT) or OAuth credentials from your Git provider. See [Connect your Git provider to Databricks](/aws/en/repos/get-access-tokens-from-git-provider).

  note

  You can clone public remote repositories without Git credentials. To modify a public remote repository or to work with private repositories, configure Git credentials with **Write** permissions.

## Add Git credentials

To configure Git credentials in Databricks:

1. Click your username in the top bar of the Databricks workspace and select **Settings**.
2. Click **Linked accounts**.
3. Click **Add Git credential**.
4. Select your Git provider from the drop-down menu. Some providers offer OAuth account linking, while others require a personal access token (PAT). If you link your account using OAuth, complete the authentication flow and skip to the last step.
5. Enter your email in the **Git provider email** field.
6. Paste your PAT in the **Token** field. For instructions on creating a PAT, see [Connect your Git provider to Databricks](/aws/en/repos/get-access-tokens-from-git-provider). If your organization has SAML SSO enabled in GitHub, [authorize your personal access token for SSO](https://docs.github.com/en/github/authenticating-to-github/authorizing-a-personal-access-token-for-use-with-saml-single-sign-on).
7. Click **Save**.

You can also manage Git credentials using the [Databricks Repos API](https://docs.databricks.com/api/workspace/repos).

### Azure DevOps

Git integration doesn't support Microsoft Entra ID tokens. You must use an Azure DevOps personal access token. See [Personal access token](/aws/en/repos/get-access-tokens-from-git-provider#diff-tenancy).

## Multiple Git credentials per user

Databricks lets each user store multiple Git credentials, so you can use different providers or accounts without having to switch credentials.

### Select credentials for Git folders

Each Git folder can use a specific credential for Git operations. To change the credential for a Git folder:

1. Open the Git folder and go to the **Git settings** tab.
2. Under **Git credential**, select a credential from the drop-down menu.
3. Click **Save**.

### How default credentials work

Each Git provider supports one default Git credential per user. Databricks automatically uses this default credential for:

* [Jobs](/aws/en/jobs/git)
* [Repos API](https://docs.databricks.com/api/workspace/repos) operations
* Git folder operations (when no specific credential is selected)

The first credential you create for a provider automatically becomes the default. To change your default credential:

1. Go to **User Settings** > **Linked accounts**.
2. Click the kebab  next to the credential that you want to make default.
3. Select **Set as default**.

### Limitations

* Jobs that require a non-default Git credential for a provider must use a service principal.
* The Databricks GitHub App allows only one [linked credential](/aws/en/repos/get-access-tokens-from-git-provider#github-link-account).
* Each user can have a maximum of 10 Git credentials.

## Configure Git commit identity

Your Git commit identity determines how commits made from Databricks appear in your Git provider. When you commit through Databricks Git folders, your Git provider needs to identify you as the author. Configure your email address so that:

* Commits appear in your Git provider profile
* Your profile picture and name display correctly
* You receive proper credit for contributions
* Team members can track who made each change

### How commit identity works

When you configure Git credentials with an email address:

* **Email:** Becomes the author email (`GIT_AUTHOR_EMAIL` and `GIT_COMMITTER_EMAIL`) for all commits
* **Username:** Becomes the committer name (`GIT_AUTHOR_NAME` and `GIT_COMMITTER_NAME`)

If you don't specify an email address, Databricks uses your Git username as the email. This can prevent proper commit attribution in your Git provider.

**Example commit in Git history:**

```
commit 480ee5b0214e4d46db2da401a83794c5f5c5d375 (HEAD -> main)  
Author: GitHub-username <your.email@example.com>  
Date:   Fri Sep 26 00:38:23 2025 -0700  
  
    My commit message
```

**Example in Git provider:**

note

If you created Git credentials before email configuration was available, your email field defaults to your username. Update it to your actual email address for proper commit attribution.

### Linked GitHub credentials

If you use linked Git credentials through the [Databricks GitHub app](https://github.com/apps/databricks), Databricks automatically configures your email and Git identity. If your identity isn't set correctly, [Approve the required permissions](/aws/en/release-notes/product/2025/october#new-permissions-for-the-databricks-github-app) or re-link your GitHub account for proper permissions.

## Configure network connectivity

Git folders require network connectivity to your Git provider. Most configurations work over the internet without additional setup. However, you might need extra configuration if you have:

* IP allowlists on your Git provider
* Self-hosted Git servers (GitHub Enterprise, Bitbucket Server, GitLab Self-managed)
* Private network hosting

Git folders with [Git CLI access](/aws/en/repos/git-operations-with-repos#use-git-cli) run UI-based Git operations on serverless compute. Workspace admins must ensure that serverless compute can reach your Git provider.

To connect serverless compute to a private Git server, configure a network connectivity configuration (NCC) with private endpoint rules. See [Configure Databricks Serverless Private Git](/aws/en/repos/serverless-private-git) for setup steps. You don't need to enable the Serverless Private Git preview to use NCC connectivity.

To enable serverless compute, see [Connect to serverless compute](/aws/en/compute/serverless/).

### Configure IP allowlists

If your Git server is internet-accessible but uses an IP allowlist, such as [GitHub allow lists](https://docs.github.com/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/managing-allowed-ip-addresses-for-your-organization):

1. Find your Databricks control plane network address translation (NAT) IP address for your region at [Databricks clouds and regions](/aws/en/resources/supported-regions).
2. Add this IP address to your Git server's IP allowlist.

### Configure private Git servers

If you host a private Git server, see [Set up private Git connectivity for Databricks Git folders](/aws/en/repos/git-proxy) or contact your Databricks account team for setup instructions.

## Security features

Databricks Git folders include the following security features to protect your code and credentials:

### Encrypt Git credentials

Use AWS Key Management Service (KMS) to encrypt Git personal access tokens and other Git credentials with your own encryption keys (customer managed keys).

For more information, see [Customer-managed keys for managed services](/aws/en/security/keys/customer-managed-keys#managed-services).

### Git URL allowlists

Workspace admins can restrict which remote repositories users can access. This helps prevent code exfiltration and enforces use of approved repositories.

#### Set up a Git URL allowlist

To configure an allowlist:

1. Click your username in the top bar of the Databricks workspace and select **Settings**.
2. Click **Development**.
3. Select a **Git URL allow list permission** option:

   * **Disabled (no restrictions):** No allowlist enforcement.
   * **Restrict Clone, Commit & Push to Allowed Git Repositories:** Restricts all operations to allowlist URLs.
   * **Only Restrict Commit & Push to Allowed Git Repositories:** Restricts only write operations. Clone and pull remain unrestricted.
4. Click the edit icon  next to **Git URL allowlist: Empty list**.
5. Enter a comma-separated list of URL prefixes. Databricks uses prefix matching (case-insensitive) to allow repository access. Wildcards aren't supported.

   **Examples:**

   * `https://github.com` - Allows all GitHub repositories
   * `https://github.com/CompanyName` - Restricts to specific organization
   * `https://dev.azure.com/CompanyName` - Restricts to Azure DevOps organization

   Don't enter URLs with user names or authentication tokens, as they might be replicated globally and can block your users from working with Git folders.
6. Click **Save**.

Saving a new list overwrites the existing allowlist. Changes can take up to 15 minutes to take effect.

### Access control

note

Only the [Premium plan or above](https://databricks.com/product/pricing/platform-addons) includes access control.

Control who can access Git folders in your workspace by setting permissions. Permissions apply to all content within a Git folder. Assign one of the following permission levels:

* `NO PERMISSIONS`: No access to the Git folder
* `CAN READ`: View files only
* `CAN RUN`: View and run files
* `CAN EDIT`: View, run, and modify files
* `CAN MANAGE`: Full control including sharing and deleting

For detailed information about Git folder permissions, see [Git folder ACLs](/aws/en/security/auth/access-control/#git-folders).

### Audit logging

When you enable [audit logging](/aws/en/admin/account-settings/audit-logs), Databricks logs all Git folder operations, including:

* Creating, updating, or deleting Git folders
* Listing Git folders in a workspace
* Syncing changes between Git folders and remote repositories

### Secrets detection

Git folders automatically scan code for exposed credentials before commits. It warns you if it detects:

* AWS access key IDs starting with `AKIA`
* Other sensitive credential patterns

## Additional resources

After setting up Git folders, explore these related topics:

* [Create and manage Git folders](/aws/en/repos/git-operations-with-repos)
* [What are workspace files?](/aws/en/files/workspace)
* [CI/CD with Databricks Git folders](/aws/en/repos/ci-cd)
* [Set up private Git connectivity for Databricks Git folders](/aws/en/repos/git-proxy)
* [Create and run your first dbt job](/aws/en/jobs/how-to/use-dbt-in-workflows#first-dbt-job)
* [Collaborate on bundles in the workspace](/aws/en/dev-tools/bundles/workspace)