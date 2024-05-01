from typing import Any

import evaluate
from evaluate import load
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


def calc_base_metrics(predictions: list[str], references: list[str], metrics: list[str]) -> dict[str, Any]:
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
            # TODO: Use "k4black/codebleu" for code
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
