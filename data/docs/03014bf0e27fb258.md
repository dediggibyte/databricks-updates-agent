This page explains how to use parameters on AI/BI dashboards. If you want to learn about field filters instead, see [Filter on fields](/aws/en/dashboards/manage/filters/field-filters).

AI/BI dashboard parameters let you substitute different values into dataset queries at runtime. This allows you to filter data by criteria such as dates and product categories before data is aggregated in a SQL query, leading to more efficient querying and precise analysis. Parameters can be used with filter widgets to make dashboards interactive or with visualization widgets to make datasets easier to reuse.

Dashboard authors or editors add parameters to datasets and connect them to one or more widgets on the dashboard canvas. For static parameters set in visualization widgets, the values are set by the authors or editors. For parameters used in filter widgets, dashboard viewers can interact with the data by selecting values in filter widgets at runtime. This interaction reruns the associated queries and displays visualizations based on the filtered data.

## Choose between field filters and parameters

Parameters directly modify the query, which can be powerful. Dataset field filters can also offer dashboard interactivity, more features, and better performance with large datasets than parameters. Field filters support cascading behavior by default: when one filter is applied, the options available in other filters automatically update to reflect compatible values. For more information, see [Should I filter on a field or a parameter?](/aws/en/dashboards/manage/filters/#field-v-param).

## Add a parameter to a query

You must have at least CAN EDIT permissions on the draft dashboard to add a parameter to a dashboard dataset. You can add parameters directly to the dataset queries in the **Data** tab.

To add a parameter to a query:

1. Place your cursor where you want to place the parameter in your query.
2. Click **Add parameter** to insert a new parameter.

   This creates a new parameter with the default name `parameter`. To change the default name, replace it in the query editor. You can also add parameters by typing this syntax in the query editor.

## Edit a query parameter

To edit a parameter:

1. Click  next to the parameter name. A **Parameter details** dialog appears and includes the following configuration options:

   * **Keyword**: The keyword that represents the parameter in the query. This can only be changed by directly updating the text in the query.
   * **Display name**: The name in the filter editor. By default, the title is the same as the keyword.
   * **Type**: Supported types include **String**, **Date**, **Date and Time**, **Numeric**.

     + The default type is **String**.
     + The **Numeric** datatype allows you to specify between **Decimal** and **Integer**. The default numeric type is **Decimal**.
   * **Allow multiple selections**: Select the checkbox to allow users to choose multiple parameters at runtime.

     note

     This selection might require an additional change to your query. See [Allow multiple selections](#multi-select).
2. Click another part of the UI to close the dialog.

## Set a default parameter value

To test your query, type a default value into the text field under the parameter name and run the query. This applies the parameter value so you can preview the results and confirm that the query runs as expected. Running the query also saves the default value.

When you use the parameter in a filter widget, the default value from the **Data** tab is used unless the widget specifies a different default. See [Use dashboard filters](/aws/en/dashboards/manage/filters/).

Dashboard authors should confirm that parameterized queries run successfully with the selected default values on the dataset tab. Databricks queries the dataset schema to populate the widget configuration editor. In some cases, particularly with parameterized queries that use the `IDENTIFIER` clause, the dataset query can fail to run with the default parameter values, even though it would succeed when a user selects a value at runtime.

## Allow multiple selections

Queries that allow multiple selections must include an `ARRAY_CONTAINS` function in the query.

The following example shows a SQL query that allows you to select multiple values to insert into the query at runtime. The `WHERE` clause uses the `ARRAY_CONTAINS` function with an additional `NULL` check. The parameter must be set to hold multiple values so that it can be inserted into the query as an array.

When the query runs:

* If specific values are selected, each row is evaluated and all rows where `l_quantity` matches at least one value in `:parameter` are included in the result set.
* If "All" is selected, the parameter is `NULL` and all rows are returned (no filtering is applied).

SQL

```
SELECT  
  *  
FROM  
  samples.tpch.lineitem  
WHERE array_contains(:parameter, l_quantity) OR :parameter IS NULL
```

To set default values:

1. Write a dataset query that uses the `ARRAY_CONTAINS` function to filter rows based on a list of values.
2. Click  the gear icon next to the parameter name. Select **Allow multiple selections**.

   note

   This step allows the parameter to be inserted into the query as an array. If the `ARRAY_CONTAINS` function is used without enabling multiple selections, an error occurs.
3. Type a value into the text field under the display name. You can enter more than one value. Select the current value before entering the next one.

## Apply date range parameters

You can use parameters to define a range and return only results within that range. When you choose one of the following parameter types, you create two parameters that are designated by `.min` and `.max` suffixes:

* Date Range
* Date and Time Range

The following example shows a SQL query that creates a date range parameter named `date_param`. The `OR :date_param IS NULL` condition handles the case when a viewer selects **All**, which sets the parameter to `null` and returns all rows.

SQL

```
SELECT * FROM samples.tpch.lineitem  
WHERE l_shipdate BETWEEN :date_param.min AND :date_param.max  
  OR :date_param IS NULL
```

To create a date range parameter:

1. Click **Add parameter**.
2. Click  next to the parameter name. Enter the **Keyword** and **Display name**. Do not include `.min` or `.max` suffixes.
3. Choose **Date Range** or **Date and Time Range** as the **Type**.
4. Insert a `WHERE` clause that defines the range into your query. To define the range, use a `BETWEEN` clause with `.min` and `.max` values and include an `OR :parameter IS NULL` condition to handle **All** selections. For example:

   SQL

   ```
    WHERE date_col BETWEEN :date_param.min AND :date_param.max  
      OR :date_param IS NULL
   ```
5. Enter default date values and run the query to test it. Use the calendar icon to choose preset options like last week or last month.

### Specify a relative date range

To set a relative date range as the default parameter value, type the expression directly into the default value field instead of selecting from the calendar. Use the following syntax to express the last `n` days:

```
now-{n}d/d
```

* `{n}`: The number of days to go back from today.
* `/d`: Rounds the result to the start of the day.

For example, to configure a default range of the last 30 days, set the `.min` value to `now-30d/d` and the `.max` value to `now/d`.

## Use parameters in custom calculations

You can reference parameters directly in custom calculations using the `:keyword` syntax. See [Use parameters in custom calculations](/aws/en/dashboards/manage/data-modeling/custom-calculations/#parameters).

## Query-based parameters

Query-based parameters allow authors to define a dynamic or static list of values that viewers can choose from when setting parameters as they explore data in a dashboard. They are defined by combining a field filter and a parameter filter in a single filter widget.

To create a query-based parameter, the dashboard author performs the following steps:

1. Create a dataset whose result set is limited to a list of possible parameter values.
2. Create a dataset query that uses a parameter.
3. Configure a filter widget on the canvas that filters on a field and uses a parameter.
   * The **Fields** configurations should be set to use the field with the desired list of eligible parameter values.
   * The **Parameters** configuration should be set to select a parameter value.

See [Use query-based parameters](/aws/en/dashboards/tutorials/query-based-params) for a step-by-step tutorial that demonstrates how to add a query-based parameter and visualization.

note

If a dataset used in query-based parameters is also used in other visualizations on a dashboard, a viewer's filter selection modifies all connected queries. To avoid this, authors should create a dedicated dataset for query-based parameters that is not used in any other visualizations on the dashboard.

### Create a dynamic parameter list

To create a dynamic dataset that populates the drop-down that viewers use to select parameter values, write a SQL query that returns a single field and includes all the values in that field. Any new value in that field is automatically added as a parameter selection. An example SQL query is as follows:

SQL

```
 SELECT  
    DISTINCT c_mktsegment  
  FROM  
    samples.tpch.customer
```

### Create a static parameter list

You can create a static dataset that only includes values you hardcode into your dataset. An example query is as follows:

SQL

```
SELECT  
  *  
FROM  
  (  
    VALUES  
      ('MACHINERY'),  
      ('BUILDING'),  
      ('FURNITURE'),  
      ('HOUSEHOLD'),  
      ('AUTOMOBILE')  
  ) AS data(available_choices)
```

## Remove a query parameter

To remove a parameter, delete it from your query.

## Static widget parameters

Static widget parameters are configured directly in a visualization widget, allowing authors to individually parameterize visualization widgets that share the same dataset. This allows for the same dataset to present different views on the canvas.

The example in this section is based on a dataset that queries the `samples.nyctaxi.trips` table. The provided query returns the distance of each trip and categorizes the pickup day as either `Weekday` or `Weekend`. The query parameter filters for results based on whether the pickup occurred on a weekday or weekend.

The query text is provided in the following code block, but the instructions in this section are limited to setting up the associated visualizations configured with static widget parameters. For instructions on setting up a dataset with parameters, see [Add a parameter to a query](#add-parameter-to-query).

SQL

```
  WITH DayType AS (  
    SELECT  
      CASE  
        WHEN DAYOFWEEK(tpep_pickup_datetime) IN (1, 7) THEN 'Weekend'  
        ELSE 'Weekday'  
      END AS day_type,  
      trip_distance  
    FROM samples.nyctaxi.trips  
  )  
  SELECT day_type, trip_distance  
  FROM DayType  
  WHERE day_type = :day_type_param
```

To add a static widget parameter to a visualization:

1. Add a visualization widget to the draft dashboard canvas.
2. With the new widget selected, choose the parameterized dataset from the **Dataset** drop-down in the configuration panel.
3. Click **Show filters**. For datasets that include parameters, a **Parameters** section appears in the configuration panel.
4. Click the plus sign to the right of the **Parameters** heading and choose a parameter from the drop-down.
5. By default, the parameter value mirrors what is set in the query on the **Data** tab. You can keep it or choose a new value to substitute into the dataset. Navigate away from the text field to show the visualization with the new parameter applied.
6. Review your dashboard.

   The following image shows two visualization widgets. Each is configured as a histogram with a static widget parameter. The chart on the left shows the distribution of trip distances for trips starting on weekdays, while the chart on the right shows the same data for weekends. Both visualizations are based on the same dataset.

### Compare data using a filter condition

You can add a filter condition that allows you to compare aggregations on a part of the data to the aggregations applied to the whole dataset.

The following example extends the previous query to include a filter condition where the specified parameter value is `All`, which does not appear in the data. The first part of the filter condition works the same as in the previous example, filtering for results where the `day_type` is either `Weekday` or `Weekend`. The second part of the filter condition checks if the parameter itself is set to a certain value, in this case `All`, that does not appear in the data. When you set the default value for that parameter in the dataset editor, you're effectively bypassing the filter when neither `Weekday` nor `Weekend` are passed in as values.

SQL

```
WITH DayType AS (  
  SELECT  
    CASE  
      WHEN DAYOFWEEK(tpep_pickup_datetime) IN (1, 7) THEN 'Weekend'  
      ELSE 'Weekday'  
    END AS day_type,  
    trip_distance  
  FROM  
    samples.nyctaxi.trips  
)  
SELECT  
  day_type,  
  trip_distance  
FROM  
  DayType  
WHERE  
  day_type = :day_type_param  
  OR :day_type_param = 'All'
```

note

This example uses a custom string value (`'All'`) for single-value parameters where "All" is defined as a static option. For multi-select parameters, use `OR :parameter IS NULL` instead to handle "All" selections. See [Allow multiple selections](#multi-select).

You can use this dataset to configure three visualization widgets, with the `day_type_param` set to `All`, `Weekday` and `Weekend` respectively. Then, dashboard viewers can compare each dataset filtered by day type to the whole dataset.

The following GIF shows how you can quickly build three charts from the dataset created with this query.

1. The first ch