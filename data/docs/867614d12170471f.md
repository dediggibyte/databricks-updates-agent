Improve Genie Agent accuracy and reliability by adding example SQL queries, Unity Catalog functions, plain-text instructions, and knowledge store snippets (table descriptions, JOIN relationships, and SQL expressions for business semantics).

note

Genie Agents were formerly known as Genie Spaces.

## Add SQL examples and instructions

You can add sample SQL queries, Unity Catalog functions, and plain-text instructions to help generate accurate responses. Click **Configure** > **Instructions**. Use the **SQL Queries** tab to manage queries and Unity Catalog functions. Use the **Text** tab to add plain text instructions.

Each Genie Agent has two separate limits:

* **Instructions (100 per agent)**: Each example SQL query, each SQL function, and the entire **General instructions** text block each count as one instruction.
* **Knowledge store snippets (200 per agent)**: Table descriptions, join relationships, and SQL expressions (measures, filters, and dimensions) share this limit. See  [View columns](#view-columns),  [Define join relationships](#join-overview), and [Define SQL expressions](#sql-expressions).

A Genie Agent aims to provide consistent and predictable responses based on clear and precise guidance. Because Genie operates in a nondeterministic manner, it's important to make the guidance free from conflicting or ambiguous information to minimize the risk of undesirable responses. When setting up the agent, a key task is to review and resolve any inconsistencies. This helps to achieve reliable results.

### Add example SQL queries and functions

Use the **SQL Queries** tab to add the following:

* **Example queries (Recommended):** Example SQL queries help Genie generate the correct SQL to answer common user questions. Queries can be static or parameterized. For each example SQL query, provide the SQL and use the most typical phrasing of the user's question as the title. This improves Genie's ability to match prompts to the example. Genie can either use the example query directly or learn from it to handle similar questions. Users with CAN EDIT privileges in the agent can view the query used to generate the response, which helps with troubleshooting and refinement.
* **SQL functions:** For questions that cannot be answered with a static or parameterized SQL query, you can register a custom function to Unity Catalog. Functions can be shared across your teams and used by Genie to answer specific questions. To learn more about using SQL functions in your Genie Agent, see [Trusted assets](#trusted-assets).

### How Genie uses example queries

Example queries show Genie how to use the available data to answer questions. Enter a sample question into the text field, and then enter a SQL query that answers that question. Write the sample question the way a user would naturally ask it. When Genie receives a matching question, it can use the example query directly to provide an answer. When Genie gets a similar question, it uses clues from the example query to learn and structure the SQL provided in the response. Focus on providing samples that highlight logic that is unique to your organization and data, as in the following example:

SQL

```
  -- Return our current total open pipeline by region.  
  -- Opportunities are only considered pipelines if they are tagged as such.  
  SELECT  
    a.region__c AS `Region`,  
    sum(o.amount) AS `Open Pipeline`  
  FROM  
    sales.crm.opportunity o  
    JOIN sales.crm.accounts a ON o.accountid = a.id  
  WHERE  
    o.forecastcategory = 'Pipeline' AND  
    o.stagename NOT ILIKE '%closed%'  
  GROUP BY ALL;
```

#### Add query parameters

Parameterized example queries allow agent users to specify a value that is inserted into the query at runtime. With parameters, Genie can take specific inputs from user questions and reuse the structure of an example query to provide verified answers.

To add a parameter to a query:

1. Place your cursor where you want to insert the parameter.
2. Click **Add parameter**.

   This creates a new parameter with the default name `parameter`. To change the name, replace it in the query editor. You can also add a parameter by typing a colon followed by a parameter name (`:parameter_name`) directly in the editor.

To edit a parameter, click  next to the parameter name. A **Parameter details** dialog includes the following options:

* **Keyword**: The keyword representing the parameter in the query. You can only change it by editing the query text directly.
* **Data type**: Supported types include **String**, **Date**, **Date and Time**, **Decimal**, and **Integer**. The default is **String**.
* **Comment**: A description of the possible values or limits for the parameter. Use this to provide context that helps Genie select the correct value.

note

If the input value does not match the selected type, Genie treats it as the incorrect type, which can lead to inaccurate results.

In chat mode, when the exact text of a parameterized query is used in a response, Genie provides a verified answer. See [Trusted assets](#trusted-assets).

#### Trusted assets

Trusted assets are example SQL queries and SQL functions that provide verified answers to questions you anticipate from users. When Genie uses a trusted asset to answer a question, it provides a verified answer, giving agent users an extra layer of confidence in the result's accuracy.

Trusted assets include:

* **Parameterized example SQL queries**: In chat mode, when the exact text of a parameterized query is used to generate a response, Genie provides a verified answer. Agent users can edit the parameter value and rerun the query. See [Add query parameters](#add-query-parameters).
* **SQL functions**: SQL functions registered in Unity Catalog can be added to a Genie Agent. See [How does Genie use SQL functions?](#how-does-genie-use-sql-functions).

Users with at least CAN EDIT permission on a Genie Agent can add or remove trusted assets. Agent users must have `EXECUTE` permission on any SQL functions used as trusted assets.

#### Provide usage guidance

You can provide Genie additional context to explain when an example query is particularly relevant.

To add usage guidance:

1. Click **Configure** > **Instructions** > **SQL Queries** to access the list of example queries.
2. Click an example query.
3. Click **Usage guidance** near the bottom of the screen.
4. Enter details about how and when to use this example query.

### How does Genie use SQL functions?

SQL functions are useful when a question involves complex logic that cannot be captured with a static or parameterized query. They are stored in Unity Catalog and can be called by Genie using user-supplied parameters. Genie cannot view or modify the SQL used in the function, making this approach well-suited for logic that should not be surfaced or changed. For guidance on registering a function in Unity Catalog, see [Create a SQL table function](/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-sql-function#create-a-sql-table-function) and [User-defined functions (UDFs) in Unity Catalog](/aws/en/udf/unity-catalog).

### Provide instructions

Click the **Text** tab to write plain text instructions that help Genie understand how to respond to specific questions about your business. You can format the instructions as a single comprehensive note or categorize them by topic for better organization.

Instructions help guide Genie's responses so that it can process the unique jargon, logic, and concepts in a given domain. General text instructions apply to all prompts. If an instruction is relevant only to a subset of prompts, it should be included as an example query or function, or documented in the relevant table as comments or metadata. Text instructions are *only* for context that should be applied globally and do not fit into the other formats.

The following example includes information you could include in general instructions:

```
- **Company-specific business information**:  
  - Fiscal year starts in February, for example fiscal year 26 or FY26 is February 1, 2026 through January 31, 2027  
- **Formatting**:  
  - Always respond in Spanish  
  - If no other specification exists, round all decimals to two places  
  - Omit commas in results for any column including "Id" or "id" or "\_id"
```

## Build a knowledge store

The Genie knowledge store allows you to curate and enhance your agent through localized metadata, prompt matching, and structured SQL instructions. These features help Genie understand your data and generate more accurate and relevant responses.

### What is a knowledge store?

A knowledge store is a collection of curated semantic definitions that enhances Genie's understanding of your data and improves response accuracy.

The knowledge store consists of:

* **Agent-level metadata customization**: Agent-specific descriptions for tables, columns, and business terms and synonyms.
* **Agent-level data customization**: Simplified, focused datasets without changing the underlying Unity Catalog tables.
* **Prompt matching**: Examples that help Genie match values that are most relevant to the user's question and correct spelling issues in user prompts. This includes [format assistance](#manage-format-assistance) and [entity matching](#configure-entity-matching).
* **Join relationships**: Defined table relationships for accurate `JOIN` statements.
* **SQL expressions**: Structured definitions of measures, filters, and dimensions that capture business logic.

note

Each Genie Agent supports a maximum of 200 knowledge store snippets. Table descriptions, join relationships, and SQL expressions (measures, filters, and dimensions) count toward this limit. Text instructions, example SQL queries, SQL functions, column descriptions, and prompt matching settings do not count toward this limit.

All knowledge store configurations are scoped to your Genie Agent and do not affect Unity Catalog metadata or other Databricks assets.

### Manage knowledge store metadata

Teach Genie about the data in your agent by providing local table and column descriptions and adding column synonyms that align with common business terms. Simplify datasets by hiding unnecessary or duplicate columns to keep Genie focused.

These practices improve usability for users who do not have direct permissions on the underlying tables, and they also support quicker iterations when updating instruction versions.

To access agent-level metadata, click **Configure > Data** in your Genie Agent. Then click a table name to view its metadata and columns.

#### View columns

Click a table name to see an overview of the column names and details. The following example shows a sample from a table named `accounts`.

* **Description:** Genie uses metadata to understand your data and generate accurate responses. The default table description shows the Unity Catalog metadata associated with your data asset. Edit this description to add specific directions that help Genie author SQL for your agent. Click **Reset** to restore the Unity Catalog description.
* **Columns:** Column names and descriptions are included in the column list. Each column is labeled with tags that show whether it includes **Format assistance** or **Entity matching**. See  [Prompt matching overview](#prompt-matching-overview).

#### Hide or show relevant columns

Hiding a column removes it from the Genie Agents's context, so Genie won't reference it when generating SQL or answering questions. This is useful for excluding unnecessary, duplicate, or potentially confusing columns so that Genie stays focused on the data that matters. Hiding a column doesn't affect the underlying data or Unity Catalog permissions. The column still exists in the table and remains visible to users with direct table access.

Columns can be managed individually or in bulk. Use the following instructions to hide or show columns.

* **Hide a single column**: Click the  next to the column name.
* **Hide multiple columns**:
  + Select the checkboxes for the columns you want to hide.
  + From the **Actions** menu, select **Hide selected columns**.
* **Undo changes**: Repeat the same steps to show a column that was hidden.

#### Edit column metadata

You can customize the following for each column:

* **Description**: Agent-specific column descriptions that enhance Genie's understanding.
* **Synonyms**: Business terms and keywords that help match user language to column names.
* **Advanced settings**: Prompt matching controls.
  + **Format assistance**: Turn sampling of representative values on or off.
  + **Entity matching**: Enable or disable entity matching for categorical columns.

To edit column metadata:

1. Click the  pencil icon next to a column name.
2. Edit the description and synonyms for the column.
3. If necessary, click **Advanced settings** to open prompt matching controls.
4. Click **Save** to keep your changes and close the dialog.

### Prompt matching overview

Prompt matching allows Genie to match columns and values that are most relevant to the user's question, and correct spelling issues in user prompts. This improves Genie's accuracy and helps generate more reliable SQL queries.

When a user asks a question in Genie, the phrasing is often conversational and can include errors such as misspellings. In these cases, the values in the prompt might not match the structure or values in the data. This can cause Genie to misinterpret the question and generate incorrect SQL.

#### Example

Review the following example:

> "Show me car sales in Florida for Q1."

If the data uses state abbreviations (such as `FL`), and Genie cannot access the values for that column, Genie might generate SQL that includes `ILIKE '%Florida%'`, which returns no results.

Enabling entity matching on the `state` column allows Genie to access representative values. With this context, Genie can recognize that `FL` corresponds to "Florida" and generate more accurate SQL.

