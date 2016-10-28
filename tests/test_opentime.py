#!/usr/bin/env python

"""
Test Harness for the otio.opentime library.
"""

import opentimelineio as otio

import unittest
import os


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

    def test_comparison(self):
        t1 = otio.opentime.RationalTime(15.2)
        t2 = otio.opentime.RationalTime(15.6)
        self.assertTrue(t1 < t2)

        # test implicit base conversion
        t2 = otio.opentime.RationalTime(15.6, 48)
        self.assertTrue(t1 > t2)

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
        t = otio.opentime.from_timecode(timecode)
        self.assertEqual(timecode, otio.opentime.to_timecode(t))

    def test_timecode_24(self):
        timecode = "00:00:01:00"
        t = otio.opentime.RationalTime(value=24, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode))

        timecode = "00:01:00:00"
        t = otio.opentime.RationalTime(value=24 * 60, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode))

        timecode = "01:00:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode))

        timecode = "24:00:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60 * 24, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode))

        timecode = "23:59:59:23"
        t = otio.opentime.RationalTime(value=24 * 60 * 60 * 24 - 1, rate=24)
        self.assertEqual(t, otio.opentime.from_timecode(timecode))

    def test_time_timecode_zero(self):
        t = otio.opentime.RationalTime()
        timecode = "00:00:00:00"
        self.assertEqual(timecode, otio.opentime.to_timecode(t))
        self.assertEqual(t, otio.opentime.from_timecode(timecode))

    def test_long_running_timecode_24(self):
        previous_time = otio.opentime.RationalTime()
        previous_timecode = "00:00:00:00"

        if os.getenv("OTIO_FAST_TEST"):
            # for faster testing, lets skip around a bunch
            step = 23
        else:
            # for completeness, try every value
            step = 1

        for frame in range(step, 24 * 60 * 60 * 24, step):
            t = otio.opentime.from_frames(frame, 24)
            timecode = otio.opentime.to_timecode(t)

            self.assertEqual(len(timecode), len(previous_timecode))
            self.assertTrue(timecode > previous_timecode)
            self.assertTrue(t > previous_time)

            self.assertEqual(
                previous_time +
                otio.opentime.RationalTime(
                    value=step,
                    rate=24),
                t)

            t2 = otio.opentime.from_timecode(timecode)
            self.assertEqual(t, t2)

            components = timecode.split(":")
            self.assertEqual(int(components[-1]), t.value % 24)

            previous_time = t
            previous_timecode = timecode

        if step == 1:
            self.assertEqual(timecode, "23:59:59:23")

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
            start_time=otio.opentime.RationalTime(),
            end_time=tend
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

    def DISABLED_test_extended_by(self):
        tr = otio.opentime.TimeRange()
        with self.assertRaises(TypeError):
            tr.extended_by("foo")
        rt = otio.opentime.RationalTime(10, 25)
        tr = tr.extended_by(rt)
        self.assert_(tr.duration)
        self.assertEqual(tr.start_time, otio.opentime.RationalTime(0, 25))
        self.assertEqual(tr.duration, rt)
        rt = otio.opentime.RationalTime(-1, 25)
        tr = tr.extended_by(rt)
        self.assertEqual(tr.start_time, otio.opentime.RationalTime(-1, 25))
        self.assertEqual(tr.duration, otio.opentime.RationalTime(11, 25))

    def test_end_time(self):
        rt_start = otio.opentime.RationalTime(1, 24)
        rt_dur = otio.opentime.RationalTime(5, 24)
        tr = otio.opentime.TimeRange(rt_start, rt_dur)
        self.assertEqual(tr.duration, rt_dur)
        self.assertEqual(tr.end_time(), rt_start + rt_dur)

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
            tr.end_time()
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
        tstart = otio.opentime.RationalTime()
        tend = otio.opentime.RationalTime(12, 25)

        tr = otio.opentime.range_from_start_end_time(
            start_time=tstart,
            end_time=tend
        )

        self.assertEqual(tr.start_time, tstart)
        self.assertEqual(tr.duration, tend)

        self.assertEqual(tr.end_time(), tend)

        self.assertEqual(
            tr,
            otio.opentime.range_from_start_end_time(
                tr.start_time, tr.end_time())
        )


if __name__ == '__main__':
    unittest.main()
