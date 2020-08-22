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

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class ClipTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        name = "test"
        rt = otio.opentime.RationalTime(5, 24)
        tr = otio.opentime.TimeRange(rt, rt)
        mr = otio.schema.ExternalReference(
            available_range=otio.opentime.TimeRange(
                rt,
                otio.opentime.RationalTime(10, 24)
            ),
            target_url="/var/tmp/test.mov"
        )

        cl = otio.schema.Clip(
            name=name,
            media_reference=mr,
            source_range=tr,
            # transition_in
            # transition_out
        )
        self.assertEqual(cl.name, name)
        self.assertEqual(cl.source_range, tr)
        self.assertIsOTIOEquivalentTo(cl.media_reference, mr)

        encoded = otio.adapters.otio_json.write_to_string(cl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(cl, decoded)

    def test_each_clip(self):
        cl = otio.schema.Clip(name="test_clip")
        self.assertEqual(list(cl.each_clip()), [cl])

    def test_str(self):
        cl = otio.schema.Clip(name="test_clip")

        self.assertMultiLineEqual(
            str(cl),
            'Clip("test_clip", MissingReference(\'\', None, {}), None, {})'
        )
        self.assertMultiLineEqual(
            repr(cl),
            'otio.schema.Clip('
            "name='test_clip', "
            'media_reference={}, '
            'source_range=None, '
            'metadata={{}}'
            ')'.format(
                repr(cl.media_reference)
            )
        )

    def test_str_with_filepath(self):
        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.schema.ExternalReference(
                "/var/tmp/foo.mov"
            )
        )
        self.assertMultiLineEqual(
            str(cl),
            'Clip('
            '"test_clip", ExternalReference("/var/tmp/foo.mov"), None, {}'
            ')'
        )
        self.assertMultiLineEqual(
            repr(cl),
            'otio.schema.Clip('
            "name='test_clip', "
            "media_reference=otio.schema.ExternalReference("
            "target_url='/var/tmp/foo.mov'"
            "), "
            'source_range=None, '
            'metadata={}'
            ')'
        )

    def test_ranges(self):
        tr = otio.opentime.TimeRange(
            # 1 hour in at 24 fps
            start_time=otio.opentime.RationalTime(86400, 24),
            duration=otio.opentime.RationalTime(200, 24)
        )

        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.schema.ExternalReference(
                "/var/tmp/foo.mov",
                available_range=tr
            )
        )
        self.assertEqual(cl.duration(), cl.trimmed_range().duration)
        self.assertEqual(cl.duration(), tr.duration)
        self.assertEqual(cl.trimmed_range(), tr)
        self.assertEqual(cl.available_range(), tr)
        self.assertIsNot(cl.trimmed_range(), tr)
        self.assertIsNot(cl.available_range(), tr)

        cl.source_range = otio.opentime.TimeRange(
            # 1 hour + 100 frames
            start_time=otio.opentime.RationalTime(86500, 24),
            duration=otio.opentime.RationalTime(50, 24)
        )
        self.assertNotEqual(cl.duration(), tr.duration)
        self.assertNotEqual(cl.trimmed_range(), tr)
        self.assertEqual(cl.duration(), cl.source_range.duration)
        self.assertIsNot(cl.duration(), cl.source_range.duration)

        self.assertEqual(cl.trimmed_range(), cl.source_range)
        self.assertIsNot(cl.trimmed_range(), cl.source_range)

    def test_ref_default(self):
        cl = otio.schema.Clip()
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.MissingReference()
        )

        cl.media_reference = None
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.MissingReference()
        )

        cl.media_reference = otio.schema.ExternalReference()
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.ExternalReference()
        )


if __name__ == '__main__':
    unittest.main()
