Preview

Okta support for automatic identity management is in [Private Preview](/aws/en/release-notes/release-types). To request access, contact your Databricks account team.

When automatic identity management is enabled, you can configure the account access denylist to control which identities from your identity provider are allowed to access your Databricks account. Using a denylist model, account admins add specific users, groups, or Databricks service principals to the denylist to block their access.

Denylist membership is transitive. If you deny a group, all members of that group are also denied, including users who belong through nested group membership. Denied users and Databricks service principals are automatically set to **Inactive** in the Databricks account.

## Configure the account access denylist

Account admins can configure the account access denylist in the account console. The denylist is an account-level configuration and applies across all workspaces in your account.

Each account supports a maximum of 100 rules.

### Before enabling automatic identity management

1. As an account admin, log in to the account console.
2. In the sidebar, click **Security**.
3. Click the **User provisioning** tab, then click **Automatic identity management**.
4. Click **Configure** and fill in the required fields.
5. Click **Test connection**.
6. If the connection is successful, click **Configure a deny list**.
7. Click the option to edit identities in your identity provider.
8. Search for and select identities from your identity provider to add to the denylist.
9. Save your changes.

After configuring the denylist, you can enable automatic identity management.

### After automatic identity management is enabled

1. As an account admin, log in to the account console.
2. In the sidebar, click **Security**.
3. Click the **User provisioning** tab, then click **Automatic identity management**.
4. Click the option to edit identities in your identity provider.
5. Search for users, Databricks service principals, or groups from your identity provider to add to the denylist.
6. Save your changes.

Deny rules are inherited. If a parent group is denied, all members of its child groups are also denied access. Changes to the denylist can take up to 10 minutes to take effect.

## Test the denylist

The account access denylist includes a test mode. Use it to verify whether a specific user, Databricks service principal, or group would be denied access based on your current denylist configuration before you apply it.

1. In the denylist configuration, click **Test mode**.
2. Search for the user, Databricks service principal, or group you want to test.
3. Review the result to see whether the identity would be denied access.

## How deny rules work

When an identity is added to the denylist, the following effects apply:

**Denied identities cannot log in to Databricks**

* Denied users and Databricks service principals cannot log in to Databricks or use their personal access tokens.
* If a group is denied, all members and transitive members of that group are also denied.
* If a denied identity attempts to log in, the system might still provision it in the account, but sets it to an inactive state even if it is active in your identity provider.
* IAMv2 APIs (such as `resolveByExternalId`) also provision denied principals as inactive.

note

When evaluating deny rules, local group membership overrides take precedence over external identity provider groups. For example, if you manually add a user to a group using the Databricks API and create a deny rule for that group, the user is denied regardless of their status in your identity provider.

**Denied identities do not appear in sharing dialogs or identity selectors**

* Denied principals are filtered out from user-facing identity selection experiences, such as sharing dialogs.
* If a denied principal already has permissions, those permissions remain visible.
* Denied principals cannot log in, so they cannot use any granted permissions.
* APIs can still grant permissions to denied principals, but those permissions are not usable.

**Denied identities are visible to admins with a denied status**

* Denied principals remain visible in the account administrator and workspace administrator pages.
* Their status is shown as **Denied**.

**Denied identities cannot be deleted without first being removed from the denylist**

* users, service principals, and groups in the denylist cannot be deleted from the account until they are removed from the denylist.

**Group external IDs cannot be updated for denied groups**

* Groups in the denylist cannot have their `externalId` updated until they are removed from the denylist.