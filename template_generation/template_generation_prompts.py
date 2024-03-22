def get_vanilla_user_prompt(full_name: str, project_description: str, project_language: str,
                            gpt_description: str) -> str:
    return f"""
    Generate template for project named {full_name.replace("/", "__")} 
    which mainly written on {project_language} 
    and aligns following description: {project_description}. {gpt_description}."""


def get_user_prompt(full_name: str, project_description: str, project_language: str,
                    gpt_description: str) -> str:
    return f"""
    Template is a small compilable project that contains small examples of all mentioned in description 
    libraries, technologies, functionality.
    Generate template for project named {full_name.replace("/", "__")} 
    which mainly written on {project_language} 
    and aligns following description: {project_description}. {gpt_description}.
    Provide files and directory structure (tree) as well as program files contents with all required functionality.
    Take into account only code producing steps.
    Project content root directory is already created, use relative paths from it."""


def get_planning_system_prompt() -> str:
    return """
    Devise a detailed step-by-step action plan for handling the task at hand, clearly emphasizing the sequential order of operations. Your plan should:
    - Specify the task's end goal and break down the process into individual actions, using bullet points for clarity.
    - Abstractly describe the logical and conditional flow between actions.
    - Do not execute any functions or write any code. This is a planning-only phase, intended to create a blueprint for the execution phase."""


def get_execution_system_prompt() -> str:
    return """
    Execute the following detailed action plan methodically. For each step of the plan:
    - Call the appropriate function with the required arguments, corresponding directly to the outlined plan's next action.
    - Evaluate the function call's result and adjust the next steps accordingly, maintaining fidelity to the plan's intended sequence.
    - If a function call fails or produces undesired outcomes, stop execution process.
    - Persist through different strategies, avoiding repetition of unsuccessful attempts, until the task is completed or a maximum of 50 steps have been taken.
    - Document solely the function calls and their outcomes. Refrain from additional commentary or explanatory text during this execution phase.
    Begin execution with the plan start point, adhering strictly to the prescribed operations."""


def get_gpt_description_system_prompt() -> str:
    return """Rewrite in 1-2 small sentences maximum template description and README heading asif user wants to generate template code using GPT.\n 
    Input:\n
    This scaffold project is written in Kotlin and will serve an example of implementing a Selenium test project with FluentLenium (Selenium3) and Gradle (with kotlin DSL). Everything is set up and tests can be added straight away. Used Testrunner is JUnit 5. Since Kotlin has an excellent Java interop it's perfectly fine to write your Tests in Java if you want, it will work out of the box. To execute the tests just browse to the path where the selenium-kotlin-example is located via terminal and type ./gradlew clean test or execute the tests in your IDE. The Project will use Chrome Browser in Headless mode by default / if no other browser is stated (see list of implemented browsers for more info on how to use them).\n
    Output:\n
    Kotlin template with gradle.kts and Selenium tests with FluentLenium and testrunner is JUnit 5"""
