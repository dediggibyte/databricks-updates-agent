Declarative Automation Bundles can be created and modified directly in the workspace.

For requirements for using bundles in the workspace, see [Declarative Automation Bundles in the workspace requirements](/aws/en/dev-tools/bundles/workspace#requirements).

For more information about bundles, see [What are Declarative Automation Bundles?](/aws/en/dev-tools/bundles/).

## Create a bundle

To create a bundle in the Databricks workspace:

1. Navigate to the Git folder where you want to create your bundle.
2. Click the **Create** button, then click **Bundle**. Alternatively, right click on the Git folder or its associated kebab in the workspace tree and click **Create** > **Bundle**:
3. In the **Create a bundle** dialog, give the bundle a name, such as *totally-awesome-bundle*. The bundle name can only contain letters, numbers, dashes, and underscores.
4. For **Template**, choose whether you want to create a bundle using a custom template, an empty bundle, a bundle that runs a sample Python notebook, or a bundle that runs SQL. If you have the [Lakeflow Pipelines Editor](/aws/en/ldp/multi-file-editor) enabled, you will also see an option to create an ETL pipeline project. Any [custom templates](/aws/en/dev-tools/bundles/templates#configure-templates) configured in the workspace, will also be available.
5. Some templates require additional configuration. Click **Next** to finish configuring the project.

   | Template | Configuration options |
   | --- | --- |
   | Lakeflow Spark Declarative Pipelines | * Default catalog to use for the pipeline data * Use personal schema (recommended) for each user collaborating on this bundle * Initial language for the code files in the pipeline |
   | Default Python | * Include a sample notebook * Include a sample pipeline * Include a sample Python package * Use serverless compute |
   | Default SQL | * SQL warehouse path * Initial catalog * Use personal schema * Initial schema during development |
6. Click **Create and deploy**.

This creates an initial bundle in the Git folder, which includes the files for the project template that you selected, a `.gitignore` Git configuration file, and the required Declarative Automation Bundles `databricks.yml` file. The `databricks.yml` file contains the main configuration for the bundle. For details, see [Declarative Automation Bundles configuration](/aws/en/dev-tools/bundles/settings).

Any changes made to the files within the bundle can be synced with the remote repository associated with the Git folder. A Git folder can contain many bundles.

## Add new files to a bundle

A bundle contains the `databricks.yml` file that defines deployment and workspace configurations, source files, such as notebooks, Python files, and test files, and definitions and settings for Databricks resources, such as Lakeflow Jobs and Lakeflow Spark Declarative Pipelines. Similar to any workspace folder, you can add new files to your bundle.

tip

To open a new tab to the bundle view that lets you modify bundle files, navigate to the bundle folder in the workspace, then click **Open in editor** to the right of the bundle name.

### Add source code files

To add new notebooks or other files to a bundle in the workspace UI, navigate to the bundle folder, then:

* Click **Create** in the upper right and choose one of the following file types to add to your bundle: Notebook, File, Query, Dashboard.
* Alternatively, click the kebab to the left of **Share** and import a file.

note

In order for the file to be part of the bundle deployment, after you add a file to your bundle folder you must add it to the `databricks.yml` bundle configuration, or create a job or pipeline definition file that includes it. See [Add an existing resource to a bundle](#add-existing).

### Create a resource definition

Bundles contain definitions for resources such as jobs and pipelines to include in a deployment. When the bundle is deployed, resources defined in the bundle are created in the workspace (or updated if they have already been deployed). These definitions are specified in YAML or Python, and you can create and edit these configurations directly in the UI.

1. Navigate to the bundle folder in the workspace where you want to define a new resource.

   tip

   If you have previously opened the bundle in the editor in the workspace, you can use the workspace browser authoring contexts list to navigate to the bundle folder. See [Authoring contexts](/aws/en/workspace/workspace-browser#context).
2. To the right of the bundle name, click **Open in editor** to navigate to the bundle editor view.
3. Click the deployment icon for the bundle to switch to the **Deployments** panel.
4. In the **Bundle resources** section, click **Add**, then choose a resource definition to create.

#### New job definition

To create a bundle configuration file that defines a job:

1. In the **Bundle resources** section of the **Deployments** panel, click **Add**, then **New job definition**.
2. Type a name for the job into the **Job name** field of the **Create job definition** dialog. Click **Create**.
3. Add YAML to the job definition file that was created. The following example YAML defines a job that runs a notebook:

   YAML

   ```
   resources:  
     jobs:  
       run_notebook:  
         name: run-notebook  
         queue:  
           enabled: true  
         tasks:  
           - task_key: my-notebook-task  
             notebook_task:  
               notebook_path: ../helloworld.ipynb
   ```

For details about defining a job in YAML, see [job](/aws/en/dev-tools/bundles/resources#jobs). For YAML syntax for other supported job task types, see [Add tasks to jobs in Declarative Automation Bundles](/aws/en/dev-tools/bundles/job-task-types).

#### New pipeline definition

note

If you have enabled the [Lakeflow Pipelines Editor](/aws/en/ldp/multi-file-editor) in your workspace, see [New ETL pipeline](#etl).

To add a pipeline definition to your bundle:

1. In the **Bundle resources** section of the **Deployments** panel, click **Add**, then **New pipeline definition**.
2. Type a name for the pipeline into the **Pipeline name** field of the **Add pipeline to existing bundle** dialog.
3. Click **Add and deploy**.

For a pipeline with the name `test_pipeline` that runs a notebook, the following YAML is created in a file `test_pipeline.pipeline.yml`:

YAML

```
resources:  
  pipelines:  
    test_pipeline:  
      name: test_pipeline  
      libraries:  
        - notebook:  
            path: ../test_pipeline.ipynb  
      serverless: true  
      catalog: main  
      target: test_pipeline_${bundle.environment}
```

You can modify the configuration to run an existing notebook. For details about defining a pipeline in YAML, see [pipeline](/aws/en/dev-tools/bundles/resources#pipelines).

#### New ETL pipeline

To add a new ETL pipeline definition:

1. In the **Bundle resources** section of the **Deployments** panel, click **Add**, then **New ETL pipeline**.
2. Type a name for the pipeline into the **Name** field of the **Add pipeline to existing bundle** dialog. The name must be unique within the workspace.
3. For the **Use personal schema** field, select **Yes** for development scenarios and **No** for production scenarios.
4. Select a **Default catalog** and a **Default schema** for the pipeline.
5. Choose a language for the pipeline source code.
6. Click **Add and deploy**.
7. Review the details in the **Deploy to dev** confirmation dialog, then click **Deploy**.

An ETL pipeline is created with example exploration and transformation tables.

For a pipeline with the name `rad_pipeline`, the following YAML is created in a file `rad_pipeline.pipeline.yml`. This pipeline is configured to run on serverless compute. For pipeline configuration reference, see [pipeline](/aws/en/dev-tools/bundles/resources#pipelines).

YAML

```
resources:  
  pipelines:  
    rad_pipeline:  
      name: rad_pipeline  
      libraries:  
        - glob:  
            include: transformations/**  
      serverless: true  
      catalog: main  
      schema: ${workspace.current_user.short_name}  
      root_path: .
```

#### New dashboard definition

To create a bundle configuration file that defines a dashboard:

1. In the **Bundle resources** section of the **Deployments** panel, click **Add**, then **New dashboard definition**.
2. Type a name for the dashboard into the **Dashboard name** field of the **Add dashboard to existing bundle** dialog.
3. Select a **Warehouse** for the dashboard. Click **Add and deploy**.

A new empty dashboard and a configuration `*.dashboard.yml` file are created in the bundle. The dashboard is stored in the warehouse specified in the configuration file.

For details about dashboards, see [Dashboards](/aws/en/dashboards/). For YAML syntax for dashboard configuration, see [dashboard](/aws/en/dev-tools/bundles/resources#dashboards).

## Add an existing resource to a bundle

You can add existing resources to your bundle using the workspace UI or by adding resource configuration to your bundle.

### Use the bundle workspace UI

To add an existing job, pipeline, or dashboard to a bundle:

1. Navigate to the bundle folder in the workspace where you want to add a resource.

   tip

   If you have previously opened the bundle in the editor in the workspace, you can use the workspace browser authoring contexts list to navigate to the bundle folder. See [Authoring contexts](/aws/en/workspace/workspace-browser#context).
2. To the right of the bundle name, click **Open in editor** to navigate to the bundle editor view.
3. Click the deployment icon for the bundle to switch to the **Deployments** panel.
4. In the **Bundle resources** section, click **Add**, then click **Add existing job**, **Add existing pipeline**, or **Add existing dashboard**.
5. In the **Add existing ...** dialog, select the existing resource from the drop down.
6. When you add an existing resource to a bundle, Databricks creates a definition in a bundle configuration file for this resource. Because you can modify this definition in the bundle, the resource defined in the bundle can diverge from the resource used to create it.

   Choose an option for how to handle updates to the bundle resource configuration:

   * **Update on production deploys**: The existing resource becomes linked to the resource in the bundle, and any changes you make to the resource in the bundle are applied to the existing resource when you deploy to the `prod` target.
   * **Update on development deploys**: The existing resource becomes linked to the resource in the bundle, and any changes you make to the resource in the bundle are applied to the existing resource when you deploy to the `dev` target.
   * **(Advanced) Don't update**: The existing resource is not linked to the bundle. Changes made to the resource in the bundle are never applied to the existing resource. Instead, a copy is created. For more information about binding bundle resources to their corresponding workspace resource, see [databricks bundle deployment bind](/aws/en/dev-tools/cli/bundle-commands#databricks-bundle-deployment-bind).
7. Click **Add ...** to add the existing resource to the bundle.

### Add bundle configuration

An existing resource can also be added to your bundle by defining bundle configuration to include it in your bundle deployment. The following example adds an existing pipeline to a bundle.

Assuming you have a pipeline named `taxifilter` that runs the `taxifilter.ipynb` notebook in your shared workspace:

1. In your Databricks workspace's sidebar, click **Jobs & Pipelines**.
2. Optionally, select the **Pipelines** and **Owned by me** filters.
3. Select the existing `taxifilter` pipeline.
4. In the pipeline page, click the kebab to the left of the **Development** deployment mode button. Then click **View settings YAML**.
5. Click the copy icon to copy the bundle configuration for the pipeline.
6. Navigate to your bundle in **Workspace**.
7. Click the deployment icon for the bundle to switch to the **Deployments** panel.
8. In the **Bundle resources** section, click **Add**, then **New pipeline definition**.

   note

   If you instead see a **New ETL pipeline** menu item, then you have the [Lakeflow Pipelines Editor](/aws/en/ldp/multi-file-editor) enabled. To add an ETL pipeline to a bundle, see [Create a source-controlled pipeline](/aws/en/ldp/source-controlled).
9. Type `taxifilter` into the **Pipeline name** field of the **Add pipeline to existing bundle** dialog. Click **Create**.
10. Paste the configuration for the existing pipeline into the file. This example pipeline is defined to run the `taxifilter` notebook:

    YAML

    ```
    resources:  
      pipelines:  
        taxifilter:  
          name: taxifilter  
          catalog: main  
          libraries:  
            - notebook:  
                path: /Workspace/Shared/taxifilter.ipynb  
          target: taxifilter_${bundle.environment}
    ```

You can now deploy the bundle, then run the pipeline resource through the UI.

## Edit bundle resources

Beta

This feature is in [Beta](/aws/en/release-notes/release-types).

You can edit job and pipelines that are part of your bundle directly in the workspace UI. Changes are automatically applied to the configuration YAML for those resources in the bundle.

To edit a job or pipeline in a bundle:

1. From the **Deployments** pane of the bundle editor, click the job or pipeline in **Bundle resources** to open the job or pipeline.
2. Make changes to the job or pipeline, such as adding a notebook task or changing the pipeline schema.
3. A workspace notification appears that confirms that the edits to the job or pipeline were applied to the bundle configuration. You can click the YAML file link in the notification to view the configuration changes in the bundle editor.
4. Deploy the bundle so that the configuration changes are applied to the deployment.

note

Editing resources is always 