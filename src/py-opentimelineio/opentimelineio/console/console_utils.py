# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import ast

from .. import (
    media_linker,
)

"""Utilities for OpenTimelineIO commandline modules."""


def arg_list_to_map(arg_list, label):
    """
    Convert an argument of the form -A foo=bar from the parsed result to a map.
    """

    argument_map = {}
    for pair in arg_list:
        if '=' not in pair:
            raise ValueError(
                "error: {} arguments must be in the form key=value"
                " got: {}".format(label, pair)
            )

        key, val = pair.split('=', 1)  # only split on the 1st '='
        try:
            # Sometimes we need to pass a bool, int, list, etc.
            parsed_value = ast.literal_eval(val)
        except (ValueError, SyntaxError):
            # Fall back to a simple string
            parsed_value = val
        argument_map[key] = parsed_value

    return argument_map


def media_linker_name(ml_name_arg):
    """
    Parse commandline arguments for the media linker, which can be not set
    (fall back to default), "" or "none" (don't link media) or the name of a
    media linker to use.
    """
    if ml_name_arg.lower() == 'default':
        media_linker_name = media_linker.MediaLinkingPolicy.ForceDefaultLinker
    elif ml_name_arg.lower() in ['none', '']:
        media_linker_name = media_linker.MediaLinkingPolicy.DoNotLinkMedia
    else:
        media_linker_name = ml_name_arg

    return media_linker_name
