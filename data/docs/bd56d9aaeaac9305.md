Preview

Context-based ingress control has the following [Beta](/aws/en/release-notes/release-types) capabilities and limitations:

* **Account-level policies**: A single context-based ingress policy can govern multiple workspaces.
* **Partner Platforms** as a network source: Allowlist the IPs that third-party apps ([Power BI](https://www.microsoft.com/download/details.aspx?id=56519), [Tableau Cloud](https://help.tableau.com/current/pro/desktop/publish_tableau_online_ip_authorization.htm), and [dbt platform](https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses)) use to connect to Databricks. Databricks manages and updates these IP lists automatically.
* Account-level policy denials are not yet logged.

note

This feature requires the [Enterprise tier](https://databricks.com/product/pricing/platform-addons).

This page provides an overview of context-based ingress control. For serverless egress control, see [What is serverless egress control?](/aws/en/security/network/serverless-network-security/network-policies).

To configure ingress policies, see [Manage context-based ingress policies](/aws/en/security/network/front-end/manage-ingress-policies).

## Context-based ingress control overview

Context-based ingress control works alongside IP access lists and frontend private connectivity to enable account admins to set allow and deny rules that combine *who* is calling, *from where* they are calling, and *what* they can reach in Databricks. This ensures that only trusted combinations of identity, request type, and network source can reach your workspace. Context-based ingress control is configured at the account level. A single policy can govern multiple workspaces.

Using context-based ingress, you can:

* Stop access from untrusted networks by requiring a second factor, a trusted network source, in addition to credentials.
* Allow access for SaaS clients without stable egress IPs by keying on identity instead of IP ranges.
* Limit access by allowing less trusted sources to use only certain scopes like Databricks APIs or the workspace UI.
* Protect privileged automation: Constrain high-value Databricks service principals to high-trust networks only.
* Audit effectively: Capture detailed denial logs in Unity Catalog system tables to monitor blocked requests.

## Context-based ingress control core concepts

### Network sources

A network source defines the origin of requests. Supported types include:

**Public access policy:**

* **All public IPs**: Any public internet source.
* **Selected IPs**: Specific IPv4 addresses or CIDR ranges.

**Private access policy:**

* **All registered private endpoints**: Any registered private endpoint in the account.
* **Selected private endpoints**: Specific registered private endpoints in the account.

### Access types

Rules apply to different incoming request scopes. Each scope represents a category of incoming requests that you can allow or deny:

**Workspace-level policy access types:**

* **Workspace UI**: Browser access to the workspace.
* **API**: Programmatic access through Databricks APIs, including SQL endpoints (JDBC / ODBC). You can target all APIs or a specific API scope, such as apps, dashboard, or model serving.
* **Apps runtime**: Allow or deny access to Databricks Apps deployments. See [Databricks Apps](/aws/en/dev-tools/databricks-apps/). Only the **All users and service principals** identity option is supported for this access type.

* **Lakebase runtime**: Connections to Lakebase database instances. See [Lakebase instances](/aws/en/oltp/instances/create/). Only the **All users and service principals** identity option is supported for this access type.

**Account-level policy access types:**

* **Account UI**: Browser access to account-level resources (for example, the account console and account-level Genie One).
* **Account API**: Programmatic access through Databricks account APIs.

### Identities

Rules can target different identity types. For the **Apps runtime** and **Lakebase runtime** access types, the only supported option is **All users and service principals**.

In the account-level policy, the only supported option is **All users and service principals**.

* **All users and Databricks service principals**: Both human users and automation.
* **All users**: Human users only.
* **All Databricks service principals**: Automation identities only.
* **Selected identities**: Specific users or Databricks service principals.

### Rule evaluation

* **Default deny**: In restricted mode, access is denied unless explicitly allowed.
* **Deny before allow**: Deny rules let you define exceptions to your allow rules.
* **Default workspace-level policy**: Each account has a default workspace-level ingress policy applied to all eligible workspaces without an explicit policy assignment.

### Enforcement modes

Context-based ingress policies enable two modes:

* **Enforced for all products**: Databricks actively applies rules and blocks violating requests.
* **Dry run mode for all products**: Databricks logs violations but does not block requests. Use this mode to evaluate policy impact before enforcing.

note

A network policy supports only one enforcement mode at a time.

## Auditing

Denied or dry-run requests are logged in the `system.access.inbound_network` system table. If you don't have access to system tables, a metastore admin can grant you permissions. See [Grant access to system tables](/aws/en/admin/system-tables/#grant-access).

Each log entry includes:

* Event time
* Workspace ID
* Rule label (of the rule that denied the request)
* Request type
* Identity
* Network source
* Access type (DENIED or DRY\_RUN\_DENIAL)

Query these logs to verify your rules work as expected and to catch unexpected access attempts.

## Relationship with other controls

* **Workspace IP access lists**: Evaluated together with the context-based ingress policy using a logical AND, with no strict sequence between the two. A request is allowed only if both the IP access list and the ingress policy permit it. Workspace IP access lists can further narrow access but cannot widen it.
* **Serverless egress control**: Complements ingress policies by controlling outbound network traffic from serverless compute. See [Manage network policies](/aws/en/security/network/serverless-network-security/network-policies).

tip

To reduce complexity, Databricks recommends using the context-based ingress policy as your only policy engine rather than also maintaining IP access lists.

* **Account IP access lists**: Evaluated together with the context-based ingress account-level policy using a logical AND, with no strict sequence between the two. A request is allowed only if both the IP access list and the account-level policy permit it. Account IP access lists can further narrow access but cannot widen it.
* **Private access setting public access toggle**: Enforced alongside ingress policies when **Public access enabled** is **True**. If **Public access enabled** is **False**, all public ingress is blocked and ingress policies are not evaluated. See [Manage private access settings](/aws/en/security/network/classic/private-access-settings).
* **Front-end private connectivity**:
  + For traffic to be allowed, both the private access settings and context-based ingress must permit the endpoint. By default, context-based ingress is set to **Allow access from all private endpoints**, which defers the access decision to the workspace's private access setting. If you would like to configure context-based private access policies, make sure your workspace has a private access setting attached, with all registered private endpoints allowed (see more below). This will defer the access decision to your workspace's context-based ingress policy.
  + For the account-level policy, context-based ingress is the single source of truth for private access policy.

## Best practices

* Begin with dry run mode to observe impacts without breaking access.
* Use identity-based rules where possible for SaaS clients that rotate IPs.
* Apply deny rules to privileged Databricks service principals first to limit affected area.
* Keep policy names clear and consistent.