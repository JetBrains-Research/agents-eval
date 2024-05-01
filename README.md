# Agents and Planning Models Evaluation 🤖⛓

Toolkit for collecting datasets for Agents and Planning models and running evaluation pipelines.

## SetUp

```shell 
pip install requirements.txt
```
## Evaluation Pipeline Configuration
We use [Hydra](https://hydra.cc/docs/intro/) library for evaluation pipeline. 
Each configuration is specified in `yaml` format:
```json lines
hydra:
  job:
    name: planning_${agent.model_name}
  run:
    dir: ./${hydra:job.name}
  job_logging:
    root:
      handlers: [console, file]
data_source:
  _target_: src.eval.data_sources.hf_data_source.HFDataSource
  cache_dir: null
  hub_name: JetBrains-Research/template-generation
  configs:
    - java
    - kt
  split: test
env:
  _target_: src.eval.envs.http_env.HttpEnv
  host: '127.0.0.1'
  port: '5050'
agent:
  _target_: src.eval.agents.openai_langchain_agent.OpenAILangchainAgent
  model_name: gpt-3.5-turbo-1106
  temperature: 0
  model_kwargs:
    seed: 76097149
  prompt:
    _target_: src.eval.prompts.planning_prompt.PlanningPrompt
    model_name: gpt-3.5-turbo-1106
    temperature: 0
    model_kwargs:
      seed: 76097149
    planning_system_prompt: |
      Devise a detailed step-by-step action plan for handling the task at hand, clearly emphasizing the sequential order of operations. 
      Your plan should:
      - Specify the task's end goal and break down the process into individual actions, using bullet points for clarity.
      - Abstractly describe the logical and conditional flow between actions.
      - Do not execute any functions or write any code. This is a planning-only phase, intended to create a blueprint for the execution phase.
    execution_system_prompt: |
      Execute the following detailed action plan methodically. 
      For each step of the plan:
      - Call the appropriate function with the required arguments, corresponding directly to the outlined plan's next action.
      - Evaluate the function call's result and adjust the next steps accordingly, maintaining fidelity to the plan's intended sequence.
      - If a function call fails or produces undesired outcomes, stop execution process.
      - Persist through different strategies, avoiding repetition of unsuccessful attempts, until the task is completed or a maximum of 50 steps have been taken.
      - Document solely the function calls and their outcomes. Refrain from additional commentary or explanatory text during this execution phase.
      Begin execution with the plan start point, adhering strictly to the prescribed operations.
```


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
