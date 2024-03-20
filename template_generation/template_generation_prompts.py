def get_vanilla_user_prompt(full_name: str, project_description: str, project_language: str, project_additional_info: str) -> str:
    return f"""
    Generate template for project named {full_name.replace("/", "__")} 
    which mainly written on {project_language} 
    and aligns following description: {project_description}. {project_additional_info}."""


def get_user_prompt(full_name: str, project_description: str, project_language: str, project_additional_info: str) -> str:
    return f"""
    Template is a small compilable project that can be described in 1-5 sentences containing small examples 
    of all mentioned libraries, technologies, functionality.
    Generate template for project named {full_name.replace("/", "__")} 
    which mainly written on {project_language} 
    and aligns following description: {project_description}. {project_additional_info}.
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
