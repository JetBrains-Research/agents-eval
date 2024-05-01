# Evaluation Pipeline Components

## Agents

One group of agents is based on raw  [LangChain](https://www.langchain.com/) library and
extends [LangchainAgent](agents/langchain_agent.py):

* [openai_langchain_agent.py](agents/openai_langchain_agent.py) - OpenAI LangChain agent without strategies

Another group uses [JetBrains-Research/planning-lib](https://github.com/JetBrains-Research/planning-library) - extension
of LangChain with several planning strategies. Such agents
extend [LangchainStrategicAgent](agents/langchain_strategic_agent.py):
All agents are driven by OpenAI models which support function calling and are written with usage
of [LangChain](https://www.langchain.com/) library.

* [tree_of_thoughts_agent.py](agents/tree_of_thoughts_agent.py) - OpenAI LangChain agent
  with [Tree-of-Thoughts](https://arxiv.org/abs/2307.16789) strategy
* [reflexion_agent.py](agents/reflexion_agent.py) - OpenAI LangChain agent
  with [Reflexion](https://arxiv.org/abs/2303.11366) strategy
* [adapt_agent.py](agents/adapt_agent.py) - OpenAI LangChain agent with [ADaPT](https://arxiv.org/abs/2311.05772)
  strategy

## Environments

Current evaluation pipeline communicates with environments using http protocol implemented
in [HttpEnv](envs/http_env.py).
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
Response: JSON array containing tool information
in [OpenAI format](https://platform.openai.com/docs/guides/function-calling).

```json lines
[
  {
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
        "required": [
          "arg1"
        ],
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

**IMPORTANT!** Some strategies require command with name `reset` and empty parameters which reset environments to
initial state.

### State Retrieval Endpoint

URL: /state\
Method: GET\
Description: Retrieves the current state of the environment.\
Response: Serializable to string response containing the current state of the environment.

## Prompts

Execution prompts are delivered to evaluation pipeline from [BasePrompt](./prompts/base_prompt.py) inheritors and
can be retrieved as `ChatPromptTemplate` by calling `execution_prompt`.
Currently supported prompts for `OpenAILangchainAgent`:

* [simple_prompt.py](prompts/simple_prompt.py) - wraps user prompt into `ChatPromptTemplate`
* [planning_prompt.py](prompts/planning_prompt.py) - builds plan by calling ChatGPT with user prompt and then forms
  execution prompt as combination of plan and user prompt.

Moreover, each strategy may have some specific prompts, for each strategy relatively we provide:

* [tree_of_thoughts_prompt.py](prompts/tree_of_thoughts_prompt.py) - prompt for `TheeOfThouhgtsAgent` which
  provide `thought_evaluator_prompt` and `thought_generator_prompt`
* [reflexion_prompt.py](prompts/reflexion_prompt.py) - prompt for `ReflectionAgent` which
  provide `action_prompt`, `evaluator_prompt` and `self_reflexion_prompt`
* [adapt_prompt.py](prompts/adapt_prompt.py) - prompt for `ADaPTAgent` which
  provide `executor_prompt`, `agent_planner_prompt` or `simple_planner_prompt`

## Data Sources

[HfDataSource](data_sources/hf_data_source.py) provides data steaming from `HuggingFace`.
But also it can be extended by custom way of data streaming by
overriding [BaseDataSource](data_sources/base_data_source.py)

