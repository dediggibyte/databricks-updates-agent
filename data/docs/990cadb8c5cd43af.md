This page describes how to create Databricks Git folders and perform common Git operations, including cloning, branching, committing, and pushing.

This guide covers the following Git operations:

| **Setup and configuration** | **Daily workflow** | **Advanced operations** |
| --- | --- | --- |
| * [Clone a repo](#clone-repo) * [Use the Git CLI (Beta)](#use-git-cli) * [Access the Git dialog](#open-the-git-dialog) | * [Create a new branch](#create-a-new-branch) * [Switch to a different branch](#switch-branch) * [Commit and push changes](#commit-push) * [Pull changes](#pull-changes) * [Collaborate in Git folders](#best-practices) | * [Merge branches](#merge-branches) * [Resolve merge conflicts](#merge-conflicts) * [Rebase a branch](#rebase) * [Reset a branch](#reset) * [Configure sparse checkout](#sparse) * [Delete a Git folder](#trash-repo) |

## Clone a repo

When you clone a remote repository, Databricks creates a Git folder in your workspace that contains the repo contents and tracks changes. You can create Git folders using the Databricks UI or the web terminal.

note

* You must have `CAN MANAGE` permission on the parent folder where you want to create the Git folder.
* Your workspace must have Git credentials configured. See [Connect your Git provider to Databricks](/aws/en/repos/get-access-tokens-from-git-provider).

### Clone from the UI

1. In the sidebar, select **Workspace** and browse to the folder where you want to create the Git repo clone.
2. Click **Create** > **Git folder**.
3. In the **Create Git folder** dialog, provide the following information:

   | Field | Description |
   | --- | --- |
   | Git repository URL | The URL of the Git repository you want to clone, in the format `https://example.com/organization/project.git`. |
   | Git provider | The Git provider for the repository you want to clone. |
   | Git folder name | The name of the folder in your workspace that contains the contents of the cloned repo. |
   | Sparse checkout mode | Whether to use [sparse checkout](#sparse), which clones only a subset of your repository's directories using a cone pattern. This is useful if your repository exceeds the [size limits](/aws/en/repos/limits). |
   | Enable Git CLI support (Beta) | Run standard Git commands directly from a Databricks terminal, including pre-commit hooks, Git submodules, and Large File Storage (LFS). See [Use Git CLI commands (Beta)](#use-git-cli). This option requires serverless compute. If serverless compute isn't available in your workspace, clone from the [web terminal](#clone-terminal) instead. |
4. Click **Create Git folder**. The remote repository contents are cloned to your workspace, and you can start working with supported Git operations.

### Clone from the web terminal

You can also create Git folders with CLI access directly from the web terminal:

1. Access the web terminal. See [Run shell commands in Databricks web terminal](/aws/en/compute/web-terminal).
2. Navigate to the parent directory in `/Workspace`:

   Bash

   ```
   cd /Workspace/Users/<your-email>/<project>
   ```

   note

   You can't create Git folders with [Git CLI access](#use-git-cli) in `/Repos` or in existing Git folders.
3. Clone your repository:

   Bash

   ```
   git clone <remote-url>
   ```

   The `git clone` command uses the Git credentials configured in your workspace. See [Connect your Git provider to Databricks](/aws/en/repos/get-access-tokens-from-git-provider).
4. Refresh your browser to see the new folder in the workspace file browser.

## Use Git CLI commands (Beta)

Beta

This feature is in [Beta](/aws/en/release-notes/release-types). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](/aws/en/admin/workspace-settings/manage-previews).

Git folders with Git CLI access let you run standard Git commands directly from a Databricks terminal. You can:

* Run any Git command including `git stash`, `git pull --force`, and `git rebase -i`.
* Integrate linting and code scanning with pre-commit hooks.
* Work with repositories that exceed the 2 GB memory and 4 GB disk limits of standard Git folders.
* Use Git submodules and Large File Storage (LFS).
* Stage multiple commits locally before pushing to the remote repository.

### Git CLI compute requirements

The required compute depends on how you use a CLI-enabled Git folder:

| Operation | Compute requirement |
| --- | --- |
| Create a Git folder with CLI access from the UI | [serverless compute](/aws/en/compute/serverless/) |
| Run Git operations from the Git folders UI (pull, push, commit) | [serverless compute](/aws/en/compute/serverless/) |
| Run Git CLI commands from the web terminal | [serverless compute](/aws/en/compute/serverless/) (environment version 4 or above) or classic compute (Databricks Runtime 17.0 or above) |

To enable serverless compute, see [Connect to serverless compute](/aws/en/compute/serverless/).

If your Git provider requires private network connectivity, see [Configure network connectivity](/aws/en/repos/repos-setup#network-connectivity).

### Create a Git folder with Git CLI access

To create a Git folder with CLI access:

* If you use the [web terminal](#clone-terminal), any repository that you clone has Git CLI access automatically.
* If you use the [UI](#clone-ui), select **Enable Git CLI support** when you create the Git folder.

After you create a Git folder with CLI access, run any standard Git command from the web terminal. To open a web terminal, see [Launch the web terminal](/aws/en/compute/web-terminal#launch).

Bash

```
cd /Workspace/Users/<your-email>/<project>/my-repo  
  
# Interactive rebase  
git rebase -i main  
  
# Stash uncommitted changes  
git stash  
  
# Work with submodules  
git submodule update --init --recursive
```

### Git CLI limitations

Git folders with CLI access have the following limitations:

* [Remote URL allowlists](/aws/en/repos/repos-setup#allow-lists) are ignored for Git folders with Git CLI support.
* Git CLI commands ignore the admin setting that blocks committing notebook outputs.
* The Repos API isn't supported for Git folders with CLI access.
* You can't enable Git CLI access for existing Git folders.

### Troubleshoot Git CLI operations

* **Git operations are disabled in the workspace UI**: Serverless compute isn't enabled in your workspace. You can still run Git commands from the web terminal. To enable serverless compute, see [Connect to serverless compute](/aws/en/compute/serverless/).
* **Terminal prompts for credentials on every operation**: The Git CLI feature isn't enabled on your workspace. Contact your workspace admin to verify that the preview is enabled.
* **Git operations fail with permission errors**: Verify that you have `CAN MANAGE` permission on the parent folder and that your workspace Git credentials are valid. See [Connect your Git provider to Databricks](/aws/en/repos/get-access-tokens-from-git-provider).

## Access the Git dialog

Access the Git dialog from a notebook or from the Databricks Git folders browser.

* From a notebook, click the button next to the notebook name that identifies the current Git branch.
* From the Databricks Git folders browser, click **Git** beside the repo name.

A full-screen dialog appears where you can perform Git operations.

1. Your current working branch. You can select other branches here. If other users have access to this Git folder, changing the branch also changes the branch for them if they share the same workspace. See a recommended [best practice](#best-practices) to avoid this problem.
2. Create a new branch.
3. File assets and subfolders checked into your current branch.
4. Show the current branch history.
5. Pull content from the remote Git repository.
6. Add a commit message and optional expanded description for your changes.
7. Commit your work to the working branch and push the updated branch to the remote Git repository.

Click the  kebab menu to choose from additional Git branch operations, such as a hard reset, merge, or rebase.

## Create a new branch

To create a new branch:

1. Open the [Git dialog](#open-the-git-dialog).
2. Click **Create Branch**.
3. Enter a name for the new branch and select the base branch.
4. Click **Create**.

## Switch to a different branch

To check out a different branch, use the branch dropdown in the Git dialog:

Uncommitted changes on the current branch carry over and show as uncommitted changes on the new branch, if the uncommitted changes don't conflict with code on the new branch. Discard the changes before or after branch switches if you don't intend to carry over the uncommitted changes.

The local version of a branch can remain present in the associated Git folder for up to 30 days after you delete the remote branch. To completely remove a local branch in a Git folder, delete the repository.

important

Switching branches might delete workspace assets when the new branch doesn't contain these assets. Switching back to the current branch recreates the deleted assets with new IDs and URLs. This change can't be reversed.

If you shared or bookmarked assets from a Git folder, verify the asset exists on the new branch before switching.

## Commit and push changes

When you add new notebooks or files, or make changes to existing notebooks or files, the Git folder UI highlights the changes.

Add a required commit message for the changes, and click **Commit & Push** to push the changes to the remote Git repository.

If you don't have permission to commit to the default branch, create a new branch and use your Git provider's interface to create a pull request and merge it into the default branch.

note

Notebook outputs aren't included in commits by default when notebooks are saved in source file formats (`.py`, `.scala`, `.sql`, `.r`). For information on committing notebook outputs using the IPYNB format, see [Control IPYNB notebook output artifact commits](/aws/en/notebooks/notebook-format#notebook-outputs-commit).

## Pull changes

To pull changes from the remote Git repository, click **Pull** in the Git operations dialog. Notebooks and other files update automatically to the latest version in your remote Git repository. If the changes pulled from the remote repo conflict with your local changes in Databricks, resolve the [merge conflicts](#merge-conflicts).

important

Git operations that pull upstream changes clear the notebook state. See [Incoming changes clear the notebook state](/aws/en/repos/limits#incoming-changes-clear-notebook-state).

## Collaborate in Git folders

Databricks Git folders behave as embedded Git clients in your workspace, letting you collaborate through Git-based source control and versioning. For effective team collaboration:

* Each team member has their own Git folder mapped to the remote Git repository, where they work in their own development branch.
* Only one user performs Git operations on each Git folder. Multiple users performing Git operations on the same folder can cause branch management issues, such as one user unintentionally switching branches for everyone.

To share your Git folder configuration with a collaborator:

1. Click **Share**.
2. Click **Copy link to create Git folder**.
3. Send the URL to your collaborator.
4. When your collaborator opens the URL, they see a dialog pre-populated with your Git folder configuration.
5. They click **Create Git folder** to clone the repository into their own workspace under their current working folder.

## Merge branches

The merge function in Databricks Git folders uses `git merge` to combine the commit history from one branch into another. For Git beginners, Databricks recommends using merge instead of rebase because it doesn't require force pushing and doesn't rewrite commit history.

To merge one branch into another, click the  kebab menu and select **Merge**.

* If there's a merge conflict, resolve it in the Git folders UI.
* If there's no conflict, the merge pushes to the remote Git repo using `git push`.

## Resolve merge conflicts

Merge conflicts occur when Git can't automatically reconcile changes to the same lines of a file from different sources, such as during a pull, rebase, or merge operation.

To resolve a merge conflict, use the Git folders UI which displays conflicting files and resolution options.

* Manually edit the file to choose which changes to keep.
* Select **Keep all current changes** or **Take all incoming changes** to accept one version entirely.
* Abort the operation and discard conflicting changes to try again.

### Manually resolve conflicts

Manual conflict resolution lets you determine which conflicting lines to accept. Edit the file contents directly to resolve the conflicts.

To resolve the conflict, select the code lines you want to preserve and delete everything else, including the Git merge conflict markers. When you're done, select **Mark As Resolved**.

If you made the wrong choices when resolving merge conflicts, click **Abort** to abort the process and undo everything. Once all conflicts are resolved, click **Continue Merge** or **Continue Rebase** to resolve the conflict and complete the operation.

## Rebase a branch

The rebase function in Databricks Git folders uses `git rebase` to integrate changes from one branch into another by reapplying your commits on top of the target branch, creating a linear history.

To rebase a branch on another branch, click the  kebab menu and select **Rebase**, then select the target branch.

* After the rebase, Git folders run `git commit` and `git push --force` to update the remote repo.
* Rebase rewrites commit history, which can cause versioning issues for collaborators working in the same repo.

## Reset a branch

Perform a Git reset from the Git folders UI. This operation is equivalent to `git reset --hard` combined with `git push --force`.

Git reset replaces the branch contents and history with the most recent state of another branch. You can use this