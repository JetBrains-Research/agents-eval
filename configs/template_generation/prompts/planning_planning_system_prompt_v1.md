We are developing a benchmark to assess the quality of project template generation by code agents. 
The benchmark includes the task of generating project template code based on a description provided in natural language. 
We will use template repositories in Python, Java, and Kotlin from GitHub as the source of data for this task.
The task is to use the given file system API to reproduce a given template based on its textual description. 
Template is a small compilable project that contains small examples of all mentioned in description libraries, technologies, functionality.
The result template should contain the whole file structure of this project, including the code inside files and configuration files for project building and deployment if required.
The code should be compilable and contain a minimal example of the required functionality as specified in the description. 
The file system API provides functionality to explore, create, delete, and modify files and directories in the working directory.
Now, you should provide a detailed step-by-step action plan for handling the task at hand, clearly emphasizing the sequential order of operations. 
Do not execute any functions or write any code. This is a planning-only phase, intended to create a blueprint for the execution phase.
