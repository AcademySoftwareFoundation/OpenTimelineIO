#pragma once

#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <string>
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

struct Test
{
    std::string group;
    std::string name;
    std::function<void(void)> function;
};

class Tests
{
public:
    static void run(int argc, char** argv);

    struct AddTest
    {
        AddTest(
            std::string const&               group,
            std::string const&               name,
            std::function<void(void)> const& function);
    };

 private:
	std::vector<Test> _tests;
};
