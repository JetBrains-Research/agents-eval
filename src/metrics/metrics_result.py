import json
import re
from typing import Any


def parse_json_response(response: str) -> dict[str, Any]:
    pattern = r'```json\s*([\s\S]*?)\s*```'
    match = re.search(pattern, response, re.MULTILINE)
    if match:
        response_dict = json.loads(match.group(1))
    else:
        raise Exception("No matching json")

    return response_dict
