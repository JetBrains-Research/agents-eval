import os
from typing import Any

import evaluate
import numpy as np
import torch
from evaluate import load
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from src.utils.project_utils import get_project_file_tree_as_dict


def calc_metrics(predictions: list[str], references: list[str], metrics: list[str]) \
        -> dict[str, Any]:
    result = {}
    for metric in metrics:
        if metric == "chrf":
            chrf = evaluate.load("chrf")
            chrf_results = chrf.compute(predictions=predictions, references=references)
            result["chrf"] = chrf_results
        elif metric == "rouge":
            rouge = evaluate.load("rouge")
            rouge_results = rouge.compute(predictions=predictions, references=references)
            result["rouge"] = rouge_results
        elif metric == "bertscore":
            bertscore = load("bertscore")
            bertscore_results = bertscore.compute(predictions=predictions, references=references, lang='en')
            result["bertscore"] = bertscore_results
        elif metric == "bleu":
            # "k4black/codebleu" for code
            bleu = load("bleu")
            bleu_results = bleu.compute(predictions=predictions, references=references)
            result["bleu"] = bleu_results
        elif metric == "gte":
            model = SentenceTransformer('thenlper/gte-large')
            embeddings = model.encode(predictions + references)
            result["gte"] = {"gte": cos_sim(embeddings[:len(predictions)], embeddings[len(predictions):])}
        else:
            raise ValueError(f"Metrics {metric} is not supported")

    return result


def gen_golden_content_metric(gen_project_path: str, golden_project_path: str) -> dict[str, Any]:
    gen_dict = get_project_file_tree_as_dict(gen_project_path)
    golden_dict = get_project_file_tree_as_dict(golden_project_path)

    def concat_code(tree_dict: dict[str, str]) -> str:
        concatenated_code = ""
        for file, code in tree_dict.items():
            concatenated_code += code
        return concatenated_code

    predictions = concat_code(gen_dict)
    references = concat_code(golden_dict)

    metrics = calc_metrics([predictions], [references], ["bleu", "rouge", "chrf", "bertscore", "gte"])

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
    metrics = calc_metrics(gen_contents, gen_files, [metric])[metric][metric]
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
