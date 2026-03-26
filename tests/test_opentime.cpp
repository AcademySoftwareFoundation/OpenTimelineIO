// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>

using namespace opentime::OPENTIME_VERSION_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("test_create", [] {
        double       t_val = 30.2;
        RationalTime t(t_val);
        assertEqual(t.value(), t_val);

        t = RationalTime();
        assertEqual(t.value(), 0.0);
        assertEqual(t.rate(), 1.0);
    });

    tests.add_test("test_valid", [] {
        RationalTime t1(0.0, 0.0);
        assertTrue(t1.is_invalid_time());
        assertFalse(t1.is_valid_time());
        RationalTime t2(0.0, 24.0);
        assertTrue(t2.is_valid_time());
        assertFalse(t2.is_invalid_time());
    });

    tests.add_test("test_equality", [] {
        RationalTime t1(30.2);
        assertEqual(t1, t1);
        RationalTime t2(30.2);
        assertEqual(t1, t2);
        RationalTime t3(60.4, 2.0);
        assertEqual(t1, t3);
    });

    tests.add_test("test_inequality", [] {
        RationalTime t1(30.2);
        assertEqual(t1, t1);
        RationalTime t2(33.2);
        assertNotEqual(t1, t2);
        RationalTime t3(30.2);
        assertFalse(t1 != t3);
    });

    tests.add_test("test_strict_equality", [] {
        RationalTime t1(30.2);
        assertTrue(t1.strictly_equal(t1));
        RationalTime t2(30.2);
        assertTrue(t1.strictly_equal(t2));
        RationalTime t3(60.4, 2.0);
        assertFalse(t1.strictly_equal(t3));
    });

    tests.add_test("test_rounding", [] {
        RationalTime t1(30.2);
        assertEqual(t1.floor(), RationalTime(30.0));
        assertEqual(t1.ceil(), RationalTime(31.0));
        assertEqual(t1.round(), RationalTime(30.0));
        RationalTime t2(30.8);
        assertEqual(t2.floor(), RationalTime(30.0));
        assertEqual(t2.ceil(), RationalTime(31.0));
        assertEqual(t2.round(), RationalTime(31.0));
    });

    tests.add_test("test_from_time_string", [] {
         std::string time_string = "0:12:04";
         auto t = RationalTime(24 * (12 * 60 + 4), 24);
         auto time_obj = RationalTime::from_time_string(time_string, 24);
         assertTrue(t.almost_equal(time_obj, 0.001));
     });

    tests.add_test("test_from_time_string24", [] {
        std::string time_string = "00:00:00.041667";
        auto t = RationalTime(1, 24);
        auto time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:00:01";
        t = RationalTime(24, 24);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:01:00";
        t = RationalTime(60 * 24, 24);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "01:00:00";
        t = RationalTime(60 * 60 * 24, 24);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "24:00:00";
        t = RationalTime(24 * 60 * 60 * 24, 24);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "23:59:59.92";
        t = RationalTime((23 * 60 * 60 + 59 * 60 + 59.92) * 24, 24);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
    });

    tests.add_test("test_from_time_string25", [] {
        std::string time_string = "0:12:04.929792";
        auto t = RationalTime((12 * 60 + 4.929792) * 25, 25);
        auto time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:00:01";
        t = RationalTime(25, 25);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "0:1";
        t = RationalTime(25, 25);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "1";
        t = RationalTime(25, 25);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:01:00";
        t = RationalTime(60 * 25, 25);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "01:00:00";
        t = RationalTime(60 * 60 * 25, 25);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "24:00:00";
        t = RationalTime(24 * 60 * 60 * 25, 25);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "23:59:59.92";
        t = RationalTime((23 * 60 * 60 + 59 * 60 + 59.92) * 25, 25);
        time_obj = RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
    });

    tests.add_test("test_create_range", [] {
        RationalTime start(0.0, 24.0);
        RationalTime duration(24.0, 24.0);
        TimeRange r(start, duration);
        assertEqual(r.start_time(), start);
        assertEqual(r.duration(), duration);

        r = TimeRange(0.0, 24.0, 24.0);
        assertEqual(r.start_time(), start);
        assertEqual(r.duration(), duration);

        r = TimeRange();
        assertEqual(r.start_time(), RationalTime());
        assertEqual(r.duration(), RationalTime());
    });

    tests.add_test("test_valid_range", [] {
        TimeRange r1(0.0, 0.0, 0.0);
        assertTrue(r1.is_invalid_range());
        assertFalse(r1.is_valid_range());
        TimeRange r2(0.0, 24.0, 24.0);
        assertTrue(r2.is_valid_range());
        assertFalse(r2.is_invalid_range());
        TimeRange r3(0.0, -24.0, 24.0);
        assertFalse(r3.is_valid_range());
        assertTrue(r3.is_invalid_range());
    });

    tests.run(argc, argv);
    return 0;
}
