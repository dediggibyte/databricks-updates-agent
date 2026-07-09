Embed a Genie Agent as an iframe in an external website or application so users can interact with Genie inside your internal tools or portals without navigating to Databricks. Workspace admins configure allowed embedding surfaces; embedded users can send prompts but cannot edit the agent configuration.

note

Genie Agents were formerly known as Genie Spaces.

## Requirements

Before you can embed a Genie Agent, the following must be in place:

* **Workspace admin**: Must configure allowed embedding surfaces in Genie access management settings.
* **Agent author**: Must have at least CAN MANAGE permission on the Genie Agent.
* **End users**: Must have explicit access to the Genie Agent and the underlying data assets it uses. Users who are not signed in to Databricks are prompted to authenticate before they can interact with the embedded agent.

note

Embedded Genie Agent users can send prompts but cannot edit the agent configuration.

## Step 1: Configure allowed embedding surfaces

A workspace admin must configure allowed embedding surfaces before a Genie Agent can be embedded. See [Manage dashboard and Genie Agent embedding](/aws/en/ai-bi/admin/embed).

## Step 2: Generate the iframe code

After an admin has configured allowed surfaces, agent authors can generate the iframe embed code.

1. Open the Genie Agent you want to embed.
2. Click **Share**.
3. In the Share dialog, click **Embed space**.
4. Copy the generated iframe code.

## Step 3: Add the iframe to your application

Paste the iframe code into your external website or application.

To enable full functionality, including copying CSV data and copying conversation links, add the `allow="clipboard-write"` attribute to the iframe element:

Html

```
<iframe src="<your-genie-space-url>" allow="clipboard-write" width="100%" height="600"></iframe>
```

## Best practices

* **Grant explicit data access**: Make sure end users have access to both the Genie Agent and all underlying data assets used by the agent. Users only see data they have permission to access.
* **Enable clipboard access**: Include `allow="clipboard-write"` on the iframe element so users can copy query results and conversation links.
* **Limit allowed surfaces**: Only add domains to the allowed embedding surfaces list that you trust and control.