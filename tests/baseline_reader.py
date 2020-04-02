#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

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
    with open(fpath, 'r') as fo:
        return json_from_string(fo.read())


def path_to_baseline_directory():
    return os.path.join(MODPATH, "baselines")


def path_to_baseline(name):
    return os.path.join(path_to_baseline_directory(), "{0}.json".format(name))


def json_baseline(name):
    return json_from_file_as_string(path_to_baseline(name))


def json_baseline_as_string(name):
    return json.dumps(json_baseline(name))
