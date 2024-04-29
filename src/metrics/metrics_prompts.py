def get_gen_golden_diff_metric_prompt() -> str:
    return """
    Estimate the difference between two projects. 
    Return 1 if they are the same in terms of functionality or 0 if the essential part is missed.
    """


def get_gen_vanilla_golden_diff_metric_prompt() -> str:
    return """
    Your are given two diffs with same base. 
    Return 1 if the first diff is smaller and contains small difference in terms of functionality or 1 if the second is second does.
    """


def get_gen_vanilla_golden_tree_metric_prompt() -> str:
    return """
    Compare the structure of two project file trees and 
    determine which one resembles the golden file tree example more closely. 
    Return only json with field "result" equals to 1 if the first tree is closer to the golden file tree example, 
    and 2 if the second one is closer, and field "comment" which describes the chosen result.
    """
