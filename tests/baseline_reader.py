# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utilities for reading baseline json."""

import os
import json

MODPATH = os.path.dirname(__file__)


def test_hook(dct):
    if "FROM_TEST_FILE" in dct:
        # fetch the baseline
        result = json_from_file_as_string(
            os.path.join(
                MODPATH,
                "baselines",
                str(dct["FROM_TEST_FILE"])
            )
        )

        # allow you to overlay values onto the baseline in the test, if they
        # store non-default for the baseline values.
        del dct["FROM_TEST_FILE"]
        result.update(dct)
        return result

    return dct


def json_from_string(jsonstr):
    return json.loads(jsonstr, object_hook=test_hook)


def json_from_file_as_string(fpath):
    with open(fpath) as fo:
        return json_from_string(fo.read())


def path_to_baseline_directory():
    return os.path.join(MODPATH, "baselines")


def path_to_baseline(name):
    return os.path.join(path_to_baseline_directory(), f"{name}.json")


def json_baseline(name):
    return json_from_file_as_string(path_to_baseline(name))


def json_baseline_as_string(name):
    return json.dumps(json_baseline(name))
