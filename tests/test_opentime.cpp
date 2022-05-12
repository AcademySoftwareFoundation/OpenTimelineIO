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
    });

    tests.add_test("test_inequality", [] {
        otime::RationalTime t1(30.2);
        assertEqual(t1, t1);
        otime::RationalTime t2(33.2);
        assertNotEqual(t1, t2);
        otime::RationalTime t3(30.2);
        assertFalse(t1 != t3);
    });

    tests.add_test("test_from_time_string", [] {
        std::string time_string = "0:12:04";
        auto t = otime::RationalTime(24 * (12 * 60 + 4), 24);
        auto time_obj = otime::RationalTime::from_time_string(time_string, 24);
        assertTrue(t.almost_equal(time_obj, 0.001));
    });

    tests.run(argc, argv);
    return 0;
}
