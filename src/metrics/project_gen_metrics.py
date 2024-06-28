from typing import Any

import numpy as np
import torch

from src.metrics.base_metrics import calc_base_metrics
from src.utils.project_utils import get_project_file_tree_as_dict


def gen_golden_content_metrics(gen_project_path: str, golden_project_path: str) -> dict[str, Any]:
    gen_dict = get_project_file_tree_as_dict(gen_project_path)
    golden_dict = get_project_file_tree_as_dict(golden_project_path)

    def concat_code(tree_dict: dict[str, str]) -> str:
        concatenated_code = ""
        for file, code in tree_dict.items():
            concatenated_code += code
        return concatenated_code

    predictions = concat_code(gen_dict)
    references = concat_code(golden_dict)

    if len(predictions) == 0 or len(references) == 0:
        return {
            "bleu": None,
            "rouge1": None,
            "rouge2": None,
            "rougeL": None,
            "rougeLsum": None,
            "chrf": None,
            "bertscoref1": None,
            "gte": None,
        }

    metrics = calc_base_metrics([predictions], [references], ["bleu", "rouge", "chrf", "bertscore", "gte"])
    return {
        "bleu": metrics["bleu"]["bleu"],
        "rouge1": metrics["rouge"]["rouge1"],
        "rouge2": metrics["rouge"]["rouge2"],
        "rougeL": metrics["rouge"]["rougeL"],
        "rougeLsum": metrics["rouge"]["rougeLsum"],
        "chrf": metrics["chrf"]["score"],
        "bertscoref1": metrics["bertscore"]["f1"][0],
        "gte": metrics["gte"]["gte"].item(),
    }


def gen_golden_content_metric_by_files(gen_project_path: str, golden_project_path: str, metrics: str = "gte") \
        -> dict[str, Any]:
    gen_dict = get_project_file_tree_as_dict(gen_project_path)
    golden_dict = get_project_file_tree_as_dict(golden_project_path)

    golden_contents = [file + content for file, content in golden_dict.items()]
    golden_files = [file for file, content in golden_dict.items()]
    golden_files_count = len(golden_contents)

    gen_contents = [file + content for file, content in gen_dict.items()]
    gen_files = [file for file, content in gen_dict.items()]

    metric = 'gte'
    metrics = calc_base_metrics(gen_contents, golden_contents, [metric])[metric][metric]
    best_match = torch.argmax(metrics, dim=1).tolist()

    best_metrics = []
    golden_selected_files = set()
    for i, best_index in enumerate(best_match):
        print(f'File {gen_files[i]} match file {golden_files[best_index]}')
        golden_selected_files.add(best_index)
        best_metrics.append(metrics[i][best_index].item())

    return {
        f'avg_{metric}_match': np.average(best_metrics),
        'uncovered_golden': (golden_files_count - len(golden_selected_files)) / golden_files_count
    }


def get_closest_project_index(description: str, other_descriptions: list[str]):
    metric = 'gte'
    metrics = \
    calc_base_metrics([description], [d if d is not None else "" for d in other_descriptions], [metric])[metric][
        metric]
    best_match = torch.argmax(metrics, dim=1).tolist()[0]

    return best_match
