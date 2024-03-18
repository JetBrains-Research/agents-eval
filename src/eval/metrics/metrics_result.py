import json
import re


def parse_json_result_comment_response(response: str) -> tuple[str, str]:
    pattern = r'```json\s*([\s\S]*?)\s*```'
    match = re.search(pattern, response, re.MULTILINE)
    if match:
        response_dict = json.loads(match.group(1))
        result = response_dict["result"]
        comment = response_dict["comment"]
    else:
        raise Exception("No matching json")

    return result, comment
