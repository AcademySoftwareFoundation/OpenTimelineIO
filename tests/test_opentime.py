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

"""Test Harness for the otio.opentime library."""

import opentimelineio as otio

import unittest
import copy


class TestTime(unittest.TestCase):

    def test_create(self):
        t_val = 30.2
        t = otio.opentime.RationalTime(t_val)
        self.assertIsNotNone(t)
        self.assertEqual(t.value, t_val)

        t = otio.opentime.RationalTime()
        self.assertEqual(t.value, 0)
        self.assertEqual(t.rate, 1.0)

    def test_equality(self):
        t1 = otio.opentime.RationalTime(30.2)
        self.assertEqual(t1, t1)
        t2 = otio.opentime.RationalTime(30.2)
        self.assertTrue(t1 is not t2)
        self.assertEqual(t1, t2)

    def test_inequality(self):
        t1 = otio.opentime.RationalTime(30.2)
        self.assertEqual(t1, t1)
        t2 = otio.opentime.RationalTime(33.2)
        self.assertTrue(t1 is not t2)
        self.assertNotEqual(t1, t2)
        t3 = otio.opentime.RationalTime(30.2)
        self.assertTrue(t1 is not t3)
        self.assertFalse(t1 != t3)

    def test_comparison(self):
        t1 = otio.opentime.RationalTime(15.2)
        t2 = otio.opentime.RationalTime(15.6)
        self.assertTrue(t1 < t2)
        self.assertTrue(t1 <= t2)
        self.assertFalse(t1 > t2)
        self.assertFalse(t1 >= t2)

        # Ensure the equality case of the comparisons works correctly
        t3 = otio.opentime.RationalTime(30.4, 2)
        self.assertTrue(t1 <= t3)
        self.assertTrue(t1 >= t3)
        self.assertTrue(t3 <= t1)
        self.assertTrue(t3 >= t1)

        # test implicit base conversion
        t2 = otio.opentime.RationalTime(15.6, 48)
        self.assertTrue(t1 > t2)
        self.assertTrue(t1 >= t2)
        self.assertFalse(t1 < t2)
        self.assertFalse(t1 <= t2)

    def test_base_conversion(self):

        # from a number
        t = otio.opentime.RationalTime(10, 24)
        with self.assertRaises(TypeError):
            t.rescaled_to("foo")
        self.assertEqual(t.rate, 24)
        t = t.rescaled_to(48)
        self.assertEqual(t.rate, 48)

        # from another RationalTime
        t = otio.opentime.RationalTime(10, 24)
        t2 = otio.opentime.RationalTime(20, 48)
        t = t.rescaled_to(t2)
        self.assertEqual(t.rate, t2.rate)

    def test_time_timecode_convert(self):
        timecode = "00:06:56:17"
        t = otio.opentime.from_timecode(timecode, 24)
        self.assertEqual(timecode, otio.opentime.to_timecode(t))

    def test_timecode_24(self):
        timecode = "00:00:01:00"
        t = otio.opentime.RationalTime(value=24, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, 24))

        timecode = "00:01:00:00"
        t = otio.opentime.RationalTime(value=24 * 60, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, 24))

        timecode = "01:00:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, 24))

        timecode = "24:00:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60 * 24, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, 24))

        timecode = "23:59:59:23"
        t = otio.opentime.RationalTime(value=24 * 60 * 60 * 24 - 1, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, 24))

    def test_time_timecode_zero(self):
        t = otio.opentime.RationalTime()
        timecode = "00:00:00:00"
        self.assertEqual(timecode, otio.opentime.to_timecode(t, 24))
        self.assertEqual(t, otio.opentime.from_timecode(timecode, 24))

    def test_long_running_timecode_24(self):
        final_frame_number = 24 * 60 * 60 * 24 - 1
        final_time = otio.opentime.from_frames(final_frame_number, 24)
        self.assertEqual(
            otio.opentime.to_timecode(final_time),
            "23:59:59:23"
        )

        step_time = otio.opentime.RationalTime(value=1, rate=24)

        # important to copy -- otherwise assigns the same thing to two names
        cumulative_time = copy.copy(step_time)

        # small optimization - remove the "." operator.
        iadd_func = cumulative_time.__iadd__

        for _ in range(1, final_frame_number):
            iadd_func(step_time)
        self.assertEqual(cumulative_time, final_time)

        # Adding by a non-multiple of 24
        for fnum in range(1113, final_frame_number, 1113):
            rt = otio.opentime.from_frames(fnum, 24)
            tc = otio.opentime.to_timecode(rt)
            rt2 = otio.opentime.from_timecode(tc, 24)
            self.assertEqual(rt, rt2)
            self.assertEqual(tc, otio.opentime.to_timecode(rt2))

    def test_timecode_23976_fps(self):
        # These are reference value from a clip with burnt-in timecode
        ref_values_23976 = [
            (1025, '00:00:01:17'),
            (179900, '00:04:59:20'),
            (180000, '00:05:00:00'),
            (360000, '00:10:00:00'),
            (720000, '00:20:00:00'),
            (1079300, '00:29:58:20'),
            (1080000, '00:30:00:00'),
            (1080150, '00:30:00:06'),
            (1440000, '00:40:00:00'),
            (1800000, '00:50:00:00'),
            (1978750, '00:54:57:22'),
            (1980000, '00:55:00:00'),
            (46700, '00:01:17:20'),
            (225950, '00:06:16:14'),
            (436400, '00:12:07:08'),
            (703350, '00:19:32:06')
        ]
        for value, tc in ref_values_23976:
            t = otio.opentime.RationalTime(value, 600)
            self.assertEqual(tc, otio.opentime.to_timecode(t, rate=23.976))
            t1 = otio.opentime.from_timecode(tc, rate=23.976)
            self.assertEqual(t, t1)

    def test_timecode_2997fps(self):
        # These are reference value from a clip with burnt-in timecode
        ref_values_2997 = [
            (940, '00:00:01:17'),
            (179800, '00:04:59:20'),
            (180000, '00:05:00:00'),
            (360000, '00:10:00:00'),
            (720000, '00:20:00:00'),
            (1079200, '00:29:58:20'),
            (1080000, '00:30:00:00'),
            (1080120, '00:30:00:06'),
            (1440000, '00:40:00:00'),
            (1800000, '00:50:00:00'),
            (1978640, '00:54:57:22'),
            (1980000, '00:55:00:00'),
            (46600, '00:01:17:20'),
            (225880, '00:06:16:14'),
            (436360, '00:12:07:08'),
            (703320, '00:19:32:06')
        ]
        for value, tc in ref_values_2997:
            t = otio.opentime.RationalTime(value, 600)
            self.assertEqual(tc, otio.opentime.to_timecode(t, rate=29.97))
            t1 = otio.opentime.from_timecode(tc, rate=29.97)
            self.assertEqual(t, t1)

    def test_time_string_24(self):

        time_string = "00:00:00.041667"
        t = otio.opentime.RationalTime(value=1.0, rate=24)
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "00:00:01"
        t = otio.opentime.RationalTime(value=24, rate=24)
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "00:01:00"
        t = otio.opentime.RationalTime(value=24 * 60, rate=24)
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "01:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60, rate=24)
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "24:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60 * 24, rate=24)
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "23:59:59.958333"
        t = otio.opentime.RationalTime(value=24 * 60 * 60 * 24 - 1, rate=24)
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

    def test_time_string_25(self):
        time_string = "00:00:01"
        t = otio.opentime.RationalTime(value=25, rate=25)
        time_obj = otio.opentime.from_time_string(time_string, 25)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "00:01:00"
        t = otio.opentime.RationalTime(value=25 * 60, rate=25)
        time_obj = otio.opentime.from_time_string(time_string, 25)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "01:00:00"
        t = otio.opentime.RationalTime(value=25 * 60 * 60, rate=25)
        time_obj = otio.opentime.from_time_string(time_string, 25)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "24:00:00"
        t = otio.opentime.RationalTime(value=25 * 60 * 60 * 24, rate=25)
        time_obj = otio.opentime.from_time_string(time_string, 25)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

        time_string = "23:59:59.92"
        t = otio.opentime.RationalTime(value=25 * 60 * 60 * 24 - 2, rate=25)
        time_obj = otio.opentime.from_time_string(time_string, 25)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

    def test_time_time_string_zero(self):
        t = otio.opentime.RationalTime()
        time_string = "00:00:00.0"
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertEqual(time_string, otio.opentime.to_time_string(t))
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

    def test_long_running_time_string_24(self):
        final_frame_number = 24 * 60 * 60 * 24 - 1
        final_time = otio.opentime.from_frames(final_frame_number, 24)
        self.assertEqual(
            otio.opentime.to_time_string(final_time),
            "23:59:59.958333"
        )

        step_time = otio.opentime.RationalTime(value=1, rate=24)

        # important to copy -- otherwise assigns the same thing to two names
        cumulative_time = copy.copy(step_time)

        # small optimization - remove the "." operator.
        iadd_func = cumulative_time.__iadd__

        for _ in range(1, final_frame_number):
            iadd_func(step_time)
        self.assertTrue(cumulative_time.almost_equal(final_time, delta=0.001))

        # Adding by a non-multiple of 24
        for fnum in range(1113, final_frame_number, 1113):
            rt = otio.opentime.from_frames(fnum, 24)
            tc = otio.opentime.to_time_string(rt)
            rt2 = otio.opentime.from_time_string(tc, 24)
            self.assertEqual(rt, rt2)
            self.assertEqual(tc, otio.opentime.to_time_string(rt2))

    def test_time_string_23976_fps(self):
        # This list is rewritten from conversion into seconds of
        # test_timecode_23976_fps
        ref_values_23976 = [
            (1025, '00:00:01.708333'),
            (179900, '00:04:59.833333'),
            (180000, '00:05:00.0'),
            (360000, '00:10:00.0'),
            (720000, '00:20:00.0'),
            (1079300, '00:29:58.833333'),
            (1080000, '00:30:00.0'),
            (1080150, '00:30:00.25'),
            (1440000, '00:40:00.0'),
            (1800000, '00:50:00.0'),
            (1978750, '00:54:57.916666'),
            (1980000, '00:55:00.0'),
            (46700, '00:01:17.833333'),
            (225950, '00:06:16.583333'),
            (436400, '00:12:07.333333'),
            (703350, '00:19:32.25')
        ]
        for value, ts in ref_values_23976:
            t = otio.opentime.RationalTime(value, 600)
            self.assertEqual(ts, otio.opentime.to_time_string(t))
            # t1 = otio.opentime.from_time_string(ts, rate=23.976)
            # fails due to precision issues
            # self.assertEqual(t, t1)

    def test_time_to_string(self):
        t = otio.opentime.RationalTime(1, 2)
        self.assertEqual(str(t), "RationalTime(1, 2)")
        self.assertEqual(
            repr(t),
            "otio.opentime.RationalTime(value=1, rate=2)"
        )

    def test_frames_with_int_fps(self):
        for fps in (24, 30, 48, 60):
            t1 = otio.opentime.from_frames(101, fps)
            t2 = otio.opentime.RationalTime(101, fps)
            self.assertEqual(t1, t2)

    def test_frames_with_nonint_fps(self):
        for fps in (23.98, 29.97, 59.94):
            t1 = otio.opentime.from_frames(101, fps)
            self.assertEqual(t1.rate, 600)
            self.assertAlmostEqual(t1.value / t1.rate, 101 / fps)

    def test_seconds(self):
        s1 = 1834
        t1 = otio.opentime.from_seconds(s1)
        self.assertEqual(t1.value, 1834)
        self.assertEqual(t1.rate, 1)
        t1_as_seconds = otio.opentime.to_seconds(t1)
        self.assertEqual(t1_as_seconds, s1)
        self.assertAlmostEqual(float(t1.value) / t1.rate, s1)

        s2 = 248474.345
        t2 = otio.opentime.from_seconds(s2)
        self.assertAlmostEqual(t2.value, s2)
        self.assertAlmostEqual(t2.rate, 1.0)
        t2_as_seconds = otio.opentime.to_seconds(t2)
        self.assertAlmostEqual(s2, t2_as_seconds)
        self.assertAlmostEqual(float(t2.value) / t2.rate, s2)

        v3 = 3459
        r3 = 24
        s3 = float(3459) / 24
        t3 = otio.opentime.RationalTime(v3, r3)
        t4 = otio.opentime.from_seconds(s3)
        self.assertAlmostEqual(otio.opentime.to_seconds(t3), s3)
        self.assertAlmostEqual(otio.opentime.to_seconds(t4), s3)

        v3 = 3459
        r3 = 24
        s3 = float(3459) / 24
        t3 = otio.opentime.RationalTime(v3, r3)
        t4 = otio.opentime.from_seconds(s3)
        self.assertAlmostEqual(otio.opentime.to_seconds(t3), s3)
        self.assertAlmostEqual(otio.opentime.to_seconds(t4), s3)

    def test_duration(self):
        start_time = otio.opentime.from_frames(100, 24)
        end = otio.opentime.from_frames(200, 24)
        duration = otio.opentime.duration_from_start_end_time(start_time, end)
        self.assertEqual(duration, otio.opentime.from_frames(100, 24))

        start_time = otio.opentime.from_frames(0, 1)
        end = otio.opentime.from_frames(200, 24)
        duration = otio.opentime.duration_from_start_end_time(start_time, end)
        self.assertEqual(duration, otio.opentime.from_frames(200, 24))

    def test_math(self):
        a = otio.opentime.from_frames(100, 24)
        gap = otio.opentime.from_frames(50, 24)
        b = otio.opentime.from_frames(150, 24)
        self.assertEqual(b - a, gap)
        self.assertEqual(a + gap, b)
        self.assertEqual(b - gap, a)

        with self.assertRaises(TypeError):
            b + "foo"

        a += gap
        self.assertEqual(a, b)

        a = otio.opentime.from_frames(100, 24)
        step = otio.opentime.from_frames(1, 24)
        for _ in range(50):
            a += step
        self.assertEqual(a, otio.opentime.from_frames(150, 24))

    def test_math_with_different_scales(self):
        a = otio.opentime.from_frames(100, 24)
        gap = otio.opentime.from_frames(100, 48)
        b = otio.opentime.from_frames(75, 12)
        self.assertEqual(b - a, gap.rescaled_to(24))
        self.assertEqual(a + gap, b.rescaled_to(48))
        self.assertEqual(b - gap, a.rescaled_to(48))

    def test_hash(self):
        rt = otio.opentime.RationalTime(1, 12)
        rt2 = otio.opentime.RationalTime(1, 12)

        self.assertEqual(hash(rt), hash(rt2))

        rt2 = otio.opentime.RationalTime(5, 12)

        self.assertNotEqual(hash(rt), hash(rt2))

    def test_duration_from_start_end_time(self):
        tend = otio.opentime.RationalTime(12, 25)

        tdur = otio.opentime.duration_from_start_end_time(
            start_time=otio.opentime.RationalTime(0, 25),
            end_time_exclusive=tend
        )

        self.assertEqual(tend, tdur)


