# Agents and Planning Models Evaluation 🤖⛓

Toolkit for collecting datasets for Agents and Planning models and running evaluation pipelines.

## SetUp

```shell 
pip install requirements.txt
```
## Evaluation Pipeline Configuration
We use [Hydra](https://hydra.cc/docs/intro/) library for evaluation pipeline. 
Each configuration is specified in `config.yaml` format:
```yaml
# @package _global_
hydra:
  job:
    name: planning_${agent.model_name}
  run:
    dir: /Users/Maria.Tigina/PycharmProjects/agents-eval-data/template_generation/${hydra:job.name}
  job_logging:
    root:
      handlers: [console, file]
defaults:
  - _self_
  - data_source: hf
  - env: http
  - agent: planning
```
Where you can define the datasource, env and agent you want to evaluate. 
We present several implementations for each defined in sub yamls:\
data_source:
* [hf.yaml]()

env: 
* [http.yaml]()

agent: 
* [planning.yaml]() 
* ...


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
