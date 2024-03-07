def get_diff_metrics_prompt() -> str:
    return """
    Estimate the difference between two projects. 
    Return 1 if they are the same in terms of functionality or 0 if the essential part is missed.
    """