#include <algorithm>
#include <cassert>
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

template <typename T>
inline void
assertNotEqual(T const& a, T const& b)
{
    assert(a != b);
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
