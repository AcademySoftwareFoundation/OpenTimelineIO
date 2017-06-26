#!/usr/bin/env python

import unittest
import os

import baseline_reader

import opentimelineio as otio

__doc__ = """ Unit tests for the adapter plugin system. """


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
            "baseline",
            ADAPTER_PATH
        )
        import ipdb; ipdb.set_trace()

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
            "baseline",
            "example.py"
        )

        self.assertEqual(self.adp.module_abs_path(), target)
        self.assertTrue(hasattr(self.adp.module(), "read_from_file"))

        # call through the module accessor
        self.assertEqual(self.adp.module().read_from_file("foo").name, "foo")

        # call through the convienence wrapper
        self.assertEqual(self.adp.read_from_file("foo").name, "foo")

    def test_run_media_linker_during_adapter(self):
        # @TODO: current issue is that the media linker argument is none
        fake_tl = self.adp.read_from_file("foo", media_linker_name="example")
        self.assertTrue(fake_tl.tracks[0][0].metadata.get('from_test_linker'))

        fake_tl = self.adp.read_from_file("foo", media_linker=None)
        self.assertTrue(fake_tl.tracks[0][0].metadata.get('from_test_linker'))


MAN_PATH = '/var/tmp/test_otio_manifest'


def test_manifest():
    full_baseline = baseline_reader.json_baseline_as_string(MANIFEST_PATH)

    with open(MAN_PATH, 'w') as fo:
        fo.write(full_baseline)
    man = otio.plugins.manifest_from_file(MAN_PATH)
    man._update_plugin_source(baseline_reader.path_to_baseline(MANIFEST_PATH))
    return man


class TestPluginManifest(unittest.TestCase):

    def test_plugin_manifest(self):
        man = test_manifest()

        self.assertEqual(man.source_files, [MAN_PATH])

        self.assertNotEqual(man.adapters, [])

    def test_find_adapter_by_suffix(self):
        man = test_manifest()
        self.assertEqual(man.from_filepath("example").name, "example")
        with self.assertRaises(Exception):
            man.from_filepath("BLARG")
        adp = man.from_filepath("example")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(man.adapter_module_from_suffix(
            "example").read_from_file("path").name, "path")

    def test_find_adapter_by_name(self):
        man = test_manifest()
        self.assertEqual(man.from_name("example").name, "example")
        with self.assertRaises(Exception):
            man.from_name("BLARG")
        adp = man.from_name("example")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(man.adapter_module_from_name(
            "example").read_from_file("path").name, "path")


if __name__ == '__main__':
    unittest.main()
