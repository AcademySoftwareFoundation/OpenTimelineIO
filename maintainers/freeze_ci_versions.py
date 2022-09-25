#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """Freeze and unfreeze image versions for CI, part of the release
process.

"""

import argparse
import os
import sys
import re
import urllib.request

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "Error: Could not import 'yaml', might need to `pip install pyyaml`\n"
    )
    raise

CI_WORKFLOW_FP = ".github/workflows/python-package.yml"
GITHUB_README_URL = "https://raw.githubusercontent.com/actions/runner-images/main/README.md"
PLATFORMS = ["ubuntu", "macos", "windows"]

def _parsed_args():
    parser = argparse.ArgumentParser(
        description='Fetch a list of contributors for a given GitHub repo.'
    )
    return parser.parse_args()


def main():
    _ = _parsed_args()

    request = urllib.request.Request(GITHUB_README_URL)
    response = urllib.request.urlopen(request).read().decode('utf-8')

    lines = response.split("\n")
    plat_map = {}
    for plat in PLATFORMS:
        plat_latest = plat + "-latest"
        for ln in lines:
            if plat_latest not in ln:
                continue
            plat_map[plat] = re.match(".*("+plat+"-.*)`.*", ln).groups(0)


def freeze_ci(plat_map):
    modified = False
    with open(CI_WORKFLOW_FP, 'r') as fi:
        output_content = fi.read()

    for plat in plat_map:
        plat_latest = plat + "-latest"
        if plat_latest not in output_content:
            print("Platform {} appears to already be frozen.".format(plat))
            continue

        output_content.replace(plat_latest, plat_map[plat])
        modified = True
        print("Platform {} frozen to version: {}".format(plat, plat_map[plat]))

    if modified:
        with open(CI_WORKFLOW_FP, 'w') as fo:
            fo.write(output_content)
        return True

    return False

if __name__ == "__main__":
    main()
