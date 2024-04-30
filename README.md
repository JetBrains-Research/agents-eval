# Agents and Planning Models Evaluation 🤖

Toolkit for collecting datasets for Agents and Planning models and running evaluation pipelines.

## SetUp

```shell 
pip install requirements.txt
```

# Evaluation Pipeline Components

## Agents
One group of agents is based on raw LangChain library and extends [LangchainAgent](src/eval/agents/langchain_agent.py)
All agents are driven by OpenAI models which support function calling and are written with usage of [LangChain](https://www.langchain.com/) library. 
The strategies implementation was provided by [JetBrains-Research/planning-lib](https://github.com/JetBrains-Research/planning-library).
* [openai_langchain_agent.py](src/eval/agents/openai_langchain_agent.py) - OpenAI LangChain agent without strategies
* [tree_of_thoughts_agent.py](src/eval/agents/openai_langchain_agent.py) - OpenAI LangChain agent with [Tree-of-Thoughts](https://arxiv.org/abs/2307.16789) strategy
* [reflection_agent.py](src/eval/agents/openai_langchain_agent.py) - OpenAI LangChain agent with [Reflexion](https://arxiv.org/abs/2303.11366) strategy
* [adapt_agent.py](src/eval/agents/openai_langchain_agent.py) - OpenAI LangChain agent with [ADaPT](https://arxiv.org/abs/2311.05772) strategy

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
```json lines
[{
    "type": "function",
    "function": {
        "name": "command_name",
        "description": "Command description.",
        "parameters": {
            "type": "object",
            "properties": {
                "arg1": {
                    "type": "atg_type",
                    "description": "Argument description",
                },
                ...
            },
            "required": ["arg1"],
        },
    }
},
...
]
```

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
**IMPORTANT!** Some strategies require command with name `reset` and empty parameters which reset environments to initial state.

### State Retrieval Endpoint
URL: /state\
Method: GET\
Description: Retrieves the current state of the environment.\
Response: Serializable to string response containing the current state of the environment.

## Prompts
Execution prompts are delivered to evaluation pipeline from [BasePrompt](./prompts/base_prompt.py) inheritors and 
can be retrieved as `ChatPromptTemplate` by calling `execution_prompt`.
Currently supported prompts for `OpenAILangchainAgent`:
* [simple_prompt.py](./prompts/simple_prompt.py) - wraps user prompt into `ChatPromptTemplate`
* [planning_prompt.py](./prompts/planning_prompt.py) - builds plan by calling ChatGPT with user prompt and then forms execution prompt as combination of plan and user prompt.

Moreover, each plugging strategy may have some specific prompts, for each strategy relatively we provide:
* [tree_of_thoughts_prompt.py](./prompts/simple_prompt.py) - prompt for `TheeOfThouhgtsAgent` which provide `thought_evaluator_message` and `thought_generator_message`
* [reflection_prompt.py](./prompts/planning_prompt.py) - prompt for `ReflectionAgent`

## Data
For now data steaming from `HuggingFace` is provided as a default data source.


## Project Template Generation
The challenge is to **generate project template** -- small compilable project that can be described in 1-5 sentences 
containing small examples of all mentioned libraries/technologies/functionality.

### Dataset
Project from [GitHub](https://github.com/) written in `Java` and `Kotlin` programming languages 
with 10+ stars and 10+ code lines, permissive licences, without forks (collected by https://seart-ghs.si.usi.ch) 
filtered by `is_template=True` or template-related keywords words presence in description.
From `Java` and `Kotlin` the `Android` projects were identified by `android` token in description or tags and 
moved to separate category.

Collected data is available in [HuggingFace 🤗](https://huggingface.co/datasets/JetBrains-Research/template-generation), data was manually labeled to select test subset in [Google Sheets](https://docs.google.com/spreadsheets/d/1tQLWBBlfDA9l72wpXT7DbqkAt9FWUo0bt9dDX1X9AU8/edit#gid=907232403)

### Agent Models
OpenAI GTP-4 with function calling, prompted with file system api (create/delete/list/... files)
