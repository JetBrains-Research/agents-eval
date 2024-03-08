import os

import datasets
import huggingface_hub
from datasets import Dataset

HUGGINGFACE_REPO = 'JetBrains-Research/template-generation'
CATEGORIES = ['java', 'kt']
SPLITS = ['dev', 'test', 'train']

FEATURES = {
    'repos_paths': datasets.Features(
        {
            category: [datasets.Value("string")] for category in CATEGORIES
        }
    ),
    'template_generation_data': datasets.Features(
        {
            "id": datasets.Value("int64"),
            "repo_owner": datasets.Value("string"),
            "repo_name": datasets.Value("string"),
            "html_url": datasets.Value("string"),
            "is_template": datasets.Value("bool"),
            "description": datasets.Value("string"),
            "template_keywords": datasets.Value("string"),
            "license": datasets.Value("string"),
            'topics': datasets.Value("string"),
            'size': datasets.Value("int64"),
        }
    )
}


def load_data(category: str, split: str) -> Dataset:
    huggingface_hub.login(token=os.environ['HUGGINGFACE_TOKEN'])

    return datasets.load_dataset(
        HUGGINGFACE_REPO, category,
        split=split,
        ignore_verifications=True,
    )
