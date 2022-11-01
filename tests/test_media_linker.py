# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os
import unittest

from tests import baseline_reader

import opentimelineio as otio
from tests import utils

LINKER_PATH = "media_linker_example"


class TestPluginMediaLinker(unittest.TestCase):
    def setUp(self):
        self.bak = otio.plugins.ActiveManifest()
        self.man = utils.create_manifest()
        otio.plugins.manifest._MANIFEST = self.man
        self.jsn = baseline_reader.json_baseline_as_string(LINKER_PATH)
        self.mln = otio.adapters.otio_json.read_from_string(self.jsn)
        self.mln._json_path = os.path.join(
            baseline_reader.MODPATH,
            "baselines",
            LINKER_PATH
        )

    def tearDown(self):
        otio.plugins.manifest._MANIFEST = self.bak
        utils.remove_manifest(self.man)

    def test_plugin_adapter(self):
        self.assertEqual(self.mln.name, "example")
        self.assertEqual(self.mln.filepath, "example.py")

    def test_load_adapter_module(self):

        target = os.path.join(
            baseline_reader.MODPATH,
            "baselines",
            "example.py"
        )

        self.assertEqual(self.mln.module_abs_path(), target)
        self.assertTrue(hasattr(self.mln.module(), "link_media_reference"))

    def test_run_linker(self):
        cl = otio.schema.Clip(name="foo")

        linked_mr = self.mln.link_media_reference(cl, {"extra_data": True})
        self.assertIsInstance(linked_mr, otio.schema.MissingReference)
        self.assertEqual(linked_mr.name, cl.name + "_tweaked")
        self.assertEqual(linked_mr.metadata.get("extra_data"), True)

    def test_serialize(self):

        self.assertEqual(
            str(self.mln),
            "MediaLinker({}, {})".format(
                repr(self.mln.name),
                repr(self.mln.filepath)
            )
        )
        self.assertEqual(
            repr(self.mln),
            "otio.media_linker.MediaLinker("
            "name={}, "
            "filepath={}"
            ")".format(
                repr(self.mln.name),
                repr(self.mln.filepath)
            )
        )

    def test_available_media_linker_names(self):
        # for now just assert that it returns a non-empty list
        self.assertTrue(otio.media_linker.available_media_linker_names())

    def test_default_media_linker(self):
        os.environ['OTIO_DEFAULT_MEDIA_LINKER'] = 'foo'
        self.assertEqual(otio.media_linker.default_media_linker(), 'foo')
        with self.assertRaises(otio.exceptions.NoDefaultMediaLinkerError):
            del os.environ['OTIO_DEFAULT_MEDIA_LINKER']
            otio.media_linker.default_media_linker()

    def test_from_name_fail(self):
        with self.assertRaises(otio.exceptions.NotSupportedError):
            otio.media_linker.from_name("should not exist")


if __name__ == '__main__':
    unittest.main()
