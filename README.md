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
    dir:[YOUR_PATH_TO_OUTPUT_DIR]/${hydra:job.name}
  job_logging:
    root:
      handlers: [ console, file ]
defaults:
  - _self_
  - data_source: hf
  - env: http
  - agent: planning
```

Where you can define the datasource, env and agent you want to evaluate.
We present several implementations for each defined in sub yamls:\

| field         | options                                                                                                                                                                                                                                                                                                                                                          |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `data_source` | [hf.yaml](configs/template_generation/data_source/hf.yaml)                                                                                                                                                                                                                                                                                                       |
| `env`         | [http.yaml](configs/template_generation/env/http.yaml)                                                                                                                                                                                                                                                                                                           |
| `agent`       | [vanilla.yaml](configs/template_generation/agent/vanilla.yaml)<br> [planning.yaml](configs/template_generation/agent/planning.yaml) <br> [reflexion.yaml](configs/template_generation/agent/reflexion.yaml)<br> [tree_of_thoughts.yaml](configs/template_generation/agent/tree_of_thoughts.yaml) <br> [adapt.yaml](configs/template_generation/agent/adapt.yaml) |

# Project Template Generation Evaluation

The challenge is to **generate project template** -- small compilable project that can be described in 1-5 sentences
containing small examples of all mentioned libraries/technologies/functionality.

### Dataset

Dataset of template-related repos collected GitHub are published
to [HuggingFace 🤗](https://huggingface.co/datasets/JetBrains-Research/template-generation). Detains about dataset
collection and source code is placed in [template_generation](src/template_generation) directory

### Agent Models

| Model             | Metrics          |
|-------------------|------------------|
| ⚠️ Coming soon ⚠️ | ⚠️ Coming soon ⚠ |



