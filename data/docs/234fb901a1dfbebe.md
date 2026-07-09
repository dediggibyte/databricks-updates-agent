Databricks notebooks can display images, mathematical equations, HTML, and links to other notebooks, all from Markdown cells.

## Display images

Databricks supports displaying images in Markdown cells. There are several ways to display images:

* **Paste**: Paste an image from your clipboard using `⌘`+`V` (mac) or `Ctrl`+`V` (Windows). The image is uploaded to the current workspace directory and displayed in the cell.
* **Drag and drop**: Drag and drop images from your local file system into markdown cells. The image is uploaded to the current workspace directory and displayed in the cell.
* **Display images from your workspace**: Use either absolute paths or relative paths to display images stored in your workspace with the following syntax:

  Markdown

  ```
  %md  
  ![my_test_image](/Workspace/absolute/path/to/image.png)  
    
  ![my_test_image](./relative/path/to/image.png)
  ```
* **Display images stored in volumes**: Use absolute paths to display images stored in volumes with the following syntax:

  Markdown

  ```
  %md  
  ![my_test_image](/Volumes/absolute/path/to/image.png)
  ```
* **Display external images**: Use URLs to display external images with the following syntax:

  Markdown

  ```
  %md  
  ![my_test_image](image_url)
  ```

## Display mathematical equations

Notebooks support [KaTeX](https://github.com/Khan/KaTeX/wiki) for displaying mathematical formulas and equations. For example,

Markdown

```
%md  
\\(c = \\pm\\sqrt{a^2 + b^2} \\)  
  
\\(A{\_i}{\_j}=B{\_i}{\_j}\\)  
  
$$c = \\pm\\sqrt{a^2 + b^2}$$  
  
\\[A{_i}{_j}=B{_i}{_j}\\]
```

renders as:

and

Markdown

```
%md  
\\( f(\beta)= -Y_t^T X_t \beta + \sum log( 1+{e}^{X_t\bullet\beta}) + \frac{1}{2}\delta^t S_t^{-1}\delta\\)  
  
where \\(\delta=(\beta - \mu\_{t-1})\\)
```

renders as:

## Include HTML

You can include HTML in a notebook by using the function `displayHTML`. See [HTML, D3, and SVG in notebooks](/aws/en/visualizations/html-d3-and-svg) for an example of how to do this.

note

The `displayHTML` iframe is served from the domain `databricksusercontent.com` and the iframe sandbox includes the `allow-same-origin` attribute. Your browser must be able to access `databricksusercontent.com`. If your corporate network blocks it, add it to an allowlist.

## Link to other notebooks

You can link to other notebooks or folders in Markdown cells using relative paths. Specify the `href`
attribute of an anchor tag as the relative path, starting with a `$` and then follow the same
pattern as in Unix file systems:

Markdown

```
%md  
<a href="$./myNotebook">Link to notebook in same folder as current notebook</a>  
<a href="$../myFolder">Link to folder in parent folder of current notebook</a>  
<a href="$./myFolder2/myNotebook2">Link to nested notebook</a>
```