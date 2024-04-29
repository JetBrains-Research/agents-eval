# Evaluation pipeline components

## Agents
All agents are driven by OpenAI models which support function calling and are written with usage of [LangChain](https://www.langchain.com/) library. 
The strategies implementation was provided by [JetBrains-Research/planning-lib](https://github.com/JetBrains-Research/planning-library).
* [openai_langchain_agent.py](./agents/openai_langchain_agent.py) - OpenAI LangChain agent without strategies
* [tree_of_thoughts_agent.py]() - OpenAI LangChain agent with [Tree-of-Thoughts](https://arxiv.org/abs/2307.16789) strategy
* [reflection_agent.py]() - OpenAI LangChain agent with [Reflexion](https://arxiv.org/abs/2303.11366) strategy
* [adapt_agent.py]() - OpenAI LangChain agent with [ADaPT](https://arxiv.org/abs/2311.05772) strategy

## Environments
Current evaluation pipeline communicates with environments using http protocol. 
Required endpoints for environment:

### Initialization Endpoint
URL: /init\
Method: POST\
Description: Initializes the environment with provided parameters.\
Request Body: Json with initialization parameters.
```json
{
  "param1": "value1",
  ...
}
```

### Tools Endpoint
URL: /tools\
Method: GET\
Description: Retrieves a list of available tools in the environment.\
Response: JSON array containing tool information in [OpenAI format](https://platform.openai.com/docs/guides/function-calling).

### Command Execution Endpoint
URL: /run_command\
Method: POST\
Description: Executes a command with specified parameters.\
Request Body: Json with command name and parameters.
```json
{
    "command_name": "command_name",
    "command_params": {
        "param1": "value1",
        "param2": "value2",
        ...
    }
}
```

### State Retrieval Endpoint
URL: /state\
Method: GET\
Description: Retrieves the current state of the environment.\
Response: Text response containing the current state.\

## Prompts
Execution prompts are delivered to evaluation pipeline from [BasePrompt](./prompts/base_prompt.py) inheritors and 
can be retrieved as `ChatPromptTemplate` by calling `execution_prompt`.
Currently supported prompts:
* [simple_prompt.py](./prompts/simple_prompt.py) - wraps user prompt into `ChatPromptTemplate`
* [planning_prompt.py](./prompts/planning_prompt.py) - builds plan by calling ChatGPT with user prompt and then forms execution prompt as combination of plan and user prompt.

## Data
For now data steaming from `HuggingFace` is provided as a default data source.