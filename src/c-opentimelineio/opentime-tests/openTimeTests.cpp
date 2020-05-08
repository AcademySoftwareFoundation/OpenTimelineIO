#include "gtest/gtest.h"

#include <rationalTime.h>

class OpenTimeTests : public ::testing::Test {
protected:
  void SetUp() override {
    rationalTime = createRationalTime(48, 24);
  }

  void TearDown() {
    deleteRationalTime(rationalTime);
  }

  RationalTime *rationalTime;
};

TEST_F(OpenTimeTests, InvalidTimeTest) {
    RationalTime *invalidTime = createRationalTime(48, -24);
    EXPECT_EQ(is_invalid_time(invalidTime), true);
    EXPECT_EQ(is_invalid_time(rationalTime), false);
    deleteRationalTime(invalidTime);
}

TEST_F(OpenTimeTests, GetValueTest) {
    EXPECT_EQ(get_value(rationalTime), 48);
}

TEST_F(OpenTimeTests, GetRateTest) {
    EXPECT_EQ(get_rate(rationalTime), 24);
}

TEST_F(OpenTimeTests, RescaleToRateTest) {
    RationalTime *rescaledTime = rescaled_to_rate(48, rationalTime);
    EXPECT_EQ(get_value(rescaledTime), 96);
    EXPECT_EQ(get_rate(rescaledTime), 48);
    deleteRationalTime(rescaledTime);
}

TEST_F(OpenTimeTests, RescaleToRationalTimeTest) {
    RationalTime *scaleTime = createRationalTime(48, 48);
    RationalTime *rescaledTime = rescaled_to_rational_time(scaleTime, rationalTime);
    EXPECT_EQ(get_value(rescaledTime), 96);
    EXPECT_EQ(get_rate(rescaledTime), 48);
    deleteRationalTime(scaleTime);
    deleteRationalTime(rescaledTime);
}

TEST_F(OpenTimeTests, ValueRescaledToRateTest) {
    EXPECT_EQ(value_rescaled_to_rate(48, rationalTime), 96);
}

TEST_F(OpenTimeTests, ValueRescaledToRationalTimeTest) {
    RationalTime *scaleTime = createRationalTime(48, 48);
    EXPECT_EQ(value_rescaled_to_rational_time(scaleTime, rationalTime), 96);
    deleteRationalTime(scaleTime);
}

TEST_F(OpenTimeTests, AlmostEqualTest) {
    RationalTime *otherTime = createRationalTime(50, 24);
    EXPECT_EQ(almost_equal(5, rationalTime, otherTime), true);
    deleteRationalTime(otherTime);
}

TEST_F(OpenTimeTests, ToFramesTest) {
  EXPECT_EQ(to_frames(rationalTime), 48);
}
