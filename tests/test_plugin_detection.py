#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest
import os
from pathlib import Path
import sys

from unittest import mock

from importlib import reload as import_reload

import importlib.metadata as metadata

import opentimelineio as otio
from tests import baseline_reader


class TestSetuptoolsPlugin(unittest.TestCase):
    def setUp(self):
        # Get the location of the mock plugin module metadata
        mock_module_path = os.path.join(
            os.path.normpath(baseline_reader.path_to_baseline_directory()),
            'plugin_module',
        )
        self.mock_module_manifest_path = Path(
            mock_module_path,
            "otio_jsonplugin",
            "plugin_manifest.json"
        ).absolute().as_posix()

        self.override_adapter_manifest_path = Path(
            mock_module_path,
            "otio_override_adapter",
            "plugin_manifest.json"
        ).absolute().as_posix()

        # Create a WorkingSet as if the module were installed
        entries = [mock_module_path] + sys.path

        self.original_sysmodule_keys = set(sys.modules.keys())

        self.sys_patch = mock.patch('sys.path', entries)
        self.sys_patch.start()

    def tearDown(self):
        self.sys_patch.stop()

        # Remove any modules added under test.  We cannot replace sys.modules with
        # a copy from setUp. For more, see: https://bugs.python.org/msg188914
        for key in set(sys.modules.keys()) ^ self.original_sysmodule_keys:
            sys.modules.pop(key)

    def test_detect_plugin(self):
        """This manifest uses the plugin_manifest function"""

        # Create a manifest and ensure it detected the mock adapter and linker
        man = otio.plugins.manifest.load_manifest()

        # Make sure the adapter is included in the adapter list
        adapter_names = [adapter.name for adapter in man.adapters]
        self.assertIn('mock_adapter', adapter_names)

        # Make sure the linker is included in the linker list
        linker_names = [linker.name for linker in man.media_linkers]
        self.assertIn('mock_linker', linker_names)

        # Make sure adapters and linkers landed in the proper place
        for adapter in man.adapters:
            self.assertIsInstance(adapter, otio.adapters.Adapter)

        for linker in man.media_linkers:
            self.assertIsInstance(linker, otio.media_linker.MediaLinker)

    def test_override_adapter(self):

        # Test that entrypoint plugins load before builtin
        man = otio.plugins.manifest.load_manifest()

        # The override_adapter creates another otiod adapter
        adapters = [adapter for adapter in man.adapters
                    if adapter.name == "otiod"]

        # More then one otiod adapter should exist.
        self.assertTrue(len(adapters) > 1)

        # Override adapter should be the first adapter found
        manifest = adapters[0].plugin_info_map().get('from manifest', None)
        self.assertEqual(manifest, self.override_adapter_manifest_path)

        self.assertTrue(
            any(
                True for p in man.source_files
                if self.override_adapter_manifest_path in p
            )
        )

    def test_entrypoints_disabled(self):
        os.environ["OTIO_DISABLE_ENTRYPOINTS_PLUGINS"] = "1"
        import_reload(otio.plugins.manifest)

        # detection of the environment variable happens on import, force a
        # reload to ensure that it is triggered
        with self.assertRaises(AssertionError):
            self.test_detect_plugin()

        # override adapter should not be loaded either
        with self.assertRaises(AssertionError):
            self.test_override_adapter()

        # remove the environment variable and reload again for usage in the
        # other tests
        del os.environ["OTIO_DISABLE_ENTRYPOINTS_PLUGINS"]
        import_reload(otio.plugins.manifest)

    def test_detect_plugin_json_manifest(self):
        # Test detecting a plugin that rather than exposing the plugin_manifest
        # function, just simply has a plugin_manifest.json provided at the
        # package top level.
        man = otio.plugins.manifest.load_manifest()

        # Make sure the adapter is included in the adapter list
        adapter_names = [adapter.name for adapter in man.adapters]
        self.assertIn('mock_adapter_json', adapter_names)

        # Make sure the linker is included in the linker list
        linker_names = [linker.name for linker in man.media_linkers]
        self.assertIn('mock_linker_json', linker_names)

        # Make sure adapters and linkers landed in the proper place
        for adapter in man.adapters:
            self.assertIsInstance(adapter, otio.adapters.Adapter)

        for linker in man.media_linkers:
            self.assertIsInstance(linker, otio.media_linker.MediaLinker)

        self.assertTrue(
            any(
                True for p in man.source_files
                if self.mock_module_manifest_path in p
            )
        )

    def test_deduplicate_env_variable_paths(self):
        "Ensure that duplicate entries in the environment variable are ignored"

        # back up existing manifest
        bak_env = os.environ.get('OTIO_PLUGIN_MANIFEST_PATH')

        relative_path = self.mock_module_manifest_path.replace(os.getcwd(), '.')

        # set where to find the new manifest
        os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = os.pathsep.join(
            (
                # absolute
                self.mock_module_manifest_path,

                # relative
                relative_path
            )
        )

        result = otio.plugins.manifest.load_manifest()
        self.assertEqual(
            len(
                [
                    p for p in result.source_files
                    if self.mock_module_manifest_path in p
                ]
            ),
            1
        )
        if relative_path != self.mock_module_manifest_path:
            self.assertNotIn(relative_path, result.source_files)

        if bak_env:
            os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = bak_env
        else:
            del os.environ['OTIO_PLUGIN_MANIFEST_PATH']

    def test_plugin_load_failure(self):
        """When a plugin fails to load, ensure the exception message
        is logged (and no exception thrown)
        """

        sys.modules['otio_mock_bad_module'] = mock.Mock(
            name='otio_mock_bad_module',
            plugin_manifest=mock.Mock(
                side_effect=Exception("Mock Exception")
            )
        )

        entry_points = mock.patch(
            'opentimelineio.plugins.manifest.metadata.entry_points',
            return_value=[
                metadata.EntryPoint(
                    'mock_bad_module',
                    'otio_mock_bad_module',
                    'opentimelineio.plugins'
                )
            ]
        )

        with self.assertLogs() as cm, entry_points:
            # Load the above mock entrypoint, expect it to fail and log
            otio.plugins.manifest.load_manifest()

            load_errors = [
                r for r in cm.records
                if r.message.startswith(
                    "could not load plugin: mock_bad_module.  "
                    "Exception is: Mock Exception"
                )
            ]
            self.assertEqual(len(load_errors), 1)


if __name__ == '__main__':
    unittest.main()
