#
# Copyright 2018 Pixar Animation Studios
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

__doc__ = """Test range_of function from algorithms."""

# @TODO: A case with scales
# @TODO: freeze frame & inverting a 0 scale transform
# @TODO: Transforms
# @TODO: up-and-down in one call


# utility constructors
# @{
def new_gap(duration_in_24fps):
    return otio.schema.Gap(source_range=new_range(0, duration_in_24fps, 24))


def new_range(start, dur, rate=24):
    return otio.opentime.TimeRange(
        otio.opentime.RationalTime(start, rate),
        otio.opentime.RationalTime(dur, rate),
    )
# @}


class TimeTransformUtilityTests(unittest.TestCase):
    def test_hierarchy_path(self):
        tr_top = otio.schema.Track(name="Parent Track")
        tr_top.append(new_gap(10))
        tr_top.append(new_gap(20))
        tr_mid = otio.schema.Track(name="middle track")
        tr_mid.append(new_gap(5))
        tr_mid.append(new_gap(41))
        tr_top.append(tr_mid)
        cl_leaf = otio.schema.Clip(
            name='child1',
            source_range=new_range(3, 12)
        )
        tr_mid.append(cl_leaf)

        l2p = otio.algorithms.time_transforms.relative_transform(
            cl_leaf,
            tr_top
        )

        local_time = otio.opentime.RationalTime(5, 24)
        time_in_parent = l2p * local_time

        self.assertEqual(
            time_in_parent.value,
            78
        )

        self.assertEqual(
            l2p,
            otio.opentime.TimeTransform(1, otio.opentime.RationalTime(73, 24))
        )

        self.assertEqual(
            otio.algorithms.time_transforms.relative_transform(tr_top, tr_top),
            otio.opentime.TimeTransform(1, otio.opentime.RationalTime(0, 24))
        )

    def test_path_between(self):
        tr_top = otio.schema.Track(name="Parent Track")
        tr_mid = otio.schema.Track(name="Middle Track")
        tr_top.append(tr_mid)
        cl_leaf = otio.schema.Clip(name='Child1')
        tr_mid.append(cl_leaf)

        self.assertEqual(
            otio.algorithms.time_transforms.path_between(cl_leaf, tr_top),
            (cl_leaf, tr_mid, tr_top)
        )

        self.assertEqual(
            otio.algorithms.time_transforms.path_between(cl_leaf, cl_leaf),
            (cl_leaf,)
        )

        self.assertEqual(
            otio.algorithms.time_transforms.path_between(tr_mid, cl_leaf),
            (tr_mid, cl_leaf)
        )

        with self.assertRaises(RuntimeError):
            otio.algorithms.time_transforms.path_between(tr_mid, new_gap(10))


def range_of_test_runner(self, arg_map):
    for i, (args, expected_result) in enumerate(arg_map):
        measured_result_range = otio.range_of(*args)
        measured_result = (
            measured_result_range.start_time.value,
            measured_result_range.duration.value
        )

        self.longMessage = True
        self.assertEqual(
            measured_result,
            expected_result,
            msg="failed test iteration {}".format(i)
        )


