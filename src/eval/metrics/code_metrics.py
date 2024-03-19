import os
from typing import Any

import evaluate
from evaluate import load

from src.utils.project_utils import get_project_file_tree_as_dict


def calc_metrics(predictions: list[str], references: list[str], metrics: list[str]) -> dict[str, Any]:
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
            bleu = load("bleu")
            bleu_results = bleu.compute(predictions=predictions, references=references)
            result["bleu"] = bleu_results
        else:
            raise ValueError(f"Metrics {metric} is not supported")

    return result


def gen_golden_code_metric(gen_project_path: str, golden_project_path: str) -> dict[str, Any]:
    gen_dict = get_project_file_tree_as_dict(gen_project_path)
    golden_dict = get_project_file_tree_as_dict(golden_project_path)

    def concat_code(tree_dict: dict[str, str]) -> str:
        concatenated_code = ""
        for file, code in tree_dict.items():
            concatenated_code += code
        return concatenated_code

    predictions = [concat_code(gen_dict)]
    references = [concat_code(golden_dict)]

    return calc_metrics(predictions, references, ["chrf", "rouge", "bertscore", "bleu"])


def gen_golden_code_metric_by_files(gen_project_path: str, golden_project_path: str) -> dict[str, Any]:
    gen_dict = get_project_file_tree_as_dict(gen_project_path)
    golden_dict = get_project_file_tree_as_dict(golden_project_path)

    pass


def gen_golden_code_metric_by_code_entities(gen_project_path: str, golden_project_path: str) -> dict[str, Any]:
    gen_dict = get_project_file_tree_as_dict(gen_project_path)
    golden_dict = get_project_file_tree_as_dict(golden_project_path)

    pass


if __name__ == '__main__':
    base_path = '/Users/Maria.Tigina/PycharmProjects/agents-eval-data/'
    score = gen_golden_code_metric(
        os.path.join(base_path, 'gen_templates/JetBrains__intellij-platform-plugin-template_gpt-4-planning'),
        os.path.join(base_path, 'repos/JetBrains__intellij-platform-plugin-template')
    )
    print(score)
