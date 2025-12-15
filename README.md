# Status: Archived 

No longer maintained 

# Agents and Planning Models Evaluation 🤖⛓

Toolkit for collecting datasets for Agents and Planning models and running evaluation pipelines.

## SetUp

```shell 
pip install requirements.txt
```

## Evaluation Pipeline Configuration

We use [Hydra](https://hydra.cc/docs/intro/) library for evaluation pipeline.
Each configuration is specified in `eval.yaml` format:

```yaml
# @package _global_
hydra:
  job:
    name: ${agent.name}_${agent.model_name}_[YOUR_ADDITIONAL_TOKEN_OR_NOTHING]
  run:
    dir:[YOUR_PATH_TO_OUTPUT_DIR]/${hydra:job.name}
  job_logging:
    root:
      handlers: [console, file]
defaults:
  - _self_
  - data_source: hf
  - env: code_engine
  - agent: planning
```

Where you can define the datasource, env and agent you want to evaluate.
We present several implementations for each defined in sub yamls:\

| field         | options                                                                                                                                                                                                                                                                                                                                                                |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `data_source` | [hf.yaml](configs/template_generation/data_source/hf.yaml)                                                                                                                                                                                                                                                                                                             |
| `env`         | [code_engine.yaml](configs/template_generation/env/code_engine.yaml) <br> [http.yaml](configs/template_generation/env/http.yaml) <br> [few_shot.yaml](configs/template_generation/env/few_shot.yaml)                                                                                                                                                                   |
| `agent`       | [few_shot.yaml](configs/template_generation/agent/few_shot.yaml) <br> [planning.yaml](configs/template_generation/agent/planning.yaml) <br> [vanilla.yaml](configs/template_generation/agent/vanilla.yaml) <br>  [reflexion.yaml](configs/template_generation/agent/reflexion.yaml) <br> [tree_of_thoughts.yaml](configs/template_generation/agent/tree_of_thoughts.yaml) <br> [adapt.yaml](configs/template_generation/agent/adapt.yaml) |


# Project Template Generation Evaluation

The challenge is to **generate project template** -- small compilable project that can be described in 1-5 sentences
containing small examples of all mentioned libraries/technologies/functionality.

### Dataset

Dataset of template-related repos collected GitHub are published
to [HuggingFace 🤗](https://huggingface.co/datasets/JetBrains-Research/template-generation). Details about the dataset
collection and source code is placed in [template_generation](src/template_generation) directory.

### Agent Models

To run the evaluation pipeline, please execute the following command in your console:
```commandline
python3 -m src/template_generation/run_eval --multirun agent=planning agent.model_name=gpt-3.5-turbo-1106,gpt-4-1106-preview
```

| Model             | Metrics            |
|-------------------|--------------------|
| ⚠️ Coming soon ⚠️ | ⚠️ Coming soon  ⚠️ |



