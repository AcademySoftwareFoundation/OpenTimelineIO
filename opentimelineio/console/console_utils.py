import ast
import sys

"""Utilities for OpenTimelineIO commandline modules."""


def arg_list_to_map(arg_list, label):
    """
    Convert an argument of the form -A foo=bar from the parsed result to a map.
    """

    argument_map = {}
    for pair in arg_list:
        if '=' in pair:
            key, val = pair.split('=', 1)  # only split on the 1st '='
            try:
                # Sometimes we need to pass a bool, int, list, etc.
                parsed_value = ast.literal_eval(val)
            except (ValueError, SyntaxError):
                # Fall back to a simple string
                parsed_value = val
            argument_map[key] = parsed_value
        else:
            print(
                "error: {} arguments must be in the form key=value"
                " got: {}".format(label, pair)
            )
            sys.exit(1)

    return argument_map
