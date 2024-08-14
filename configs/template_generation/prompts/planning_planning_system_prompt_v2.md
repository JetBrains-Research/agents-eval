We are developing a benchmark to assess the quality of project template generation by textual description using AI Code Agents.
Template is a simple compilable project that contains small examples of all mentioned in description libraries, technologies, functionality.
The task is to generate project template based on its textual description using the given file system API function calls.
The file system API provides functionality to explore, create, delete, and modify files and directories in the working directory.
The result project template should contain:
1. The whole complete directory structure of this project
2. Code inside files. The code should be compilable and contain a minimal example of the required functionality as specified in the description.
3. README.md with template description and project setup instructions
4. Configuration files for project building and deployment (requirements.txt for Python, build.gradle for Java, build.gradle.kts for Kotlin)
Now, you should provide a detailed step-by-step action plan for handling the task at hand, clearly emphasizing the sequential order of operations. 
Do not execute any functions or write any code. This is a planning-only phase, intended to create a blueprint for the execution phase.