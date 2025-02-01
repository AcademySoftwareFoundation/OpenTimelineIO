# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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

        t_val = -30.2
        t = otio.opentime.RationalTime(t_val)
        self.assertIsNotNone(t)
        self.assertEqual(t.value, t_val)

        t = otio.opentime.RationalTime()
        self.assertEqual(t.value, 0)
        self.assertEqual(t.rate, 1.0)

    def test_valid(self):
        t1 = otio.opentime.RationalTime(0, 0)
        self.assertTrue(t1.is_invalid_time())
        self.assertFalse(t1.is_valid_time())
        t2 = otio.opentime.RationalTime(24)
        self.assertTrue(t2.is_valid_time())
        self.assertFalse(t2.is_invalid_time())

    def test_equality(self):
        t1 = otio.opentime.RationalTime(30.2)
        self.assertEqual(t1, t1)
        t2 = otio.opentime.RationalTime(30.2)
        self.assertTrue(t1 is not t2)
        self.assertEqual(t1, t2)
        t3 = otio.opentime.RationalTime(60.4, 2.0)
        self.assertEqual(t1, t3)

    def test_inequality(self):
        t1 = otio.opentime.RationalTime(30.2)
        self.assertEqual(t1, t1)
        t2 = otio.opentime.RationalTime(33.2)
        self.assertTrue(t1 is not t2)
        self.assertNotEqual(t1, t2)
        t3 = otio.opentime.RationalTime(30.2)
        self.assertTrue(t1 is not t3)
        self.assertFalse(t1 != t3)

    def test_strict_equality(self):
        t1 = otio.opentime.RationalTime(30.2)
        self.assertTrue(t1.strictly_equal(t1))
        t2 = otio.opentime.RationalTime(30.2)
        self.assertTrue(t1.strictly_equal(t2))
        t3 = otio.opentime.RationalTime(60.4, 2.0)
        self.assertFalse(t1.strictly_equal(t3))

    def test_rounding(self):
        t1 = otio.opentime.RationalTime(30.2)
        self.assertEqual(t1.floor(), otio.opentime.RationalTime(30.0))
        self.assertEqual(t1.ceil(), otio.opentime.RationalTime(31.0))
        self.assertEqual(t1.round(), otio.opentime.RationalTime(30.0))
        t2 = otio.opentime.RationalTime(30.8)
        self.assertEqual(t2.floor(), otio.opentime.RationalTime(30.0))
        self.assertEqual(t2.ceil(), otio.opentime.RationalTime(31.0))
        self.assertEqual(t2.round(), otio.opentime.RationalTime(31.0))

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

    def test_copy(self):
        t1 = otio.opentime.RationalTime(18, 24)

        t2 = copy.copy(t1)
        self.assertEqual(t2, otio.opentime.RationalTime(18, 24))

    def test_deepcopy(self):
        t1 = otio.opentime.RationalTime(18, 24)

        t2 = copy.deepcopy(t1)
        self.assertEqual(t2, otio.opentime.RationalTime(18, 24))

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

    def test_negative_timecode(self):
        with self.assertRaises(ValueError):
            otio.opentime.from_timecode('-01:00:13:13', 24)

    def test_bogus_timecode(self):
        with self.assertRaises(ValueError):
            otio.opentime.from_timecode('pink elephants', 13)

    def test_time_timecode_convert_bad_rate(self):
        with self.assertRaises(ValueError) as exception_manager:
            otio.opentime.from_timecode('01:00:13:24', 24)

        exc_message = str(exception_manager.exception)
        self.assertEqual(
            exc_message,
            "Frame rate mismatch.  Timecode '01:00:13:24' has frames beyond 23",
        )

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

    def test_plus_equals(self):
        sum1 = otio.opentime.RationalTime()
        sum2 = otio.opentime.RationalTime()

        for i in range(10):
            incr = otio.opentime.RationalTime(i + 1, 24)
            sum1 += incr
            sum2 = sum2 + incr

        self.assertEqual(sum1, sum2)

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

        # fetching this test function from the c++ module directly
        cumulative_time = otio._opentime._testing.add_many(
            step_time,
            final_frame_number
        )
        self.assertEqual(cumulative_time, final_time)

        # Adding by a non-multiple of 24
        for fnum in range(1113, final_frame_number, 1113):
            rt = otio.opentime.from_frames(fnum, 24)
            tc = otio.opentime.to_timecode(rt)
            rt2 = otio.opentime.from_timecode(tc, 24)
            self.assertEqual(rt, rt2)
            self.assertEqual(tc, otio.opentime.to_timecode(rt2))

    def test_timecode_23976_fps(self):
        # This should behave exactly like 24 fps
        ntsc_23976 = 24000 / 1001.0
        timecode = "00:00:01:00"
        t = otio.opentime.RationalTime(value=24, rate=ntsc_23976)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, ntsc_23976))

        timecode = "00:01:00:00"
        t = otio.opentime.RationalTime(value=24 * 60, rate=ntsc_23976)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, ntsc_23976))

        timecode = "01:00:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60, rate=ntsc_23976)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, ntsc_23976))

        timecode = "24:00:00:00"
        t = otio.opentime.RationalTime(value=24 * 60 * 60 * 24, rate=ntsc_23976)
        self.assertEqual(t, otio.opentime.from_timecode(timecode, ntsc_23976))

        timecode = "23:59:59:23"
        t = otio.opentime.RationalTime(
            value=24 * 60 * 60 * 24 - 1,
            rate=ntsc_23976
        )
        self.assertEqual(
            t, otio.opentime.from_timecode(timecode, ntsc_23976)
        )

    def test_converting_negative_values_to_timecode(self):
        t = otio.opentime.RationalTime(value=-1, rate=25)
        with self.assertRaises(ValueError):
            otio.opentime.to_timecode(t, 25)

    def test_dropframe_timecode_2997fps(self):
        """Test drop frame in action. Focused on minute roll overs

        We nominal_fps 30 for frame calculation
        For this frame rate we drop 2 frames per minute except every 10th.

        Compensation is calculated like this when below 10 minutes:
          (fps * seconds + frames - dropframes * (minutes - 1))
        Like this when not a whole 10 minute above 10 minutes:
          --minutes == minutes - 1
          (fps * seconds + frames - dropframes * (--minutes - --minutes / 10))
        And like this after that:
          (fps * seconds + frames - dropframes * (minutes - minutes / 10))
        """
        test_values = {
            'first_four_frames': [
                (0, '00:00:00;00'),
                (1, '00:00:00;01'),
                (2, '00:00:00;02'),
                (3, '00:00:00;03')
            ],

            'first_minute_rollover': [
                (30 * 59 + 29, '00:00:59;29'),
                (30 * 59 + 30, '00:01:00;02'),
                (30 * 59 + 31, '00:01:00;03'),
                (30 * 59 + 32, '00:01:00;04'),
                (30 * 59 + 33, '00:01:00;05')
            ],

            'fift_minute': [
                (30 * 299 + 29 - 2 * 4, '00:04:59;29'),
                (30 * 299 + 30 - 2 * 4, '00:05:00;02'),
                (30 * 299 + 31 - 2 * 4, '00:05:00;03'),
                (30 * 299 + 32 - 2 * 4, '00:05:00;04'),
                (30 * 299 + 33 - 2 * 4, '00:05:00;05')
            ],

            'seventh_minute': [
                (30 * 419 + 29 - 2 * 6, '00:06:59;29'),
                (30 * 419 + 30 - 2 * 6, '00:07:00;02'),
                (30 * 419 + 31 - 2 * 6, '00:07:00;03'),
                (30 * 419 + 32 - 2 * 6, '00:07:00;04'),
                (30 * 419 + 33 - 2 * 6, '00:07:00;05')
            ],

            'tenth_minute': [
                (30 * 599 + 29 - 2 * (10 - 10 // 10), '00:09:59;29'),
                (30 * 599 + 30 - 2 * (10 - 10 // 10), '00:10:00;00'),
                (30 * 599 + 31 - 2 * (10 - 10 // 10), '00:10:00;01'),
                (30 * 599 + 32 - 2 * (10 - 10 // 10), '00:10:00;02'),
                (30 * 599 + 33 - 2 * (10 - 10 // 10), '00:10:00;03')
            ],

            'second_hour': [
                (30 * 7199 + 29 - 2 * (120 - 120 // 10), '01:59:59;29'),
                (30 * 7199 + 30 - 2 * (120 - 120 // 10), '02:00:00;00'),
                (30 * 7199 + 31 - 2 * (120 - 120 // 10), '02:00:00;01'),
                (30 * 7199 + 32 - 2 * (120 - 120 // 10), '02:00:00;02'),
                (30 * 7199 + 33 - 2 * (120 - 120 // 10), '02:00:00;03')
            ],

            'second_and_a_half_hour': [
                (30 * 8999 + 29 - 2 * (150 - 150 // 10), '02:29:59;29'),
                (30 * 8999 + 30 - 2 * (150 - 150 // 10), '02:30:00;00'),
                (30 * 8999 + 31 - 2 * (150 - 150 // 10), '02:30:00;01'),
                (30 * 8999 + 32 - 2 * (150 - 150 // 10), '02:30:00;02'),
                (30 * 8999 + 33 - 2 * (150 - 150 // 10), '02:30:00;03')
            ],

            'tenth_hour': [
                (30 * 35999 + 29 - 2 * (600 - 600 // 10), '09:59:59;29'),
                (30 * 35999 + 30 - 2 * (600 - 600 // 10), '10:00:00;00'),
                (30 * 35999 + 31 - 2 * (600 - 600 // 10), '10:00:00;01'),
                (30 * 35999 + 32 - 2 * (600 - 600 // 10), '10:00:00;02'),
                (30 * 35999 + 33 - 2 * (600 - 600 // 10), '10:00:00;03')
            ],

            # Since 3 minutes < 10, we subtract 1 from 603 minutes
            'tenth_hour_third minute': [
                (30 * 36179 + 29 - 2 * (602 - 602 // 10), '10:02:59;29'),
                (30 * 36179 + 30 - 2 * (602 - 602 // 10), '10:03:00;02'),
                (30 * 36179 + 31 - 2 * (602 - 602 // 10), '10:03:00;03'),
                (30 * 36179 + 32 - 2 * (602 - 602 // 10), '10:03:00;04'),
                (30 * 36179 + 33 - 2 * (602 - 602 // 10), '10:03:00;05')
            ]
        }

        ntsc_2997 = otio.opentime.RationalTime.nearest_smpte_timecode_rate(29.97)
        self.assertEqual(ntsc_2997, 30000 / 1001.0)
        for time_key, time_values in test_values.items():
            for value, tc in time_values:
                t = otio.opentime.RationalTime(value, ntsc_2997)
                self.assertEqual(
                    tc, otio.opentime.to_timecode(
                        t, rate=ntsc_2997, drop_frame=True
                    )
                )
                t1 = otio.opentime.from_timecode(tc, rate=ntsc_2997)
                self.assertEqual(t, t1)

    def test_timecode_ntsc_2997fps(self):
        frames = 1084319
        rate_float = (30000 / 1001.0)
        t = otio.opentime.RationalTime(frames, rate_float)

        dftc = otio.opentime.to_timecode(t, rate_float, drop_frame=True)
        self.assertEqual(dftc, '10:03:00;05')

        tc = otio.opentime.to_timecode(t, rate_float, drop_frame=False)
        self.assertEqual(tc, '10:02:23:29')

        # Detect DFTC from rate for backward compatibility with old versions
        tc_auto = otio.opentime.to_timecode(t, rate_float)
        self.assertEqual(tc_auto, '10:03:00;05')

        invalid_df_rate = otio.opentime.RationalTime(30, (24000 / 1001.0))
        with self.assertRaises(ValueError):
            otio.opentime.to_timecode(
                invalid_df_rate, (24000 / 1001.0), drop_frame=True
            )

    def test_timecode_infer_drop_frame(self):
        # These rates are all non-integer SMPTE rates.
        # When `to_timecode` is called without specifying
        # a value for `drop_frame`, it will infer that these
        # should be displayed as drop-frame timecode.
        frames = 1084319
        rates = [
            (29.97, '10:03:00;05'),
            (30000.0 / 1001.0, '10:03:00;05'),
            (59.94, '05:01:30;03'),
            (60000.0 / 1001.0, '05:01:30;03')
        ]
        for rate, timecode in rates:
            t = otio.opentime.RationalTime(frames, rate)

            self.assertEqual(t.to_timecode(rate, drop_frame=None), timecode)
            self.assertEqual(t.to_timecode(rate), timecode)

    def test_timecode_2997(self):
        ref_values = [
            (10789, '00:05:59:19', '00:05:59;29'),
            (10790, '00:05:59:20', '00:06:00;02'),
            (17981, '00:09:59:11', '00:09:59;29'),
            (17982, '00:09:59:12', '00:10:00;00'),
            (17983, '00:09:59:13', '00:10:00;01'),
            (17984, '00:09:59:14', '00:10:00;02'),
        ]
        ntsc_2997 = 30000 / 1001.0
        for value, tc, dftc in ref_values:
            t = otio.opentime.RationalTime(value, ntsc_2997)
            to_dftc = otio.opentime.to_timecode(t, rate=ntsc_2997, drop_frame=True)
            to_tc = otio.opentime.to_timecode(t, rate=ntsc_2997, drop_frame=False)
            to_auto_tc = otio.opentime.to_timecode(t, rate=ntsc_2997)

            # 29.97 should auto-detect dftc for backward compatibility
            self.assertEqual(to_dftc, to_auto_tc)

            # check calculated against reference
            self.assertEqual(to_dftc, dftc)
            self.assertEqual(tc, to_tc)

            # Check they convert back
            t1 = otio.opentime.from_timecode(to_dftc, rate=ntsc_2997)
            self.assertEqual(t1, t)

            t2 = otio.opentime.from_timecode(to_tc, rate=ntsc_2997)
            self.assertEqual(t2, t)

    def test_faulty_formatted_timecode_24(self):
        """
        01:00:13;23 is drop-frame timecode, which only applies for
        NTSC rates (24000/1001, 30000/1001, etc). Such timecodes
        drop frames to compensate for the NTSC rates being slightly
        slower than whole frame rates (eg: 24 fps).
        It does not make sense to use drop-frame timecodes for
        non-NTSC rates.

        This is what we're testing here. When using 24 fps for the
        drop-frame timecode 01:00:13;23 we should get a ValueError
        mapping internally to the ErrorStatus
        'INVALID_RATE_FOR_DROP_FRAME_TIMECODE'.
        """
        with self.assertRaises(ValueError):
            otio.opentime.from_timecode('01:00:13;23', 24)

    def test_faulty_time_string(self):
        with self.assertRaises(ValueError):
            otio.opentime.from_time_string("bogus", 24)

    def test_invalid_rate_to_timecode_functions(self):
        # Use a bogus rate, expecting `to_timecode` to complain
        t = otio.opentime.RationalTime(100, 999)

        with self.assertRaises(ValueError):
            otio.opentime.to_timecode(t, 777)

        with self.assertRaises(ValueError):
            otio.opentime.to_timecode(t)

    def test_time_string_24(self):

        time_string = "00:00:00.041667"
        t = otio.opentime.RationalTime(value=1.0, rate=24)
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))
        self.assertEqual(time_obj.rate, 24)

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

    def test_time_time_string_negative_rational_time(self):
        """
        Negative rational time should return a valid time string
        with a '-' signage. (This is making it ffmpeg compatible)
        """

        baseline_time_string = "-00:00:01.0"
        rt = otio.opentime.RationalTime(-24, 24)
        time_string = otio.opentime.to_time_string(rt)
        self.assertEqual(baseline_time_string, time_string)

    def test_time_time_string_zero(self):
        t = otio.opentime.RationalTime()
        time_string = "00:00:00.0"
        time_obj = otio.opentime.from_time_string(time_string, 24)
        self.assertEqual(time_string, otio.opentime.to_time_string(t))
        self.assertTrue(t.almost_equal(time_obj, delta=0.001))

    def test_to_time_string_microseconds_starts_with_zero(self):
        # this number has a leading 0 in the fractional part when converted to
        # time string (ie 27.08333)
        rt = otio.opentime.RationalTime(2090, 24)
        self.assertEqual(
            str(rt),
            str(otio.opentime.from_time_string(otio.opentime.to_time_string(rt), 24))
        )

    def test_long_running_time_string_24(self):
        final_frame_number = 24 * 60 * 60 * 24 - 1
        final_time = otio.opentime.from_frames(final_frame_number, 24)
        self.assertEqual(
            otio.opentime.to_time_string(final_time),
            "23:59:59.958333"
        )

        step_time = otio.opentime.RationalTime(value=1, rate=24)
        cumulative_time = otio._opentime._testing.add_many(
            step_time,
            final_frame_number
        )

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
        t = otio.opentime.RationalTime(1.0, 2.0)
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
            t2 = otio.opentime.RationalTime(101, fps)
            self.assertEqual(t1, t2)

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

        t5 = otio.opentime.from_seconds(s3).rescaled_to(r3)
        t6 = otio.opentime.from_seconds(s3, r3)
        self.assertEqual(t5, t6)
        self.assertEqual(t6.rate, r3)

    def test_duration(self):
        start_time = otio.opentime.from_frames(100, 24)
        end = otio.opentime.from_frames(200, 24)
        duration = otio.opentime.duration_from_start_end_time(start_time, end)
        self.assertEqual(duration, otio.opentime.from_frames(100, 24))

        start_time = otio.opentime.from_frames(0, 1)
        end = otio.opentime.from_frames(200, 24)
        duration = otio.opentime.duration_from_start_end_time(start_time, end)
        self.assertEqual(duration, otio.opentime.from_frames(200, 24))

        start_time = otio.opentime.from_frames(100, 24)
        end = otio.opentime.from_frames(200, 24)
        duration = otio.opentime.duration_from_start_end_time_inclusive(start_time, end)
        self.assertEqual(duration, otio.opentime.from_frames(101, 24))

        start_time = otio.opentime.from_frames(0, 30)
        end = otio.opentime.from_frames(200, 24)
        duration = otio.opentime.duration_from_start_end_time_inclusive(start_time, end)
        self.assertEqual(duration, otio.opentime.from_frames(251, 30))

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
        gap2 = copy.copy(gap)
        gap2 += a
        self.assertEqual(gap2, a + gap)
        self.assertEqual(b - gap, a.rescaled_to(48))

    def test_duration_from_start_end_time(self):
        tend = otio.opentime.RationalTime(12, 25)

        tdur = otio.opentime.duration_from_start_end_time(
            start_time=otio.opentime.RationalTime(0, 25),
            end_time_exclusive=tend
        )

        self.assertEqual(tend, tdur)

    def test_subtract_with_different_rates(self):
        t1 = otio.opentime.RationalTime(12, 10)
        t2 = otio.opentime.RationalTime(12, 5)

        self.assertEqual((t1 - t2).value, -12)

    def test_incomparable_floats(self):
        t1 = otio.opentime.RationalTime(12, 10)
        with self.assertRaises(TypeError):
            t1 < -1

    def test_immutable(self):
        t1 = otio.opentime.RationalTime(12, 10)

        with self.assertRaises(AttributeError):
            t1.value = 12

    def test_passing_ndf_tc_at_df_rate(self):
        DF_TC = "01:00:02;05"
        NDF_TC = "00:59:58:17"
        frames = 107957
        ntsc_2997 = otio.opentime.RationalTime.nearest_smpte_timecode_rate(29.97)
        self.assertEqual(ntsc_2997, 30000 / 1001.0)

        tc1 = otio.opentime.to_timecode(
            otio.opentime.RationalTime(frames, ntsc_2997)
        )
        self.assertEqual(tc1, DF_TC)

        tc2 = otio.opentime.to_timecode(
            otio.opentime.RationalTime(frames, ntsc_2997),
            ntsc_2997,
            drop_frame=False
        )
        self.assertEqual(tc2, NDF_TC)

        t1 = otio.opentime.from_timecode(DF_TC, ntsc_2997)
        self.assertEqual(t1.value, frames)

        t2 = otio.opentime.from_timecode(NDF_TC, ntsc_2997)
        self.assertEqual(t2.value, frames)

    def test_nearest_smpte_timecode_rate(self):
        rate_pairs = (
            (23.97602397602397, 24000.0 / 1001.0),
            (23.97, 24000.0 / 1001.0),
            (23.976, 24000.0 / 1001.0),
            (23.98, 24000.0 / 1001.0),
            (29.97, 30000.0 / 1001.0),
            (59.94, 60000.0 / 1001.0),
            (24.0, 24.0),
            (23.999999, 24.0),
            (29.999999, 30.0),
            (30.01, 30.0),
            (60.01, 60.0)
        )

        for wonky_rate, smpte_rate in rate_pairs:
            self.assertTrue(
                otio.opentime.RationalTime.is_smpte_timecode_rate(
                    smpte_rate
                )
            )
            self.assertEqual(
                otio.opentime.RationalTime.nearest_smpte_timecode_rate(
                    wonky_rate
                ),
                smpte_rate,
            )


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
        tstart = otio.opentime.RationalTime(12.0, 25.0)
        txform = otio.opentime.TimeTransform(offset=tstart, scale=2.0)
        self.assertEqual(
            repr(txform),
            "otio.opentime.TimeTransform("
            "offset=otio.opentime.RationalTime("
            "value=12, "
            "rate=25"
            "), "
            "scale=2, "
            "rate=-1"
            ")"
        )

        self.assertEqual(
            str(txform),
            "TimeTransform(RationalTime(12, 25), 2, -1)"
        )

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

    def test_copy(self):
        tstart = otio.opentime.RationalTime(12, 25)
        t1 = otio.opentime.TimeTransform(tstart)

        t2 = copy.copy(t1)
        self.assertEqual(t1, t2)
        self.assertIsNot(t1, t2)
        self.assertEqual(t1.offset, t2.offset)
        # TimeTransform.__copy__ acts as a deep copy
        self.assertIsNot(t1.offset, t2.offset)

    def test_deepcopy(self):
        tstart = otio.opentime.RationalTime(12, 25)
        t1 = otio.opentime.TimeTransform(tstart)

        t2 = copy.deepcopy(t1)
        self.assertEqual(t1, t2)
        self.assertIsNot(t1, t2)
        self.assertEqual(t1.offset, t2.offset)
        # TimeTransform.__copy__ acts as a deep copy
        self.assertIsNot(t1.offset, t2.offset)


class TestTimeRange(unittest.TestCase):

    def test_create(self):
        tr = otio.opentime.TimeRange()
        blank = otio.opentime.RationalTime()
        self.assertEqual(tr.start_time, blank)
        self.assertEqual(tr.duration, blank)

        tr1 = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(10, 48)
        )
        self.assertEqual(tr1.start_time.rate, tr1.duration.rate)

        tr2 = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 48)
        )
        self.assertEqual(tr2.start_time.rate, tr2.duration.rate)

        tr3 = otio.opentime.TimeRange(0, 48, 24)
        self.assertEqual(tr3.start_time, otio.opentime.RationalTime(0, 24))
        self.assertEqual(tr3.duration, otio.opentime.RationalTime(48, 24))

    def test_valid(self):
        tr = otio.opentime.TimeRange(0, 0, 0)
        self.assertTrue(tr.is_invalid_range())
        self.assertFalse(tr.is_valid_range())
        tr2 = otio.opentime.TimeRange(0, 48, 24)
        self.assertTrue(tr2.is_valid_range())
        self.assertFalse(tr2.is_invalid_range())
        tr3 = otio.opentime.TimeRange(0, -48, 24)
        self.assertFalse(tr3.is_valid_range())
        self.assertTrue(tr3.is_invalid_range())

    def test_duration_validation(self):
        tr = otio.opentime.TimeRange()
        with self.assertRaises(AttributeError):
            setattr(tr, "duration", "foo")

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
            otio.opentime.RationalTime(-1.0, 24.0),
            otio.opentime.RationalTime(6.0, 24.0)
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

    def test_copy(self):
        start_time1 = otio.opentime.RationalTime(18, 24)
        duration1 = otio.opentime.RationalTime(7, 24)
        tr1 = otio.opentime.TimeRange(start_time1, duration1)

        tr2 = copy.copy(tr1)
        self.assertEqual(
            tr2,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(18, 24),
                otio.opentime.RationalTime(7, 24),
            ),
        )

    def test_deepcopy(self):
        start_time1 = otio.opentime.RationalTime(18, 24)
        duration1 = otio.opentime.RationalTime(7, 24)
        tr1 = otio.opentime.TimeRange(start_time1, duration1)

        tr2 = copy.deepcopy(tr1)
        self.assertEqual(
            tr2,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(18, 24),
                otio.opentime.RationalTime(7, 24),
            ),
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

        self.assertEqual(tr.clamped(test_point_min), tr.start_time)
        self.assertEqual(tr.clamped(test_point_max), tr.end_time_inclusive())

        self.assertEqual(tr.clamped(other_tr), tr)

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

        self.assertFalse(tr.contains(tr))

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

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(13, 25)
        tdur = otio.opentime.RationalTime(1, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(2, 25)
        tdur = otio.opentime.RationalTime(30, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(2, 50)
        tdur = otio.opentime.RationalTime(60, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(2, 50)
        tdur = otio.opentime.RationalTime(14, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(-100, 50)
        tdur = otio.opentime.RationalTime(400, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

        tstart = otio.opentime.RationalTime(100, 50)
        tdur = otio.opentime.RationalTime(400, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.overlaps(tr_t))

    def test_intersects_timerange(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        tstart = otio.opentime.RationalTime(0, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(10, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(10, 25)
        tdur = otio.opentime.RationalTime(2, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(14, 25)
        tdur = otio.opentime.RationalTime(2, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(15, 25)
        tdur = otio.opentime.RationalTime(2, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(13, 25)
        tdur = otio.opentime.RationalTime(1, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(2, 25)
        tdur = otio.opentime.RationalTime(30, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(2, 50)
        tdur = otio.opentime.RationalTime(60, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(2, 50)
        tdur = otio.opentime.RationalTime(14, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(-100, 50)
        tdur = otio.opentime.RationalTime(400, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.intersects(tr_t))

        tstart = otio.opentime.RationalTime(100, 50)
        tdur = otio.opentime.RationalTime(400, 50)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.intersects(tr_t))

    def test_before_timerange(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        tstart = otio.opentime.RationalTime(10, 25)
        tdur = otio.opentime.RationalTime(1.5, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)
        self.assertTrue(tr_t.before(tr))
        self.assertFalse(tr.before(tr_t))

        tdur = otio.opentime.RationalTime(12, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)
        self.assertFalse(tr_t.before(tr))

        self.assertFalse(tr.before(tr))

    def test_before_rationaltime(self):
        tafter = otio.opentime.RationalTime(15, 25)
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        self.assertFalse(tr.before(tafter))
        self.assertFalse(tr.before(tstart))

        tdur = otio.opentime.RationalTime(1.99, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)
        self.assertTrue(tr.before(tafter))

    def test_meets(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)
        tstart = otio.opentime.RationalTime(15, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.meets(tr_t))
        self.assertFalse(tr_t.meets(tr))

        tstart = otio.opentime.RationalTime(14.99, 25)
        tdur = otio.opentime.RationalTime(0, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr_t.meets(tr_t))

    def test_begins_timerange(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)
        tdur = otio.opentime.RationalTime(5, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.begins(tr_t))
        self.assertFalse(tr_t.begins(tr))
        self.assertFalse(tr.begins(tr))

        tdur = otio.opentime.RationalTime(0, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)
        self.assertTrue(tr.begins(tr_t))
        self.assertFalse(tr.begins(tr))

        tstart = otio.opentime.RationalTime(30, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)
        self.assertFalse(tr.begins(tr_t))

        tstart = otio.opentime.RationalTime(13, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)
        tdur = otio.opentime.RationalTime(3, 25)
        tstart = otio.opentime.RationalTime(12, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)
        self.assertFalse(tr_t.begins(tr))

    def test_begins_rationaltime(self):
        tend = otio.opentime.RationalTime(15, 25)
        tbefore = otio.opentime.RationalTime(11.9, 25)
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.begins(tstart))
        self.assertFalse(tr.begins(tend))
        self.assertFalse(tr.begins(tbefore))

    def test_finishes_timerange(self):
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)
        tstart = otio.opentime.RationalTime(13, 25)
        tdur = otio.opentime.RationalTime(2, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr_t.finishes(tr))
        self.assertFalse(tr.finishes(tr_t))
        self.assertFalse(tr.finishes(tr))

        tdur = otio.opentime.RationalTime(1, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)
        self.assertFalse(tr_t.finishes(tr))

        tstart = otio.opentime.RationalTime(30, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)
        self.assertFalse(tr_t.finishes(tr))

        tstart = otio.opentime.RationalTime(15, 25)
        tdur = otio.opentime.RationalTime(0, 25)
        tr_t = otio.opentime.TimeRange(tstart, tdur)
        self.assertTrue(tr_t.finishes(tr))

    def test_finishes_rationaltime(self):
        tafter = otio.opentime.RationalTime(16, 25)
        tend = otio.opentime.RationalTime(15, 25)
        tstart = otio.opentime.RationalTime(12, 25)
        tdur = otio.opentime.RationalTime(3, 25)
        tr = otio.opentime.TimeRange(tstart, tdur)

        self.assertTrue(tr.finishes(tend))
        self.assertFalse(tr.finishes(tstart))
        self.assertFalse(tr.finishes(tafter))

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

    def test_range_from_start_end_time_inclusive(self):
        tstart = otio.opentime.RationalTime(0, 25)
        tend = otio.opentime.RationalTime(12, 25)

        tr = otio.opentime.range_from_start_end_time_inclusive(
            start_time=tstart,
            end_time_inclusive=tend
        )

        self.assertEqual(tr.start_time, tstart)
        self.assertEqual(tr.duration, otio.opentime.RationalTime(13, 25))

        self.assertEqual(tr.end_time_inclusive(), tend)
        self.assertEqual(
            tr.end_time_inclusive(),
            otio.opentime.RationalTime(12, 25),
        )

        self.assertEqual(
            tr,
            otio.opentime.range_from_start_end_time_inclusive(
                tr.start_time, tr.end_time_inclusive()
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
        self.assertNotEqual(timecode, otio.opentime.to_timecode(t, 48))

        time1 = otio.opentime.RationalTime(24.0, 24.0)
        time2 = otio.opentime.RationalTime(1.0, 1.0)
        self.assertEqual(
            otio.opentime.to_timecode(time1, 24.0),
            otio.opentime.to_timecode(time2, 24.0)
        )

    def test_to_frames_mixed_rates(self):
        frame = 100
        t = otio.opentime.from_frames(frame, 24)
        self.assertEqual(frame, otio.opentime.to_frames(t))
        self.assertEqual(frame, otio.opentime.to_frames(t, 24))
        self.assertNotEqual(frame, otio.opentime.to_frames(t, 12))


if __name__ == '__main__':
    unittest.main()
