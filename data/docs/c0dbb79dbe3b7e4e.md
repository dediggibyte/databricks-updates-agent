Genie Code in Agent mode is the AI dashboard authoring partner for developers in Databricks AI/BI dashboards. Describe a dashboard in natural language, and the agent plans the work, builds it, and refines it with you, from finding data to laying out finished pages.

## What is Genie Code for dashboard authoring?

Genie Code for dashboard authoring is a capability in Genie Code's Agent mode that automates entire multi-step dashboard authoring workflows.

Compared to Genie Code Chat mode, Agent mode has expanded capabilities, including planning solutions, retrieving relevant assets, creating visualizations, configuring multi-page layouts, applying filters, and fixing errors automatically. The agent works with you to approve its plans and confirm next steps before proceeding. With your approval, it can search tables, create datasets, add visualizations, configure filters, and organize dashboard pages.

Genie Code's access and actions are governed by the user's permissions. It can only access data that you have access to and perform operations that you have permissions for.

## Requirements

To use Genie Code for dashboard authoring, your workspace needs the following:

* Partner-powered AI features enabled for both the account and workspace. See [Partner-powered AI features](/aws/en/databricks-ai/partner-powered).
* Your workspace must be in a supported region. Genie Code is a [Designated Service](/aws/en/resources/designated-services) that uses Geos to manage data residency. See [Geo availability of Genie Code features](/aws/en/genie-code/#geo-availability).

note

For customers with a [compliance security profile (CSP)](/aws/en/security/privacy/enhanced-security-compliance), Genie Code for dashboard authoring is turned on by default and runs on Databricks-hosted models, even when partner-powered AI features are turned off. Availability depends on your compliance standard. See [Partner-powered AI features](/aws/en/databricks-ai/partner-powered).

## Use Genie Code for dashboard authoring

When you create a new dashboard, Genie Code is available in the center of the canvas.

1. For existing dashboards, open the Genie Code side panel. In the bottom-right corner, confirm that **Agent** is selected.
2. Enter a prompt for the agent:

   prompt

   Tell Genie Code (Agent mode) to do this for you:

   ```
   Create a dashboard showing bakehouse trends using @sales_transactions from samples.bakehouse.
   ```

   tip

   Reference specific tables by using `@table_name`. The agent uses that table and any associated metadata to curate its response. The agent respects the user's Unity Catalog permissions, so it can only access the data that you have access to.
3. As the agent generates its response, it often pauses to get your input:

   * For more complex tasks, the agent might create a step-by-step plan and ask clarifying questions. Answer the agent's clarifying questions to help it hone its plan.
   * When the agent needs to create or modify dashboard elements, it asks for your approval before proceeding. **Allow** or **Decline** its request. You can also select **Always allow in current thread** (referring to the Genie Code conversation thread) or **Always allow**.
   * As the agent continues its work, you might be prompted to select **Continue** or **Reject**. Review the agent's existing work, then select **Continue** to allow the agent to continue to its next steps or **Reject** to tell it to try something else.
   * To stop the agent while it is working, click the red .

The agent can create new datasets, generate visualizations, configure filters, add pages, and organize dashboard layouts to interpret the results.

note

Keep the current tab open while Genie Code for dashboard authoring is working. If you switch tabs, the agent stops and can't take further steps.

## Author image widgets

Genie Code for dashboard authoring can add image widgets to a dashboard, such as a logo, diagram, or other branded visual. Ask the agent to add an image, and it creates an image widget on the canvas.

prompt

Tell Genie Code (Agent mode) to do this for you:

```
Add an image widget with our company logo to the top of the dashboard.
```

For more about image widgets and the image sources they support, see [Image widgets](/aws/en/dashboards/manage/visualizations/image-widgets).

## Beautify a dashboard

Genie Code for dashboard authoring can redesign a dashboard's appearance, adjusting elements like color, layout, and spacing to make the dashboard more polished and readable. Ask the agent to beautify the dashboard, then review the result.

prompt

Tell Genie Code (Agent mode) to do this for you:

```
Beautify this dashboard.
```

To revert the changes, undo them on the canvas. See [Keyboard shortcuts](/aws/en/dashboards/manage/#keyboard-shortcuts).

## Example prompts

The following prompts show the range of tasks Genie Code for dashboard authoring can handle, from data exploration and visualization creation to layout design and filter configuration. You can even create a new dashboard from scratch.

For better results, provide the agent with context by referencing tables, pipelines, notebooks, queries, and files with `@<resource_name>`. You can also click  **Add context** to manually select context to provide. Each reference asset persists in the chat context.

Try the following prompts to get started:

* **Dashboard creation**:
  + "Create a dashboard showing bakehouse trends from the `@sales_transactions` table."
  + "Build a sales performance dashboard using `@sales_data` with revenue by region and product category."
  + "Create a customer analytics dashboard from `@customer_data` showing retention, churn, and engagement metrics."
* **Visualization creation**:
  + "Add a line chart showing sales trends over time from this dataset."
  + "Create a bar chart comparing revenue across regions."
  + "Add a pie chart showing product category distribution."
  + "Build a counter widget displaying total revenue for this quarter."
* **Data exploration**:
  + "Which tables contain customer transaction data?"
  + "Show me the first 10 rows of the `@sales_transactions` dataset."
  + "Find a table that contains product inventory data."
* **Dashboard layout and organization**:
  + "Create a new page for regional performance metrics."
  + "Organize these visualizations into a two-column layout."
  + "Add a text widget explaining the key findings from this dashboard."
  + "Clone this page and modify it to show monthly trends instead of weekly."
* **Filters and interactivity**:
  + "Add a date range filter for the entire dashboard."
  + "Create a filter to allow users to select specific product categories."
  + "Add a region filter that applies to all visualizations on this page."
* **Data preparation**:
  + "Create a dataset from `@sales_transactions` that aggregates sales by week and product."
  + "Build a dataset that joins `@customers` and `@orders` tables."
  + "Add a custom calculation to compute the year-over-year growth rate."
* **Dashboard refinement**:
  + "Improve the color scheme to make the charts more readable."
  + "Add titles and descriptions to all visualizations."
  + "Add an image widget with our company logo to the header."
  + "Beautify this dashboard."
  + "Rename this dashboard to 'Q1 2026 Sales Performance'."