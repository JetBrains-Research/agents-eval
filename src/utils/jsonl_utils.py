import json


def append_to_jsonl(repo_data: list[dict], jsonl_path: str) -> None:
    with open(jsonl_path, "a+") as f_data_output:
        for item in repo_data:
            f_data_output.write(json.dumps(item) + "\n")


def read_jsonl(jsonl_path: str) -> list[dict]:
    with open(jsonl_path, "r") as f_data_input:
        data = [json.loads(line) for line in f_data_input]
    return data
