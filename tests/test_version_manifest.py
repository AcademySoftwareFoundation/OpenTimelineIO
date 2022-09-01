# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""unit tests for the version manifest plugin system"""

import unittest

import opentimelineio as otio
from tests import utils


class TestPlugin_VersionManifest(unittest.TestCase):
    def setUp(self):
        self.bak = otio.plugins.ActiveManifest()
        self.man = utils.create_manifest()
        otio.plugins.manifest._MANIFEST = self.man

    def tearDown(self):
        otio.plugins.manifest._MANIFEST = self.bak
        utils.remove_manifest(self.man)

    def test_read_in_manifest(self):
        self.assertIn("TEST_FAMILY_NAME", self.man.version_manifests)
        self.assertIn(
                "TEST_LABEL",
                self.man.version_manifests["TEST_FAMILY_NAME"]
        )

    def test_full_map(self):
        d = otio.versioning.full_map()
        self.assertIn("TEST_FAMILY_NAME", d)
        self.assertIn(
                "TEST_LABEL",
                d["TEST_FAMILY_NAME"]
        )

    def test_fetch_map(self):
        self.assertEquals(
                otio.versioning.fetch_map("TEST_FAMILY_NAME", "TEST_LABEL"),
                {"ExampleSchema": 1, "Clip": 1}
        )


if __name__ == '__main__':
    unittest.main()
