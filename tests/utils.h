// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once
#undef NDEBUG

#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <string>
#include <cstring>
#include <vector>

void assertTrue(bool value);
void assertFalse(bool value);

template <typename T>
inline void
assertEqual(T const& a, T const& b)
{
    assert(a == b);
}

// We are not testing values outside of one million seconds.
// At one million second, and double precision, the smallest
// resolvable number that can be added to one million and return
// a new value one million + epsilon is 5.82077e-11.
//
// This was calculated by searching iteratively for epsilon
// around 1,000,000, with epsilon starting from 1 and halved
// at every iteration, until epsilon when added to 1,000,000
// resulted in 1,000,000.
constexpr double double_epsilon = 5.82077e-11;

inline void
assertEqual(double a, double b)
{
    assert(std::abs(a - b) <= double_epsilon);
}

inline void
assertEqual(const char* a, const char* b)
{
    assert(a != nullptr);
    assert(b != nullptr);
    assert(strcmp(a, b) == 0);
}

inline void
assertEqual(const void* a, const void* b)
{
    assert(a == b);
}

template <typename T>
inline void
assertNotEqual(T const& a, T const& b)
{
    assert(a != b);
}

inline void
assertNotEqual(double a, double b)
{
    assert(std::abs(a - b) > double_epsilon);
}

inline void
assertNotNull(const void* a)
{
    assert(a != nullptr);
}

class Tests
{
public:
    void
    add_test(std::string const& name, std::function<void(void)> const& test);

    void run(int argc, char** argv);

private:
    std::vector<std::pair<std::string, std::function<void(void)>>> _tests;
};
