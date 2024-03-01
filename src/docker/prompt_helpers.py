import io
import sys
from typing import Union


class ColorCodes:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def tee(*values, end: str = "", color: Union[ColorCodes, str] = None, file=sys.stdout, flush=False) -> str:
    """Prints the values to a stream, or to sys.stdout by default
    and returns the string that was printed.

    Optional arguments except `end` affect only the output stream and not the return value.
    `end` is always appended to both the stream and the return value.

    :param values: The values to print. Follows the same syntax as the print function.
    :param end: The string to append to the end of the string.
    :param color: The color to print the string in.
    :param file: The file to print the string to.
    :param flush: Whether to flush the file after printing.

    :return: The string that was printed.
    """
    output_stream = io.StringIO()
    print(*values, end=end, file=output_stream, flush=True)
    output = output_stream.getvalue()

    output_to_print = output if color is None else f"{color}{output}{ColorCodes.ENDC}"
    print(output_to_print, end=end, file=file, flush=flush)

    return output
