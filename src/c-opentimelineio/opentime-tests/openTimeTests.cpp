#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <iostream>
class OpenTimeTests : public ::testing::Test
{
protected:
    void SetUp () override { rationalTime = RationalTime_create (48, 24); }

    void TearDown ()
    {
        RationalTime_destroy (rationalTime);
        rationalTime = NULL;
    }

    RationalTime* rationalTime;
};

TEST_F (OpenTimeTests, InvalidTimeTest)
{
    RationalTime* invalidTime = RationalTime_create (48, -24);
    EXPECT_EQ (RationalTime_is_invalid_time (invalidTime), true);
    EXPECT_EQ (RationalTime_is_invalid_time (rationalTime), false);
    RationalTime_destroy (invalidTime);
    invalidTime = NULL;
}

TEST_F (OpenTimeTests, GetValueTest)
{
    EXPECT_EQ (RationalTime_value (rationalTime), 48);
}

TEST_F (OpenTimeTests, GetRateTest)
{
    EXPECT_EQ (RationalTime_rate (rationalTime), 24);
}

TEST_F (OpenTimeTests, RescaleToRateTest)
{
    RationalTime* rescaledTime = RationalTime_rescaled_to (rationalTime, 48);
    EXPECT_EQ (RationalTime_value (rescaledTime), 96);
    EXPECT_EQ (RationalTime_rate (rescaledTime), 48);
    RationalTime_destroy (rescaledTime);
    rescaledTime = NULL;
}

TEST_F (OpenTimeTests, RescaleToRationalTimeTest)
{
    RationalTime* scaleTime = RationalTime_create (48, 48);
    RationalTime* rescaledTime =
        RationalTime_rescaled_to_rational_time (rationalTime, scaleTime);
    EXPECT_EQ (RationalTime_value (rescaledTime), 96);
    EXPECT_EQ (RationalTime_rate (rescaledTime), 48);
    RationalTime_destroy (scaleTime);
    RationalTime_destroy (rescaledTime);
    scaleTime = rescaledTime = NULL;
}

TEST_F (OpenTimeTests, ValueRescaledToRateTest)
{
    EXPECT_EQ (RationalTime_value_rescaled_to_rate (rationalTime, 48), 96);
}

TEST_F (OpenTimeTests, ValueRescaledToRationalTimeTest)
{
    RationalTime* scaleTime = RationalTime_create (48, 48);
    EXPECT_EQ (
        RationalTime_value_rescaled_to_rational_time (rationalTime, scaleTime),
        96);
    RationalTime_destroy (scaleTime);
    scaleTime = NULL;
}

TEST_F (OpenTimeTests, AlmostEqualTest)
{
    RationalTime* otherTime = RationalTime_create (50, 24);
    EXPECT_EQ (RationalTime_almost_equal (rationalTime, otherTime, 5), true);
    RationalTime_destroy (otherTime);
    otherTime = NULL;
}

TEST_F (OpenTimeTests, DurationFromStartEndTimeTest)
{
    RationalTime* startTime = RationalTime_create (0, 24);
    RationalTime* endTime   = RationalTime_create (24, 24);
    RationalTime* result =
        RationalTime_duration_from_start_end_time (startTime, endTime);
    RationalTime* comparisonResult = RationalTime_compare (result, endTime);
    EXPECT_EQ (RationalTime_value (comparisonResult), 0);
    RationalTime_destroy (startTime);
    RationalTime_destroy (endTime);
    RationalTime_destroy (result);
    RationalTime_destroy (comparisonResult);
    startTime = endTime = result = comparisonResult = NULL;
}

TEST_F (OpenTimeTests, IsValidTimeCodeTest)
{
    EXPECT_EQ (RationalTime_is_valid_timecode_rate (23.97), true);
    EXPECT_EQ (RationalTime_is_valid_timecode_rate (24.97), false);
}

TEST_F (OpenTimeTests, FromFramesTest)
{
    float fps[7] = { 24, 30, 48, 60, 23.98, 29.97, 59.94 };
    for (int i = 0; i < 7; i++)
    {
        RationalTime* t1               = RationalTime_create (101, fps[i]);
        RationalTime* t2               = RationalTime_from_frames (101, fps[i]);
        RationalTime* comparisonResult = RationalTime_compare (t1, t2);
        EXPECT_EQ (RationalTime_value (comparisonResult), 0);
        RationalTime_destroy (t1);
        RationalTime_destroy (t2);
        RationalTime_destroy (comparisonResult);
        t1 = t2          = NULL;
        comparisonResult = NULL;
    }
}

