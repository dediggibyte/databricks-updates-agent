This page describes how to create, edit, view, and delete ABAC row filter and column mask policies in Unity Catalog. To create and manage GRANT policies (Beta), see [ABAC GRANT policies for models (Beta)](/aws/en/data-governance/unity-catalog/abac/grant-policies). For an overview of policy concepts, see [Core concepts for ABAC](/aws/en/data-governance/unity-catalog/abac/core-concepts).

## Requirements

All policy operations (create, edit, delete, show, describe) require `MANAGE` on the securable object or object ownership. Creating a policy also requires:

* Databricks Runtime 16.4 or above, or serverless compute. See [Compute requirements](/aws/en/data-governance/unity-catalog/abac/requirements#compute-requirements).
* For the filtering or masking logic, a user-defined function (UDF) in Unity Catalog that you have `EXECUTE` on, or a SQL function that you define inline when creating the policy.
* Governed tags applied to target objects. See [Governed tags](/aws/en/admin/governed-tags/).

## Create a policy

You can create a policy using the Catalog Explorer UI, the [`CREATE POLICY`](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-policy) SQL statement, or the Databricks REST APIs, SDKs, and Terraform.

To create a policy, you must have `MANAGE` on the securable object where the policy is attached (catalog, schema, or table) or own the securable object, and `EXECUTE` on the UDF that implements the filtering or masking logic.

* Catalog Explorer
* SQL
* Python SDK

1. In your Databricks workspace, click  **Catalog**.
2. Select the object that determines the policy scope, such as a catalog, schema, or table.
3. Click the **Policies** tab.
4. Click **New policy**.
5. Complete the **Policy identification** section. The following table summarizes each field:

   | Field | Description | Example |
   | --- | --- | --- |
   | **Name** | A name for the policy. Must be unique among all policies defined on the same securable object. | `hide_eu_customers`, `mask_ssn` |
   | **Description** | Optional. A description for the policy. Appears in audit logs and helps administrators understand policy intent. | `Restrict EU customer rows from US analysts`, `Mask SSN for all account users` |
6. Complete the **Principals and scope** section. The following table summarizes each field:

   | Field | Description | Example |
   | --- | --- | --- |
   | **Applied to...** | The users, groups, or service principals subject to the policy. When these principals query tables in scope, the row filter or column mask is applied. To apply the policy to all principals in the account, select `All account users`. | `us_analysts`, `All account users` |
   | **Except for** | Principals exempt from the policy. Exempt principals are not subject to filtering or masking and see the full, unmodified data. | `admins`, `compliance_team` |
   | **Scope** | The securable object where the policy is attached. The policy evaluates against all tables within the selected scope. Select a catalog, schema, or table. Databricks recommends attaching policies at the highest applicable level. | Select catalog `prod`, then select schema `customers`. |
   | **Table condition** | Determines which tables within the scope the policy applies to. **No condition**: Applies the policy to all tables in scope. **Tables matching any of these tags**: Applies the policy to the specified list of tag keys or tag key-value pairs. Tables that have any of these match the policy. **Tables matching a custom expression**: You can build a boolean expression using `has_tag` and `has_tag_value`, combined with `AND`, `OR`, and `NOT` for more complex matching logic. Applies the policy to tables where the expression evaluates to `TRUE` and matches the policy. If a table in scope does not match the condition, the policy does not apply to that table. | Select **Tables matching any of these tags**, then choose tag key `sensitivity` with value `high` to restrict the policy to sensitive tables only. |
7. For **Policy type**, choose the type of access control to enforce:

   | Option | Description | Use when |
   | --- | --- | --- |
   | **Row filter** | Creates a row filter policy. The UDF evaluates each row and returns a boolean. Rows where the UDF returns `FALSE` are excluded from query results. | Access depends on the values in each row, such as filtering by the values in a column that contains geographic regions. |
   | **Column mask** | Creates a column mask policy. The UDF takes the column value as input and returns the original or a masked version. The return type must be castable to the target column's data type. | You need to redact sensitive fields, such as SSNs, phone numbers, or email addresses, while still allowing the principal to query the table. |
8. The next few sections depend on your **Policy type** selection. Expand the section that matches your selection:

   Row filter

   In the **Row filter function** section, choose how to specify the row filter function:

   * **Select existing**: Select a UDF already defined in Unity Catalog. The UDF evaluates each row and returns a boolean. Rows where the function returns `FALSE` are excluded from query results. You must have `EXECUTE` on the UDF.
   * **Create**: Define a SQL function to use as the row filter logic.

   In the **Function inputs** section, provide a value for each function parameter. Each input can be a column matched by tags, a column matched by a custom expression, or a constant value.

   Column mask

   In the **Column conditions** section, choose how to identify the columns to mask:

   * **Columns matching any of these tags**: Specify a list of tag keys or tag key-value pairs. Columns that have any of these are masked by the policy.
   * **Columns matching a custom expression**: Build a boolean expression using `has_tag` and `has_tag_value`, combined with `AND`, `OR`, and `NOT` for more complex matching logic. Columns where the expression evaluates to `TRUE` are masked.

   Then, choose the **Masking function** to apply to the matched columns:

   * **Select existing**: Select a UDF already defined in Unity Catalog. The UDF returns the original or masked value. The return type must be castable to the target column's data type. You must have `EXECUTE` on the UDF.
   * **Create**: Define a SQL function to use as the column masking logic.

   In the **Function inputs** section, provide a value for each additional function parameter. Each input can be a column matched by tags, a column matched by a custom expression, or a constant value.

   This example uses a constant value of `4` to show the last 4 characters of the SSN.
9. Click **Create policy**.

For complete documentation, see [CREATE POLICY](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-policy).

SQL

```
CREATE [OR REPLACE] POLICY policy_name  
ON { CATALOG catalog_name | SCHEMA schema_name | TABLE table_name }  
[COMMENT description]  
{ row_filter_body | column_mask_body }
```

Row filter body:

SQL

```
ROW FILTER function_name  
TO principal [, ...]  
[EXCEPT principal [, ...]]  
FOR TABLES  
[WHEN condition]  
[MATCH COLUMNS condition [[AS] alias] [, ...]]  
[USING COLUMNS (function_arg [, ...])]
```

Column mask body:

SQL

```
COLUMN MASK function_name  
TO principal [, ...]  
[EXCEPT principal [, ...]]  
FOR TABLES  
[WHEN condition]  
[MATCH COLUMNS condition [[AS] alias] [, ...]]  
ON COLUMN alias  
[USING COLUMNS (function_arg [, ...])]
```

Parameters:

* `policy_name`: A name for the policy. Must be unique among all policies defined on the same securable object.
* `ON { CATALOG | SCHEMA | TABLE }`: The scope where the policy is attached. The policy evaluates against all tables that are descendants of this securable object.
* `function_name`: The fully qualified name of the UDF that implements the filtering or masking logic.
* `TO principal [, ...]`: The users, groups, or service principals the policy applies to.
* `EXCEPT principal [, ...]`: Principals exempt from the policy. Exempt principals are not subject to filtering or masking.
* `FOR TABLES`: Specifies that the policy targets tables. Tables are currently the only supported securable object type, and that includes streaming tables and Materialized views.
* `WHEN condition`: A boolean expression that determines which tables the policy applies to, based on their tags. Uses built-in functions `has_tag('tag_name')` and `has_tag_value('tag_name', 'tag_value')`. If omitted, defaults to `TRUE` (applies to all tables in scope).
* `MATCH COLUMNS condition [[AS] alias] [, ...]`: Column conditions that identify which columns the policy targets. Each condition is a boolean expression built from `has_tag('tag_name')` and `has_tag_value('tag_name', 'tag_value')`, optionally combined with `AND`, `OR`, and `NOT`. Each condition can be assigned an alias for use in `ON COLUMN` and `USING COLUMNS`. A policy can include up to 3 `MATCH COLUMNS` expressions, and all must match for the policy to apply.
* `ON COLUMN alias`: For column mask policies, specifies the matched column to mask, referenced by its alias from `MATCH COLUMNS`.
* `USING COLUMNS (function_arg [, ...])`: Arguments passed to the UDF. Each argument can be an alias from `MATCH COLUMNS` or a constant literal.

Example: column mask policy. Mask all columns tagged with `pii:ssn` in the `prod.customers` schema, showing only the last 4 characters. The policy applies to `us_analysts` except `admins`.

SQL

```
CREATE FUNCTION ssn_to_last_nr (ssn STRING, nr INT) RETURNS STRING  
  RETURN right(ssn, nr);  
  
CREATE POLICY mask_ssn  
ON SCHEMA prod.customers  
COLUMN MASK ssn_to_last_nr  
TO us_analysts EXCEPT admins  
FOR TABLES  
MATCH COLUMNS has_tag_value('pii', 'ssn') AS ssn  
ON COLUMN ssn  
USING COLUMNS (4);
```

Example: row filter policy. Exclude rows with European customers from tables tagged with `sensitivity:high` in the `prod.customers` schema. The policy applies to `us_analysts` and filters rows based on a `geo_region` column.

SQL

```
CREATE FUNCTION non_eu_region (geo_region STRING) RETURNS BOOLEAN  
  RETURN geo_region <> 'eu';  
  
CREATE POLICY hide_eu_customers  
ON SCHEMA prod.customers  
COMMENT 'Exclude rows with European customers from sensitive tables'  
ROW FILTER non_eu_region  
TO us_analysts  
FOR TABLES  
WHEN has_tag_value('sensitivity', 'high')  
MATCH COLUMNS has_tag('geo_region') AS region  
USING COLUMNS (region);
```

For complete documentation, see the [Databricks SDK for Python documentation](https://databricks-sdk-py.readthedocs.io/en/stable/workspace/catalog/policies.html).

This example creates a row filter policy that excludes rows with European customers for US-based analysts:

Python

```
from databricks.sdk import WorkspaceClient  
from databricks.sdk.service.catalog import (  
    FunctionArgument,  
    MatchColumn,  
    PolicyInfo,  
    PolicyType,  
    RowFilterOptions,  
    SecurableType,  
)  
  
w = WorkspaceClient()  
  
w.policies.create_policy(PolicyInfo(  
    name="hide_eu_customers",  
    comment="Exclude rows with European customers from sensitive tables",  
    on_securable_type=SecurableType.SCHEMA,  
    on_securable_fullname="prod.customers",  
    for_securable_type=SecurableType.TABLE,  
    policy_type=PolicyType.POLICY_TYPE_ROW_FILTER,  
    to_principals=["us_analysts"],  
    match_columns=[  
        MatchColumn(condition="has_tag('geo_region')", alias="region"),  
    ],  
    row_filter=RowFilterOptions(  
        function_name="prod.customers.non_eu_region",  
        using=[FunctionArgument(alias="region")],  
    ),  
))
```

This example creates a column mask policy that masks social security numbers for US analysts, except those in the `admins` group:

Python

```
from databricks.sdk import WorkspaceClient  
from databricks.sdk.service.catalog import (  
    ColumnMaskOptions,  
    FunctionArgument,  
    MatchColumn,  
    PolicyInfo,  
    PolicyType,  
    SecurableType,  
)  
  
w = WorkspaceClient()  
  
w.policies.create_policy(PolicyInfo(  
    name="mask_ssn",  
    comment="Mask social security numbers",  
    on_securable_type=SecurableType.SCHEMA,  
    on_securable_fullname="prod.customers",  
    for_securable_type=SecurableType.TABLE,  
    policy_type=PolicyType.POLICY_TYPE_COLUMN_MASK,  
    to_principals=["us_analysts"],  
    except_principals=["admins"],  
    match_columns=[  
        MatchColumn(condition="has_tag_value('pii', 'ssn')", alias="ssn"),  
    ],  
    column_mask=ColumnMaskOptions(  
        function_name="prod.customers.ssn_to_last_nr",  
        on_column="ssn",  
        using=[FunctionArgument(constant="4")],  
    ),  
))
```

## Edit a policy

* Catalog Explorer
* SQL
* Python SDK

1. In your Databricks workspace, click  **Catalog**.
2. Select the object the policy is attached to.
3. Click the **Policies** tab.
4. Select the policy you want to edit.
5. Update any fields you want to change. You can modify the description, principals, policy type, conditions, and function input mappings. The policy name and the securable object where the policy is applied cannot be edited. For field descriptions, see [Create a policy](#create-policy).
6. Click **Update policy**.

[`CREATE OR REPLACE POLICY`](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-policy) replaces the entire policy definition. Specify all clauses, not just the fields you want to change. The replacement policy must have the same name and be on the same securable object.

SQL

```
CREATE OR REPLACE POLICY mask_ssn  
ON SCHEMA prod.customers  
COLUMN MASK ssn_to_last_nr  
TO us_analysts EXCEPT admins, compliance_team  
FOR TABLES  
MATCH COLUMNS has_tag_value('pii', 'ssn') AS ssn  
ON COLUMN ssn  
USING COLUMNS (4);
```

Unlike `CREATE OR REPLACE POLICY` in SQL, `update_policy` supports partial updates. Use the `update_mask` parameter to specify which fields to change. Only those fields are updated. If `update_mask` is `"*"` or empty, all fields in `policy_info` are applied.

Python

``