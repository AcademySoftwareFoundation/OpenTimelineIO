#
# Copyright 2017 Pixar Animation Studios
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
import unittest
import os

import opentimelineio as otio
import baseline_reader
import utils

"""Unit tests for the adapter plugin system."""


MANIFEST_PATH = "adapter_plugin_manifest.plugin_manifest"
ADAPTER_PATH = "adapter_example"
MEDIA_LINKER_EXAMPLE = "media_linker_example"


class TestAdapterSuffixes(unittest.TestCase):
    def test_supported_suffixes_is_not_none(self):
        result = otio.adapters.suffixes_with_defined_adapters()
        self.assertIsNotNone(result)
        self.assertNotEqual(result, [])
        self.assertNotEqual(result, set([]))


class TestPluginAdapters(unittest.TestCase):
    def setUp(self):
        self.jsn = baseline_reader.json_baseline_as_string(ADAPTER_PATH)
        self.adp = otio.adapters.otio_json.read_from_string(self.jsn)
        self.adp._json_path = os.path.join(
            baseline_reader.MODPATH,
            "baselines",
            ADAPTER_PATH
        )

    def test_plugin_adapter(self):
        self.assertEqual(self.adp.name, "example")
        self.assertEqual(self.adp.execution_scope, "in process")
        self.assertEqual(self.adp.filepath, "example.py")
        self.assertEqual(self.adp.suffixes, ["example"])

        self.assertMultiLineEqual(
            str(self.adp),
            "Adapter("
            "{}, "
            "{}, "
            "{}, "
            "{}"
            ")".format(
                repr(self.adp.name),
                repr(self.adp.execution_scope),
                repr(self.adp.filepath),
                repr(self.adp.suffixes),
            )
        )
        self.assertMultiLineEqual(
            repr(self.adp),
            "otio.adapter.Adapter("
            "name={}, "
            "execution_scope={}, "
            "filepath={}, "
            "suffixes={}"
            ")".format(
                repr(self.adp.name),
                repr(self.adp.execution_scope),
                repr(self.adp.filepath),
                repr(self.adp.suffixes),
            )
        )

        self.assertNotEqual(self.adp._json_path, None)

    def test_load_adapter_module(self):
        target = os.path.join(
            baseline_reader.MODPATH,
            "baselines",
            "example.py"
        )

        self.assertEqual(self.adp.module_abs_path(), target)
        self.assertTrue(hasattr(self.adp.module(), "read_from_file"))

        # call through the module accessor
        self.assertEqual(self.adp.module().read_from_file("foo").name, "foo")

        # call through the convienence wrapper
        self.assertEqual(self.adp.read_from_file("foo").name, "foo")

    def test_has_feature(self):
        self.assertTrue(self.adp.has_feature("read"))
        self.assertTrue(self.adp.has_feature("read_from_file"))
        self.assertFalse(self.adp.has_feature("write"))

    def test_pass_arguments_to_adapter(self):
        self.assertEqual(self.adp.read_from_file("foo", suffix=3).name, "foo3")

    def test_run_media_linker_during_adapter(self):
        mfest = otio.plugins.ActiveManifest()

        manifest = utils.create_manifest()
        # this wires up the media linkers into the active manifest
        mfest.media_linkers.extend(manifest.media_linkers)
        fake_tl = self.adp.read_from_file("foo", media_linker_name="example")

        self.assertTrue(
            fake_tl.tracks[0][0].media_reference.metadata.get(
                'from_test_linker'
            )
        )

        fake_tl = self.adp.read_from_string(
            "foo",
            media_linker_name="example"
        )

        self.assertTrue(
            fake_tl.tracks[0][0].media_reference.metadata.get(
                'from_test_linker'
            )
        )

        # explicitly turn the media_linker off
        fake_tl = self.adp.read_from_file("foo", media_linker_name=None)
        self.assertIsNone(
            fake_tl.tracks[0][0].media_reference.metadata.get(
                'from_test_linker'
            )
        )

        # Delete the temporary manifest
        utils.remove_manifest(manifest)


class TestPluginManifest(unittest.TestCase):

    def setUp(self):
        self.man = utils.create_manifest()

    def tearDown(self):
        utils.remove_manifest(self.man)

    def test_plugin_manifest(self):
        self.assertNotEqual(self.man.adapters, [])

    def test_find_adapter_by_suffix(self):
        self.assertEqual(self.man.from_filepath("example").name, "example")
        with self.assertRaises(Exception):
            self.man.from_filepath("BLARG")
        adp = self.man.from_filepath("example")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(
            self.man.adapter_module_from_suffix(
                "example"
            ).read_from_file("path").name,
            "path"
        )

    def test_find_adapter_by_name(self):
        self.assertEqual(self.man.from_name("example").name, "example")
        with self.assertRaises(Exception):
            self.man.from_name("BLARG")
        adp = self.man.from_name("example")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(
            self.man.adapter_module_from_name("example").read_from_file(
                "path"
            ).name,
            "path"
        )


if __name__ == '__main__':
    unittest.main()