TEST_F (OpenTimeTests, SecondsTest)
{
    int           s1 = 1834;
    RationalTime* t1 = RationalTime_from_seconds (s1);
    EXPECT_EQ (RationalTime_value (t1), 1834);
    EXPECT_EQ (RationalTime_rate (t1), 1);
    EXPECT_EQ (RationalTime_to_seconds (t1), s1);
    EXPECT_DOUBLE_EQ (RationalTime_value (t1) / RationalTime_rate (t1), s1);
    RationalTime_destroy (t1);
    t1 = NULL;

    double        s2 = 248474.345;
    RationalTime* t2 = RationalTime_from_seconds (s2);
    EXPECT_DOUBLE_EQ (RationalTime_value (t2), s2);
    EXPECT_DOUBLE_EQ (RationalTime_rate (t2), 1.0);
    EXPECT_DOUBLE_EQ (RationalTime_to_seconds (t2), s2);
    EXPECT_DOUBLE_EQ (RationalTime_value (t2) / RationalTime_rate (t2), s2);
    RationalTime_destroy (t2);
    t2 = NULL;

    float         v3 = 3459;
    float         r3 = 24;
    float         s3 = v3 / r3;
    RationalTime* t3 = RationalTime_create (v3, r3);
    RationalTime* t4 = RationalTime_from_seconds (s3);
    EXPECT_DOUBLE_EQ (RationalTime_to_seconds (t3), s3);
    EXPECT_DOUBLE_EQ (RationalTime_to_seconds (t4), s3);
    RationalTime_destroy (t3);
    RationalTime_destroy (t4);
    t3 = t4 = NULL;
}