class RangeOfTests(unittest.TestCase):
    def test_range_no_trims_no_scales(self):
        tr_top = otio.schema.Track(name="Parent Track")
        tr_top.append(new_gap(10))
        tr_top.append(new_gap(20))
        tr_mid = otio.schema.Track(name="middle track")
        tr_mid.append(new_gap(5))
        tr_mid.append(new_gap(41))
        tr_top.append(tr_mid)
        cl_leaf = otio.schema.Clip(
            name='child1',
            source_range=new_range(3, 12)
        )
        tr_mid.append(cl_leaf)

        argument_to_result_map = [
            ((cl_leaf, cl_leaf), (3, 12)),
            ((cl_leaf, tr_top), (76, 12)),
            ((tr_top, cl_leaf), (-73, 88)),
            ((tr_top, tr_top), (0, 88)),
        ]

        range_of_test_runner(self, argument_to_result_map)

    def test_range_of_track_shorter_than_clip(self):
        """Test the range_of for a shorter track containing a longer clip."""

        # Track
        # [0---30 frames gap---30][10----10 frames clip---20]
        # [0--------------------track space---------------40]
        #              track trim                  [35   3]

        tr = otio.schema.Track(name="Parent Track")
        tr.source_range = new_range(35, 3)
        tr.append(new_gap(30))

        mr_1 = otio.schema.ExternalReference(available_range=new_range(0, 20))

        cl_1 = otio.schema.Clip(
            name='cl1',
            source_range=new_range(10, 10),
            media_reference=mr_1
        )
        tr.append(cl_1)

        # clip range in clip space: 10->20 (dur: 10)
        # clip range in clip space trimmed to track: 15->18 (dur: 3)
        # clip range in track space: 30->40 (dur: 10)
        # clip range in track space trimmed to track: 35->38 (dur: 3)
        #
        # track range in clip space: 15->18 (dur: 3)
        # track range in clip space trimmed to clip: 15->18 (dur: 3)
        # track range in track space: 35->38 (dur: 3)
        # track range in track space trimmed to track: 35->38 (dur: 3)

        argument_to_result_map = [
            # ARGUMENT           EXPECTED RESULT (start_time.value, dur.value)
            # the clip's range
            ((cl_1, cl_1, cl_1), (10, 10)),
            # the clip's range but trimmed to the track's range
            ((cl_1, cl_1, tr),   (15, 3)),
            # the clip's range in the space of the track trimmed to the clip
            ((cl_1, tr,   cl_1), (30, 10)),
            # the clip's range in the space and trimmed to the track
            ((cl_1, tr, tr),     (35, 3)),

            # from the track down to the clip
            ((tr, cl_1, cl_1), (15, 3)),
            ((tr, cl_1, tr),   (15, 3)),
            ((tr, tr,   cl_1), (35, 3)),
            ((tr, tr, tr),     (35, 3)),
        ]

        range_of_test_runner(self, argument_to_result_map)

    def test_range_of_track_longer_than_clip(self):
        """Test the range_of for a longer track containing a shorter clip."""

        # Track
        # [0---30 frames gap---30][10----10 frames clip---20]
        # [0--------------------track space---------------40]

        tr = otio.schema.Track(name="Parent Track")
        tr.append(new_gap(30))

        mr_1 = otio.schema.ExternalReference(available_range=new_range(0, 20))

        cl_1 = otio.schema.Clip(
            name='cl1',
            source_range=new_range(10, 10),
            media_reference=mr_1
        )
        tr.append(cl_1)

        # clip range in clip space: 10->20 (dur: 10)
        # clip range in clip space trimmed to track: 10->20 (dur: 10)
        # clip range in track space: 30->40 (dur: 10)
        # clip range in track space trimmed to track: 30->40 (dur: 10)
        #
        # track range in clip space: -20->20 (dur: 40)
        # track range in clip space trimmed to clip: 10->20 (dur: 10)
        # track range in track space: 30->40 (dur:10)
        # track range in track space trimmed to track: 0->40 (dur: 40)

        argument_to_result_map = [
            # ARGUMENT           EXPECTED RESULT (start_time.value, dur.value)
            # the clip's range
            ((cl_1, cl_1, cl_1), (10, 10)),
            # the clip's range but trimmed to the track's range
            ((cl_1, cl_1, tr),   (10, 10)),
            # the clip's range in the space of the track trimmed to the clip
            ((cl_1, tr,   cl_1), (30, 10)),
            # the clip's range in the space and trimmed to the track
            ((cl_1, tr, tr),     (30, 10)),

            # from the track down to the clip
            ((tr, cl_1, tr),   (-20, 40)),
            ((tr, cl_1, cl_1), (10, 10)),
            ((tr, tr,   cl_1), (30, 10)),
            ((tr, tr, tr),     (0, 40)),
        ]

        range_of_test_runner(self, argument_to_result_map)

    def test_range_of_with_small_middle_track(self):
        # Stack
        #                                   [0 gap ... 40]
        #                                   [0 stack space                 40]
        # [0--------------------track space-[35-38]-------40]
        # [0---30 frames gap---30][10----10 frames clip---20]

        st = otio.schema.Stack(name="Parent Stack")
        tr = otio.schema.Track(name="Parent Track")
        st.append(new_gap(40))
        st.append(tr)
        tr.source_range = new_range(35, 3)
        tr.append(new_gap(30))

        mr_1 = otio.schema.ExternalReference(available_range=new_range(0, 20))

        cl_1 = otio.schema.Clip(
            name='cl1',
            source_range=new_range(10, 10),
            media_reference=mr_1
        )
        tr.append(cl_1)

        # clip range in clip space: 10->20 (dur: 10)
        # clip range in clip space trimmed to stack: 15->18 (dur: 3)
        # clip range in stack space: 30->40 (dur: 10)
        # clip range in stack space trimmed to stack: 35->38 (dur: 3)
        #
        # stack range in clip space: -20 (dur: 20)
        # stack range in clip space trimmed to clip: 15->18 (dur: 3)
        # stack range in stack space: 0->40 (dur: 40)
        # stack range in stack space trimmed to trac: 35->38 (dur: 3)

        argument_to_result_map = [
            # ARGUMENT           EXPECTED RESULT (start_time.value, dur.value)
            # the clip's range
            ((cl_1, cl_1, cl_1), (10, 10)),
            # the clip's range but trimmed to the track's range
            ((cl_1, cl_1, st),   (15, 3)),
            # the clip's range in the space of the track trimmed to the clip
            ((cl_1, st,   cl_1), (-5, 10)),
            # the clip's range in the space and trimmed to the track
            ((cl_1, st, st),     (0, 3)),

            # from the track down to the clip
            ((tr, cl_1, cl_1), (15, 3)),
            ((tr, cl_1, tr),   (15, 3)),
            ((st, st,   cl_1), (0, 3)),
            ((tr, st, st),     (0, 3)),
        ]

        range_of_test_runner(self, argument_to_result_map)


if __name__ == '__main__':
    unittest.main()
