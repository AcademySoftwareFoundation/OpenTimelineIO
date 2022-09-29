# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Reusable utilities for tests."""

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
