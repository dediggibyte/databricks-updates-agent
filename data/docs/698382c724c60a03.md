This page explains how to use and customize visualization widgets on AI/BI dashboards.

## Create and configure a chart

After adding a visualization widget to the canvas, the **Visualization Configuration** panel appears on the right side of the screen. By default, the first dataset listed on the **Data** tab is selected, and the default visualization type is a **Bar** chart.

To create a chart, use the following steps:

1. **Select a dataset:** Use the **Dataset** drop-down to choose the dataset for your visualization.
2. **Add filters (optional):** Click **Show filters** to apply a static filter or parameter to your visualization. You can filter on any field. If your dataset includes a parameter, an option to apply it will also appear.
3. **Choose a visualization type:** Select a visualization type from the **Visualization** drop-down menu. For details about available visualization types and their configurations, see [AI/BI dashboard visualization types](/aws/en/dashboards/manage/visualizations/types).
4. **Define x-axis and y-axis fields:** After selecting a dataset, choose the fields to display on the x-axis and y-axis. You can reorder fields by dragging them into the desired position. For chart labels, you can use the display name field to rename the axis label.

note

If you use the Genie Code to generate a chart, the dataset and visualization selections automatically adjust based on your request. For step-by-step guidance on creating AI-assisted visualizations, see [Use Genie Code for dashboard authoring](/aws/en/dashboards/manage/dashboard-agent).

## View the visualization query

While in draft mode, you can view the full SQL query that a visualization widget runs, including any parameters and filters currently applied. This is useful for verifying data accuracy, troubleshooting unexpected results, or understanding how dashboard filters and parameters affect the underlying query.

1. Click the  kebab menu on the visualization widget.
2. Click **View visualization query**.

A modal appears displaying the SQL query for the visualization widget. This query is specific to the widget and only returns the data necessary to render that visualization — it is not the same as the full dataset query. The query reflects the current state of any applied filters. If the underlying dataset uses parameters, parameter values are not substituted into the query. Instead, they appear at the top of the modal for reference.

## Apply chart formatting

Charts include customizable formatting options for axes, colors, labels, and tooltips. Formatting options vary by chart type and dataset values.

The following screenshot highlights the kebab menus used for formatting the x and y axes.

### Format axis settings

To format the x-axis or y-axis, use the  kebab menu in the respective **X Axis** or **Y Axis** section of the visualization editing panel.

Configure the following settings:

* **Show axis title:** Enabled by default. Enter a custom title or clear the checkbox to hide the axis title.
* **Show axis values:** Enabled by default. Clear the checkbox to hide axis values.

Depending on the type of data represented, additional controls appear.

For continuous data:

