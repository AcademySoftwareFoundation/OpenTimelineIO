#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <iostream>
class OpenTimeTests : public ::testing::Test {
protected:
  void SetUp() override {
    rationalTime = RationalTime_create(48, 24);
  }

  void TearDown() {
    RationalTime_destroy(rationalTime);
  }

  RationalTime *rationalTime;
};

TEST_F(OpenTimeTests, InvalidTimeTest) {
    RationalTime *invalidTime = RationalTime_create(48, -24);
    EXPECT_EQ(RationalTime_is_invalid_time(invalidTime), true);
    EXPECT_EQ(RationalTime_is_invalid_time(rationalTime), false);
    RationalTime_destroy(invalidTime);
}

TEST_F(OpenTimeTests, GetValueTest) {
    EXPECT_EQ(RationalTime_value(rationalTime), 48);
}

TEST_F(OpenTimeTests, GetRateTest) {
    EXPECT_EQ(RationalTime_rate(rationalTime), 24);
}

TEST_F(OpenTimeTests, RescaleToRateTest) {
    RationalTime *rescaledTime = RationalTime_rescaled_to(rationalTime, 48);
    EXPECT_EQ(RationalTime_value(rescaledTime), 96);
    EXPECT_EQ(RationalTime_rate(rescaledTime), 48);
    RationalTime_destroy(rescaledTime);
}

TEST_F(OpenTimeTests, RescaleToRationalTimeTest) {
    RationalTime *scaleTime = RationalTime_create(48, 48);
    RationalTime *rescaledTime = RationalTime_rescaled_to_1(rationalTime, scaleTime);
    EXPECT_EQ(RationalTime_value(rescaledTime), 96);
    EXPECT_EQ(RationalTime_rate(rescaledTime), 48);
    RationalTime_destroy(scaleTime);
    RationalTime_destroy(rescaledTime);
}

TEST_F(OpenTimeTests, ValueRescaledToRateTest) {
    EXPECT_EQ(RationalTime_value_rescaled_to(rationalTime, 48), 96);
}

TEST_F(OpenTimeTests, ValueRescaledToRationalTimeTest) {
    RationalTime *scaleTime = RationalTime_create(48, 48);
    EXPECT_EQ(RationalTime_value_rescaled_to_1(rationalTime, scaleTime), 96);
    RationalTime_destroy(scaleTime);
}

TEST_F(OpenTimeTests, AlmostEqualTest) {
    RationalTime *otherTime = RationalTime_create(50, 24);
    EXPECT_EQ(RationalTime_almost_equal(rationalTime, otherTime, 5), true);
    RationalTime_destroy(otherTime);
}

TEST_F(OpenTimeTests, DurationFromStartEndTimeTest) {
  RationalTime *startTime = RationalTime_create(0, 24);
  RationalTime *endTime = RationalTime_create(24, 24);
  RationalTime *result = RationalTime_duration_from_start_end_time(rationalTime, startTime, endTime);
  EXPECT_EQ(RationalTime_value(result), RationalTime_value(endTime));
  EXPECT_EQ(RationalTime_rate(result), RationalTime_rate(endTime));
  RationalTime_destroy(startTime);
  RationalTime_destroy(endTime);
  RationalTime_destroy(result);
}

TEST_F(OpenTimeTests, IsValidTimeCodeTest){
  EXPECT_EQ(RationalTime_is_valid_timecode_rate(rationalTime, 23.97), true);
  EXPECT_EQ(RationalTime_is_valid_timecode_rate(rationalTime, 24.97), false);
}

TEST_F(OpenTimeTests, ToFramesTest) {
  EXPECT_EQ(RationalTime_to_frames(rationalTime), 48);
}

TEST_F(OpenTimeTests, ToFrames1Test) {
  EXPECT_EQ(RationalTime_to_frames_1(rationalTime, 48), 96);
}

TEST_F(OpenTimeTests, ToSecondsTest) {
  EXPECT_EQ(RationalTime_to_seconds(rationalTime), 2);
}

TEST_F(OpenTimeTests, ToTimecodeTest) {
  ErrorStatus* errorStatus = ErrorStatus_create();
  const char* c = RationalTime_to_timecode(rationalTime, 24, InferFromRate, errorStatus);
  EXPECT_STREQ(c, "00:00:02:00");
  delete c;
  ErrorStatus_destroy(errorStatus);
}

TEST_F(OpenTimeTests, ToTimecode1Test) {
  ErrorStatus* errorStatus = ErrorStatus_create();
  const char* c = RationalTime_to_timecode_1(rationalTime, errorStatus);
  EXPECT_STREQ(c, "00:00:02:00");
  delete c;
  ErrorStatus_destroy(errorStatus);
}

TEST_F(OpenTimeTests, ToTimeStringTest) {
  RationalTime *time = RationalTime_create(24, 23.976);
  const char* c = RationalTime_to_time_string(time);
  EXPECT_STREQ(c, "00:00:01.001001");
  RationalTime_destroy(time);
  delete c;
}
