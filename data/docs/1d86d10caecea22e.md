This page shows how to embed an AI/BI dashboard in an external website or application.

## Work with published dashboards

Only published dashboards can be embedded into external applications. Dashboards can be published with or without shared data permissions. Briefly, the implications of each setting are as follows:

* **Shared data permission:** For dashboards published with this setting, the publisher's credentials determine access to the underlying data. Queries run with the publisher’s permissions.
* **Individual data permissions:** For dashboard published with this setting, each viewer must have explicit access to the underlying data to view results.

For more details, see [Share a dashboard](/aws/en/dashboards/share/share).

note

If you use a service principal for embedding, the principal’s permissions control access to APIs (such as retrieving dashboard configuration or requesting results). However, these permissions do not override access granted by shared data permissions.

## Embedding options

As with dashboards in the Databricks UI, embedded dashboards allow you to centrally manage read permissions for Unity Catalog-governed data assets and run permissions for dashboards, track user activity through query history and audit logs, and maintain unique viewer counts even for users without a Databricks account. Use one of the following options to embed your dashboard.

### Basic embedding

Users must sign in with their Databricks credentials to view the embedded dashboard. The following points outline the key details of how basic embedding works:

* Dashboard authors can generate iframe code from the **Share** dialog.
* Workspace admins must define allowed surfaces for embedding. See [Manage dashboard and Genie access](/aws/en/ai-bi/admin/#manage-access).
* Only users who have been explicitly granted access can view the embedded dashboards. See [Share a dashboard](/aws/en/dashboards/share/share) to learn more about dashboard sharing.
* Viewers are prompted to sign in to Databricks unless they have an active session from a recent sign-in to the originating workspace.

### Embedding for external users

Embedding for external users allows you to integrate dashboards into external systems without requiring viewers to have Databricks accounts. See [What is embedding for external users?](/aws/en/dashboards/share/embedding/external-embed). Use embedding for external users to:

* Allow your application to authenticate with Databricks using a service principal with an OAuth secret.
* Enable access for users outside your Databricks account or identity provider.

#### Example use case

An organization managing building operations for property managers could use embedding for external users to provide each property manager with an embedded dashboard for each building that displays energy usage, occupancy statistics, and maintenance alerts within their management portal.

### Embedding authentication approaches

To help choose the right embedding approach, consider interactions and use cases in the following table.

| Embedding method | How users authenticate | How permissions are evaluated | Typical use case | Ask Genie support |
| --- | --- | --- | --- | --- |
| Databricks-authentication | Users sign in with Databricks account | Users’ own permissions are checked (and, if dashboard uses shared data permissions, publisher’s permissions are applied) | Users registered to the Databricks account | Supported. See [Ask Genie in embedded dashboards](/aws/en/dashboards/share/embedding/basic#ask-genie). |
| Embedding for external users | Application authenticates using a service principal and OAuth token | Service principal’s permissions control API access, but shared data permissions (if granted) still determine data access | External users, portals, or broad distribution | Not supported. Use the [Genie Conversation API](/aws/en/genie/conversation-api) instead. |

note

For embedding for external users, Databricks recommends publishing the embedded dashboard *with individual data permissions* and assigning required data permissions to the service principal associated with the application. If the dashboard is published with shared data permissions, the publisher’s permissions are used for data access, not the service principal’s.

## Best practices for permission setting

To reduce the risk of exposing sensitive data when using an access token:

* **Publish the dashboard with individual data permissions:** This ensures queries run with the viewer’s permissions, not the publisher’s. It prevents unintended access if the publisher’s permissions later expand.
* **Restrict service principal to expected tables:** Even if Databricks cannot infer which tables a dashboard will query—especially with parameterized queries—you can configure your service principal to limit token access only to the required tables.

Tokens used for embedding for external users are valid for one hour. If a token is compromised and was created without proper scoping, an attacker might be able to access any tables included in a later version of the dashboard during that time.

## Refresh an embedded dashboard

All viewers of an embedded dashboard can manually refresh dashboards on demand. You can also set up a schedule to refresh dashboards periodically. See [Manage scheduled dashboard updates and subscriptions](/aws/en/dashboards/share/schedule-subscribe).

## Troubleshooting embedded dashboards

This section lists common problems and provides suggested resolutions.

### Dark mode isn't displaying

By default, embedded dashboards display using light mode. To enable dark mode or allow the dashboard to automatically match the user's system preference, set the `colorScheme` option when initializing the dashboard:

* `"light"`: Forces light mode. This is the default behavior if `colorScheme` is not set.
* `"dark"`: Forces dark mode.
* `"light dark"`: Automatically matches the user's system or browser preference.

This option maps to the CSS [`color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme) property applied to the embedded iframe.

To preview how your dashboard appears in a specific color mode, open it in draft mode, go to [dashboard settings](/aws/en/dashboards/manage/settings#open-settings), and select the desired theme under **Theme**. For more information about customizing dashboard themes, see [Theme settings](/aws/en/dashboards/manage/settings#custom-theme).

### The embedded iframe is blank

If the embedded iframe isn’t displaying data, ensure that third-party cookies are enabled in your browser. External content, such as embedded dashboards, requires this setting to function correctly.

To resolve the issue, enable third-party cookies in your browser settings. If you prefer not to enable cookies for all sites, you can add exceptions for specific sites. Refer to your browser’s help documentation for instructions on managing cookies.

The following steps explain how to restart your session with third-party cookies enabled in the Chrome browser. This process ensures a clean state by first disabling, then re-enabling third-party cookies:

1. Log out of all active Databricks sessions.
2. Click the slider icon next to the to the URL.
3. Click **Cookies and site data** and disable or block **Third party cookies**. You are prompted to refresh the page.
4. Refresh the page and click the **Sign in** in the embedded iframe. An error message should appear. Close the browser window.
5. Under **Cookies and site data**, allow **Third-party cookies**.
6. Refresh the page once more.
7. Go to your embedded dashboard and click **Sign in**.

## Next steps

* **Set up basic embedding**: See [Basic dashboard embedding](/aws/en/dashboards/share/embedding/basic).
* **Configure embedding for external users**: See [What is embedding for external users?](/aws/en/dashboards/share/embedding/external-embed).
* **Manage embedding permissions**: See [Manage dashboard and Genie Agent embedding](/aws/en/ai-bi/admin/embed).
* **Share published dashboards**: See [Share a dashboard](/aws/en/dashboards/share/share).