* **Custom minimum and maximum values:** Type in values to set limits on the displayed data.
* **Reverse axis:** Select **Reverse Axis** to show the axis values in descending order.
* **Scale function:** Choose **Linear** or **Log (Symmetric)**.
* Click **Format** to view additional formatting options. **Auto** automatically formats your chart and is selected by default. Click **Custom** to see additional formatting options. See [Format numeric values](#number-formatting).

For categorical data:

* **Label Angle:** Choose the angle at which to apply the labels. **Auto** is selected by default.
* **Sort:** Choose how to order categorical values on the axis:
  + **Alphabetical**: Sort category names alphabetically
  + **By field**: Sort by a measure field value in ascending or descending order. After selecting the sort direction, choose which field to use:
    - **Y axis**: Sort by the measure field displayed on the Y axis
    - **Field**: Sort by any other measure field in the dataset, even if it's not displayed on the chart. Select the field from the dropdown and choose the aggregation (SUM, MIN, MAX, or COUNT). This is useful for ordering categories by metrics that provide context without cluttering the visualization.
  + **Custom**: Arrange values in a specific order. Hover over a value and use the grab-handle to drag it into position.

note

If any of the listed options are unavailable, they cannot be applied to the selected chart type.

## Format numeric values

You can format numbers for axis tick labels, data labels, and tooltips. To access formatting options:

1. Click the  kebab menu next to **X Axis** or **Y Axis** in the chart configuration panel.
2. Click **Format** and choose from the following options:

* **Type:** None, Currency (**$**), Percentage (**%**)
* **Abbreviation:** None, Compact, Scientific
* **Decimal places:** Max, Exact, All, or a custom number of places
* **Group separator:** Optionally, include a comma or other separator.
* **Negative sign:** Choose how negative numbers are displayed. Select **-123.45** (default) for a standard minus sign, or select **(123.45)** to use accounting-style parentheses.

note

Different currency formats are available. After selecting **Currency**, choose your preferred option from the drop-down menu.

## Customize chart elements

You can format chart legends, colors, line patterns, tooltips, and value labels.

### Chart colors

To change chart colors:

1. Click a color in the chart to open the color picker.
2. Enter a HEX or RGB value for an exact color.
3. Click the  kebab menu in the **Color** section to adjust the opacity of all colors.

### Legend

Click the  kebab menu in the **Color** section to show options for changing the visibility, title, or position of the chart legend. The following options are available:

* **Show legend:** Use the checkbox to show or hide the legend.
* **Show legend title:** Use the checkbox to show or hide the legend title. When the title is visible, you can type to override the default value, which is the column name.
* **Legend position:** Use the drop-down to adjust the legend's placement in the visualization widget. Legends can be positioned at the top, bottom, left, or right of the visualization.

### Tooltips

Tooltips display precise measures of the data under the pointer. By default, they show values from the x-axis, y-axis, and any color/grouping fields. To add more fields to a tooltip:

1. Click the the  plus icon in the **Tooltip** section of the visualization editor.
2. Use the drop-down to select additional fields, or use the text entry box to search by name.

note

If the **Tooltip** section is not present in the visualization editor, that chart type does not support tooltip customization.

### Value labels

Use the toggle to turn data labels on or off. When enabled, you can choose how the labels display:

* **Auto**: Displays y-axis values as labels.
* **Field**: Select a specific field to display as labels. You can apply a transformation (such as SUM or AVG) and choose formatting options for the selected field.

Null values are not displayed as labels on the chart. You can use conditional logic to selectively display labels.

The following query creates a dataset where labels appear only for specific data points:

SQL

```
SELECT  
  *,  
  CASE  
    WHEN pickup_zip = 10009 THEN fare_amount  
    ELSE NULL  
  END AS custom_label  
FROM  
  main.samples.taxi_trips
```

When you use `custom_label` as the value label field, only data points where `pickup_zip = 10009` display labels showing the `fare_amount`. All other data points with null values appear on the chart without labels.

### Size settings

The **Size** setting controls visual dimensions for line charts, scatter charts, bubble charts, and point maps. Its usage depends on the chart type:

**Line charts:**

* If no series are specified in the **Size** area, the slider changes all line thickness uniformly.
* If series are specified in the **Size** area, you can set different thickness values for each series.

**Scatter and bubble charts:**

* Add a field to the **Size** setting to vary the point marker size based on a metric.
* When size is based on a data field, the chart becomes a bubble chart where each point's size reflects the metric value.

**Point maps:** Use the **Size** setting to vary map marker sizes based on a quantitative field, showing magnitude at different geographical locations.

### Gridlines

Charts support toggling gridlines on and off to improve readability. Gridlines appear by default on supported chart types and help viewers interpret data points by providing visual reference lines aligned with axis values.

To toggle gridlines:

1. In the visualization configuration panel, locate the gridline options.
2. Use the toggle to show or hide gridlines for the chart.

Gridlines automatically adjust based on your custom background colors and axis formatting settings.

### Annotations

Annotations are horizontal or vertical reference lines that you can add to charts to track thresholds, targets, or benchmarks. Annotation lines can be a fixed constant value or driven by your data, such as an average or a specific measure.

The following chart types support annotations:

* **Constant and Custom**: Area, Bar, Box, Combo, Heatmap, Histogram, Line, Scatter, and Waterfall
* **Aggregate**: Area, Bar, Box, Line, and Scatter only. Not available on charts with 100% stack layout.

To add an annotation:

1. In the visualization configuration panel, locate the **Annotation** section.
2. Click the  plus icon to add a new annotation.
3. Select the line orientation:
   * **Horizontal**: Draws a line parallel to the x-axis at a specified y-axis value.
   * **Vertical**: Draws a line parallel to the y-axis at a specified x-axis value.
4. Select the annotation type and configure it:
   * **Constant**: Enter a fixed value where the line should appear.
   * **Aggregate Y** (horizontal) / **Aggregate X** (vertical): Select an aggregation (**Avg**, **Min**, or **Max**). The line position is calculated as an aggregation over the underlying chart data.
   * **Custom**: Select a field or measure from your dataset. The line position is calculated in a separate query. If you select an aggregated field, a single line is drawn. If you select a non-aggregated field, one line is drawn per returned row.
5. (Optional) Enter a label. The label appears on the chart next to the line.
6. (Optional) Click the color picker to customize the line color.

You can add multiple annotations to a single chart to track different thresholds or reference points.

## Generate a forecast

Use **AI Forecast** ([Public Preview](/aws/en/release-notes/release-types)) to apply predictive forecasting to line charts to visualize future trends and patterns. Your line chart must have a temporal date field on the x-axis and a single numeric field on the y-axis.

To create a chart with AI forecast:

* With your line chart selected, click the  plus icon to the right of **Forecast**.
* Click **Clone with AI Forecast** in the dialog that appears. A new line chart is created with forecasting applied.

To learn more about the function that generates the forecast, see [`ai_forecast` function](/aws/en/sql/language-manual/functions/ai_forecast).

### Faceting

Add a dimension to the **Facet** encoding to repeat a chart for all values in that dimension, also known as trellis or small multiple charts. Axes remain synced across all repeated charts, making comparisons easy. To add faceting:

1. Click the the  plus icon in the **Facet** section of the visualization editor.
2. Use the drop-down menu to select a dimension field.

In the  kebab menu next to **Facet**, you can optionally set the number of rows and columns in the underlying grid. Values that overflow the grid scroll on the chart.

**Configuration values**: For this example, the following values were set:

* Dataset: `samples.bakehouse.sales_transactions`
* X axis:
  + Field: `dateTime`
  + Transform: `Daily`
* Y axis:
  + Field: `COUNT(*)`
* Facet:
  + Field: `product`

## Other visualization types

To learn more about working with table visualizations, see [Table and pivot table visualizations](/aws/en/dashboards/manage/visualizations/tables).

To learn more about working with map visualizations, see [Map visualizations](/aws/en/dashboards/manage/visualizations/maps).