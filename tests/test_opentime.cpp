#include "utils.h"

#include <opentime/rationalTime.h>

namespace otime = opentime::OPENTIME_VERSION;

Tests::AddTest test_create("test_opentime", "test_create", [] {
    double              t_val = 30.2;
    otime::RationalTime t(t_val);
    assertEqual(t.value(), t_val);

    t = otime::RationalTime();
    assertEqual(t.value(), 0.0);
    assertEqual(t.rate(), 1.0);
});

Tests::AddTest test_equality("test_opentime", "test_equality", [] {
    otime::RationalTime t1(30.2);
    assertEqual(t1, t1);
    otime::RationalTime t2(30.2);
    assertEqual(t1, t2);
});

Tests::AddTest test_inequality("test_opentime", "test_inequality", [] {
    otime::RationalTime t1(30.2);
    assertEqual(t1, t1);
    otime::RationalTime t2(33.2);
    assertNotEqual(t1, t2);
    otime::RationalTime t3(30.2);
    assertFalse(t1 != t3);
});
