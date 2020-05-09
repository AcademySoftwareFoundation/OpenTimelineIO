#include "gtest/gtest.h"

#include <copentime/rationalTime.h>

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

TEST_F(OpenTimeTests, ToFramesTest) {
  EXPECT_EQ(RationalTime_to_frames(rationalTime), 48);
}
