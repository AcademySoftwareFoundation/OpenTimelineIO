#!/usr/bin/env python
""" Utilities for reading baseline json. """

import os
import json

MODPATH = os.path.dirname(__file__)


def test_hook(dct):
    if "FROM_TEST_FILE" in dct:
        return json_from_file_as_string(
            os.path.join(
                MODPATH,
                "baseline",
                str(dct["FROM_TEST_FILE"])
            )
        )

    return dct


def json_from_string(jsonstr):
    return json.loads(jsonstr, object_hook=test_hook)


def json_from_file_as_string(fpath):
    with open(fpath, 'r') as fo:
        return json_from_string(fo.read())


def path_to_baseline(name):
    return os.path.join(MODPATH, "baseline", "{0}.json".format(name))


def json_baseline(name):
    return json_from_file_as_string(path_to_baseline(name))


def json_baseline_as_string(name):
    return json.dumps(json_baseline(name))