TEST_F (OpenTimeTests, Timecode24_Test)
{
    ErrorStatus*  errorStatus = ErrorStatus_create ();
    const char*   timecode    = "00:00:01:00";
    RationalTime* t           = RationalTime_create (24, 24);
    RationalTime* fromTimeCode =
        RationalTime_from_timecode (timecode, 24, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode     = "00:01:00:00";
    t            = RationalTime_create (24 * 60, 24);
    fromTimeCode = RationalTime_from_timecode (timecode, 24, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode     = "01:00:00:00";
    t            = RationalTime_create (24 * 60 * 60, 24);
    fromTimeCode = RationalTime_from_timecode (timecode, 24, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode     = "24:00:00:00";
    t            = RationalTime_create (24 * 60 * 60 * 24, 24);
    fromTimeCode = RationalTime_from_timecode (timecode, 24, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode     = "23:59:59:23";
    t            = RationalTime_create (24 * 60 * 60 * 24 - 1, 24);
    fromTimeCode = RationalTime_from_timecode (timecode, 24, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;
}

TEST_F (OpenTimeTests, Timecode23976fps_Test)
{
    ErrorStatus*  errorStatus = ErrorStatus_create ();
    const char*   timecode    = "00:00:01:00";
    RationalTime* t           = RationalTime_create (24, 23.976);
    RationalTime* fromTimeCode =
        RationalTime_from_timecode (timecode, 23.976, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode     = "00:01:00:00";
    t            = RationalTime_create (24 * 60, 23.976);
    fromTimeCode = RationalTime_from_timecode (timecode, 23.976, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode     = "01:00:00:00";
    t            = RationalTime_create (24 * 60 * 60, 23.976);
    fromTimeCode = RationalTime_from_timecode (timecode, 23.976, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode     = "24:00:00:00";
    t            = RationalTime_create (24 * 60 * 60 * 24, 23.976);
    fromTimeCode = RationalTime_from_timecode (timecode, 23.976, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;

    timecode = "23:59:59:23";
    t        = RationalTime_create (24 * 60 * 60 * 24 - 1, 24000.0 / 1001.0);
    fromTimeCode =
        RationalTime_from_timecode (timecode, 24000.0 / 1001.0, errorStatus);
    EXPECT_EQ (RationalTime_value (t), RationalTime_value (fromTimeCode));
    EXPECT_EQ (RationalTime_rate (t), RationalTime_rate (fromTimeCode));
    RationalTime_destroy (t);
    RationalTime_destroy (fromTimeCode);
    t = fromTimeCode = NULL;
}

TEST_F (OpenTimeTests, TimecodeNTSC2997fps_Test)
{
    ErrorStatus*  errorStatus = ErrorStatus_create ();
    double        frames      = 1084319;
    double        rate_float  = 30000.0 / 1001.0;
    RationalTime* t           = RationalTime_create (frames, rate_float);
    const char*   dftc =
        RationalTime_to_timecode (t, rate_float, ForceYes, errorStatus);
    EXPECT_STREQ (dftc, "10:03:00;05");

    const char* tc =
        RationalTime_to_timecode (t, rate_float, ForceNo, errorStatus);
    EXPECT_STREQ (tc, "10:02:23:29");

    /* Detect DFTC from rate for backward compatibility with old versions */
    const char* tc_auto =
        RationalTime_to_timecode (t, rate_float, InferFromRate, errorStatus);
    EXPECT_STREQ (tc_auto, "10:03:00;05");

    RationalTime_destroy (t);
    t = NULL;
    delete dftc;
    delete tc;
    delete tc_auto;
    ErrorStatus_destroy (errorStatus);
}

TEST_F (OpenTimeTests, Timecode2997Test)
{
    ErrorStatus* errorStatus = ErrorStatus_create ();
    int ref_values_val[6]    = { 10789, 10790, 17981, 17982, 17983, 17984 };
    const char*   ref_values_tc[6]   = { "00:05:59:19", "00:05:59:20",
                                     "00:09:59:11", "00:09:59:12",
                                     "00:09:59:13", "00:09:59:14" };
    const char*   ref_values_dftc[6] = { "00:05:59;29", "00:06:00;02",
                                       "00:09:59;29", "00:10:00;00",
                                       "00:10:00;01", "00:10:00;02" };
    const char*   to_dftc            = "";
    const char*   to_tc              = "";
    const char*   to_auto_tc         = "";
    RationalTime* t                  = NULL;
    RationalTime* t1                 = NULL;
    RationalTime* t2                 = NULL;
    for (int i = 0; i < 6; i++)
    {
        t       = RationalTime_create (ref_values_val[i], 29.97);
        to_dftc = RationalTime_to_timecode (t, 29.97, ForceYes, errorStatus);
        to_tc   = RationalTime_to_timecode (t, 29.97, ForceNo, errorStatus);
        to_auto_tc =
            RationalTime_to_timecode (t, 29.97, InferFromRate, errorStatus);

        /* 29.97 should auto-detect dftc for backward compatability */
        EXPECT_STREQ (to_dftc, to_auto_tc);

        /* check calculated against reference */
        EXPECT_STREQ (to_dftc, ref_values_dftc[i]);
        EXPECT_STREQ (to_tc, ref_values_tc[i]);

        /* Check they convert back */
        t1 =
            RationalTime_from_timecode (ref_values_dftc[i], 29.97, errorStatus);
        EXPECT_EQ (RationalTime_value (t1), RationalTime_value (t));
        EXPECT_EQ (RationalTime_rate (t1), RationalTime_rate (t));

        t2 = RationalTime_from_timecode (ref_values_tc[i], 29.97, errorStatus);
        EXPECT_EQ (RationalTime_value (t2), RationalTime_value (t));
        EXPECT_EQ (RationalTime_rate (t2), RationalTime_rate (t));

        RationalTime_destroy (t);
        RationalTime_destroy (t1);
        RationalTime_destroy (t2);
        t = t1 = t2 = NULL;
    }

    delete to_dftc;
    delete to_tc;
    delete to_auto_tc;
    ErrorStatus_destroy (errorStatus);
}

TEST_F (OpenTimeTests, TimeString24Test)
{
    ErrorStatus*  errorStatus = ErrorStatus_create ();
    const char*   time_string = "00:00:00.041667";
    RationalTime* t           = RationalTime_create (1.0, 24);
    RationalTime* time_obj =
        RationalTime_from_time_string (time_string, 24, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    EXPECT_EQ (RationalTime_rate (time_obj), 24);
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "00:00:01";
    t           = RationalTime_create (24, 24);
    time_obj    = RationalTime_from_time_string (time_string, 24, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "00:01:00";
    t           = RationalTime_create (24 * 60, 24);
    time_obj    = RationalTime_from_time_string (time_string, 24, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "01:00:00";
    t           = RationalTime_create (24 * 60 * 60, 24);
    time_obj    = RationalTime_from_time_string (time_string, 24, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "24:00:00";
    t           = RationalTime_create (24 * 60 * 60 * 24, 24);
    time_obj    = RationalTime_from_time_string (time_string, 24, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "23:59:59.958333";
    t           = RationalTime_create (24 * 60 * 60 * 24 - 1, 24);
    time_obj    = RationalTime_from_time_string (time_string, 24, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;
}

TEST_F (OpenTimeTests, TimeString25Test)
{
    ErrorStatus*  errorStatus = ErrorStatus_create ();
    const char*   time_string = "00:00:01";
    RationalTime* t           = RationalTime_create (25, 25);
    RationalTime* time_obj =
        RationalTime_from_time_string (time_string, 25, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "00:01:00";
    t           = RationalTime_create (25 * 60, 25);
    time_obj    = RationalTime_from_time_string (time_string, 25, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "01:00:00";
    t           = RationalTime_create (25 * 60 * 60, 25);
    time_obj    = RationalTime_from_time_string (time_string, 25, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "24:00:00";
    t           = RationalTime_create (25 * 60 * 60 * 24, 25);
    time_obj    = RationalTime_from_time_string (time_string, 25, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;

    time_string = "23:59:59.92";
    t           = RationalTime_create (25 * 60 * 60 * 24 - 2, 25);
    time_obj    = RationalTime_from_time_string (time_string, 25, errorStatus);
    EXPECT_TRUE (RationalTime_almost_equal (t, time_obj, 0.001));
    RationalTime_destroy (t);
    RationalTime_destroy (time_obj);
    t = time_obj = NULL;
}

TEST_F (OpenTimeTests, TimeString23976fpsTest)
{

    int         ref_values_val[16] = { 1025,    179900,  180000,  360000,
                               720000,  1079300, 1080000, 1080150,
                               1440000, 1800000, 1978750, 1980000,
                               46700,   225950,  436400,  703350 };
    const char* ref_values_ts[16]  = {
        "00:00:01.708333", "00:04:59.833333", "00:05:00.0",      "00:10:00.0",
        "00:20:00.0",      "00:29:58.833333", "00:30:00.0",      "00:30:00.25",
        "00:40:00.0",      "00:50:00.0",      "00:54:57.916666", "00:55:00.0",
        "00:01:17.833333", "00:06:16.583333", "00:12:07.333333", "00:19:32.25"
    };
    RationalTime* t = NULL;
    for (int i = 0; i < 16; i++)
    {
        t = RationalTime_create (ref_values_val[i], 600);
        EXPECT_STREQ (ref_values_ts[i], RationalTime_to_time_string (t));
        RationalTime_destroy (t);
        t = NULL;
    }
}

TEST_F (OpenTimeTests, ToFramesTest)
{
    EXPECT_EQ (RationalTime_to_frames (rationalTime), 48);
}

TEST_F (OpenTimeTests, ToFramesWithRateTest)
{
    EXPECT_EQ (RationalTime_to_frames_with_rate (rationalTime, 48), 96);
}

TEST_F (OpenTimeTests, MathTimeTest)
{
    RationalTime* a           = RationalTime_from_frames (100, 24);
    RationalTime* gap         = RationalTime_from_frames (50, 24);
    RationalTime* b           = RationalTime_from_frames (150, 24);
    RationalTime* b_minus_a   = RationalTime_subtract (b, a);
    RationalTime* a_plus_gap  = RationalTime_add (a, gap);
    RationalTime* b_minus_gap = RationalTime_subtract (b, gap);

    EXPECT_EQ (RationalTime_value (b_minus_a), RationalTime_value (gap));
    EXPECT_EQ (RationalTime_rate (b_minus_a), RationalTime_rate (gap));

    EXPECT_EQ (RationalTime_value (a_plus_gap), RationalTime_value (b));
    EXPECT_EQ (RationalTime_rate (a_plus_gap), RationalTime_rate (b));

    EXPECT_EQ (RationalTime_value (b_minus_gap), RationalTime_value (a));
    EXPECT_EQ (RationalTime_rate (b_minus_gap), RationalTime_rate (a));

    RationalTime_destroy (a);
    RationalTime_destroy (gap);
    RationalTime_destroy (b);
    RationalTime_destroy (b_minus_a);
    RationalTime_destroy (a_plus_gap);
    RationalTime_destroy (b_minus_gap);
    a = gap = b = b_minus_a = a_plus_gap = b_minus_gap = NULL;
}

TEST_F (OpenTimeTests, CompareTimeTest)
{
    RationalTime* t1               = RationalTime_create (15.2, 1);
    RationalTime* t2               = RationalTime_create (15.6, 1);
    RationalTime* comparisonResult = RationalTime_compare (t1, t2);
    EXPECT_TRUE (RationalTime_value (comparisonResult) > 0);
    RationalTime_destroy (comparisonResult);
    comparisonResult = NULL;

    RationalTime* t3 = RationalTime_create (30.4, 2);
    comparisonResult = RationalTime_compare (t1, t3);
    EXPECT_TRUE (RationalTime_value (comparisonResult) == 0);
    RationalTime_destroy (comparisonResult);
    RationalTime_destroy (t1);
    RationalTime_destroy (t2);
    RationalTime_destroy (t3);
    t1 = t2 = t3 = comparisonResult = NULL;
}
