def get_gen_golden_diff_metric_prompt() -> str:
    return """
    Estimate the difference between two projects. 
    Return 1 if they are the same in terms of functionality or 0 if the essential part is missed.
    """


def get_gen_vanilla_golden_diff_metric_prompt() -> str:
    return """
    Your are given two diffs. 
    Return 1 if the first diff is smaller and contains small difference in terms of functionality or 1 if the second is second does.
    """
