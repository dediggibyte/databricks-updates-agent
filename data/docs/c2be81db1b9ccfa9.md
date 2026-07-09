Learn how to navigate the Analytics and AI workspace UI and find the features you need. This article explains the core concepts of the Databricks workspace UI, an environment for authoring and accessing all of your Databricks objects.

You can manage workspace assets and settings using the workspace UI, the [Databricks CLI](/aws/en/dev-tools/cli/), and the [Workspace API](https://docs.databricks.com/api/workspace/introduction). Most of the articles in the Databricks documentation focus on performing tasks using the Analytics and AI workspace UI.

## Homepage

The following sections of the workspace homepage provide shortcuts to common tasks and workspace objects to help you onboard to and navigate Databricks:

**Ask Genie**

Ask Genie is the first section on the workspace homepage. It gives you quick access to three modes:

* **Ask**: Ask data questions in natural language. Genie routes your question to the most relevant Genie Agent.
* **Search**: Search for workspace objects such as dashboards, notebooks, and queries.
* **Genie Code**: Start a Genie Code conversation to author dashboards and analyze data using natural language.

**Suggested**

This section displays workspace objects recommended based on your activity.

**Favorited**

This section displays objects you have marked as favorites.

**Popular**

This section displays objects with the most user interactions in the last 30 days across product areas, including notebooks, queries, dashboards, and alerts.

**Mosaic AI**

This section provides quick access to AI-related assets and features.

**What's new**

This section highlights recently released features and updates in Databricks.

## Sidebar

The following common categories are visible at the top of the sidebar:

* Workspace
* Recents
* Catalog
* Jobs & Pipelines
* Compute
* Marketplace

note

There is a lock icon next to items that require an entitlement you aren't assigned.

The features in the following sections are also always visible in the sidebar, grouped by product area:

### Analytics

* Dashboards
* Genie Agents
* Alerts

### Lakehouse

* SQL Editor
* Queries
* Query History
* SQL Warehouses

### Data Engineering

* Job Runs
* Data Ingestion

### AI/ML

* Playground
* Agents
* Experiments
* Features
* Models
* Serving

## + New menu

Click **+ New** to complete the following tasks:

* Create workspace objects such as notebooks, queries, repos, dashboards, alerts, jobs, pipelines, experiments, models, and serving endpoints.
* Create compute resources such as clusters, SQL warehouses, and ML endpoints.
* Upload CSV or TSV files to Delta Lake using the **Create or modify table from file upload** page or load data from various data sources using the add data UI.

## Search

Use the top bar to search for workspace objects such as notebooks, queries, dashboards, alerts, files, folders, libraries, tables registered in Unity Catalog, jobs, and repos in a single place. You can also access recently viewed objects in the search bar. For more information about search features, see [Search for workspace objects](/aws/en/search/).

## Workspace admin and user settings

Workspace admin and workspace user settings are unified across product areas. SQL settings are combined with general settings to create a unified experience for admin and non-admin users.

All workspace admin settings are now accessed from **Settings**.

All workspace user settings are now accessed from **Settings**.

* The **Password** setting is on the **Profile** tab.
* **SQL query snippets** (**Settings** > **Developer**) is visible to users with the Databricks SQL access entitlement.

## Switch to a different workspace

If you have access to more than one workspace in the same account, you can quickly switch among them.

1. Click the workspace name in the top bar of the Databricks workspace.
2. Select a workspace from the drop-down to switch to it.

## Switch between authoring contexts

In the notebook, file, SQL, and pipeline editors, click the icon in the upper-left (either , , or ) to switch between tab groups based on the following authoring contexts:

* **Workspace**: Switch to the default workspace tab group, which shows open tabs for notebooks and files. These tabs are ephemeral and might not be saved if you exit your browser.
* **Recent workspace tabs**: View past workspace tab sessions and restore them.
* **SQL Editor**: Switch to the SQL editor for your SQL queries. These tabs are persistent and remain open even after you exit your browser.
* **Pipeline**: Switch to the pipeline. Each pipeline has its own distinct authoring context. When you switch to a pipeline, you’ll see a persistent set of tabs specific to that pipeline.

## Change the workspace language settings

The workspace is available in multiple languages. To change the workspace language, click your username in the top navigation bar, select **Settings** and go to the **Preferences** tab.

## Get help

This section describes the in-product help experience.

Click  in the top bar of the workspace to access the AI assistant. Enter any question for Genie Code in the text box.

Genie Code is intended to quickly answer questions by referencing Databricks documentation and knowledge base articles. Results include links to any documentation used to answer the question.
If Genie Code cannot find documentation related to the user question, it declines to answer. Genie Code is new, so mistakes are possible. Review the linked documentation to verify answers.
To share feedback, click  in the top bar of Genie Code, then **Send feedback to Databricks**.

If your organization has a [Databricks Support contract](/aws/en/resources/support), at the top of the Genie Code menu, you can click **Contact Support** for additional help. You can also access
**Contact Support** by clicking on your user icon at the top bar of the workspace.

With a Databricks Support contract, Genie Code also asks whether its response answered your question. If you need additional help, click **No, continue with ticket submission** to submit a ticket to Support.
This opens the **Contact support** modal, where you can provide additional information describing your issue.

In the top bar of Genie Code, click  to view the following resources:

* **History**: View your chat history with Genie Code.
* **Help**: Visit the Help Center to search across Databricks documentation, Databricks Knowledge Base articles, Apache Spark documentation, training courses, and Databricks forums.
* **Send feedback to Databricks**: Use the feedback form to submit product feedback from your workspace. See [Submit product feedback](/aws/en/resources/ideas).

## Managing files and folders

For detailed information about managing files and folders in the workspace browser, see [Workspace browser and file management](/aws/en/workspace/workspace-browser).