class TestTimeTransform(unittest.TestCase):

    def test_identity_transform(self):
        tstart = otio.opentime.RationalTime(12, 25)
        txform = otio.opentime.TimeTransform()
        self.assertEqual(tstart, txform.applied_to(tstart))

        tstart = otio.opentime.RationalTime(12, 25)
        txform = otio.opentime.TimeTransform(rate=50)
        self.assertEqual(24, txform.applied_to(tstart).value)

    def test_offset(self):
        tstart = otio.opentime.RationalTime(12, 25)
        toffset = otio.opentime.RationalTime(10, 25)
        txform = otio.opentime.TimeTransform(offset=toffset)
        self.assertEqual(tstart + toffset, txform.applied_to(tstart))

        tr = otio.opentime.TimeRange(tstart, tstart)
        self.assertEqual(
            txform.applied_to(tr),
            otio.opentime.TimeRange(tstart + toffset, tstart)
        )

    def test_scale(self):
        tstart = otio.opentime.RationalTime(12, 25)
        txform = otio.opentime.TimeTransform(scale=2)
        self.assertEqual(
            otio.opentime.RationalTime(24, 25),
            txform.applied_to(tstart)
        )

        tr = otio.opentime.TimeRange(tstart, tstart)
        tstart_scaled = otio.opentime.RationalTime(24, 25)
        self.assertEqual(
            txform.applied_to(tr),
            otio.opentime.TimeRange(tstart_scaled, tstart_scaled)
        )

    def test_rate(self):
        txform1 = otio.opentime.TimeTransform()
        txform2 = otio.opentime.TimeTransform(rate=50)
        self.assertEqual(txform2.rate, txform1.applied_to(txform2).rate)

    def test_string(self):
        tstart = otio.opentime.RationalTime(12, 25)
        txform = otio.opentime.TimeTransform(offset=tstart, scale=2)
        self.assertEqual(
            repr(txform),
            "otio.opentime.TimeTransform("
            "offset=otio.opentime.RationalTime("
            "value=12, "
            "rate=25"
            "), "
            "scale=2, "
            "rate=None"
            ")"
        )

        self.assertEqual(
            str(txform),
            "TimeTransform(RationalTime(12, 25), 2, None)"
        )

    def test_hash(self):
        tstart = otio.opentime.RationalTime(12, 25)
        txform = otio.opentime.TimeTransform(offset=tstart, scale=2)
        tstart = otio.opentime.RationalTime(12, 25)
        txform2 = otio.opentime.TimeTransform(offset=tstart, scale=2)

        self.assertEqual(hash(txform), hash(txform2))

        txform2 = otio.opentime.TimeTransform(offset=tstart, scale=3)
        self.assertNotEqual(hash(txform), hash(txform2))

        txform2 = otio.opentime.TimeTransform(offset=tstart, scale=2, rate=10)
        self.assertNotEqual(hash(txform), hash(txform2))

    def test_comparison(self):
        tstart = otio.opentime.RationalTime(12, 25)
        txform = otio.opentime.TimeTransform(offset=tstart, scale=2)
        tstart = otio.opentime.RationalTime(12, 25)
        txform2 = otio.opentime.TimeTransform(offset=tstart, scale=2)
        self.assertEqual(txform, txform2)
        self.assertFalse(txform != txform2)

        tstart = otio.opentime.RationalTime(23, 25)
        txform3 = otio.opentime.TimeTransform(offset=tstart, scale=2)
        self.assertNotEqual(txform, txform3)
        self.assertFalse(txform == txform3)


