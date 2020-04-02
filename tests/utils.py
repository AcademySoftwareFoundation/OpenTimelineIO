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

"""Reusable utilities for tests."""
from __future__ import absolute_import

# import built-in modules
import os
import tempfile

# import local modules
import opentimelineio as otio
from tests import baseline_reader


MANIFEST_PATH = "adapter_plugin_manifest.plugin_manifest"


def create_manifest():
    """Create a temporary manifest."""
    full_baseline = baseline_reader.json_baseline_as_string(MANIFEST_PATH)

    temp_dir = tempfile.mkdtemp(prefix='test_otio_manifest')
    man_path = os.path.join(temp_dir, 'manifest')
    with open(man_path, 'w') as fo:
        fo.write(full_baseline)
    man = otio.plugins.manifest_from_file(man_path)
    man._update_plugin_source(baseline_reader.path_to_baseline(MANIFEST_PATH))
    return man


def remove_manifest(manifest):
    """Remove the manifest source files."""
    for file_path in manifest.source_files:
        # don't accidentally blow away python
        if not file_path.endswith('.py'):
            os.remove(file_path)
