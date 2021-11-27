#pragma once

#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <string>
#include <vector>

inline void
assertTrue(bool value)
{
    assert(value);
}

inline void
assertFalse(bool value)
{
    assert(!value);
}

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

class Tests
{
public:
	void add_test(std::string const& name, std::function<void(void)> const& test) {
		_tests.push_back(std::make_pair(name, test));
	}
	
	void run(int argc, char** argv) {
        std::vector<std::string> filter;
		for (int arg = 1; arg < argc; ++arg)
		{
            filter.push_back(argv[arg]);
		}

		for (auto const& test : _tests)
		{
            bool run_test = true;
			if (!filter.empty())
			{
                const auto filter_it =
                    std::find(filter.begin(), filter.end(), test.first);
                run_test = filter_it != filter.end();
			}
            if (run_test)
			{
                test.second();
			}
		}
	}

private:
	std::vector<std::pair<std::string, std::function<void(void)> > > _tests;
};
