def get_user_prompt(full_name: str, project_description: str, project_language: str) -> str:
    return f"""
    Generate template for project named {full_name.replace("/", "__")} 
    which mainly written on {project_language} 
    and aligns following description: {project_description}. """


def get_gpt_description_system_prompt() -> str:
    return """Rewrite in 1-2 small sentences maximum template description and README heading asif user wants to generate template code using GPT.\n 
    Input:\n
    This scaffold project is written in Kotlin and will serve an example of implementing a Selenium test project with FluentLenium (Selenium3) and Gradle (with kotlin DSL). Everything is set up and tests can be added straight away. Used Testrunner is JUnit 5. Since Kotlin has an excellent Java interop it's perfectly fine to write your Tests in Java if you want, it will work out of the box. To execute the tests just browse to the path where the selenium-kotlin-example is located via terminal and type ./gradlew clean test or execute the tests in your IDE. The Project will use Chrome Browser in Headless mode by default / if no other browser is stated (see list of implemented browsers for more info on how to use them).\n
    Output:\n
    Kotlin template with gradle.kts and Selenium tests with FluentLenium and testrunner is JUnit 5"""
