This article describes how to manage VPC endpoint registrations in the account console.

## What is a VPC endpoint registration?

This article discusses how to create Databricks VPC endpoint registration objects, which is a Databricks configuration object wrapping the regional AWS VPC endpoint. You must register AWS VPC endpoints to enable [AWS PrivateLink](https://aws.amazon.com/privatelink). An AWS VPC endpoint represents a connection from one VPC to a Private Link service in another VPC.

This article does not contain all the information necessary to configure Private Link for your workspace. For all requirements and steps, see [Configure classic private connectivity to Databricks](/aws/en/security/network/classic/privatelink).

One of the Private Link requirements is to use a [customer-managed VPC](/aws/en/security/network/classic/customer-managed-vpc), which you register with Databricks to create a network configuration object. For Private Link back-end support, that network configuration object must reference your VPC endpoint registrations (your registered VPC endpoints). For more information about network configurations, see [Configure classic private connectivity to Databricks](/aws/en/security/network/classic/privatelink) and [Register your VPC with Databricks](/aws/en/security/network/classic/customer-managed-vpc#register-vpc).

If you have multiple workspaces that share the same customer-managed VPC, you can choose to share the AWS VPC endpoints. You can also share these VPC endpoints among multiple Databricks accounts, in which case register the AWS VPC endpoint in each Databricks account.

## Register a VPC endpoint

note

These instructions show you how to create the VPC endpoints from the **Securitys** page in the account console before you create a new workspace. You can also create the VPC endpoints in a similar way as part of the flow of creating or updating a new workspace and choosing **Register a VPC endpoint** from menus in the network configuration editor. See [Create a classic workspace](/aws/en/admin/workspace/create-workspace) and [Configure a customer-managed VPC](/aws/en/security/network/classic/customer-managed-vpc).

1. In the [account console](https://accounts.cloud.databricks.com), click **Security**.
2. Click **Networking**.
3. From the vertical navigation on the page, click **VPC endpoints**.
4. Click **Register a VPC endpoint**.
5. In the **VPC endpoint registration name** field, type the human-readable name you'd like for the new configuration. Databricks recommends including the region and the destination of this particular VPC endpoint. For example, if this is a VPC endpoint for back-end Private Link connectivity to the Databricks control plane secure cluster connectivity relay, you might name it something like `VPCE us-west-2 for SCC`.
6. Choose the region.

   important

   The region field must match your workspace region and the region of the AWS VPC endpoints that you are registering. However, Databricks validates this only during workspace creation (or during updating a workspace with Private Link), so it is critical that you carefully set the region in this step.
7. In the **AWS VPC endpoint ID** field, paste the ID from the relevant AWS VPC endpoint.
8. Click **Register new VPC endpoint**.

## Delete a VPC endpoint registration

VPC endpoint registrations cannot be edited after creation. If the configuration has incorrect data or if you no longer need it, delete the VPC endpoint registration:

1. In the [account console](https://accounts.cloud.databricks.com), click **Security**.
2. Click **Networking**.
3. From the vertical navigation on the page, click **VPC endpoints**.
4. On the row for the configuration, click the kebab menu  on the right, and select **Delete**.
5. In the confirmation dialog, click **Confirm Delete**.