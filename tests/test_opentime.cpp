// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentime/rationalTime.h>

namespace otime = opentime::OPENTIME_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("test_create", [] {
        double              t_val = 30.2;
        otime::RationalTime t(t_val);
        assertEqual(t.value(), t_val);

        t = otime::RationalTime();
        assertEqual(t.value(), 0.0);
        assertEqual(t.rate(), 1.0);
    });

    tests.add_test("test_equality", [] {
        otime::RationalTime t1(30.2);
        assertEqual(t1, t1);
        otime::RationalTime t2(30.2);
        assertEqual(t1, t2);
        otime::RationalTime t3(60.4, 2.0);
        assertEqual(t1, t3);
    });

    tests.add_test("test_inequality", [] {
        otime::RationalTime t1(30.2);
        assertEqual(t1, t1);
        otime::RationalTime t2(33.2);
        assertNotEqual(t1, t2);
        otime::RationalTime t3(30.2);
        assertFalse(t1 != t3);
    });

    tests.add_test("test_strict_equality", [] {
        otime::RationalTime t1(30.2);
        assertTrue(t1.strictly_equal(t1));
        otime::RationalTime t2(30.2);
        assertTrue(t1.strictly_equal(t2));
        otime::RationalTime t3(60.4, 2.0);
        assertFalse(t1.strictly_equal(t3));
    });

    tests.add_test("test_rounding", [] {
        otime::RationalTime t1(30.2);
        assertEqual(t1.floor(), otime::RationalTime(30.0));
        assertEqual(t1.ceil(), otime::RationalTime(31.0));
        assertEqual(t1.round(), otime::RationalTime(30.0));
        otime::RationalTime t2(30.8);
        assertEqual(t2.floor(), otime::RationalTime(30.0));
        assertEqual(t2.ceil(), otime::RationalTime(31.0));
        assertEqual(t2.round(), otime::RationalTime(31.0));
    });

    tests.add_test("test_from_time_string", [] {
         std::string time_string = "0:12:04";
         auto t = otime::RationalTime(24 * (12 * 60 + 4), 24);
         auto time_obj = otime::RationalTime::from_time_string(time_string, 24);
         assertTrue(t.almost_equal(time_obj, 0.001));
     });

    tests.add_test("test_from_time_string24", [] {
        std::string time_string = "00:00:00.041667";
        auto t = otime::RationalTime(1, 24);
        auto time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:00:01";
        t = otime::RationalTime(24, 24);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:01:00";
        t = otime::RationalTime(60 * 24, 24);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "01:00:00";
        t = otime::RationalTime(60 * 60 * 24, 24);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "24:00:00";
        t = otime::RationalTime(24 * 60 * 60 * 24, 24);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "23:59:59.92";
        t = otime::RationalTime((23 * 60 * 60 + 59 * 60 + 59.92) * 24, 24);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
    });

    tests.add_test("test_from_time_string25", [] {
        std::string time_string = "0:12:04.929792";
        auto t = otime::RationalTime((12 * 60 + 4.929792) * 25, 25);
        auto time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:00:01";
        t = otime::RationalTime(25, 25);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "0:1";
        t = otime::RationalTime(25, 25);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "1";
        t = otime::RationalTime(25, 25);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "00:01:00";
        t = otime::RationalTime(60 * 25, 25);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "01:00:00";
        t = otime::RationalTime(60 * 60 * 25, 25);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "24:00:00";
        t = otime::RationalTime(24 * 60 * 60 * 25, 25);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
        time_string = "23:59:59.92";
        t = otime::RationalTime((23 * 60 * 60 + 59 * 60 + 59.92) * 25, 25);
        time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
    });

    tests.run(argc, argv);
    return 0;
}