class TestTimeRange(unittest.TestCase):

    def test_create(self):
        tr = otio.opentime.TimeRange()
        blank = otio.opentime.RationalTime()
        self.assertEqual(tr.start_time, blank)
        self.assertEqual(tr.duration, blank)

    def test_duration_validation(self):
        tr = otio.opentime.TimeRange()
        with self.assertRaises(TypeError):
            setattr(tr, "duration", "foo")

        bad_t = otio.opentime.RationalTime(-1, 1)
        with self.assertRaises(TypeError):
            setattr(tr, "duration", bad_t)

    def test_extended_by(self):
        # base 25 is just for testing

        # range starts at 0 and has duration 0
        tr = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 25)
        )
        with self.assertRaises(TypeError):
            tr.extended_by("foo")
        self.assertEqual(tr.duration, otio.opentime.RationalTime())

    def test_end_time(self):
        # test whole number duration
        rt_start = otio.opentime.RationalTime(1, 24)
        rt_dur = otio.opentime.RationalTime(5, 24)
        tr = otio.opentime.TimeRange(rt_start, rt_dur)
        self.assertEqual(tr.duration, rt_dur)
        self.assertEqual(tr.end_time_exclusive(), rt_start + rt_dur)
        self.assertEqual(
            tr.end_time_inclusive(),
            rt_start + rt_dur - otio.opentime.RationalTime(1, 24)
        )

        # test non-integer duration value
        rt_dur = otio.opentime.RationalTime(5.5, 24)
        tr = otio.opentime.TimeRange(rt_start, rt_dur)
        self.assertEqual(tr.end_time_exclusive(), rt_start + rt_dur)
        self.assertEqual(
            tr.end_time_inclusive(),
            otio.opentime.RationalTime(6, 24)
        )

    def test_repr(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(-1, 24),
            otio.opentime.RationalTime(6, 24)
        )
        self.assertEqual(
            repr(tr),
            "otio.opentime.TimeRange("
            "start_time=otio.opentime.RationalTime(value=-1, rate=24), "
            "duration=otio.opentime.RationalTime(value=6, rate=24))"
        )

    def test_compare(self):
        start_time1 = otio.opentime.RationalTime(18, 24)
        duration1 = otio.opentime.RationalTime(7, 24)
        tr1 = otio.opentime.TimeRange(start_time1, duration1)
        start_time2 = otio.opentime.RationalTime(18, 24)
        duration2 = otio.opentime.RationalTime(14, 48)
        tr2 = otio.opentime.TimeRange(start_time2, duration2)
        self.assertEqual(tr1, tr2)
        self.assertFalse(tr1 != tr2)

        start_time3 = otio.opentime.RationalTime(20, 24)
        duration3 = otio.opentime.RationalTime(3, 24)
        tr3 = otio.opentime.TimeRange(start_time3, duration3)
        self.assertNotEqual(tr1, tr3)
        self.assertFalse(tr1 == tr3)

    def test_clamped(self):
        test_point_min = otio.opentime.RationalTime(-2, 24)
        test_point_max = otio.opentime.RationalTime(6, 24)

        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(-1, 24),
            otio.opentime.RationalTime(6, 24),
        )

        other_tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(-2, 24),
            otio.opentime.RationalTime(7, 24),
        )

        self.assertEqual(tr.clamped(test_point_min), test_point_min)
        self.assertEqual(tr.clamped(test_point_max), test_point_max)

        self.assertEqual(tr.clamped(other_tr), other_tr)

        start_bound = otio.opentime.BoundStrategy.Clamp
        end_bound = otio.opentime.BoundStrategy.Clamp

        self.assertEqual(
            tr.clamped(test_point_min, start_bound, end_bound),
            tr.start_time
        )
        self.assertEqual(
            tr.clamped(test_point_max, start_bound, end_bound),
            tr.end_time_exclusive()
        )

        self.assertEqual(
            tr.clamped(other_tr, start_bound, end_bound),
            other_tr
        )

        with self.assertRaises(TypeError):
            tr.clamped("foo")

    def test_hash(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr2 = otio.opentime.TimeRange(tstart, tdur)

        self.assertEqual(hash(tr), hash(tr2))

    def test_overlaps_garbage(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        with self.assertRaises(TypeError):
            tr.overlaps("foo")

    def test_contains(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3.3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        with self.assertRaises(TypeError):
            tr.contains("foo")
        self.assertTrue(tr.contains(tstart))
        self.assertFalse(tr.contains(tstart + tdur))
        self.assertFalse(tr.contains(tstart - tdur))

        self.assertTrue(tr.contains(tr))

        tr_2 = otio.opentime.TimeRange(tstart - tdur, tdur)
        self.assertFalse(tr.contains(tr_2))
        self.assertFalse(tr_2.contains(tr))

    def test_overlaps_rationaltime(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.overlaps(otio.opentime.RationalTime(13, 25)))
        self.assertFalse(tr.overlaps(otio.opentime.RationalTime(1, 25)))

    def test_overlaps_timerange(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        tstart = otio.opentime.RationalTime(0, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(10, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(13, 25)
        tdur = otio.opentime.RationalTime(1, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(2, 25)
        tdur = otio.opentime.RationalTime(30, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(2, 50)
        tdur = otio.opentime.RationalTime(60, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(2, 50)
        tdur = otio.opentime.RationalTime(14, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(-100, 50)
        tdur = otio.opentime.RationalTime(400, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(100, 50)
        tdur = otio.opentime.RationalTime(400, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

    def test_range_from_start_end_time(self):
        tstart = otio.opentime.RationalTime(0, 25)
        tend = otio.opentime.RationalTime(12, 25)

        tr = otio.opentime.range_from_start_end_time(
            start_time=tstart,
            end_time_exclusive=tend
        )

        self.assertEqual(tr.start_time, tstart)
        self.assertEqual(tr.duration, tend)

        self.assertEqual(tr.end_time_exclusive(), tend)
        self.assertEqual(
            tr.end_time_inclusive(),
            tend - otio.opentime.RationalTime(1, 25)
        )

        self.assertEqual(
            tr,
            otio.opentime.range_from_start_end_time(
                tr.start_time, tr.end_time_exclusive()
            )
        )

    def test_adjacent_timeranges(self):
        d1 = 0.3
        d2 = 0.4
        r1 = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(d1, 1)
        )
        r2 = otio.opentime.TimeRange(
            r1.end_time_exclusive(),
            otio.opentime.RationalTime(d2, 1)
        )
        full = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(d1 + d2, 1)
        )
        self.assertFalse(r1.overlaps(r2))
        self.assertEqual(r1.extended_by(r2), full)

    def test_distant_timeranges(self):
        start = 0.1
        d1 = 0.3
        gap = 1.7
        d2 = 0.4
        r1 = otio.opentime.TimeRange(
            otio.opentime.RationalTime(start, 1),
            otio.opentime.RationalTime(d1, 1)
        )
        r2 = otio.opentime.TimeRange(
            otio.opentime.RationalTime(start + gap + d1, 1),
            otio.opentime.RationalTime(d2, 1)
        )
        full = otio.opentime.TimeRange(
            otio.opentime.RationalTime(start, 1),
            otio.opentime.RationalTime(d1 + gap + d2, 1)
        )
        self.assertFalse(r1.overlaps(r2))
        self.assertEqual(full, r1.extended_by(r2))
        self.assertEqual(full, r2.extended_by(r1))

    def test_to_timecode_mixed_rates(self):
        timecode = "00:06:56:17"
        t = otio.opentime.from_timecode(timecode, 24)
        self.assertEqual(timecode, otio.opentime.to_timecode(t))
        self.assertEqual(timecode, otio.opentime.to_timecode(t, 24))
        self.assertNotEqual(timecode, otio.opentime.to_timecode(t, 12))

    def test_to_frames_mixed_rates(self):
        frame = 100
        t = otio.opentime.from_frames(frame, 24)
        self.assertEqual(frame, otio.opentime.to_frames(t))
        self.assertEqual(frame, otio.opentime.to_frames(t, 24))
        self.assertNotEqual(frame, otio.opentime.to_frames(t, 12))


if __name__ == '__main__':
    unittest.main()
